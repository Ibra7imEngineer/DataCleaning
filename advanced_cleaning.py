"""
═══════════════════════════════════════════════════════════════════════════════
    ADVANCED DATA CLEANING UTILITIES
    معالجات متقدمة لتنظيف البيانات
═══════════════════════════════════════════════════════════════════════════════
"""

import re
import pandas as pd
import numpy as np
import chardet
from typing import Dict, List, Tuple, Optional, Union
from dateutil import parser as date_parser
from datetime import datetime, timedelta
from collections import Counter

# ─── Fuzzy backends ─────────────────────────────────────────────────────────
try:
    from rapidfuzz import fuzz, process
    _FUZZ_BACKEND = "rapidfuzz"
except ImportError:
    from thefuzz import fuzz, process
    _FUZZ_BACKEND = "thefuzz"


# ═══════════════════════════════════════════════════════════════════════════════
# 1️⃣ PHONE NUMBER STANDARDIZATION | توحيد أرقام التليفونات
# ═══════════════════════════════════════════════════════════════════════════════

# Arabic → Western digits
_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# Country codes supported with expected lengths (including country code)
_COUNTRY_CONFIG = {
    # (dial_code, min_length, max_length)
    "+20":  ("+20", 12, 13),   # Egypt
    "+966": ("+966", 12, 13),  # Saudi Arabia
    "+971": ("+971", 12, 13),  # UAE
    "+965": ("+965", 11, 12),  # Kuwait
    "+974": ("+974", 11, 12),  # Qatar
    "+973": ("+973", 11, 12),  # Bahrain
    "+968": ("+968", 11, 12),  # Oman
    "+962": ("+962", 12, 13),  # Jordan
    "+964": ("+964", 13, 14),  # Iraq
    "+961": ("+961", 10, 11),  # Lebanon
    "+963": ("+963", 12, 13),  # Syria
    "+970": ("+970", 12, 13),  # Palestine
    "+967": ("+967", 12, 13),  # Yemen
    "+249": ("+249", 12, 13),  # Sudan
    "+218": ("+218", 12, 13),  # Libya
    "+216": ("+216", 12, 13),  # Tunisia
    "+213": ("+213", 12, 13),  # Algeria
    "+212": ("+212", 12, 13),  # Morocco
    "+222": ("+222", 12, 13),  # Mauritania
}


def _to_western_digits(text: str) -> str:
    """Convert Arabic digits to Western digits."""
    return text.translate(_ARABIC_DIGITS)


def detect_phone_column(df: pd.DataFrame) -> Optional[str]:
    """
    كشف تلقائي للعمود الذي يحتوي على أرقام التليفونات
    يبحث عن الكلمات المفتاحية: phone, tel, mobile, رقم, تليفون
    """
    keywords = [
        'phone', 'tel', 'mobile', 'رقم', 'تليفون', 'الهاتف',
        'cellular', 'number', 'هاتف', 'جوال', 'نقال',
        'mob', 'cell', 'phone_no', 'phone_num',
    ]
    for col in df.columns:
        col_name_lower = col.lower()
        if any(kw in col_name_lower for kw in keywords):
            return col
    return None


def standardize_phone_number(phone: Union[str, float, int, None],
                             default_country: str = "+20") -> str:
    """
    توحيد رقم التليفون لصيغة موحدة
    - Supports Arabic digits
    - Supports multiple Arab country codes
    - Validates length per country
    """
    if pd.isna(phone):
        return ""

    # Convert to string and translate Arabic digits
    phone = _to_western_digits(str(phone).strip())

    # Remove all non-digit/non-plus characters
    phone = re.sub(r'[^\d+]', '', phone)

    if not phone:
        return ""

    # Handle 00 prefix → +
    if phone.startswith('00'):
        phone = '+' + phone[2:]

    # Handle country codes without +
    if phone.startswith('20') and len(phone) >= 11:
        phone = '+' + phone
    elif phone.startswith('966') and len(phone) >= 12:
        phone = '+' + phone
    elif phone.startswith('971') and len(phone) >= 12:
        phone = '+' + phone
    elif phone.startswith('1') and len(phone) == 11:
        # Egyptian mobile starting with 1
        phone = '+20' + phone[1:]
    elif phone.startswith('5') and len(phone) == 9:
        # Saudi mobile starting with 5
        phone = '+966' + phone
    elif phone.startswith('05') and len(phone) == 10:
        # Saudi mobile with leading 0
        phone = '+966' + phone[1:]
    elif not phone.startswith('+'):
        # Generic fallback
        phone = default_country + phone

    # Validate length
    for code, (prefix, min_len, max_len) in _COUNTRY_CONFIG.items():
        if phone.startswith(code):
            if min_len <= len(phone) <= max_len:
                return phone
            else:
                return ""

    # If no specific country matched but starts with +, validate generic length
    if phone.startswith('+') and 10 <= len(phone) <= 15:
        return phone

    return ""


