#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
    ملف اختبار شامل لمحرك المعالجة النهائي
    Comprehensive Test Suite for Final Engine
================================================================================

هذا الملف يوضح اختبار المحرك على سيناريوهات مختلفة
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from comprehensive_final_engine import ComprehensiveFinalEngine
import time


# ============================================================================
# 1️⃣  إنشاء بيانات اختبار متنوعة
# ============================================================================

def create_test_datasets():
    """
    إنشاء مجموعات بيانات اختبار مختلفة
    """
    print("\n" + "=" * 80)
    print("🔨 إنشاء مجموعات بيانات الاختبار")
    print("=" * 80)
    
    # ========================================================================
    # اختبار 1: بيانات نظيفة (Clean Data)
    # ========================================================================
    print("\n✓ إنشاء مجموعة 1: بيانات نظيفة (Clean Data)")
    
    clean_data = {
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Ahmed', 'Fatima', 'Omar', 'Zainab', 'Layla'],
        'Date': ['2026-01-15', '2026-02-20', '2026-03-10', '2026-04-05', '2026-05-12'],
        'Amount': [1500, 2300, 1800, 950, 1200],
        'City': ['Cairo', 'Alexandria', 'Giza', 'Cairo', 'Alexandria']
    }
    
    df_clean = pd.DataFrame(clean_data)
    df_clean.to_csv('test_clean_data.csv', index=False)
    print(f"   📁 test_clean_data.csv ({len(df_clean)} صفوف)")
    
    # ========================================================================
    # اختبار 2: بيانات فوضوية (Messy Data)
    # ========================================================================
    print("\n✓ إنشاء مجموعة 2: بيانات فوضوية (Messy Data)")
    
    messy_data = {
        'ID': [1, 2, '3', 4, 4],  # تكرار و نص
        'Name': ['Ahmed Hassan', 'Fatima', None, 'Omar', 'Omar'],  # فراغ و تكرار
        'Date': ['2026-01-15', '15/02/2026', 'Cairo', '2026-03-10', 'Ahmed Hassan'],  # صيغ مختلفة و نصوص
        'Amount': [1500, 'Two Thousand', 1800.0, 950, 1200],  # نص و float
        'City': ['Cairo', 'Alexandria', 'Giza', '', 'Cairo']  # فراغ
    }
    
    df_messy = pd.DataFrame(messy_data)
    df_messy.to_csv('test_messy_data.csv', index=False)
    print(f"   📁 test_messy_data.csv ({len(df_messy)} صفوف)")
    
    # ========================================================================
    # اختبار 3: بيانات بصيغ تاريخ مختلفة (Various Date Formats)
    # ========================================================================
    print("\n✓ إنشاء مجموعة 3: صيغ تاريخ مختلفة (Various Date Formats)")
    
    date_data = {
        'ID': np.arange(1, 11),
        'Date_ISO': ['2026-01-15', '2026-02-20', '2026-03-10', '2026-04-05', '2026-05-12',
                     '2026-06-15', '2026-07-20', '2026-08-10', '2026-09-05', '2026-10-12'],
        'Date_EU': ['15/01/2026', '20/02/2026', '10/03/2026', '05/04/2026', '12/05/2026',
                    '15/06/2026', '20/07/2026', '10/08/2026', '05/09/2026', '12/10/2026'],
        'Date_US': ['01-15-2026', '02-20-2026', '03-10-2026', '04-05-2026', '05-12-2026',
                    '06-15-2026', '07-20-2026', '08-10-2026', '09-05-2026', '10-12-2026'],
        'Amount': np.random.uniform(1000, 5000, 10)
    }
    
    df_dates = pd.DataFrame(date_data)
    df_dates.to_csv('test_various_dates.csv', index=False)
    print(f"   📁 test_various_dates.csv ({len(df_dates)} صفوف)")
    
    # ========================================================================
    # اختبار 4: بيانات برقم مختلفة (Various Number Formats)
    # ========================================================================
    print("\n✓ إنشاء مجموعة 4: صيغ أرقام مختلفة (Various Number Formats)")
    
    number_data = {
        'ID': [1, 2, 3, 4, 5, 6, 7, 8],
        'Integer': [100, 200, 300, 400, 500, 600, 700, 800],
        'Float': [100.5, 200.75, 300.25, 400.0, 500.99, 600.5, 700.0, 800.33],
        'Text_Number': ['1000', '2000', 'N/A', '4000', '5000', '6000', '7000', '8000'],
        'Mixed': [100, 200.5, 300, 400.0, 500, 600.5, 700, 800.0]
    }
    
    df_numbers = pd.DataFrame(number_data)
    df_numbers.to_csv('test_various_numbers.csv', index=False)
    print(f"   📁 test_various_numbers.csv ({len(df_numbers)} صفوف)")
    
    # ========================================================================
    # اختبار 5: بيانات بفراغات عشوائية (Missing Data)
    # ========================================================================
    print("\n✓ إنشاء مجموعة 5: بيانات بفراغات (Missing Data)")
    
    missing_data = {
        'ID': [1, 2, None, 4, 5, 6, None, 8],
        'Name': ['Ahmed', None, 'Omar', 'Zainab', None, 'Karim', 'Hany', 'Eman'],
        'Date': ['2026-01-15', '2026-02-20', None, '2026-04-05', '2026-05-12', None, '2026-07-20', '2026-08-10'],
        'Amount': [1500, None, 1800, 950, None, 1100, 1200, None],
        'Status': [None, 'Active', 'Inactive', None, 'Active', 'Pending', None, 'Active']
    }
    
    df_missing = pd.DataFrame(missing_data)
    df_missing.to_csv('test_missing_data.csv', index=False)
    print(f"   📁 test_missing_data.csv ({len(df_missing)} صفوف)")
    
    # ========================================================================
    # اختبار 6: بيانات كبيرة (Large Dataset)
    # ========================================================================
    print("\n✓ إنشاء مجموعة 6: بيانات كبيرة (Large Dataset - 100k rows)")
    
    np.random.seed(42)
    large_data = {
        'ID': np.arange(1, 100001),
        'Name': np.random.choice(['Ahmed', 'Fatima', 'Omar', 'Zainab', 'Karim'], 100000),
        'Date': pd.date_range('2026-01-01', periods=100000, freq='H').astype(str),
        'Amount': np.random.uniform(100, 5000, 100000),
        'City': np.random.choice(['Cairo', 'Alexandria', 'Giza', 'Mansoura', 'Tanta'], 100000)
    }
    
    df_large = pd.DataFrame(large_data)
    df_large.to_csv('test_large_data.csv', index=False)
    print(f"   📁 test_large_data.csv ({len(df_large)} صفوف)")
    
    print("\n✅ تم إنشاء جميع مجموعات الاختبار بنجاح")
    
    return {
        'clean': 'test_clean_data.csv',
        'messy': 'test_messy_data.csv',
        'dates': 'test_various_dates.csv',
        'numbers': 'test_various_numbers.csv',
        'missing': 'test_missing_data.csv',
        'large': 'test_large_data.csv'
    }


