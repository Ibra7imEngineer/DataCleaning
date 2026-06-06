import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import difflib
import unicodedata

from .date_cleaner import clean_dates_advanced


_PLACEHOLDERS = [
    'غير محدد', 'بيانات ناقصة', 'unknown', 'null', '', 'nan', 'None'
]

_ARABIC_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

_COUNTRY_CONFIG = {
    '+20': ('+20', 12, 13),
    '+966': ('+966', 12, 13),
    '+971': ('+971', 12, 13),
    '+965': ('+965', 11, 12),
    '+974': ('+974', 11, 12),
    '+973': ('+973', 12, 13),
    '+968': ('+968', 11, 12),
    '+962': ('+962', 12, 13),
    '+964': ('+964', 13, 14),
    '+961': ('+961', 10, 11),
    '+963': ('+963', 12, 13),
    '+970': ('+970', 12, 13),
    '+967': ('+967', 12, 13),
    '+249': ('+249', 12, 13),
    '+218': ('+218', 12, 13),
    '+216': ('+216', 12, 13),
    '+213': ('+213', 12, 13),
    '+212': ('+212', 12, 13),
    '+222': ('+222', 12, 13),
}


@dataclass
class AuditTrail:
    records: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.records is None:
            self.records = []

    def log_change(self, row_idx: int, col_name: str, old_value: Any, new_value: Any, reason: str = "") -> None:
        """Log a single cell-level change."""
        self.records.append({
            "row_index": row_idx,
            "column": col_name,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "type": "cell_change",
        })

    def log_bulk_change(self, count: int, message: str) -> None:
        self.records.append({
            "count": count,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "type": "bulk_change",
        })

    def get_audit_report(self) -> List[Dict[str, Any]]:
        return list(self.records)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert the audit trail records into a DataFrame for display/export."""
        return pd.DataFrame(self.records)


class AdvancedCleaner:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy(deep=True)
        self.audit_trail = AuditTrail()
        self.text_imputation_mask = None  # Store imputation mask for later access

    def run_full_pipeline(
        self,
        clean_phones: bool = True,
        clean_numeric: bool = True,
        fuzzy_match: bool = True,
        fix_dates: bool = True,
        optimize_mem: bool = True,
        impute_text: bool = True,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Run the full cleaning pipeline and return cleaned DataFrame + text imputation mask.
        
        Returns:
            Tuple of (cleaned_df, text_imputation_mask)
            - cleaned_df: Main DataFrame with all cleaning operations applied
            - text_imputation_mask: Boolean mask DataFrame (True only for imputed text cells)
        """
        df = self.df.copy(deep=True)
        text_mask = pd.DataFrame(False, index=df.index, columns=df.columns)

        if clean_phones:
            df, phone_log = clean_phone_column(df)
            if phone_log.get("phones_standardized", 0) > 0:
                self.audit_trail.log_bulk_change(
                    phone_log["phones_standardized"],
                    "Phone number standardization",
                )

        if clean_numeric:
            df, numeric_log = clean_numeric_columns(df)
            if numeric_log.get("columns_cleaned", 0) > 0:
                self.audit_trail.log_bulk_change(
                    numeric_log["values_converted"],
                    "Mixed numeric cleaning",
                )

        # Name/company column cleanup: normalize spacing, unicode, and harmonize similar names
        try:
            df, name_log = clean_name_columns(df)
            if name_log.get("columns_cleaned", 0) > 0:
                self.audit_trail.log_bulk_change(
                    name_log.get("harmonized", 0),
                    "Name/company column normalization",
                )
        except Exception:
            # non-fatal: don't break pipeline if name cleaning fails
            pass

        if fuzzy_match:
            df, fuzzy_log = apply_fuzzy_matching(df)
            if fuzzy_log.get("total_changes", 0) > 0:
                self.audit_trail.log_bulk_change(
                    fuzzy_log["total_changes"],
                    "Fuzzy text harmonization",
                )

        if fix_dates:
            df, dates_log = clean_dates_advanced(df)
            if dates_log.get("dates_fixed", 0) > 0:
                self.audit_trail.log_bulk_change(
                    dates_log["dates_fixed"],
                    "Advanced date cleaning",
                )

        # NEW: Dynamic Contextual Text Imputation
        if impute_text:
            df, text_mask = dynamic_contextual_text_imputation(df)
            imputation_count = text_mask.sum().sum()
            if imputation_count > 0:
                self.audit_trail.log_bulk_change(
                    int(imputation_count),
                    "Dynamic contextual text imputation",
                )
            self.text_imputation_mask = text_mask

        if optimize_mem:
            df, mem_log = optimize_memory(df)
            self.audit_trail.log_bulk_change(
                int(mem_log.get("reduction_bytes", 0)),
                "Memory optimization",
            )

        return df, text_mask

    def get_audit_trail(self) -> AuditTrail:
        return self.audit_trail
    
    def get_text_imputation_mask(self) -> pd.DataFrame:
        """Get the text imputation mask (True where text values were imputed)."""
        if self.text_imputation_mask is None:
            return pd.DataFrame(False, index=self.df.index, columns=self.df.columns)
        return self.text_imputation_mask


