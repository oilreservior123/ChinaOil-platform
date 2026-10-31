# RotatE 数据说明

数据性质：公开FORCE井层事实构建三元组。

来源：04_graph/rotate_{split}.tsv。

划分：沿用原始三元组划分；训练实体与关系覆盖验证/测试。实际记录数：训练 444、验证 73、测试 74；比例随分组粒度可能偏离70/15/15。

- train：仅用于拟合/词表/标准化。
- validation：选择超参数/阈值，不能合并进测试。
- test：独立最终评价；机理/规则模型为工况或一致性比较，无需学习。
- overall：上述三部分合并，用于平台重新划分；重分后不能与旧指标混用。
- infer：计算输入，UIE不带spans，异常检测不带label；此演示复用测试输入，不能另称新独立测试集。

字段：

|字段|类型|单位|要求|说明|
|---|---|---|---|---|
|head|string||必有字段||
|relation|string||必有字段||
|tail|string||必有字段||

输入样例（只展示前2条，实际训练请上传完整文件）：

```json
[
  {
    "head": "FORCE:FORMATION:Bryne Fm.",
    "relation": "PART_OF_STRATIGRAPHIC_GROUP",
    "tail": "FORCE:STRAT_GROUP:VESTLAND GP."
  },
  {
    "head": "FORCE:25/11-19 S",
    "relation": "INTERSECTS_FORMATION",
    "tail": "FORCE:FORMATION:Intra Balder Fm. Sst."
  }
]
```