def clean_phone_column(df: pd.DataFrame,
                       col_name: Optional[str] = None) -> Tuple[pd.DataFrame, Dict]:
    """
    تنظيف عمود التليفونات بالكامل وإرجاع إحصائيات التغييرات
    """
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

    df_copy[col_name] = df_copy[col_name].fillna("").astype(str).apply(
        standardize_phone_number
    )

    log["phones_standardized"] = int((original_values.astype(str) != df_copy[col_name]).sum())
    log["invalid_phones"] = int((df_copy[col_name] == "").sum())

    return df_copy, log


# ═══════════════════════════════════════════════════════════════════════════════
# 2️⃣ CURRENCY & MIXED TEXT/NUMBERS CLEANING
# ═══════════════════════════════════════════════════════════════════════════════

# Arabic numerals & separators
_ARABIC_DECIMAL = "٫"
_ARABIC_THOUSAND = "٬"

_CURRENCY_WORDS = re.compile(
    r'\b(USD|EGP|SAR|AED|KWD|QAR|OMR|BHD|JOD|LBP|IQD|'
    r'MAD|TND|DZD|LYD|SDG|YER|SYP|PLE|MRU|EUR|GBP|CNY|JPY|'
    r'ج\.م|ج\s*\.\s*م|ريال|درهم|دينار|جنيه|ليرة| pound|'
    r'dollar|euro| dirham|riyal)\b',
    flags=re.IGNORECASE
)


def clean_mixed_numeric(value) -> Optional[float]:
    """
    تنظيف الأرقام المخلوطة بنصوص أو عملات
    - Arabic digits → Western
    - Arabic decimal separator (٫) → .
    - Arabic thousands separator (٬) removed
    - Accounting negatives (123) → -123
    - K/M/B suffixes
    - Percentages → decimal
    """
    if pd.isna(value):
        return np.nan

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    val = str(value).strip()
    if not val:
        return np.nan

    # Translate Arabic digits
    val = _to_western_digits(val)

    # Handle Arabic decimal/thousands separators
    val = val.replace(_ARABIC_THOUSAND, '')
    val = val.replace(_ARABIC_DECIMAL, '.')

    # Handle accounting negative: (123) → -123
    is_negative = False
    if val.startswith('(') and val.endswith(')'):
        is_negative = True
        val = val[1:-1]
    elif val.startswith('(-') and val.endswith(')'):
        is_negative = True
        val = val[2:-1]

    # Remove currency words & symbols
    val = _CURRENCY_WORDS.sub('', val)
    val = re.sub(r'[\$€¥£]', '', val)

    # Remove spaces inside numbers
    val = re.sub(r'(?<=\d)\s+(?=\d)', '', val)

    # Remove remaining non-numeric chars except . - % K M B
    val = re.sub(r'[^\d\.\-KMBkmb%]', '', val)

    # Percentage
    pct = False
    if val.endswith('%'):
        pct = True
        val = val[:-1]

    # K/M/B suffixes
    multiplier = 1.0
    if val:
        last_char = val[-1].upper()
        if last_char == 'K':
            multiplier = 1_000
            val = val[:-1]
        elif last_char == 'M':
            multiplier = 1_000_000
            val = val[:-1]
        elif last_char == 'B':
            multiplier = 1_000_000_000
            val = val[:-1]

    try:
        result = float(val) * multiplier
        if pct:
            result = result / 100.0
        if is_negative:
            result = -abs(result)
        return result
    except ValueError:
        return np.nan


