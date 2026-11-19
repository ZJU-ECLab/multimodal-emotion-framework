# 多模态情绪识别研究资料

在线入口：https://zju-eclab.github.io/multimodal-emotion-framework/

本分支为 `web-entry`，用于发布网页；`main` 保留研究源文件，不需要合并本分支。

## 网页目录

```text
index.html                     # 统一主页
assets/                        # 主页和信号综述的样式、交互
docs/                         # 两份综述及四份 Excel（无重复副本）
  情绪识别模型综述.html
  情绪各模态信号综述.html
  情绪各模态信号整理.xlsx
  人人交互情绪词筛选流程.xlsx
  人人交互情绪词主观发生频率.xlsx
  人人交互情绪词各模态表达频率.xlsx
scripts/build_signal_review.py # 从信号工作簿重新生成综述，无第三方依赖
```

既有“人机交互情绪词”研究目录保持原样。

## GitHub Pages

仓库 Settings → Pages → Build and deployment：

- Source: **Deploy from a branch**
- Branch: **web-entry**
- Folder: **/ (root)**

根目录 `.nojekyll` 使网页直接按静态文件发布。推送本分支后自动重新发布。

## 更新资料

直接更新 `docs/` 中的 Excel 或模型综述。若更新“情绪各模态信号整理.xlsx”，运行：

```sh
python3 scripts/build_signal_review.py
```

脚本读取“证据矩阵”和“参考文献”，生成完整矩阵、覆盖统计和参考条目。
若调整表结构或情绪条目数量，应相应调整脚本；正文解读也需随内容变化人工核对。
脚本保留原表的证据限定，不执行外部文献真实性核验。

提交变更并推送 `web-entry` 即可。main 的更新不会自动进入本分支；同步源文件时，请放到对应的 `docs/` 路径。

## 本地预览

在仓库根目录运行：

```sh
python3 -m http.server 8000
```

打开 http://localhost:8000/ 。
