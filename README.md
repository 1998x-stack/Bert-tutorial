# BERT 模型系列教程

一套从 Transformer Encoder、BERT 原始论文到 BERT 家族演进与中文 NLU 实践的中文课程。课程由 28 个章节组成，并新增五篇独立专题精读文章。

## 在线阅读

- **课程首页**：https://1998x-stack.github.io/Bert-tutorial/
- **五篇专题精读**：https://1998x-stack.github.io/Bert-tutorial/articles/
- [专题 01：从词向量到上下文预训练](articles/01-pretraining-evolution.html)
- [专题 02：Transformer Encoder 的计算路径](articles/02-transformer-encoder.html)
- [专题 03：BERT 预训练与 MLM](articles/03-bert-pretraining.html)
- [专题 04：BERT 下游微调与实验解读](articles/04-bert-finetuning-evidence.html)
- [专题 05：WordPiece 与输入表示](articles/05-wordpiece-inputs.html)

## 仓库结构

```text
.
├── index.html                 # 课程门户与离线目录
├── courses.json               # 28 章唯一目录数据源
├── theme.css                 # 既有课程章节主题
├── 01.html ... 28.html        # 28 章课程正文
├── articles/
│   ├── index.html            # 五篇专题入口
│   ├── article.css           # 专题文章设计系统
│   ├── 01-*.html ... 05-*.html
│   └── evidence-*.json       # 每篇文章的来源账本
├── pdfs/                     # 论文原文
├── docs/                     # 维护与改进记录
└── tests/                    # 离线目录一致性测试
```

## 学习路线

1. 先读 01–02，建立表示学习与 Transformer Encoder 的计算直觉。
2. 再读 03–05，理解 BERT 的训练目标、下游接口与输入构造。
3. 回到 06–14，研究训练配方、数据规模、稳定性与模型变体。
4. 继续 15–25，比较 ELECTRA、XLNet、MPNet、DeBERTa、长文本、句向量、蒸馏与高效微调。
5. 最后完成 26–28 的现代编码器、端侧压缩与端到端项目。

## 本地运行

无需构建步骤。直接打开 `index.html` 即可浏览 28 章课程；专题文章可从 `articles/index.html` 打开。也可启动静态服务器：

```bash
python -m http.server 8000
# http://localhost:8000
```

## 质量与事实边界

- 论文中的结论以原始论文为准；专题页在文末链接论文或官方文档，并在 `articles/evidence-*.json` 中登记来源。
- 教学示意、公式推导、论文报告结果与工程实践建议分开表述。
- 不把跨论文排行榜数字当作受控实验；没有完整实验条件时不宣称复现了论文结果。
- 目录数据以 `courses.json` 为准，首页保留离线嵌入数据以支持 `file://` 打开。

## 贡献

欢迎提交术语修正、公式勘误、可复现实验和浏览器兼容性问题。涉及论文数值的修改请附原文表格/章节定位与模型、数据集、指标、切分条件。