def _to_western_digits(text: str) -> str:
    return str(text).translate(_ARABIC_DIGITS)


def standardize_phone_number(phone: Union[str, float, int, None], default_country: str = "+20") -> str:
    if pd.isna(phone):
        return ""

    phone_text = _to_western_digits(str(phone).strip())
    phone_text = re.sub(r"[^\d+]|\s+", "", phone_text)

    if phone_text.startswith("00"):
        phone_text = "+" + phone_text[2:]

    if phone_text.startswith("20") and len(phone_text) >= 11:
        phone_text = "+" + phone_text
    elif phone_text.startswith("966") and len(phone_text) >= 12:
        phone_text = "+" + phone_text
    elif phone_text.startswith("971") and len(phone_text) >= 12:
        phone_text = "+" + phone_text
    elif phone_text.startswith("1") and len(phone_text) == 11:
        phone_text = "+20" + phone_text[1:]
    elif phone_text.startswith("5") and len(phone_text) == 9:
        phone_text = "+966" + phone_text
    elif phone_text.startswith("05") and len(phone_text) == 10:
        phone_text = "+966" + phone_text[1:]
    elif not phone_text.startswith("+"):
        phone_text = default_country + phone_text

    for code, (_, min_len, max_len) in _COUNTRY_CONFIG.items():
        if phone_text.startswith(code):
            if min_len <= len(phone_text) <= max_len:
                return phone_text
            return ""

    if phone_text.startswith("+") and 10 <= len(phone_text) <= 15:
        return phone_text

    return ""


def detect_phone_column(df: pd.DataFrame) -> Optional[str]:
    keywords = [
        'phone', 'tel', 'mobile', 'رقم', 'تليفون', 'الهاتف',
        'cellular', 'number', 'هاتف', 'جوال', 'نقال',
        'mob', 'cell', 'phone_no', 'phone_num',
    ]
    for col in df.columns:
        col_lower = str(col).lower()
        if any(kw in col_lower for kw in keywords):
            return col
    return None


def clean_phone_column(df: pd.DataFrame, col_name: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, int]]:
    log = {
        "phones_standardized": 0,
        "invalid_phones": 0,
        "empty_phones": 0,
    }

    if col_name is None:
        col_name = detect_phone_column(df)

    if col_name is None or col_name not in df.columns:
        return df, log

    df_copy = df.copy()
    original_values = df_copy[col_name].copy()
    df_copy[col_name] = df_copy[col_name].fillna("").astype(str).apply(standardize_phone_number)

    log["phones_standardized"] = int((original_values.astype(str) != df_copy[col_name]).sum())
    log["invalid_phones"] = int((df_copy[col_name] == "").sum())
    log["empty_phones"] = int(df_copy[col_name].eq("").sum())

    return df_copy, log


def _common_placeholder_regex(extra_terms: Optional[List[str]] = None) -> re.Pattern:
    base = [
        r'nan', r'unknown', r'null', r'none', r'n/?a', r'n\.?.a\.?', r'missing',
        r'not available', r'ناقص', r'غير\s+محدد', r'غير\s+متوفر', r'بيانات\s+ناقصة',
    ]
    if extra_terms:
        base += [re.escape(t) for t in extra_terms if t]
    pattern = r'^(?:[\W_]*)(?:' + r'|'.join(base) + r')(?:[\W_]*)$'
    return re.compile(pattern, flags=re.IGNORECASE | re.UNICODE)