def detect_numeric_columns_with_text(df: pd.DataFrame) -> List[str]:
    """
    كشف الأعمدة التي تحتوي على أرقام مخلوطة بنصوص أو رموز عملات
    """
    numeric_cols = []

    for col in df.columns:
        sample = df[col].dropna().astype(str).head(20)
        if len(sample) == 0:
            continue
        has_digits = any(any(c.isdigit() for c in val) for val in sample)
        has_text = any(
            any(c.isalpha() for c in val) for val in sample
        ) or any(
            any(c in "ج.مج٫$€¥ر" for c in val) for val in sample
        )

        if has_digits and has_text:
            numeric_cols.append(col)

    return numeric_cols


def clean_numeric_columns(df: pd.DataFrame,
                          cols: Optional[List[str]] = None) -> Tuple[pd.DataFrame, Dict]:
    """
    تنظيف أعمدة الأرقام المخلوطة بالنصوص
    """
    log = {
        "columns_cleaned": 0,
        "values_converted": 0,
        "invalid_conversions": 0,
    }

    if cols is None:
        cols = detect_numeric_columns_with_text(df)

    df_copy = df.copy()

    for col in cols:
        if col not in df.columns:
            continue

        original_non_null = int(df[col].notna().sum())
        df_copy[col] = df_copy[col].apply(clean_mixed_numeric)

        after_non_null = int(df_copy[col].notna().sum())
        converted = original_non_null - (original_non_null - after_non_null)
        invalid = original_non_null - after_non_null

        log["columns_cleaned"] += 1
        log["values_converted"] += converted
        log["invalid_conversions"] += invalid

    return df_copy, log


# ═══════════════════════════════════════════════════════════════════════════════
# 3️⃣ FUZZY MATCHING — SMART DUPLICATE HANDLING
# ═══════════════════════════════════════════════════════════════════════════════

def _pre_normalize_for_fuzzy(val: str) -> str:
    """Light normalization before fuzzy matching."""
    val = _to_western_digits(val)
    for ch in "\u0640\u200C\u200D\u200E\u200F\uFEFF":
        val = val.replace(ch, "")
    for ch in "أإآٱ":
        val = val.replace(ch, "ا")
    val = val.replace("ة", "ه").replace("ى", "ي")
    return re.sub(r"\s+", " ", val).strip()


def fuzzy_match_series(series: pd.Series,
                       threshold: int = 90,
                       max_unique: int = 1000) -> Dict[str, str]:
    """
    إيجاد القيم المتشابهة جداً وجمعها
    - Performance guard: sample if too many uniques
    - Uses most frequent as canonical
    """
    unique_vals = series.dropna().astype(str).unique()
    if len(unique_vals) == 0:
        return {}

    # Performance guard for very large categorical columns
    if len(unique_vals) > max_unique:
        # Sample most frequent values
        freq = series.value_counts().head(max_unique)
        unique_vals = freq.index.astype(str).tolist()

    # Pre-normalize for comparison
    norm_map = {v: _pre_normalize_for_fuzzy(v) for v in unique_vals}

    # Determine canonical forms (prefer most frequent)
    value_counts = series.value_counts().to_dict()

    mapping = {}
    processed = set()

    for val in unique_vals:
        if val in processed:
            continue

        norm_val = norm_map[val]

        if _FUZZ_BACKEND == "rapidfuzz":
            matches = process.extract(
                norm_val,
                [norm_map[v] for v in unique_vals if v not in processed],
                scorer=fuzz.token_set_ratio,
                limit=None
            )
            # rapidfuzz returns (matched_str, score, idx)
            high_matches = []
            for m in matches:
                if m[1] >= threshold:
                    # Map back to original
                    for orig, n in norm_map.items():
                        if n == m[0] and orig not in processed:
                            high_matches.append(orig)
                            break
        else:
            matches = process.extract(
                norm_val,
                [norm_map[v] for v in unique_vals if v not in processed],
                scorer=fuzz.token_set_ratio,
                limit=None
            )
            high_matches = []
            for m in matches:
                if m[1] >= threshold:
                    for orig, n in norm_map.items():
                        if n == m[0] and orig not in processed:
                            high_matches.append(orig)
                            break

        if len(high_matches) > 1:
            # Prefer most frequent as canonical
            canonical = max(
                high_matches,
                key=lambda x: value_counts.get(x, 0)
            )
            for match in high_matches:
                mapping[match] = canonical
                processed.add(match)
        else:
            mapping[val] = val
            processed.add(val)

    return mapping


