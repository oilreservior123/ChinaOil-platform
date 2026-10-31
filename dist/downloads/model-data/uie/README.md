# UIE式精简抽取模型 数据说明

数据性质：Volve真实表格事实生成中文模板及精确跨度标注，非人工原报告。

来源：03_extraction/{split}_prompt_spans.jsonl。

划分：沿用按doc_id分组划分；训练24篇、验证/测试各5篇文档，每文档多个prompt。实际记录数：训练 216、验证 45、测试 45；比例随分组粒度可能偏离70/15/15。

- train：仅用于拟合/词表/标准化。
- validation：选择超参数/阈值，不能合并进测试。
- test：独立最终评价；机理/规则模型为工况或一致性比较，无需学习。
- overall：上述三部分合并，用于平台重新划分；重分后不能与旧指标混用。
- infer：计算输入，UIE不带spans，异常检测不带label；此演示复用测试输入，不能另称新独立测试集。

字段：

|字段|类型|单位|要求|说明|
|---|---|---|---|---|
|doc_id|string||必有字段||
|content|string||必有字段||
|prompt|string||必有字段||
|spans|array||必有字段|训练/验证/测试必填，推理可省；[{start,end,text}]，Unicode字符索引左闭右开|

输入样例（只展示前2条，实际训练请上传完整文件）：

```json
[
  {
    "doc_id": "VOLVE_SUMMARY:0005",
    "content": "Volve油田生产月报：井号15/9-F-14，统计月份2008-07，产油体积51285.08 Sm3，产水体积126.17 Sm3。",
    "prompt": "井号",
    "spans": [
      {
        "text": "15/9-F-14",
        "start": 14,
        "end": 23
      }
    ]
  },
  {
    "doc_id": "VOLVE_SUMMARY:0005",
    "content": "Volve油田生产月报：井号15/9-F-14，统计月份2008-07，产油体积51285.08 Sm3，产水体积126.17 Sm3。",
    "prompt": "油田",
    "spans": [
      {
        "text": "Volve",
        "start": 0,
        "end": 5
      }
    ]
  }
]
```