def clean_mixed_numeric(value: Any) -> Optional[float]:
    if pd.isna(value):
        return np.nan

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    val = str(value).strip()
    if not val:
        return np.nan

    val = _to_western_digits(val)
    val = val.replace('٬', '').replace('٫', '.')

    negative = False
    if val.startswith('(') and val.endswith(')'):
        negative = True
        val = val[1:-1]
    elif val.startswith('(-') and val.endswith(')'):
        negative = True
        val = val[2:-1]

    val = re.sub(r'[\$€¥£]', '', val)
    val = re.sub(r'\b(USD|EGP|SAR|AED|KWD|QAR|OMR|BHD|JOD|LBP|IQD|MAD|TND|DZD|LYD|SDG|YER|SYP|PLE|MRU|EUR|GBP|CNY|JPY|ج\.م|ج\s*\.\s*م|ريال|درهم|دينار|جنيه|ليرة| pound| dollar| euro| dirham| riyal)\b', '', val, flags=re.IGNORECASE)
    val = re.sub(r'(?<=\d)\s+(?=\d)', '', val)
    val = re.sub(r'[^\d\.\-KMBkmb%]', '', val)

    pct = False
    if val.endswith('%'):
        pct = True
        val = val[:-1]

    multiplier = 1.0
    if val:
        suffix = val[-1].upper()
        if suffix == 'K':
            multiplier = 1_000
            val = val[:-1]
        elif suffix == 'M':
            multiplier = 1_000_000
            val = val[:-1]
        elif suffix == 'B':
            multiplier = 1_000_000_000
            val = val[:-1]

    try:
        result = float(val) * multiplier
        if pct:
            result = result / 100.0
        if negative:
            result = -abs(result)
        return result
    except ValueError:
        return np.nan


def detect_numeric_columns_with_text(df: pd.DataFrame) -> List[str]:
    numeric_cols = []

    for col in df.columns:
        sample = df[col].dropna().astype(str).head(20)
        if sample.empty:
            continue

        has_digits = any(any(c.isdigit() for c in val) for val in sample)
        has_text = any(any(c.isalpha() for c in val) for val in sample)
        if has_digits and has_text:
            numeric_cols.append(col)

    return numeric_cols


def clean_numeric_columns(df: pd.DataFrame, cols: Optional[List[str]] = None) -> Tuple[pd.DataFrame, Dict[str, int]]:
    if cols is None:
        cols = detect_numeric_columns_with_text(df)

    df_copy = df.copy()
    log = {
        "columns_cleaned": 0,
        "values_converted": 0,
        "invalid_conversions": 0,
    }

    for col in cols:
        if col not in df_copy.columns:
            continue

        original_non_null = int(df_copy[col].notna().sum())
        df_copy[col] = df_copy[col].apply(clean_mixed_numeric)
        after_non_null = int(df_copy[col].notna().sum())

        log["columns_cleaned"] += 1
        log["values_converted"] += int(after_non_null)
        log["invalid_conversions"] += max(0, original_non_null - after_non_null)

    return df_copy, log


