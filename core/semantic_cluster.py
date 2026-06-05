import re
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from rapidfuzz import fuzz


def normalize_arabic_text(text: str) -> str:
    if not isinstance(text, str):
        return str(text).strip()

    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    return text.strip()


def _clean_value(text: str, normalize_func) -> str:
    value = str(text).strip()
    if normalize_func:
        return normalize_func(value)
    return value


def _build_replacement_map(values: List[str], threshold: int, normalize_func) -> Dict[str, str]:
    normalized = {val: _clean_value(val, normalize_func) for val in values}
    counts = pd.Series(values).value_counts().to_dict()
    mapping: Dict[str, str] = {}
    processed = set()

    for raw_value in values:
        if raw_value in processed:
            continue

        processed.add(raw_value)
        base_normalized = normalized[raw_value]
        if base_normalized == "":
            mapping[raw_value] = raw_value
            continue

        matches = []
        for candidate in values:
            if candidate in processed:
                continue
            candidate_normalized = normalized[candidate]
            if candidate_normalized == "":
                continue
            score = fuzz.WRatio(base_normalized, candidate_normalized)
            if score >= threshold:
                matches.append(candidate)

        cluster = [raw_value] + matches
        canonical = max(cluster, key=lambda x: counts.get(x, 0))
        for member in cluster:
            mapping[member] = canonical
            processed.add(member)

    return mapping


def semantic_clustering_harmonization(
    df: pd.DataFrame,
    fuzzy_threshold: int = 80,
    max_unique_values: int = 500,
    min_unique_values: int = 2,
    normalize_func=None,
) -> Tuple[pd.DataFrame, Dict[str, List[Dict[str, object]]]]:
    if normalize_func is None:
        normalize_func = normalize_arabic_text

    df_cleaned = df.copy()
    logs: Dict[str, List[Dict[str, object]]] = {}
    text_columns = df_cleaned.select_dtypes(include=['object', 'string']).columns.tolist()

    for col in text_columns:
        df_cleaned[col] = df_cleaned[col].astype('string').str.strip()
        unique_values = df_cleaned[col].dropna().unique().tolist()
        normalized_values = [_clean_value(val, normalize_func) for val in unique_values]
        normalized_counts = pd.Series(normalized_values).value_counts()
        unique_count = len(normalized_counts)

        if unique_count < min_unique_values or unique_count > max_unique_values:
            logs[col] = []
            continue

        mapping = _build_replacement_map(unique_values, fuzzy_threshold, normalize_func)
        if mapping:
            df_cleaned[col] = df_cleaned[col].map(lambda x: mapping.get(str(x), x))

        corrections = []
        for raw_value, canonical in mapping.items():
            if raw_value != canonical:
                corrections.append({
                    'old_value': raw_value,
                    'new_value': canonical,
                    'match_method': 'fuzzy_harmonization',
                })

        logs[col] = corrections

    return df_cleaned, logs


def format_logs_for_display(logs: Dict[str, List[Dict[str, object]]]) -> str:
    if not logs:
        return "No corrections made."

    output_lines = []
    for col, corrections in logs.items():
        if not corrections:
            output_lines.append(f"Column '{col}': no corrections.")
            continue
        output_lines.append(f"Column '{col}':")
        for item in corrections:
            output_lines.append(f"  - {item['old_value']} -> {item['new_value']} ({item['match_method']})")

    return "\n".join(output_lines)


__all__ = [
    "normalize_arabic_text",
    "semantic_clustering_harmonization",
    "format_logs_for_display",
]
