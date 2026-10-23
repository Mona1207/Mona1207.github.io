# 逐题详细解析完善

本目录保存本轮的题目专属讲解、可复现演算和复核清单。

范围是四本教材的独立例题与习题，合计 1,724 题：离散数学 861、线性代数 250、概率论与数理统计 550、物理学下册 63。整组习题页不是额外的独立题，不重复计数。

## 当前状态

以 `data/detailed-solutions-review-ledger.json` 为准；不要使用旧的 `reviewed`、OCR 校订计数或答案存在率代替详细解析的完成率。

- 已有全部 1,724 题的相关易错提示。其中知识点关联的提示标记为 `topic_guidance`，不冒充逐小问复核。
- 本轮逐题核对了物理 63 题，保留 5 道条件或解释依赖约定的题的通式、分支与假设。
- 本轮新增或重写了离散数学、线性代数、概率论共 484 题的专属推导。连同物理 63 题和先前已详细复核的 12 题，累计 559 题，仍有 1,165 题待完成。
- 已逐题覆盖离散数学前三章的习题及例题（40 + 51 + 26 题）、线性代数全书六章全部 250 题（23 + 48 + 37 + 64 + 52 + 26 题）、概率论前三章习题及例题（27 + 38 + 58 题），以及 63 道物理题。其余完成题分布在后续章节，具体以逐题清单为准。
- 另有 20 题的 63 个公式获得穷举真值表，23 题的 47 处矩阵演算获得逐次变换。这些补充不能自动替代原题要求的证明方法或其余小问。
- 全量详细推导尚未完成；清单中的 `all_questions_complete` 保持 `false`。

## 验收标准

每题须逐小问检查：条件与目标、方法的适用性、公式依据、关键中间计算、完整结论、反代或独立检查、与本题有关的易错点。不能只增加“整理条件—套公式—核对”这样的通用段落便标为完成。

含参数的题须讨论除数为零等分支；选择题须解释正确项和关键干扰项；题面条件缺失时保留一般式，不擅自补数值。

## 运行方式

Python 需要 SymPy 1.14.0。公式与视图检查需要 Node.js，以及 `katex`、`react`、`react-dom`，通过 `MONA_QA_DEPENDENCIES` 指定它们所在的 `node_modules` 目录。

在仓库根目录，按下面顺序运行。当前已写入 JSON 的物理详细解析本身是内容源，脚本不会从旧版 APK 自动重建它。

```bash
python3 discrete-math/scripts/solution-authoring/normalize_text.py
python3 discrete-math/scripts/solution-authoring/pitfalls.py
python3 discrete-math/scripts/solution-authoring/physics_pitfalls.py
python3 discrete-math/scripts/solution-authoring/logic_proofs.py
python3 discrete-math/scripts/solution-authoring/matrix_workings.py
python3 discrete-math/scripts/solution-authoring/author_all.py
python3 discrete-math/scripts/solution-authoring/review_ledger.py
python3 discrete-math/scripts/solution-authoring/test_authoring.py
node discrete-math/scripts/solution-authoring/check_math_and_view.cjs
node --check discrete-math/assets/app-ui-v33.js
```

先运行基础规则，再运行专属题目补丁，避免用知识点提示覆盖已人工编写的易错点。每次更改题干后必须重新核对 `detail_review.prompt_sha256`；不能把旧复核结果套到变化后的题面上。

## 发布边界

本轮先保存在内容完善分支，未改线上 v33 的版本信息，未声称现有离线 APK 已包含这些内容。全量完成与发布是两个不同状态。后续正式发布时应更新网页资源地址和离线安装包，保留原题号、笔记和学习记录标识。
