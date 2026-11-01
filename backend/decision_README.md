# 油藏智能生产决策计算与大模型服务

入口网页：`https://oilreservior123.github.io/ChinaOil-platform/decision/`。
GitHub Pages直接运行浏览器端模型；不直接承载Python与大模型推理。

## 启动

使用Python 3.10+。网关仅用标准库；XGBoost训练另安装 `pip install 'xgboost>=2,<4'`。

在服务器安全配置中设置以下环境变量（不要提交真实值到Git）：

- `DECISION_ACCESS_TOKEN`：至少16位随机访问令牌；在网页服务配置中填写对应令牌，浏览器不持久保存。
- `DECISION_LLM_BASE_URL`：兼容Chat Completions的HTTPS服务根路径，包含所需的`/v1`，不包含`/chat/completions`。
- `DECISION_LLM_API_KEY`：上游密钥，仅服务器读取。
- `DECISION_LLM_MODEL`：实际可用模型名称，由你配置的服务商决定。
- `DECISION_ALLOWED_ORIGINS`：精确前端origin，默认包含`https://oilreservior123.github.io`，多项逗号分隔。
- `DECISION_HOST`：默认127.0.0.1；`DECISION_PORT`：默认8090。

运行 `python backend/decision_service.py`。通过自己的HTTPS反向代理暴露服务；配置请求大小2MB、适当限流及75秒以上上游超时。网页填写HTTPS服务地址，点击测试连接。私有数据传输前勾选当次授权。

## 接口

全部为JSON POST，需`Authorization: Bearer <访问令牌>`。CORS不允许通配origin。

- `/health`：返回实际大模型配置状态、模型名称、XGBoost可用状态。
- `/chat`：`{question,evidence}` → `{answer,model}`。模型上游地址来自服务器环境，不能由浏览器请求覆盖。输出须人工复核。
- `/train`：`{model_id:"xgboost",rows,validation,options:{trees,depth}}` → 模型会话token与实测duration秒。当前固定轮次，不用验证/测试选模。
- `/predict`：`{model_token,rows}` → `{predictions}`。

XGBoost输入为`lag_oil,lag_water,lag_pressure,lag_injection,lag_water_cut`，训练标签`oil`。这些特征由网页按同一口井前一日构造，断点不构造窗口。模型最多缓存12个，1小时过期，重启清空。当前仅会话内缓存，不提供跨用户持久模型库。共享服务应按组织身份管理令牌和资源配额。

## 已实现边界

无服务时，网页仍支持浏览器模型、数据上传、数值工具与清楚标记的本地证据模板报告。未提供服务器或上游凭证时，不能声称远程XGBoost或大模型推理已上线。测试：`python -m unittest discover -s backend -p test_decision_service.py`。
