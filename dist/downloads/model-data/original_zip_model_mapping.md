# 原ZIP逐文件—模型对应清单

公开观测、人工注入标签、模板语料、生成机理算例已分开说明。没有现场专家异常金标准；候选事件不等于异常确诊。

|原ZIP内路径|可用于模型|性质|使用注意|
|---|---|---|---|
|00_sources/dbcl-10.txt|全部模型（来源与许可）|来源/许可元数据|非训练样本，保留归属与许可|
|00_sources/download_receipts.json|全部模型（来源与许可）|来源/许可元数据|非训练样本，保留归属与许可|
|00_sources/odbl-10.txt|全部模型（来源与许可）|来源/许可元数据|非训练样本，保留归属与许可|
|00_sources/porepy_LICENSE.md|全部模型（来源与许可）|来源/许可元数据|非训练样本，保留归属与许可|
|00_sources/volve_production_original.xlsx|grin;anomaly_transformer;arps;crm;lag;rules|公开原始生产观测|源文件；先经单位/停井/缺失检查再转成长表，不能直接当统一模型上传格式|
|01_well_logs/test.csv|isolation_forest;rules;entity_align;hierarchy|公开抽样观测|部分测井为空；测试集不参与填补器/标准化拟合|
|01_well_logs/test_mask_targets.csv|grin（需按深度序列适配）；isolation_forest（质控）|公开观测＋人工遮蔽/目标|目标值仅在测评中使用，禁止作为输入特征；现网页GRIN适配器使用生产时间序列|
|01_well_logs/test_masked.csv|grin（需按深度序列适配）；isolation_forest（质控）|公开观测＋人工遮蔽/目标|目标值仅在测评中使用，禁止作为输入特征；现网页GRIN适配器使用生产时间序列|
|01_well_logs/test_spike_labels.csv|isolation_forest;rules|公开观测＋人工注入异常/标签|仅用于受控异常检测评价，不等于现场专家确认异常|
|01_well_logs/test_spiked.csv|isolation_forest;rules|公开观测＋人工注入异常/标签|仅用于受控异常检测评价，不等于现场专家确认异常|
|01_well_logs/train.csv|isolation_forest;rules;entity_align;hierarchy|公开抽样观测|部分测井为空；测试集不参与填补器/标准化拟合|
|01_well_logs/train_mask_targets.csv|grin（需按深度序列适配）；isolation_forest（质控）|公开观测＋人工遮蔽/目标|目标值仅在测评中使用，禁止作为输入特征；现网页GRIN适配器使用生产时间序列|
|01_well_logs/train_masked.csv|grin（需按深度序列适配）；isolation_forest（质控）|公开观测＋人工遮蔽/目标|目标值仅在测评中使用，禁止作为输入特征；现网页GRIN适配器使用生产时间序列|
|01_well_logs/validation.csv|isolation_forest;rules;entity_align;hierarchy|公开抽样观测|部分测井为空；测试集不参与填补器/标准化拟合|
|01_well_logs/validation_mask_targets.csv|grin（需按深度序列适配）；isolation_forest（质控）|公开观测＋人工遮蔽/目标|目标值仅在测评中使用，禁止作为输入特征；现网页GRIN适配器使用生产时间序列|
|01_well_logs/validation_masked.csv|grin（需按深度序列适配）；isolation_forest（质控）|公开观测＋人工遮蔽/目标|目标值仅在测评中使用，禁止作为输入特征；现网页GRIN适配器使用生产时间序列|
|01_well_logs/well_split.csv|isolation_forest;grin|划分元数据|按整井隔离，非训练特征|
|02_production/array_schema.json|grin;anomaly_transformer;arps;crm;lag;rules|公开生产观测及派生特征|NPZ是已构造张量，上传入口用转换后的CSV/JSONL；不同井/流动角色不能直接混合；CRM需注采日期对齐；Arps需稳定制度筛选|
|02_production/daily_all.csv|grin;anomaly_transformer;arps;crm;lag;rules|公开生产观测及派生特征|NPZ是已构造张量，上传入口用转换后的CSV/JSONL；不同井/流动角色不能直接混合；CRM需注采日期对齐；Arps需稳定制度筛选|
|02_production/grin_test.npz|grin;anomaly_transformer;arps;crm;lag;rules|公开生产观测及派生特征|NPZ是已构造张量，上传入口用转换后的CSV/JSONL；不同井/流动角色不能直接混合；CRM需注采日期对齐；Arps需稳定制度筛选|
|02_production/grin_train.npz|grin;anomaly_transformer;arps;crm;lag;rules|公开生产观测及派生特征|NPZ是已构造张量，上传入口用转换后的CSV/JSONL；不同井/流动角色不能直接混合；CRM需注采日期对齐；Arps需稳定制度筛选|
|02_production/grin_validation.npz|grin;anomaly_transformer;arps;crm;lag;rules|公开生产观测及派生特征|NPZ是已构造张量，上传入口用转换后的CSV/JSONL；不同井/流动角色不能直接混合；CRM需注采日期对齐；Arps需稳定制度筛选|
|02_production/monthly_derived.csv|grin;anomaly_transformer;arps;crm;lag;rules|公开生产观测及派生特征|NPZ是已构造张量，上传入口用转换后的CSV/JSONL；不同井/流动角色不能直接混合；CRM需注采日期对齐；Arps需稳定制度筛选|
|02_production/test.csv|grin;anomaly_transformer;arps;crm;lag;rules|公开生产观测及派生特征|NPZ是已构造张量，上传入口用转换后的CSV/JSONL；不同井/流动角色不能直接混合；CRM需注采日期对齐；Arps需稳定制度筛选|
|02_production/train.csv|grin;anomaly_transformer;arps;crm;lag;rules|公开生产观测及派生特征|NPZ是已构造张量，上传入口用转换后的CSV/JSONL；不同井/流动角色不能直接混合；CRM需注采日期对齐；Arps需稳定制度筛选|
|02_production/validation.csv|grin;anomaly_transformer;arps;crm;lag;rules|公开生产观测及派生特征|NPZ是已构造张量，上传入口用转换后的CSV/JSONL；不同井/流动角色不能直接混合；CRM需注采日期对齐；Arps需稳定制度筛选|
|03_extraction/retrieval_corpus.jsonl|entity_align;语义检索（非训练神经向量模型）|表格事实转中文模板＋检索基准|非人工撰写油藏报告；qrels仅测评|
|03_extraction/retrieval_qrels.json|entity_align;语义检索（非训练神经向量模型）|表格事实转中文模板＋检索基准|非人工撰写油藏报告；qrels仅测评|
|03_extraction/retrieval_test.jsonl|entity_align;语义检索（非训练神经向量模型）|表格事实转中文模板＋检索基准|非人工撰写油藏报告；qrels仅测评|
|03_extraction/retrieval_train.jsonl|entity_align;语义检索（非训练神经向量模型）|表格事实转中文模板＋检索基准|非人工撰写油藏报告；qrels仅测评|
|03_extraction/retrieval_validation.jsonl|entity_align;语义检索（非训练神经向量模型）|表格事实转中文模板＋检索基准|非人工撰写油藏报告；qrels仅测评|
|03_extraction/schema.json|uie;entity_align|真实表格事实生成中文模板/实体跨度标注|非原始报告人工标注；同doc_id全部prompt必须在同分区；模板化数据泛化有限|
|03_extraction/test_annotated.jsonl|uie;entity_align|真实表格事实生成中文模板/实体跨度标注|非原始报告人工标注；同doc_id全部prompt必须在同分区；模板化数据泛化有限|
|03_extraction/test_prompt_spans.jsonl|uie;entity_align|真实表格事实生成中文模板/实体跨度标注|非原始报告人工标注；同doc_id全部prompt必须在同分区；模板化数据泛化有限|
|03_extraction/train_annotated.jsonl|uie;entity_align|真实表格事实生成中文模板/实体跨度标注|非原始报告人工标注；同doc_id全部prompt必须在同分区；模板化数据泛化有限|
|03_extraction/train_prompt_spans.jsonl|uie;entity_align|真实表格事实生成中文模板/实体跨度标注|非原始报告人工标注；同doc_id全部prompt必须在同分区；模板化数据泛化有限|
|03_extraction/validation_annotated.jsonl|uie;entity_align|真实表格事实生成中文模板/实体跨度标注|非原始报告人工标注；同doc_id全部prompt必须在同分区；模板化数据泛化有限|
|03_extraction/validation_prompt_spans.jsonl|uie;entity_align|真实表格事实生成中文模板/实体跨度标注|非原始报告人工标注；同doc_id全部prompt必须在同分区；模板化数据泛化有限|
|04_graph/edges.csv|rotate;hierarchy;entity_align|公开数据构造关联图|完整图包含验证/测试边，不能整图当训练集|
|04_graph/event_graph.json|rules;历史异常检索|公开动态规则生成候选事件图|候选异常非专家确诊，非因果标签|
|04_graph/graph.json|rotate;hierarchy;entity_align|公开数据构造关联图|完整图包含验证/测试边，不能整图当训练集|
|04_graph/link_prediction_protocol.json|rotate|评价协议|非训练数据|
|04_graph/nodes.csv|rotate;hierarchy;entity_align|公开数据构造关联图|完整图包含验证/测试边，不能整图当训练集|
|04_graph/rotate_test.tsv|rotate|公开井层事实构造三元组|使用三元组预划分；验证/测试端点须在训练词表；已知真关系只用于filtered测评|
|04_graph/rotate_train.tsv|rotate|公开井层事实构造三元组|使用三元组预划分；验证/测试端点须在训练词表；已知真关系只用于filtered测评|
|04_graph/rotate_validation.tsv|rotate|公开井层事实构造三元组|使用三元组预划分；验证/测试端点须在训练词表；已知真关系只用于filtered测评|
|05_simulation/darcy_samples.csv|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/darcy_test.npz|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/darcy_train.npz|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/darcy_validation.npz|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/schema.json|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/spe1/SPE1CASE1.DATA|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/spe1/SPE1CASE2.DATA|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/spe9/PERMVALUES.DATA|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/spe9/SPE9.DATA|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/spe9/SPE9.GRDECL|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/spe9/SPE9_CP_GROUP.DATA|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/spe9/SPE9_README.txt|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|05_simulation/spe9/TOPSVALUES.DATA|edfm（几何/参数参考）；未来Darcy代理模型|公开SPE算例/生成Darcy解|原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值|
|06_fractures/original_fractures_2d.csv|dfn;edfm|公开裂缝几何基准（非现场观测）|缺少现场应力、开度、导流校准；需补充假设参数并明确生成|
|06_fractures/original_fractures_3d.csv|dfn;edfm|公开裂缝几何基准（非现场观测）|缺少现场应力、开度、导流校准；需补充假设参数并明确生成|
|06_fractures/planes_3d.json|dfn;edfm|公开裂缝几何基准（非现场观测）|缺少现场应力、开度、导流校准；需补充假设参数并明确生成|
|06_fractures/segments_2d.csv|dfn;edfm|公开裂缝几何基准（非现场观测）|缺少现场应力、开度、导流校准；需补充假设参数并明确生成|
|07_diagnosis/candidate_events.jsonl|rules;anomaly_transformer（辅助筛查）；lag|公开观测派生/规则生成候选|规则结果不是监督学习专家金标准；不得用候选标签声称现场异常准确率|
|07_diagnosis/causal_features.csv|rules;anomaly_transformer（辅助筛查）；lag|公开观测派生/规则生成候选|规则结果不是监督学习专家金标准；不得用候选标签声称现场异常准确率|
|07_diagnosis/rules.json|rules;anomaly_transformer（辅助筛查）；lag|公开观测派生/规则生成候选|规则结果不是监督学习专家金标准；不得用候选标签声称现场异常准确率|
|08_platform/diagnosis_response.json|平台接口演示（非训练样本）|接口响应/配置示例|不是模型训练数据；可用于接口联调|
|08_platform/extraction_response.json|平台接口演示（非训练样本）|接口响应/配置示例|不是模型训练数据；可用于接口联调|
|08_platform/hierarchy_response.json|平台接口演示（非训练样本）|接口响应/配置示例|不是模型训练数据；可用于接口联调|
|08_platform/model_registry.json|平台接口演示（非训练样本）|接口响应/配置示例|不是模型训练数据；可用于接口联调|
|08_platform/well_detail_response.json|平台接口演示（非训练样本）|接口响应/配置示例|不是模型训练数据；可用于接口联调|
|08_platform/workflow.json|平台接口演示（非训练样本）|接口响应/配置示例|不是模型训练数据；可用于接口联调|
|README_使用说明.md|全部模型（说明元数据）|说明/校验|非训练数据|
|SHA256SUMS.txt|全部模型（说明元数据）|说明/校验|非训练数据|
|docs/SOURCES.md|全部模型（说明元数据）|说明/校验|非训练数据|
|docs/data_dictionary.csv|全部模型（说明元数据）|说明/校验|非训练数据|
