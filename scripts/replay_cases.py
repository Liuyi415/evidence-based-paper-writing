#!/usr/bin/env python3
"""Replay included real-artifact cases; preserve command output in a new run directory."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    base = Path(__file__).resolve().parent.parent
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = base / 'records' / 'runs' / run_id
    output.mkdir(parents=True, exist_ok=False)
    records = []

    def execute(label, arguments):
        command = [sys.executable, '-X', 'utf8', *arguments]
        start = time.perf_counter()
        result = subprocess.run(command, cwd=base, capture_output=True, encoding='utf-8')
        elapsed = time.perf_counter() - start
        record = {'label': label, 'argv': command, 'exit_code': result.returncode,
                  'elapsed_seconds': elapsed, 'stdout': result.stdout, 'stderr': result.stderr}
        records.append(record)
        transcript = 'ARGV: ' + json.dumps(command, ensure_ascii=False) + '\n'
        transcript += f'EXIT: {result.returncode}\nELAPSED_SECONDS: {elapsed:.6f}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}'
        (output / (label + '.txt')).write_text(transcript, encoding='utf-8')
        print(f'{label}: exit={result.returncode}; {elapsed:.6f}s')
        return result.returncode == 0

    success = True
    for folder in sorted((base / 'cases').iterdir()):
        if not (folder / 'input').is_dir():
            continue
        relative = folder.relative_to(base)
        manifest = relative / 'manifest.json'
        if not (base / manifest).exists():
            ok = execute(folder.name + '-inventory', ['scripts/evidence_tools.py', 'inventory',
                         '--sources-root', str(relative / 'input'), '--out', str(manifest)])
            success = ok and success
        ok = execute(folder.name + '-check', ['scripts/evidence_tools.py', 'check',
                     '--sources-root', str(relative / 'input'), '--manifest', str(manifest),
                     '--evidence', str(relative / 'evidence.json'), '--draft', str(relative / 'draft.md'),
                     '--out', str(relative / 'verification.json')])
        success = ok and success
    ok = execute('boundary-tests', ['scripts/test_evidence_tools.py'])
    success = ok and success
    (output / 'run.json').write_text(json.dumps({'run_id': run_id, 'all_passed': success,
        'scope': 'Mechanical replay of existing artifact snapshots; no model training or full writing-time measurement.',
        'commands': records}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Run records: {output}')
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
