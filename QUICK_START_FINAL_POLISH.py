"""
🚀 البدء السريع - دالة final_polish
====================================
استخدام سريع وسهل للدالة قبل التصدير مباشرة

استخدم هذا الملف كنموذج سريع للبدء الفوري!
"""

import pandas as pd
import numpy as np
from final_polish import final_polish
from datetime import datetime


# ============================================================
# مثال 1️⃣: الاستخدام الأساسي (3 أسطر فقط)
# ============================================================

def example_basic():
    """استخدام بسيط وسريع"""
    
    print("\n" + "=" * 70)
    print("مثال 1️⃣: الاستخدام الأساسي")
    print("=" * 70)
    
    # 1. تحميل البيانات
    df = pd.DataFrame({
        'ProductID': ['1.0', '2.0', '3.0'],
        'Price': [99.5, 150.0, 'غير محدد'],
        'OrderDate': ['2024-01-15', '2024-02-20 14:30:00', '2024-03-10']
    })
    
    print("\n📥 البيانات الأصلية:")
    print(df)
    
    # 2. المعالجة النهائية
    clean_df, report = final_polish(
        df,
        date_columns=['OrderDate'],
        numeric_columns=['ProductID', 'Price']
    )
    
    # 3. النتائج
    print("\n📤 البيانات المعالجة:")
    print(clean_df)
    print(f"\n✓ العمليات المنفذة: {report['operations']}")


# ============================================================
# مثال 2️⃣: مع بيانات معقدة
# ============================================================

def example_complex():
    """معالجة بيانات معقدة وشاذة"""
    
    print("\n" + "=" * 70)
    print("مثال 2️⃣: بيانات معقدة وشاذة")
    print("=" * 70)
    
    df = pd.DataFrame({
        'TransactionID': [1.0, 2.0, '3.0', 4.0, '5.0'],
        'TransactionID_Backup': [1.0, 2.0, '3.0', 4.0, '5.0'],  # متطابق
        'Amount': [100.5, 200.0, 'N/A', 400.0, 'غير متوفر'],
        'OrderDate': [
            '2024-01-15',
            '2024-02-20 14:30:00',
            'تاريخ غير محدد',  # نص بدل تاريخ
            '2024-04-10 00:00:00',
            None
        ],
        'ShipDate': [
            datetime(2024, 1, 16, 9, 30),
            '2024-02-21',
            '2024-03-01',
            '2024-04-11',
            'لم يتم الشحن'
        ],
        'CustomerName': ['أحمد', '', 'محمد', 'فاطمة', 'علي']
    })
    
    print("\n📥 البيانات الأصلية:")
    print(df)
    print(f"الحجم: {len(df)} صف × {len(df.columns)} عمود")
    
    # المعالجة
    clean_df, report = final_polish(
        df=df,
        date_columns=['OrderDate', 'ShipDate'],
        numeric_columns=['TransactionID', 'Amount'],
        verbose=True
    )
    
    print("\n📤 البيانات المعالجة:")
    print(clean_df)
    print(f"\nالحجم: {len(clean_df)} صف × {len(clean_df.columns)} عمود")
    
    # عرض التقرير
    print("\n📊 التقرير التفصيلي:")
    print(f"  • أعمدة متطابقة محذوفة: {report['duplicate_columns_removed']}")
    print(f"  • أعمدة تاريخ معالجة: {report['date_columns_cleaned']}")
    print(f"  • أعمدة رقمية معالجة: {report['numeric_columns_converted']}")
    print(f"  • ملاحظات النظام المضافة: {report['system_notes_added']}")
    
    # عرض الملاحظات
    if 'System_Notes' in clean_df.columns:
        notes = clean_df[clean_df['System_Notes'] != '']['System_Notes']
        if len(notes) > 0:
            print(f"\n  ملاحظات النظام:")
            for idx, note in notes.items():
                print(f"    - الصف {idx}: {note}")


# ============================================================
# مثال 3️⃣: مع Streamlit (بدون تشغيل Streamlit)
# ============================================================

def example_for_streamlit():
    """الكود الذي تحتاجه في تطبيق Streamlit"""
    
    print("\n" + "=" * 70)
    print("مثال 3️⃣: للاستخدام مع Streamlit")
    print("=" * 70)
    
    code = '''
import streamlit as st
import pandas as pd
from final_polish import final_polish

# رفع الملف
uploaded_file = st.file_uploader("اختر ملف CSV", type=['csv', 'xlsx'])

if uploaded_file:
    # قراءة البيانات
    df = pd.read_csv(uploaded_file)
    
    st.info(f"📊 البيانات المرفوعة: {len(df):,} صف × {len(df.columns)} عمود")
    
    # المعالجة النهائية
    if st.button("🧹 تطبيق المعالجة النهائية"):
        clean_df, report = final_polish(df, verbose=True)
        
        st.success(f"✅ تمت المعالجة!")
        
        # عرض الملخص
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("الصفوف", f"{len(clean_df):,}")
        with col2:
            st.metric("الأعمدة", len(clean_df.columns))
        with col3:
            st.metric("الملاحظات", report['system_notes_added'])
        
        # تحميل النتائج
        st.download_button(
            label="📥 تحميل Excel",
            data=clean_df.to_excel(index=False),
            file_name="cleaned.xlsx"
        )
    '''
    
    print("\n📋 انسخ هذا الكود في تطبيق Streamlit:")
    print(code)


# ============================================================
# مثال 4️⃣: معالجة بيانات ضخمة
# ============================================================

