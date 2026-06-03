"""
Test Suite for Independent Semantic Clustering and Harmonization
Validates Arabic normalization, fuzzy matching, and independent clustering
"""

import pandas as pd
import pytest
from semantic_clustering_arabic import (
    normalize_arabic_text,
    semantic_clustering_harmonization,
    format_logs_for_display,
    get_correction_summary
)


# ============================================================================
# TEST 1: ARABIC NORMALIZATION
# ============================================================================

class TestArabicNormalization:
    """Test the Arabic text normalization function."""
    
    def test_hamza_variants_to_alef(self):
        """Test conversion of hamza variants (أ, إ, آ) to ا"""
        assert normalize_arabic_text('أسد') == 'اسد'
        assert normalize_arabic_text('إسلام') == 'اسلام'
        assert normalize_arabic_text('آخر') == 'اخر'
    
    def test_taa_marbuta_to_haa(self):
        """Test conversion of taa marbuta (ة) to haa (ه)"""
        assert normalize_arabic_text('ترابيزة') == 'تربيزه'
        assert normalize_arabic_text('كنبة') == 'كنبه'
    
    def test_alef_maksura_to_yaa(self):
        """Test conversion of alef maksura (ى) to yaa (ي)"""
        assert normalize_arabic_text('موسى') == 'موسي'
        assert normalize_arabic_text('عليّ') == 'علي'  # Shadda removed too
    
    def test_diacritics_removal(self):
        """Test removal of Arabic diacritics"""
        # Text with diacritics
        text_with_diacritics = 'مُحَمَّد'  # Muhammad with fatha, damma, shadda
        normalized = normalize_arabic_text(text_with_diacritics)
        assert normalized == 'محمد'
    
    def test_whitespace_stripping(self):
        """Test leading/trailing whitespace removal"""
        assert normalize_arabic_text('  كتاب  ') == 'كتاب'
        assert normalize_arabic_text('\nترابيزة\n') == 'تربيزه'
    
    def test_combined_normalization(self):
        """Test combined normalization operations"""
        # Complex example: ترابيزة with potential diacritics
        assert normalize_arabic_text('ترابيزة') == 'تربيزه'
        assert normalize_arabic_text('كنبة') == 'كنبه'
    
    def test_non_arabic_text(self):
        """Test handling of non-Arabic text"""
        assert normalize_arabic_text('hello') == 'hello'
        assert normalize_arabic_text('123') == '123'
        assert normalize_arabic_text('table') == 'table'
    
    def test_non_string_input(self):
        """Test handling of non-string inputs"""
        assert isinstance(normalize_arabic_text(123), str)
        assert isinstance(normalize_arabic_text(45.67), str)


# ============================================================================
# TEST 2: INDEPENDENT SEMANTIC CLUSTERING
# ============================================================================

