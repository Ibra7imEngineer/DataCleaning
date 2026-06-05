"""
Generic, production-ready imputation and cleaning utility for DataX.

Provides a single, fully-documented function `clean_and_impute` that:
- Standardises placeholder text into np.nan for all text columns
- Performs a 4-level context-aware numeric imputation waterfall
- Performs a 3-level context-aware categorical prediction
- Emits per-column imputation status columns
- Returns a pandas Styler highlighting Level-1/Level-2 filled rows

Key design goals:
- Fully vectorized (no `iterrows` or explicit Python loops over rows)
- Generic: no hardcoded column names; auto-detects numeric/text columns
- Production-minded: preserves original columns, writes status columns

Usage:
    from datax_imputation import clean_and_impute
    df_cleaned, styler = clean_and_impute(df,
                                         numeric_cols=None,
                                         categorical_cols=None,
                                         fine_grain_col='item_name',
                                         coarse_grain_col='category',
                                         transaction_keys=['order_id'])

Return: (cleaned_df, styler)
    - `cleaned_df` is a shallow copy of the original DataFrame with
      imputed values and new `{col}_imputation_status` columns.
    - `styler` is a `pandas.io.formats.style.Styler` instance with
      a premium neon-green background applied to rows filled by
      Level-1 or Level-2 context; it can be rendered by Streamlit.

"""
from typing import List, Optional, Tuple, Callable
import re
import numpy as np
import pandas as pd


def _common_placeholder_regex(extra_terms: Optional[List[str]] = None) -> re.Pattern:
    """Build a regex pattern for common placeholder tokens (multi-lingual).

    We include a short, conservative list of widely used placeholders
    (e.g. 'unknown', 'null', Arabic equivalents) and allow callers to
    extend it via `extra_terms`. Matching is case-insensitive and
    ignores surrounding whitespace and punctuation.
    """
    base = [
        r'unknown', r'null', r'none', r'n/?a', r'n\.?a\.?', r'missing',
        r'not available', r'ناقص', r'غير\s+محدد', r'غير\s+متوفر', r'بيانات\s+ناقصة',
    ]
    if extra_terms:
        base += [re.escape(t) for t in extra_terms if t]
    # word boundaries + allow punctuation/whitespace around
    pattern = r'^(?:[\W_]*)(?:' + r'|'.join(base) + r')(?:[\W_]*)$'
    return re.compile(pattern, flags=re.IGNORECASE | re.UNICODE)


