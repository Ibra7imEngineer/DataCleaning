"""Text normalization utilities for Arabic and English aimed at robust
data-cleaning in pandas workflows.

Functions accept either a Python string or a pandas.Series and return the
normalized value of the same type. Vectorized pandas operations are used
where possible for performance; non-string values are left untouched.

Usage examples:
    from text_normalization import clean_text
    df['name_clean'] = clean_text(df['name'], lang='auto')

"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional, Union

import pandas as pd

# Precompiled regexes (targeting common Arabic diacritics and control chars)
ARABIC_DIACRITICS_RE = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]')
TATWEEL_RE = re.compile(r'\u0640')
ZERO_WIDTH_RE = re.compile(r'[\u200c\u200d\u200e\u200f\uFEFF]')
NON_PRINTING_RE = re.compile(r'[\x00-\x1f\x7f]')
MULTI_SPACES_RE = re.compile(r'\s+')
ARABIC_DETECT_RE = re.compile(r'[\u0600-\u06FF]')

# Basic English contraction expansions (small and non-exhaustive)
CONTRACTION_MAP = {
    "can't": "cannot",
    "won't": "will not",
    "n't": " not",
    "'re": " are",
    "'s": " is",
    "'d": " would",
    "'ll": " will",
    "'ve": " have",
    "'m": " am",
    "w/": " with ",
    "w/o": " without ",
}


def _is_arabic_text(s: str) -> bool:
    return bool(ARABIC_DETECT_RE.search(s))


def _strip_non_printing(s: str) -> str:
    s = NON_PRINTING_RE.sub('', s)
    s = ZERO_WIDTH_RE.sub('', s)
    return s


def _normalize_whitespace(s: str) -> str:
    return MULTI_SPACES_RE.sub(' ', s).strip()


def _normalize_unicode(s: str) -> str:
    s = unicodedata.normalize('NFKC', s)
    s = _strip_non_printing(s)
    return s


def normalize_arabic_string(s: str, teh_marbuta_to: str = 'ه') -> str:
    """Normalize an Arabic string according to specifications.

    - removes Arabic diacritics and tatweel
    - normalizes alef variants (أ إ آ -> ا)
    - standardizes ligatures (لآ, لأ, لإ -> لا)
    - converts ؤ -> و, ئ -> ي, ى -> ي
    - standardizes ة to chosen `teh_marbuta_to` (default 'ه')
    - strips zero-width and control characters; collapses whitespace
    """
    if not s:
        return s
    s = _normalize_unicode(s)

    # remove tashkeel / diacritics
    s = ARABIC_DIACRITICS_RE.sub('', s)

    # remove tatweel (kashida)
    s = TATWEEL_RE.sub('', s)

    # Alef variants -> bare alef
    s = re.sub(r'[إأآ]', 'ا', s)

    # ligatures: لآ, لأ, لإ -> لا
    s = re.sub(r'ل[آأإ]', 'لا', s)

    # waw with hamza ؤ -> و
    s = s.replace('ؤ', 'و')

    # yeh with hamza ئ -> ي
    s = s.replace('ئ', 'ي')

    # alef maksura ى -> ي
    s = s.replace('ى', 'ي')

    # standardize teh marbuta
    if teh_marbuta_to not in ('ه', 'ة'):
        raise ValueError("teh_marbuta_to must be 'ه' or 'ة'")
    s = s.replace('ة', teh_marbuta_to)

    # clean control / zero-width again and normalize whitespace
    s = _strip_non_printing(s)
    s = _normalize_whitespace(s)
    return s


def normalize_english_string(s: str, case: Optional[str] = 'lower', expand_contractions: bool = False,
                             remove_non_ascii: bool = True) -> str:
    """Normalize English (Latin) string.

    - optional contraction expansion (small set)
    - optional removal of non-ASCII via NFKD->ASCII
    - case normalization: 'lower', 'title', or None
    - unicode normalization and whitespace collapse
    """
    if not s:
        return s
    s = _normalize_unicode(s)

    if expand_contractions:
        for k, v in CONTRACTION_MAP.items():
            s = re.sub(re.escape(k), v, s, flags=re.IGNORECASE)

    if remove_non_ascii:
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')

    if case == 'lower':
        s = s.lower()
    elif case == 'title':
        s = s.title()

    s = _normalize_whitespace(s)
    return s


def _vectorized_arabic(series: pd.Series, teh_marbuta_to: str = 'ه') -> pd.Series:
    # apply NFKC normalization elementwise then use vectorized regex ops
    s = series.map(lambda x: unicodedata.normalize('NFKC', x))
    s = s.str.replace(ARABIC_DIACRITICS_RE, '', regex=True)
    s = s.str.replace(TATWEEL_RE, '', regex=True)
    s = s.str.replace(r'[إأآ]', 'ا', regex=True)
    s = s.str.replace(r'ل[آأإ]', 'لا', regex=True)
    s = s.str.replace('ؤ', 'و', regex=False)
    s = s.str.replace('ئ', 'ي', regex=False)
    s = s.str.replace('ى', 'ي', regex=False)
    if teh_marbuta_to == 'ه':
        s = s.str.replace('ة', 'ه', regex=False)
    else:
        s = s.str.replace('ة', 'ة', regex=False)
    s = s.str.replace(ZERO_WIDTH_RE, '', regex=True)
    s = s.str.replace(NON_PRINTING_RE, '', regex=True)
    s = s.str.replace(MULTI_SPACES_RE, ' ', regex=True).str.strip()
    return s


def _vectorized_english(series: pd.Series, case: Optional[str] = 'lower', expand_contractions: bool = False,
                        remove_non_ascii: bool = True) -> pd.Series:
    s = series.map(lambda x: unicodedata.normalize('NFKC', x))
    s = pd.Series(s, index=series.index)
    if expand_contractions:
        for k, v in CONTRACTION_MAP.items():
            s = s.str.replace(re.escape(k), v, case=False, regex=True)
    if remove_non_ascii:
        s = s.map(lambda x: unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode('ascii'))
        s = pd.Series(s, index=series.index)
    if case == 'lower':
        s = s.str.lower()
    elif case == 'title':
        s = s.str.title()
    s = s.str.replace(MULTI_SPACES_RE, ' ', regex=True).str.strip()
    return s


def clean_text(obj: Union[str, pd.Series], *, lang: str = 'auto',
               english_case: Optional[str] = 'lower', expand_contractions: bool = False,
               remove_non_ascii_english: bool = True, teh_marbuta_to: str = 'ه') -> Union[str, pd.Series]:
    """Main entrypoint for cleaning text.

    Parameters:
    - obj: input string or pandas.Series
    - lang: 'ar', 'en', or 'auto' (per-value detection)
    - english_case: 'lower', 'title', or None
    - expand_contractions: apply small contraction expansions for English
    - remove_non_ascii_english: strip non-ASCII chars for English normalization
    - teh_marbuta_to: 'ه' or 'ة' (how to normalize Teh Marbuta)

    Returns the cleaned value(s) with the same type as the input.
    """
    if lang not in ('ar', 'en', 'auto'):
        raise ValueError("lang must be 'ar', 'en', or 'auto'")

    if isinstance(obj, str):
        if lang == 'ar' or (lang == 'auto' and _is_arabic_text(obj)):
            return normalize_arabic_string(obj, teh_marbuta_to=teh_marbuta_to)
        return normalize_english_string(obj, case=english_case, expand_contractions=expand_contractions,
                                        remove_non_ascii=remove_non_ascii_english)

    if isinstance(obj, pd.Series):
        series = obj.copy()
        # operate only on string elements
        str_mask = series.map(lambda x: isinstance(x, str))
        if not str_mask.any():
            return series

        strings = series[str_mask].astype(str)

        if lang == 'ar':
            series.loc[str_mask] = _vectorized_arabic(strings, teh_marbuta_to=teh_marbuta_to)
        elif lang == 'en':
            series.loc[str_mask] = _vectorized_english(strings, case=english_case,
                                                     expand_contractions=expand_contractions,
                                                     remove_non_ascii=remove_non_ascii_english)
        else:  # auto: detect per-value
            arabic_mask = strings.str.contains(r'[\u0600-\u06FF]', na=False)
            if arabic_mask.any():
                series.loc[str_mask & arabic_mask] = _vectorized_arabic(strings[arabic_mask],
                                                                        teh_marbuta_to=teh_marbuta_to)
            if (~arabic_mask).any():
                series.loc[str_mask & ~arabic_mask] = _vectorized_english(strings[~arabic_mask],
                                                                          case=english_case,
                                                                          expand_contractions=expand_contractions,
                                                                          remove_non_ascii=remove_non_ascii_english)
        return series

    return obj


if __name__ == '__main__':
    import pandas as _pd
    sample = _pd.Series(['  هبة', 'Ibrahim Mohamed', None, 123, 'لإسلام', 'ؤرد', "don't ", 'résumé'])
    print('Original:')
    print(sample)
    print('\nCleaned (auto):')
    print(clean_text(sample, lang='auto', expand_contractions=True))