# ============================================================================
# 2️⃣  تشغيل الاختبارات
# ============================================================================

def run_tests(test_files):
    """
    تشغيل الاختبارات على جميع مجموعات البيانات
    """
    print("\n" + "=" * 80)
    print("🧪 تشغيل الاختبارات على جميع مجموعات البيانات")
    print("=" * 80)
    
    results = {}
    
    for test_name, file_path in test_files.items():
        print(f"\n{'=' * 80}")
        print(f"🔬 اختبار: {test_name.upper()} ({file_path})")
        print(f"{'=' * 80}")
        
        try:
            # قراءة البيانات الأصلية
            df_original = pd.read_csv(file_path)
            print(f"\n📊 البيانات الأصلية:")
            print(f"   • الصفوف: {len(df_original)}")
            print(f"   • الأعمدة: {len(df_original.columns)}")
            print(f"   • أنواع: {dict(df_original.dtypes)}")
            
            # معالجة البيانات
            print(f"\n⏱️  بدء المعالجة...")
            start_time = time.time()
            
            engine = ComprehensiveFinalEngine(verbose=False)
            output_file = f'test_output_{test_name}.xlsx'
            
            processed_df = engine.process_comprehensive(
                input_path=file_path,
                output_path=output_file
            )
            
            elapsed_time = time.time() - start_time
            
            # النتائج
            print(f"\n✅ المعالجة انتهت في {elapsed_time:.2f} ثانية")
            print(f"\n📊 البيانات بعد المعالجة:")
            print(f"   • الصفوف: {len(processed_df)}")
            print(f"   • الأعمدة: {len(processed_df.columns)}")
            print(f"   • أنواع: {dict(processed_df.dtypes)}")
            
            # الإحصائيات
            print(f"\n📈 الإحصائيات:")
            print(f"   • أعمدة التاريخ المكتشفة: {len(engine.date_columns)}")
            print(f"   • الأعمدة الرقمية المكتشفة: {len(engine.numeric_columns)}")
            print(f"   • عدد العمليات في السجل: {len(engine.audit_log)}")
            print(f"   • عدد عمليات الترحيل: {len(engine.data_shifts_log)}")
            
            # النسبة المئوية للفراغات
            print(f"\n🔍 نسبة الفراغات:")
            for col in processed_df.columns:
                null_count = processed_df[col].isna().sum()
                if null_count > 0:
                    null_percentage = (null_count / len(processed_df)) * 100
                    print(f"   • {col}: {null_percentage:.1f}%")
            
            results[test_name] = {
                'status': '✅ نجح',
                'time': elapsed_time,
                'rows': len(processed_df),
                'columns': len(processed_df.columns),
                'output': output_file
            }
            
        except Exception as e:
            print(f"\n❌ خطأ: {e}")
            import traceback
            traceback.print_exc()
            
            results[test_name] = {
                'status': '❌ فشل',
                'error': str(e)
            }
    
    return results


