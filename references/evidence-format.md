# 输入格式与核验边界

`inventory` 扫描指定目录中的普通文件，忽略 `.git`、`__pycache__` 和符号链接；记录相对路径、字节数、SHA-256。不联网、不执行数据文件，原始目录保持只读。不要将敏感原始材料默认加入公开仓库。

`check` 使用生成的清单、`evidence.json` 和审计初稿，所有来源路径必须是清单内且位于 `--sources-root` 中的相对路径。清单中的所有文件均复核哈希；输入改变时退出失败。清单与证据表也是用户/AI提供的工件，并非独立的真实性证明。

## evidence.json

以下是**模拟格式示例**，路径和数据不代表用户实验；实际文件须先生成清单。

```json
{
  "evidence": [
    {"id": "E001", "path": "results.csv", "kind": "csv", "row": 1, "column": "score", "value": "0.80"},
    {"id": "E002", "path": "results.csv", "kind": "csv", "row": 2, "column": "score", "value": "0.84"},
    {"id": "E003", "path": "notes.md", "kind": "text", "line_start": 1, "line_end": 1, "quote": "This is synthetic data."}
  ],
  "claims": [
    {
      "id": "C001",
      "text": "模拟得分从 0.80 增至 0.84，相对变化为 5%。",
      "status": "observed",
      "evidence_ids": ["E001", "E002"],
      "calculation": {"operation": "relative_change_percent", "inputs": ["E001", "E002"], "expected": "5", "tolerance": "0.000001"}
    }
  ]
}
```

草稿包含完整论断原句并紧随 `[[C001]]`。支持 `C`/`E` 加至少三位数字的编号；编号须唯一。`status` 仅支持 `observed` 和 `hypothesis`；假设需在原句中明确标明假设性质。至少一条论断和一条证据才允许通过。

### 文本证据

UTF-8 文本；`line_start`/`line_end` 为从 1 开始的闭区间；`quote` 为该区间中可精确匹配的非空原文片段。应选短而足以定位的范围。脚本核对片段存在，不判读其是否足以支持论断。

### CSV 证据

UTF-8（允许 BOM）、逗号分隔、唯一且非空列名，每条记录列数与表头一致。`row` 从表头之后的第一条记录开始计数，1 为首条。`value` 是有限十进制数字字符串，和原始单元格作 Decimal 数值比较。行标识/实验条件应另建文本证据或在人工复核表注明。脚本不会推断行代表的实验是否可比较。

### JSON 证据

`kind: json` 用 `pointer` 指定 JSON Pointer 路径，例如 `/models/C0/metrics_slice_mean/psnr`，数值以 `value` 与原始十进制数精确比较，不经二进制浮点重算。字符串、布尔值与 null 也可精确比对，但不参与运算。数组仅允许按从0开始的索引继续定位，不将对象或数组整体当成数值。重复 JSON 键拒绝处理，防止默默取最后一项。

### 派生计算

只支持两个有序 CSV 或 JSON 数值证据，第一项为基线 a，第二项为比较值 b：

- `difference`：b - a（保持原单位）。
- `ratio`：b / a。
- `relative_change_percent`：(b - a) / abs(a) × 100。

分母为零时拒绝。`expected` 必填；`tolerance` 必填、有限且非负，是原计算单位下的绝对误差容限；选择容限必须符合报告精度，不能靠放大容限掩盖错误。脚本不自动从自由文本识别数值；必须人工核对原句中的数字与计算结果一致。单位、显著性、实验公平性不在机械核验范围内。

## 输出

JSON 中 `mechanical_pass` 为机械检查结果，`errors` 给出问题，`verified_calculations` 给出实际重算值；`registered_claims` 仅是登记条数，不代表全文章节论断覆盖率。退出码 0=通过，1=材料/核验失败，2=命令参数错误。

无法解析 PDF、图片、Excel 的原始语义或公式。先导出后必须保存转换溯源，并人工复核转换正确性。脚本报错时不得将未经核验项目写为“已验证”。
