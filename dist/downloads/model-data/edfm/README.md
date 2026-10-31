# EDFM油水两相求解模型 数据说明

数据性质：生成工况参数；底层使用公开基准几何。

来源：机理求解输入参数，不可作为神经网络监督目标。

划分：完整工况8/2/2；直接机理求解，无训练真值。实际记录数：训练 8、验证 2、测试 2；比例随分组粒度可能偏离70/15/15。

- train：仅用于拟合/词表/标准化。
- validation：选择超参数/阈值，不能合并进测试。
- test：独立最终评价；机理/规则模型为工况或一致性比较，无需学习。
- overall：上述三部分合并，用于平台重新划分；重分后不能与旧指标混用。
- infer：计算输入，UIE不带spans，异常检测不带label；此演示复用测试输入，不能另称新独立测试集。

字段：

|字段|类型|单位|要求|说明|
|---|---|---|---|---|
|case_id|string||必有字段||
|aperture_mm|number|mm|必有字段|0.1到2|
|pressure_drop_mpa|number|MPa|必有字段|0.1到10|
|duration_days|number|d|必有字段|1到365|

输入样例（只展示前2条，实际训练请上传完整文件）：

```json
[
  {
    "case_id": "DEMO:EDFM:01",
    "aperture_mm": 0.3,
    "pressure_drop_mpa": 2.0,
    "duration_days": 15
  },
  {
    "case_id": "DEMO:EDFM:04",
    "aperture_mm": 0.45,
    "pressure_drop_mpa": 2.9,
    "duration_days": 30
  }
]
```
