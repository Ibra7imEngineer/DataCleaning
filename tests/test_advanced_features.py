"""
═══════════════════════════════════════════════════════════════════════════════
    QUICK TEST FILE FOR ADVANCED FEATURES
═══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ─── Create sample data with various problems ───
sample_data = {
    'الاسم | Name': ['أحمد', 'فاطمة', 'علي', 'عائشة', 'محمد'],
    'الهاتف | Phone': ['+2010123456', '010123456', '002010234567', '010345678', '+201234567890'],
    'العمر | Age': [25, 35, 200, 28, 32],  # Note: 200 is an outlier
    'السعر | Price': ['1500 ج.م', '$250.50', '3000 EGP', '1,234.56', '999 USD'],
    'المحافظة | City': ['القاهرة', 'القاهره', 'الاسكندرية', 'القاهارة', 'الاسكندريه'],
    'التاريخ | Date': ['2020-01-15', '01-02-2020', '2050-01-01', '15/03/2020', '2020-05-20'],
}

df = pd.DataFrame(sample_data)

print("=" * 80)
print("📊 SAMPLE DATA WITH PROBLEMS")
print("=" * 80)
print(df.to_string())
print("\n")

# ─── Import advanced functions (if available) ───
try:
    from advanced_cleaning import (
        standardize_phone_number,
        clean_mixed_numeric,
        fuzzy_match_series,
        smart_parse_date,
        clean_phone_column,
        clean_numeric_columns,
        apply_fuzzy_matching,
        clean_dates_advanced,
        optimize_memory,
        impute_text_with_context,
        streamlit_text_imputation_style,
        universal_missing_value_imputation,
        streamlit_imputation_style,
    )
    
    print("✅ Advanced cleaning module loaded successfully!\n")
    
    # Test 1: Phone Standardization
    print("1️⃣ PHONE STANDARDIZATION TEST")
    print("-" * 80)
    print("Original phones:")
    for phone in df['الهاتف | Phone']:
        print(f"  {phone}")
    print("\nStandardized phones:")
    for phone in df['الهاتف | Phone']:
        standardized = standardize_phone_number(phone)
        print(f"  {phone} → {standardized}")
    print()
    
    # Test 2: Numeric Cleaning
    print("2️⃣ NUMERIC CLEANING TEST")
    print("-" * 80)
    print("Original prices:")
    for price in df['السعر | Price']:
        print(f"  {price}")
    print("\nCleaned prices:")
    for price in df['السعر | Price']:
        cleaned = clean_mixed_numeric(price)
        print(f"  {price} → {cleaned}")
    print()
    
    print("2.1️⃣ CONTEXTUAL TEXT IMPUTATION TEST")
    print("-" * 80)
    partial = pd.DataFrame({
        'OrderID': [1, 1, 1, 2, 4, 6, 4, 3, 3, 5],
        'Customer': ['A', 'A', 'A', 'B', 'D', 'Z', 'D', 'C', 'C', 'E'],
        'Price': [10, 10, 10, 20, 40, 99, 40, 30, 35, 50],
        'Product': ['Widget', None, 'Widget', 'Gadget', None, 'Something', 'Widget', None, 'Widget', None],
    })

    imputed = impute_text_with_context(
        partial,
        target_text_col='Product',
        feature_cols=['OrderID', 'Customer', 'Price'],
    )

    print(imputed.to_string(index=False))
    assert imputed.loc[1, 'Product'] == 'Widget'
    assert imputed.loc[1, 'Product_prediction_type'] == 'Neighbor Match'
    assert imputed.loc[4, 'Product'] == 'Widget'
    assert imputed.loc[4, 'Product_prediction_type'] == 'Multi-Feature Matrix'
    assert imputed.loc[7, 'Product'] == 'Widget'
    assert imputed.loc[7, 'Product_prediction_type'] == 'Relaxed Feature Match'
    assert imputed.loc[9, 'Product'].endswith('_Estimated')
    assert imputed.loc[9, 'Product_prediction_type'] == 'Global Mode Fallback'
    print("✅ Text imputation passes basic phase checks.\n")

    print("2.2️⃣ UNIVERSAL MISSING VALUE IMPUTATION TEST")
    print("-" * 80)
    universal = pd.DataFrame({
        'Item Name': ['Coffee', 'Coffee', 'Tea', 'Tea', 'Bread', 'Bread', None],
        'Category': ['Beverage', 'Beverage', None, 'Beverage', 'Bakery', None, None],
        'Department': ['Drinks', 'Drinks', 'Drinks', 'Drinks', 'Food', 'Food', 'Food'],
        'Price': [5.0, np.nan, 3.0, np.nan, 2.5, np.nan, np.nan],
        'OrderID': ['A', 'A', 'B', 'B', 'C', 'C', 'C'],
    })

    universal_imputed = universal_missing_value_imputation(
        universal,
        numeric_cols_to_fill=['Price'],
        categorical_cols_to_fill=['Category'],
        fine_grain_guide='Item Name',
        coarse_grain_guide='Department',
    )

    print(universal_imputed.to_string(index=False))
    assert universal_imputed.loc[1, 'Price'] == 5.0
    assert universal_imputed.loc[1, 'Price_imputation_status'] == 'Filled by Item Context'
    assert universal_imputed.loc[3, 'Price'] == 3.0
    assert universal_imputed.loc[3, 'Price_imputation_status'] == 'Filled by Item Context'
    assert universal_imputed.loc[5, 'Category'] == 'Bakery'
    assert universal_imputed.loc[5, 'Category_imputation_status'] == 'Filled by Item Context'
    assert universal_imputed.loc[6, 'Category'] in {'Bakery', 'Beverage', 'Unknown'}
    assert universal_imputed.loc[6, 'Category_imputation_status'] in {
        'Filled by Category Fallback',
        'Filled by Sequential Neighbor',
        'Populated',
    }

    styled = streamlit_imputation_style(
        universal_imputed,
        status_cols=['Price_imputation_status', 'Category_imputation_status'],
    )
    assert hasattr(styled, 'to_html') or hasattr(styled, 'render')
    print("✅ Universal missing value imputation passes basic phase checks.\n")

    # Test 3: Fuzzy Matching
    print("3️⃣ FUZZY MATCHING TEST")
    print("-" * 80)
    print("Original cities:", df['المحافظة | City'].tolist())
    mapping = fuzzy_match_series(df['المحافظة | City'], threshold=90)
    print("Fuzzy mapping (90% threshold):")
    for orig, canonical in mapping.items():
        if orig != canonical:
            print(f"  {orig} → {canonical}")
    print()
    
    # Test 4: Date Parsing
    print("4️⃣ SMART DATE PARSING TEST")
    print("-" * 80)
    print("Original dates:")
    for date_str in df['التاريخ | Date']:
        print(f"  {date_str}")
    print("\nParsed dates:")
    for date_str in df['التاريخ | Date']:
        parsed = smart_parse_date(date_str)
        print(f"  {date_str} → {parsed}")
    print()
    
    # Test 5: Full pipeline
    print("5️⃣ FULL PIPELINE TEST")
    print("-" * 80)
    print("Running full cleaning pipeline...")
    
    from advanced_cleaning import AdvancedCleaner
    
    cleaner = AdvancedCleaner(df.copy())
    df_cleaned = cleaner.run_full_pipeline(
        clean_phones=True,
        clean_numeric=True,
        fuzzy_match=True,
        fix_dates=True,
        optimize_mem=True
    )
    
    print("\n✨ CLEANED DATA:")
    print(df_cleaned.to_string())
    print()
    
    print("📊 SUMMARY:")
    summary = cleaner.get_summary()
    print(f"  Total rows: {summary['total_rows']}")
    print(f"  Total columns: {summary['total_cols']}")
    print(f"  Memory optimization: {summary['memory_optimization']}")
    print()
    
    print("✅ All tests passed!")
    
except ImportError as e:
    print(f"⚠️ Error importing advanced_cleaning: {e}")
    print("Make sure advanced_cleaning.py is in the same directory as this file.")
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()

print("=" * 80)
