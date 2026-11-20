# 论断证据表与复核事项

| 编号 | 原句 | 来源定位 |
|---|---|---|
| C001 | 当前学生训练包含配对 NDCT 图像的 L1 监督，自监督属性来自 DINO 预训练，因而本例不能称为纯自监督 LDCT 去噪。 | E001：project_summary.md 第3行 |
| C002 | 在 L096/L109 的切片合并均值口径下，E_PUR_001 相对 C0 的 SSIM 增加约 0.001331。 | E002：summary.json /models/C0/metrics_slice_mean/ssim；E003：summary.json /models/E_PUR_001/metrics_slice_mean/ssim |
| C003 | 同一口径下，E_PUR_001 相对 C0 的 PSNR 下降约 0.023559 dB。 | E004：summary.json /models/C0/metrics_slice_mean/psnr；E005：summary.json /models/E_PUR_001/metrics_slice_mean/psnr |
| C004 | 同一口径下，E_PUR_001 相对 C0 的 MAE 增加约 0.000050631。 | E006：summary.json /models/C0/metrics_slice_mean/mae；E007：summary.json /models/E_PUR_001/metrics_slice_mean/mae |
| C005 | 该合并口径包括 L096 的 823 张切片和 L109 的 318 张切片，共 1141 张；L096/L109 同属 AAPM 且已被开发观察，应称为同来源未参与训练患者的开发验证。 | E008：summary.json /patient_summary/L096/C0/slices；E009：summary.json /patient_summary/L109/C0/slices；E010：summary.json /models/C0/slices；E014：project_summary.md 第3行 |
| C006 | 项目记录表明 L333 曾在初始 A/B 阶段评价，当前继续封存，因此不能将本轮未访问写成项目从未访问。 | E015：project_summary.md 第3行 |
| C007 | 同一切片合并口径下，A50 的 PSNR、SSIM、MAE 分别约为 39.437257 dB、0.933304 和 0.007498505，可作为后续比较的空间基线候选。 | E011：summary.json /models/A50/metrics_slice_mean/psnr；E012：summary.json /models/A50/metrics_slice_mean/ssim；E013：summary.json /models/A50/metrics_slice_mean/mae |
| C008 | 本轮材料记录为单种子评价，使用存储强度且 HU 映射未知，也没有医生阅片研究。 | E016：summary.json /interpretation/limitations；E017：original_report.md 第15行 |

## 语义复核

- 已对照项目汇总纠正“纯自监督”命名。
- 旧轮次报告中的“没有访问 L333”只描述该轮；项目汇总确认历史访问，不能外推为全项目未访问。
- 1141 张切片是两个患者的合并数，不是1141个独立患者；本例未重新从逐切片文件重算汇总。
- 相同患者编号在其他项目中可能扮演不同角色，不跨项目推断划分。
- 仅复核已有汇总与文字，尚未经导师或医生审核。

## 核验边界

我使用已有实验材料，在 AI 辅助下整理了本例的证据表与小节初稿，没有为本作业重训模型或重跑原实验。机械检查覆盖已登记的定位、数值与计算；正式写作时，我仍需结合方法与实验设计复核术语、统计口径和解释范围。
