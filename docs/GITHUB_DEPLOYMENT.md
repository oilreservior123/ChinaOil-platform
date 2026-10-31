# GitHub 部署

本项目是静态网页＋独立Python服务。GitHub Pages发布dist/，不能提供Python/GPU训练。

## 网页

1. 将项目代码推送至自己的仓库（既有目标：oilreservior123/ChinaOil-platform，先核实所有权与现有文件）。不要覆盖已有README或历史，先合并审查。
2. 在 GitHub 仓库 Settings → Pages → Build and deployment，将 Source 设置为 GitHub Actions。
3. `.github/workflows/pages.yml` 在main推送后运行检查并部署。完成后使用该次Actions给出的URL。
4. 路径使用相对URL，可部署于仓库子路径。网页运行时只在浏览器内存保存用户上传；上传文件不应提交Git。

GitHub Pages的可见性取决于账号计划和仓库设置；发布前确认需要的访问范围，勿将私密数据加入dist。当前公开来源/生成演示数据附有来源及许可说明。

## 模型服务

按backend/README.md在本机或自己的计算服务器启动。互联网演示需要HTTPS端点、限定GEOTWIN_ALLOWED_ORIGINS为最终GitHub站点origin、设置GEOTWIN_API_TOKEN。网页输入服务地址与令牌后检查连接。每次计算请求重新使用本次训练分区拟合，结果含运行时间、指标、JSON权重/参数，可下载复现。

## 验证

`npm test`、`npm run check`；后端 `python -m unittest discover -s backend -p 'test_*.py' -v`。
