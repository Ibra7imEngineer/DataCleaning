"""
أمثلة عملية متقدمة لمحرك المعالجة الشامل
يتضمن حالات واقعية معقدة وتحديات عملية شائعة
"""

import pandas as pd
import numpy as np
from comprehensive_processing_engine import ComprehensiveProcessingEngine
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedProcessingExamples:
    """أمثلة متقدمة لاستخدام محرك المعالجة الشامل"""
    
    @staticmethod
    def example_1_mixed_data_types():
        """
        مثال 1️⃣: البيانات المختلطة (Mixed Data Types)
        ====================================================
        سيناريو: بيانات تم جمعها من مصادر متعددة بصيغ مختلفة
        التحديات:
        - أرقام مخزنة كنصوص
        - تواريخ بصيغ متعددة
        - نصوص مختلطة مع أرقام
        """
        print("\n" + "="*70)
        print("🔍 مثال 1: البيانات المختلطة من مصادر متعددة")
        print("="*70)
        
        # بيانات مختلطة ومعقدة
        data = {
            'Product_ID': ['P001', 'P002', 'غير متوفر', 'P004', '5', 'P006'],
            'Quantity': ['100', '250.5', '300.0', 'كمية غير محددة', '500', np.nan],
            'Unit_Price': [99.99, '150', 200, 'سعر مخفي', '350.50', 425],
            'Order_Date': [
                '2024-01-15',
                '2024-02-20 14:30:45',
                'يناير 15, 2024',
                '2024-04-10',
                '15/05/2024',
                None
            ],
            'Invoice_Date': [
                datetime(2024, 1, 15, 9, 30),
                '2024-02-20',
                '2024-03-15 08:45:30',
                '2024-04-10 23:59:59',
                'فاتورة معلقة',
                '2024-06-01'
            ],
            'Customer': [
                'أحمد محمد',
                'فاطمة علي',
                'محمد خليل',
                '12345',  # رقم بدلاً من اسم
                'سارة',
                'علي بن سلطان'
            ]
        }
        
        df = pd.DataFrame(data)
        print("\n📥 البيانات الخام (Raw Data):")
        print(df.to_string())
        
        # معالجة باستخدام المحرك
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Order_Date', 'Invoice_Date'],
            numeric_columns=['Product_ID', 'Quantity', 'Unit_Price']
        )
        
        result = engine.run_complete_pipeline(
            output_file='example_1_mixed_data.xlsx'
        )
        
        print("\n📤 البيانات المعالجة:")
        print(result['dataframe'].to_string())
        
        print("\n📋 الملاحظات المضافة:")
        notes = result['dataframe'][result['dataframe']['Notes'] != '']
        for idx, row in notes.iterrows():
            print(f"  صف {idx}: {row['Notes']}")
        
        print("\n📊 إحصائيات المعالجة:")
        audit = result['audit_report']['summary']
        print(f"  ✓ الخلايا المفحوصة: {audit['cells_checked']:,} من {audit['total_cells']:,}")
        print(f"  ✓ الخلايا المعدلة: {audit['cells_modified']}")
        print(f"  ✓ نقل للملاحظات: {audit['cells_moved_to_notes']}")
        print(f"  ✓ تحويلات النوع: {audit['type_conversions']}")
        print(f"  ✓ التواريخ المنظفة: {audit['date_sterilized']}")
        print(f"  ✓ نسبة الفحص: {audit['coverage_percentage']:.2f}%")
    
    @staticmethod
    def example_2_large_scale_data():
        """
        مثال 2️⃣: البيانات الضخمة (Large-Scale Data Performance)
        ====================================================
        سيناريو: معالجة 100,000 صف لاختبار الأداء
        التحديات:
        - سرعة المعالجة
        - استهلاك الذاكرة
        - ضمان فحص كل صف
        """
        print("\n" + "="*70)
        print("⚡ مثال 2: البيانات الضخمة واختبار الأداء")
        print("="*70)
        
        # إنشاء بيانات ضخمة (100,000 صف)
        n_rows = 100000
        
        print(f"\n🔨 إنشاء {n_rows:,} صف من البيانات...")
        
        np.random.seed(42)
        
        data = {
            'Transaction_ID': np.arange(1, n_rows + 1),
            'Amount': np.random.uniform(10, 5000, n_rows),
            'Commission': np.random.choice(['5.0', '10.0', 'مرتفعة', np.nan], n_rows),
            'Transaction_Date': [
                (datetime(2024, 1, 1) + timedelta(days=int(x))).strftime('%Y-%m-%d')
                if np.random.random() > 0.1 else
                (datetime(2024, 1, 1) + timedelta(days=int(x), hours=12, minutes=30)).isoformat()
                for x in np.random.uniform(0, 365, n_rows)
            ],
            'Completion_Date': [
                datetime(2024, 1, 1) + timedelta(days=int(x), hours=np.random.randint(0, 24))
                if np.random.random() > 0.05 else None
                for x in np.random.uniform(0, 365, n_rows)
            ]
        }
        
        df = pd.DataFrame(data)
        print(f"✓ تم إنشاء البيانات بنجاح")
        print(f"\nأول 5 صفوف:")
        print(df.head().to_string())
        
        # المعالجة
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Transaction_Date', 'Completion_Date'],
            numeric_columns=['Transaction_ID', 'Amount', 'Commission']
        )
        
        result = engine.run_complete_pipeline(
            output_file='example_2_large_scale.xlsx'
        )
        
        print(f"\n📊 نتائج المعالجة (من {n_rows:,} صف):")
        audit = result['audit_report']['summary']
        print(f"  ✓ الوقت المستغرق: {result['duration_seconds']:.2f} ثانية")
        print(f"  ✓ الخلايا المفحوصة: {audit['cells_checked']:,}")
        print(f"  ✓ الخلايا المعدلة: {audit['cells_modified']:,}")
        print(f"  ✓ الملاحظات المضافة: {audit['notes_added']}")
        print(f"  ✓ متوسط الوقت لكل صف: {(result['duration_seconds'] / n_rows) * 1000:.4f} ميلي ثانية")
    
    @staticmethod
    def example_3_complex_business_logic():
        """
        مثال 3️⃣: منطق العمل المعقد (Complex Business Logic)
        ====================================================
        سيناريو: معالجة بيانات مبيعات بقواعد عمل محددة
        التحديات:
        - التحقق من القيم المنطقية
        - كشف القيم الشاذة (Outliers)
        - التحقق من تماسك البيانات
        """
        print("\n" + "="*70)
        print("🏢 مثال 3: منطق العمل المعقد لبيانات المبيعات")
        print("="*70)
        
        data = {
            'Invoice_Number': ['INV001', 'INV002', 'INV003', 'مسودة', 'INV005', 'INV006'],
            'Quantity': [10, '50', '0', '100', '-5', 200],  # قيم غير منطقية
            'Unit_Price': [99.5, 150, 200, 'تحت المراجعة', 350.50, 425],
            'Total_Amount': [995, 7500, 0, 'تحت الحساب', -1752.5, 85000],
            'Discount_Percentage': [5, '10.5', 50.5, 'بدون خصم', '0', 15],
            'Final_Amount': [945.25, 6750, 0, '؟', -1752.5, 72250],
            'Sale_Date': [
                '2024-03-01',
                '2024-03-02 10:30:00',
                '2024-03-03',
                'تاريخ غير محدد بعد',
                '2024-03-05',
                '2024-03-06'
            ],
            'Customer_Since': [
                datetime(2020, 5, 15),
                '2019-08-20',
                '2021-12-01',
                'عميل جديد',
                '2018-01-10',
                datetime(2022, 6, 30)
            ]
        }
        
        df = pd.DataFrame(data)
        print("\n📥 بيانات المبيعات الخام:")
        print(df.to_string())
        
        # معالجة
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Sale_Date', 'Customer_Since'],
            numeric_columns=['Quantity', 'Unit_Price', 'Total_Amount', 
                           'Discount_Percentage', 'Final_Amount']
        )
        
        result = engine.run_complete_pipeline(
            output_file='example_3_business_logic.xlsx'
        )
        
        print("\n📤 البيانات المعالجة:")
        print(result['dataframe'].to_string())
        
        # تحليل القيم الشاذة
        print("\n⚠️  كشف القيم غير المنطقية:")
        for idx, violation in enumerate(result['audit_report']['type_violations'], 1):
            print(f"  {idx}. الصف {violation['row']}, العمود '{violation['column']}':")
            print(f"     القيمة المتوقعة: {violation['expected_type']}")
            print(f"     القيمة الفعلية: {violation['actual_value']}")
            print(f"     الإجراء المتخذ: {violation['action']}")
    
    @staticmethod
    def example_4_data_quality_audit():
        """
        مثال 4️⃣: مراجعة جودة البيانات (Data Quality Audit)
        ====================================================
        سيناريو: مراجعة شاملة لجودة البيانات
        التحديات:
        - إنشاء تقرير مفصل
        - توثيق جميع التغييرات
        - تقييم مستوى جودة البيانات
        """
        print("\n" + "="*70)
        print("📈 مثال 4: مراجعة شاملة لجودة البيانات")
        print("="*70)
        
        # بيانات بجودة متوسطة
        data = {
            'Employee_ID': ['E001', 'E002', 'موظف جديد', 'E004', '5', 'E006'],
            'Salary': [50000, '60000.0', '70000', 'قيد المراجعة', 85000, np.nan],
            'Department': ['IT', 'HR', 'IT', 'Finance', 'IT', 'HR'],
            'Hire_Date': [
                '2020-01-15',
                '2021-03-20',
                '01/15/2022',
                'تاريخ قديم',
                '2023-07-10',
                datetime(2024, 2, 1)
            ],
            'Last_Review': [
                datetime(2024, 1, 15, 9, 30),
                '2024-02-20',
                None,
                '2024-03-15 18:45:30',
                'تحت الانتظار',
                '2024-04-01'
            ],
            'Performance_Score': [
                8.5,
                '9.0',
                10,
                'ممتاز',
                '7.5',
                None
            ]
        }
        
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Hire_Date', 'Last_Review'],
            numeric_columns=['Employee_ID', 'Salary', 'Performance_Score']
        )
        
        result = engine.run_complete_pipeline(
            output_file='example_4_audit_report.xlsx'
        )
        
        # تقرير مفصل
        print("\n📊 تقرير جودة البيانات:")
        audit = result['audit_report']['summary']
        
        total_cells = audit['total_cells']
        checked_cells = audit['cells_checked']
        modified_cells = audit['cells_modified']
        quality_score = (checked_cells / total_cells * 100) if total_cells > 0 else 0
        
        print(f"\n  📈 إحصائيات عامة:")
        print(f"     • إجمالي الخلايا: {total_cells:,}")
        print(f"     • الخلايا المفحوصة: {checked_cells:,} ({quality_score:.1f}%)")
        print(f"     • الخلايا المعدلة: {modified_cells:,} ({(modified_cells/total_cells*100):.1f}%)")
        
        print(f"\n  🔄 تحويلات البيانات:")
        print(f"     • تحويلات النوع: {audit['type_conversions']}")
        print(f"     • الخلايا المنقولة للملاحظات: {audit['cells_moved_to_notes']}")
        print(f"     • التواريخ المنظفة: {audit['date_sterilized']}")
        
        print(f"\n  ⚠️  انتهاكات النوع: {len(result['audit_report']['type_violations'])}")
        print(f"  🔀 الترحيل المكتشف: {len(result['audit_report']['data_shifts'])}")
        
        # درجة الجودة الكلية
        quality_grade = "ممتاز ⭐⭐⭐⭐⭐" if quality_score >= 95 else \
                       "جيد جداً ⭐⭐⭐⭐" if quality_score >= 85 else \
                       "جيد ⭐⭐⭐" if quality_score >= 70 else \
                       "متوسط ⭐⭐" if quality_score >= 50 else "ضعيف ⭐"
        
        print(f"\n  🎯 درجة الجودة الكلية: {quality_grade}")


def run_all_examples():
    """تشغيل جميع الأمثلة"""
    print("\n" + "#" * 70)
    print("# محرك المعالجة الشامل - أمثلة عملية متقدمة")
    print("#" * 70)
    
    examples = AdvancedProcessingExamples()
    
    try:
        # تشغيل الأمثلة
        examples.example_1_mixed_data_types()
        examples.example_2_large_scale_data()
        examples.example_3_complex_business_logic()
        examples.example_4_data_quality_audit()
        
        print("\n" + "="*70)
        print("✅ تم إكمال جميع الأمثلة بنجاح!")
        print("="*70)
        print("\n📁 الملفات المُنتجة:")
        print("  • example_1_mixed_data.xlsx")
        print("  • example_2_large_scale.xlsx")
        print("  • example_3_business_logic.xlsx")
        print("  • example_4_audit_report.xlsx")
        
    except Exception as e:
        logger.error(f"❌ حدث خطأ: {str(e)}")
        raise


if __name__ == "__main__":
    run_all_examples()
