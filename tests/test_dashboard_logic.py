from pathlib import Path
import sys
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from decision import recommend
from metrics import build_model_summary


class DashboardLogicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = pd.read_csv(ROOT / "data" / "evaluation_results.csv")
        cls.summary = build_model_summary(cls.results)

    def test_required_models_exist(self):
        self.assertEqual({"Current Model", "Candidate Model"}, set(self.summary.index))

    def test_summary_includes_all_five_requirement_groups(self):
        expected = {"quality_score", "critical_error_rate", "cost_per_acceptable", "p95_latency_ms", "reliability_score"}
        self.assertTrue(expected.issubset(self.summary.columns))

    def test_candidate_is_cheaper_and_faster(self):
        current = self.summary.loc["Current Model"]
        candidate = self.summary.loc["Candidate Model"]
        self.assertLess(candidate.cost_per_acceptable, current.cost_per_acceptable)
        self.assertLess(candidate.p95_latency_ms, current.p95_latency_ms)

    def test_critical_risk_prevents_full_promotion(self):
        self.assertEqual("USE SELECTIVELY", recommend(self.summary)["recommendation"])


if __name__ == "__main__":
    unittest.main()

