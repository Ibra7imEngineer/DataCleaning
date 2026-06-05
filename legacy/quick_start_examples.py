"""
Quick Start Examples: Semantic Clustering & Harmonization
Practical examples for common data cleaning scenarios
"""

import pandas as pd
from semantic_clustering_arabic import (
    semantic_clustering_harmonization,
    format_logs_for_display,
    get_correction_summary
)


# ============================================================================
# EXAMPLE 1: Arabic E-Commerce Products
# ============================================================================

def example_arabic_ecommerce():
    """
    Scenario: E-commerce platform with Arabic product names
    Problem: Multiple spelling variants due to manual entry and typos
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Arabic E-Commerce Products")
    print("="*70)
    
    df = pd.DataFrame({
        'ProductID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'ProductName': [
            'ترابيزة خشبية',      # Table wooden (variant 1)
            'ترابيزه خشبيه',      # Table wooden (variant 2 - with typo)
            'ترابيزة',            # Table (variant 3)
            'كنبة جلد أسود',      # Couch leather black
            'كنبه جلديه اسود',    # Couch leather black (typo)
            'كنبة',               # Couch (short)
            'كرسي مكتب',          # Office chair
            'كرسي مكتب',          # Office chair (dup)
            'كرسي',               # Chair (short)
            'طاولة قهوة',         # Coffee table
            'طاوله قهوه',         # Coffee table (typo)
            'طاولة',              # Table short
        ],
        'Category': ['Furniture'] * 12,
        'Price': [500, 500, 550, 1200, 1200, 1100, 300, 300, 250, 400, 400, 350]
    })
    
    print("\n📊 BEFORE Harmonization:")
    print(df[['ProductName', 'Price']].head(8))
    print(f"\nUnique Product Names: {df['ProductName'].nunique()}")
    
    # Apply harmonization
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=90,
        max_unique_values=500,
        min_unique_values=2
    )
    
    print("\n✨ AFTER Harmonization:")
    print(df_clean[['ProductName', 'Price']].head(8))
    print(f"\nUnique Product Names: {df_clean['ProductName'].nunique()}")
    
    print("\n📋 CORRECTIONS APPLIED:")
    print(format_logs_for_display(logs))
    
    print("\n📈 SUMMARY STATISTICS:")
    summary = get_correction_summary(logs)
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    return df_clean, logs


# ============================================================================
# EXAMPLE 2: English Products with Typos
# ============================================================================

def example_english_products():
    """
    Scenario: Online store with English product names
    Problem: Typos from manual entry (misspellings, transpositions)
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: English Products with Typos")
    print("="*70)
    
    df = pd.DataFrame({
        'SKU': ['A001', 'A002', 'A003', 'B001', 'B002', 'B003', 'C001', 'C002'],
        'ProductName': [
            'Apple',      # Correct
            'Appl',       # Typo (missing 'e')
            'Aple',       # Typo (transposition)
            'Orange',     # Correct
            'Oragne',     # Typo (transposition)
            'Orang',      # Typo (missing 'e')
            'Banana',     # Correct
            'Bananna'     # Typo (extra 'n')
        ],
        'Stock': [100, 98, 102, 50, 48, 52, 75, 73]
    })
    
    print("\n📊 BEFORE Harmonization:")
    print(df)
    print(f"\nUnique Product Names: {df['ProductName'].nunique()}")
    
    # Apply harmonization with threshold appropriate for English
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=85,  # Slightly lower for English typos
        max_unique_values=500,
        min_unique_values=2
    )
    
    print("\n✨ AFTER Harmonization:")
    print(df_clean)
    print(f"\nUnique Product Names: {df_clean['ProductName'].nunique()}")
    
    print("\n📋 CORRECTIONS APPLIED:")
    print(format_logs_for_display(logs))
    
    return df_clean, logs


# ============================================================================
# EXAMPLE 3: Customer Addresses (Address Standardization)
# ============================================================================

