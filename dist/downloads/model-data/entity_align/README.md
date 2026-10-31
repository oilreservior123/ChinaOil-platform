# 语义实体对齐字典基线 数据说明

数据性质：生成实体别名词典与同一实体的未见格式变体。

来源：生成格式规范化测试。

划分：别名记录4/1/1；canonical实体训练已见，不代表未知实体发现能力。实际记录数：训练 120、验证 30、测试 30；比例随分组粒度可能偏离70/15/15。

- train：仅用于拟合/词表/标准化。
- validation：选择超参数/阈值，不能合并进测试。
- test：独立最终评价；机理/规则模型为工况或一致性比较，无需学习。
- overall：上述三部分合并，用于平台重新划分；重分后不能与旧指标混用。
- infer：计算输入，UIE不带spans，异常检测不带label；此演示复用测试输入，不能另称新独立测试集。

字段：

|字段|类型|单位|要求|说明|
|---|---|---|---|---|
|entity_id|string||必有字段||
|alias|string||必有字段||
|canonical|string||必有字段||
|type|string||必有字段||

输入样例（只展示前2条，实际训练请上传完整文件）：

```json
[
  {
    "entity_id": "DEMO:ENTITY:001",
    "alias": "DEMO-W001",
    "canonical": "DEMO-W001",
    "type": "well"
  },
  {
    "entity_id": "DEMO:ENTITY:001",
    "alias": "demo-w001",
    "canonical": "DEMO-W001",
    "type": "well"
  }
]
```