def apply_fuzzy_matching(df: pd.DataFrame,
                         cols: Optional[List[str]] = None,
                         threshold: int = 90) -> Tuple[pd.DataFrame, Dict]:
    """
    تطبيق الدمج الذكي للمتشابهات على أعمدة نصية
    """
    log = {
        "columns_processed": 0,
        "duplicates_merged": 0,
        "total_changes": 0,
    }

    if cols is None:
        cols = df.select_dtypes(include=['object']).columns.tolist()

    df_copy = df.copy()

    for col in cols:
        if col not in df.columns:
            continue

        # Skip phone columns (handled separately)
        col_lower = col.lower()
        if any(k in col_lower for k in ['phone', 'tel', 'mobile', 'رقم', 'هاتف', 'جوال']):
            continue

        mapping = fuzzy_match_series(df_copy[col], threshold)
        if mapping:
            original = df_copy[col].copy()
            df_copy[col] = df_copy[col].map(lambda x: mapping.get(x, x))
            merged = len([m for m in mapping.items() if m[0] != m[1]])
            log["columns_processed"] += 1
            log["duplicates_merged"] += merged
            log["total_changes"] += int((original != df_copy[col]).sum())

    return df_copy, log


def apply_fuzzy_matching_phones(series: pd.Series,
                                threshold: int = 95) -> Dict[str, str]:
    """
    Fuzzy merge for already-normalized phone numbers.
    Very high threshold since phones should be exact or near-exact.
    """
    unique_vals = series.dropna().astype(str).unique()
    unique_vals = [v for v in unique_vals if v.startswith('+')]

    if len(unique_vals) <= 1:
        return {}

    mapping = {}
    processed = set()

    for val in unique_vals:
        if val in processed:
            continue

        matches = process.extract(
            val,
            [v for v in unique_vals if v not in processed],
            scorer=fuzz.ratio,
            limit=None
        )

        high_matches = [val]
        for m in matches:
            if m[1] >= threshold:
                # Map back
                matched_val = m[0]
                high_matches.append(matched_val)

        high_matches = list(set(high_matches))
        if len(high_matches) > 1:
            # Prefer shortest as canonical for phones
            canonical = min(high_matches, key=len)
            for match in high_matches:
                mapping[match] = canonical
                processed.add(match)
        else:
            mapping[val] = val
            processed.add(val)

    return mapping


# ═══════════════════════════════════════════════════════════════════════════════
# 4️⃣ DATE VALIDATION & LOGICAL BOUNDS | التحقق من صحة التواريخ
# ═══════════════════════════════════════════════════════════════════════════════

# Arabic month mapping
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
    "ديسمبر": 12, "كانون الأول": 12, "كانون الاول": 12, "كانون الثاني": 1,
}

# English month mapping for quick validation
_EN_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

# Days per month (non-leap year)
_DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

_EXCEL_EPOCH = datetime(1899, 12, 30)


def _is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def _replace_arabic_months(date_str: str) -> str:
    """Replace Arabic month names with numeric equivalents."""
    date_str = date_str.strip()
    for ar_month, num in _ARABIC_MONTHS.items():
        if ar_month in date_str:
            date_str = date_str.replace(ar_month, str(num))
    return date_str


def _parse_arabic_date(date_str: str) -> Optional[datetime]:
    """Try parsing dates with Arabic month names."""
    date_str = _replace_arabic_months(date_str)
    # After replacement, try standard parsing
    try:
        return date_parser.parse(date_str, dayfirst=True)
    except Exception:
        try:
            return date_parser.parse(date_str, dayfirst=False)
        except Exception:
            return None


def _excel_serial_to_date(serial) -> Optional[datetime]:
    """Convert Excel serial number to datetime."""
    try:
        n = int(float(str(serial).strip()))
        if 1 <= n <= 2958465:
            return _EXCEL_EPOCH + timedelta(days=n)
    except Exception:
        pass
    return None


def _is_valid_calendar_date(year: int, month: int, day: int) -> bool:
    """Check if Y-M-D is a valid calendar date (respects month lengths & leap years)."""
    if month < 1 or month > 12 or day < 1:
        return False
    max_day = _DAYS_IN_MONTH[month]
    if month == 2 and _is_leap_year(year):
        max_day = 29
    return day <= max_day