def _normalize_text_value(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def _build_fuzzy_mapping(series: pd.Series, threshold: int = 90) -> Dict[str, str]:
    from rapidfuzz import process, fuzz

    unique_vals = [v for v in series.dropna().astype(str).unique() if str(v).strip() != ""]
    mapping: Dict[str, str] = {}
    processed = set()
    normalized = {val: re.sub(r'\s+', ' ', _normalize_text_value(val)).strip() for val in unique_vals}
    value_counts = series.value_counts(dropna=True).to_dict()

    for value in unique_vals:
        if value in processed:
            continue

        processed.add(value)
        group = [value]
        base = normalized[value]

        candidates = [v for v in unique_vals if v not in processed and normalized[v] != ""]
        matches = process.extract(base, [normalized[c] for c in candidates], scorer=fuzz.token_set_ratio, limit=None)
        for candidate_norm, score, idx in matches:
            if score >= threshold:
                candidate = candidates[idx]
                processed.add(candidate)
                group.append(candidate)

        if len(group) > 1:
            canonical = max(group, key=lambda x: value_counts.get(x, 0))
            for member in group:
                mapping[member] = canonical
        else:
            mapping[value] = value

    return mapping


def apply_fuzzy_matching(df: pd.DataFrame, cols: Optional[List[str]] = None, threshold: int = 90) -> Tuple[pd.DataFrame, Dict[str, int]]:
    log = {
        "columns_processed": 0,
        "duplicates_merged": 0,
        "total_changes": 0,
    }

    if cols is None:
        cols = df.select_dtypes(include=['object', 'string']).columns.tolist()

    df_copy = df.copy()
    for col in cols:
        if col not in df_copy.columns:
            continue

        mapping = _build_fuzzy_mapping(df_copy[col], threshold=threshold)
        if not mapping:
            continue

        original = df_copy[col].copy()
        df_copy[col] = df_copy[col].map(lambda x: mapping.get(str(x), x))
        changes = int((original != df_copy[col]).sum())

        log["columns_processed"] += 1
        log["duplicates_merged"] += len([k for k, v in mapping.items() if k != v])
        log["total_changes"] += changes

    return df_copy, log


def optimize_memory(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    df_copy = df.copy()
    before = df_copy.memory_usage(deep=True).sum()

    for col in df_copy.columns:
        series = df_copy[col]
        if pd.api.types.is_integer_dtype(series):
            df_copy[col] = pd.to_numeric(series, downcast="integer")
        elif pd.api.types.is_float_dtype(series):
            df_copy[col] = pd.to_numeric(series, downcast="float")
        elif pd.api.types.is_object_dtype(series):
            card = series.nunique(dropna=False) / max(len(series), 1)
            if card <= 0.2:
                df_copy[col] = series.astype("category")

    after = df_copy.memory_usage(deep=True).sum()
    reduction_bytes = int(before - after)
    reduction_percent = int((reduction_bytes / before * 100)) if before > 0 else 0
    
    return df_copy, {
        "memory_before_bytes": int(before),
        "memory_after_bytes": int(after),
        "reduction_bytes": reduction_bytes,
        "reduction_percent": reduction_percent,
    }


def read_csv_with_encoding_fallback(file_path: str) -> pd.DataFrame:
    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1256",
        "windows-1256",
        "iso-8859-6",
        "latin-1",
    ]

    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except Exception:
            continue

    return pd.read_csv(file_path, encoding="utf-8", errors="replace")


# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMIC CONTEXTUAL TEXT IMPUTATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def _normalize_for_matching(text: Any) -> str:
    """Normalize text for matching by converting to lowercase and removing special chars."""
    if pd.isna(text) or text is None:
        return ""
    text = str(text).strip().lower()
    text = re.sub(r'[^\w\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def _extract_keywords_from_text(text: str, min_length: int = 2) -> set:
    """Extract keywords from descriptive text (words, not short strings)."""
    if pd.isna(text) or not isinstance(text, str):
        return set()
    words = re.findall(r'\b\w+\b', text.lower())
    return set(w for w in words if len(w) >= min_length)


def _find_contextual_sibling_value(
    df: pd.DataFrame,
    target_row_idx: int,
    target_col: str,
    context_cols: Optional[List[str]] = None,
) -> Optional[str]:
    """
    Search for missing value in target_col by finding rows with matching context columns.

    Strategy:
    1. Look for rows where context columns match the target row
    2. Return non-null value from target_col if found
    3. Prioritize rows with exact multi-column match
    """
    if context_cols is None or len(context_cols) == 0:
        return None

    target_row = df.iloc[target_row_idx]
    best_candidate = None
    best_match_count = 0
    placeholder_rx = _common_placeholder_regex()

    for context_col in context_cols:
        if context_col not in df.columns or pd.isna(target_row[context_col]):
            continue

        context_val = _normalize_for_matching(target_row[context_col])
        if not context_val:
            continue

        # Find all rows where context_col matches
        mask = df[context_col].apply(lambda x: _normalize_for_matching(x) == context_val)
        matching_rows = df.index[mask & df[target_col].notna()]

        if len(matching_rows) > 0:
            # Get the most common non-null value
            candidates = df.loc[matching_rows, target_col].dropna().astype(str)
            if len(candidates) > 0:
                value_counts = candidates.value_counts()
                candidate = str(value_counts.index[0]).strip()
                if candidate and not placeholder_rx.match(candidate):
                    match_count = len(matching_rows)
                    if match_count > best_match_count:
                        best_candidate = candidate
                        best_match_count = match_count

    return best_candidate


def _extract_value_from_descriptive_column(
    row: pd.Series,
    target_col: str,
    descriptive_cols: Optional[List[str]] = None,
    keywords: Optional[set] = None,
) -> Optional[str]:
    """
    Extract missing categorical value from descriptive text using keyword matching.

    Example:
    - Missing "Color" in row
    - "Product Description" = "Red leather jacket with zipper"
    - Keywords for Color category = {"red", "blue", "green", ...}
    - Match "Red" from description -> return as Color value
    """
    if descriptive_cols is None or len(descriptive_cols) == 0:
        return None

    if keywords is None:
        keywords = set()

    for desc_col in descriptive_cols:
        if desc_col not in row.index or pd.isna(row[desc_col]):
            continue

        desc_text = str(row[desc_col]).lower()
        keywords_from_desc = _extract_keywords_from_text(desc_text)

        # Find intersection between keywords and description words
        matched_keywords = keywords_from_desc & keywords

        if matched_keywords:
            # Return the first (most likely) matched keyword
            return list(matched_keywords)[0].capitalize()

    return None


def _detect_categorical_columns(df: pd.DataFrame) -> List[str]:
    """
    Detect categorical/text columns that could have missing values to impute.
    Exclude: identifiers, PII, very high cardinality, and columns with no missing values.
    """
    categorical_cols = []
    
    for col in df.select_dtypes(include=['object', 'string', 'category']).columns:
        if col.startswith('__'):
            continue
        
        # Skip if no missing values
        if df[col].notna().all():
            continue
        
        # Skip PII columns (email, phone, SSN patterns)
        sample = df[col].dropna().astype(str).head(50)
        if len(sample) == 0:
            continue
        
        email_count = sum(1 for v in sample if '@' in v and '.' in v)
        phone_count = sum(1 for v in sample if re.search(r'[\d\s\-()]{7,}', v))
        
        if email_count / len(sample) > 0.5 or phone_count / len(sample) > 0.5:
            continue
        
        # Skip very high cardinality columns (likely identifiers)
        cardinality_ratio = df[col].nunique() / len(df)
        if cardinality_ratio > 0.8:
            continue
        
        categorical_cols.append(col)
    
    return categorical_cols


def _find_descriptive_text_columns(df: pd.DataFrame) -> List[str]:
    """Find columns that likely contain descriptive text (description, notes, comments, etc.)."""
    descriptive_keywords = [
        'description', 'notes', 'comments', 'text', 'detail', 'info',
        'remarks', 'details', 'summary', 'content', 'message',
        'وصف', 'ملاحظات', 'تعليقات', 'تفاصيل', 'معلومات',
    ]
    
    descriptive_cols = []
    for col in df.select_dtypes(include=['object', 'string']).columns:
        col_lower = str(col).lower()
        if any(kw in col_lower for kw in descriptive_keywords):
            descriptive_cols.append(col)
    
    return descriptive_cols


def _identify_context_columns(df: pd.DataFrame, target_col: str) -> List[str]:
    """
    Identify columns that could provide context for imputing target_col.
    Prioritize: categorical/low cardinality columns that are NOT the target.
    """
    context_candidates = []
    
    for col in df.columns:
        if col == target_col or col.startswith('__'):
            continue
        
        # Skip numeric columns for context
        if pd.api.types.is_numeric_dtype(df[col]):
            continue
        
        # Prefer low-cardinality text columns
        cardinality_ratio = df[col].nunique() / len(df)
        if cardinality_ratio < 0.3:
            context_candidates.append((col, cardinality_ratio))
    
    # Sort by cardinality (lower is better for context)
    context_candidates.sort(key=lambda x: x[1])
    return [col for col, _ in context_candidates[:5]]  # Top 5 context columns


def dynamic_contextual_text_imputation(
    df: pd.DataFrame,
    target_columns: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Perform intelligent contextual imputation for missing categorical/text values.
    
    Returns:
        - Updated DataFrame with imputed text values
        - Boolean Mask DataFrame (True only where imputation occurred)
    """
    # Mutate the source DataFrame directly so the same dataset object
    # is used for UI rendering and export/download operations.
    df_filled = df
    imputation_mask = pd.DataFrame(False, index=df.index, columns=df.columns)
    predicted_mask = pd.DataFrame(False, index=df.index, columns=df.columns)

    # Universal Null Identification: normalize common placeholders to real NaN
    placeholder_rx = _common_placeholder_regex()
    for col in df_filled.select_dtypes(include=['object', 'string']).columns:
        # Replace matches like '', ' ', 'unknown', 'null', 'NaN', etc. with np.nan
        def _norm(v):
            try:
                if v is None:
                    return np.nan
                if pd.isna(v):
                    return np.nan
            except Exception:
                pass
            if isinstance(v, str):
                if v.strip() == "":
                    return np.nan
                if placeholder_rx.match(v):
                    return np.nan
            return v

        df_filled[col] = df_filled[col].apply(_norm)

    # Auto-detect categorical columns if not provided
    if target_columns is None:
        target_columns = _detect_categorical_columns(df_filled)

    if len(target_columns) == 0:
        return df_filled, imputation_mask

    descriptive_cols = _find_descriptive_text_columns(df_filled)

    # Helper to detect whether a column is primarily Arabic (for sensible Arabic fallback)
    arabic_re = re.compile(r'[\u0600-\u06FF]')
    def _col_prefers_arabic(series: pd.Series) -> bool:
        sample = series.dropna().astype(str).head(200)
        if sample.empty:
            return True
        arabic_count = sum(1 for v in sample if bool(arabic_re.search(v)))
        return arabic_count / max(len(sample), 1) >= 0.5

    # Keep a snapshot of which cells were originally missing (after normalization)
    original_missing = pd.DataFrame(False, index=df_filled.index, columns=df_filled.columns)
    for col in df_filled.select_dtypes(include=['object', 'string']).columns:
        original_missing[col] = df_filled[col].isna()

    # Primary imputation strategies
    for target_col in target_columns:
        if target_col not in df_filled.columns:
            continue

        # Rows considered missing after normalization
        missing_mask = df_filled[target_col].isna()
        missing_indices = df_filled.index[missing_mask]
        if len(missing_indices) == 0:
            continue

        context_cols = _identify_context_columns(df_filled, target_col)

        # Precompute keyword set for this target column from its existing non-null values
        all_values = df_filled[target_col].dropna().astype(str).unique()
        keywords = set()
        for val in all_values:
            keywords.update(_extract_keywords_from_text(val))

        for row_idx in missing_indices:
            imputed_value = None

            # Strategy 1: Cross-referencing siblings sharing context cols
            if context_cols:
                imputed_value = _find_contextual_sibling_value(
                    df_filled,
                    row_idx,
                    target_col,
                    context_cols,
                )

            # Strategy 2: Feature extraction from descriptive text within same row
            if imputed_value is None and descriptive_cols:
                row = df_filled.iloc[row_idx]
                imputed_value = _extract_value_from_descriptive_column(
                    row,
                    target_col,
                    descriptive_cols,
                    keywords,
                )

            if imputed_value is not None:
                df_filled.at[row_idx, target_col] = imputed_value
                # Only mark as predicted if the cell was originally missing
                if original_missing.at[row_idx, target_col]:
                    imputation_mask.at[row_idx, target_col] = True
                    predicted_mask.at[row_idx, target_col] = True

    # Final Fallback: Only after all intelligent attempts, fill remaining missing
    for target_col in target_columns:
        if target_col not in df_filled.columns:
            continue
        still_missing = df_filled[target_col].isna()
        if not still_missing.any():
            continue

        fallback = "غير محدد"

        for idx in df_filled.index[still_missing]:
            # Only fill if originally missing (do not overwrite any existing non-missing)
            if original_missing.at[idx, target_col]:
                df_filled.at[idx, target_col] = fallback
                imputation_mask.at[idx, target_col] = True

    return df_filled, predicted_mask


# ═══════════════════════════════════════════════════════════════════════════════
# Name detection & normalization helpers (small, focused improvements)
# ═══════════════════════════════════════════════════════════════════════════════
def _arabic_text_cleanup(text: str) -> str:
    if text is None:
        return ""
    try:
        s = str(text)
        # Normalize unicode form and remove tatweel and extra diacritics
        s = unicodedata.normalize('NFKC', s)
        s = re.sub(r'[ـ]+', '', s)
        s = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]', '', s)
        return s.strip()
    except Exception:
        return str(text).strip()


def detect_name_columns(df: pd.DataFrame) -> List[str]:
    """Detect likely name/company columns using header keywords and simple heuristics."""
    keywords = [
        'name', 'full_name', 'fullname', 'customer', 'client', 'company', 'organisation', 'organization',
        'person', 'contact', 'اسم', 'الاسم', 'اسم_الكامل', 'اسم العميل', 'شركة', 'اسم_الشركة', 'زبون'
    ]
    detected = []
    for col in df.columns:
        low = str(col).lower()
        if any(kw in low for kw in keywords):
            detected.append(col)
            continue

        # heuristic: text column with low-to-medium cardinality and contains words
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            non_null = df[col].dropna().astype(str).head(200)
            if len(non_null) == 0:
                continue
            avg_words = sum(len(re.findall(r"\w+", v)) for v in non_null) / len(non_null)
            card_ratio = df[col].nunique(dropna=True) / max(len(df[col]), 1)
            if 1.0 <= avg_words <= 4.0 and card_ratio < 0.6:
                detected.append(col)

    return detected


def clean_name_columns(df: pd.DataFrame, cols: Optional[List[str]] = None, similarity_threshold: float = 0.86) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Clean and harmonize name/company columns.

    - Normalizes whitespace and unicode
    - Removes repeated punctuation
    - Applies simple fuzzy harmonization using the most frequent existing values
    Returns modified df and a small log.
    """
    log = {"columns_cleaned": 0, "values_normalized": 0, "harmonized": 0}
    if cols is None:
        cols = detect_name_columns(df)

    df_copy = df.copy()

    for col in cols:
        if col not in df_copy.columns:
            continue
        series = df_copy[col].astype(object)
        original = series.copy()

        def _norm_name(v):
            if v is None or pd.isna(v):
                return np.nan
            s = str(v).strip()
            if s == "":
                return np.nan
            s = _arabic_text_cleanup(s)
            # collapse multiple spaces and punctuation
            s = re.sub(r'[\s\u00A0]+', ' ', s)
            s = re.sub(r'[\-]{2,}', '-', s)
            s = re.sub(r'[\._]{2,}', '.', s)
            s = re.sub(r'[^\w\s\-\.,ء-يÀ-ÿ]', '', s)
            # Normalize casing: if mostly ascii use title(), else keep as-is but strip
            ascii_ratio = sum(1 for ch in s if ord(ch) < 128) / max(len(s), 1)
            if ascii_ratio > 0.5:
                s = s.title()
            return s.strip()

        series = series.apply(_norm_name)

        # Fuzzy harmonization: build canonical list from most frequent existing names
        candidates = [v for v in series.dropna().astype(str).unique() if v.strip() != ""]
        canonical = []
        canonical_map = {}
        # sort candidates by frequency
        freq = series.value_counts(dropna=True).to_dict()
        candidates.sort(key=lambda x: freq.get(x, 0), reverse=True)

        for c in candidates:
            if c in canonical_map:
                continue
            canonical.append(c)
            canonical_map[c] = c
            # find close matches among remaining candidates
            for other in candidates:
                if other == c or other in canonical_map:
                    continue
                score = difflib.SequenceMatcher(a=c.lower(), b=other.lower()).ratio()
                if score >= similarity_threshold:
                    canonical_map[other] = c

        # apply mapping
        def _map_name(v):
            if v is None or pd.isna(v) or str(v).strip() == "":
                return np.nan
            return canonical_map.get(str(v), v)

        series = series.map(_map_name)

        df_copy[col] = series

        changes = int((original.fillna('') != series.fillna('')).sum())
        log["columns_cleaned"] += 1
        log["values_normalized"] += int(series.notna().sum())
        log["harmonized"] += changes

    return df_copy, log
