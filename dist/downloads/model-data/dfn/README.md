# DFN应力约束几何模型 数据说明

数据性质：公开PorePy二维几何＋生成应力/开度假设。

来源：06_fractures/segments_2d.csv；应力与开度非现场实测。

划分：12个完整工况8/2/2隔离；机理模型无需训练。实际记录数：训练 504、验证 126、测试 126；比例随分组粒度可能偏离70/15/15。

- train：仅用于拟合/词表/标准化。
- validation：选择超参数/阈值，不能合并进测试。
- test：独立最终评价；机理/规则模型为工况或一致性比较，无需学习。
- overall：上述三部分合并，用于平台重新划分；重分后不能与旧指标混用。
- infer：计算输入，UIE不带spans，异常检测不带label；此演示复用测试输入，不能另称新独立测试集。

字段：

|字段|类型|单位|要求|说明|
|---|---|---|---|---|
|case_id|string||必有字段||
|x1|number|m|必有字段||
|y1|number|m|必有字段||
|x2|number|m|必有字段||
|y2|number|m|必有字段||
|aperture_mm|number|mm|必有字段||
|stress_direction_deg|number|°|必有字段||
|stress_ratio|number||必有字段|最小/最大应力比例0到1|

输入样例（只展示前2条，实际训练请上传完整文件）：

```json
[
  {
    "case_id": "DEMO:DFN:01",
    "x1": 269.611206,
    "y1": 152.05243,
    "x2": 356.924011,
    "y2": 310.14123,
    "aperture_mm": 0.3,
    "stress_direction_deg": 0,
    "stress_ratio": 0.5
  },
  {
    "case_id": "DEMO:DFN:01",
    "x1": 249.511719,
    "y1": 514.99078,
    "x2": 272.218872,
    "y2": 470.97082,
    "aperture_mm": 0.3,
    "stress_direction_deg": 0,
    "stress_ratio": 0.5
  }
]
```
