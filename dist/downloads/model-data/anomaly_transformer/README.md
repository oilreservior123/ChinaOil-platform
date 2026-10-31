# Anomaly Transformer精简结构复现 数据说明

数据性质：固定随机种子、解析信号生成数据；非现场观测。

来源：generate_sequences()。

划分：每井前70%日期训练/中15%验证/后15%测试；推理样例保留同一数据字典。实际记录数：训练 1008、验证 216、测试 216；比例随分组粒度可能偏离70/15/15。

- train：仅用于拟合/词表/标准化。
- validation：选择超参数/阈值，不能合并进测试。
- test：独立最终评价；机理/规则模型为工况或一致性比较，无需学习。
- overall：上述三部分合并，用于平台重新划分；重分后不能与旧指标混用。
- infer：计算输入，UIE不带spans，异常检测不带label；此演示复用测试输入，不能另称新独立测试集。

字段：

|字段|类型|单位|要求|说明|
|---|---|---|---|---|
|well_id|string||必有字段||
|date|date||必有字段||
|oil|number|Sm³/d|必有字段|日均产油，缺失填null|
|liquid|number|Sm³/d|必有字段|日均产液|
|water_cut|number|fraction|必有字段|0到1|
|pressure|number|MPa|必有字段||
|injection|number|Sm³/d|必有字段|同一口径注水量|
|label|integer||可选/按任务|可选专家标签0/1，仅有标签时计算分类评价|

输入样例（只展示前2条，实际训练请上传完整文件）：

```json
[
  {
    "well_id": "DEMO:W01",
    "date": "2025-01-01",
    "oil": 110.0,
    "liquid": 134.14634,
    "water_cut": 0.18,
    "pressure": 24.0,
    "injection": 130.0,
    "label": 0
  },
  {
    "well_id": "DEMO:W01",
    "date": "2025-01-02",
    "oil": 109.67049,
    "liquid": 134.31774,
    "water_cut": 0.1835,
    "pressure": 23.99709,
    "injection": 132.33063,
    "label": 0
  }
]
```
