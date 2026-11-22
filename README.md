# BERT 模型系列教程

一套从语言表示学习、Transformer Encoder、BERT 原始论文到模型家族演进与中文 NLU 工程实践的中文课程。课程包含 **28 个章节**，其中前二十篇已升级为可独立阅读的专题精读文章。

## 在线入口

- **课程首页**：https://1998x-stack.github.io/Bert-tutorial/
- **二十篇专题精读**：https://1998x-stack.github.io/Bert-tutorial/articles/
- [01 · 从词向量到上下文预训练](articles/01-pretraining-evolution.html)
- [02 · Transformer Encoder 计算路径](articles/02-transformer-encoder.html)
- [03 · BERT 预训练与 MLM](articles/03-bert-pretraining.html)
- [04 · BERT 下游微调与实验解读](articles/04-bert-finetuning-evidence.html)
- [05 · WordPiece 与输入表示](articles/05-wordpiece-inputs.html)
- [06 · MLM、WWM、SpanBERT、NSP 与 SOP](articles/06-mlm-nsp-masking-objectives.html)
- [07 · BERT 微调实战与评估协议](articles/07-bert-finetuning-practice.html)
- [08 · RoBERTa 训练配方与消融](articles/08-roberta-training-recipe.html)
- [09 · 预训练数据工程](articles/09-pretraining-data-engineering.html)
- [10 · AdamW、Warmup 与超参数](articles/10-bert-optimization-hyperparameters.html)
- [11 · 规模效应、Chinchilla 的 Encoder 适用边界](articles/11-encoder-scaling-compute.html)
- [12 · 混合精度、梯度与 FlashAttention](articles/12-numerical-stability-attention.html)
- [13 · mBERT、XLM-R 与零样本迁移](articles/13-multilingual-transfer.html)
- [14 · 模型选型与统一评估协议](articles/14-encoder-model-selection.html)
- [15 · ELECTRA 的 Generator、Discriminator 与 RTD](articles/15-electra-replaced-token-detection.html)
- [16 · XLNet：排列模型与双流注意力](articles/16-xlnet-permutation-language-model.html)
- [17 · MPNet：排列预测与位置补偿](articles/17-mpnet-masked-permuted.html)
- [18 · ALBERT：参数分解、共享与 SOP](articles/18-albert-factorized-sharing.html)
- [19 · DeBERTa：解耦相对位置注意力](articles/19-deberta-disentangled-attention.html)
- [20 · 中文 BERT：全词掩码与中文模型变体](articles/20-chinese-bert-whole-word-masking.html)

## 学习路线

| 阶段 | 章节 | 学习目标 |
|---|---:|---|
| 基础与架构 | 01–02 | 从静态表示走到上下文表示，理解 Transformer Encoder 的计算路径 |
| 原始 BERT 机制 | 03–06 | 理解 MLM、NSP、输入表示、遮盖策略与目标函数 |
| 微调与训练配方 | 07–10 | 掌握分类、序列标注、问答、RoBERTa、数据工程和优化配置 |
| 数据规模与工程 | 11–14 | 研究 scaling、训练稳定性、多语言迁移和模型选型 |
| 模型家族与变体 | 15–19 | 比较 ELECTRA、XLNet、MPNet、ALBERT 与 DeBERTa |
| 中文与长文本 | 20–22 | 研究中文预训练、长文档注意力和句向量 |
| 轻量化与部署 | 23–27 | 掌握蒸馏、移动端、参数高效微调、量化和推理优化 |
| 综合项目 | 28 | 构建可复现的端到端中文 NLU 流水线 |

## 仓库结构

    .
    ├── index.html                       # 课程门户、学习路线与离线目录
    ├── courses.json                     # 28 章课程元数据（唯一目录源）
    ├── 01.html ... 20.html              # 旧链接兼容页，重定向到专题文章
    ├── 21.html ... 28.html              # 既有课程章节
    ├── articles/
    │   ├── index.html                   # 二十篇专题入口
    │   ├── 01-*.html ... 20-*.html      # 二十篇独立精读文章
    │   ├── evidence-01.json ... 20.json # 逐篇事实与来源账本
    │   └── article.css                  # 旧样式路径兼容桥
    ├── assets/
    │   ├── css/course.css               # 首页与专题共用设计系统
    │   ├── js/site.js                   # 目录、进度与专题交互
    │   └── diagrams/                    # 二十篇专题专属 SVG 图解
    ├── examples/                        # 标准库教学参考实现（含 Encoder 预算、采样、RTD 标签及模型变体机制）
    ├── pdfs/                            # 论文原文
    ├── tests/                           # Node、Python 与 Playwright 验收
    ├── .github/workflows/quality.yml    # 自动化质量门禁
    └── docs/improvements.md             # 审计、决策与验证记录

## 本地运行

不需要构建工具或 CDN。可以直接打开 index.html；也可以启动静态服务器：

    python -m http.server 8000
    # 打开 http://localhost:8000

课程首页在 HTTP/HTTPS 下读取 courses.json，在 file:// 模式下使用内嵌 JSON 快照。两份目录数据由测试强制保持一致。专题 CSS、JS 和 SVG 均为仓库内资源。

## 质量检查

需要 Node.js 22+、Python 3.10+ 和 Chromium：

    npm install
    npm test
    python -m unittest discover -s tests -p "test_*.py" -v
    npx playwright install chromium
    npm run test:browser

GitHub Actions 在 push、pull request 和手动触发时运行目录测试、文章结构测试、Python 单元测试，以及 HTTP / file:// 浏览器检查。浏览器测试覆盖首页搜索与阶段筛选、进度交互、二十篇专题交互、MathML 渲染和 1440 / 768 / 390 / 360 px 布局；截图作为 workflow artifact 保存。是否通过以实际 workflow run 为准。

## 内容与事实标准

- 每篇文章必须从问题定义开始，补齐读者理解主题所需的上下文、术语、公式、输入输出和适用边界。
- 不用“论文介绍了……”代替技术解释；文章应能被没有阅读过其他章节的人独立理解。
- 论文报告结果必须同时注明模型、数据集版本、切分、指标、模型数量、额外数据和原文表格位置。
- 论文事实、作者解释、教学示意和工程建议分开表述；未实际运行的实验不写成复现结果。
- 每篇专题使用独立图解和交互示例；示意数据必须明确标为示意。
- articles/evidence-XX.json 为逐篇来源账本，记录可核查的 claim、原始 URL、章节/表格定位和核验说明。
- 真实工程应使用与 checkpoint 配套的 tokenizer、词表和配置；玩具示例不替代官方实现。

## 兼容与迁移

根目录的 01.html–20.html 保留为兼容入口，自动转向升级后的 articles/ 专题页面。第 21–28 章和论文 PDF 暂时保留原路径，避免一次性移动造成旧链接失效；后续章节迁移沿用相同的独立文章标准。

## 贡献

欢迎提交术语修正、公式勘误、原文定位、可复现实验和浏览器兼容性问题。涉及论文数字的修改，请附模型配置、数据集版本、指标、切分条件和原始表格/章节定位。
