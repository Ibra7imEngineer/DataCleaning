import re
import warnings
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from dateutil import parser as date_parser


_THREE_DIGIT_YEAR_PATTERN = re.compile(r"\b(?P<d>\d{1,2})[\/\\-](?P<m>\d{1,2})[\/\\-](?P<y>\d{3})\b")
_EMBEDDED_DATE_PATTERN = re.compile(r"\b\d{1,4}[\/\\-]\d{1,2}[\/\\-]\d{1,4}\b")
_TIME_COMPONENT_PATTERN = re.compile(r"\d{1,2}:\d{2}(?::\d{2})?")

_ARABIC_MONTHS = {
    "يناير": 1, "كانون الثاني": 1, "كانون الاول": 1,
    "فبراير": 2, "شباط": 2,
    "مارس": 3, "آذار": 3,
    "أبريل": 4, "ابريل": 4, "نيسان": 4,
    "مايو": 5, "أيار": 5, "ايار": 5,
    "يونيو": 6, "يونية": 6, "حزيران": 6,
    "يوليو": 7, "يولية": 7, "تموز": 7,
    "أغسطس": 8, "اغسطس": 8, "آب": 8,
    "سبتمبر": 9, "أيلول": 9, "ايلول": 9,
    "أكتوبر": 10, "اكتوبر": 10, "تشرين الأول": 10, "تشرين الاول": 10,
    "نوفمبر": 11, "تشرين الثاني": 11,
    "ديسمبر": 12, "كانون الأول": 12, "كانون الاول": 12,
}

_EN_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

_DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
_EXCEL_EPOCH = datetime(1899, 12, 30)


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
    candidates = [
        (current_century - 1) * 100 + last_two_digits,
        current_century * 100 + last_two_digits,
        (current_century + 1) * 100 + last_two_digits,
    ]
    candidates = [year for year in candidates if 1900 <= year <= current_year + 30]
    return min(candidates, key=lambda year: abs(year - current_year)) if candidates else None


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
            parsed = pd.to_datetime(candidate, errors="coerce")
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

    if parsed is None and repaired != normalized:
        parsed = _parse_candidate(normalized)

    if parsed is None:
        extracted = _extract_embedded_date(normalized)
        if extracted:
            parsed = _parse_candidate(extracted)
            if parsed is not None:
                return parsed.normalize(), "Extracted Embedded Date"

    if parsed is None:
        try:
            from dateutil.parser import parse as fuzzy_parse
            parsed = fuzzy_parse(raw_text, fuzzy=True, dayfirst=False)
            parsed = pd.Timestamp(parsed)
        except Exception:
            parsed = None

    if parsed is None:
        return None, "Coerced Text to Null"

    action = ""
    if typo_fixed:
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
    cleaned_df = df.copy()
    anomalies: List[Dict[str, Any]] = []

    for col in date_columns:
        if col not in cleaned_df.columns:
            raise ValueError(f"Date column not found in DataFrame: {col}")

        parsed_values: List[Optional[pd.Timestamp]] = []
        for row_index, original_value in cleaned_df[col].items():
            parsed_value, action = _clean_date_cell(original_value)
            parsed_values.append(parsed_value)
            if action:
                anomalies.append({
                    "row_index": row_index,
                    "column_name": col,
                    "original_value": original_value,
                    "action_taken": action,
                })

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
                anomalies.append({
                    "row_index": row_index,
                    "column_name": f"{previous_col} -> {next_col}",
                    "original_value": f"{earlier.loc[row_index].strftime('%Y-%m-%d')} > {later.loc[row_index].strftime('%Y-%m-%d')}",
                    "action_taken": "Chronology Invalid",
                })
        cleaned_df[chronology_flag_name] = invalid_flags

    anomalies_df = pd.DataFrame(anomalies, columns=["row_index", "column_name", "original_value", "action_taken"])
    return cleaned_df, anomalies_df


def _replace_arabic_months(date_str: str) -> str:
    normalized = date_str.strip()
    for ar_month, num in _ARABIC_MONTHS.items():
        normalized = normalized.replace(ar_month, str(num))
    return normalized


def _parse_arabic_date(date_str: str) -> Optional[datetime]:
    normalized = _replace_arabic_months(date_str)
    try:
        return date_parser.parse(normalized, dayfirst=True)
    except Exception:
        try:
            return date_parser.parse(normalized, dayfirst=False)
        except Exception:
            return None


