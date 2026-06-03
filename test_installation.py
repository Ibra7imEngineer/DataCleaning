"""
اختبار سريع للتحقق من أن المحرك يعمل بشكل صحيح
Quick Test - Verify Engine Installation
"""

import sys
import pandas as pd
import numpy as np


def test_imports():
    """اختبار استيراد المكتبات"""
    print("\n" + "="*70)
    print("1️⃣  اختبار الاستيراد")
    print("="*70)
    
    try:
        import pandas
        print("✓ pandas مثبت بنجاح")
    except ImportError:
        print("✗ pandas غير مثبت - يجب تثبيته")
        return False
    
    try:
        import numpy
        print("✓ numpy مثبت بنجاح")
    except ImportError:
        print("✗ numpy غير مثبت - يجب تثبيته")
        return False
    
    try:
        import openpyxl
        print("✓ openpyxl مثبت بنجاح")
    except ImportError:
        print("✗ openpyxl غير مثبت - يجب تثبيته")
        return False
    
    try:
        from comprehensive_processing_engine import ComprehensiveProcessingEngine
        print("✓ ComprehensiveProcessingEngine استورد بنجاح")
    except ImportError as e:
        print(f"✗ فشل استيراد ComprehensiveProcessingEngine: {e}")
        return False
    
    return True


def test_basic_functionality():
    """اختبار الوظائف الأساسية"""
    print("\n" + "="*70)
    print("2️⃣  اختبار الوظائف الأساسية")
    print("="*70)
    
    try:
        from comprehensive_processing_engine import ComprehensiveProcessingEngine
        
        # إنشاء بيانات بسيطة
        data = {
            'ID': ['1.0', '2.0', '3.0'],
            'Name': ['أحمد', 'فاطمة', 'محمد'],
            'Date': ['2024-01-15', '2024-02-20', '2024-03-15']
        }
        df = pd.DataFrame(data)
        print(f"✓ تم إنشاء DataFrame: {len(df)} صف × {len(df.columns)} عمود")
        
        # إنشاء المحرك
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Date'],
            numeric_columns=['ID']
        )
        print("✓ تم إنشاء ComprehensiveProcessingEngine")
        
        # اختبار المعالجة
        engine.process_numeric_columns()
        print("✓ معالجة الأعمدة الرقمية نجحت")
        
        engine.process_date_columns()
        print("✓ معالجة أعمدة التاريخ نجحت")
        
        engine.detect_data_shifting()
        print("✓ فحص الترحيل العشوائي نجح")
        
        report = engine.generate_audit_report()
        print("✓ إنشاء التقرير نجح")
        
        return True, engine, report
        
    except Exception as e:
        print(f"✗ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None, None


def test_pipeline():
    """اختبار خط الإنتاج الكامل"""
    print("\n" + "="*70)
    print("3️⃣  اختبار خط الإنتاج الكامل")
    print("="*70)
    
    try:
        from comprehensive_processing_engine import ComprehensiveProcessingEngine
        
        # بيانات أكثر تعقيداً
        data = {
            'Product_ID': ['P001', 'P002', 'P003'],
            'Price': [999.99, '50.0', 'غير متوفر'],
            'Quantity': ['100', '50.5', 0],
            'Order_Date': ['2024-01-15', '2024-02-20 14:30', '2024-03-15'],
            'Stock': [10, 20, np.nan]
        }
        df = pd.DataFrame(data)
        print(f"✓ بيانات اختبار: {len(df)} صف")
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Order_Date'],
            numeric_columns=['Product_ID', 'Price', 'Quantity', 'Stock']
        )
        print("✓ محرك معالجة جاهز")
        
        # تشغيل المعالجة الكاملة
        result = engine.run_complete_pipeline()
        print("✓ خط الإنتاج اكتمل بنجاح")
        
        # عرض الإحصائيات
        summary = result['audit_report']['summary']
        print(f"\n📊 الإحصائيات:")
        print(f"  • الصفوف المعالجة: {summary['total_rows']}")
        print(f"  • الخلايا الكلية: {summary['total_cells']}")
        print(f"  • الخلايا المفحوصة: {summary['cells_checked']}")
        print(f"  • الخلايا المعدلة: {summary['cells_modified']}")
        print(f"  • نسبة الفحص: {summary['coverage_percentage']:.1f}%")
        
        return True, result
        
    except Exception as e:
        print(f"✗ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_performance():
    """اختبار الأداء مع بيانات كبيرة"""
    print("\n" + "="*70)
    print("4️⃣  اختبار الأداء (1000 صف)")
    print("="*70)
    
    try:
        from comprehensive_processing_engine import ComprehensiveProcessingEngine
        import time
        
        # إنشاء بيانات كبيرة
        n_rows = 1000
        np.random.seed(42)
        
        data = {
            'ID': np.arange(1, n_rows + 1),
            'Value': np.random.uniform(10, 1000, n_rows),
            'Date': pd.date_range('2024-01-01', periods=n_rows)
        }
        df = pd.DataFrame(data)
        print(f"✓ تم إنشاء {n_rows:,} صف من البيانات")
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Date'],
            numeric_columns=['ID', 'Value']
        )
        
        # قياس الوقت
        start_time = time.time()
        result = engine.run_complete_pipeline()
        duration = time.time() - start_time
        
        print(f"✓ المعالجة اكتملت في: {duration:.2f} ثانية")
        print(f"✓ متوسط الوقت لكل صف: {(duration / n_rows * 1000):.4f} ميلي ثانية")
        
        if duration < 10:
            print("✓ الأداء ممتاز! ⭐")
            return True
        elif duration < 30:
            print("✓ الأداء جيد! ⭐⭐")
            return True
        else:
            print("⚠️  الأداء مقبول")
            return True
            
    except Exception as e:
        print(f"✗ خطأ: {str(e)}")
        return False


