"""
Streamlit UI for Independent Semantic Clustering and Harmonization
Provides an interactive interface to clean and harmonize DataFrame values
with real-time feedback and detailed logging.
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime
from semantic_clustering_arabic import (
    semantic_clustering_harmonization,
    format_logs_for_display,
    get_correction_summary,
    normalize_arabic_text
)


def build_before_after_sample(df_original: pd.DataFrame, logs: dict, max_examples: int = 6) -> pd.DataFrame:
    """Build a small before/after sample table from harmonization logs."""
    rows = []
    for col, corrections in logs.items():
        if not corrections:
            continue
        for record in corrections:
            master = record.get('master_word')
            for raw_value in record.get('matched_variations', []):
                rows.append({
                    'Column': col,
                    'Before': raw_value,
                    'After': master
                })
                if len(rows) >= max_examples:
                    break
            if len(rows) >= max_examples:
                break
        if len(rows) >= max_examples:
            break
    return pd.DataFrame(rows)


def build_audit_report(logs: dict, max_examples: int = 200) -> pd.DataFrame:
    """Build a clear audit report table from harmonization logs."""
    rows = []
    for col, corrections in logs.items():
        if not corrections:
            continue
        for record in corrections:
            for item in record.get('audit_items', []):
                rows.append({
                    'Column': col,
                    'Old Value': item.get('old_value'),
                    'New Value': item.get('new_value'),
                    'Match Method': item.get('match_method'),
                    'Score': item.get('score')
                })
                if len(rows) >= max_examples:
                    break
            if len(rows) >= max_examples:
                break
        if len(rows) >= max_examples:
            break
    return pd.DataFrame(rows)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Data Harmonization Engine",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("✨ Independent Semantic Clustering & Harmonization")
st.markdown("*Transform messy text data into consistent, harmonized values*")


# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    fuzzy_threshold = st.slider(
        "Fuzzy Matching Threshold",
        min_value=70,
        max_value=100,
        value=80,
        step=1,
        help="Higher = stricter matching. 80 is recommended for aggressive Arabic typo matching."
    )
    
    max_unique_values = st.number_input(
        "Max Unique Values per Column",
        min_value=10,
        max_value=10000,
        value=500,
        step=50,
        help="Skip columns with more unique values (protects IDs/Emails)"
    )
    
    min_unique_values = st.number_input(
        "Min Unique Values per Column",
        min_value=1,
        max_value=100,
        value=2,
        step=1,
        help="Skip columns with fewer unique values"
    )
    
    st.markdown("---")
    st.markdown(
        """
        ### 📚 How It Works:
        1. **Upload** a CSV or Excel file
        2. **Configure** matching parameters
        3. **Execute** harmonization
        4. **Review** corrections and download results
        
        ### 🎯 Best For:
        - Arabic text with typographic variants
        - Fuzzy duplicates (typos, spacing)
        - Multi-language product names
        - Address/location standardization
        """
    )


# ============================================================================
# MAIN INTERFACE
# ============================================================================

tab1, tab2, tab3 = st.tabs(["📤 Upload & Execute", "📊 Results", "📋 Logs & Details"])

# TAB 1: UPLOAD AND EXECUTE
with tab1:
    st.subheader("Step 1: Upload Your Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            help="Supported formats: CSV, XLSX, XLS"
        )
    
    with col2:
        use_sample = st.checkbox(
            "Use Sample Data",
            help="Load a sample Arabic dataset for testing"
        )
    
    # Initialize session state
    if 'df_original' not in st.session_state:
        st.session_state.df_original = None
    if 'df_cleaned' not in st.session_state:
        st.session_state.df_cleaned = None
    if 'harmonization_logs' not in st.session_state:
        st.session_state.harmonization_logs = None
    if 'harmonization_summary' not in st.session_state:
        st.session_state.harmonization_summary = None
    if 'execution_timestamp' not in st.session_state:
        st.session_state.execution_timestamp = None
    
    # Load data
    if use_sample:
        st.session_state.df_original = pd.DataFrame({
            'Item': [
                'ترابيزة', 'ترابيزه', 'ترابيزه', 'ترابيزة',
                'كنبة', 'كنبه', 'كنبة', 'كنبه',
                'كرسي', 'كرسي', 'كرسي',
                'طاولة', 'طاولة', 'طاوله',
                'دولاب', 'دولابة', 'دولاب'
            ],
            'Category': ['Furniture'] * 17,
            'Price': [100, 100, 100, 100, 200, 200, 200, 200, 50, 50, 50, 120, 120, 120, 300, 300, 300]
        })
        st.success("✅ Sample data loaded successfully!")
        
    elif uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.df_original = pd.read_csv(uploaded_file)
            else:
                st.session_state.df_original = pd.read_excel(uploaded_file)
            st.success(f"✅ File loaded: {uploaded_file.name}")
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
            st.session_state.df_original = None
    
    # Display preview
    if st.session_state.df_original is not None:
        st.info(f"📊 DataFrame Shape: {st.session_state.df_original.shape[0]} rows × {st.session_state.df_original.shape[1]} columns")
        
        with st.expander("👁️ Preview Data", expanded=False):
            st.dataframe(st.session_state.df_original.head(10), use_container_width=True)
        
        # Show unique value counts for text columns
        with st.expander("📈 Text Column Analysis", expanded=False):
            text_cols = st.session_state.df_original.select_dtypes(include=['object', 'string']).columns
            for col in text_cols:
                unique_count = st.session_state.df_original[col].nunique()
                st.write(f"**{col}**: {unique_count} unique values")
                
                if unique_count <= 50:
                    counts = st.session_state.df_original[col].value_counts()
                    st.bar_chart(counts)
    
    # EXECUTE BUTTON
    st.markdown("---")
    st.subheader("Step 2: Execute Harmonization")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        execute_button = st.button(
            "🚀 Execute Semantic Clustering",
            key="execute_btn",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        show_normalization = st.checkbox("Show Normalization Examples", help="Display how Arabic text gets normalized")
    
    with col3:
        pass
    
    # Show normalization examples
    if show_normalization:
        st.info("### 📝 Arabic Normalization Examples:")
        examples = [
            ('ترابيزة', normalize_arabic_text('ترابيزة')),
            ('كنبه', normalize_arabic_text('كنبه')),
            ('آخر', normalize_arabic_text('آخر')),
            ('إسلام', normalize_arabic_text('إسلام')),
        ]
        
        example_df = pd.DataFrame(examples, columns=['Original', 'Normalized'])
        st.table(example_df)
    
    # Execute harmonization
    if execute_button:
        if st.session_state.df_original is None:
            st.error("❌ Please upload a file or use sample data first!")
        else:
            with st.spinner("⏳ Processing... Executing semantic clustering..."):
                try:
                    st.session_state.df_cleaned, st.session_state.harmonization_logs = \
                        semantic_clustering_harmonization(
                            st.session_state.df_original,
                            fuzzy_threshold=fuzzy_threshold,
                            max_unique_values=max_unique_values,
                            min_unique_values=min_unique_values,
                            normalize_func=normalize_arabic_text
                        )
                    
                    st.session_state.harmonization_summary = get_correction_summary(
                        st.session_state.harmonization_logs
                    )
                    st.session_state.execution_timestamp = datetime.now()
                    
                    st.success("✅ Harmonization completed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error during harmonization: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())


# TAB 2: RESULTS
with tab2:
    st.subheader("🎯 Harmonized Data")
    
    if st.session_state.df_cleaned is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ BEFORE (Original)")
            st.info(f"Rows: {st.session_state.df_original.shape[0]} | Columns: {st.session_state.df_original.shape[1]}")
            st.dataframe(st.session_state.df_original, use_container_width=True, height=300)
        
        with col2:
            st.markdown("### ✨ AFTER (Harmonized)")
            st.success(f"Rows: {st.session_state.df_cleaned.shape[0]} | Columns: {st.session_state.df_cleaned.shape[1]}")
            st.dataframe(st.session_state.df_cleaned, use_container_width=True, height=300)
        
        # Comparison by column
        st.markdown("---")
        st.subheader("📊 Value Count Comparison")
        
        text_cols = st.session_state.df_original.select_dtypes(include=['object', 'string']).columns
        
        for col in text_cols:
            with st.expander(f"📌 Column: {col}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Before:**")
                    before_counts = st.session_state.df_original[col].value_counts()
                    st.dataframe(before_counts)
                
                with col2:
                    st.write("**After:**")
                    after_counts = st.session_state.df_cleaned[col].value_counts()
                    st.dataframe(after_counts)
        
        st.markdown("---")
        st.subheader("🔍 Before vs After Sample")
        sample_df = build_before_after_sample(
            st.session_state.df_original,
            st.session_state.harmonization_logs,
            max_examples=6
        )
        if not sample_df.empty:
            st.table(sample_df)
        else:
            st.info("No corrected before/after sample rows available. Run harmonization with eligible text columns first.")
        
        # Download section
        st.markdown("---")
        st.subheader("💾 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = st.session_state.df_cleaned.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"harmonized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            excel_buffer = io.BytesIO()
            st.session_state.df_cleaned.to_excel(excel_buffer, index=False, sheet_name='Harmonized')
            excel_buffer.seek(0)
            st.download_button(
                label="📊 Download as Excel",
                data=excel_buffer,
                file_name=f"harmonized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )
        
        with col3:
            st.info("✨ Clean data ready to use!")
    else:
        st.info("⏳ Run harmonization first to see results")


# TAB 3: LOGS AND DETAILS
with tab3:
    st.subheader("📋 Harmonization Logs & Statistics")
    
    if st.session_state.harmonization_logs is not None:
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Columns Processed",
                st.session_state.harmonization_summary['total_columns_processed']
            )
        
        with col2:
            st.metric(
                "Correction Groups",
                st.session_state.harmonization_summary['total_correction_groups']
            )
        
        with col3:
            st.metric(
                "Variations Harmonized",
                st.session_state.harmonization_summary['total_variations_harmonized']
            )
        
        with col4:
            if st.session_state.execution_timestamp:
                st.metric(
                    "Execution Time",
                    st.session_state.execution_timestamp.strftime("%H:%M:%S")
                )
        
        # Detailed logs
        st.markdown("---")
        st.subheader("🔍 Detailed Correction Logs")
        
        for col, corrections in st.session_state.harmonization_logs.items():
            if corrections:
                with st.expander(f"📌 Column: {col}", expanded=True):
                    st.write(f"**Total Correction Groups:** {len(corrections)}")
                    
                    for idx, record in enumerate(corrections, 1):
                        st.write(f"**Group {idx}:**")
                        st.write(f"- Master Word: `{record['master_word']}`")
                        st.write(f"- Matched Variations: {record['matched_variations']}")
                        st.write(f"- Number of Values Unified: {record['num_corrections']}")
                        st.divider()
            else:
                with st.expander(f"📌 Column: {col} (No corrections)", expanded=False):
                    st.info(f"ℹ️ No fuzzy matches found for this column.")
        
        # Audit report
        st.markdown("---")
        st.subheader("🧾 Audit Report")
        audit_df = build_audit_report(st.session_state.harmonization_logs, max_examples=200)
        if not audit_df.empty:
            st.dataframe(audit_df, use_container_width=True, height=250)
        else:
            st.info("No audit report items available. Run harmonization with eligible text columns first.")
        
        # Export logs
        st.markdown("---")
        st.subheader("📤 Export Logs")
        
        logs_text = format_logs_for_display(st.session_state.harmonization_logs)
        st.download_button(
            label="📥 Download Logs as Text",
            data=logs_text,
            file_name=f"harmonization_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    else:
        st.info("⏳ Run harmonization first to see detailed logs")


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 0.85rem;">
    <p>🔧 Data Harmonization Engine | Powered by Rapidfuzz & Streamlit</p>
    <p>Supports Arabic normalization, fuzzy matching, and independent clustering</p>
    </div>
    """,
    unsafe_allow_html=True
)
