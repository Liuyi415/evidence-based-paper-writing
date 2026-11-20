# 实验依据驱动的论文小节写作

每次出结果时保存一张实验结果卡，再将已有记录整理为可复核的 Results/Discussion 小节，保留“原始材料 → 证据定位 → 论断 → 初稿”的对应关系，减少正式写作时重新查找材料。

这是我为课程“把一项日常科研工作固化为 SKILL”完成的作业。我原来习惯将结果复制到 PPT 并补充简短说明，正式写论文时又需要重新梳理。因此，我将实验结果整理和论文小节写作固化为一个可复用技能，并借助 AI 完成脚本与案例整理，使用自己三个研究项目的已有结果进行了实测。

## 适合谁

- 经常从多份 CSV/JSON 和实验日志整理结果段落的研究生。
- 需要同时报告正结果、负结果与指标权衡的科研作者。
- 希望让导师或同门能沿着论断回查原始结果的人。

本技能不从题目生成整篇论文，不替代实验、统计设计或研究者判断。第一版支持 UTF-8 文本、CSV 数值和 JSON 路径；PDF/Excel 需另外导出并核验转换关系。

## 文件入口

| 文件 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | AI 执行规程、触发场景与边界 |
| [example.md](example.md) | 作业实战报告，含真实材料、图与终端记录 |
| [loop-ledger.md](loop-ledger.md) | 基线、发现的问题、修改与结案条件 |
| [references/evidence-format.md](references/evidence-format.md) | 可执行证据格式与核验边界 |
| [scripts/evidence_tools.py](scripts/evidence_tools.py) | 输入清单、哈希、证据和计算检查 |
| [cases/fpkd-ct/draft.md](cases/fpkd-ct/draft.md) | 主案例：DINO 教师指导的指标权衡 |
| [cases/tda-ldct/draft.md](cases/tda-ldct/draft.md) | 迁移案例：拓扑去噪开发结果 |
| [cases/topology-time-series/draft.md](cases/topology-time-series/draft.md) | 迁移案例：拓扑结构描述的解释边界 |
| [records/source-map.json](records/source-map.json) | 选定原始文件与快照的对应和哈希 |

## 快速复现

先下载本仓库：在 GitHub 页面点击绿色 **Code → Download ZIP**，解压后进入文件夹；已安装 Git 的同学也可执行：

```powershell
git clone https://github.com/Liuyi415/evidence-based-paper-writing.git
cd evidence-based-paper-writing
```

需要 Python 3.10+，脚本只使用标准库，无需 pip 安装依赖。进入本仓库后执行：

```powershell
python -X utf8 scripts/replay_cases.py
```

这会核验三个案例，运行边界测试，并在 `records/runs/` 下新建真实终端记录。已有 `manifest.json` 会保留，不重新冻结发生变动的输入。`verification.json` 更新为这次核验结果；原始快照不改动。只有当输入目录缺少清单时，才会首次生成。

单独核验一个案例：

```powershell
python -X utf8 scripts/evidence_tools.py check --sources-root cases/fpkd-ct/input --manifest cases/fpkd-ct/manifest.json --evidence cases/fpkd-ct/evidence.json --draft cases/fpkd-ct/draft.md --out cases/fpkd-ct/verification.json
```

`mechanical_pass: true` 表示登记项目在机械层面一致，不表示科学结论已经证明或全文没有遗漏。完整写作流程仍需 AI 阅读材料与研究者复核；`replay_cases.py` 只回放已有工件的核验，不调用大模型重新写稿。

## 让 AI 使用这个技能

无需安装即可给支持读取本地技能的助手发送：

> 请读取本仓库的 SKILL.md，使用我指定的实验结果目录，围绕【研究问题】撰写一个 Results/Discussion 小节。请将所有输出保存在【新输出目录】，先列材料缺口，再建立证据表与草稿，执行核验，保留不利结果和需要我裁决的解释。

也可以将本目录复制到助手支持的个人技能目录。Windows 上以默认 Codex 目录为例，在本仓库运行以下命令；若自定义了技能目录，按自己的目录调整：

```powershell
$skillDestination = Join-Path $env:USERPROFILE '.codex\skills\evidence-based-paper-writing'
if (Test-Path -LiteralPath $skillDestination) { throw '目标技能目录已存在，请先比较版本。' }
Copy-Item -LiteralPath '.' -Destination $skillDestination -Recurse
```

在支持技能发现的会话中用 `$evidence-based-paper-writing` 配合真实任务调用。各助手的安装和刷新方式以其实际支持为准；本次未修改个人技能目录。

## 用自己的新材料

1. 指定只包含原始输入的目录，说明研究问题、指标单位和方向、训练/验证/测试划分。
2. 让 AI 按 `SKILL.md` 调用 `inventory` 并读取输入，将输出写到另一个目录。
3. 按格式建立证据表和初稿，调用 `check`，再做语义复核。
4. 保存本次真实日志、人工修改、未解决的问题。不要把这个仓库的示例结论搬到其他实验。

## 同学试用与反馈

建议先运行已有案例，确认本机能够完成核验，再选择自己的一组真实结果，让 AI 按 `SKILL.md` 输出结果卡、证据表和一个简短小节。记录从读取材料到完成个人检查的总时间，并检查数值、实验条件及解释范围。

可在本仓库的 **Issues → New issue** 中反馈，按下面几项填写即可；失败或“不好用”的反馈同样有帮助：

- 使用环境：操作系统、Python 版本、AI 助手名称。
- 任务类型：实验结果卡或论文结果/讨论小节；无需上传未获准公开的研究材料。
- 实际过程：执行命令、是否成功、错误信息或截图。
- 使用感受：哪些步骤有帮助，哪些步骤繁琐，是否出现错值或过度解释。
- 用时：总时间及人工修改时间；没有计时就写“未测量”。

已有案例回放检查的是脚本行为；使用自己的材料完成一轮整理，才能评价技能对实际写作的帮助。

## 本次实测与局限

我以 FPKD-CT 为主案例，并在拓扑 LDCT 与拓扑时间序列材料上检查流程的可迁移性。三个案例共登记36条证据、16条论断和6项派生计算，机械核验通过；21项模拟边界测试通过。完整过程、问题和前后对比见 [example.md](example.md)。

我保留了不利结果和实验范围限制，没有将脚本通过当作科学结论成立。以往一至两周的重新整理耗时属于回忆估计，本次尚无同口径后测，因此不报告提速百分比。

案例包含我选取的研究汇总、项目说明和结果图，不包含模型权重或原始 CT。原研究材料的使用范围与授权应单独确认，本仓库不替原研究项目添加开源授权。
