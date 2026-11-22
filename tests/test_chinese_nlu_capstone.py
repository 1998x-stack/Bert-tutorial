"""Offline tests for the chapter-28 synthetic Chinese NLU capstone."""
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT = ROOT / "examples" / "chinese_nlu_capstone"
spec = importlib.util.spec_from_file_location("chinese_nlu_capstone_pipeline", PROJECT / "pipeline.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = lab.load_rows(PROJECT / "sample.jsonl")
        cls.splits = lab.validate(cls.rows)

    def test_three_splits_contain_every_label(self):
        self.assertEqual(len(self.rows), 60)
        for split in ("train", "dev", "test"):
            self.assertEqual({r["label"] for r in self.splits[split]}, set(lab.LABELS))

    def test_group_cross_split_rejected(self):
        rows = [dict(r) for r in self.rows]
        rows[1]["group"] = rows[0]["group"]
        rows[1]["split"] = "dev"
        with self.assertRaises(ValueError):
            lab.validate(rows)

    def test_duplicate_id_rejected(self):
        rows = [dict(r) for r in self.rows]
        rows[1]["id"] = rows[0]["id"]
        with self.assertRaises(ValueError):
            lab.validate(rows)

    def test_duplicate_text_cross_split_rejected(self):
        rows = [dict(r) for r in self.rows]
        rows[1]["text"] = rows[0]["text"]
        rows[1]["split"] = "dev"
        with self.assertRaises(ValueError):
            lab.validate(rows)

    def test_invalid_label_rejected(self):
        rows = [dict(r) for r in self.rows]
        rows[0]["label"] = "unknown"
        with self.assertRaises(ValueError):
            lab.validate(rows)


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        by_split = lab.validate(lab.load_rows(PROJECT / "sample.jsonl"))
        cls.train = by_split["train"]
        cls.model = lab.train(cls.train)

    def test_fixed_labels(self):
        self.assertEqual(self.model["labels"], list(lab.LABELS))

    def test_probability_sum(self):
        scores = lab.predict_proba(self.model, "今天晚上会下雨吗")
        self.assertEqual(set(scores), set(lab.LABELS))
        self.assertAlmostEqual(sum(scores.values()), 1.0, places=12)
        self.assertTrue(all(0.0 <= v <= 1.0 for v in scores.values()))

    def test_train_deterministic(self):
        self.assertEqual(self.model, lab.train(self.train))
        self.assertEqual(lab.predict(self.model, "你好呀"), lab.predict(self.model, "你好呀"))

    def test_macro_f1_handles_absent_predictions(self):
        result = lab.metrics(["food", "greeting", "weather"], ["food", "food", "food"])
        self.assertEqual(result["sample_count"], 3)
        self.assertAlmostEqual(result["macro_f1"], 1.0 / 6.0)
        self.assertEqual(result["per_label"]["weather"]["f1"], 0.0)

    def test_artifact_export(self):
        with tempfile.TemporaryDirectory() as folder:
            report = lab.run(PROJECT / "sample.jsonl", pathlib.Path(folder))
            model = json.loads((pathlib.Path(folder) / "model.json").read_text(encoding="utf-8"))
            exported = json.loads((pathlib.Path(folder) / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(exported, report)
            self.assertEqual(model["labels"], list(lab.LABELS))
            self.assertTrue(0 <= report["dev"]["macro_f1"] <= 1)
            self.assertTrue(0 <= report["test"]["macro_f1"] <= 1)


if __name__ == "__main__":
    unittest.main()
