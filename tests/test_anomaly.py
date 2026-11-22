import sys, unittest
import numpy as np, pandas as pd
sys.path.insert(0, "src")
from anomaly_engine import detect

class TestAnomaly(unittest.TestCase):
    def test_flat_series_has_no_anomalies(self):
        s = pd.Series(100 + np.random.RandomState(0).normal(0, 2, 60), index=pd.date_range("2026-01-01", periods=60).astype(str))
        self.assertFalse(detect(s).is_anomaly.any())
    def test_spike_is_flagged(self):
        s = pd.Series(100 + np.random.RandomState(0).normal(0, 2, 60), index=pd.date_range("2026-01-01", periods=60).astype(str))
        s.iloc[40] = 400
        r = detect(s); self.assertTrue(r.is_anomaly.iloc[40]); self.assertEqual(r.is_anomaly.sum(), 1)
    def test_spike_not_masked_by_itself(self):
        s = pd.Series([100.0] * 20 + [1000.0]); s.index = pd.date_range("2026-01-01", periods=21).astype(str)
        s.iloc[:20] += np.arange(20) % 3
        self.assertTrue(detect(s).is_anomaly.iloc[-1])

if __name__ == "__main__":
    unittest.main()
