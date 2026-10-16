import unittest
import pandas as pd
from src.clean import load_crashes, parse_hhmm, time_period, summarize, tableau_export, model_frame


class DataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df, cls.quality = load_crashes()

    def test_snapshot_totals(self):
        self.assertEqual(self.quality['rows'], 81261)
        self.assertEqual(self.quality['severe_crashes'], 8774)
        self.assertEqual(self.quality['unique_crashes'], 81261)

    def test_invalid_times_are_not_shifted_into_another_day(self):
        hour, minute = parse_hhmm(pd.Series(['0', '59', '100', '2359', '1260', '2400', '2500', None, '101.5']))
        self.assertEqual(hour.iloc[:4].tolist(), [0, 0, 1, 23])
        self.assertEqual(minute.iloc[:4].tolist(), [0, 59, 0, 59])
        self.assertTrue(hour.iloc[4:].isna().all())
        self.assertEqual(self.quality['invalid_time_rows'], 65)

    def test_period_boundaries(self):
        periods = time_period(pd.Series([0, 4, 5, 9, 10, 14, 15, 18, 19, 23])).tolist()
        self.assertEqual(periods, ['Late Night']*2 + ['Morning Rush']*2 + ['Midday']*2 + ['Evening Rush']*2 + ['Night']*2)

    def test_city_aggregation_conserves_counts(self):
        summary = summarize(self.df, ['CITY'])
        self.assertEqual(int(summary.crashes.sum()), 81261)
        self.assertEqual(int(summary.severe_crashes.sum()), 8774)

    def test_tableau_denominator_and_schema(self):
        export = tableau_export(self.df)
        expected = self.df.HAS_COORDINATES & self.df.HOUR.notna()
        self.assertEqual(len(export), int(expected.sum()))
        self.assertEqual(export.collision_severity_binary.sum(), self.df.loc[expected, 'IS_SEVERE'].sum())
        self.assertFalse(export[['POINT_X', 'POINT_Y', 'hour', 'time_period']].isna().any().any())
        self.assertEqual(len(export.columns), 17)

    def test_model_target_and_time_flags(self):
        frame = model_frame(self.df)
        self.assertTrue(frame.IS_SEVERE.eq(pd.to_numeric(frame.COLLISION_SEVERITY).isin([1, 2])).all())
        self.assertTrue(frame.IS_LATE_NIGHT.eq(frame.HOUR.isin([20, 21, 22, 23, 0])).all())


if __name__ == '__main__':
    unittest.main()
