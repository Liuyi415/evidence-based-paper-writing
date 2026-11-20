# 论断证据表与复核事项

| 编号 | 原句 | 来源定位 |
|---|---|---|
| C001 | 本例选取 L310 的单患者方法开发描述性评价，图像指标表记录 533 张切片，不构成患者层面的统计推断或最终测试。 | E001：decision.json /scientific_status；E008：image_metrics.csv 数据行1，列n |
| C002 | GATED_TRUST 的平均 PSNR 约为 34.814468 dB，CONTROL 约为 34.823811 dB，差值约为 -0.009343 dB。 | E002：image_metrics.csv 数据行1，列psnr_mean；E003：image_metrics.csv 数据行2，列psnr_mean |
| C003 | 在 CONTROL-safe、原始 QD Top5 且 forward identity 稳定的 H1 子组中，V1 与 GATED_TRUST 各有 239 个特征；相对 CONTROL 的平均误差增量分别约为 0.000281968 与 0.000214328，后者比前者低约 0.000067639。 | E004：branch_identity.csv 数据行4，列forward_delta_error_mean；E005：branch_identity.csv 数据行8，列forward_delta_error_mean；E006：branch_identity.csv 数据行4，列n_forward_identity；E007：branch_identity.csv 数据行8，列n_forward_identity |
| C004 | GATED_TRUST 在该 safe 子组中的误差增量仍为正，本例支持附带误差减少的描述，不支持附带误差已经消除或整体图像质量提高。 | E003：image_metrics.csv 数据行2，列psnr_mean；E002：image_metrics.csv 数据行1，列psnr_mean；E005：branch_identity.csv 数据行8，列forward_delta_error_mean |

## 语义复核

- CSV 第4/8条数据记录分别是 V1/GATED_TRUST 的 H1_QD_TOP5_CONTROL_SAFE；引用列为 forward_delta_error_mean。
- 图像切片与拓扑特征数量属于不同层级；239个特征不是239位患者。
- 后续写作时，我会结合方法部分继续确认两组身份集合的对应关系、误差定义及稳定条件。
- 只报告选定冻结包的开发结论，不推断项目后续最终测试状态。

## 核验边界

我使用已有实验材料，在 AI 辅助下整理了本例的证据表与小节初稿，没有为本作业重训模型或重跑原实验。机械检查覆盖已登记的定位、数值与计算；正式写作时，我仍需结合方法与实验设计复核术语、统计口径和解释范围。