def clean_and_impute(
    df: pd.DataFrame,
    numeric_cols: Optional[List[str]] = None,
    categorical_cols: Optional[List[str]] = None,
    fine_grain_col: Optional[str] = None,
    coarse_grain_col: Optional[str] = None,
    transaction_keys: Optional[List[str]] = None,
    placeholder_terms: Optional[List[str]] = None,
    copy: bool = True,
) -> Tuple[pd.DataFrame, pd.io.formats.style.Styler]:
    """
    Clean and impute numeric and categorical columns in a generic DataFrame.

    Parameters
    - df: input DataFrame (not mutated unless `copy=False`)
    - numeric_cols: list of numeric column names; if None, auto-detected
    - categorical_cols: list of categorical column names; if None, auto-detected
    - fine_grain_col: column name used for Level-1 grouping (e.g. item name)
    - coarse_grain_col: column name used for Level-2 grouping (e.g. category)
    - transaction_keys: list of columns that together identify a transaction/sequence
    - placeholder_terms: extra text tokens to treat as placeholders
    - copy: whether to operate on a copy (default True)

    Returns
    - (cleaned_df, styler): cleaned DataFrame and a Pandas Styler which highlights
      rows resolved by Level-1 or Level-2 context.

    Behavior overview
    1) Phase 1: standardises placeholder-like text to np.nan in all text columns.
    2) Phase 2: for each numeric col, uses the 4-step waterfall to impute missing values.
    3) Phase 3: for each categorical col, predicts missing values using item-mode,
       sequential neighbor, then global mode.
    4) Phase 4: emits `{col}_imputation_status` columns and a Styler highlighting
       Level-1/Level-2 filled rows.

    Notes
    - The function is vectorized and avoids row-wise Python loops.
    - If `fine_grain_col` or `coarse_grain_col` are not provided or missing from
      the DataFrame, their corresponding levels are skipped.
    """
    if copy:
        df = df.copy()

    # Auto-detect columns when not provided
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if categorical_cols is None:
        # treat object and string dtypes as categorical/text
        categorical_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()

    # Defensive filters: remove fine/coarse/transaction columns from processed lists
    reserved = set(filter(None, [fine_grain_col, coarse_grain_col]))
    if transaction_keys:
        reserved.update(transaction_keys)
    numeric_cols = [c for c in numeric_cols if c not in reserved]
    categorical_cols = [c for c in categorical_cols if c not in reserved]

    # PHASE 1: Text standardisation -> convert common placeholders to np.nan
    placeholder_re = _common_placeholder_regex(placeholder_terms)

    text_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    for col in text_cols:
        # build boolean mask of values considered placeholders
        series = df[col].astype("string")
        # empty / whitespace-only strings
        empty_mask = series.str.strip().eq("")
        # regex placeholders
        placeholder_mask = series.fillna("").str.strip().apply(lambda v: bool(placeholder_re.match(v)))
        mask = empty_mask | placeholder_mask
        # set to np.nan where placeholder detected
        if mask.any():
            df.loc[mask, col] = np.nan

    # Helper: build transaction-equality masks for neighbor checks
    if transaction_keys:
        # Ensure keys exist
        tx_keys = [k for k in transaction_keys if k in df.columns]
        if tx_keys:
            # DataFrame of booleans where each key equals previous/next
            prev_eq = pd.concat([df[k].eq(df[k].shift(1)) for k in tx_keys], axis=1).all(axis=1)
            next_eq = pd.concat([df[k].eq(df[k].shift(-1)) for k in tx_keys], axis=1).all(axis=1)
        else:
            prev_eq = pd.Series(False, index=df.index)
            next_eq = pd.Series(False, index=df.index)
    else:
        prev_eq = pd.Series(False, index=df.index)
        next_eq = pd.Series(False, index=df.index)

    # Keep track of which status values correspond to Level 1/2 for styling
    L1_L2_statuses = set([
        'Filled by Item Match',            # numeric L1
        'Filled by Category Fallback',     # numeric L2
        'Filled by Item Mode',             # categorical L1
        'Filled by Sequential Neighbor',   # categorical L2
    ])

    # PHASE 2: Context-aware numeric imputation (4-step waterfall)
    for col in numeric_cols:
        status_col = f"{col}_imputation_status"
        # initialize status: Original for non-missing, Missing for NaN
        is_missing_orig = df[col].isna()
        df[status_col] = np.where(is_missing_orig, 'Missing', 'Original')

        # Level 1: Group by fine_grain_col median
        if fine_grain_col and fine_grain_col in df.columns:
            med_fine = df.groupby(fine_grain_col)[col].transform('median')
            mask_lvl1 = df[col].isna() & med_fine.notna()
            df.loc[mask_lvl1, col] = med_fine[mask_lvl1]
            df.loc[mask_lvl1, status_col] = 'Filled by Item Match'

        # Level 2: Group by coarse_grain_col median
        if coarse_grain_col and coarse_grain_col in df.columns:
            med_coarse = df.groupby(coarse_grain_col)[col].transform('median')
            mask_lvl2 = df[col].isna() & med_coarse.notna()
            df.loc[mask_lvl2, col] = med_coarse[mask_lvl2]
            df.loc[mask_lvl2, status_col] = 'Filled by Category Fallback'

        # Level 3: Sequential neighbor copy (previous then next) when transaction keys match
        remaining_na = df[col].isna()
        if remaining_na.any() and (prev_eq.any() or next_eq.any()):
            prev_vals = df[col].shift(1)
            mask_prev = remaining_na & prev_eq & prev_vals.notna()
            df.loc[mask_prev, col] = prev_vals[mask_prev]
            df.loc[mask_prev, status_col] = 'Filled by Sequential Neighbor'

            # recompute remaining
            remaining_na = df[col].isna()
            next_vals = df[col].shift(-1)
            mask_next = remaining_na & next_eq & next_vals.notna()
            df.loc[mask_next, col] = next_vals[mask_next]
            df.loc[mask_next, status_col] = 'Filled by Sequential Neighbor'

        # Level 4: Global median as last resort
        remaining_na = df[col].isna()
        if remaining_na.any():
            try:
                global_med = df[col].median(skipna=True)
            except Exception:
                global_med = np.nan
            if pd.notna(global_med):
                mask_lvl4 = remaining_na
                df.loc[mask_lvl4, col] = global_med
                df.loc[mask_lvl4, status_col] = 'Filled by Global Median'
            else:
                # Could not compute a global median (no numeric data at all)
                df.loc[remaining_na, status_col] = 'Unfilled'

    # PHASE 3: Context-aware categorical prediction (Mode + neighbors + global mode)
    for col in categorical_cols:
        status_col = f"{col}_imputation_status"
        # initialize status
        is_missing_orig = df[col].isna()
        df[status_col] = np.where(is_missing_orig, 'Missing', 'Original')

        # Level 1: Group by fine_grain_col mode
        if fine_grain_col and fine_grain_col in df.columns:
            # compute group mode mapping (first mode if multimodal)
            grp = df.groupby(fine_grain_col)[col]
            def first_mode(s):
                s2 = s.dropna()
                if s2.empty:
                    return np.nan
                modes = s2.mode()
                return modes.iloc[0] if not modes.empty else np.nan

            group_mode = grp.transform(lambda s: first_mode(s))
            mask_lvl1 = df[col].isna() & group_mode.notna()
            df.loc[mask_lvl1, col] = group_mode[mask_lvl1]
            df.loc[mask_lvl1, status_col] = 'Filled by Item Mode'

        # Level 2: Sequential neighbor copy when transaction keys match
        remaining_na = df[col].isna()
        if remaining_na.any() and (prev_eq.any() or next_eq.any()):
            prev_vals = df[col].shift(1)
            mask_prev = remaining_na & prev_eq & prev_vals.notna()
            df.loc[mask_prev, col] = prev_vals[mask_prev]
            df.loc[mask_prev, status_col] = 'Filled by Sequential Neighbor'

            remaining_na = df[col].isna()
            next_vals = df[col].shift(-1)
            mask_next = remaining_na & next_eq & next_vals.notna()
            df.loc[mask_next, col] = next_vals[mask_next]
            df.loc[mask_next, status_col] = 'Filled by Sequential Neighbor'

        # Level 3: Global mode fallback
        remaining_na = df[col].isna()
        if remaining_na.any():
            try:
                global_mode = df[col].mode(dropna=True)
                global_mode_val = global_mode.iloc[0] if not global_mode.empty else np.nan
            except Exception:
                global_mode_val = np.nan
            if pd.notna(global_mode_val):
                df.loc[remaining_na, col] = global_mode_val
                df.loc[remaining_na, status_col] = 'Filled by Global Mode'
            else:
                df.loc[remaining_na, status_col] = 'Unfilled'

    # PHASE 4: Build a Pandas Styler that highlights rows filled by Level-1/Level-2
    def _styler_highlight(s: pd.Series) -> List[str]:
        """Return CSS styles for a row series: neon-green for L1/L2 rows, otherwise empty."""
        # Check any _imputation_status columns for L1/L2 values
        status_cols = [c for c in s.index if str(c).endswith('_imputation_status')]
        row_statuses = s[status_cols].astype(str)
        highlight = any(st in L1_L2_statuses for st in row_statuses.values)
        if highlight:
            return ['background-color: rgba(46, 204, 113, 0.2)'] * len(s)
        return [''] * len(s)

    styler = df.style.apply(_styler_highlight, axis=1)

    return df, styler