def example_large_dataset():
    """معالجة مليون صف بسرعة"""
    
    print("\n" + "=" * 70)
    print("مثال 4️⃣: بيانات ضخمة (مليون صف)")
    print("=" * 70)
    
    import time
    
    # إنشاء مليون صف
    print("\n🔨 إنشاء بيانات اختبار: مليون صف...")
    n_rows = 1_000_000
    
    df = pd.DataFrame({
        'ID': np.arange(1, n_rows + 1).astype(float),
        'Value': np.random.rand(n_rows),
        'Date': pd.date_range('2024-01-01', periods=n_rows),
        'Category': np.random.choice(['A', 'B', 'C'], n_rows)
    })
    
    print(f"✓ تم إنشاء {n_rows:,} صف")
    
    # المعالجة
    print("\n⏱️  بدء المعالجة...")
    start_time = time.time()
    
    clean_df, report = final_polish(
        df,
        date_columns=['Date'],
        numeric_columns=['ID', 'Value'],
        verbose=False
    )
    
    duration = time.time() - start_time
    
    # النتائج
    print(f"✓ انتهت المعالجة في: {duration:.2f} ثانية")
    print(f"📊 الإحصائيات:")
    print(f"  • معالجة: {n_rows / duration:,.0f} صف/ثانية")
    print(f"  • الصفوف: {len(clean_df):,}")
    print(f"  • الأعمدة: {len(clean_df.columns)}")


# ============================================================
# مثال 5️⃣: معالجة متعددة المراحل
# ============================================================

def example_multi_stage():
    """معالجة البيانات على مراحل متعددة"""
    
    print("\n" + "=" * 70)
    print("مثال 5️⃣: معالجة متعددة المراحل")
    print("=" * 70)
    
    # البيانات الخام
    df = pd.DataFrame({
        'ID': ['1.0', '2.0', '3.0'],
        'Name': ['أحمد', 'فاطمة', ''],
        'Age': [30.0, 'غير محدد', 25.0],
        'JoinDate': ['2024-01-15', '2024-02-20 14:30:00', None]
    })
    
    print("\n📥 المرحلة 1: البيانات الخام")
    print(df)
    
    # المرحلة 2: التنظيف الأولي
    print("\n🔄 المرحلة 2: التنظيف الأولي")
    df = df.dropna(subset=['ID'])  # حذف صفوف بدون ID
    print(df)
    
    # المرحلة 3: المعالجة النهائية
    print("\n✨ المرحلة 3: المعالجة النهائية (final_polish)")
    clean_df, report = final_polish(
        df,
        date_columns=['JoinDate'],
        numeric_columns=['ID', 'Age'],
        verbose=False
    )
    
    print("\n📤 النتيجة النهائية:")
    print(clean_df)
    
    # المرحلة 4: التصدير
    print("\n💾 المرحلة 4: التصدير")
    clean_df.to_excel('cleaned_data.xlsx', index=False)
    print("✓ تم حفظ في: cleaned_data.xlsx")


# ============================================================
# مثال 6️⃣: معالجة ملف حقيقي
# ============================================================

def example_real_file():
    """معالجة ملف CSV حقيقي من المجلد"""
    
    print("\n" + "=" * 70)
    print("مثال 6️⃣: معالجة ملف CSV حقيقي")
    print("=" * 70)
    
    try:
        # محاولة قراءة ملف sample_data.csv
        df = pd.read_csv('sample_data.csv')
        
        print(f"\n📥 تم تحميل: {len(df):,} صف × {len(df.columns)} عمود")
        
        # تطبيق المعالجة
        clean_df, report = final_polish(df, verbose=True)
        
        print(f"\n📤 تم المعالجة: {len(clean_df):,} صف × {len(clean_df.columns)} عمود")
        
        # التصدير
        clean_df.to_excel('sample_data_cleaned.xlsx', index=False)
        print(f"\n✓ تم حفظ في: sample_data_cleaned.xlsx")
        
    except FileNotFoundError:
        print("⚠️  الملف 'sample_data.csv' غير موجود")
        print("💡 إذا كان لديك ملف CSV، استخدم:")
        print("   df = pd.read_csv('your_file.csv')")


# ============================================================
# الدالة الرئيسية
# ============================================================

def main():
    """تشغيل الأمثلة"""
    
    print("\n" + "#" * 70)
    print("# 🚀 البدء السريع - دالة final_polish")
    print("# Quick Start Guide - final_polish Function")
    print("#" * 70)
    
    print("\n📋 الأمثلة المتاحة:")
    print("  1. الاستخدام الأساسي (أبسط نموذج)")
    print("  2. بيانات معقدة وشاذة")
    print("  3. كود Streamlit (نسخ مباشر)")
    print("  4. بيانات ضخمة (مليون صف)")
    print("  5. معالجة متعددة المراحل")
    print("  6. ملف CSV حقيقي")
    
    # تشغيل جميع الأمثلة
    example_basic()
    example_complex()
    example_for_streamlit()
    example_large_dataset()
    example_multi_stage()
    example_real_file()
    
    # الخلاصة
    print("\n" + "=" * 70)
    print("✅ انتهت جميع الأمثلة!")
    print("=" * 70)
    
    print("\n💡 نصائح للبدء:")
    print("  • استخدم المثال 1️⃣ كقالب أساسي")
    print("  • أضف هذا الكود قبل تصدير Excel مباشرة")
    print("  • اقرأ FINAL_POLISH_GUIDE.md للتفاصيل")
    print("  • شغّل test_final_polish.py للاختبارات")
    
    print("\n🎯 الخطوة التالية:")
    print("  python test_final_polish.py  # تشغيل الاختبارات")
    print("  streamlit run streamlit_final_polish_example.py  # عرض Streamlit")


if __name__ == "__main__":
    main()