def validate_date_bounds(date_val: Union[datetime, str, int, float, None],
                         min_year: int = 1900,
                         max_future_years: int = 1) -> Optional[datetime]:
    """
    التحقق من أن التاريخ منطقي:
    - Not before min_year
    - Not too far in the future (default: today + max_future_years)
    - Valid calendar date (no Feb 30)
    """
    if date_val is None or pd.isna(date_val):
        return None

    parsed = None

    if isinstance(date_val, datetime):
        parsed = date_val
    elif isinstance(date_val, (int, float, np.integer, np.floating)):
        if not np.isnan(date_val):
            parsed = _excel_serial_to_date(date_val)
    elif isinstance(date_val, str):
        s = date_val.strip()
        if not s:
            return None
        # Try Arabic months first
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

    # Validate calendar bounds
    if not _is_valid_calendar_date(parsed.year, parsed.month, parsed.day):
        return None

    now = datetime.now()
    max_future = now + timedelta(days=365 * max_future_years)

    if parsed.year < min_year or parsed > max_future:
        return None

    return parsed


def smart_parse_date(date_str: str) -> Optional[datetime]:
    """
    محاولة تحويل أي صيغة تاريخ إلى datetime
    - Arabic months supported
    - Excel serials supported
    """
    if not isinstance(date_str, str) or not date_str.strip():
        return None

    # Try Arabic months
    parsed = _parse_arabic_date(date_str)
    if parsed:
        return parsed

    # Try Excel serial
    try:
        n = int(float(date_str.strip()))
        if 1 <= n <= 2958465:
            return _excel_serial_to_date(n)
    except Exception:
        pass

    # Try dateutil
    try:
        return date_parser.parse(date_str, dayfirst=True)
    except Exception:
        try:
            return date_parser.parse(date_str, dayfirst=False)
        except Exception:
            return None


