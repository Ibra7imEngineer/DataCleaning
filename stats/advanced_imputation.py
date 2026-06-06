import re
from typing import Any, List, Optional, Tuple

import numpy as np
import pandas as pd

DEFAULT_MISSING_TERMS = {
    "", "na", "n/a", "n\a", "nan", "none", "null", "unknown",
    "missing", "not available", "not applicable", "غير محدد", "غير متوفر",
    "ناقص", "بدون", "لا يوجد", "ليس متاح",
}

DATE_CANDIDATE_REGEX = re.compile(
    r'^(?:\d{4}[-/\. ]\d{1,2}[-/\. ]\d{1,2}|\d{1,2}[-/\. ]\d{1,2}[-/\. ]\d{2,4}|'
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}|\d{1,2}:\d{2}(?::\d{2})?)$'
)


def _is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except Exception:
        pass
    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized in DEFAULT_MISSING_TERMS
    return False


def _sanitize_arabic_text(value: str) -> str:
    value = value.strip()
    for ch in "ـ‌‍‎‏﻿":
        value = value.replace(ch, "")
    value = re.sub(r"[ً-ْٰٴ]", "", value)
    for ch in "أإآٱ":
        value = value.replace(ch, "ا")
    value = value.replace("ة", "ه").replace("ى", "ي")
    value = value.replace("ؤ", "و").replace("ئ", "ي")
    return re.sub(r"\s+", " ", value).strip()


