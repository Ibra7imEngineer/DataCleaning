"""
دليل البدء السريع - استخدام محرك المعالجة الشاملة
Quick Start Guide - Comprehensive Processing Engine

اتبع هذه الخطوات البسيطة للبدء فوراً!
"""

import pandas as pd
import numpy as np
from comprehensive_processing_engine import ComprehensiveProcessingEngine
from datetime import datetime


def quick_start_example_1():
    """
    🚀 البدء السريع 1: معالجة بسيطة
    Simple Processing - Transform your data in 3 lines!
    """
    print("\n" + "="*70)
    print("🚀 البدء السريع 1: معالجة بسيطة")
    print("="*70)
    
    # ✅ الخطوة 1: تحميل البيانات
    data = {
        'ID': ['1.0', '2.0', '3.0'],
        'Amount': [100.5, 200, 'غير متوفر'],
        'Date': ['2024-01-15', '2024-02-20 14:30', 'تاريخ قديم']
    }
    df = pd.DataFrame(data)
    print("\n📥 البيانات الخام:")
    print(df)
    
    # ✅ الخطوة 2: إنشاء المحرك
    engine = ComprehensiveProcessingEngine(
        df=df,
        date_columns=['Date'],
        numeric_columns=['ID', 'Amount']
    )
    
    # ✅ الخطوة 3: المعالجة والتصدير
    result = engine.run_complete_pipeline(output_file='output_simple.xlsx')
    
    # 📤 النتائج
    print("\n📤 البيانات المعالجة:")
    print(result['dataframe'])
    
    print(f"\n✅ تم إنشاء: output_simple.xlsx")
    print(f"✓ الخلايا المفحوصة: {result['audit_report']['summary']['cells_checked']}")
    print(f"✓ الخلايا المعدلة: {result['audit_report']['summary']['cells_modified']}")


def quick_start_example_2():
    """
    🚀 البدء السريع 2: معالجة متقدمة مع تقرير شامل
    Advanced Processing - Complete Audit Trail
    """
    print("\n" + "="*70)
    print("🚀 البدء السريع 2: معالجة متقدمة")
    print("="*70)
    
    # إنشاء بيانات حقيقية أكثر تعقيداً
    data = {
        'Employee_ID': ['E001', 'E002', 'موظف جديد', 'E004'],
        'Department': ['IT', 'HR', 'Finance', 'IT'],
        'Salary': [50000, '60000.0', 'قيد المراجعة', 85000],
        'Hire_Date': ['2020-01-15', '2021-03-20 09:30', 'تاريخ قديم', '2023-07-10'],
        'Performance_Score': [8.5, '9.0', 10.0, 'ممتاز']
    }
    
    df = pd.DataFrame(data)
    print("\n📥 بيانات الموظفين:")
    print(df)
    
    # إنشاء المحرك مع كل الأعمدة
    engine = ComprehensiveProcessingEngine(
        df=df,
        date_columns=['Hire_Date'],
        numeric_columns=['Employee_ID', 'Salary', 'Performance_Score']
    )
    
    # المعالجة
    result = engine.run_complete_pipeline(output_file='output_advanced.xlsx')
    
    # عرض النتائج
    print("\n📤 البيانات المعالجة:")
    print(result['dataframe'])
    
    # عرض التقرير
    print("\n📊 التقرير الشامل:")
    audit = result['audit_report']['summary']
    print(f"  • الخلايا المفحوصة: {audit['cells_checked']:,}")
    print(f"  • الخلايا المعدلة: {audit['cells_modified']}")
    print(f"  • الملاحظات المضافة: {audit['notes_added']}")
    print(f"  • تحويلات النوع: {audit['type_conversions']}")
    print(f"  • نسبة الفحص: {audit['coverage_percentage']:.1f}%")
    
    # عرض الانتهاكات
    if result['audit_report']['type_violations']:
        print(f"\n⚠️  انتهاكات النوع ({len(result['audit_report']['type_violations'])}):")
        for v in result['audit_report']['type_violations']:
            print(f"  • الصف {v['row']}, العمود '{v['column']}': {v['actual_value']}")


