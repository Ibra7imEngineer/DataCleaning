"""
================================================================================
    STREAMLIT INTEGRATION: Advanced Imputation Engine for DataX Platform
    حرك الاستدلال الذكي - Smart Imputation UI for Enterprise Data Cleaning
================================================================================

This is the PRODUCTION-GRADE Streamlit application that integrates the
Advanced Imputation Engine with a beautiful, intuitive UI for the DataX platform.

FEATURES:
✓ Real-time imputation preview
✓ Configurable imputation levels
✓ Enterprise audit trail & metrics
✓ Premium Neon-Green styling for filled cells
✓ CSV/Excel export with metadata
✓ Multi-column simultaneous processing
✓ Responsive, mobile-friendly UI

USAGE:
    streamlit run streamlit_advanced_imputation_ui.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from advanced_imputation_engine import (
    AdvancedImputationEngine,
    streamlit_imputation_style,
    get_imputation_summary
)
import io


# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION & STYLING
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="DataX - Advanced Imputation Engine",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    /* Premium gradient header */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    /* Neon green accent for success states */
    .success-box {
        background-color: rgba(46, 204, 113, 0.1);
        border-left: 4px solid rgba(46, 204, 113, 1);
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 8px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR: CONFIGURATION PANEL
# ═══════════════════════════════════════════════════════════════════════════

st.sidebar.title("⚙️ Configuration Panel")

with st.sidebar.expander("📋 Engine Settings", expanded=True):
    verbose_mode = st.checkbox("Verbose Logging", value=True)
    show_original = st.checkbox("Show Original Data", value=True)
    show_comparison = st.checkbox("Side-by-Side Comparison", value=False)


# ═══════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="header-container">
    <h1>🧹 DataX - Advanced Imputation Engine</h1>
    <p>Elite-Tier Missing Value Management for Enterprise Data Cleaning</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# MAIN CONTENT: DATA UPLOAD & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("## 📂 Step 1: Upload Your Dataset")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your dataset with missing values"
    )

# Initialize session state for data
if uploaded_file is not None:
    # Load data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.session_state.df = df
        st.session_state.df_original = df.copy()
        
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        st.stop()

# Show data preview if available
if 'df' in st.session_state:
    df = st.session_state.df
    
    if show_original:
        st.markdown("### Original Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Show missing value summary
        st.markdown("### Missing Values Summary")
        missing_summary = pd.DataFrame({
            'Column': df.columns,
            'Missing Count': df.isna().sum().values,
            'Missing %': (df.isna().sum() / len(df) * 100).round(2).values
        })
        st.dataframe(missing_summary, use_container_width=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # CONFIGURATION: COLUMN SELECTION & GUIDES
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("## ⚙️ Step 2: Configure Imputation Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔢 Numeric Columns to Fill")
        numeric_options = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols_to_fill = st.multiselect(
            "Select numeric columns for imputation",
            options=numeric_options,
            default=numeric_options[:min(2, len(numeric_options))],
            help="Columns that contain numeric values (prices, quantities, etc.)"
        )
    
    with col2:
        st.markdown("### 📝 Categorical Columns to Fill")
        categorical_options = df.select_dtypes(include=['object']).columns.tolist()
        categorical_cols_to_fill = st.multiselect(
            "Select categorical columns for imputation",
            options=categorical_options,
            default=categorical_options[:min(1, len(categorical_options))],
            help="Columns that contain text/categories"
        )
    
    # Guide columns selection
    st.markdown("### 🎯 Context Guides for Intelligent Imputation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fine_grain_guide = st.selectbox(
            "Fine-Grain Guide (Item/Product Identifier)",
            options=df.columns.tolist(),
            help="Column that identifies specific items (e.g., 'Product Name', 'Item ID')"
        )
    
    with col2:
        coarse_grain_guide = st.selectbox(
            "Coarse-Grain Guide (Department/Category)",
            options=df.columns.tolist(),
            index=1 if len(df.columns) > 1 else 0,
            help="Column that identifies broader categories (e.g., 'Department', 'Category')"
        )
    
    # Run imputation
    if st.button("🚀 Run Advanced Imputation", type="primary", use_container_width=True):
        
        if not numeric_cols_to_fill and not categorical_cols_to_fill:
            st.warning("⚠️ Please select at least one column to fill")
        else:
            with st.spinner("🔄 Processing... Running Advanced Imputation Waterfall..."):
                try:
                    # Initialize engine
                    engine = AdvancedImputationEngine(verbose=verbose_mode)
                    
                    # Run imputation
                    df_filled, metrics = engine.fill_missing_values_advanced(
                        df=df,
                        numeric_cols_to_fill=numeric_cols_to_fill,
                        categorical_cols_to_fill=categorical_cols_to_fill,
                        fine_grain_guide=fine_grain_guide,
                        coarse_grain_guide=coarse_grain_guide
                    )
                    
                    # Store in session state
                    st.session_state.df_filled = df_filled
                    st.session_state.metrics = metrics
                    st.session_state.imputation_complete = True
                    
                    st.success("✅ Imputation Complete!")
                    
                except Exception as e:
                    st.error(f"❌ Error during imputation: {str(e)}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # RESULTS SECTION
    # ═══════════════════════════════════════════════════════════════════════
    
    if 'imputation_complete' in st.session_state and st.session_state.imputation_complete:
        
        st.markdown("## ✅ Imputation Results")
        
        df_filled = st.session_state.df_filled
        metrics = st.session_state.metrics
        
        # Display metrics summary
        st.markdown("### 📊 Imputation Metrics Summary")
        summary_df = get_imputation_summary(metrics)
        st.dataframe(summary_df, use_container_width=True)
        
        # Show detailed breakdown
        st.markdown("### 🔍 Level-by-Level Breakdown")
        
        metrics_data = []
        for col_name, metric in metrics.items():
            metrics_data.append({
                'Column': col_name,
                'Level 1 (Item)': f"{metric.level_1_count} ({metric.level_1_count/metric.total_missing*100:.1f}%)" if metric.total_missing > 0 else "0%",
                'Level 2 (Category)': f"{metric.level_2_count} ({metric.level_2_count/metric.total_missing*100:.1f}%)" if metric.total_missing > 0 else "0%",
                'Level 3 (Neighbor)': f"{metric.level_3_count} ({metric.level_3_count/metric.total_missing*100:.1f}%)" if metric.total_missing > 0 else "0%",
                'Level 4 (Global)': f"{metric.level_4_count} ({metric.level_4_count/metric.total_missing*100:.1f}%)" if metric.total_missing > 0 else "0%",
            })
        
        breakdown_df = pd.DataFrame(metrics_data)
        st.dataframe(breakdown_df, use_container_width=True)
        
        # Show comparison if requested
        if show_comparison:
            st.markdown("### 🔄 Side-by-Side Comparison")
            
            comparison_tabs = st.tabs(["Before", "After", "Differences"])
            
            with comparison_tabs[0]:
                st.subheader("Before Imputation")
                st.dataframe(df.head(15), use_container_width=True)
            
            with comparison_tabs[1]:
                st.subheader("After Imputation")
                st.dataframe(df_filled.head(15), use_container_width=True)
            
            with comparison_tabs[2]:
                st.subheader("What Changed")
                # Find columns with imputation status
                status_cols = [col for col in df_filled.columns if '_imputation_status' in col]
                if status_cols:
                    st.dataframe(df_filled[status_cols].head(15), use_container_width=True)
        
        # Show filled data with premium styling
        st.markdown("### 🎨 Styled Output (Premium Neon-Green Highlights)")
        
        status_cols = [col for col in df_filled.columns if '_imputation_status' in col]
        
        if status_cols:
            # Create styled version
            try:
                styled = streamlit_imputation_style(df_filled, status_cols)
                st.dataframe(styled, use_container_width=True)
            except:
                # Fallback if styling fails
                st.dataframe(df_filled.head(20), use_container_width=True)
        else:
            st.dataframe(df_filled.head(20), use_container_width=True)
        
        # ═══════════════════════════════════════════════════════════════════════
        # EXPORT SECTION
        # ═══════════════════════════════════════════════════════════════════════
        
        st.markdown("## 💾 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV export
            csv = df_filled.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="datax_imputed.csv",
                mime="text/csv"
            )
        
        with col2:
            # Excel export
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_filled.to_excel(writer, sheet_name='Imputed Data', index=False)
                summary_df.to_excel(writer, sheet_name='Metrics', index=False)
            
            buffer.seek(0)
            st.download_button(
                label="📊 Download as Excel",
                data=buffer,
                file_name="datax_imputed.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            # JSON export (metadata only)
            metrics_json = {}
            for col_name, metric in metrics.items():
                metrics_json[col_name] = {
                    'total_missing': metric.total_missing,
                    'total_filled': metric.total_filled,
                    'level_1': metric.level_1_count,
                    'level_2': metric.level_2_count,
                    'level_3': metric.level_3_count,
                    'level_4': metric.level_4_count,
                    'fillrate': f"{metric.fillrate:.1f}%"
                }
            
            import json
            json_data = json.dumps(metrics_json, indent=2)
            st.download_button(
                label="📋 Download Metadata (JSON)",
                data=json_data,
                file_name="datax_metrics.json",
                mime="application/json"
            )

# ═══════════════════════════════════════════════════════════════════════════
# FOOTER & DOCUMENTATION
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("---")

st.markdown("""
### 📚 How the Advanced Imputation Engine Works

#### 4-Level Waterfall Logic for Numeric Values:
1. **Level 1 - Item Context**: Uses the median of the specific item (e.g., all "Coffee" records)
2. **Level 2 - Category Fallback**: Uses the median of the broader category (e.g., all "Foods")
3. **Level 3 - Sequential Neighbor**: Copies value from adjacent row if same transaction
4. **Level 4 - Global Median**: Falls back to column-wide median as last resort

#### 4-Level Waterfall Logic for Categorical Values:
1. **Level 1 - Identifier Mode**: Most frequent category for this specific item
2. **Level 2 - Value-Range Proximity**: Most frequent category in same price range
3. **Level 3 - Sequential Propagation**: Copies category from adjacent row
4. **Level 4 - Global Mode**: Most frequent category in entire column

#### Enterprise Features:
- ✅ Metadata tracking for every imputed cell
- ✅ 100% vectorized Pandas operations (no loops)
- ✅ Premium Neon-Green styling for audit trails
- ✅ Complete imputation metrics and compliance reports
- ✅ Export to CSV, Excel, JSON with full provenance

---
**DataX Platform v2.0** | Elite Principal Data Scientist  
*Transforming missing values into intelligent insights.*
""")
