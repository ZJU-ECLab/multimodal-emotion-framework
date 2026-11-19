# 多模态情绪识别研究资料

静态入口位于 `docs/index.html`，链接到 4 份 Excel 和模型综述 HTML。

## GitHub Pages

发布分支为 `web-entry`，保留 `main` 中的源文件。
在仓库 **Settings → Pages → Build and deployment** 中选择：

- Source: **Deploy from a branch**
- Branch: **web-entry**
- Folder: **/docs**

保存后等待 Pages 构建完成。标准站点地址为：
https://zju-eclab.github.io/multimodal-emotion-framework/

若无法打开 Pages 设置，需要仓库管理员启用。无需合并到 main。

## 更新资料

根目录保留原始文件，`docs/files/` 是供网页下载和阅读的发布副本。
更新源文件后，在 `web-entry` 分支运行：

```sh
python3 scripts/prepare_site.py
```

提交源文件及生成的 `docs/files/` 后推送 `web-entry`，Pages 自动重新发布。
首次创建分支后，main 上的新修改不会自动进入本分支；需要先同步所需源文件，再运行脚本。

## 本地预览

```sh
python3 -m http.server 8000 --directory docs
```

打开 http://localhost:8000/ 。无需安装依赖或运行前端构建。