def quick_start_example_3():
    """
    🚀 البدء السريع 3: معالجة مباشرة بدون ملف
    Direct Processing - No file needed
    """
    print("\n" + "="*70)
    print("🚀 البدء السريع 3: معالجة مباشرة")
    print("="*70)
    
    # بيانات بسيطة
    data = {
        'Product': ['Laptop', 'Mouse', 'Monitor'],
        'Price': ['999.99', '50.0', 'غير محدد'],
        'Stock': [10, '5', 0],
        'Updated': ['2024-01-15', '2024-02-20 14:30', '2024-03-10']
    }
    
    df = pd.DataFrame(data)
    
    # معالجة بدون تصدير
    engine = ComprehensiveProcessingEngine(
        df=df,
        numeric_columns=['Price', 'Stock'],
        date_columns=['Updated']
    )
    
    result = engine.run_complete_pipeline()  # بدون output_file
    
    # الحصول على البيانات المعالجة
    processed = result['dataframe']
    print("\n✓ تم المعالجة في الذاكرة فقط (بدون ملف)")
    print(processed)
    
    # يمكن حفظها لاحقاً
    processed.to_csv('output_direct.csv', index=False)
    print("\n✅ تم حفظ البيانات في: output_direct.csv")


def quick_start_example_4():
    """
    🚀 البدء السريع 4: معالجة ملف CSV حقيقي
    Real CSV File Processing
    """
    print("\n" + "="*70)
    print("🚀 البدء السريع 4: معالجة ملف CSV")
    print("="*70)
    
    # قراءة الملف
    try:
        df = pd.read_csv('sample_data.csv')
        print(f"\n📥 تم قراءة الملف: sample_data.csv")
        print(f"البيانات: {len(df)} صف × {len(df.columns)} عمود")
        print("\nأول 5 صفوف:")
        print(df.head())
        
        # تحديد أنواع الأعمدة (يجب تعديله حسب بيانتك)
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'Date' in col]
        numeric_cols = [col for col in df.columns if df[col].dtype in ['int64', 'float64']]
        
        print(f"\n🔍 الأعمدة المكتشفة:")
        print(f"  • أعمدة التاريخ: {date_cols}")
        print(f"  • الأعمدة الرقمية: {numeric_cols}")
        
        # المعالجة
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=date_cols,
            numeric_columns=numeric_cols
        )
        
        result = engine.run_complete_pipeline(output_file='sample_processed.xlsx')
        
        print(f"\n✅ تم المعالجة بنجاح!")
        print(f"⏱️  المدة: {result['duration_seconds']:.2f} ثانية")
        print(f"📊 الملف الناتج: sample_processed.xlsx")
        
    except FileNotFoundError:
        print("❌ الملف 'sample_data.csv' غير موجود")
        print("💡 تلميح: أنشئ ملف CSV أولاً")


def quick_start_template():
    """
    📝 قالب للاستخدام الخاص بك
    Your Template - Copy & Modify
    """
    print("\n" + "="*70)
    print("📝 القالب - يمكنك نسخه وتعديله")
    print("="*70)
    
    template_code = '''
# ======================================
# قالب - Copy & Modify
# ======================================

import pandas as pd
from comprehensive_processing_engine import ComprehensiveProcessingEngine

# 1️⃣ تحميل البيانات
df = pd.read_csv('your_file.csv')
# أو:
# df = pd.read_excel('your_file.xlsx')

# 2️⃣ تحديد الأعمدة
date_columns = ['Order_Date', 'Ship_Date']  # اتركها فارغة إذا لم تكن هناك
numeric_columns = ['Product_ID', 'Quantity', 'Price']  # اتركها فارغة إذا لم تكن هناك

# 3️⃣ إنشاء المحرك
engine = ComprehensiveProcessingEngine(
    df=df,
    date_columns=date_columns,
    numeric_columns=numeric_columns
)

# 4️⃣ المعالجة
result = engine.run_complete_pipeline(
    output_file='processed_output.xlsx'
)

# 5️⃣ الحصول على النتائج
processed_df = result['dataframe']
audit_report = result['audit_report']

# 6️⃣ عرض النتائج
print(processed_df)
print(f"الخلايا المفحوصة: {audit_report['summary']['cells_checked']}")
print(f"الملاحظات المضافة: {audit_report['summary']['notes_added']}")
    '''
    
    print(template_code)
    
    # حفظ القالب
    with open('TEMPLATE.py', 'w', encoding='utf-8') as f:
        f.write(template_code)
    print("\n✅ تم حفظ القالب في: TEMPLATE.py")


