# 📖 BERT 模型系列 · 从入门到精通

> 📘 28章 实战体系 · 交互式 HTML 课程

> **English TL;DR:** An all-Chinese 28-chapter course on the **BERT model family** — from the 2018 breakthrough (MLM + NSP) through the encoder family tree that followed: RoBERTa, ELECTRA, XLNet, MPNet, ALBERT, DeBERTa, Chinese ERNIE/WWM, Longformer/BigBird, SimCSE, distillation (DistilBERT/TinyBERT/MobileBERT), and efficient fine-tuning (LoRA/AdaLoRA/BitFit) — ending with ModernBERT & edge-compressed end-to-end. Covers pretraining recipes, data/scale effects, training stability, multilingual transfer, and a real Chinese NLU capstone.

## 📖 课程简介

本课程围绕 **BERT 及其衍生模型家族**做系统性精读与实践：从 NLP 预训练简史与 Transformer 精讲切入，逐篇精读 BERT 开山论文（MLM/NSP/微调范式），再按家族演进线覆盖 RoBERTa（训练配方革命）、ELECTRA（判别式）、XLNet/MPNet、ALBERT（参数高效）、DeBERTa（解耦注意力）与中文生态 ERNIE/WWM，加上长文本、句向量、蒸馏、移动端部署与高效微调（LoRA/BitFit），最终以 ModernBERT 前沿与端到端中文 NLU 项目收束。

## 🚀 快速开始

```bash
open index.html   # macOS，纯静态即开即看
```

## 📂 项目结构

```text
Bert-tutorial/
├── index.html / 01.html ~ 28.html / courses.json / theme.css
```

## 📖 章节目录（阶段映射）

| 阶段 | 章节 | 核心 |
|------|------|------|
| **铺垫** | 01–04 | NLP 预训练简史、Transformer、BERT 开山论文精读 |
| **机制** | 05–06 | 输入表示/分词、MLM 与 NSP 深度剖析 |
| **微调与配方** | 07–11 | 微调范式、RoBERTa、数据工程、超参/优化、scaling |
| **训练技术** | 12–13 | 训练稳定性、多语言/零样本 |
| **家族横评** | 14–19 | 变体生态、ELECTRA、XLNet、MPNet、ALBERT、DeBERTa |
| **中文+长文** | 20–21 | ERNIE/WWW、Longformer/LongBigBird |
| **句向量+轻量** | 22–25 | SimCL/SBERT、蒸馏、移动部署、高效微调 |
| **前沿+实战** | 26–28 | ModernBERT、极致压缩、端到端中文 NLU |

## ✨ 亮点

- 唯一按「开山本义 → 家族谱系 → 部署/前沿」组织的 BERT 课程
- 中文生态（ERNIE / WWM）+ 极致压缩（EI-BERT 1.91MB）覆盖完整
- 端到端实战：预训练→微调→蒸馏→部署（电商评论分析）

## 🎯 前置知识

- 适合：NLP 学习者 / 预训练模型工程师
- 建议具备：PyTorch + Transformer 基础概念

## ✨ 特色

- 从 2018 开山到 2025 ModernBERT 的全谱系
- 即开即用纯静态 HTML

---
*本课程由 `Bert-tutorial/` 项目维护。*