def example_address_standardization():
    """
    Scenario: Customer database with various address formats
    Problem: Different ways to write the same location
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Address Standardization")
    print("="*70)
    
    df = pd.DataFrame({
        'CustomerID': [1, 2, 3, 4, 5, 6],
        'Address': [
            'Cairo',
            'Cario',      # Typo
            'cairo',      # Different case
            'New Cairo',
            'New Cario',  # Typo
            'New cairo'   # Different case
        ],
        'City': ['Cairo', 'Cairo', 'Cairo', 'Cairo', 'Cairo', 'Cairo']
    })
    
    print("\n📊 BEFORE Harmonization:")
    print(df)
    print(f"\nUnique Addresses: {df['Address'].nunique()}")
    
    # Apply harmonization
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=85,
        max_unique_values=500,
        min_unique_values=2
    )
    
    print("\n✨ AFTER Harmonization:")
    print(df_clean)
    print(f"\nUnique Addresses: {df_clean['Address'].nunique()}")
    
    print("\n📋 CORRECTIONS APPLIED:")
    print(format_logs_for_display(logs))
    
    return df_clean, logs


# ============================================================================
# EXAMPLE 4: Multi-Column Processing
# ============================================================================

def example_multi_column():
    """
    Scenario: Dataset with multiple text columns
    Problem: Each column has its own set of variations
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Multi-Column Processing (Independent Clustering)")
    print("="*70)
    
    df = pd.DataFrame({
        'Category': [
            'Furniture',
            'Furnituure',   # Typo
            'Furniture',
            'Electronics',
            'Electroncs',   # Typo
            'Electronics'
        ],
        'Subcategory': [
            'Table',
            'Tabel',        # Typo
            'Table',
            'Phone',
            'Phon',         # Typo
            'Phone'
        ],
        'Brand': [
            'Samsung',
            'Samsng',       # Typo
            'Samsung',
            'LG',
            'LG',
            'LG'
        ]
    })
    
    print("\n📊 BEFORE Harmonization:")
    print(df)
    print("\nUnique values per column:")
    for col in ['Category', 'Subcategory', 'Brand']:
        print(f"  {col}: {df[col].nunique()}")
    
    # Apply harmonization - processes each column independently!
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=88,
        max_unique_values=500,
        min_unique_values=2
    )
    
    print("\n✨ AFTER Harmonization:")
    print(df_clean)
    print("\nUnique values per column after cleaning:")
    for col in ['Category', 'Subcategory', 'Brand']:
        print(f"  {col}: {df_clean[col].nunique()}")
    
    print("\n📋 CORRECTIONS BY COLUMN:")
    print(format_logs_for_display(logs))
    
    return df_clean, logs


# ============================================================================
# EXAMPLE 5: Protecting High-Cardinality Columns (IDs, Emails)
# ============================================================================

