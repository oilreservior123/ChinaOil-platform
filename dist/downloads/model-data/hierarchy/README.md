# 井—层—井组—区块关联 数据说明

数据性质：完整生成井—层—井组—区块映射。

来源：不代表Volve真实地层/区块/注采边界。

划分：按整井14/3/3划分，确定性建图无需模型训练。实际记录数：训练 28、验证 6、测试 6；比例随分组粒度可能偏离70/15/15。

- train：仅用于拟合/词表/标准化。
- validation：选择超参数/阈值，不能合并进测试。
- test：独立最终评价；机理/规则模型为工况或一致性比较，无需学习。
- overall：上述三部分合并，用于平台重新划分；重分后不能与旧指标混用。
- infer：计算输入，UIE不带spans，异常检测不带label；此演示复用测试输入，不能另称新独立测试集。

字段：

|字段|类型|单位|要求|说明|
|---|---|---|---|---|
|well_id|string||必有字段||
|layer_id|string||必有字段||
|group_id|string||必有字段||
|block_id|string||必有字段||
|valid_from|date||必有字段||
|valid_to|date||必有字段||

输入样例（只展示前2条，实际训练请上传完整文件）：

```json
[
  {
    "well_id": "DEMO:W01",
    "layer_id": "DEMO:L01",
    "group_id": "DEMO:G01",
    "block_id": "DEMO:B01",
    "valid_from": "2025-01-01",
    "valid_to": "2025-12-31"
  },
  {
    "well_id": "DEMO:W01",
    "layer_id": "DEMO:L02",
    "group_id": "DEMO:G01",
    "block_id": "DEMO:B01",
    "valid_from": "2025-01-01",
    "valid_to": "2025-12-31"
  }
]
```