def _detect_date_column(series: pd.Series) -> bool:
    """Heuristic detection of date columns."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return True

    date_kws = [
        "date", "تاريخ", "يوم", "day", "time", "وقت",
        "created", "updated", "birth", "ميلاد",
        "انشاء", "اضافة", "تعديل", "انتهاء",
        "بداية", "نهاية", "timestamp", "recorded",
        "created_at", "updated_at", "birth_date",
        "registration", "تسجيل", "order_date", "تاريخ_الطلب",
    ]
    col_lower = str(series.name).lower()
    if any(k in col_lower for k in date_kws):
        return True

    if series.dtype == object:
        non_null = series.dropna().astype(str)
        non_null = non_null[non_null.str.strip() != ""]
        if len(non_null) == 0:
            return False
        sample = non_null.head(30)
        hits = 0
        for v in sample:
            if smart_parse_date(v) is not None:
                hits += 1
        if hits / len(sample) >= 0.4:
            return True

    return False


def clean_dates_advanced(df: pd.DataFrame,
                         cols: Optional[List[str]] = None,
                         min_year: int = 1900,
                         max_future_years: int = 1) -> Tuple[pd.DataFrame, Dict]:
    """
    تنظيف أعمدة التواريخ بمعالجة متقدمة
    - Arabic month names
    - Excel serial numbers
    - Invalid calendar date rejection
    - Future date guard
    """
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
        if col not in df.columns:
            continue

        try:
            original = df_copy[col].copy()
            new_vals = []
            changes = 0

            for val in original:
                validated = validate_date_bounds(
                    val, min_year=min_year, max_future_years=max_future_years
                )
                if validated is not None:
                    new_vals.append(validated.strftime("%Y-%m-%d"))
                else:
                    new_vals.append(np.nan)

            df_copy[col] = new_vals

            # Count changes
            for old, new in zip(original, new_vals):
                old_str = str(old).strip() if pd.notna(old) else ""
                new_str = str(new).strip() if pd.notna(new) else ""
                if old_str != new_str and old_str != "" and old_str.lower() != "nan":
                    changes += 1

            if changes > 0:
                log["columns_processed"] += 1
                log["dates_fixed"] += changes

        except Exception:
            continue

    return df_copy, log


# ═══════════════════════════════════════════════════════════════════════════════
# 5️⃣ ENCODING DETECTION & FALLBACK | معالجة الترميز
# ═══════════════════════════════════════════════════════════════════════════════

def detect_file_encoding(file_path: str) -> str:
    """كشف الترميز الفعلي للملف"""
    try:
        with open(file_path, 'rb') as f:
            raw = f.read()
            result = chardet.detect(raw)
            return result['encoding'] or 'utf-8'
    except Exception:
        return 'utf-8'


def read_csv_with_encoding_fallback(file_path: str) -> pd.DataFrame:
    """
    قراءة ملف CSV مع محاولات متعددة للترميز
    الترتيب: utf-8 → cp1256 (Windows Arabic) → iso-8859-6 → latin-1
    """
    encodings = ['utf-8', 'utf-8-sig', 'cp1256', 'windows-1256', 'iso-8859-6', 'latin-1']

    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except Exception:
            continue

    # Last resort
    try:
        return pd.read_csv(file_path, encoding='utf-8', errors='replace')
    except Exception:
        raise ValueError(
            "❌ فشل في قراءة الملف بأي ترميز | Failed to read file with any encoding"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 6️⃣ MEMORY OPTIMIZATION | تحسين استهلاك الذاكرة
# ═══════════════════════════════════════════════════════════════════════════════

def _safe_float_downcast(series: pd.Series) -> pd.Series:
    """
    Safely downcast float64 to float32, checking for precision loss.
    """
    if series.dtype != np.float64:
        return series

    # Check for NaN/Inf
    finite_vals = series.dropna()
    if len(finite_vals) == 0:
        return series.astype(np.float32)

    # Check range: float32 max ~ 3.4e38, min positive ~ 1.4e-45
    if finite_vals.abs().max() > 3.4e38:
        return series

    # Check precision: if values have many significant digits, keep float64
    # float32 has ~7 decimal digits of precision
    max_val = finite_vals.abs().max()
    if max_val > 0:
        significant_digits = np.log10(max_val) + 1
        if significant_digits > 7:
            # Check if rounding would lose meaningful data
            as_f32 = series.astype(np.float32)
            diff = (series - as_f32).abs()
            max_diff = diff.max()
            # Allow tiny relative differences
            if max_diff > 1e-5 * max_val:
                return series

    return series.astype(np.float32)


def _safe_int_downcast(series: pd.Series) -> pd.Series:
    """
    Safely downcast int64 to nullable Int32/Int16, preserving NaN.
    """
    if not pd.api.types.is_integer_dtype(series):
        return series

    # If series has nulls, use nullable integer dtype
    has_nulls = series.isnull().any()

    min_v, max_v = series.min(), series.max()

    if min_v >= 0:
        if max_v < 256:
            return series.astype("Int8" if has_nulls else np.int8)
        elif max_v < 65536:
            return series.astype("Int16" if has_nulls else np.int16)
        elif max_v < 2147483648:
            return series.astype("Int32" if has_nulls else np.int32)
    else:
        if min_v > -128 and max_v < 128:
            return series.astype("Int8" if has_nulls else np.int8)
        elif min_v > -32768 and max_v < 32768:
            return series.astype("Int16" if has_nulls else np.int16)
        elif min_v > -2147483648 and max_v < 2147483648:
            return series.astype("Int32" if has_nulls else np.int32)

    return series


def optimize_memory(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    تحسين استهلاك الذاكرة:
    - float64 → float32 (with precision guard)
    - int64 → nullable Int32/Int16/Int8 (preserving NaN)
    - object/text with low cardinality → Category
    """
    log = {
        "original_memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        "optimized_memory_mb": 0,
        "reduction_percent": 0,
        "float_downcast": 0,
        "int_downcast": 0,
        "categorical_converted": 0,
    }

    df_opt = df.copy()

    # Float downcast
    float_cols = df_opt.select_dtypes(include=['float64']).columns
    for col in float_cols:
        df_opt[col] = _safe_float_downcast(df_opt[col])
        if df_opt[col].dtype == np.float32:
            log["float_downcast"] += 1

    # Integer downcast
    int_cols = df_opt.select_dtypes(include=['int64']).columns
    for col in int_cols:
        new_series = _safe_int_downcast(df_opt[col])
        if new_series.dtype != np.int64:
            df_opt[col] = new_series
            log["int_downcast"] += 1

    # Object → Category
    object_cols = df_opt.select_dtypes(include=['object']).columns
    n_rows = len(df_opt)
    for col in object_cols:
        n_unique = df_opt[col].nunique()
        # Only convert if meaningful savings possible
        if n_unique < 50000 and (n_unique / max(n_rows, 1)) < 0.5:
            df_opt[col] = df_opt[col].astype('category')
            log["categorical_converted"] += 1

    log["optimized_memory_mb"] = round(
        df_opt.memory_usage(deep=True).sum() / 1024 / 1024, 2
    )
    orig = log["original_memory_mb"]
    opt = log["optimized_memory_mb"]
    log["reduction_percent"] = round((orig - opt) / max(orig, 0.001) * 100, 2)

    return df_opt, log