def _sanitize_english_text(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[\W_]+", " ", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def _normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        return str(value) if value is not None else ""
    value = value.strip()
    if not value:
        return ""
    if any('؀' <= ch <= 'ۿ' for ch in value):
        return _sanitize_arabic_text(value)
    return _sanitize_english_text(value)


def normalize_text_series(series: pd.Series) -> pd.Series:
    if series.dtype == object or pd.api.types.is_string_dtype(series):
        return series.astype(str).replace({r'^[\s\uFEFF\u200B]+|[\s\uFEFF\u200B]+$': ''}, regex=True).apply(
            lambda v: _normalize_text(v) if not _is_missing_value(v) else np.nan
        )
    return series


def detect_column_role(series: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    values = series.dropna().astype(str).str.strip()
    values = values[~values.str.lower().isin(DEFAULT_MISSING_TERMS)]
    if values.empty:
        return "text"

    sampled = values.sample(min(60, len(values)), random_state=42)
    parsed = pd.to_datetime(sampled, dayfirst=True, errors="coerce")
    if parsed.notna().mean() >= 0.65:
        return "datetime"

    numeric_mask = sampled.str.fullmatch(r"[-+]?\d*\.?\d+")
    if numeric_mask.mean() >= 0.85:
        return "numeric"

    unique_count = values.str.lower().nunique()
    ratio = unique_count / max(len(values), 1)
    top_pct = values.str.lower().value_counts(normalize=True).iloc[0]

    if ratio <= 0.2 or top_pct >= 0.2:
        return "categorical"
    if ratio >= 0.85 and len(values) >= 8:
        return "identifier"
    return "text"


def infer_context_guides(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    candidates = []
    for col in df.columns:
        role = detect_column_role(df[col])
        if role in {"categorical", "text", "identifier"}:
            non_null = df[col].dropna().astype(str).str.strip()
            if non_null.empty:
                continue
            unique = non_null.str.lower().nunique()
            top_pct = non_null.str.lower().value_counts(normalize=True).iloc[0]
            ratio = unique / max(len(non_null), 1)
            candidates.append((col, role, unique, ratio, top_pct, len(non_null)))

    if not candidates:
        return None, None

    candidates.sort(key=lambda item: (
        item[1] == "categorical",
        item[4],
        -item[3],
        item[5],
    ), reverse=True)

    fine = None
    coarse = None
    for col, role, unique, ratio, top_pct, count in candidates:
        if fine is None and role == "categorical" and unique > 1:
            fine = col
        elif coarse is None and unique > 1:
            coarse = col
        if fine and coarse and fine != coarse:
            break

    if fine is None and len(candidates) >= 1:
        fine = candidates[0][0]
    if coarse is None and len(candidates) >= 2:
        coarse = candidates[1][0]
    if coarse is None and fine is not None:
        coarse = fine

    return fine, coarse


def _best_grouping_column(df: pd.DataFrame, numeric_col: str, categorical_cols: List[str]) -> Optional[str]:
    best_col = None
    best_score = 0.0
    numeric_values = pd.to_numeric(df[numeric_col], errors="coerce")
    base_var = numeric_values.var(skipna=True)
    if base_var == 0 or np.isnan(base_var):
        return None

    for col in categorical_cols:
        if col == numeric_col or col not in df.columns:
            continue
        groups = df[[numeric_col, col]].dropna()
        if len(groups) < 4 or groups[col].nunique() < 2:
            continue
        medians = groups.groupby(col)[numeric_col].transform("median")
        between_var = medians.var(skipna=True)
        score = float((between_var / base_var) * min(1.0, len(groups) / max(len(df), 1)))
        if score > best_score:
            best_score = score
            best_col = col

    return best_col if best_score >= 0.02 else None


def _fill_numeric_grouped(
    df: pd.DataFrame,
    numeric_cols: List[str],
    categorical_cols: List[str],
    fallback_groups: Optional[List[str]] = None,
) -> pd.DataFrame:
    df = df.copy()
    for col in numeric_cols:
        status_col = f"{col}_imputation_status"
        df[status_col] = pd.Series([pd.NA] * len(df), index=df.index, dtype="string")

        numeric_series = pd.to_numeric(df[col], errors="coerce")
        missing_mask = numeric_series.isna()
        if not missing_mask.any():
            df.loc[~missing_mask, status_col] = "Original Value"
            continue

        best_group = _best_grouping_column(df, col, categorical_cols)
        if best_group:
            group_median = numeric_series.groupby(df[best_group]).transform("median")
            fill_mask = missing_mask & group_median.notna()
            df.loc[fill_mask, col] = group_median.loc[fill_mask]
            df.loc[fill_mask, status_col] = f"Filled by Grouped Median ({best_group})"
            missing_mask = pd.to_numeric(df[col], errors="coerce").isna()

        if missing_mask.any() and fallback_groups:
            for group_col in fallback_groups:
                if group_col == best_group or group_col not in df.columns:
                    continue
                group_median = numeric_series.groupby(df[group_col]).transform("median")
                fill_mask = missing_mask & group_median.notna()
                df.loc[fill_mask, col] = group_median.loc[fill_mask]
                df.loc[fill_mask, status_col] = f"Filled by Grouped Median ({group_col})"
                missing_mask = pd.to_numeric(df[col], errors="coerce").isna()
                if not missing_mask.any():
                    break

        df.loc[~pd.to_numeric(df[col], errors="coerce").isna(), status_col] = df.loc[~pd.to_numeric(df[col], errors="coerce").isna(), status_col].fillna("Original Value")
    return df


def _fill_categorical_by_context(
    df: pd.DataFrame,
    categorical_cols: List[str],
    anchor_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    df = df.copy()
    for target in categorical_cols:
        status_col = f"{target}_imputation_status"
        df[status_col] = pd.Series([pd.NA] * len(df), index=df.index, dtype="string")

        if target not in df.columns:
            continue

        target_series = df[target].astype("string")
        missing_mask = target_series.isna()
        if not missing_mask.any():
            df.loc[~missing_mask, status_col] = "Original Value"
            continue

        anchors = [c for c in (anchor_cols or df.select_dtypes(include=["object", "string"]).columns.tolist()) if c != target and c in df.columns]
        if not anchors:
            df.loc[~missing_mask, status_col] = "Original Value"
            continue

        context = df[anchors].fillna("<MISSING>").astype(str).agg("||".join, axis=1)
        group_mode = df.groupby(context)[target].transform(
            lambda x: x.mode().iloc[0] if not x.mode().empty else pd.NA
        )
        fill_mask = missing_mask & group_mode.notna()
        df.loc[fill_mask, target] = group_mode.loc[fill_mask]
        df.loc[fill_mask, status_col] = "Filled by Item Context"
        missing_mask = df[target].isna()

        if missing_mask.any():
            for anchor in anchors:
                group_mode = df.groupby(anchor)[target].transform(
                    lambda x: x.mode().iloc[0] if not x.mode().empty else pd.NA
                )
                fill_mask = missing_mask & group_mode.notna()
                df.loc[fill_mask, target] = group_mode.loc[fill_mask]
                df.loc[fill_mask, status_col] = "Filled by Anchor Context"
                missing_mask = df[target].isna()
                if not missing_mask.any():
                    break

        df.loc[~df[target].isna(), status_col] = df.loc[~df[target].isna(), status_col].fillna("Original Value")
    return df


def detect_multiplicative_relations(
    df: pd.DataFrame,
    tolerance: float = 0.04,
    min_support: int = 5,
) -> List[Tuple[str, str, str]]:
    numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns if df[col].notna().sum() >= min_support]
    relations: List[Tuple[str, str, str]] = []

    for i, a in enumerate(numeric_cols):
        for j, b in enumerate(numeric_cols):
            if i == j:
                continue
            for k, c in enumerate(numeric_cols):
                if k in {i, j}:
                    continue
                sample = df[[a, b, c]].copy()
                sample = sample.dropna()
                if len(sample) < min_support:
                    continue
                expected = sample[a].astype(float) * sample[b].astype(float)
                denom = sample[c].astype(float).abs().replace(0, np.nan)
                ratio = expected.div(denom)
                if ratio.notna().sum() < min_support:
                    continue
                match_ratio = (ratio.between(1 - tolerance, 1 + tolerance)).mean()
                if match_ratio >= 0.85:
                    relations.append((a, b, c))
    return relations


def correct_multiplicative_relationships(
    df: pd.DataFrame,
    relations: List[Tuple[str, str, str]],
    tolerance: float = 0.03,
) -> Tuple[pd.DataFrame, int]:
    df = df.copy()
    changes = 0
    for a, b, c in relations:
        if not all(col in df.columns for col in (a, b, c)):
            continue
        a_vals = pd.to_numeric(df[a], errors="coerce")
        b_vals = pd.to_numeric(df[b], errors="coerce")
        expected = a_vals * b_vals

        missing_mask = df[c].isna() & a_vals.notna() & b_vals.notna()
        if missing_mask.any():
            df.loc[missing_mask, c] = expected.loc[missing_mask]
            df.loc[missing_mask, f"{c}_calculation_status"] = f"Recalculated by {a}*{b}"
            changes += int(missing_mask.sum())

        present_mask = df[c].notna() & a_vals.notna() & b_vals.notna()
        if present_mask.any():
            current = pd.to_numeric(df.loc[present_mask, c], errors="coerce")
            diff = (current - expected.loc[present_mask]).abs()
            is_outlier = diff.gt(np.maximum(expected.loc[present_mask].abs() * tolerance, 1e-9))
            if is_outlier.any():
                df.loc[present_mask & is_outlier, c] = expected.loc[present_mask & is_outlier]
                df.loc[present_mask & is_outlier, f"{c}_calculation_status"] = f"Corrected by {a}*{b}"
                changes += int(is_outlier.sum())
    return df, changes


def flag_grouped_outliers(
    df: pd.DataFrame,
    numeric_cols: Optional[List[str]] = None,
    group_cols: Optional[List[str]] = None,
    min_group_size: int = 4,
) -> Tuple[pd.DataFrame, int, List[Tuple[Any, str]]]:
    df = df.copy()
    coords: List[Tuple[Any, str]] = []
    mask = pd.Series(False, index=df.index)

    if numeric_cols is None:
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns]

    group_cols = [col for col in (group_cols or []) if col in df.columns]

    for col in numeric_cols:
        if col not in df.columns:
            continue
        numeric_values = pd.to_numeric(df[col], errors="coerce")
        if numeric_values.notna().sum() < min_group_size:
            continue

        if group_cols:
            for group_col in group_cols:
                group = df[group_col].astype(str).fillna("<MISSING>")
                q1 = numeric_values.groupby(group).transform("quantile", q=0.25)
                q3 = numeric_values.groupby(group).transform("quantile", q=0.75)
                iqr = q3 - q1
                group_mask = (
                    numeric_values.notna()
                    & (iqr > 0)
                    & ((numeric_values < q1 - 1.5 * iqr) | (numeric_values > q3 + 1.5 * iqr))
                )
                if group_mask.any():
                    mask |= group_mask
                    coords.extend((idx, col) for idx in df.index[group_mask])
        else:
            q1 = numeric_values.quantile(0.25)
            q3 = numeric_values.quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                global_mask = numeric_values.notna() & ((numeric_values < q1 - 1.5 * iqr) | (numeric_values > q3 + 1.5 * iqr))
                mask |= global_mask
                coords.extend((idx, col) for idx in df.index[global_mask])

    df["__outlier__"] = mask
    return df, int(mask.sum()), coords


def streamlit_imputation_style(df: pd.DataFrame, status_cols: List[str]) -> Any:
    def _highlight(row: pd.Series) -> List[str]:
        for status_col in status_cols:
            if status_col in row and row[status_col] not in {"Original Value", pd.NA, None, ""}:
                return ["background-color: rgba(252, 211, 77, 0.25);" for _ in row]
        return ["" for _ in row]

    return df.style.apply(_highlight, axis=1)


def universal_missing_value_imputation(
    df: pd.DataFrame,
    numeric_cols_to_fill: List[str],
    categorical_cols_to_fill: List[str],
    fine_grain_guide: Optional[str],
    coarse_grain_guide: Optional[str],
) -> pd.DataFrame:
    df_work = df.copy(deep=True)
    text_cols = [col for col in df_work.columns if df_work[col].dtype == object or pd.api.types.is_string_dtype(df_work[col])]
    for col in text_cols:
        df_work[col] = normalize_text_series(df_work[col])

    numeric_targets = [c for c in numeric_cols_to_fill if c in df_work.columns]
    categorical_targets = [c for c in categorical_cols_to_fill if c in df_work.columns]
    auto_fine, auto_coarse = infer_context_guides(df_work)
    fine = fine_grain_guide if fine_grain_guide in df_work.columns else auto_fine
    coarse = coarse_grain_guide if coarse_grain_guide in df_work.columns else auto_coarse

    if fine is None and coarse is None:
        return df_work

    if categorical_targets:
        anchor_cols = [col for col in df_work.columns if col not in categorical_targets + [fine, coarse] and (df_work[col].dtype == object or pd.api.types.is_string_dtype(df_work[col]))]
        df_work = _fill_categorical_by_context(df_work, categorical_targets, anchor_cols=anchor_cols)

    if numeric_targets:
        group_cols = [col for col in [fine, coarse] if col in df_work.columns]
        df_work = _fill_numeric_grouped(df_work, numeric_targets, group_cols, fallback_groups=group_cols)

    relations = detect_multiplicative_relations(df_work)
    if relations:
        df_work, _ = correct_multiplicative_relationships(df_work, relations)

    return df_work


__all__ = [
    "detect_column_role",
    "infer_context_guides",
    "detect_multiplicative_relations",
    "correct_multiplicative_relationships",
    "flag_grouped_outliers",
    "universal_missing_value_imputation",
    "streamlit_imputation_style",
]
