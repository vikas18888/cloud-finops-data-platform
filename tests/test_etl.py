import sys, unittest
import pandas as pd
sys.path.insert(0, "src")
from ingest_billing import parse_dates, parse_tags, transform

class TestETL(unittest.TestCase):
    def test_mixed_date_formats(self):
        out = parse_dates(pd.Series(["2026-08-05", "2026/08/05", "05/08/2026", "garbage"]))
        self.assertEqual(out.iloc[0], out.iloc[1]); self.assertEqual(out.iloc[1], out.iloc[2]); self.assertTrue(pd.isna(out.iloc[3]))
    def test_tags(self):
        self.assertEqual(parse_tags('{"team": "ml"}'), {"team": "ml"}); self.assertEqual(parse_tags(""), {}); self.assertEqual(parse_tags("{bad"), {})
    def test_transform_quarantines_bad_rows_and_dedupes(self):
        base = dict(usage_date="2026-08-01", account_id="1", region="r", service="AmazonEC2", resource_id="x", tags="")
        df = pd.DataFrame([dict(base, line_item_id="a", unblended_cost=1.0), dict(base, line_item_id="a", unblended_cost=1.0),
                           dict(base, line_item_id="b", unblended_cost=-5.0), dict(base, line_item_id="c", unblended_cost=None)])
        clean, quar, stats = transform(df)
        self.assertEqual(len(clean), 1); self.assertEqual(len(quar), 2); self.assertEqual(stats["duplicates_removed"], 1)

if __name__ == "__main__":
    unittest.main()
