"""Enterprise-grade data cleaning utilities for DataX projects.

This module provides a single unified, fully-vectorized pipeline
`ultimate_datax_cleaner` that performs strict pre-cleaning of string
placeholders, context-aware numeric imputation (granular -> category ->
sequence -> global), and context-aware categorical prediction (mode ->
sequence -> global). It does not mutate the original DataFrame passed
in; it returns a cleaned copy and creates an imputation status column
for every column in `numeric_cols` and `categorical_cols` named
`{col}_imputation_status` with values from the set
{'Filled by Item Match','Filled by Category Fallback','Original'}.

Also provides `style_datax_dataframe` which returns a pandas Styler
highlighting rows resolved by Level 1 or Level 2 fills for a given
numeric target column.

Execution flow (strict):
- Phase 1: Trim whitespace from all object/string columns and replace
  explicit placeholder strings with real `np.nan` values.
- Phase 2: For each numeric column: coerce to numeric and fill NaNs in
  the cascading order: group(fine_grain_col) median ->
  group(coarse_grain_col) median -> ffill/bfill -> global median. Mark Level 1 and Level 2 fills
  in `{col}_imputation_status`.
- Phase 3: For each categorical column: fill NaNs by group(fine_grain_col)
  mode -> ffill/bfill -> global mode. Mark Level 1 as
  'Filled by Item Match' and Level 2 as 'Filled by Category Fallback'.

All operations are written to be fully vectorized and avoid `iterrows`.
"""

from typing import List

import numpy as np
import pandas as pd


PLACEHOLDERS = ['غير محدد', 'بيانات ناقصة', 'unknown', 'null', '', 'nan', 'None']


