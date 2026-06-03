"""
═══════════════════════════════════════════════════════════════════════════════
    STREAMLIT OPTIMIZATION MODULE
    للتعامل مع البيانات الضخمة (مليون+ صفوف / 10 مليون+ خلية)
═══════════════════════════════════════════════════════════════════════════════
Best Practices for Large Dataset Handling
- Lazy loading: Preview only, full processing in background
- Memory efficiency: Optimize dtypes, reduce RAM usage
- Caching: Cache expensive computations  
- Limited UI rendering: Prevent Pandas Styler from rendering entire dataset
"""

import pandas as pd
import numpy as np
import streamlit as st
from functools import lru_cache, wraps
import time
from typing import Tuple, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# 1. MEMORY OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════════

def optimize_dtypes(df: pd.DataFrame, verbose: bool = False) -> Tuple[pd.DataFrame, dict]:
    """
    Optimize DataFrame dtypes to reduce memory usage
    - object (strings) → category (if < 50% unique values)
    - float64 → float32 (for non-critical precision)
    - int64 → int32 (if values fit)
    - bool → stay as bool
    
    Returns:
        df (optimized), memory_savings (dict with before/after stats)
    """
    df = df.copy()
    initial_memory = df.memory_usage(deep=True).sum() / 1024**2  # MB
    savings = {}

    for col in df.columns:
        col_type = df[col].dtype

        # Optimize object columns → category
        if col_type == "object" and col != "__outlier__":
            try:
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.5:  # Less than 50% unique
                    df[col] = df[col].astype("category")
                    savings[col] = f"object → category"
            except Exception:
                pass

        # Optimize float64 → float32
        elif col_type == "float64":
            try:
                # Check if precision loss is acceptable
                min_val, max_val = df[col].min(), df[col].max()
                if pd.notna(min_val) and pd.notna(max_val):
                    # Only downcast if not scientific data
                    if abs(min_val) < 1e6 and abs(max_val) < 1e6:
                        df[col] = df[col].astype("float32")
                        savings[col] = f"float64 → float32"
            except Exception:
                pass

        # Optimize int64 → int32
        elif col_type == "int64":
            try:
                if df[col].min() >= -2**31 and df[col].max() <= 2**31 - 1:
                    df[col] = df[col].astype("int32")
                    savings[col] = f"int64 → int32"
            except Exception:
                pass

    final_memory = df.memory_usage(deep=True).sum() / 1024**2  # MB
    memory_reduction = initial_memory - final_memory
    reduction_pct = (memory_reduction / initial_memory * 100) if initial_memory > 0 else 0

    memory_stats = {
        "before_mb": round(initial_memory, 2),
        "after_mb": round(final_memory, 2),
        "saved_mb": round(memory_reduction, 2),
        "reduction_pct": round(reduction_pct, 1),
        "optimizations": savings,
    }

    if verbose:
        print(f"✓ Memory Optimization Summary:")
        print(f"  Before: {memory_stats['before_mb']} MB")
        print(f"  After:  {memory_stats['after_mb']} MB")
        print(f"  Saved:  {memory_stats['saved_mb']} MB ({memory_stats['reduction_pct']}%)")

    return df, memory_stats


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SMART CACHING FOR HEAVY COMPUTATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def cache_compute(func):
    """
    Decorator for Streamlit cache_data with clear hash generation
    Use for expensive DataFrame operations
    
    Example:
        @cache_compute
        def build_profile(df):
            return {...}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable version of the dataframe
        def _make_hashable(obj):
            if isinstance(obj, pd.DataFrame):
                return hash(pd.util.hash_pandas_object(obj, index=True).values.tobytes())
            elif isinstance(obj, (list, tuple)):
                return tuple(_make_hashable(item) for item in obj)
            elif isinstance(obj, dict):
                return tuple(sorted((k, _make_hashable(v)) for k, v in obj.items()))
            return hash(obj)

        cache_key = (func.__name__, _make_hashable(args), _make_hashable(kwargs))
        return st.cache_data(func, ttl=3600)(*args, **kwargs)

    return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# 3. LAZY LOADING & PREVIEW-ONLY RENDERING
# ═══════════════════════════════════════════════════════════════════════════════

def create_lazy_preview(df: pd.DataFrame, preview_rows: int = 100) -> Tuple[pd.DataFrame, dict]:
    """
    Create a preview DataFrame for UI rendering WITHOUT limiting full processing
    
    Key Point: 
    - Returns preview_df (head) for displaying in st.dataframe()
    - Original df remains unchanged for background processing
    - All operations still apply to FULL dataset
    
    Args:
        df: Full DataFrame (can have 1M+ rows)
        preview_rows: Number of rows to show in UI (default 100)
    
    Returns:
        preview_df, metadata (rows_total, cells_total, cells_preview)
    """
    preview_df = df.head(preview_rows).copy()
    
    metadata = {
        "total_rows": len(df),
        "total_cols": len(df.columns),
        "total_cells": len(df) * len(df.columns),
        "preview_rows": preview_rows,
        "preview_cols": len(preview_df.columns),
        "preview_cells": len(preview_df) * len(preview_df.columns),
        "data_hidden": len(df) - preview_rows,
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
    }
    
    return preview_df, metadata


def create_safe_styler(df: pd.DataFrame, 
                       style_func=None,
                       preview_rows: int = 100) -> 'pd.io.formats.style.Styler':
    """
    Create a Pandas Styler ONLY on preview data to avoid rendering limits
    
    CRITICAL: This applies styling to preview only, not to full dataset
    Use this for ALL st.dataframe(style_...) calls with large data
    
    Args:
        df: Full DataFrame
        style_func: Function that takes preview_df and returns styled df
        preview_rows: Preview size
    
    Returns:
        styled preview DataFrame (safe to render)
    """
    preview_df = df.head(preview_rows).copy()
    
    if style_func is None:
        # Default: just apply basic styling
        return preview_df.style
    
    # Apply custom styling to PREVIEW ONLY
    return style_func(preview_df)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. IMPROVED DATA LOADING WITH CHUNKING (for CSV)
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def read_large_csv(file_path: str, 
                   chunk_size: int = 50000,
                   encoding: str = "utf-8") -> pd.DataFrame:
    """
    Read large CSV files efficiently using chunking
    
    Args:
        file_path: Path to CSV file
        chunk_size: Rows per chunk (default 50k)
        encoding: File encoding
    
    Returns:
        Combined DataFrame
    """
    chunks = []
    try:
        for chunk in pd.read_csv(file_path, 
                                  chunksize=chunk_size,
                                  encoding=encoding,
                                  dtype_backend='numpy_nullable'):  # Faster parsing
            chunks.append(chunk)
        
        df = pd.concat(chunks, ignore_index=True)
        return df
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# 5. SESSION STATE MANAGEMENT FOR LARGE DATA
# ═══════════════════════════════════════════════════════════════════════════════

def init_session_state_optimized():
    """Initialize session state with memory-efficient patterns"""
    defaults = {
        "df": None,                    # Full dataset
        "df_preview": None,            # Preview only (for display)
        "df_original": None,           # Original unmodified
        "file_name": None,
        "file_size": 0,
        "step": 1,
        "profile": None,               # CACHED profile
        "quality_before": 0,
        "quality_after": 0,
        "detected_langs": {},
        "advanced_options": {},
        "memory_stats": {},            # Track memory optimization
        "processing_log": [],          # Track operations on full data
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ═══════════════════════════════════════════════════════════════════════════════
# 6. DISPLAY HELPERS WITH MEMORY WARNINGS
# ═══════════════════════════════════════════════════════════════════════════════

def display_data_summary(df: pd.DataFrame, title: str = "Data Summary"):
    """Show safe summary metrics without rendering full data"""
    
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("📊 Rows", f"{len(df):,}")
    
    with cols[1]:
        st.metric("📋 Columns", f"{len(df.columns):,}")
    
    with cols[2]:
        cells = len(df) * len(df.columns)
        st.metric("🔢 Cells", f"{cells:,}")
    
    with cols[3]:
        memory_mb = df.memory_usage(deep=True).sum() / 1024**2
        st.metric("💾 Memory", f"{memory_mb:.1f} MB")


def safe_dataframe_display(df: pd.DataFrame, 
                          styled: bool = True,
                          style_func=None,
                          preview_rows: int = 100,
                          height: int = 420,
                          show_preview_notice: bool = True):
    """
    SAFE way to display large DataFrames in Streamlit
    
    ALWAYS use this instead of st.dataframe() directly for large data
    
    Args:
        df: DataFrame (can be 1M+ rows)
        styled: Whether to apply styling
        style_func: Custom style function
        preview_rows: How many rows to show
        height: Height of dataframe widget
        show_preview_notice: Show "Preview of X rows" notice
    """
    
    if show_preview_notice and len(df) > preview_rows:
        st.info(
            f"👀 **Preview Mode**: Showing first {preview_rows:,} of {len(df):,} rows  \n"
            f"💾 All {len(df):,} rows processed in background  \n"
            f"📥 Download below to export complete cleaned data"
        )
    
    if styled and style_func:
        styled_df = create_safe_styler(df, style_func, preview_rows)
        st.dataframe(styled_df, use_container_width=True, height=height)
    else:
        preview = df.head(preview_rows)
        st.dataframe(preview, use_container_width=True, height=height)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. PERFORMANCE MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

class PerformanceMonitor:
    """Track computation times and memory usage"""
    
    def __init__(self):
        self.operations = []
    
    def __call__(self, func_name: str, df: pd.DataFrame = None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = None
                
                if df is not None:
                    import psutil
                    import os
                    process = psutil.Process(os.getpid())
                    start_memory = process.memory_info().rss / 1024**2  # MB
                
                result = func(*args, **kwargs)
                
                end_time = time.time()
                duration = end_time - start_time
                
                end_memory = None
                if df is not None:
                    end_memory = process.memory_info().rss / 1024**2
                    memory_delta = end_memory - start_memory
                else:
                    memory_delta = None
                
                self.operations.append({
                    "function": func_name,
                    "duration_sec": round(duration, 3),
                    "memory_delta_mb": round(memory_delta, 2) if memory_delta else None,
                })
                
                return result
            return wrapper
        return decorator
    
    def summary(self) -> pd.DataFrame:
        """Return performance summary"""
        return pd.DataFrame(self.operations)


# Example usage in your main code:
"""
# In your cleaning pipeline:
@st.cache_data
def process_large_dataset(df):
    # This will be cached
    df, mem_stats = optimize_dtypes(df)
    return df, mem_stats

# In your UI:
df = st.session_state.df
preview_df, metadata = create_lazy_preview(df, preview_rows=100)

# Display safe version
safe_dataframe_display(df, styled=True, style_func=style_preview)

# Show data summary
display_data_summary(df)
"""
