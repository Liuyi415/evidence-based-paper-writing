# 论断证据表与复核事项

| 编号 | 原句 | 来源定位 |
|---|---|---|
| C001 | 本例为五种合成信号的结构描述对照，序列长度为 240，延迟嵌入维数为 2、延迟为 10，点云最多取 80 个点。 | E001：results.json /configuration/length；E002：results.json /configuration/embedding_dimension；E003：results.json /configuration/delay；E004：results.json /configuration/max_cloud_points；E010：results.json /limitations |
| C002 | 白噪声的 H1 总寿命约为 1.698291，高于纯正弦的 1.625095，差约为 0.073196；白噪声仍产生 16 个有限 H1 特征。 | E005：summary.csv 数据行1，列h1_total_lifetime；E006：summary.csv 数据行5，列h1_total_lifetime；E007：summary.csv 数据行5，列finite_h1_count |
| C003 | 白噪声最大谱峰对应约 4.210526 个采样点的周期，该选峰结果不能单独证明信号具有真实周期。 | E008：summary.csv 数据行5，列period_at_peak_samples |
| C004 | 这组实验没有比较预测性能，不能据此声称拓扑特征提高了多变量时间序列预测精度。 | E009：original_report.md 第3行；E010：results.json /limitations |

## 语义复核

- 保留原研究中已经生成的合成数据，作为真实已有教学/探索实验使用；它不是真实多变量预测性能实验。
- 原报告标题与表格一致，点云距离寿命不能和谱峰比例横向比数值大小。
- 只复核结果快照和论断范围，没有重跑序列生成或持久同调。

## 核验边界

我使用已有实验材料，在 AI 辅助下整理了本例的证据表与小节初稿，没有为本作业重训模型或重跑原实验。机械检查覆盖已登记的定位、数值与计算；正式写作时，我仍需结合方法与实验设计复核术语、统计口径和解释范围。
