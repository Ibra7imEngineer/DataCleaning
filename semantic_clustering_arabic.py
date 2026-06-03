"""
Independent Semantic Clustering and Harmonization Engine
Author: Data Engineering Team
Purpose: Performs fuzzy-matching based clustering on DataFrame columns,
         with special support for Arabic text normalization.
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from rapidfuzz import process, fuzz
from rapidfuzz.distance import Levenshtein


# ============================================================================
# 1. ARABIC NORMALIZATION HELPER FUNCTION
# ============================================================================

def normalize_arabic_text(text: str) -> str:
    """
    Normalize common Arabic characters and diacritics for consistent clustering.
    
    Transformations:
    - أ, إ, آ → ا (all hamza variants to alef)
    - ة → ه (taa marbuta to haa)
    - ى → ي (alef maksura to yaa)
    - Removes all diacritics (sukun, fatha, damma, kasra, etc.)
    - Strips leading/trailing whitespace
    
    Args:
        text (str): Input text to normalize
        
    Returns:
        str: Normalized text
        
    Example:
        >>> normalize_arabic_text("ترابيزة")
        "تربيزه"
    """
    if not isinstance(text, str):
        return str(text).strip()
    
    # Normalize hamza variants to alef
    text = re.sub(r'[أإآ]', 'ا', text)
    
    # Normalize taa marbuta to haa (end of word)
    text = re.sub(r'ة', 'ه', text)
    
    # Normalize alef maksura to yaa
    text = re.sub(r'ى', 'ي', text)
    
    # Remove Arabic diacritics (harakat)
    # This includes: fatha, damma, kasra, sukun, shadda, tanwin, etc.
    diacritics_pattern = r'[\u064B-\u065F]'  # Arabic diacritics Unicode range
    text = re.sub(diacritics_pattern, '', text)
    
    # Strip whitespace
    text = text.strip()
    
    return text


# ============================================================================
# 2. SEMANTIC CLUSTERING AND HARMONIZATION FUNCTION
# ============================================================================

def semantic_clustering_harmonization(
    df: pd.DataFrame,
    fuzzy_threshold: int = 80,
    max_unique_values: int = 500,
    min_unique_values: int = 2,
    normalize_func=None
) -> Tuple[pd.DataFrame, Dict]:
    """
    Perform independent semantic clustering and harmonization on DataFrame columns
    using fuzzy matching with Arabic normalization. Master words are selected by
    normalized frequency count before applying fuzzy matching.
    
    Args:
        df (pd.DataFrame): Input DataFrame to clean
        fuzzy_threshold (int): Fuzzy matching threshold (0-100). Default: 80
        max_unique_values (int): Max unique values to process (protection for IDs). Default: 500
        min_unique_values (int): Min unique values to process. Default: 2
        normalize_func (callable): Optional normalization function applied before matching.
                                  Default: normalize_arabic_text
    
    Returns:
        Tuple[pd.DataFrame, Dict]:
            - df_cleaned (pd.DataFrame): DataFrame with harmonized values
            - logs (Dict): Mapping of column -> list of correction records
    """
    
    if normalize_func is None:
        normalize_func = normalize_arabic_text
    
    df_cleaned = df.copy()
    logs = {}
    
    text_columns = df_cleaned.select_dtypes(include=['object', 'string']).columns.tolist()
    
    if not text_columns:
        print("⚠️  No text columns found in DataFrame.")
        return df_cleaned, logs
    
    print(f"📊 Found {len(text_columns)} text columns to process.")
    
    for col in text_columns:
        col_logs = []
        
        # Forced pre-cleaning: strip hidden whitespace and normalize text before frequency analysis
        df_cleaned[col] = df_cleaned[col].astype('string').str.strip()
        
        # Build normalized values and frequency counts prior to matching
        unique_values = df_cleaned[col].dropna().unique().tolist()
        normalized_map = {
            raw_value: normalize_func(raw_value)
            for raw_value in unique_values
        }
        normalized_series = df_cleaned[col].map(normalized_map)
        normalized_counts = normalized_series.value_counts()
        unique_count = len(normalized_counts)
        
        if unique_count > max_unique_values:
            print(f"⏭️  Skipping '{col}': {unique_count} unique normalized values (> {max_unique_values})")
            logs[col] = col_logs
            continue
        
        if unique_count < min_unique_values:
            print(f"⏭️  Skipping '{col}': {unique_count} unique normalized values (< {min_unique_values})")
            logs[col] = col_logs
            continue
        
        print(f"\n🔄 Processing column '{col}' ({unique_count} normalized unique values)")
        
        replacement_map = {}
        processed_normalized = set()
        raw_value_counts = df_cleaned[col].value_counts()
        
        for normalized_master in normalized_counts.index:
            if normalized_master in processed_normalized:
                continue
            
            # All raw values that normalize to this master normalized string
            exact_group = [raw for raw, norm in normalized_map.items() if norm == normalized_master]
            if not exact_group:
                continue

            processed_normalized.add(normalized_master)
            matched_variations = []
            audit_items = []

            # Choose the master word by raw frequency within the normalized cluster.
            master_word = max(exact_group, key=lambda x: raw_value_counts.get(x, 0))

            # Prepare remaining normalized candidates for fuzzy comparison
            remaining_normalized = [
                norm for norm in normalized_counts.index
                if norm not in processed_normalized
            ]

            if remaining_normalized:
                for candidate_norm in remaining_normalized:
                    match_method = None
                    match_score = None
                    is_match = False

                    if len(normalized_master) < 4 or len(candidate_norm) < 4:
                        match_method = 'levenshtein'
                        match_score = Levenshtein.distance(normalized_master, candidate_norm)
                        if match_score <= 1:
                            is_match = True
                    else:
                        match_method = 'WRatio'
                        match_score = fuzz.WRatio(normalized_master, candidate_norm)
                        if match_score >= fuzzy_threshold:
                            is_match = True

                    if not is_match or candidate_norm in processed_normalized:
                        continue

                    processed_normalized.add(candidate_norm)
                    group_variations = [
                        raw for raw, norm in normalized_map.items()
                        if norm == candidate_norm
                    ]

                    for raw_value in group_variations:
                        if raw_value == master_word:
                            continue
                        replacement_map[raw_value] = master_word
                        if raw_value not in matched_variations:
                            matched_variations.append(raw_value)
                        audit_items.append({
                            'old_value': raw_value,
                            'new_value': master_word,
                            'match_method': match_method,
                            'score': int(match_score) if isinstance(match_score, (int, float)) else None
                        })

            # Map exact normalized variants to the chosen master word as well
            for raw_value in exact_group:
                if raw_value != master_word:
                    replacement_map[raw_value] = master_word
                    if raw_value not in matched_variations:
                        matched_variations.append(raw_value)
                    audit_items.append({
                        'old_value': raw_value,
                        'new_value': master_word,
                        'match_method': 'normalized_exact',
                        'score': None
                    })

            if matched_variations:
                col_logs.append({
                    'master_word': master_word,
                    'master_normalized': normalized_master,
                    'matched_variations': matched_variations,
                    'audit_items': audit_items,
                    'normalized_count': int(normalized_counts[normalized_master]),
                    'num_corrections': len(matched_variations)
                })
                print(f"  ✓ Master: '{master_word}' ({normalized_master}) <- {matched_variations}")
        
        if replacement_map:
            df_cleaned[col] = df_cleaned[col].map(
                lambda x: replacement_map.get(x, x)
            )
            print(f"  ✅ Applied {len(replacement_map)} replacements to '{col}'")
        else:
            print(f"  ℹ️  No fuzzy matches found for '{col}'")
        
        logs[col] = col_logs
    
    return df_cleaned, logs


# ============================================================================
# 3. LOGGING AND DISPLAY HELPERS
# ============================================================================

def format_logs_for_display(logs: Dict) -> str:
    """
    Format logs into a readable string for display/export.
    
    Args:
        logs (Dict): Logs dictionary from semantic_clustering_harmonization
        
    Returns:
        str: Formatted log string
    """
    if not logs:
        return "No corrections made."
    
    output_lines = []
    total_corrections = 0
    
    for col, corrections in logs.items():
        if not corrections:
            output_lines.append(f"\n📌 Column '{col}': No corrections needed")
            continue
        
        output_lines.append(f"\n📌 Column '{col}': {len(corrections)} correction groups")
        for idx, record in enumerate(corrections, 1):
            master = record['master_word']
            matched = record['matched_variations']
            count = record['num_corrections']
            total_corrections += count
            output_lines.append(f"   {idx}. Master: '{master}' ← Unified {count} variation(s): {matched}")
            for item in record.get('audit_items', []):
                old_value = item.get('old_value')
                new_value = item.get('new_value')
                output_lines.append(f"      - [Old Value] {old_value} -> [New Value] {new_value}")
    
    output_lines.append(f"\n\n📊 Total Variations Harmonized: {total_corrections}")
    return "\n".join(output_lines)


def get_correction_summary(logs: Dict) -> Dict:
    """
    Generate summary statistics for corrections.
    
    Args:
        logs (Dict): Logs dictionary from semantic_clustering_harmonization
        
    Returns:
        Dict: Summary statistics
    """
    summary = {
        'total_columns_processed': len([c for c in logs.values() if c]),
        'total_correction_groups': sum(len(c) for c in logs.values()),
        'total_variations_harmonized': sum(
            record['num_corrections'] 
            for c in logs.values() 
            for record in c
        ),
        'columns_breakdown': {}
    }
    
    for col, corrections in logs.items():
        if corrections:
            summary['columns_breakdown'][col] = {
                'correction_groups': len(corrections),
                'total_variations': sum(r['num_corrections'] for r in corrections)
            }
    
    return summary


# ============================================================================
# 4. EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example DataFrame with Arabic text variations
    example_df = pd.DataFrame({
        'Item': [
            'ترابيزة',      # Table (variation 1)
            'ترابيزه',      # Table (variation 2)
            'ترابيزه',      # Table (variation 2 - duplicate)
            'كنبة',         # Couch (variation 1)
            'كنبه',         # Couch (variation 2)
            'كنبة',         # Couch (variation 1 - duplicate)
            'كرسي',         # Chair
            'كرسي',         # Chair (duplicate)
        ],
        'Category': [
            'Furniture',
            'Furniture',
            'Furniture',
            'Furniture',
            'Furniture',
            'Furniture',
            'Furniture',
            'Furniture',
        ]
    })
    
    print("📋 Original DataFrame:")
    print(example_df)
    print(f"\nUnique Items Before: {example_df['Item'].unique()}")
    
    # Run clustering
    df_clean, logs = semantic_clustering_harmonization(example_df)
    
    print("\n" + "="*70)
    print("📋 Cleaned DataFrame:")
    print(df_clean)
    print(f"\nUnique Items After: {df_clean['Item'].unique()}")
    
    print("\n" + "="*70)
    print("📊 CORRECTION LOGS:")
    print(format_logs_for_display(logs))
    
    print("\n" + "="*70)
    print("📈 SUMMARY STATISTICS:")
    summary = get_correction_summary(logs)
    for key, value in summary.items():
        print(f"{key}: {value}")
