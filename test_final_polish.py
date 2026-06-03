"""
اختبارات شاملة لدالة final_polish
==================================
التحقق من جميع الوظائف والحالات الخاصة

Author: Testing Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
import pytest
from final_polish import final_polish


class TestFinalPolish:
    """مجموعة الاختبارات الشاملة"""
    
    def test_date_column_cleaning(self):
        """اختبار تنظيف أعمدة التاريخ"""
        df = pd.DataFrame({
            'OrderDate': [
                '2024-01-15',
                '2024-02-20 14:30:00',
                '2024-03-10 00:00:00',
                None
            ]
        })
        
        clean_df, _ = final_polish(df, date_columns=['OrderDate'], verbose=False)
        
        # التحقق من النتائج
        assert clean_df['OrderDate'].iloc[0] == date(2024, 1, 15)
        assert clean_df['OrderDate'].iloc[1] == date(2024, 2, 20)
        assert clean_df['OrderDate'].iloc[2] == date(2024, 3, 10)
        assert pd.isna(clean_df['OrderDate'].iloc[3])
        
        print("✓ اختبار تنظيف التواريخ نجح")
    
    def test_numeric_int_conversion(self):
        """اختبار تحويل الأرقام الصحيحة لـ Int64"""
        df = pd.DataFrame({
            'ProductID': [1.0, 2.0, 3.0, None, 5.0]
        })
        
        clean_df, _ = final_polish(df, numeric_columns=['ProductID'], verbose=False)
        
        # التحقق من النوع
        assert clean_df['ProductID'].dtype == 'Int64'
        
        # التحقق من القيم
        assert clean_df['ProductID'].iloc[0] == 1
        assert clean_df['ProductID'].iloc[1] == 2
        assert pd.isna(clean_df['ProductID'].iloc[3])
        
        print("✓ اختبار تحويل الأرقام نجح")
    
    def test_text_in_date_column(self):
        """اختبار كشف النصوص في أعمدة التاريخ"""
        df = pd.DataFrame({
            'OrderDate': [
                '2024-01-15',
                'تاريخ غير محدد',
                '2024-03-10',
                'unknown'
            ]
        })
        
        clean_df, report = final_polish(
            df,
            date_columns=['OrderDate'],
            verbose=False
        )
        
        # التحقق من وجود ملاحظات
        assert report['system_notes_added'] > 0
        assert clean_df['System_Notes'].iloc[1] != ''
        
        print("✓ اختبار كشف النصوص في التواريخ نجح")
    
    def test_duplicate_columns_removal(self):
        """اختبار حذف الأعمدة المتطابقة"""
        df = pd.DataFrame({
            'ProductID': [1, 2, 3],
            'ProductID_Copy': [1, 2, 3],
            'Name': ['A', 'B', 'C']
        })
        
        clean_df, report = final_polish(df, verbose=False)
        
        # التحقق من حذف العمود
        assert report['duplicate_columns_removed'] == 1
        assert clean_df.shape[1] == 2
        assert 'ProductID_Copy' not in clean_df.columns
        
        print("✓ اختبار حذف الأعمدة المتطابقة نجح")
    
    def test_empty_cell_standardization(self):
        """اختبار توحيد الخلايا الفارغة"""
        df = pd.DataFrame({
            'Quantity': [100, 'N/A', 'غير محدد', np.nan, 500],
            'Name': ['أحمد', '', 'محمد', 'علي', 'فاطمة']
        })
        
        clean_df, _ = final_polish(
            df,
            numeric_columns=['Quantity'],
            verbose=False
        )
        
        # في الأعمدة الرقمية: N/A يصبح NaN
        assert pd.isna(clean_df['Quantity'].iloc[1])
        assert pd.isna(clean_df['Quantity'].iloc[2])
        
        print("✓ اختبار توحيد الخلايا الفارغة نجح")
    
    def test_auto_detection(self):
        """اختبار الكشف التلقائي للأعمدة"""
        df = pd.DataFrame({
            'UserID': [1.0, 2.0, 3.0],
            'OrderDate': ['2024-01-15', '2024-02-20', '2024-03-10'],
            'Amount': [100.5, 200.0, 300.25],
            'Name': ['أحمد', 'فاطمة', 'محمد']
        })
        
        # بدون تحديد الأعمدة
        clean_df, report = final_polish(df, verbose=False)
        
        # يجب أن تُعالج جميع الأعمدة المناسبة
        assert report['date_columns_cleaned'] >= 1
        assert report['numeric_columns_converted'] >= 2
        
        print("✓ اختبار الكشف التلقائي نجح")
    
    def test_large_dataset_performance(self):
        """اختبار الأداء مع بيانات كبيرة"""
        # إنشاء مليون صف
        n_rows = 1_000_000
        
        df = pd.DataFrame({
            'ID': np.arange(1, n_rows + 1).astype(float),
            'Date': pd.date_range('2024-01-01', periods=n_rows),
            'Value': np.random.rand(n_rows)
        })
        
        # المعالجة
        import time
        start = time.time()
        clean_df, report = final_polish(
            df,
            date_columns=['Date'],
            numeric_columns=['ID', 'Value'],
            verbose=False
        )
        duration = time.time() - start
        
        # التحقق من السرعة (يجب أن تكون أقل من 30 ثانية)
        assert duration < 30
        assert len(clean_df) == n_rows
        
        print(f"✓ اختبار الأداء نجح: {n_rows:,} صف في {duration:.2f} ثانية")
    
    def test_mixed_data_types(self):
        """اختبار مع بيانات مختلطة"""
        df = pd.DataFrame({
            'ID': ['1.0', '2.0', '3', 'text'],
            'OrderDate': [
                '2024-01-15',
                '2024-02-20 10:30',
                'invalid date',
                None
            ],
            'Amount': [100.5, '200.0', 'N/A', 400]
        })
        
        clean_df, report = final_polish(
            df,
            date_columns=['OrderDate'],
            numeric_columns=['ID', 'Amount'],
            verbose=False
        )
        
        # يجب أن تُعالج البيانات بدون أخطاء
        assert len(clean_df) == len(df)
        assert report['date_columns_cleaned'] > 0
        
        print("✓ اختبار البيانات المختلطة نجح")
    
    def test_all_null_values(self):
        """اختبار مع قيم فارغة فقط"""
        df = pd.DataFrame({
            'Col1': [None, None, None],
            'Col2': [np.nan, np.nan, np.nan],
            'Col3': ['', '', '']
        })
        
        clean_df, _ = final_polish(df, verbose=False)
        
        # يجب أن تبقى البيانات الفارغة فارغة
        assert clean_df['Col1'].isna().all()
        assert clean_df['Col2'].isna().all()
        
        print("✓ اختبار القيم الفارغة نجح")
    
    def test_report_structure(self):
        """اختبار بنية التقرير"""
        df = pd.DataFrame({
            'ID': [1.0, 2.0, 3.0],
            'Date': ['2024-01-15', '2024-02-20', '2024-03-10']
        })
        
        _, report = final_polish(
            df,
            date_columns=['Date'],
            numeric_columns=['ID'],
            verbose=False
        )
        
        # التحقق من وجود جميع الحقول
        required_keys = [
            'original_rows', 'original_columns', 'final_rows',
            'final_columns', 'operations', 'warnings'
        ]
        
        for key in required_keys:
            assert key in report
        
        print("✓ اختبار بنية التقرير نجح")


def run_all_tests():
    """تشغيل جميع الاختبارات"""
    
    print("=" * 70)
    print("🧪 تشغيل اختبارات final_polish الشاملة")
    print("=" * 70 + "\n")
    
    test_suite = TestFinalPolish()
    
    tests = [
        ('تنظيف التواريخ', test_suite.test_date_column_cleaning),
        ('تحويل الأرقام', test_suite.test_numeric_int_conversion),
        ('كشف النصوص في التواريخ', test_suite.test_text_in_date_column),
        ('حذف الأعمدة المتطابقة', test_suite.test_duplicate_columns_removal),
        ('توحيد الخلايا الفارغة', test_suite.test_empty_cell_standardization),
        ('الكشف التلقائي', test_suite.test_auto_detection),
        ('الأداء مع بيانات ضخمة', test_suite.test_large_dataset_performance),
        ('البيانات المختلطة', test_suite.test_mixed_data_types),
        ('القيم الفارغة', test_suite.test_all_null_values),
        ('بنية التقرير', test_suite.test_report_structure),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 {test_name}...")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ فشل: {e}")
            failed += 1
    
    # ملخص النتائج
    print("\n" + "=" * 70)
    print("📊 ملخص الاختبارات")
    print("=" * 70)
    print(f"✅ نجح: {passed}/{len(tests)}")
    print(f"❌ فشل: {failed}/{len(tests)}")
    print("=" * 70 + "\n")
    
    if failed == 0:
        print("🎉 جميع الاختبارات نجحت!")
        return True
    else:
        print(f"⚠️  {failed} اختبار فشل")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