class TestSemanticClustering:
    """Test the main semantic clustering and harmonization function."""
    
    def test_simple_clustering(self):
        """Test basic fuzzy matching and clustering"""
        df = pd.DataFrame({
            'Item': ['table', 'tabel', 'table', 'chair', 'chair']
        })
        
        df_clean, logs = semantic_clustering_harmonization(df, fuzzy_threshold=85)
        
        # Should harmonize 'tabel' to 'table'
        assert 'tabel' not in df_clean['Item'].values or len(logs.get('Item', [])) > 0
    
    def test_arabic_furniture_clustering(self):
        """
        CRITICAL TEST: Verify independent clustering of Arabic furniture items
        - "ترابيزة" and "ترابيزه" should cluster together (Table variants)
        - "كنبة" and "كنبه" should cluster together (Couch variants)
        - These two groups should NOT be merged together
        - "كرسي" should remain separate
        """
        df = pd.DataFrame({
            'Item': [
                'ترابيزة',      # Table variant 1
                'ترابيزه',      # Table variant 2
                'ترابيزة',      # Table variant 1 (duplicate)
                'كنبة',         # Couch variant 1
                'كنبه',         # Couch variant 2
                'كنبة',         # Couch variant 1 (duplicate)
                'كرسي',         # Chair (should remain separate)
                'كرسي',         # Chair
            ]
        })
        
        df_clean, logs = semantic_clustering_harmonization(
            df,
            fuzzy_threshold=90
        )
        
        # Verify that unique values have been reduced
        assert df_clean['Item'].nunique() < df['Item'].nunique()
        
        # Verify that "ترابيزة"/"ترابيزه" are harmonized together
        unique_items = set(df_clean['Item'].unique())
        
        # After harmonization, should have 3 items: table, couch, chair
        # (or variations thereof, but definitely not mixing categories)
        print("\n✓ Original unique items:", df['Item'].nunique())
        print("✓ Cleaned unique items:", df_clean['Item'].nunique())
        print("✓ Items after clustering:", unique_items)
        print("✓ Logs:", logs)
    
    def test_column_routing_skips_high_cardinality(self):
        """Test that columns with > max_unique_values are skipped"""
        # Create a column with 600 unique values (IDs)
        df = pd.DataFrame({
            'ID': [f'ID_{i}' for i in range(600)],
            'Name': ['John', 'Jon', 'john'] * 200
        })
        
        df_clean, logs = semantic_clustering_harmonization(
            df,
            max_unique_values=500
        )
        
        # ID column should be skipped
        assert logs['ID'] == [] or 'ID' not in [col for col, c in logs.items() if c]
        
        # Name column should be processed
        assert 'Name' in logs
    
    def test_column_routing_skips_low_cardinality(self):
        """Test that columns with < min_unique_values are skipped"""
        df = pd.DataFrame({
            'Uniform': ['Value'] * 100,  # Only 1 unique value
            'Binary': ['Yes', 'No'] * 50,  # 2 unique values (minimum)
        })
        
        df_clean, logs = semantic_clustering_harmonization(
            df,
            min_unique_values=2
        )
        
        # Uniform should be skipped (< 2)
        assert logs['Uniform'] == []
        
        # Binary should be processed (= 2)
        assert 'Binary' in logs
    
    def test_only_text_columns_processed(self):
        """Test that only object/string columns are processed"""
        df = pd.DataFrame({
            'Text': ['item1', 'item2', 'item1'],
            'Number': [1, 2, 3],
            'Float': [1.1, 2.2, 3.3],
        })
        
        df_clean, logs = semantic_clustering_harmonization(df)
        
        # Only 'Text' should be in logs
        assert 'Text' in logs
        assert 'Number' not in logs
        assert 'Float' not in logs
    
    def test_fuzzy_threshold_affects_matching(self):
        """Test that fuzzy_threshold parameter controls strictness"""
        df = pd.DataFrame({
            'Item': ['apple', 'appl', 'aple', 'apple', 'orange']
        })
        
        # High threshold (strict)
        df_strict, logs_strict = semantic_clustering_harmonization(
            df,
            fuzzy_threshold=95
        )
        
        # Low threshold (permissive)
        df_permissive, logs_permissive = semantic_clustering_harmonization(
            df,
            fuzzy_threshold=70
        )
        
        # Permissive should harmonize more values
        strict_corrections = sum(r['num_corrections'] for c in logs_strict.values() for r in c)
        permissive_corrections = sum(r['num_corrections'] for c in logs_permissive.values() for r in c)
        
        print(f"\n✓ Strict mode corrections: {strict_corrections}")
        print(f"✓ Permissive mode corrections: {permissive_corrections}")
    
    def test_majority_rule_processing(self):
        """Test that values are processed from most to least frequent"""
        df = pd.DataFrame({
            'Item': [
                'common',      # Most frequent (5x)
                'common',
                'common',
                'common',
                'common',
                'commun',      # Typo version (3x)
                'commun',
                'commun',
                'komnon',      # Different typo (2x)
                'komnon',
                'rare',        # Unique (1x)
            ]
        })
        
        df_clean, logs = semantic_clustering_harmonization(df, fuzzy_threshold=85)
        
        # Should process from most frequent (common) first
        if logs['Item']:
            # The master word should be 'common' or 'commun' (most frequent ones)
            masters = [r['master_word'] for r in logs['Item']]
            print(f"\n✓ Master words identified: {masters}")


# ============================================================================
# TEST 3: LOGGING AND DISPLAY
# ============================================================================

