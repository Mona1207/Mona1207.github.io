# 知序 · v17

GitHub Pages：<https://mona1207.github.io/discrete-math/?v=17#home>

三本教材分别保存学习进度，设置 → 我的教材切换。历史离散数学学习指导保留独立记录。

## 例题文字化

| 教材 | 文字例题条目 | 内容 |
| --- | ---: | --- |
| 离散数学第2版 | 227 | 全文、公式、解答和本题讲解 |
| 工程数学·线性代数第7版 | 103 | 全文、矩阵、解答和本题讲解；含2条续例 |
| 概率统计简明教程第3版 | 190 | 全文、分布表、解答和本题讲解；含17个Excel辅助示例 |

以上520条逐页核对后，以 Markdown、LaTeX、表格及可重建的图结构展示，例题页不使用 PDF 裁切。图论图形的必要顶点、边、覆盖关系等改为明确结构；Excel 示例保留选区、可执行公式与结果。课本解答与系统补充的分步讲解分别阅读，少数原书疑点、舍入和建模约定在对应题内说明。

入口 ID 沿用原索引，文字作答与自评仍可恢复。例题阅读、自评不直接增加独立掌握证据。520个例题的知识点映射已按实际题意重新核对。课后习题本轮仍保留完整原页定位，不能把“例题文字化”理解为所有课后习题均已转写或可以自动评分。

上线数据为 `data/examples-*-ready-v17.json`；`examples-*-v17.json` 和章节覆盖文件是构建输入，部分输入保留最初OCR草稿，最终文件由合并脚本生成。`example-knowledge-v17.json` 保存最终知识关联。

## 图片笔记与完整备份

习题或例题右侧 → 图片笔记，可导入PNG/JPG/WebP/GIF，亦可粘贴、拖入，图片原文件内嵌在本机记录中。每张图片绑定当前教材和题号，可填写说明、放大、下载。删除进入回收区，可以恢复。单张最大20MB。手写草稿可直接“存为笔记”。

“下载备份”及设置 → 学习规则与备份 → 备份恢复，下载同一份当前教材完整JSON：学习进度、作答、自评、文字笔记、图片原文件、手写向量草稿与原题记录均包含在内。恢复不依赖原设备的图片路径，也无需逐张重新导入。

恢复流程：选文件 → 校验教材与完整性 → 预览条目数量 → 确认恢复。恢复前保留完整副本，可另行下载。图片与笔迹恢复使用持久日志处理页面中断，重新打开时继续；其他教材记录保留。旧版学习备份仍可导入，并保留当前图片及草稿。

自动保存属于当前浏览器本机存储，不自动同步其他设备。更换设备需下载并导入完整备份。

## 保留的平板交互

700px及以上为紧凑布局，题干与右侧草稿/解析/图片笔记并排。章节树、小节、并排知识点及长列表分页，设置两列。自评仍为独立正确、部分正确、错误三项；客观判题和辅助限制保留。过长题目、笔记、公式允许栏内滚动。

## 重建

```sh
python discrete-math/scripts/merge-examples-v17.py
python discrete-math/scripts/build-ui-v17.py
```

原始扫描书的OCR提取脚本为 `extract-DM2T-v17.py`、`extract-LA7-v17.py`、`extract-PS3-v17.py`；它们依赖原始教材、Tesseract/中文模型及脚本内指定的本机缓存路径。日常UI构建无需重跑OCR。原始教材分段仍由v16流程管理，按需加载，图片笔记不上传公共仓库。

## 验证

```sh
node --check discrete-math/assets/app-ui-v17.js
node discrete-math/scripts/test-ui-v17.mjs
node discrete-math/scripts/test-handwriting-v17.mjs
node discrete-math/scripts/test-notebook-v17.mjs
V17_REQUIRE_ALL_REVIEWED=1 node discrete-math/scripts/audit-examples-v17.mjs
```

测试额外依赖 `fake-indexeddb`、`@napi-rs/canvas` 和 `katex`。可用 `V17_FAKE_INDEXEDDB` 指向fake-indexeddb的ESM入口、`V17_KATEX`指向KaTeX包；画布测试使用 `CODEX_PRIMARY_RUNTIME_NODE_MODULES` 中的Canvas依赖。

检查覆盖520条目及知识关联、全部已校订状态、5497处LaTeX、数学控制字符、分布表、答案隐藏与自评限制、画布真实像素、图片原字节、新设备恢复、旧备份兼容、损坏拒绝、课程隔离、恢复前副本、中断续恢复及保存中的笔迹/图片。

当前环境未提供受支持的浏览器QA，未做真实平板像素布局、原生IndexedDB及实体手写笔验收；组件、模拟IndexedDB与离线Canvas测试不替代实机测试。
