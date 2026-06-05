"""
اختبارات شاملة لمحرك المعالجة الشامل
Testing Suite for Comprehensive Processing Engine
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from comprehensive_processing_engine import ComprehensiveProcessingEngine
import tempfile
import os


class TestComprehensiveProcessingEngine(unittest.TestCase):
    """مجموعة الاختبارات الشاملة"""
    
    def setUp(self):
        """تحضير البيانات قبل كل اختبار"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """تنظيف الملفات المؤقتة"""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    # ============================================================
    # اختبارات معالجة الأعمدة الرقمية
    # ============================================================
    
    def test_numeric_integer_conversion(self):
        """اختبار تحويل الأرقام الصحيحة إلى Int64"""
        data = {'ID': ['1.0', '2.0', '3.0']}
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['ID']
        )
        engine.process_numeric_columns()
        
        # التحقق من التحويل
        self.assertTrue(all(isinstance(x, (int, np.integer)) for x in engine.df['ID'].dropna()))
        self.assertEqual(engine.df['ID'].dtype, 'Int64')
    
    def test_numeric_text_detection(self):
        """اختبار كشف النصوص في الأعمدة الرقمية"""
        data = {'Price': [100.0, 'غير متوفر', 300.0]}
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['Price']
        )
        engine.process_numeric_columns()
        
        # التحقق من نقل النص للملاحظات
        self.assertTrue(pd.isna(engine.df.loc[1, 'Price']))
        self.assertIn('غير متوفر', engine.df.loc[1, 'Notes'])
        self.assertEqual(engine.stats['cells_moved_to_notes'], 1)
    
    def test_numeric_float_preservation(self):
        """اختبار الحفاظ على الأرقام العشرية"""
        data = {'Amount': [10.5, 20.75, 30.25]}
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['Amount']
        )
        engine.process_numeric_columns()
        
        # التحقق من الحفاظ على الكسور العشرية
        self.assertAlmostEqual(engine.df.loc[0, 'Amount'], 10.5)
        self.assertAlmostEqual(engine.df.loc[1, 'Amount'], 20.75)
    
    def test_numeric_null_handling(self):
        """اختبار التعامل مع القيم الفارغة"""
        data = {'Quantity': [10, None, np.nan, 40]}
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['Quantity']
        )
        engine.process_numeric_columns()
        
        # التحقق من بقاء القيم الفارغة
        self.assertTrue(pd.isna(engine.df.loc[1, 'Quantity']))
        self.assertTrue(pd.isna(engine.df.loc[2, 'Quantity']))
    
    # ============================================================
    # اختبارات معالجة أعمدة التاريخ
    # ============================================================
    
    def test_date_sterilization(self):
        """اختبار تنظيف أصفار الوقت من التواريخ"""
        data = {'Order_Date': ['2024-01-15 14:30:00', '2024-02-20 00:00:00']}
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Order_Date']
        )
        engine.process_date_columns()
        
        # التحقق من إزالة الوقت
        result = engine.df['Order_Date'].iloc[0]
        self.assertIsInstance(result, date)
        self.assertEqual(result, date(2024, 1, 15))
    
    def test_date_text_detection(self):
        """اختبار كشف النصوص في أعمدة التاريخ"""
        data = {'Date': ['2024-01-15', 'تاريخ غير محدد', '2024-03-20']}
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Date']
        )
        engine.process_date_columns()
        
        # التحقق من نقل النص
        self.assertIsNone(engine.df.loc[1, 'Date'])
        self.assertIn('تاريخ غير محدد', engine.df.loc[1, 'Notes'])
        self.assertEqual(engine.stats['cells_moved_to_notes'], 1)
    
    def test_date_multiple_formats(self):
        """اختبار تحويل تواريخ بصيغ مختلفة"""
        data = {'Date': [
            '2024-01-15',
            '01/15/2024',
            '15-01-2024',
            datetime(2024, 2, 20),
            '2024-03-15 10:30:45'
        ]}
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Date']
        )
        engine.process_date_columns()
        
        # التحقق من التحويل الناجح
        successful_dates = engine.df['Date'].dropna()
        self.assertEqual(len(successful_dates), 5)
    
    def test_date_null_handling(self):
        """اختبار التعامل مع القيم الفارغة في التواريخ"""
        data = {'Date': ['2024-01-15', None, np.nan, '2024-04-20']}
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Date']
        )
        engine.process_date_columns()
        
        # التحقق من بقاء القيم الفارغة
        self.assertIsNone(engine.df.loc[1, 'Date'])
        self.assertIsNone(engine.df.loc[2, 'Date'])
    
    # ============================================================
    # اختبارات الفحص الشامل
    # ============================================================
    
    def test_row_by_row_integrity(self):
        """اختبار فحص كل صف بشكل مستقل"""
        data = {
            'ID': ['1', '2', '3', '4', '5'],
            'Value': [100, 200, 'N/A', 400, 500],
            'Date': ['2024-01-01', '2024-01-02', 'N/A', '2024-01-04', '2024-01-05']
        }
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['ID', 'Value'],
            date_columns=['Date']
        )
        engine.run_complete_pipeline()
        
        # التحقق من فحص جميع الصفوف
        # إجمالي الخلايا = 5 صفوف × 3 أعمدة = 15
        self.assertEqual(engine.stats['total_rows'], 5)
        self.assertGreater(engine.stats['cells_checked'], 0)
    
    def test_audit_log_creation(self):
        """اختبار إنشاء سجل العمليات"""
        data = {
            'ID': ['1.0', '2.0'],
            'Date': ['2024-01-15 10:30', '2024-01-16']
        }
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['ID'],
            date_columns=['Date']
        )
        result = engine.run_complete_pipeline()
        
        # التحقق من وجود السجل
        audit_report = result['audit_report']
        self.assertIn('summary', audit_report)
        self.assertIn('operations_log', audit_report)
        self.assertGreater(len(audit_report['operations_log']), 0)
    
    def test_data_shifting_detection(self):
        """اختبار كشف الترحيل العشوائي"""
        data = {
            'Col1': ['A', 'B', 'C'],
            'Col2': ['X', 'Y', 'Z']
        }
        df = pd.DataFrame(data)
        
        # تعديل القيم بدون توثيق
        engine = ComprehensiveProcessingEngine(df=df)
        engine.df.loc[0, 'Col1'] = 'Modified'  # تغيير غير متوقع
        
        engine.detect_data_shifting()
        
        # التحقق من كشف التغيير
        self.assertGreater(len(engine.data_shift_log), 0)
    
    # ============================================================
    # اختبارات الأداء
    # ============================================================
    
    def test_performance_large_dataset(self):
        """اختبار الأداء مع البيانات الكبيرة"""
        n_rows = 10000
        
        data = {
            'ID': np.arange(1, n_rows + 1),
            'Value': np.random.uniform(10, 1000, n_rows),
            'Date': pd.date_range('2024-01-01', periods=n_rows)
        }
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['ID', 'Value'],
            date_columns=['Date']
        )
        
        result = engine.run_complete_pipeline()
        
        # التحقق من الأداء (يجب أن تكون سريعة)
        self.assertLess(result['duration_seconds'], 30)  # أقل من 30 ثانية
        print(f"⏱️  معالجة {n_rows} صف في {result['duration_seconds']:.2f} ثانية")
    
    def test_coverage_percentage(self):
        """اختبار نسبة الفحص الشاملة"""
        data = {
            'A': [1, 2, 3],
            'B': [4, 5, 6],
            'C': [7, 8, 9]
        }
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['A', 'B', 'C']
        )
        result = engine.run_complete_pipeline()
        
        # يجب فحص جميع الخلايا
        coverage = result['audit_report']['summary']['coverage_percentage']
        self.assertEqual(coverage, 100.0)
    
    # ============================================================
    # اختبارات التصدير
    # ============================================================
    
    def test_excel_export(self):
        """اختبار التصدير لـ Excel"""
        data = {
            'ID': ['1.0', '2.0'],
            'Name': ['أحمد', 'فاطمة'],
            'Date': ['2024-01-15', '2024-01-16']
        }
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['ID'],
            date_columns=['Date']
        )
        
        output_file = os.path.join(self.temp_dir, 'test_export.xlsx')
        engine.run_complete_pipeline(output_file=output_file)
        
        # التحقق من إنشاء الملف
        self.assertTrue(os.path.exists(output_file))
        
        # التحقق من قراءة الملف
        loaded_df = pd.read_excel(output_file, sheet_name='Data')
        self.assertEqual(len(loaded_df), 2)
    
    def test_audit_sheet_creation(self):
        """اختبار إنشاء ورقة السجل"""
        data = {
            'ID': ['1.0', '2.0'],
            'Value': [100, 'N/A']
        }
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['ID', 'Value']
        )
        
        output_file = os.path.join(self.temp_dir, 'test_audit.xlsx')
        engine.run_complete_pipeline(output_file=output_file)
        
        # التحقق من وجود ورقة السجل
        xl_file = pd.ExcelFile(output_file)
        self.assertIn('Audit Report', xl_file.sheet_names)
    
    # ============================================================
    # اختبارات الحالات الخاصة
    # ============================================================
    
    def test_empty_dataframe(self):
        """اختبار مع DataFrame فارغ"""
        df = pd.DataFrame()
        
        engine = ComprehensiveProcessingEngine(df=df)
        result = engine.run_complete_pipeline()
        
        # يجب أن تعمل بدون أخطاء
        self.assertEqual(len(result['dataframe']), 0)
    
    def test_single_row(self):
        """اختبار مع صف واحد"""
        data = {'ID': [1], 'Name': ['أحمد'], 'Date': ['2024-01-15']}
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['ID'],
            date_columns=['Date']
        )
        result = engine.run_complete_pipeline()
        
        self.assertEqual(len(result['dataframe']), 1)
    
    def test_all_null_values(self):
        """اختبار مع قيم فارغة فقط"""
        data = {
            'ID': [None, None, None],
            'Value': [np.nan, np.nan, np.nan]
        }
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['ID', 'Value']
        )
        result = engine.run_complete_pipeline()
        
        # يجب أن تبقى القيم الفارغة
        self.assertTrue(result['dataframe']['ID'].isna().all())
    
    def test_special_characters(self):
        """اختبار مع أحرف خاصة"""
        data = {
            'Description': ['مرحباً', 'مرحبا بك! 😊', 'النص @ مع رموز'],
            'Value': [100, 200, 300]
        }
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            numeric_columns=['Value']
        )
        result = engine.run_complete_pipeline()
        
        # يجب الحفاظ على الأحرف الخاصة
        self.assertEqual(result['dataframe'].loc[0, 'Description'], 'مرحباً')
    
    # ============================================================
    # اختبارات التحقق من النوع
    # ============================================================
    
    def test_type_checking_functions(self):
        """اختبار دوال التحقق من النوع"""
        engine = ComprehensiveProcessingEngine(pd.DataFrame())
        
        # اختبار التحقق من التاريخ
        self.assertTrue(engine._is_valid_date('2024-01-15'))
        self.assertTrue(engine._is_valid_date(datetime(2024, 1, 15)))
        self.assertFalse(engine._is_valid_date('ليس تاريخاً'))
        
        # اختبار الرقم الصحيح
        self.assertTrue(engine._is_numeric_integer(10.0))
        self.assertTrue(engine._is_numeric_integer('10'))
        self.assertFalse(engine._is_numeric_integer(10.5))
        self.assertFalse(engine._is_numeric_integer('ليس رقماً'))


class TestIntegration(unittest.TestCase):
    """اختبارات التكامل الشاملة"""
    
    def test_complete_workflow(self):
        """اختبار سير العمل الكامل"""
        # إنشاء بيانات معقدة
        data = {
            'Product_ID': ['P001', 'P002', 'معرف غير محدد', 'P004'],
            'Quantity': ['10', '50.5', '0', 'كمية مرتفعة'],
            'Price': [99.99, '150', 'مختلف', 300.0],
            'Order_Date': ['2024-01-15', '2024-02-20 14:30', 'تاريخ قديم', '2024-04-10'],
            'Delivery_Date': [
                datetime(2024, 2, 1, 10, 30),
                '2024-03-05',
                None,
                '2024-05-20 00:00:00'
            ]
        }
        
        df = pd.DataFrame(data)
        
        # المعالجة
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Order_Date', 'Delivery_Date'],
            numeric_columns=['Product_ID', 'Quantity', 'Price']
        )
        
        result = engine.run_complete_pipeline()
        
        # التحقق من النتائج
        processed_df = result['dataframe']
        audit_report = result['audit_report']
        
        # يجب أن يكون هناك تعديلات
        self.assertGreater(audit_report['summary']['cells_modified'], 0)
        
        # يجب أن تكون نسبة الفحص 100%
        self.assertEqual(audit_report['summary']['coverage_percentage'], 100.0)
        
        # يجب أن يكون هناك ملاحظات
        self.assertGreater(audit_report['summary']['notes_added'], 0)


def run_tests():
    """تشغيل جميع الاختبارات"""
    # إنشاء مجموعة الاختبارات
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # إضافة الاختبارات
    suite.addTests(loader.loadTestsFromTestCase(TestComprehensiveProcessingEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # تشغيل الاختبارات
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # طباعة الملخص
    print("\n" + "="*70)
    print("📊 ملخص الاختبارات")
    print("="*70)
    print(f"✓ عدد الاختبارات: {result.testsRun}")
    print(f"✓ النجاحات: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"✗ الفشل: {len(result.failures)}")
    print(f"✗ الأخطاء: {len(result.errors)}")
    print("="*70)
    
    return result


if __name__ == '__main__':
    result = run_tests()
