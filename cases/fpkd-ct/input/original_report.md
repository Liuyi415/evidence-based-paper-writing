# 稳定性复验与双分支消融

日期：2026-11-09。所有模型均为冻结检查点；外部患者 L096、L109 未参与训练或选模。没有访问 L333 测试数据。

## 结论

E-low purified teacher improves SSIM over C0 on L506 and on the two external patients, but remains lower in PSNR and higher in MAE; the direction is consistent but not a comprehensive improvement.

Matched spatial-only A50 exceeds the current B/C0 spatial-spectral model on L506 and on the two external patients. The current Fourier branch is therefore not supported as a beneficial component under this protocol.

Pause D2 and revise the student backbone. Treat A50 as the current stronger baseline; test a capacity-matched or parameter-matched spectral branch only after fixing spatial training and validation protocol. Revalidate E-low against A50 before attributing any teacher gain.

## 外部患者冻结检查点评价

外部患者不参与模型选择，指标仅用于泛化方向检查。所有输出为完整切片 float32 推理，不裁剪，data_range=1。

| 模型 | PSNR | SSIM | MAE |
| --- | ---: | ---: | ---: |
| C0 | 39.3822 | 0.932139 | 0.007518 |
| E_PUR_001 | 39.3586 | 0.933470 | 0.007569 |
| E_PUR_01 | 39.2767 | 0.932425 | 0.007668 |
| A50 | 39.4373 | 0.933304 | 0.007499 |

相对 C0：

| 模型 | ΔPSNR | ΔSSIM | ΔMAE |
| --- | ---: | ---: | ---: |
| E_PUR_001 | -0.0236 | +0.001331 | +0.000051 |
| E_PUR_01 | -0.1055 | +0.000286 | +0.000150 |
| A50 | +0.0551 | +0.001166 | -0.000020 |

患者级结果见 `summary.json`，每张切片见 `per_slice.csv`。L096有823张切片，L109有318张；切片不是独立患者样本。

## L506双分支消融

固定 L067/L310 配对训练、L506选模、随机种子、128裁剪、批量8、50轮×200更新、Adam与余弦学习率。A50为空间-only SpatialUNet；C0为已有空间—频谱 B 的纯L1控制。

| 模型 | PSNR | SSIM | MAE |
| --- | ---: | ---: | ---: |
| C0：空间—频谱 | 40.8747 | 0.948116 | 0.006063 |
| A50：空间-only | 40.9053 | 0.949064 | 0.006064 |

A50相对C0：PSNR +0.0307 dB，SSIM +0.000949，MAE +0.000001。外部患者上方向一致，说明当前频谱分支没有显示收益；B的频率分支与空间分支参数量略有不同，后续仍需参数量匹配的严格消融。

## 定性材料

`results/figures/stability_ablation_20261109_v1/` 中保存 L096/L109 的固定相对位置图和 `external_patient_metrics.png`。图像使用存储归一化强度，不是HU窗；尚无医生盲评。外部图只用于开发泛化观察，不改变选模。

## 后续决策

暂缓 D2。以 A50 作为新的强空间基线，先完成参数量/计算量匹配的频谱分支消融，再比较 E-low 净化教师是否仍有独立收益。只有在多患者或多种子上相对 A50 出现稳定结构收益，才进入未配对 LDCT 训练。
