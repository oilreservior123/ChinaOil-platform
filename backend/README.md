# GeoTwin 独立模型训练与推理服务

GitHub Pages 只托管静态页面，不能运行 Python 或训练深度模型。本服务运行在自己的电脑或计算服务器；网页“模型实验室”配置它的地址后调用。所有计算来自上传数据，无需默认私有数据。Python 3.11+、Node.js 20+。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

最简本地同源演示（网页＋训练服务一个进程）：

```bash
python -m uvicorn backend.dev:app --host 127.0.0.1 --port 4173
```

浏览器打开 `http://localhost:4173`，前端服务地址填写同一个 `http://localhost:4173`。API端点先注册，网页StaticFiles仅处理其余路径。也可分别运行前后端：同电脑 `http://localhost:4173` 前端连接 `http://127.0.0.1:8000`。GitHub 的 HTTPS 网页连接本机 HTTP 可能被浏览器的混合内容/本地网络策略阻止；正式演示应将服务部署到有 HTTPS 的自有服务器/可信反向代理，并在网页填写该 HTTPS 服务地址。不可通过关闭浏览器安全检查解决。

服务器部署时，设置 `GEOTWIN_ALLOWED_ORIGINS=https://你的账号.github.io`、`GEOTWIN_API_TOKEN=自设强随机令牌`，用反向代理配置 TLS、请求大小和计算超时，再由网页的服务设置填写令牌。不要把令牌放入 GitHub 代码或 Pages 配置；前端仅当前会话使用。默认命令只监听本机，不要在无认证情况下将 8000 端口暴露公网。服务支持一次一个计算任务，并返回409忙碌；刷新网页不会取消服务器正在运行的训练。

## 接口

- `GET /health`：服务模型列表及状态。
- `GET /api/contracts`：13类模型数据格式、特征、单位、样例、结构和推荐划分。
- `POST /api/run`：JSON `{model_id,operation,train,validation,test,input,parameters}`。operation 为 `train`/`validate`/`test`/`predict`，所有数据为记录对象数组。predict使用input；validate/test分别使用对应分区。每次请求独立使用本次train重新拟合，validation选择权重或阈值，test只评价，不保留上一请求模型或上传数据。
- 可选认证头：`X-API-Key: ...` 或 `Authorization: Bearer ...`。
- 返回 `{results,metrics,history,model_artifact,training_seconds,compute_seconds,elapsed_seconds,limitations,...}`，网页可下载JSON/CSV结果。权重为纯JSON，不接受不安全的pickle上传。部分非神经模型返回参数摘要，完整服务源码可复现计算。

示例

```json
{"model_id":"arps","operation":"test","train":[{"well_id":"W1","date":"2025-01-01","t":0,"oil":100}],"validation":[],"test":[],"input":[],"parameters":{"epochs":6,"seed":20261031}}
```

上例展示字段，实际Arps至少6条训练记录；测试操作还需非空独立test。可使用网站提供的完整模型数据包。

## 计算边界

- Isolation Forest：真实sklearn训练，训练期中位数/RobustScaler，验证标签可选择阈值。
- GRIN / UIE式抽取 / Anomaly Transformer / RotatE：从头训练的小型PyTorch结构复现，不是官方预训练模型。CPU默认6 epochs，1–100，上限10000条训练数据。UIE每提示一个非空span，prompt＋正文最多255 Unicode字符。GRIN网络中的井必须在train出现，指标仅针对已知数据人工遮蔽。RotatE验证/测试/预测实体、关系必须在训练词表中。
- Arps / CRM：真实参数校准，`training_seconds`兼容字段对应`calibration_seconds`；仅在工程适用前提成立时解释。
- DFN：二维端点几何及声明的应力方向开度权重假设，非耦合地质力学预测。
- EDFM：调用与网页相同的实际Node.js保守两相求解器；输入为自带公开几何基准的工况参数，不能替换真实地质几何。每批最多12工况；无需训练，training_seconds=null。
- 对齐/规则/层级/时滞：实际确定性/统计计算，无需神经训练，training_seconds=null。
- 无标签的异常数据不返回F1/AUC；无真实目标的预测不冒充验证成绩。相同样本跨train/validation/test会被拒绝。

测试：`python -m unittest discover -s backend -p 'test_*.py' -v`。
