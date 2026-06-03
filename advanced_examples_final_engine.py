"""
================================================================================
    أمثلة استخدام متقدمة لمحرك المعالجة الشامل
================================================================================

هذا الملف يوضح جميع الميزات والخيارات المتاحة
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from comprehensive_final_engine import ComprehensiveFinalEngine


# ============================================================================
# مثال 1: الاستخدام الأساسي البسيط
# ============================================================================

def example_1_basic_usage():
    """
    المثال الأول: معالجة ملف CSV بسيط
    """
    print("\n" + "=" * 80)
    print("📚 مثال 1: الاستخدام الأساسي (Basic Usage)")
    print("=" * 80)
    
    engine = ComprehensiveFinalEngine(verbose=True)
    
    # معالجة الملف
    processed_df = engine.process_comprehensive(
        input_path='sample_data.csv',
        output_path='example_1_output.xlsx'
    )
    
    print("\n✅ تم إنشاء الملفات:")
    print("   • example_1_output.xlsx (البيانات المعالجة)")
    print("   • example_1_output_audit_report.txt (تقرير العمليات)")
    
    return processed_df


# ============================================================================
# مثال 2: معالجة بيانات بدون تنسيق (Messy Data)
# ============================================================================

def example_2_messy_data():
    """
    المثال الثاني: معالجة بيانات فوضوية مع:
    - تواريخ بصيغ مختلفة
    - أرقام تحتوي على رموز
    - نصوص في أعمدة رقمية
    - قيم مكررة
    """
    print("\n" + "=" * 80)
    print("📚 مثال 2: البيانات الفوضوية (Messy Data)")
    print("=" * 80)
    
    # إنشاء بيانات فوضوية
    messy_data = {
        'ID': [1, 2, 2, 'Three', 4, 5, 5],
        'Name': ['Ahmed', 'Fatima', 'Fatima', 'Omar', '', 'Layla', 'Zainab'],
        'Date': ['2026-01-15', '15/02/2026', '2026-02-15', 'Ahmed Hassan', '2026-03-05', None, '2026-03-10'],
        'Amount': [1500, 2300, 2300, 1800, '950', '', 1200.00],
        'City': ['Cairo', 'Alexandria', 'Alexandria', 'Giza', 'Cairo', 'Alexandria', 'Cairo']
    }
    
    df_messy = pd.DataFrame(messy_data)
    df_messy.to_csv('messy_data.csv', index=False)
    
    print("\n📊 البيانات الفوضوية الأصلية:")
    print(df_messy)
    
    # معالجة البيانات
    engine = ComprehensiveFinalEngine(verbose=True)
    processed_df = engine.process_comprehensive(
        input_path='messy_data.csv',
        output_path='example_2_output.xlsx'
    )
    
    print("\n📊 البيانات بعد المعالجة:")
    print(processed_df)
    
    print("\n✅ تم إنشاء الملفات:")
    print("   • example_2_output.xlsx (البيانات النظيفة)")
    print("   • example_2_output_audit_report.txt (تقرير التنظيف)")
    
    return processed_df


# ============================================================================
# مثال 3: معالجة بيانات ضخمة (Performance Test)
# ============================================================================

def example_3_large_dataset():
    """
    المثال الثالث: معالجة مليون صف للتحقق من الأداء
    
    ملاحظة: هذا المثال قد يستغرق عدة دقائق
    """
    print("\n" + "=" * 80)
    print("📚 مثال 3: البيانات الضخمة (Large Dataset - 1M Rows)")
    print("=" * 80)
    
    # إنشاء بيانات ضخمة
    print("\n🔨 إنشاء مليون صف من البيانات...")
    np.random.seed(42)
    
    large_data = {
        'ID': np.arange(1, 1000001),
        'Name': np.random.choice(['Ahmed', 'Fatima', 'Omar', 'Zainab', 'Layla'], 1000000),
        'Date': pd.date_range('2026-01-01', periods=1000000, freq='H').astype(str),
        'Amount': np.random.uniform(100, 5000, 1000000),
        'Status': np.random.choice(['Active', 'Inactive', 'Pending'], 1000000)
    }
    
    df_large = pd.DataFrame(large_data)
    large_file = 'large_data.csv'
    
    print(f"💾 حفظ البيانات ({len(df_large):,} صف)...")
    df_large.to_csv(large_file, index=False)
    
    # معالجة البيانات
    print("\n⏱️  بدء المعالجة... (يرجى الانتظار)")
    
    import time
    start_time = time.time()
    
    engine = ComprehensiveFinalEngine(verbose=False)
    processed_df = engine.process_comprehensive(
        input_path=large_file,
        output_path='example_3_output.xlsx'
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"\n✅ انتهت المعالجة في {elapsed_time:.2f} ثانية")
    print(f"   السرعة: {len(processed_df) / elapsed_time:,.0f} صف/ثانية")
    print(f"\n✅ تم إنشاء الملفات:")
    print("   • example_3_output.xlsx (البيانات المعالجة)")
    print("   • example_3_output_audit_report.txt (تقرير العمليات)")
    
    return processed_df


# ============================================================================
# مثال 4: معالجة متقدمة مع تخصيص
# ============================================================================

def example_4_custom_processing():
    """
    المثال الرابع: معالجة متقدمة مع تخصيص المحرك
    """
    print("\n" + "=" * 80)
    print("📚 مثال 4: المعالجة المتقدمة (Advanced Custom Processing)")
    print("=" * 80)
    
    # إنشاء بيانات اختبار
    custom_data = {
        'Customer_ID': [1, 2, 3, 4, 5],
        'Purchase_Date': ['2026-01-15', '2026-02-20', 'Invalid Date', '2026-03-10', None],
        'Amount': [1500.50, 2300, 1800, 950, 1200],
        'Notes': ['', '', 'تم الشراء من المتجر', '', '']
    }
    
    df_custom = pd.DataFrame(custom_data)
    df_custom.to_csv('custom_data.csv', index=False)
    
    print("\n📊 البيانات الأصلية:")
    print(df_custom)
    
    # معالجة متقدمة
    engine = ComprehensiveFinalEngine(verbose=True)
    
    # تشخيص أولي
    print("\n🔍 تشخيص البيانات:")
    column_types = engine.detect_column_types(df_custom)
    print(f"\n   أنواع الأعمدة المكتشفة: {column_types}")
    
    # معالجة شاملة
    print("\n")
    processed_df = engine.process_comprehensive(
        input_path='custom_data.csv',
        output_path='example_4_output.xlsx'
    )
    
    print("\n📊 البيانات بعد المعالجة:")
    print(processed_df)
    
    # عرض السجلات
    print("\n📋 سجل العمليات:")
    for log_entry in engine.audit_log[-10:]:  # آخر 10 إدخالات
        print(f"   {log_entry}")
    
    return processed_df


# ============================================================================
# مثال 5: معالجة مع تحليل الجودة
# ============================================================================

def example_5_quality_analysis():
    """
    المثال الخامس: معالجة مع تحليل شامل لجودة البيانات
    """
    print("\n" + "=" * 80)
    print("📚 مثال 5: تحليل جودة البيانات (Data Quality Analysis)")
    print("=" * 80)
    
    # معالجة البيانات الأصلية
    engine = ComprehensiveFinalEngine(verbose=False)
    processed_df = engine.process_comprehensive(
        input_path='sample_data.csv',
        output_path='example_5_output.xlsx'
    )
    
    # تحليل الجودة
    print("\n📊 تحليل جودة البيانات:")
    print("-" * 80)
    
    # 1. نسبة الاكتمالية (Completeness)
    print("\n✓ نسبة الاكتمالية (Completeness):")
    for col in processed_df.columns:
        completeness = (1 - processed_df[col].isna().sum() / len(processed_df)) * 100
        print(f"   • {col}: {completeness:.1f}%")
    
    # 2. الصفوف المكررة
    print("\n✓ الصفوف المكررة:")
    duplicates = processed_df.duplicated().sum()
    print(f"   • عدد الصفوف المكررة: {duplicates}")
    
    # 3. توزيع البيانات
    print("\n✓ توزيع البيانات:")
    for col in processed_df.select_dtypes(include='number').columns:
        print(f"   • {col}:")
        print(f"       - الحد الأدنى: {processed_df[col].min()}")
        print(f"       - الحد الأقصى: {processed_df[col].max()}")
        print(f"       - المتوسط: {processed_df[col].mean():.2f}")
    
    # 4. أنواع البيانات
    print("\n✓ أنواع البيانات:")
    for col in processed_df.columns:
        print(f"   • {col}: {processed_df[col].dtype}")
    
    print("\n✅ تم إنشاء ملف التحليل: example_5_output.xlsx")
    
    return processed_df


# ============================================================================
# مثال 6: مقارنة قبل وبعد
# ============================================================================

def example_6_before_after_comparison():
    """
    المثال السادس: مقارنة شاملة بين البيانات قبل وبعد المعالجة
    """
    print("\n" + "=" * 80)
    print("📚 مثال 6: مقارنة قبل وبعد (Before & After Comparison)")
    print("=" * 80)
    
    # تحميل البيانات الأصلية
    df_before = pd.read_csv('sample_data.csv')
    
    print("\n📊 البيانات قبل المعالجة:")
    print("-" * 80)
    print(f"عدد الصفوف: {len(df_before)}")
    print(f"عدد الأعمدة: {len(df_before.columns)}")
    print(f"\n{df_before.info()}")
    
    # معالجة البيانات
    engine = ComprehensiveFinalEngine(verbose=False)
    df_after = engine.process_comprehensive(
        input_path='sample_data.csv',
        output_path='example_6_output.xlsx'
    )
    
    print("\n\n📊 البيانات بعد المعالجة:")
    print("-" * 80)
    print(f"عدد الصفوف: {len(df_after)}")
    print(f"عدد الأعمدة: {len(df_after.columns)}")
    print(f"\n{df_after.info()}")
    
    # إحصائيات الفروقات
    print("\n\n📈 الفروقات:")
    print("-" * 80)
    
    # الصفوف المحذوفة
    rows_removed = len(df_before) - len(df_after)
    print(f"✓ الصفوف المحذوفة: {rows_removed}")
    
    # الأعمدة المضافة
    cols_added = len(df_after.columns) - len(df_before.columns)
    print(f"✓ الأعمدة المضافة: {cols_added}")
    
    # الفراغات المسحوحة
    print(f"\n✓ الفراغات المسحوحة:")
    for col in df_before.columns:
        if col in df_after.columns:
            before_nulls = df_before[col].isna().sum()
            after_nulls = df_after[col].isna().sum()
            cleaned = before_nulls - after_nulls
            if cleaned > 0:
                print(f"   • {col}: {cleaned} خلية")
    
    print("\n✅ تم إنشاء ملف المقارنة: example_6_output.xlsx")
    
    return df_before, df_after


# ============================================================================
# دالة التشغيل الرئيسية
# ============================================================================

def run_all_examples():
    """
    تشغيل جميع الأمثلة
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "أمثلة محرك المعالجة الشامل" + " " * 33 + "║")
    print("║" + " " * 15 + "Comprehensive Processing Engine Examples" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # تشغيل الأمثلة
    try:
        # مثال 1
        print("\n\n🎬 تشغيل المثال 1...")
        example_1_basic_usage()
        
        # مثال 2
        print("\n\n🎬 تشغيل المثال 2...")
        example_2_messy_data()
        
        # مثال 3 (اختياري - قد يستغرق وقتاً)
        print("\n\n🎬 تشغيل المثال 3 (قد يستغرق وقتاً)...")
        user_input = input("هل تريد تشغيل اختبار البيانات الضخمة؟ (y/n): ").lower()
        if user_input == 'y':
            example_3_large_dataset()
        else:
            print("⏭️  تم تخطي المثال 3")
        
        # مثال 4
        print("\n\n🎬 تشغيل المثال 4...")
        example_4_custom_processing()
        
        # مثال 5
        print("\n\n🎬 تشغيل المثال 5...")
        example_5_quality_analysis()
        
        # مثال 6
        print("\n\n🎬 تشغيل المثال 6...")
        example_6_before_after_comparison()
        
        # الخلاصة
        print("\n\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "✅ انتهت جميع الأمثلة بنجاح" + " " * 28 + "║")
        print("╚" + "=" * 78 + "╝")
        print("\n📁 الملفات المُنشأة:")
        print("   1. example_1_output.xlsx / example_1_output_audit_report.txt")
        print("   2. example_2_output.xlsx / example_2_output_audit_report.txt")
        print("   3. example_3_output.xlsx / example_3_output_audit_report.txt (اختياري)")
        print("   4. example_4_output.xlsx / example_4_output_audit_report.txt")
        print("   5. example_5_output.xlsx / example_5_output_audit_report.txt")
        print("   6. example_6_output.xlsx / example_6_output_audit_report.txt")
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