# ============================================================================
# 3️⃣  ملخص النتائج
# ============================================================================

def print_summary(results):
    """
    طباعة ملخص نتائج الاختبارات
    """
    print("\n" + "=" * 80)
    print("📊 ملخص النتائج")
    print("=" * 80)
    
    print("\n┌─────────────────────────────────────────────────────────────────────────────┐")
    print("│ الاختبار          │ الحالة      │ الوقت      │ الصفوف    │ الأعمدة        │")
    print("├─────────────────────────────────────────────────────────────────────────────┤")
    
    successful = 0
    failed = 0
    total_time = 0
    
    for test_name, result in results.items():
        if result['status'].startswith('✅'):
            successful += 1
            status = '✅ نجح'
            time_str = f"{result['time']:.2f}s"
            rows_str = f"{result['rows']}"
            cols_str = f"{result['columns']}"
            total_time += result['time']
            
            print(f"│ {test_name:<16} │ {status:11} │ {time_str:10} │ {rows_str:9} │ {cols_str:14} │")
        else:
            failed += 1
            status = '❌ فشل'
            print(f"│ {test_name:<16} │ {status:11} │ -          │ -         │ -              │")
    
    print("└─────────────────────────────────────────────────────────────────────────────┘")
    
    print(f"\n📈 الإجمالي:")
    print(f"   • اختبارات ناجحة: {successful}")
    print(f"   • اختبارات فاشلة: {failed}")
    print(f"   • إجمالي الوقت: {total_time:.2f} ثانية")
    
    if successful > 0:
        avg_time = total_time / successful
        print(f"   • متوسط الوقت: {avg_time:.2f} ثانية")
    
    print(f"\n{'✅' if failed == 0 else '⚠️'} النتيجة النهائية:")
    if failed == 0:
        print("   🏆 جميع الاختبارات نجحت!")
    else:
        print(f"   ⚠️  {failed} اختبار(ات) فشل(ت)")


# ============================================================================
# 4️⃣  اختبار الأداء المتقدم
# ============================================================================

def performance_benchmark():
    """
    اختبار متقدم لقياس الأداء
    """
    print("\n" + "=" * 80)
    print("⚡ اختبار الأداء المتقدم (Performance Benchmark)")
    print("=" * 80)
    
    sizes = [10000, 50000, 100000]
    results = []
    
    for size in sizes:
        print(f"\n🔨 إنشاء مجموعة بيانات بـ {size:,} صف...")
        
        np.random.seed(42)
        data = {
            'ID': np.arange(1, size + 1),
            'Name': np.random.choice(['Ahmed', 'Fatima', 'Omar'], size),
            'Date': pd.date_range('2026-01-01', periods=size, freq='H').astype(str),
            'Amount': np.random.uniform(100, 5000, size)
        }
        
        df = pd.DataFrame(data)
        test_file = f'benchmark_{size}.csv'
        df.to_csv(test_file, index=False)
        
        # بدء الاختبار
        print(f"⏱️  بدء المعالجة...")
        start_time = time.time()
        
        engine = ComprehensiveFinalEngine(verbose=False)
        processed_df = engine.process_comprehensive(
            input_path=test_file,
            output_path=f'benchmark_{size}_output.xlsx'
        )
        
        elapsed_time = time.time() - start_time
        rows_per_second = len(processed_df) / elapsed_time
        
        print(f"✅ انتهت المعالجة:")
        print(f"   • الوقت: {elapsed_time:.2f}s")
        print(f"   • السرعة: {rows_per_second:,.0f} صف/ثانية")
        
        results.append({
            'size': size,
            'time': elapsed_time,
            'speed': rows_per_second
        })
    
    # ملخص الأداء
    print(f"\n" + "=" * 80)
    print("📊 ملخص الأداء:")
    print("=" * 80)
    
    print("\n┌────────────────────────────────────────────────┐")
    print("│ الحجم      │ الوقت      │ السرعة (صف/ثا)     │")
    print("├────────────────────────────────────────────────┤")
    
    for result in results:
        print(f"│ {result['size']:>6,}     │ {result['time']:>6.2f}s   │ {result['speed']:>12,.0f}    │")
    
    print("└────────────────────────────────────────────────┘")


# ============================================================================
# 5️⃣  الدالة الرئيسية
# ============================================================================

def main():
    """
    تشغيل جميع الاختبارات
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ملف الاختبار الشامل لمحرك المعالجة" + " " * 26 + "║")
    print("║" + " " * 15 + "Comprehensive Test Suite for Final Engine" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # 1. إنشاء مجموعات الاختبار
        test_files = create_test_datasets()
        
        # 2. تشغيل الاختبارات
        results = run_tests(test_files)
        
        # 3. طباعة الملخص
        print_summary(results)
        
        # 4. اختبار الأداء
        performance_benchmark()
        
        # الخلاصة
        print("\n" + "=" * 80)
        print("✅ انتهت جميع الاختبارات بنجاح!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