# ═══════════════════════════════════════════════════════════════════════════════
# 7️⃣ AUDIT TRAIL / CHANGE LOG | سجل التغييرات
# ═══════════════════════════════════════════════════════════════════════════════

class AuditTrail:
    """تتبع كل التغييرات التي تحدث على البيانات"""

    def __init__(self):
        self.changes = []

    def log_change(self, row_idx: int, col_name: str, old_value, new_value, reason: str):
        """تسجيل تغيير واحد"""
        self.changes.append({
            "صف | Row": row_idx,
            "عمود | Column": col_name,
            "القيمة القديمة | Old": str(old_value)[:50],
            "القيمة الجديدة | New": str(new_value)[:50],
            "السبب | Reason": reason,
        })

    def log_bulk_change(self, count: int, reason: str):
        """تسجيل عملية جماعية"""
        self.changes.append({
            "صف | Row": "N/A",
            "عمود | Column": "N/A",
            "القيمة القديمة | Old": "N/A",
            "القيمة الجديدة | New": "N/A",
            "السبب | Reason": f"{reason} ({count} قيم | values)",
        })

    def to_dataframe(self) -> pd.DataFrame:
        """تحويل السجل إلى DataFrame"""
        if not self.changes:
            return pd.DataFrame()
        return pd.DataFrame(self.changes)

    def to_excel(self, file_path: str):
        """حفظ السجل في ملف Excel"""
        self.to_dataframe().to_excel(file_path, index=False, engine='openpyxl')


# ═══════════════════════════════════════════════════════════════════════════════
# 8️⃣ COMPREHENSIVE CLEANING PIPELINE | خط الأنابيب الشامل
# ═══════════════════════════════════════════════════════════════════════════════

class AdvancedCleaner:
    """محرك التنظيف المتقدم يجمع كل الميزات"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df_original = df.copy()
        self.audit = AuditTrail()
        self.log = {}

    def run_full_pipeline(self,
                          clean_phones: bool = True,
                          clean_numeric: bool = True,
                          fuzzy_match: bool = True,
                          fix_dates: bool = True,
                          optimize_mem: bool = True) -> pd.DataFrame:
        """تشغيل خط الأنابيب الكامل"""
        df = self.df.copy()

        if clean_phones:
            df, log = clean_phone_column(df)
            self.log["phones"] = log
            self.audit.log_bulk_change(
                log.get("phones_standardized", 0), "Phone standardization"
            )

        if clean_numeric:
            df, log = clean_numeric_columns(df)
            self.log["numeric"] = log
            self.audit.log_bulk_change(
                log.get("values_converted", 0), "Numeric cleaning"
            )

        if fuzzy_match:
            df, log = apply_fuzzy_matching(df)
            self.log["fuzzy"] = log
            self.audit.log_bulk_change(
                log.get("total_changes", 0), "Fuzzy matching"
            )

        if fix_dates:
            df, log = clean_dates_advanced(df)
            self.log["dates"] = log
            self.audit.log_bulk_change(
                log.get("dates_fixed", 0), "Date fixing"
            )

        if optimize_mem:
            df, log = optimize_memory(df)
            self.log["memory"] = log

        self.df = df
        return df

    def get_audit_trail(self) -> pd.DataFrame:
        """الحصول على سجل التغييرات"""
        return self.audit.to_dataframe()

    def get_summary(self) -> Dict:
        """ملخص العمليات المنفذة"""
        return {
            "total_rows": len(self.df),
            "total_cols": len(self.df.columns),
            "memory_optimization": self.log.get("memory", {}),
            "operations": {k: v for k, v in self.log.items() if k != "memory"}
        }

