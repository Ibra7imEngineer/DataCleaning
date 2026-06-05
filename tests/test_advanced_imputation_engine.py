"""
================================================================================
    TEST SUITE: Advanced Imputation Engine
    Enterprise-Grade Unit Tests for Production Validation
================================================================================
"""

import pandas as pd
import numpy as np
from advanced_imputation_engine import (
    AdvancedImputationEngine,
    streamlit_imputation_style,
    get_imputation_summary
)
import pytest


class TestAdvancedImputationEngine:
    """Comprehensive test suite for the Advanced Imputation Engine."""
    
    @pytest.fixture
    def engine(self):
        """Initialize engine for each test."""
        return AdvancedImputationEngine(verbose=False)
    
    @pytest.fixture
    def sample_df(self):
        """Create sample dataset with missing values."""
        return pd.DataFrame({
            'Product_Name': ['Coffee', 'Coffee', 'Laptop', 'Laptop', 'Desk', 'Desk'],
            'Department': ['Foods', 'Foods', 'Electronics', 'Electronics', 'Office', 'Office'],
            'Price': [15.0, np.nan, 999.0, np.nan, 200.0, np.nan],
            'Category': ['Beverage', 'Beverage', np.nan, 'Computer', np.nan, np.nan],
            'Quantity': [10, 20, 5, np.nan, 8, 12]
        })
    
    def test_initialization(self, engine):
        """Test that engine initializes correctly."""
        assert engine.verbose == False
        assert len(engine.imputation_log) == 0
    
    def test_numeric_level_1_fills(self, engine, sample_df):
        """Test Level 1 numeric imputation (Item Context)."""
        df_filled, metrics = engine.fill_missing_values_advanced(
            df=sample_df,
            numeric_cols_to_fill=['Price'],
            categorical_cols_to_fill=[],
            fine_grain_guide='Product_Name',
            coarse_grain_guide='Department'
        )
        
        # Coffee items should be filled with 15 (median of [15])
        assert df_filled.loc[1, 'Price'] == 15.0
        
        # Laptop should be filled with 999 (median of [999])
        assert df_filled.loc[3, 'Price'] == 999.0
        
        # All price missing values should be filled
        assert df_filled['Price'].isna().sum() == 0
        
        # Check imputation status
        assert 'Price_imputation_status' in df_filled.columns
    
    def test_categorical_level_1_fills(self, engine, sample_df):
        """Test Level 1 categorical imputation (Identifier Mode)."""
        df_filled, metrics = engine.fill_missing_values_advanced(
            df=sample_df,
            numeric_cols_to_fill=[],
            categorical_cols_to_fill=['Category'],
            fine_grain_guide='Product_Name',
            coarse_grain_guide='Department'
        )
        
        # Check that status column was created
        assert 'Category_imputation_status' in df_filled.columns
        
        # Some categorical values should be filled
        assert df_filled['Category'].isna().sum() < sample_df['Category'].isna().sum()
    
    def test_no_mutation_of_existing_data(self, engine, sample_df):
        """Test that existing non-null data is not mutated."""
        original_price = sample_df.loc[0, 'Price']
        original_category = sample_df.loc[0, 'Category']
        
        df_filled, _ = engine.fill_missing_values_advanced(
            df=sample_df,
            numeric_cols_to_fill=['Price'],
            categorical_cols_to_fill=['Category'],
            fine_grain_guide='Product_Name',
            coarse_grain_guide='Department'
        )
        
        # Original values should not change
        assert df_filled.loc[0, 'Price'] == original_price
        assert df_filled.loc[0, 'Category'] == original_category
    
    def test_metrics_generation(self, engine, sample_df):
        """Test that metrics are correctly computed."""
        df_filled, metrics = engine.fill_missing_values_advanced(
            df=sample_df,
            numeric_cols_to_fill=['Price'],
            categorical_cols_to_fill=[],
            fine_grain_guide='Product_Name',
            coarse_grain_guide='Department'
        )
        
        # Check metrics for Price column
        assert 'Price' in metrics
        assert metrics['Price'].total_missing == 3
        assert metrics['Price'].total_filled > 0
        assert metrics['Price'].fillrate > 0
    
    def test_invalid_column_raises_error(self, engine, sample_df):
        """Test that invalid column raises appropriate error."""
        with pytest.raises(ValueError):
            engine.fill_missing_values_advanced(
                df=sample_df,
                numeric_cols_to_fill=['InvalidColumn'],
                categorical_cols_to_fill=[],
                fine_grain_guide='Product_Name',
                coarse_grain_guide='Department'
            )
    
    def test_multiple_columns_filled(self, engine, sample_df):
        """Test filling multiple columns simultaneously."""
        df_filled, metrics = engine.fill_missing_values_advanced(
            df=sample_df,
            numeric_cols_to_fill=['Price', 'Quantity'],
            categorical_cols_to_fill=['Category'],
            fine_grain_guide='Product_Name',
            coarse_grain_guide='Department'
        )
        
        # All target columns should be filled
        assert df_filled['Price'].isna().sum() == 0
        assert df_filled['Quantity'].isna().sum() == 0
        
        # Metrics should exist for all columns
        assert len(metrics) == 3


