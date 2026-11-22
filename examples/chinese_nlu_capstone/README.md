# 中文 NLU 最小可复现项目

这一目录对应课程第 28 章。**sample.jsonl 全部为人工构造的 60 条合成文本，不含真实用户语料，不代表生产准确率。**

## 纯标准库离线基线

在仓库根目录运行：

```bash
python examples/chinese_nlu_capstone/pipeline.py --data examples/chinese_nlu_capstone/sample.jsonl --output /tmp/chinese-nlu-toy --predict "今晚想吃面"
python -m unittest discover -s tests -p 'test_*.py' -v
```

输出 `/tmp/chinese-nlu-toy/model.json` 和 `report.json`。基线是字符 unigram/bigram Multinomial Naive Bayes，**不是 BERT**。只用于可执行地验证数据契约、划分、防泄漏、训练、评估与输出路径；无需安装依赖，也不访问网络。

## 可选：真正的 BERT / Encoder 微调

1. 准备自己有权使用、已下载的本地模型目录，包含权重、config 与完全匹配的 tokenizer；在单独环境安装指定依赖。对于 CUDA/CPU 安装应选择与目标环境兼容的 Torch wheel。
2. 用训练集更新分类模型，dev 上选择 checkpoint，冻结后评估 test。脚本会导出模型、tokenizer、label2id/id2label 与运行报告。

```bash
python -m pip install -r examples/chinese_nlu_capstone/requirements-optional.txt
python examples/chinese_nlu_capstone/train_transformer.py --checkpoint ./models/bert-base-chinese --data examples/chinese_nlu_capstone/sample.jsonl --output ./runs/intent-bert-toy --epochs 2 --batch-size 8 --max-length 128 --seed 2026
```

**可选脚本未在仓库 CI 中实际执行，也没有提供可下载的模型权重。** 需要用户自行提供合法 checkpoint 并按本机环境检验 dependencies。别把教学语料输出视为中文业务 benchmark。

## 数据合同与防泄漏

每行 JSONL 至少包含 `id,text,label,group,split`。三个标签固定为 `food,greeting,weather`，切分为 `train/dev/test`。标准库校验拒绝重复 ID、跨 split 的 group、跨 split 的完全重复文本、未知标签、空字段和某个 split 缺类别。每条合成句子都拥有独立 group，这不等同于针对真实语料的近重复检测能力。

实际数据需要来源许可、采集时间、主体/用户/文档分组、近重复治理、隐私脱敏与标注复审。先按来源或时间切分，随后只在 train 构造数据增强；dev 用于调参、选模型和拒识阈值，test 只用于冻结模型的单次正式评价。

## 评估、部署和验收

保存每类 precision、recall、F1、support、Macro F1、accuracy 与 confusion matrix；训练与推理的 label mapping 严格一致。服务文件需包含完整模型及 tokenizer、配置、依赖锁定、数据版本、checksum、部署硬件、最大长度和预处理规则。生产使用前还需要 OOD/unknown 策略、拒识阈值、人工确认、p50/p95 与内存峰值测试、错误分析及回滚方案。

只可声称基线代码与自动化测试实际执行的检查结果；不能把 CI 的合成示例分数写成真实业务质量。
