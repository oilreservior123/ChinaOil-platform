# 数据来源与加工记录

访问/下载日期：2026-10-31。精确下载URL、字节数与SHA256见 `../00_sources/download_receipts.json`。

| 来源 | 官方入口与实际下载 | 交付加工 | 许可/边界 |
|---|---|---|---|
| Equinor Volve | [官方数据说明](https://www.equinor.com/energy/volve-data-sharing)；实际Excel字节来自[yohanesnuwara/MLGeo镜像](https://github.com/yohanesnuwara/MLGeo/blob/main/Volve%20production%20data.xlsx) | 原工作簿保留；日表标准化、时间划分、月度汇总、候选事件、中文事实摘要 | 官方标示Equinor Open Data Licence；以原数据条款为准，不将镜像的代码许可覆盖到数据。官方当前完整数据入口为Databricks Marketplace |
| FORCE 2020 | [Zenodo DOI 10.5281/zenodo.4351156](https://zenodo.org/records/4351156)；实际CSV来自[竞赛仓库GIR贡献者子集](https://github.com/bolgebrygg/Force-2020-Machine-Learning-competition/blob/master/lithology_competition/code/GIR/train.csv) | 28井、342,177行源子集，最多3,000行/井等距抽样为81,220行，保留源行号；派生遮蔽/尖峰集分开 | Zenodo说明原井数据为挪威开放政府数据许可NLOD 2.0（页面拼写NOLD）。该子集不是完整118井数据；上游可能已作清洗，未宣称原始仪器采集数据 |
| OPM opm-data | [仓库与许可说明](https://github.com/OPM/opm-data)；`spe1/`、`spe9/` | 原始输入及INCLUDE依赖保留；SPE9 PERMX切片用于新增无量纲2D Darcy实验；WELSPECS生成图谱 | 原始deck为ODbL 1.0，内容为DbCL 1.0，原文附包。SPE1/SPE9为公开模拟算例，不是实际Volve油藏。来源只取当前仓库文件，不取历史中已删除的受限deck |
| PorePy | [官方仓库](https://github.com/pmgbergen/porepy)；`src/porepy/applications/md_grids/gmsh_file_library/benchmark_2d_case_4/fracture_network_benchmark_2d_case_4.csv`、`benchmark_3d_case_2/fracture_network.csv` | 原CSV保留；线段长度、方位与3D顶点JSON由几何确定计算 | 仓库GPL-3.0原文附包。只是公开数值基准几何，不是裂缝预测监督数据 |

FORCE建议署名：Bormann P., Aursand P., Dilib F., Manral S., Dischington P. (2020). FORCE 2020 well log and lithofacies dataset for machine learning competition. Zenodo. DOI:10.5281/zenodo.4351156；并引用竞赛仓库。

SPE9输入文件包含对Killough (1995), Ninth SPE Comparative Solution Project的来源说明，随原文件保留。PorePy仓库中的基准可对应Flemisch等关于裂缝介质单相渗流的公开研究，具体模型定义应以该仓库应用说明为准。

## 未作为交付文件的候选来源

- [Utah FORGE 2025 DFN](https://gdr.openei.org/submissions/1750)：官方描述131个解释裂缝面及额外随机裂缝；没有开度、渗透率等水力属性。页面许可链接为CC BY 4.0。本次下载返回不可用页面，未将其误存为数据或替换成自造裂缝。
- [Utah FORGE 2020 DFN](https://gdr.openei.org/submissions/1222)：官方说明为随机裂缝实现，不能称实测裂缝标签；本次未下载成功。
- FORCE Zenodo完整LAS压缩包本次返回403，因此采用竞赛仓库中实际下载并解析成功的28井子集。

## 加工类型

- `public_observation`：原公开观测表中的值。
- `derived`：单位不变的重命名、抽样、汇总、比例、图结构或规则候选。
- `generated_chinese_summary_of_public_table`：由真实事实生成的中文模板文本及程序标注，非原报告。
- `controlled_injection`：在真实观测上人工遮蔽/添加尖峰，标签只说明这项加工。
- `public_benchmark_geometry`：公开数值基准的几何。
- `numerically_solved_derivative`：公开渗透率场＋新实验条件的实际求解输出，非油田实测压力场。