def test_excel_export():
    """اختبار التصدير لـ Excel"""
    print("\n" + "="*70)
    print("5️⃣  اختبار التصدير لـ Excel")
    print("="*70)
    
    try:
        from comprehensive_processing_engine import ComprehensiveProcessingEngine
        import os
        
        # إنشاء بيانات
        data = {
            'ID': ['1.0', '2.0'],
            'Name': ['أحمد', 'فاطمة'],
            'Date': ['2024-01-15', '2024-02-20']
        }
        df = pd.DataFrame(data)
        
        engine = ComprehensiveProcessingEngine(
            df=df,
            date_columns=['Date'],
            numeric_columns=['ID']
        )
        
        # التصدير
        output_file = 'test_output.xlsx'
        engine.run_complete_pipeline(output_file=output_file)
        
        # التحقق من الملف
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✓ تم إنشاء الملف: {output_file}")
            print(f"✓ حجم الملف: {file_size:,} بايت")
            
            # محاولة قراءته
            try:
                test_df = pd.read_excel(output_file, sheet_name='Data')
                print(f"✓ تم قراءة البيانات: {len(test_df)} صف")
                
                # حذف الملف
                os.remove(output_file)
                print("✓ تم حذف ملف الاختبار")
                return True
            except Exception as e:
                print(f"✗ فشل قراءة الملف: {e}")
                os.remove(output_file)
                return False
        else:
            print("✗ لم يتم إنشاء الملف")
            return False
            
    except Exception as e:
        print(f"✗ خطأ: {str(e)}")
        return False


def print_summary(results):
    """طباعة ملخص الاختبارات"""
    print("\n" + "="*70)
    print("📊 ملخص الاختبارات")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for r in results if r)
    failed = total - passed
    
    print(f"\n✓ النجاحات: {passed}/{total}")
    print(f"✗ الفشل: {failed}/{total}")
    
    if failed == 0:
        print("\n🎉 جميع الاختبارات نجحت! المحرك جاهز للاستخدام.")
        return True
    else:
        print(f"\n⚠️  {failed} اختبارات فشلت - يجب حل المشاكل")
        return False


def main():
    """الدالة الرئيسية"""
    print("\n" + "#" * 70)
    print("# 🧪 اختبار سريع لمحرك المعالجة الشاملة")
    print("#" * 70)
    
    results = []
    
    # 1. اختبار الاستيراد
    result1 = test_imports()
    results.append(result1)
    
    if not result1:
        print("\n❌ فشل اختبار الاستيراد - يجب تثبيت المكتبات أولاً")
        print("استخدم: pip install pandas numpy openpyxl")
        return False
    
    # 2. اختبار الوظائف الأساسية
    result2, engine, report = test_basic_functionality()
    results.append(result2)
    
    # 3. اختبار خط الإنتاج
    result3, pipeline_result = test_pipeline()
    results.append(result3)
    
    # 4. اختبار الأداء
    result4 = test_performance()
    results.append(result4)
    
    # 5. اختبار التصدير
    result5 = test_excel_export()
    results.append(result5)
    
    # الملخص
    success = print_summary(results)
    
    if success:
        print("\n💡 الخطوات التالية:")
        print("  1. جرّب: python QUICK_START.py")
        print("  2. اقرأ: PROCESSING_ENGINE_GUIDE.md")
        print("  3. جرّب الأمثلة: python advanced_examples_processing.py")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