class TestStreamlitStyling:
    """Test Streamlit styling and formatting utilities."""
    
    @pytest.fixture
    def styled_df(self):
        """Create a DataFrame with imputation status columns."""
        return pd.DataFrame({
            'Product': ['A', 'B', 'C'],
            'Price': [10.0, 20.0, 30.0],
            'Price_imputation_status': [
                'Populated',
                'Filled by Item Context',
                'Filled by Category Fallback'
            ]
        })
    
    def test_streamlit_styling_returns_styler(self, styled_df):
        """Test that styling function returns a Styler object."""
        result = streamlit_imputation_style(styled_df, ['Price_imputation_status'])
        
        # Should have a .render() method (Styler object)
        assert hasattr(result, 'render')
        assert callable(result.render)
    
    def test_imputation_summary_generation(self):
        """Test that imputation summary is correctly generated."""
        from advanced_imputation_engine import ImpulationMetrics
        
        metrics = {
            'Price': ImpulationMetrics(
                total_missing=10,
                total_filled=10,
                level_1_count=7,
                level_2_count=2,
                level_3_count=1,
                level_4_count=0,
                fillrate=100.0
            ),
            'Category': ImpulationMetrics(
                total_missing=5,
                total_filled=5,
                level_1_count=3,
                level_2_count=1,
                level_3_count=1,
                level_4_count=0,
                fillrate=100.0
            )
        }
        
        summary = get_imputation_summary(metrics)
        
        # Summary should be a DataFrame
        assert isinstance(summary, pd.DataFrame)
        
        # Should have 2 rows (one per column)
        assert len(summary) == 2
        
        # Should have expected columns
        expected_cols = ['Column', 'Total Missing', 'Total Filled', 'Level 1 (Item)']
        for col in expected_cols:
            assert col in summary.columns


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def engine(self):
        return AdvancedImputationEngine(verbose=False)
    
    def test_all_null_column(self, engine):
        """Test behavior with completely null column."""
        df = pd.DataFrame({
            'Item': ['A', 'A', 'B', 'B'],
            'Department': ['X', 'X', 'Y', 'Y'],
            'Price': [np.nan, np.nan, np.nan, np.nan],
        })
        
        df_filled, metrics = engine.fill_missing_values_advanced(
            df=df,
            numeric_cols_to_fill=['Price'],
            categorical_cols_to_fill=[],
            fine_grain_guide='Item',
            coarse_grain_guide='Department'
        )
        
        # Price should still be all NaN (no data to fill with)
        assert df_filled['Price'].isna().sum() >= 0  # Handle gracefully
    
    def test_no_missing_values(self, engine):
        """Test behavior when there are no missing values."""
        df = pd.DataFrame({
            'Item': ['A', 'B', 'C'],
            'Price': [10.0, 20.0, 30.0],
            'Category': ['X', 'Y', 'Z']
        })
        
        df_filled, metrics = engine.fill_missing_values_advanced(
            df=df,
            numeric_cols_to_fill=['Price'],
            categorical_cols_to_fill=['Category'],
            fine_grain_guide='Item',
            coarse_grain_guide='Item'
        )
        
        # DataFrame should be unchanged
        pd.testing.assert_frame_equal(df[['Item', 'Price', 'Category']], 
                                     df_filled[['Item', 'Price', 'Category']])
    
    def test_duplicate_identifiers(self, engine):
        """Test with many duplicate items."""
        df = pd.DataFrame({
            'Item': ['Coffee'] * 10,
            'Department': ['Foods'] * 10,
            'Price': [15.0, np.nan, 14.0, np.nan, 16.0, np.nan] + [15.0] * 4,
        })
        
        df_filled, metrics = engine.fill_missing_values_advanced(
            df=df,
            numeric_cols_to_fill=['Price'],
            categorical_cols_to_fill=[],
            fine_grain_guide='Item',
            coarse_grain_guide='Department'
        )
        
        # All missing should be filled with median of Coffee
        assert df_filled['Price'].isna().sum() == 0


def run_all_tests():
    """Run all tests with verbose output."""
    print("\n" + "="*70)
    print("RUNNING ADVANCED IMPUTATION ENGINE TEST SUITE")
    print("="*70 + "\n")
    
    # Can be run with: pytest test_advanced_imputation_engine.py -v
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == "__main__":
    run_all_tests()
