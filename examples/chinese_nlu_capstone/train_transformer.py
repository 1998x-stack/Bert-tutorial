"""Optional real Encoder fine-tuning using a user-provided local checkpoint.

Not executed in the standard-library CI. Requires compatible torch and
transformers dependencies, plus locally available checkpoint/config/tokenizer.

Usage:
  python examples/chinese_nlu_capstone/train_transformer.py \
    --checkpoint ./models/bert-base-chinese --output ./runs/intent-bert
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from pipeline import LABELS, load_rows, metrics, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True, help="Existing local model directory")
    parser.add_argument("--data", type=Path, default=Path(__file__).resolve().parent / "sample.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    if not args.checkpoint.is_dir():
        parser.error("Checkpoint must be an existing local folder; nothing downloads automatically")
    if args.epochs < 1 or args.batch_size < 1 or args.max_length < 8 or args.learning_rate <= 0:
        parser.error("Invalid training configuration")
    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as exc:
        raise SystemExit("Install requirements-optional.txt in an isolated environment") from exc

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    splits = validate(load_rows(args.data))
    label2id = {label: i for i, label in enumerate(LABELS)}
    id2label = {i: label for label, i in label2id.items()}
    tokenizer = AutoTokenizer.from_pretrained(str(args.checkpoint), local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        str(args.checkpoint), num_labels=len(LABELS), id2label=id2label,
        label2id=label2id, local_files_only=True, ignore_mismatched_sizes=True,
    ).to(device)

    def make_loader(rows, shuffle):
        def collate(batch):
            tokens = tokenizer([r["text"] for r in batch], padding=True, truncation=True,
                               max_length=args.max_length, return_tensors="pt")
            tokens["labels"] = torch.tensor([label2id[r["label"]] for r in batch], dtype=torch.long)
            return tokens
        gen = torch.Generator().manual_seed(args.seed)
        return torch.utils.data.DataLoader(rows, batch_size=args.batch_size,
                                           shuffle=shuffle, collate_fn=collate, generator=gen)

    def score(rows):
        model.eval()
        predictions, truths = [], []
        for batch in make_loader(rows, False):
            labels = batch.pop("labels").tolist()
            with torch.no_grad():
                outputs = model(**{k: value.to(device) for k, value in batch.items()})
            truths.extend(LABELS[int(x)] for x in labels)
            predictions.extend(LABELS[int(x)] for x in outputs.logits.argmax(-1).cpu().tolist())
        return metrics(truths, predictions)

    args.output.mkdir(parents=True, exist_ok=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    best_dev = -1.0
    history = []
    for epoch in range(args.epochs):
        model.train()
        total_loss, steps = 0.0, 0
        for batch in make_loader(splits["train"], True):
            optimizer.zero_grad(set_to_none=True)
            result = model(**{k: value.to(device) for k, value in batch.items()})
            result.loss.backward()
            optimizer.step()
            total_loss += float(result.loss.item())
            steps += 1
        dev = score(splits["dev"])
        history.append({"epoch": epoch + 1, "train_loss_mean": total_loss / steps,
                        "dev_macro_f1": dev["macro_f1"]})
        if dev["macro_f1"] > best_dev:
            best_dev = dev["macro_f1"]
            model.save_pretrained(str(args.output))
            tokenizer.save_pretrained(str(args.output))

    # Evaluate TEST exactly once, on dev-selected checkpoint.
    model = AutoModelForSequenceClassification.from_pretrained(
        str(args.output), local_files_only=True
    ).to(device)
    test = score(splits["test"])
    report = {
        "disclaimer": "Synthetic toy labels/texts; not production Chinese NLU quality",
        "checkpoint": str(args.checkpoint), "seed": args.seed, "device": str(device),
        "labels": list(LABELS), "epochs": args.epochs,
        "max_length": args.max_length, "batch_size": args.batch_size,
        "learning_rate": args.learning_rate, "history": history, "test": test,
    }
    (args.output / "run-report.json").write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"best_dev_macro_f1": best_dev,
                      "test_macro_f1": test["macro_f1"],
                      "disclaimer": report["disclaimer"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
