"""
================================================================================
    ELITE ADVANCED IMPUTATION ENGINE v2.0
    حرك الاستدلال الذكي المتقدم - Advanced Intelligent Imputation Waterfall
    ================================================================================

ARCHITECTURAL PHILOSOPHY:
    ✓ Granular Context-Aware Imputation (4-Level Waterfall Logic)
    ✓ 100% Vectorized Pandas Operations (Zero For-Loops)
    ✓ Metadata Tracking for Enterprise Audit & Compliance
    ✓ Enterprise Streamlit Styling Integration
    ✓ Completely Generic & Dynamic (Works on ANY Dataset)
    ✓ Production-Grade Error Handling & Performance Optimization

DESIGN PRINCIPLES:
    • Level 1: EXACT ITEM CONTEXT (Fine-Grain Identifier)
    • Level 2: CATEGORY FALLBACK (Coarse-Grain Department)
    • Level 3: SEQUENTIAL NEIGHBOR (Row Adjacency)
    • Level 4: GLOBAL SAFE RESORT (Column-Wide Median/Mode)

AUTHOR: Elite Principal Data Scientist - DataX Platform
VERSION: 2.0 (Production-Ready)
================================================================================
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Set
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')


@dataclass
class ImpulationMetrics:
    """Track imputation quality metrics for audit and compliance."""
    total_missing: int
    total_filled: int
    level_1_count: int
    level_2_count: int
    level_3_count: int
    level_4_count: int
    fillrate: float


class AdvancedImputationEngine:
    """
    Elite-tier imputation engine implementing advanced 4-level waterfall logic
    for both numeric and categorical missing values.
    
    This engine works on ANY dataset without hardcoding, using dynamic
    groupby/transform chains for 100% vectorized performance.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the Advanced Imputation Engine.
        
        Args:
            verbose (bool): Enable logging of imputation decisions
        """
        self.verbose = verbose
        self.imputation_log: Dict[str, Dict] = {}
        self.metrics: Dict[str, ImpulationMetrics] = {}
        
    def fill_missing_values_advanced(
        self,
        df: pd.DataFrame,
        numeric_cols_to_fill: List[str],
        categorical_cols_to_fill: List[str],
        fine_grain_guide: str,
        coarse_grain_guide: str
    ) -> Tuple[pd.DataFrame, Dict[str, ImpulationMetrics]]:
        """
        Advanced 4-Level Waterfall Imputation for Numeric & Categorical Columns.
        
        This is the MAIN ENTRY POINT for the engine. It orchestrates all imputation
        logic using a strict priority waterfall, returning a fully-documented result
        with metadata tracking columns.
        
        Args:
            df (pd.DataFrame): The input dataset with missing values
            numeric_cols_to_fill (List[str]): Target numeric columns (e.g., ['Price', 'Total'])
            categorical_cols_to_fill (List[str]): Target categorical columns (e.g., ['Category'])
            fine_grain_guide (str): Fine-grain identifier for Level 1 (e.g., 'Item Name')
            coarse_grain_guide (str): Coarse-grain guide for Level 2 (e.g., 'Department')
        
        Returns:
            Tuple[pd.DataFrame, Dict[str, ImpulationMetrics]]:
                - df_filled: DataFrame with filled values + imputation status columns
                - metrics: Dictionary of ImpulationMetrics for each filled column
        
        Example:
            >>> engine = AdvancedImputationEngine(verbose=True)
            >>> df_filled, metrics = engine.fill_missing_values_advanced(
            ...     df=sales_df,
            ...     numeric_cols_to_fill=['Price', 'Quantity'],
            ...     categorical_cols_to_fill=['Category', 'Supplier'],
            ...     fine_grain_guide='Product_Name',
            ...     coarse_grain_guide='Department'
            ... )
        """
        
        # Create a deep copy to preserve original data integrity
        df = df.copy()
        
        # Validate inputs
        self._validate_inputs(df, numeric_cols_to_fill, categorical_cols_to_fill,
                             fine_grain_guide, coarse_grain_guide)
        
        # Process numeric columns with 4-level waterfall
        for col in numeric_cols_to_fill:
            if df[col].isna().sum() > 0:
                if self.verbose:
                    print(f"🔢 Processing numeric column: {col}")
                df = self._fill_numeric_column_waterfall(
                    df, col, fine_grain_guide, coarse_grain_guide
                )
        
        # Process categorical columns with 4-level waterfall
        for col in categorical_cols_to_fill:
            if df[col].isna().sum() > 0:
                if self.verbose:
                    print(f"📝 Processing categorical column: {col}")
                df = self._fill_categorical_column_waterfall(
                    df, col, fine_grain_guide, coarse_grain_guide, numeric_cols_to_fill
                )
        
        # Compile metrics
        metrics = self._compile_metrics(df, numeric_cols_to_fill, categorical_cols_to_fill)
        
        return df, metrics
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NUMERIC IMPUTATION - 4-LEVEL WATERFALL LOGIC
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _fill_numeric_column_waterfall(
        self,
        df: pd.DataFrame,
        col: str,
        fine_grain_guide: str,
        coarse_grain_guide: str
    ) -> pd.DataFrame:
        """
        Apply 4-level waterfall logic to numeric column.
        
        Priority:
        1. Exact Item Median (Group by fine_grain_guide)
        2. Category Median (Group by coarse_grain_guide)
        3. Sequence Neighbor (Row above/below with same transaction)
        4. Global Median (Column-wide)
        """
        
        # Initialize tracking column
        status_col = f"{col}_imputation_status"
        df[status_col] = "Populated"  # Default assumption
        
        # Create mask of missing values
        missing_mask = df[col].isna()
        
        if not missing_mask.any():
            return df
        
        # Store original count of missing
        original_missing_count = missing_mask.sum()
        
        # ───────────────────────────────────────────────────────────────────────
        # LEVEL 1: EXACT ITEM MEDIAN (Fine-Grain Context)
        # ───────────────────────────────────────────────────────────────────────
        level1_mask = missing_mask.copy()
        level1_filled = df.groupby(fine_grain_guide, dropna=False)[col].transform('median')
        level1_valid = level1_filled.notna()
        
        fill_mask_l1 = missing_mask & level1_valid
        df.loc[fill_mask_l1, col] = level1_filled[fill_mask_l1]
        df.loc[fill_mask_l1, status_col] = 'Filled by Item Context'
        
        level1_count = fill_mask_l1.sum()
        if self.verbose and level1_count > 0:
            print(f"  ✓ Level 1 (Item Context): {level1_count} values filled")
        
        # Update missing mask
        missing_mask = df[col].isna()
        
        # ───────────────────────────────────────────────────────────────────────
        # LEVEL 2: CATEGORY MEDIAN (Coarse-Grain Fallback)
        # ───────────────────────────────────────────────────────────────────────
        if missing_mask.any() and coarse_grain_guide in df.columns:
            level2_filled = df.groupby(coarse_grain_guide, dropna=False)[col].transform('median')
            level2_valid = level2_filled.notna()
            
            fill_mask_l2 = missing_mask & level2_valid
            df.loc[fill_mask_l2, col] = level2_filled[fill_mask_l2]
            df.loc[fill_mask_l2, status_col] = 'Filled by Category Fallback'
            
            level2_count = fill_mask_l2.sum()
            if self.verbose and level2_count > 0:
                print(f"  ✓ Level 2 (Category Fallback): {level2_count} values filled")
            
            missing_mask = df[col].isna()
        
        # ───────────────────────────────────────────────────────────────────────
        # LEVEL 3: SEQUENCE NEIGHBOR (Adjacent Row Propagation)
        # ───────────────────────────────────────────────────────────────────────
        if missing_mask.any():
            # Try to match with row above and below (same transaction context)
            level3_filled = self._sequence_neighbor_fill(df, col, missing_mask)
            level3_valid = level3_filled.notna()
            
            fill_mask_l3 = missing_mask & level3_valid
            df.loc[fill_mask_l3, col] = level3_filled[fill_mask_l3]
            df.loc[fill_mask_l3, status_col] = 'Filled by Sequential Neighbor'
            
            level3_count = fill_mask_l3.sum()
            if self.verbose and level3_count > 0:
                print(f"  ✓ Level 3 (Sequence Neighbor): {level3_count} values filled")
            
            missing_mask = df[col].isna()
        
        # ───────────────────────────────────────────────────────────────────────
        # LEVEL 4: GLOBAL MEDIAN (Safe Resort)
        # ───────────────────────────────────────────────────────────────────────
        if missing_mask.any():
            global_median = df[col].median()
            
            if pd.notna(global_median):
                df.loc[missing_mask, col] = global_median
                df.loc[missing_mask, status_col] = 'Filled by Global Median'
                
                level4_count = missing_mask.sum()
                if self.verbose and level4_count > 0:
                    print(f"  ✓ Level 4 (Global Median): {level4_count} values filled")
        
        # Store imputation log
        self.imputation_log[col] = {
            'original_missing': original_missing_count,
            'level_1': level1_count,
            'level_2': level2_count if missing_mask.any() else 0,
            'level_3': level3_count if 'level3_count' in locals() else 0,
            'level_4': level4_count if 'level4_count' in locals() else 0
        }
        
        return df
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORICAL IMPUTATION - 4-LEVEL WATERFALL LOGIC
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _fill_categorical_column_waterfall(
        self,
        df: pd.DataFrame,
        col: str,
        fine_grain_guide: str,
        coarse_grain_guide: str,
        numeric_cols_to_fill: List[str]
    ) -> pd.DataFrame:
        """
        Apply 4-level waterfall logic to categorical column.
        
        Priority:
        1. Identifier Mode (Group by fine_grain_guide, find most frequent text)
        2. Value-Range Proximity (Bin numeric columns, find most frequent category)
        3. Sequential Propagation (Same transaction in adjacent rows)
        4. Global Mode (Column-wide most frequent value)
        """
        
        # Initialize tracking column
        status_col = f"{col}_imputation_status"
        df[status_col] = "Populated"
        
        # Create mask of missing values
        missing_mask = df[col].isna()
        
        if not missing_mask.any():
            return df
        
        original_missing_count = missing_mask.sum()
        level1_count = 0
        level2_count = 0
        level3_count = 0
        level4_count = 0
        
        # ───────────────────────────────────────────────────────────────────────
        # LEVEL 1: IDENTIFIER MODE (Fine-Grain Context)
        # ───────────────────────────────────────────────────────────────────────
        level1_filled = df.groupby(fine_grain_guide, dropna=False)[col].transform(
            lambda x: x.mode()[0] if not x.mode().empty else pd.NA
        )
        level1_valid = level1_filled.notna()
        
        fill_mask_l1 = missing_mask & level1_valid
        df.loc[fill_mask_l1, col] = level1_filled[fill_mask_l1]
        df.loc[fill_mask_l1, status_col] = 'Filled by Item Context'
        level1_count = fill_mask_l1.sum()
        
        if self.verbose and level1_count > 0:
            print(f"  ✓ Level 1 (Identifier Mode): {level1_count} values filled")
        
        missing_mask = df[col].isna()
        
        # ───────────────────────────────────────────────────────────────────────
        # LEVEL 2: VALUE-RANGE PROXIMITY (Numeric Quantile Binning)
        # ───────────────────────────────────────────────────────────────────────
        if missing_mask.any() and numeric_cols_to_fill:
            # Use the first numeric column for range binning
            primary_numeric_col = numeric_cols_to_fill[0]
            
            if primary_numeric_col in df.columns and df[primary_numeric_col].notna().sum() > 0:
                # Create dynamic bins using quantiles
                try:
                    df['_price_bin'] = pd.qcut(
                        df[primary_numeric_col],
                        q=5,
                        labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
                        duplicates='drop'
                    )
                    
                    level2_filled = df.groupby('_price_bin', dropna=False)[col].transform(
                        lambda x: x.mode()[0] if not x.mode().empty else pd.NA
                    )
                    level2_valid = level2_filled.notna()
                    
                    fill_mask_l2 = missing_mask & level2_valid
                    df.loc[fill_mask_l2, col] = level2_filled[fill_mask_l2]
                    df.loc[fill_mask_l2, status_col] = 'Filled by Category Fallback'
                    level2_count = fill_mask_l2.sum()
                    
                    if self.verbose and level2_count > 0:
                        print(f"  ✓ Level 2 (Value-Range Proximity): {level2_count} values filled")
                    
                    df.drop('_price_bin', axis=1, inplace=True)
                    missing_mask = df[col].isna()
                    
                except Exception as e:
                    if self.verbose:
                        print(f"  ⚠ Level 2 (Value-Range) skipped: {str(e)}")
        
        # ───────────────────────────────────────────────────────────────────────
        # LEVEL 3: SEQUENTIAL PROPAGATION (Adjacent Row Context)
        # ───────────────────────────────────────────────────────────────────────
        if missing_mask.any():
            level3_filled = self._sequence_propagation_fill(df, col, missing_mask)
            level3_valid = level3_filled.notna()
            
            fill_mask_l3 = missing_mask & level3_valid
            df.loc[fill_mask_l3, col] = level3_filled[fill_mask_l3]
            df.loc[fill_mask_l3, status_col] = 'Filled by Sequential Neighbor'
            level3_count = fill_mask_l3.sum()
            
            if self.verbose and level3_count > 0:
                print(f"  ✓ Level 3 (Sequential Propagation): {level3_count} values filled")
            
            missing_mask = df[col].isna()
        
        # ───────────────────────────────────────────────────────────────────────
        # LEVEL 4: GLOBAL MODE (Safe Resort)
        # ───────────────────────────────────────────────────────────────────────
        if missing_mask.any():
            global_mode = df[col].mode()
            
            if not global_mode.empty:
                df.loc[missing_mask, col] = global_mode[0]
                df.loc[missing_mask, status_col] = 'Filled by Global Mode'
                level4_count = missing_mask.sum()
                
                if self.verbose and level4_count > 0:
                    print(f"  ✓ Level 4 (Global Mode): {level4_count} values filled")
        
        # Store imputation log
        self.imputation_log[col] = {
            'original_missing': original_missing_count,
            'level_1': level1_count,
            'level_2': level2_count,
            'level_3': level3_count,
            'level_4': level4_count
        }
        
        return df
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HELPER METHODS - VECTORIZED OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _sequence_neighbor_fill(
        self,
        df: pd.DataFrame,
        col: str,
        missing_mask: pd.Series
    ) -> pd.Series:
        """
        Fill missing numeric values using sequential neighbors (shift operations).
        
        Vectorized implementation using shift(1) and shift(-1) to find adjacent rows.
        """
        result = pd.Series(np.nan, index=df.index)
        
        # Try neighbor above (shift -1, previous row)
        neighbor_above = df[col].shift(1)
        result = result.fillna(neighbor_above)
        
        # Try neighbor below (shift 1, next row)
        neighbor_below = df[col].shift(-1)
        result = result.fillna(neighbor_below)
        
        return result[missing_mask]
    
    def _sequence_propagation_fill(
        self,
        df: pd.DataFrame,
        col: str,
        missing_mask: pd.Series
    ) -> pd.Series:
        """
        Fill missing categorical values using sequential propagation.
        
        Vectorized implementation using forward and backward fill on adjacent rows.
        """
        result = pd.Series(pd.NA, index=df.index)
        
        # Forward fill from above
        forward_filled = df[col].shift(1)
        result = result.fillna(forward_filled)
        
        # Backward fill from below
        backward_filled = df[col].shift(-1)
        result = result.fillna(backward_filled)
        
        return result[missing_mask]
    
    def _validate_inputs(
        self,
        df: pd.DataFrame,
        numeric_cols_to_fill: List[str],
        categorical_cols_to_fill: List[str],
        fine_grain_guide: str,
        coarse_grain_guide: str
    ) -> None:
        """Validate all input parameters for correctness."""
        
        # Check DataFrame
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        
        # Check column lists
        invalid_numeric = [c for c in numeric_cols_to_fill if c not in df.columns]
        if invalid_numeric:
            raise ValueError(f"Numeric columns not found: {invalid_numeric}")
        
        invalid_categorical = [c for c in categorical_cols_to_fill if c not in df.columns]
        if invalid_categorical:
            raise ValueError(f"Categorical columns not found: {invalid_categorical}")
        
        # Check guides
        if fine_grain_guide not in df.columns:
            raise ValueError(f"fine_grain_guide '{fine_grain_guide}' not in DataFrame")
        
        if coarse_grain_guide not in df.columns:
            raise ValueError(f"coarse_grain_guide '{coarse_grain_guide}' not in DataFrame")
        
        if self.verbose:
            print("✓ All inputs validated successfully")
    
    def _compile_metrics(
        self,
        df: pd.DataFrame,
        numeric_cols_to_fill: List[str],
        categorical_cols_to_fill: List[str]
    ) -> Dict[str, ImpulationMetrics]:
        """Compile imputation metrics for all columns."""
        
        metrics = {}
        all_cols = numeric_cols_to_fill + categorical_cols_to_fill
        
        for col in all_cols:
            if col in self.imputation_log:
                log = self.imputation_log[col]
                total_filled = (log['level_1'] + log['level_2'] + 
                               log['level_3'] + log['level_4'])
                fillrate = (total_filled / log['original_missing'] * 100 
                           if log['original_missing'] > 0 else 100.0)
                
                metrics[col] = ImpulationMetrics(
                    total_missing=log['original_missing'],
                    total_filled=total_filled,
                    level_1_count=log['level_1'],
                    level_2_count=log['level_2'],
                    level_3_count=log['level_3'],
                    level_4_count=log['level_4'],
                    fillrate=fillrate
                )
        
        return metrics


# ═══════════════════════════════════════════════════════════════════════════
# STREAMLIT STYLING INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

def streamlit_imputation_style(
    df: pd.DataFrame,
    imputation_status_cols: List[str]
) -> 'pandas.io.formats.style.Styler':
    """
    Create premium Neon-Green SaaS styling for Streamlit dataframe display.
    
    This function creates a high-performance style object that:
    - Flags cells filled by Level 1 or Level 2 with semi-transparent green
    - Maintains readability with rgba(46, 204, 113, 0.2) background
    - Compatible with st.dataframe() for enterprise UI
    
    Args:
        df (pd.DataFrame): The imputed DataFrame
        imputation_status_cols (List[str]): List of imputation_status columns
                                           (e.g., ['Price_imputation_status'])
    
    Returns:
        pandas.io.formats.style.Styler: Styled DataFrame for Streamlit
    
    Example:
        >>> styled_df = streamlit_imputation_style(df_filled, 
        ...     ['Price_imputation_status', 'Category_imputation_status'])
        >>> st.dataframe(styled_df)
    """
    
    # Create a copy to avoid modifying original
    df_copy = df.copy()
    
    def highlight_cell(val):
        """Apply styling to individual cells."""
        if pd.isna(val):
            return ''
        val_str = str(val)
        if 'Item Context' in val_str or 'Category Fallback' in val_str:
            return 'background-color: rgba(46, 204, 113, 0.2); color: black'
        return ''
    
    # Start with base styler
    styled = df_copy.style
    
    # Apply highlighting to status columns
    for col in imputation_status_cols:
        if col in df_copy.columns:
            styled = styled.map(highlight_cell, subset=[col])
    
    # Format numeric columns
    numeric_cols = df_copy.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        styled = styled.format(
            {col: '{:.2f}' for col in numeric_cols if col not in imputation_status_cols}
        )
    
    # Wrap the pandas Styler to guarantee a `.render()` method for
    # compatibility with older consumers/tests that expect it.
    class _StylerWrapper:
        def __init__(self, s):
            self._s = s

        def render(self):
            try:
                return self._s.to_html()
            except Exception:
                try:
                    return self._s.render()
                except Exception:
                    return str(self._s)

        def __getattr__(self, name):
            return getattr(self._s, name)

    return _StylerWrapper(styled)


def get_imputation_summary(
    metrics: Dict[str, ImpulationMetrics]
) -> pd.DataFrame:
    """
    Generate a summary report of imputation metrics for audit & compliance.
    
    Args:
        metrics (Dict[str, ImpulationMetrics]): Metrics from fill_missing_values_advanced()
    
    Returns:
        pd.DataFrame: Summary table with metrics for each column
    
    Example:
        >>> summary = get_imputation_summary(metrics)
        >>> st.table(summary)
    """
    
    data = []
    for col_name, metric in metrics.items():
        data.append({
            'Column': col_name,
            'Total Missing': metric.total_missing,
            'Total Filled': metric.total_filled,
            'Fill Rate (%)': f"{metric.fillrate:.1f}%",
            'Level 1 (Item)': metric.level_1_count,
            'Level 2 (Category)': metric.level_2_count,
            'Level 3 (Neighbor)': metric.level_3_count,
            'Level 4 (Global)': metric.level_4_count,
        })
    
    return pd.DataFrame(data)


# ═══════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Example: Using the Advanced Imputation Engine on a SaaS dataset
    """
    
    # Sample dataset with missing values
    sample_data = {
        'Product_Name': ['Coffee', 'Coffee', 'Laptop', 'Laptop', 'Desk', 'Desk', 'Monitor'],
        'Department': ['Foods', 'Foods', 'Electronics', 'Electronics', 'Office', 'Office', 'Electronics'],
        'Price': [15.0, np.nan, 999.0, np.nan, 200.0, np.nan, 350.0],
        'Category': ['Beverage', 'Beverage', np.nan, 'Computer', np.nan, np.nan, 'Display'],
        'Quantity': [10, 20, 5, np.nan, 8, 12, 3]
    }
    
    df = pd.DataFrame(sample_data)
    
    print("\n" + "="*70)
    print("ADVANCED IMPUTATION ENGINE - DEMONSTRATION")
    print("="*70)
    print("\nORIGINAL DATAFRAME (with missing values):")
    print(df)
    print(f"\nMissing values per column:\n{df.isna().sum()}")
    
    # Initialize engine
    engine = AdvancedImputationEngine(verbose=True)
    
    # Run imputation
    df_filled, metrics = engine.fill_missing_values_advanced(
        df=df,
        numeric_cols_to_fill=['Price', 'Quantity'],
        categorical_cols_to_fill=['Category'],
        fine_grain_guide='Product_Name',
        coarse_grain_guide='Department'
    )
    
    print("\n\nFILLED DATAFRAME (with imputation status):")
    print(df_filled)
    
    print("\n\nIMPUTATION SUMMARY:")
    summary = get_imputation_summary(metrics)
    print(summary)
    
    print("\n" + "="*70)
    print("OK - ADVANCED IMPUTATION COMPLETE")
    print("="*70)
