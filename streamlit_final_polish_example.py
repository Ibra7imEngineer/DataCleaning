"""
مثال على استخدام دالة final_polish مع تطبيق Streamlit
====================================================
يوضح كيفية دمج الدالة في عملية التنظيف قبل التصدير مباشرة

Author: Streamlit App Team
Version: 1.0
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
from final_polish import final_polish


def example_streamlit_integration():
    """
    🎯 مثال على دمج final_polish مع تطبيق Streamlit
    
    هذا المثال يوضح:
    1. رفع ملف CSV
    2. معالجة البيانات
    3. تطبيق final_polish
    4. تصدير النتيجة
    """
    
    st.set_page_config(page_title="Data Cleaner - Final Polish", layout="wide")
    
    st.title("🧹 أداة تنظيف البيانات مع المعالجة النهائية")
    st.markdown("---")
    
    # ============================================================
    # القسم 1: رفع الملف
    # ============================================================
    
    st.header("📤 الخطوة 1: رفع البيانات")
    uploaded_file = st.file_uploader("اختر ملف CSV", type=['csv', 'xlsx'])
    
    if uploaded_file is None:
        st.info("👈 الرجاء رفع ملف CSV أو Excel")
        return
    
    # قراءة الملف
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✓ تم تحميل {len(df):,} صف × {len(df.columns)} عمود")
    except Exception as e:
        st.error(f"❌ خطأ في قراءة الملف: {e}")
        return
    
    # ============================================================
    # القسم 2: معلومات الملف
    # ============================================================
    
    st.header("📊 معلومات البيانات الأصلية")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("عدد الصفوف", f"{len(df):,}")
    with col2:
        st.metric("عدد الأعمدة", len(df.columns))
    with col3:
        st.metric("الذاكرة المستخدمة", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    with col4:
        st.metric("القيم الفارغة", df.isna().sum().sum())
    
    # عرض البيانات
    st.subheader("معاينة البيانات الأصلية")
    st.dataframe(df.head(10), use_container_width=True)
    
    # ============================================================
    # القسم 3: تحديد الأعمدة
    # ============================================================
    
    st.header("🎯 الخطوة 2: تحديد أنواع الأعمدة")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 أعمدة التاريخ")
        available_cols = df.columns.tolist()
        date_columns = st.multiselect(
            "اختر أعمدة التاريخ",
            options=available_cols,
            default=[col for col in available_cols if 'date' in col.lower()],
            key='date_cols'
        )
    
    with col2:
        st.subheader("🔢 الأعمدة الرقمية")
        numeric_columns = st.multiselect(
            "اختر الأعمدة الرقمية",
            options=available_cols,
            default=df.select_dtypes(include=[np.number]).columns.tolist(),
            key='numeric_cols'
        )
    
    # ============================================================
    # القسم 4: تطبيق المعالجة النهائية
    # ============================================================
    
    st.header("⚙️ الخطوة 3: تطبيق المعالجة النهائية")
    
    # الإعدادات
    col1, col2 = st.columns(2)
    with col1:
        verbose_mode = st.checkbox("عرض التفاصيل", value=True)
    with col2:
        auto_detect = st.checkbox("كشف تلقائي للأعمدة", value=True)
    
    # زر المعالجة
    if st.button("🚀 تطبيق المعالجة النهائية", use_container_width=True):
        
        with st.spinner("⏳ جاري المعالجة..."):
            try:
                # تطبيق final_polish
                cleaned_df, report = final_polish(
                    df=df,
                    date_columns=date_columns if date_columns else None,
                    numeric_columns=numeric_columns if numeric_columns else None,
                    verbose=verbose_mode
                )
                
                st.session_state.cleaned_df = cleaned_df
                st.session_state.report = report
                st.success("✅ تمت المعالجة بنجاح!")
                
            except Exception as e:
                st.error(f"❌ خطأ: {e}")
                return
    
    # ============================================================
    # القسم 5: عرض النتائج
    # ============================================================
    
    if 'cleaned_df' in st.session_state:
        
        cleaned_df = st.session_state.cleaned_df
        report = st.session_state.report
        
        st.header("📋 نتائج المعالجة")
        
        # ملخص المعالجة
        st.subheader("📊 ملخص التحسينات")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "الصفوف",
                f"{report['final_rows']:,}",
                f"{report['final_rows'] - report['original_rows']:,}"
            )
        with col2:
            st.metric(
                "الأعمدة",
                report['final_columns'],
                f"-{report['duplicate_columns_removed']}"
            )
        with col3:
            st.metric(
                "أعمدة التاريخ معالجة",
                report['date_columns_cleaned']
            )
        with col4:
            st.metric(
                "الأعمدة الرقمية معالجة",
                report['numeric_columns_converted']
            )
        
        # تفاصيل العمليات
        if report['operations']:
            st.subheader("🔧 العمليات المُنفذة")
            for op in report['operations']:
                st.write(f"  • {op}")
        
        # التحذيرات
        if report['warnings']:
            st.subheader("⚠️  التحذيرات")
            for warning in report['warnings']:
                st.warning(warning)
        
        # معاينة البيانات المعالجة
        st.subheader("📊 معاينة البيانات المعالجة")
        st.dataframe(cleaned_df.head(10), use_container_width=True)
        
        # ============================================================
        # القسم 6: التصدير
        # ============================================================
        
        st.header("💾 الخطوة 4: تصدير النتائج")
        
        col1, col2, col3 = st.columns(3)
        
        # تصدير Excel
        with col1:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                cleaned_df.to_excel(writer, sheet_name='البيانات المنظفة', index=False)
                
                # إضافة ورقة التقرير
                report_df = pd.DataFrame([report])
                report_df.to_excel(writer, sheet_name='التقرير', index=False)
            
            excel_buffer.seek(0)
            
            st.download_button(
                label="📥 تحميل Excel",
                data=excel_buffer,
                file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # تصدير CSV
        with col2:
            csv_buffer = cleaned_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 تحميل CSV",
                data=csv_buffer,
                file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # عرض التقرير JSON
        with col3:
            import json
            report_json = json.dumps(report, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 تحميل التقرير",
                data=report_json,
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        st.success("✅ جاهز للتصدير!")
    
    st.markdown("---")
    st.info("💡 للمزيد من المعلومات: اقرأ documentation في final_polish.py")


# ============================================================
# مثال للاستخدام المباشر (بدون Streamlit)
# ============================================================

def example_direct_usage():
    """
    💻 مثال للاستخدام المباشر في Jupyter أو سكريبت
    """
    
    print("=" * 70)
    print("مثال الاستخدام المباشر لـ final_polish")
    print("=" * 70)
    
    # إنشاء بيانات
    data = {
        'TransactionID': [1.0, 2.0, 3.0, '4.0', 5.0],
        'TransactionID_Backup': [1.0, 2.0, 3.0, '4.0', 5.0],  # متطابق
        'Amount': [100.5, 200.0, 'N/A', 400.0, 'غير محدد'],
        'OrderDate': [
            '2024-01-15',
            '2024-02-20 14:30:00',
            'تاريخ غير صحيح',
            '2024-04-10 00:00:00',
            None
        ],
        'ShipDate': [
            datetime(2024, 1, 16, 9, 30),
            '2024-02-21',
            '2024-03-01',
            '2024-04-11',
            'لم يتم الشحن بعد'
        ],
        'CustomerName': ['أحمد', '', 'محمد', 'فاطمة', 'علي']
    }
    
    df = pd.DataFrame(data)
    
    print("\n📥 البيانات الأصلية:")
    print(df)
    print(f"\nحجم: {len(df)} صف × {len(df.columns)} عمود")
    
    # تطبيق final_polish
    print("\n" + "=" * 70)
    print("تطبيق final_polish...")
    print("=" * 70)
    
    clean_df, report = final_polish(
        df=df,
        date_columns=['OrderDate', 'ShipDate'],
        numeric_columns=['TransactionID', 'Amount'],
        verbose=True
    )
    
    print("\n📤 البيانات المعالجة:")
    print(clean_df)
    
    print(f"\nحجم بعد المعالجة: {len(clean_df)} صف × {len(clean_df.columns)} عمود")
    
    print("\n📊 التقرير:")
    for key, value in report.items():
        if isinstance(value, list):
            print(f"  {key}:")
            for item in value:
                print(f"    - {item}")
        else:
            print(f"  {key}: {value}")
    
    # حفظ النتيجة
    output_file = "cleaned_data_demo.xlsx"
    clean_df.to_excel(output_file, index=False)
    print(f"\n✅ تم حفظ النتيجة في: {output_file}")


if __name__ == "__main__":
    # اختر نوع الاستخدام
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'direct':
        # الاستخدام المباشر
        example_direct_usage()
    else:
        # استخدام Streamlit
        example_streamlit_integration()