def example_column_protection():
    """
    Scenario: Dataset with IDs, emails, and product names
    Problem: Don't want to fuzzy-match IDs or emails
    Solution: automatic skipping of high-cardinality columns
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Protecting High-Cardinality Columns")
    print("="*70)
    
    # Create dataset with 300 unique emails (will be skipped)
    df = pd.DataFrame({
        'EmailID': [f'user{i}@example.com' for i in range(300)],  # 300 unique
        'ProductName': ['iPhone', 'Iphone', 'IPHONE'] * 100,
        'Status': ['Active', 'Activ'] * 150
    })
    
    print("\n📊 BEFORE Harmonization:")
    print(f"Total rows: {len(df)}")
    print(f"EmailID unique values: {df['EmailID'].nunique()}")
    print(f"ProductName unique values: {df['ProductName'].nunique()}")
    print(f"Status unique values: {df['Status'].nunique()}")
    
    # Apply harmonization with max_unique_values=500
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=90,
        max_unique_values=200,  # EmailID has 300 > 200, so it will be SKIPPED
        min_unique_values=2
    )
    
    print("\n✨ AFTER Harmonization:")
    print(f"ProductName unique values: {df_clean['ProductName'].nunique()}")
    print(f"Status unique values: {df_clean['Status'].nunique()}")
    
    print("\n📊 Processing Report:")
    print(f"Columns in logs: {list(logs.keys())}")
    print(f"EmailID processed: {'EmailID' in logs and bool(logs['EmailID'])}")
    print(f"ProductName processed: {'ProductName' in logs and bool(logs['ProductName'])}")
    print(f"Status processed: {'Status' in logs and bool(logs['Status'])}")
    
    print("\n📋 ACTUAL CORRECTIONS:")
    print(format_logs_for_display(logs))
    
    return df_clean, logs


# ============================================================================
# EXAMPLE 6: Fine-Tuning Threshold
# ============================================================================

def example_threshold_tuning():
    """
    Scenario: Understanding how fuzzy_threshold affects results
    Problem: Need to find the right balance between fixing typos and avoiding false matches
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Threshold Fine-Tuning")
    print("="*70)
    
    df = pd.DataFrame({
        'Item': [
            'apple', 'aple', 'appl',           # Apple variants (high similarity)
            'orange', 'orng', 'orang',         # Orange variants
            'pineapple', 'pineaple',           # Pineapple (could mix with apple?)
        ]
    })
    
    print("\n📊 Original data:")
    print(f"Unique values: {df['Item'].nunique()}")
    print(df['Item'].unique())
    
    thresholds = [70, 80, 85, 90, 95]
    
    for threshold in thresholds:
        df_clean, logs = semantic_clustering_harmonization(
            df.copy(),
            fuzzy_threshold=threshold
        )
        
        corrections = sum(r['num_corrections'] for c in logs.values() for r in c)
        unique_after = df_clean['Item'].nunique()
        
        print(f"\n🎯 Threshold {threshold}:")
        print(f"   Unique values after: {unique_after}")
        print(f"   Corrections made: {corrections}")
        if logs.get('Item'):
            for correction in logs['Item']:
                print(f"   - {correction['master_word']} ← {correction['matched_variations']}")


# ============================================================================
# EXAMPLE 7: Working with Large Datasets
# ============================================================================

def example_large_dataset():
    """
    Scenario: Processing a larger dataset from file
    Problem: Need efficient processing with reporting
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Processing Large Dataset")
    print("="*70)
    
    # Create a realistic large dataset
    import random
    
    product_variants = {
        'iPhone': ['iPhone', 'Iphone', 'IPHONE', 'iphone', 'iPone'],
        'Samsung': ['Samsung', 'Samsng', 'SAMSUNG', 'samsung'],
        'iPad': ['iPad', 'Ipad', 'IPAD', 'ipad'],
    }
    
    data = []
    for _ in range(1000):
        product_type = random.choice(list(product_variants.keys()))
        variant = random.choice(product_variants[product_type])
        data.append({
            'OrderID': random.randint(1000, 99999),
            'Product': variant,
            'Quantity': random.randint(1, 10),
            'Price': random.uniform(100, 2000)
        })
    
    df = pd.DataFrame(data)
    
    print("\n📊 Dataset Statistics:")
    print(f"Total rows: {len(df)}")
    print(f"Unique products: {df['Product'].nunique()}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
    
    # Process the dataset
    import time
    start_time = time.time()
    
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=90,
        max_unique_values=500,
        min_unique_values=2
    )
    
    elapsed = time.time() - start_time
    
    print("\n✨ Harmonization Results:")
    print(f"Processing time: {elapsed:.3f} seconds")
    print(f"Unique products before: {df['Product'].nunique()}")
    print(f"Unique products after: {df_clean['Product'].nunique()}")
    
    summary = get_correction_summary(logs)
    print(f"\nCorrections made:")
    print(f"  Total variations harmonized: {summary['total_variations_harmonized']}")
    print(f"  Correction groups: {summary['total_correction_groups']}")
    
    print("\n📊 Product Distribution After Cleaning:")
    print(df_clean['Product'].value_counts())
    
    return df_clean, logs


# ============================================================================
# MAIN RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  SEMANTIC CLUSTERING & HARMONIZATION - PRACTICAL EXAMPLES".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    # Run all examples
    try:
        example_arabic_ecommerce()
        example_english_products()
        example_address_standardization()
        example_multi_column()
        example_column_protection()
        example_threshold_tuning()
        example_large_dataset()
        
        print("\n" + "█"*70)
        print("█" + " "*68 + "█")
        print("█" + "  ✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!".center(68) + "█")
        print("█" + " "*68 + "█")
        print("█"*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()
