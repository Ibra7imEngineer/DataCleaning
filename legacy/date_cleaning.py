"""Professional datetime cleaning utilities for DataX.

This module provides a single SaaS-ready function to clean, normalize,
validate, and report corrupted datetime columns in Pandas DataFrames.
"""

import re
import warnings
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

_THREE_DIGIT_YEAR_PATTERN = re.compile(r"\b(?P<d>\d{1,2})[\/\\-](?P<m>\d{1,2})[\/\\-](?P<y>\d{3})\b")
_EMBEDDED_DATE_PATTERN = re.compile(r"\b\d{1,4}[\/\\-]\d{1,2}[\/\\-]\d{1,4}\b")
_TIME_COMPONENT_PATTERN = re.compile(r"\d{1,2}:\d{2}(?::\d{2})?")


def _normalize_separators(value: str) -> str:
    normalized = value.strip()
    normalized = normalized.replace("\\", "/").replace("-", "/")
    normalized = re.sub(r"[^\w\s:/]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _guess_full_year(three_digit_year: str) -> Optional[int]:
    if not three_digit_year.isdigit() or len(three_digit_year) != 3:
        return None

    current_year = datetime.now().year
    current_century = current_year // 100
    last_two_digits = int(three_digit_year[-2:])
    candidates: List[int] = []

    for century in (current_century - 1, current_century, current_century + 1):
        candidate = century * 100 + last_two_digits
        if 1900 <= candidate <= current_year + 30:
            candidates.append(candidate)

    if not candidates:
        return None

    return min(candidates, key=lambda year: abs(year - current_year))


def _repair_three_digit_years(text: str) -> Tuple[str, bool]:
    fixed = False

    def _replace(match: re.Match) -> str:
        nonlocal fixed
        year_chunk = match.group("y")
        corrected_year = _guess_full_year(year_chunk)
        if corrected_year is None:
            return match.group(0)

        fixed = True
        return f"{match.group('d')}/{match.group('m')}/{corrected_year}"

    repaired_text = _THREE_DIGIT_YEAR_PATTERN.sub(_replace, text)
    return repaired_text, fixed


def _extract_embedded_date(text: str) -> Optional[str]:
    match = _EMBEDDED_DATE_PATTERN.search(text)
    return match.group(0) if match else None


def _parse_candidate(candidate: str) -> Optional[pd.Timestamp]:
    if not candidate or not isinstance(candidate, str):
        return None

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            parsed = pd.to_datetime(candidate, errors="coerce", dayfirst=False)
        if pd.isna(parsed):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                parsed = pd.to_datetime(candidate, errors="coerce", dayfirst=True)
        if pd.isna(parsed):
            return None
        if parsed.year < 1000:
            return None
        return parsed
    except Exception:
        return None


def _clean_date_cell(value: Any) -> Tuple[Optional[pd.Timestamp], str]:
    if value is None:
        return None, ""

    if isinstance(value, (pd.Timestamp, datetime)) and not isinstance(value, str):
        return pd.Timestamp(value).normalize(), ""

    if isinstance(value, date) and not isinstance(value, datetime):
        return pd.Timestamp(value).normalize(), ""

    if isinstance(value, np.datetime64):
        parsed = pd.to_datetime(value, errors="coerce")
        return (pd.Timestamp(parsed).normalize(), "") if not pd.isna(parsed) else (None, "")

    raw_text = str(value).strip()
    if raw_text == "":
        return None, ""

    normalized = _normalize_separators(raw_text)
    repaired, typo_fixed = _repair_three_digit_years(normalized)

    parsed = _parse_candidate(repaired)
    action = ""

    if parsed is None and repaired != normalized:
        parsed = _parse_candidate(normalized)

    if parsed is None:
        extracted = _extract_embedded_date(normalized)
        if extracted:
            parsed = _parse_candidate(extracted)
            if parsed is not None:
                action = "Extracted Embedded Date"

    if parsed is None:
        try:
            from dateutil.parser import parse as fuzzy_parse  # type: ignore

            parsed = fuzzy_parse(raw_text, fuzzy=True, dayfirst=False)
            parsed = pd.Timestamp(parsed)
        except Exception:
            parsed = None

    if parsed is None:
        return None, "Coerced Text to Null"

    if typo_fixed and action == "":
        action = "Corrected Year Typo"

    if action == "" and _TIME_COMPONENT_PATTERN.search(raw_text):
        action = "Stripped Time"

    return parsed.normalize(), action


def clean_datetime_columns(
    df: pd.DataFrame,
    date_columns: List[str],
    chronology_sequence: Optional[List[str]] = None,
    chronology_flag_name: str = "is_chronology_invalid",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Clean and standardize datetime columns with audit-ready anomaly reporting.

    Parameters:
        df: Source DataFrame.
        date_columns: Columns that should be cleaned as dates.
        chronology_sequence: Optional ordered list of date columns to validate.
        chronology_flag_name: Flag column name for invalid chronology.

    Returns:
        cleaned_df: DataFrame with cleaned date columns in YYYY-MM-DD string form.
        anomalies_df: Tracking DataFrame with row index, column, original value, and action.
    """
    cleaned_df = df.copy()
    anomalies: List[Dict[str, Any]] = []

    for col in date_columns:
        if col not in cleaned_df.columns:
            raise ValueError(f"Date column not found in DataFrame: {col}")

        parsed_values: List[Optional[pd.Timestamp]] = []
        column_series = cleaned_df[col]

        for row_index, original_value in column_series.items():
            parsed_value, action = _clean_date_cell(original_value)
            parsed_values.append(parsed_value)
            if action:
                anomalies.append(
                    {
                        "row_index": row_index,
                        "column_name": col,
                        "original_value": original_value,
                        "action_taken": action,
                    }
                )

        parsed_series = pd.to_datetime(pd.Series(parsed_values, index=cleaned_df.index), errors="coerce")
        cleaned_df[col] = parsed_series.dt.strftime("%Y-%m-%d").astype("string")

    if chronology_sequence:
        missing_columns = [col for col in chronology_sequence if col not in cleaned_df.columns]
        if missing_columns:
            raise ValueError(f"Chronology columns not found in DataFrame: {missing_columns}")

        invalid_flags = pd.Series(False, index=cleaned_df.index)
        for previous_col, next_col in zip(chronology_sequence, chronology_sequence[1:]):
            earlier = pd.to_datetime(cleaned_df[previous_col], errors="coerce")
            later = pd.to_datetime(cleaned_df[next_col], errors="coerce")
            invalid_mask = earlier.notna() & later.notna() & (later < earlier)
            invalid_flags |= invalid_mask

            for row_index in invalid_mask[invalid_mask].index:
                anomalies.append(
                    {
                        "row_index": row_index,
                        "column_name": f"{previous_col} -> {next_col}",
                        "original_value": f"{earlier.loc[row_index].strftime('%Y-%m-%d')} > {later.loc[row_index].strftime('%Y-%m-%d')}",
                        "action_taken": "Chronology Invalid",
                    }
                )

        cleaned_df[chronology_flag_name] = invalid_flags

    anomalies_df = pd.DataFrame(
        anomalies,
        columns=["row_index", "column_name", "original_value", "action_taken"],
    )
    return cleaned_df, anomalies_df


__all__ = ["clean_datetime_columns"]