def ultimate_datax_cleaner(
    df: pd.DataFrame,
    numeric_cols: List[str],
    categorical_cols: List[str],
    fine_grain_col: str,
    coarse_grain_col: str,
) -> pd.DataFrame:
    """Return a cleaned copy of `df` with context-aware imputations.

    Parameters
    - df: original DataFrame (not mutated).
    - numeric_cols: list of numeric column names to impute.
    - categorical_cols: list of categorical column names to impute.
    - fine_grain_col: identifier column used for the most granular grouping
      (e.g., item name).
    - coarse_grain_col: higher-level grouping used as a fallback
      (e.g., category/department).

    Behavior (summary):
    1. Phase 1: Trim whitespace for all object/string columns and convert
       explicit placeholder tokens to `np.nan`.
    2. Phase 2 (numeric waterfall): For each numeric column, coerce to
       numeric and fill missing values by: item median -> category median
       -> ffill/bfill -> global median. Only Level 1 and Level 2 fills
       are recorded in `{col}_imputation_status` as required. All other
       cells keep status 'Original'.
    3. Phase 3 (categorical prediction): For each categorical column,
       fill missing values by: item mode -> ffill/bfill -> global mode.
       Level 1 and Level 2 fills are recorded similarly in
       `{col}_imputation_status`.

    Returns
    - A deep copy of the DataFrame with imputations applied and status
      columns added per target column.
    """

    # Work on a deep copy to avoid mutating caller's DataFrame
    df_clean = df.copy(deep=True)

    # Phase 1: strict pre-cleaning of string-like columns
    obj_cols = df_clean.select_dtypes(include=["object", "string"]).columns.tolist()
    for col in obj_cols:
        # convert to string dtype for safe vectorized operations, then strip
        s = df_clean[col].astype("string").str.strip()
        # Replace explicit placeholders with np.nan (this must happen first)
        s = s.replace(PLACEHOLDERS, np.nan)
        # Any empty/blank strings after strip should also be NaN
        s = s.where(s.str.len().fillna(0) > 0, np.nan)
        df_clean[col] = s

    # Helper for marking status columns
    def _init_status(series: pd.Series) -> pd.Series:
        return pd.Series(np.where(series.notna(), 'Original', np.nan), index=series.index)

    # Phase 2: numeric waterfall logic
    for col in numeric_cols:
        if col not in df_clean.columns:
            continue
        # coerce to numeric (creates np.nan where coercion fails)
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

        status = _init_status(df_clean[col])

        # LEVEL 1: Fine-grain median (item-level)
        try:
            item_median = df_clean.groupby(fine_grain_col)[col].transform('median')
        except Exception:
            # If grouping column missing or problematic, create all-NaN
            item_median = pd.Series(np.nan, index=df_clean.index)

        mask1 = df_clean[col].isna() & item_median.notna()
        if mask1.any():
            df_clean.loc[mask1, col] = item_median[mask1]
            status.loc[mask1] = 'Filled by Item Match'

        # LEVEL 2: Coarse-grain median (category-level)
        try:
            cat_median = df_clean.groupby(coarse_grain_col)[col].transform('median')
        except Exception:
            cat_median = pd.Series(np.nan, index=df_clean.index)

        mask2 = df_clean[col].isna() & cat_median.notna()
        if mask2.any():
            df_clean.loc[mask2, col] = cat_median[mask2]
            # Only set Category Fallback if not already filled by Level1
            status.loc[mask2] = 'Filled by Category Fallback'

        # LEVEL 3: Sequence neighbor propagation (ffill then bfill)
        remaining = df_clean[col].isna()
        if remaining.any():
            seq_filled = df_clean[col].ffill().bfill()
            mask3 = remaining & seq_filled.notna()
            if mask3.any():
                df_clean.loc[mask3, col] = seq_filled[mask3]
                # Per specification, only Level1 and Level2 get special status.
                # Leave these as 'Original' for downstream UI semantics.

        # LEVEL 4: Global median as last resort
        remaining = df_clean[col].isna()
        if remaining.any():
            global_med = df_clean[col].median(skipna=True)
            if not np.isnan(global_med):
                df_clean.loc[remaining, col] = global_med

        # Finalize status column (fill any remaining NaN statuses with 'Original')
        status = status.fillna('Original')
        df_clean[f"{col}_imputation_status"] = status

    # Phase 3: categorical prediction
    for col in categorical_cols:
        if col not in df_clean.columns:
            continue
        # Ensure string dtype and already pre-cleaned by Phase 1
        df_clean[col] = df_clean[col].astype('string')

        status = _init_status(df_clean[col])

        # LEVEL 1: Group (fine_grain_col) mode
        def _group_mode(series: pd.Series):
            m = series.mode()
            return m.iloc[0] if not m.empty else np.nan

        try:
            item_mode = df_clean.groupby(fine_grain_col)[col].transform(lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan)
        except Exception:
            item_mode = pd.Series(np.nan, index=df_clean.index)

        mask1 = df_clean[col].isna() & item_mode.notna()
        if mask1.any():
            df_clean.loc[mask1, col] = item_mode[mask1]
            status.loc[mask1] = 'Filled by Item Match'

        # LEVEL 2: Transaction sequence ffill/bfill
        remaining = df_clean[col].isna()
        if remaining.any():
            seq_vals = df_clean[col].ffill().bfill()
            mask2 = remaining & seq_vals.notna()
            if mask2.any():
                df_clean.loc[mask2, col] = seq_vals[mask2]
                status.loc[mask2] = 'Filled by Category Fallback'

        # LEVEL 3: Global mode fallback
        remaining = df_clean[col].isna()
        if remaining.any():
            global_mode = df_clean[col].mode()
            if not global_mode.empty:
                df_clean.loc[remaining, col] = global_mode.iloc[0]

        # Finalize status
        status = status.fillna('Original')
        df_clean[f"{col}_imputation_status"] = status

    return df_clean


def style_datax_dataframe(df: pd.DataFrame, target_numeric_col: str) -> pd.io.formats.style.Styler:
    """Return a pandas Styler highlighting rows with Level 1/Level 2 fills.

    The Styler highlights entire rows where the corresponding
    `{target_numeric_col}_imputation_status` value is either
    'Filled by Item Match' or 'Filled by Category Fallback'. The style
    uses a semi-transparent neon green background and green text to
    work well in Streamlit's `st.dataframe` widget.

    This function does not modify the DataFrame; it returns a Styler.
    """

    status_col = f"{target_numeric_col}_imputation_status"

    if status_col not in df.columns:
        # Nothing to highlight; return default styler
        return df.style

    highlight_values = {'Filled by Item Match', 'Filled by Category Fallback'}

    def _highlight_row(row: pd.Series):
        if row.get(status_col) in highlight_values:
            return ['background-color: rgba(46, 204, 113, 0.25); color: #2ecc71'] * len(row)
        return [''] * len(row)

    return df.style.apply(_highlight_row, axis=1)
