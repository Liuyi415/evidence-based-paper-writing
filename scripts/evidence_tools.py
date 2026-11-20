#!/usr/bin/env python3
"""Read-only source inventory and mechanical claim checks. Python 3.10+ stdlib."""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys


class EvidenceError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path, exact=False):
    options = {'object_pairs_hook': unique_object}
    if exact:
        options['parse_float'] = Decimal
    return json.loads(path.read_text(encoding='utf-8-sig'), **options)


def write_json(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def safe_source(root, name):
    require(isinstance(name, str) and bool(name), 'source path must be nonempty text')
    relative = PurePosixPath(name)
    require(not relative.is_absolute() and '\\' not in name and ':' not in name
            and '..' not in relative.parts, f'unsafe relative source path: {name}')
    path = (root / name).resolve()
    require(path.is_relative_to(root) and path.is_file(), f'missing/outside source: {name}')
    return path


def valid_output(output, root, protected=()):
    path = output.resolve()
    require(not path.is_relative_to(root), 'output must be outside sources-root')
    require(path not in {p.resolve() for p in protected}, 'output would overwrite an input artifact')
    return path


def number(value):
    require(isinstance(value, (str, int, float, Decimal)) and not isinstance(value, bool),
            'expected a finite decimal value')
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise EvidenceError(f'invalid decimal: {value}') from exc
    require(result.is_finite(), f'nonfinite decimal: {value}')
    return result


def index(value, label):
    require(type(value) is int and value >= 1, f'{label} must be an integer >= 1')
    return value


def inventory(root, output):
    require(root.is_dir(), 'sources-root is not a directory')
    valid_output(output, root)
    files = []
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if any(p in {'.git', '__pycache__'} for p in relative.parts):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        require(path.resolve().is_relative_to(root), f'file resolves outside sources-root: {relative}')
        files.append({'path': relative.as_posix(), 'bytes': path.stat().st_size, 'sha256': sha256(path)})
    require(bool(files), 'no source files found')
    result = {'schema_version': 1, 'created_at_utc': datetime.now(timezone.utc).isoformat(), 'files': files}
    write_json(output, result)
    return result


def json_pointer(document, pointer):
    require(isinstance(pointer, str) and pointer.startswith('/'), 'JSON pointer must start with /')
    current = document
    for token in pointer[1:].split('/'):
        require(re.search(r'~(?![01])', token) is None, 'invalid JSON pointer escape')
        key = token.replace('~1', '/').replace('~0', '~')
        if isinstance(current, list):
            require(bool(re.fullmatch(r'0|[1-9][0-9]*', key)), 'invalid JSON array index')
            current = current[int(key)]
        else:
            require(isinstance(current, dict) and key in current, f'JSON pointer key missing: {key}')
            current = current[key]
    return current


def verify_evidence(item, root, manifest_paths):
    require(isinstance(item, dict), 'evidence item must be an object')
    eid = item.get('id', '')
    require(isinstance(eid, str) and re.fullmatch(r'E[0-9]{3,}', eid), 'invalid evidence id')
    name = item.get('path')
    require(isinstance(name, str) and name in manifest_paths, f'{eid}: path not in manifest')
    path = safe_source(root, name)
    kind = item.get('kind')
    if kind == 'text':
        start, end = index(item.get('line_start'), 'line_start'), index(item.get('line_end'), 'line_end')
        lines = path.read_text(encoding='utf-8-sig').splitlines()
        require(start <= end <= len(lines), f'{eid}: text line range out of bounds')
        quote = item.get('quote')
        require(isinstance(quote, str) and bool(quote.strip()), f'{eid}: quote required')
        require(quote in '\n'.join(lines[start - 1:end]), f'{eid}: quote not found in stated lines')
        return eid, None
    if kind == 'csv':
        with path.open(encoding='utf-8-sig', newline='') as stream:
            rows = list(csv.reader(stream, strict=True))
        require(bool(rows), f'{eid}: empty CSV')
        header = rows[0]
        require(all(header) and len(header) == len(set(header)), f'{eid}: empty/duplicate CSV column')
        require(all(len(row) == len(header) for row in rows[1:]), f'{eid}: inconsistent CSV row widths')
        row_index = index(item.get('row'), 'row')
        column = item.get('column')
        require(isinstance(column, str) and column in header, f'{eid}: CSV column not found')
        require(row_index < len(rows), f'{eid}: CSV data row out of bounds')
        actual = number(rows[row_index][header.index(column)])
    elif kind == 'json':
        actual_value = json_pointer(read_json(path, exact=True), item.get('pointer'))
        # Boolean/string context can be verified without being eligible for arithmetic.
        if type(actual_value) is bool or actual_value is None or isinstance(actual_value, str):
            require(type(actual_value) is type(item.get('value')) and actual_value == item.get('value'),
                    f'{eid}: JSON scalar mismatch')
            return eid, None
        actual = number(actual_value)
    else:
        raise EvidenceError(f'{eid}: unsupported evidence kind: {kind}')
    require(actual == number(item.get('value')), f'{eid}: numeric mismatch; source={actual}, stated={item.get("value")}')
    return eid, actual


def check(root, manifest_path, evidence_path, draft_path):
    errors, numbers, calculations = [], {}, []
    manifest = read_json(manifest_path)
    require(isinstance(manifest, dict) and manifest.get('schema_version') == 1, 'unsupported manifest schema')
    records = manifest.get('files')
    require(isinstance(records, list) and bool(records), 'manifest has no files')
    manifest_paths = set()
    for entry in records:
        try:
            require(isinstance(entry, dict), 'manifest file must be an object')
            name = entry.get('path')
            require(isinstance(name, str) and name not in manifest_paths, 'invalid/duplicate manifest path')
            manifest_paths.add(name)
            path = safe_source(root, name)
            require(sha256(path) == entry.get('sha256') and path.stat().st_size == entry.get('bytes'),
                    f'source changed since inventory: {name}')
        except (EvidenceError, OSError) as exc:
            errors.append(str(exc))
    data = read_json(evidence_path)
    require(isinstance(data, dict), 'evidence file must be an object')
    evidence, claims = data.get('evidence'), data.get('claims')
    require(isinstance(evidence, list) and bool(evidence), 'no evidence registered')
    require(isinstance(claims, list) and bool(claims), 'no claims registered')
    seen_evidence = set()
    for item in evidence:
        try:
            eid, value = verify_evidence(item, root, manifest_paths)
            require(eid not in seen_evidence, f'duplicate evidence id: {eid}')
            seen_evidence.add(eid)
            if value is not None:
                numbers[eid] = value
        except (EvidenceError, OSError, ValueError, IndexError, TypeError, csv.Error) as exc:
            errors.append(str(exc))
    draft = draft_path.read_text(encoding='utf-8-sig')
    seen_claims = set()
    for claim in claims:
        try:
            require(isinstance(claim, dict), 'claim must be an object')
            cid = claim.get('id', '')
            require(isinstance(cid, str) and re.fullmatch(r'C[0-9]{3,}', cid), 'invalid claim id')
            require(cid not in seen_claims, f'duplicate claim id: {cid}')
            seen_claims.add(cid)
            text = claim.get('text')
            require(isinstance(text, str) and bool(text.strip()), f'{cid}: text required')
            require(re.search(re.escape(text) + r'\s*\[\[' + re.escape(cid) + r'\]\]', draft),
                    f'{cid}: claim text must be followed by its marker in draft')
            require(claim.get('status') in {'observed', 'hypothesis'}, f'{cid}: invalid status')
            refs = claim.get('evidence_ids')
            require(isinstance(refs, list) and bool(refs) and all(isinstance(x, str) for x in refs),
                    f'{cid}: evidence_ids required')
            require(len(refs) == len(set(refs)) and all(x in seen_evidence for x in refs),
                    f'{cid}: unknown/duplicate/invalid evidence reference')
            if 'calculation' in claim:
                calc = claim['calculation']
                require(isinstance(calc, dict), f'{cid}: calculation must be an object')
                inputs = calc.get('inputs')
                require(isinstance(inputs, list) and len(inputs) == 2
                        and all(isinstance(x, str) and x in numbers and x in refs for x in inputs),
                        f'{cid}: calculation requires two referenced numeric evidence items')
                a, b = (numbers[x] for x in inputs)
                operation = calc.get('operation')
                with localcontext() as context:
                    context.prec = 40
                    if operation == 'difference':
                        actual = b - a
                    elif operation in {'ratio', 'relative_change_percent'}:
                        require(a != 0, f'{cid}: zero baseline denominator')
                        actual = b / a if operation == 'ratio' else (b - a) / abs(a) * 100
                    else:
                        raise EvidenceError(f'{cid}: unknown calculation operation')
                    expected, tolerance = number(calc.get('expected')), number(calc.get('tolerance'))
                    require(tolerance >= 0, f'{cid}: negative tolerance')
                    require(abs(actual - expected) <= tolerance,
                            f'{cid}: calculation mismatch; actual={actual}, expected={expected}, tolerance={tolerance}')
                calculations.append({'claim': cid, 'operation': operation, 'actual': str(actual),
                                     'expected': str(expected), 'tolerance': str(tolerance)})
        except (EvidenceError, InvalidOperation, TypeError, ValueError) as exc:
            errors.append(str(exc))
    markers = re.findall(r'\[\[([^\[\]\r\n]+)\]\]', draft)
    for marker in sorted(set(markers) - seen_claims):
        errors.append(f'draft refers to unknown claim: {marker}')
    return {'mechanical_pass': not errors, 'errors': errors, 'registered_evidence': len(evidence),
            'registered_claims': len(claims), 'verified_calculations': calculations,
            'input_artifact_sha256': {p.name: sha256(p) for p in (manifest_path, evidence_path, draft_path)},
            'limits': 'Checks declared locators, values and calculations only; not scientific truth or full-text coverage.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    inv = sub.add_parser('inventory', help='freeze file hashes without modifying sources')
    inv.add_argument('--sources-root', type=Path, required=True)
    inv.add_argument('--out', type=Path, required=True)
    chk = sub.add_parser('check', help='check registered evidence and draft claims')
    chk.add_argument('--sources-root', type=Path, required=True)
    for key in ('manifest', 'evidence', 'draft', 'out'):
        chk.add_argument('--' + key, type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        root = args.sources_root.resolve()
        require(root.is_dir(), 'sources-root is not a directory')
        protected = () if args.command == 'inventory' else (args.manifest, args.evidence, args.draft)
        valid_output(args.out, root, protected)
        if args.command == 'inventory':
            result = inventory(root, args.out)
            print(f'INVENTORY files={len(result["files"])} output={args.out}')
            return 0
        try:
            result = check(root, args.manifest, args.evidence, args.draft)
        except (OSError, ValueError, KeyError, TypeError, IndexError, csv.Error) as exc:
            result = {'mechanical_pass': False, 'errors': [str(exc)]}
        result['checked_at_utc'] = datetime.now(timezone.utc).isoformat()
        write_json(args.out, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['mechanical_pass'] else 1
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
