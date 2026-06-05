import pandas as pd
import numpy as np
from stats.advanced_imputation import universal_missing_value_imputation, streamlit_imputation_style


def test_universal_missing_value_imputation_basic():
    df = pd.DataFrame({
        'Item Name': ['Coffee', 'Coffee', 'Tea', 'Tea', 'Bread', 'Bread', None],
        'Category': ['Beverage', 'Beverage', None, 'Beverage', 'Bakery', None, None],
        'Department': ['Drinks', 'Drinks', 'Drinks', 'Drinks', 'Food', 'Food', 'Food'],
        'Price': [5.0, np.nan, 3.0, np.nan, 2.5, np.nan, np.nan],
        'OrderID': ['A', 'A', 'B', 'B', 'C', 'C', 'C'],
    })

    imputed = universal_missing_value_imputation(
        df,
        numeric_cols_to_fill=['Price'],
        categorical_cols_to_fill=['Category'],
        fine_grain_guide='Item Name',
        coarse_grain_guide='Department',
    )

    assert imputed.loc[1, 'Price'] == 5.0
    assert imputed.loc[1, 'Price_imputation_status'] == 'Filled by Item Context'
    assert imputed.loc[3, 'Price'] == 3.0
    assert imputed.loc[3, 'Price_imputation_status'] == 'Filled by Item Context'
    assert imputed.loc[5, 'Category'] == 'Bakery'
    assert imputed.loc[5, 'Category_imputation_status'] == 'Filled by Item Context'
    assert imputed.loc[6, 'Category_imputation_status'] in {
        'Filled by Category Fallback',
        'Filled by Sequential Neighbor',
        'Populated',
    }
    styler = streamlit_imputation_style(
        imputed,
        status_cols=['Price_imputation_status', 'Category_imputation_status'],
    )
    assert hasattr(styler, 'to_html')


if __name__ == '__main__':
    test_universal_missing_value_imputation_basic()
    print('test_universal_missing_value_imputation_basic passed')