def show_tips_and_tricks():
    """
    💡 نصائح وحيل مفيدة
    Tips & Tricks
    """
    print("\n" + "="*70)
    print("💡 نصائح وحيل مفيدة")
    print("="*70)
    
    tips = """
    1️⃣ تحديد الأعمدة تلقائياً:
    ──────────────────────────────
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    2️⃣ عرض الملاحظات المضافة:
    ──────────────────────────────
    notes_df = result['dataframe'][result['dataframe']['Notes'] != '']
    print(notes_df[['Notes']])
    
    3️⃣ حفظ البيانات بطرق مختلفة:
    ──────────────────────────────
    result['dataframe'].to_csv('output.csv', index=False)
    result['dataframe'].to_excel('output.xlsx', index=False)
    result['dataframe'].to_parquet('output.parquet')
    
    4️⃣ معالجة ملايين الصفوف:
    ──────────────────────────────
    # استخدم نفس الطريقة، المحرك محسّن للأداء
    df_large = pd.read_csv('huge_file.csv', chunksize=50000)
    for chunk in df_large:
        engine = ComprehensiveProcessingEngine(chunk, ...)
        result = engine.run_complete_pipeline()
    
    5️⃣ إعادة المحاولة مع تعديل الإعدادات:
    ──────────────────────────────
    # إذا لم تكن النتائج مرضية، عدّل تحديد الأعمدة وحاول مجدداً
    date_columns = ['col1', 'col2']
    numeric_columns = ['col3']
    
    6️⃣ دمج التقارير من عمليات متعددة:
    ──────────────────────────────
    all_violations = []
    for file in files_list:
        result = engine.run_complete_pipeline()
        all_violations.extend(result['audit_report']['type_violations'])
    
    7️⃣ تصفية البيانات بناءً على الملاحظات:
    ──────────────────────────────
    problematic_rows = result['dataframe'][result['dataframe']['Notes'] != '']
    clean_rows = result['dataframe'][result['dataframe']['Notes'] == '']
    
    8️⃣ حفظ التقرير كـ JSON:
    ──────────────────────────────
    import json
    with open('audit_report.json', 'w', encoding='utf-8') as f:
        json.dump(result['audit_report'], f, ensure_ascii=False, indent=2)
    """
    
    print(tips)


def main():
    """الدالة الرئيسية"""
    print("\n" + "#" * 70)
    print("# 🚀 دليل البدء السريع - محرك المعالجة الشاملة")
    print("# Comprehensive Processing Engine - Quick Start Guide")
    print("#" * 70)
    
    print("\n📌 الخيارات المتاحة:")
    print("  1. البدء السريع 1: معالجة بسيطة")
    print("  2. البدء السريع 2: معالجة متقدمة")
    print("  3. البدء السريع 3: معالجة مباشرة")
    print("  4. البدء السريع 4: معالجة ملف CSV")
    print("  5. عرض القالب")
    print("  6. نصائح وحيل")
    print("  7. تشغيل الكل")
    print("  0. خروج")
    
    choice = input("\nاختر رقماً (1-7، أو 0 للخروج): ").strip()
    
    if choice == '1':
        quick_start_example_1()
    elif choice == '2':
        quick_start_example_2()
    elif choice == '3':
        quick_start_example_3()
    elif choice == '4':
        quick_start_example_4()
    elif choice == '5':
        quick_start_template()
    elif choice == '6':
        show_tips_and_tricks()
    elif choice == '7':
        quick_start_example_1()
        quick_start_example_2()
        quick_start_example_3()
        quick_start_template()
        show_tips_and_tricks()
    elif choice == '0':
        print("👋 إلى اللقاء!")
        return
    else:
        print("❌ اختيار غير صحيح")
        return
    
    print("\n" + "="*70)
    print("✅ انتهى - شكراً لاستخدام محرك المعالجة الشاملة!")
    print("="*70 + "\n")


if __name__ == "__main__":
    # تشغيل المثال الأول تلقائياً عند الاستيراد
    quick_start_example_1()
    quick_start_example_2()
    quick_start_example_3()
    
    # يمكن تشغيل القائمة التفاعلية بـ:
    # main()
