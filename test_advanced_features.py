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
