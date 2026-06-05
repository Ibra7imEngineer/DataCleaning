import unittest
import pandas as pd
import app


class TestAppNumericConversion(unittest.TestCase):
    def test_enforce_strict_numeric_candidates_converts_numeric_strings(self):
        df = pd.DataFrame(
            {
                "price": ["100", "200", None],
                "name": ["Alice", "Bob", "Carol"],
            }
        )

        result = app.enforce_strict_numeric_candidates(df.copy())

        self.assertTrue(pd.api.types.is_float_dtype(result["price"]))
        self.assertEqual(result.loc[0, "price"], 100.0)
        self.assertEqual(result.loc[1, "price"], 200.0)
        self.assertTrue(pd.isna(result.loc[2, "price"]))

    def test_enforce_strict_numeric_candidates_leaves_mixed_text(self):
        df = pd.DataFrame(
            {
                "amount": ["100", "invalid", "300"],
            }
        )

        result = app.enforce_strict_numeric_candidates(df.copy())

        self.assertFalse(pd.api.types.is_numeric_dtype(result["amount"]))
        self.assertEqual(result.loc[0, "amount"], "100")
        self.assertEqual(result.loc[1, "amount"], "invalid")
        self.assertEqual(result.loc[2, "amount"], "300")


if __name__ == "__main__":
    unittest.main()