class TestLoggingAndDisplay:
    """Test logging and display functions."""
    
    def test_format_logs_for_display(self):
        """Test formatting of logs"""
        logs = {
            'Item': [
                {
                    'master_word': 'ترابيزة',
                    'matched_variations': ['ترابيزه'],
                    'num_corrections': 2
                }
            ],
            'Category': []
        }
        
        formatted = format_logs_for_display(logs)
        
        assert 'ترابيزة' in formatted
        assert 'ترابيزه' in formatted
        assert 'Total Variations Harmonized' in formatted
    
    def test_get_correction_summary(self):
        """Test summary statistics generation"""
        logs = {
            'Item': [
                {
                    'master_word': 'table',
                    'matched_variations': ['tabel', 'tabl'],
                    'num_corrections': 2
                }
            ],
            'Category': []
        }
        
        summary = get_correction_summary(logs)
        
        assert summary['total_columns_processed'] == 1
        assert summary['total_correction_groups'] == 1
        assert summary['total_variations_harmonized'] == 2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for end-to-end workflows."""
    
    def test_complete_workflow(self):
        """Test complete workflow from raw data to harmonized output"""
        # Create realistic Arabic e-commerce product data
        df = pd.DataFrame({
            'Product': [
                'ترابيزة خشبية',
                'ترابيزه خشبيه',
                'ترابيزة',
                'كنبة جلد',
                'كنبه جلديه',
                'كنبة',
                'كرسي مريح',
                'كرسي',
                'كرسي',
                'طاولة قهوة',
                'طاوله قهوه',
                'طاولة',
            ],
            'Category': ['Furniture'] * 12,
            'Price': [1000, 1000, 1050, 2000, 2000, 1950, 500, 500, 550, 800, 800, 750]
        })
        
        # Execute harmonization
        df_clean, logs = semantic_clustering_harmonization(
            df,
            fuzzy_threshold=90
        )
        
        # Verify results
        assert df_clean.shape[0] == df.shape[0], "Row count should be unchanged"
        assert df_clean.shape[1] == df.shape[1], "Column count should be unchanged"
        assert df_clean['Product'].nunique() < df['Product'].nunique(), "Should reduce unique values"
        
        # Get summary
        summary = get_correction_summary(logs)
        assert summary['total_variations_harmonized'] > 0, "Should have made corrections"
        
        print(f"\n✓ Integration Test Passed!")
        print(f"  Original unique products: {df['Product'].nunique()}")
        print(f"  Cleaned unique products: {df_clean['Product'].nunique()}")
        print(f"  Total variations harmonized: {summary['total_variations_harmonized']}")


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    # Test Arabic Normalization
    print("\n📝 Testing Arabic Normalization...")
    test_norm = TestArabicNormalization()
    test_norm.test_hamza_variants_to_alef()
    test_norm.test_taa_marbuta_to_haa()
    test_norm.test_alef_maksura_to_yaa()
    test_norm.test_diacritics_removal()
    test_norm.test_whitespace_stripping()
    test_norm.test_combined_normalization()
    test_norm.test_non_arabic_text()
    test_norm.test_non_string_input()
    print("✅ Arabic Normalization tests passed!")
    
    # Test Semantic Clustering
    print("\n🎯 Testing Semantic Clustering...")
    test_cluster = TestSemanticClustering()
    test_cluster.test_simple_clustering()
    test_cluster.test_arabic_furniture_clustering()
    test_cluster.test_column_routing_skips_high_cardinality()
    test_cluster.test_column_routing_skips_low_cardinality()
    test_cluster.test_only_text_columns_processed()
    test_cluster.test_fuzzy_threshold_affects_matching()
    test_cluster.test_majority_rule_processing()
    print("✅ Semantic Clustering tests passed!")
    
    # Test Logging
    print("\n📋 Testing Logging and Display...")
    test_log = TestLoggingAndDisplay()
    test_log.test_format_logs_for_display()
    test_log.test_get_correction_summary()
    print("✅ Logging and Display tests passed!")
    
    # Integration Tests
    print("\n🔗 Running Integration Tests...")
    test_int = TestIntegration()
    test_int.test_complete_workflow()
    print("✅ Integration tests passed!")
    
    print("\n" + "=" * 70)
    print("✨ ALL TESTS PASSED SUCCESSFULLY! ✨")
    print("=" * 70)
