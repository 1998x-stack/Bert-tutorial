"""Offline Chinese NLU baseline: contract, training, dev, test, export.

Standard library only. The synthetic fixtures are not a production benchmark.
This character n-gram Naive Bayes is not a BERT implementation.
"""
from __future__ import annotations
import argparse
import collections
import json
import math
from pathlib import Path

LABELS = ("food", "greeting", "weather")
SPLITS = ("train", "dev", "test")
HERE = Path(__file__).resolve().parent


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def validate(rows: list[dict]) -> dict[str, list[dict]]:
    if not rows:
        raise ValueError("empty dataset")
    ids, seen_texts, group_split = set(), {}, {}
    by_split = {split: [] for split in SPLITS}
    for row in rows:
        if not isinstance(row, dict) or not {"id", "text", "label", "group", "split"} <= row.keys():
            raise ValueError("every row needs id, text, label, group, split")
        rid, text, label, group, split = (row[k] for k in ("id", "text", "label", "group", "split"))
        if (not all(isinstance(x, str) and x.strip() for x in (rid, text, label, group, split))
                or label not in LABELS or split not in SPLITS):
            raise ValueError("invalid row field, label or split")
        if rid in ids:
            raise ValueError(f"duplicate id: {rid}")
        ids.add(rid)
        if group in group_split and group_split[group] != split:
            raise ValueError(f"group leaked across splits: {group}")
        group_split[group] = split
        normalized = "".join(text.split())
        if normalized in seen_texts and seen_texts[normalized] != split:
            raise ValueError(f"exact text leaked across splits: {text}")
        seen_texts[normalized] = split
        by_split[split].append(row)
    for split, items in by_split.items():
        if {x["label"] for x in items} != set(LABELS):
            raise ValueError(f"{split} must include every target label")
    return by_split


def features(text: str) -> collections.Counter[str]:
    chars = [ch for ch in text if not ch.isspace()]
    if not chars:
        raise ValueError("empty string after whitespace removal")
    result = collections.Counter("1:" + ch for ch in chars)
    result.update("2:" + chars[i] + chars[i + 1] for i in range(len(chars) - 1))
    return result


def train(rows: list[dict]) -> dict:
    if not rows or {row["label"] for row in rows} != set(LABELS):
        raise ValueError("train requires all labels")
    label_counts = collections.Counter(x["label"] for x in rows)
    total_counts = {label: collections.Counter() for label in LABELS}
    for row in rows:
        total_counts[row["label"]].update(features(row["text"]))
    vocab = sorted({token for count in total_counts.values() for token in count})
    return {"schema_version": 1, "labels": list(LABELS), "label_counts": dict(label_counts),
            "token_counts": {label: dict(total_counts[label]) for label in LABELS},
            "vocabulary": vocab, "alpha": 1.0, "model_type": "char_ngram_multinomial_nb_toy"}


def predict_proba(model: dict, text: str) -> dict[str, float]:
    feats = features(text)
    vocab = set(model["vocabulary"])
    total_rows = sum(model["label_counts"].values())
    alpha = float(model["alpha"])
    scores = {}
    for label in model["labels"]:
        cls_count = model["label_counts"][label]
        freq = model["token_counts"][label]
        total_tokens = sum(freq.values())
        denominator = total_tokens + alpha * len(vocab)
        score = math.log((cls_count + 1) / (total_rows + len(LABELS)))
        score += sum(count * math.log((freq.get(token, 0) + alpha) / denominator)
                     for token, count in feats.items() if token in vocab)
        scores[label] = score
    maximum = max(scores.values())
    exp = {label: math.exp(v - maximum) for label, v in scores.items()}
    z = sum(exp.values())
    return {label: exp[label] / z for label in model["labels"]}


def predict(model: dict, text: str) -> str:
    scores = predict_proba(model, text)
    return max(model["labels"], key=lambda label: scores[label])


def metrics(y_true: list[str], y_pred: list[str]) -> dict:
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("equal-length nonempty labels required")
    if any(x not in LABELS for x in y_true + y_pred):
        raise ValueError("unknown prediction or label")
    confusion = {true: {pred: 0 for pred in LABELS} for true in LABELS}
    for truth, pred in zip(y_true, y_pred):
        confusion[truth][pred] += 1
    per_label = {}
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in LABELS if other != label)
        fn = sum(confusion[label][other] for other in LABELS if other != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_label[label] = {"precision": precision, "recall": recall, "f1": f1, "support": tp + fn}
    return {"accuracy": sum(a == b for a, b in zip(y_true, y_pred)) / len(y_true),
            "macro_f1": sum(per_label[x]["f1"] for x in LABELS) / len(LABELS),
            "per_label": per_label, "confusion": confusion, "sample_count": len(y_true)}


def evaluate(model: dict, rows: list[dict]) -> dict:
    return metrics([x["label"] for x in rows], [predict(model, x["text"]) for x in rows])


def run(dataset: Path, output: Path) -> dict:
    data = validate(load_rows(dataset))
    model = train(data["train"])
    # Hyperparameters are fixed in this toy; test is touched only after training.
    report = {"disclaimer": "SYNTHETIC TEACHING DATA, not real production NLU evaluation",
              "labels": list(LABELS),
              "counts": {split: len(rows) for split, rows in data.items()},
              "dev": evaluate(model, data["dev"]), "test": evaluate(model, data["test"])}
    output.mkdir(parents=True, exist_ok=True)
    (output / "model.json").write_text(json.dumps(model, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=HERE / "sample.jsonl")
    parser.add_argument("--output", type=Path, default=HERE / "outputs")
    parser.add_argument("--predict", type=str, default=None)
    args = parser.parse_args()
    report = run(args.data, args.output)
    print("Toy report:", json.dumps({"dev_macro_f1": report["dev"]["macro_f1"],
                                     "test_macro_f1": report["test"]["macro_f1"]}, ensure_ascii=False))
    if args.predict:
        model = json.loads((args.output / "model.json").read_text(encoding="utf-8"))
        print("Toy prediction:", json.dumps({"label": predict(model, args.predict),
                                              "probabilities": predict_proba(model, args.predict)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
