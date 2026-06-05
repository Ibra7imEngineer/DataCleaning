import unittest
import pandas as pd
from date_cleaning import clean_datetime_columns


class TestDateCleaning(unittest.TestCase):
    def test_strips_zeroed_time_and_formats_dates(self):
        df = pd.DataFrame(
            {
                "Order_Date": ["2024-01-15 14:30:00", "2024-02-20 00:00:00"],
            }
        )

        cleaned_df, anomalies_df = clean_datetime_columns(df, ["Order_Date"])

        self.assertEqual(cleaned_df.loc[0, "Order_Date"], "2024-01-15")
        self.assertEqual(cleaned_df.loc[1, "Order_Date"], "2024-02-20")
        self.assertEqual(set(anomalies_df["action_taken"].tolist()), {"Stripped Time"})
        self.assertEqual(len(anomalies_df), 2)

    def test_extracts_embedded_dates_and_coerces_text(self):
        df = pd.DataFrame(
            {
                "Delivery_Date": [
                    "تم التسليم في 2024-09-22",
                    "N/A",
                    "تم الشحن 27\\7\\2024",
                ]
            }
        )

        cleaned_df, anomalies_df = clean_datetime_columns(df, ["Delivery_Date"])

        self.assertEqual(cleaned_df.loc[0, "Delivery_Date"], "2024-09-22")
        self.assertTrue(pd.isna(cleaned_df.loc[1, "Delivery_Date"]))
        self.assertEqual(cleaned_df.loc[2, "Delivery_Date"], "2024-07-27")
        self.assertIn("Extracted Embedded Date", anomalies_df["action_taken"].tolist())
        self.assertIn("Coerced Text to Null", anomalies_df["action_taken"].tolist())

    def test_corrects_three_digit_year_typo(self):
        df = pd.DataFrame(
            {
                "Invoice_Date": ["01/01/224", "15-03-124", "2024-08-25"],
            }
        )

        cleaned_df, anomalies_df = clean_datetime_columns(df, ["Invoice_Date"])

        self.assertEqual(cleaned_df.loc[0, "Invoice_Date"], "2024-01-01")
        self.assertIn("Corrected Year Typo", anomalies_df["action_taken"].tolist())

    def test_chronology_flag_detects_invalid_sequence(self):
        df = pd.DataFrame(
            {
                "Order_Date": ["2024-01-10", "2024-01-20"],
                "Expected_Delivery": ["2024-01-15", "2024-01-15"],
                "Actual_Delivery": ["2024-01-18", "2024-01-14"],
            }
        )

        cleaned_df, anomalies_df = clean_datetime_columns(
            df,
            ["Order_Date", "Expected_Delivery", "Actual_Delivery"],
            chronology_sequence=["Order_Date", "Expected_Delivery", "Actual_Delivery"],
        )

        self.assertFalse(cleaned_df.loc[0, "is_chronology_invalid"])
        self.assertTrue(cleaned_df.loc[1, "is_chronology_invalid"])
        self.assertTrue((anomalies_df["action_taken"] == "Chronology Invalid").any())


if __name__ == "__main__":
    unittest.main()