def _excel_serial_to_date(serial: Any) -> Optional[datetime]:
    try:
        n = int(float(str(serial).strip()))
        if 1 <= n <= 2958465:
            return _EXCEL_EPOCH + timedelta(days=n)
    except Exception:
        pass
    return None


def _is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def _is_valid_calendar_date(year: int, month: int, day: int) -> bool:
    if month < 1 or month > 12 or day < 1:
        return False
    max_day = _DAYS_IN_MONTH[month]
    if month == 2 and _is_leap_year(year):
        max_day = 29
    return day <= max_day


def validate_date_bounds(date_val: Union[datetime, str, int, float, None], min_year: int = 1900, max_future_years: int = 1) -> Optional[datetime]:
    if date_val is None or pd.isna(date_val):
        return None

    parsed: Optional[datetime] = None
    if isinstance(date_val, datetime):
        parsed = date_val
    elif isinstance(date_val, (int, float, np.integer, np.floating)):
        if not np.isnan(date_val):
            parsed = _excel_serial_to_date(date_val)
    elif isinstance(date_val, str):
        s = date_val.strip()
        if not s:
            return None
        parsed = _parse_arabic_date(s)
        if parsed is None:
            try:
                parsed = date_parser.parse(s, dayfirst=True)
            except Exception:
                try:
                    parsed = date_parser.parse(s, dayfirst=False)
                except Exception:
                    return None

    if parsed is None:
        return None

    if not _is_valid_calendar_date(parsed.year, parsed.month, parsed.day):
        return None

    now = datetime.now()
    max_future = now + timedelta(days=365 * max_future_years)
    if parsed.year < min_year or parsed > max_future:
        return None

    return parsed


def clean_dates_advanced(df: pd.DataFrame, cols: Optional[List[str]] = None, min_year: int = 1900, max_future_years: int = 1) -> Tuple[pd.DataFrame, Dict[str, int]]:
    log = {
        "columns_processed": 0,
        "dates_fixed": 0,
        "invalid_dates": 0,
        "future_dates_caught": 0,
        "ancient_dates_caught": 0,
    }

    if cols is None:
        cols = [c for c in df.columns if _detect_date_column(df[c])]

    df_copy = df.copy()
    for col in cols:
        if col not in df_copy.columns:
            continue

        original = df_copy[col].copy()
        new_vals = []
        changes = 0
        for val in original:
            validated = validate_date_bounds(val, min_year=min_year, max_future_years=max_future_years)
            if validated is not None:
                new_vals.append(validated.strftime("%Y-%m-%d"))
            else:
                new_vals.append(np.nan)

        df_copy[col] = new_vals
        for old, new in zip(original, new_vals):
            old_str = str(old).strip() if pd.notna(old) else ""
            new_str = str(new).strip() if pd.notna(new) else ""
            if old_str != new_str and old_str != "" and old_str.lower() != "nan":
                changes += 1

        if changes > 0:
            log["columns_processed"] += 1
            log["dates_fixed"] += changes

    return df_copy, log


def _detect_date_column(series: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True

    col_lower = str(series.name).lower()
    date_kws = [
        "date", "تاريخ", "يوم", "day", "time", "وقت",
        "created", "updated", "birth", "ميلاد", "انشاء", "اضافة",
        "تعديل", "انتهاء", "بداية", "نهاية", "timestamp", "recorded",
        "created_at", "updated_at", "birth_date", "registration", "تسجيل", "order_date", "تاريخ_الطلب",
    ]
    identifier_kws = [
        "id", "order id", "orderid", "order_no", "order no", "order number",
        "رقم", "رقم الطلب", "رقم الطلبية", "كود", "sku", "barcode", "token", "code",
        "uid", "user id",
    ]

    if any(k in col_lower for k in date_kws):
        return True
    if any(k in col_lower for k in identifier_kws):
        return False

    if series.dtype == object:
        non_null = series.dropna().astype(str)
        non_null = non_null[non_null.str.strip() != ""]
        if len(non_null) == 0:
            return False
        sample = non_null.head(30)
        hits = 0
        for v in sample:
            if _parse_candidate(str(v)) is not None:
                hits += 1
        return hits / len(sample) >= 0.4

    return False

__all__ = [
    "clean_datetime_columns",
    "clean_dates_advanced",
    "validate_date_bounds",
]
