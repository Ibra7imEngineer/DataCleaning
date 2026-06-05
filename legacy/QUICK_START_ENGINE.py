#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
    دليل التشغيل السريع - محرك المعالجة النهائي
    Quick Start Guide - Comprehensive Final Engine
================================================================================

هذا الملف يوفر أسرع طريقة لبدء استخدام المحرك
"""

import sys
import os
from pathlib import Path

# التأكد من وجود المكتبات
try:
    import pandas as pd
    import numpy as np
    from comprehensive_final_engine import ComprehensiveFinalEngine
except ImportError as e:
    print(f"❌ خطأ: مكتبة مفقودة: {e}")
    print("\nالرجاء تثبيت المكتبات المطلوبة:")
    print("pip install pandas numpy openpyxl python-dateutil")
    sys.exit(1)


# ============================================================================
# دالة بسيطة جداً للمستخدم الجديد
# ============================================================================

def simple_processing():
    """
    أبسط طريقة لمعالجة البيانات
    """
    print("\n" + "=" * 80)
    print("🚀 بدء المعالجة البسيطة")
    print("=" * 80)
    
    # ملف الإدخال
    input_file = 'sample_data.csv'
    output_file = 'sample_data_processed.xlsx'
    
    # التحقق من وجود الملف
    if not Path(input_file).exists():
        print(f"❌ الملف '{input_file}' غير موجود")
        print(f"\n💡 الملفات المتاحة:")
        for f in Path('.').glob('*.csv'):
            print(f"   • {f}")
        return
    
    # إنشاء المحرك
    print(f"\n📂 الملف المراد معالجته: {input_file}")
    engine = ComprehensiveFinalEngine(verbose=True)
    
    # معالجة البيانات
    try:
        processed_df = engine.process_comprehensive(
            input_path=input_file,
            output_path=output_file
        )
        
        print(f"\n✅ تمت المعالجة بنجاح!")
        print(f"\n📁 الملفات المُنشأة:")
        print(f"   1. {output_file}")
        print(f"   2. {output_file.replace('.xlsx', '_raw.xlsx')}")
        print(f"   3. {output_file.replace('.xlsx', '_audit_report.txt')}")
        
        print(f"\n📊 ملخص البيانات:")
        print(f"   • عدد الصفوف: {len(processed_df)}")
        print(f"   • عدد الأعمدة: {len(processed_df.columns)}")
        print(f"   • أعمدة التاريخ: {len(engine.date_columns)}")
        print(f"   • الأعمدة الرقمية: {len(engine.numeric_columns)}")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# دالة متقدمة مع خيارات
# ============================================================================

def advanced_processing():
    """
    معالجة متقدمة مع خيارات مخصصة
    """
    print("\n" + "=" * 80)
    print("⚙️  بدء المعالجة المتقدمة")
    print("=" * 80)
    
    print("\n📋 الملفات المتاحة:")
    csv_files = list(Path('.').glob('*.csv'))
    
    if not csv_files:
        print("❌ لا توجد ملفات CSV")
        return
    
    for i, f in enumerate(csv_files, 1):
        print(f"   {i}. {f}")
    
    # اختيار الملف
    try:
        choice = int(input("\n📌 اختر رقم الملف: "))
        if choice < 1 or choice > len(csv_files):
            print("❌ اختيار غير صحيح")
            return
        
        input_file = str(csv_files[choice - 1])
    except ValueError:
        print("❌ الرجاء إدخال رقم صحيح")
        return
    
    # اسم الملف الناتج
    output_file = input("\n📝 اسم الملف الناتج (بدون امتداد): ").strip()
    if not output_file:
        output_file = Path(input_file).stem + '_processed'
    
    output_file = output_file.replace('.xlsx', '') + '.xlsx'
    
    # إنشاء المحرك
    verbose = input("\n📊 هل تريد عرض التفاصيل؟ (y/n): ").lower() == 'y'
    
    print(f"\n🔄 المعالجة قيد التنفيذ...")
    engine = ComprehensiveFinalEngine(verbose=verbose)
    
    try:
        processed_df = engine.process_comprehensive(
            input_path=input_file,
            output_path=output_file
        )
        
        print(f"\n✅ تمت المعالجة بنجاح!")
        print(f"\n📁 الملفات المُنشأة:")
        print(f"   • {output_file}")
        print(f"   • {output_file.replace('.xlsx', '_raw.xlsx')}")
        print(f"   • {output_file.replace('.xlsx', '_audit_report.txt')}")
        
        # عرض معلومات إضافية
        print(f"\n📊 إحصائيات البيانات:")
        print(f"   • عدد الصفوف: {len(processed_df)}")
        print(f"   • عدد الأعمدة: {len(processed_df.columns)}")
        print(f"   • أعمدة التاريخ: {len(engine.date_columns)} -> {engine.date_columns}")
        print(f"   • الأعمدة الرقمية: {len(engine.numeric_columns)} -> {engine.numeric_columns}")
        
        # عرض السجل
        if verbose:
            print(f"\n📋 ملخص السجل:")
            for log in engine.audit_log[-5:]:
                print(f"   {log}")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# دالة اختبار البيانات الضخمة
# ============================================================================

def test_large_dataset():
    """
    اختبار أداء المحرك على بيانات ضخمة
    """
    print("\n" + "=" * 80)
    print("⚡ اختبار الأداء - بيانات ضخمة")
    print("=" * 80)
    
    import time
    
    # اختيار حجم البيانات
    print("\n📊 اختر حجم البيانات للاختبار:")
    print("   1. صغير (10,000 صف)")
    print("   2. متوسط (100,000 صف)")
    print("   3. كبير (1,000,000 صف)")
    
    try:
        choice = int(input("\n📌 الاختيار: "))
        
        sizes = {
            1: 10000,
            2: 100000,
            3: 1000000
        }
        
        if choice not in sizes:
            print("❌ اختيار غير صحيح")
            return
        
        size = sizes[choice]
        
    except ValueError:
        print("❌ الرجاء إدخال رقم صحيح")
        return
    
    # إنشاء البيانات
    print(f"\n🔨 إنشاء {size:,} صف من البيانات...")
    
    np.random.seed(42)
    data = {
        'ID': np.arange(1, size + 1),
        'Name': np.random.choice(['Ahmed', 'Fatima', 'Omar', 'Zainab'], size),
        'Date': pd.date_range('2026-01-01', periods=size, freq='H').astype(str),
        'Amount': np.random.uniform(100, 5000, size),
        'City': np.random.choice(['Cairo', 'Alexandria', 'Giza'], size)
    }
    
    df = pd.DataFrame(data)
    test_file = f'test_large_{size}.csv'
    
    print(f"💾 حفظ البيانات...")
    df.to_csv(test_file, index=False)
    
    # بدء الاختبار
    print(f"\n⏱️  بدء المعالجة...")
    start_time = time.time()
    
    engine = ComprehensiveFinalEngine(verbose=False)
    
    try:
        processed_df = engine.process_comprehensive(
            input_path=test_file,
            output_path=f'test_large_{size}_output.xlsx'
        )
        
        elapsed_time = time.time() - start_time
        rows_per_second = len(processed_df) / elapsed_time
        
        print(f"\n✅ اختبار الأداء انتهى بنجاح!")
        print(f"\n📈 النتائج:")
        print(f"   • عدد الصفوف: {len(processed_df):,}")
        print(f"   • الوقت المستغرق: {elapsed_time:.2f} ثانية")
        print(f"   • السرعة: {rows_per_second:,.0f} صف/ثانية")
        
        # تقييم الأداء
        print(f"\n⭐ تقييم الأداء:")
        if rows_per_second > 100000:
            print("   • 🏆 ممتاز جداً! (> 100k صف/ث)")
        elif rows_per_second > 50000:
            print("   • ✅ ممتاز (50k-100k صف/ث)")
        elif rows_per_second > 10000:
            print("   • ✓ جيد (10k-50k صف/ث)")
        else:
            print("   • ⚠️  قد تحتاج لتحسينات")
        
        # حذف ملف الاختبار
        print(f"\n🧹 تنظيف الملفات المؤقتة...")
        Path(test_file).unlink()
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# دالة عرض السجل
# ============================================================================

def view_audit_log():
    """
    عرض سجل العمليات من الملف
    """
    print("\n" + "=" * 80)
    print("📋 عرض سجل العمليات")
    print("=" * 80)
    
    print("\n📁 ملفات التقارير المتاحة:")
    report_files = list(Path('.').glob('*_audit_report.txt'))
    
    if not report_files:
        print("❌ لا توجد ملفات تقارير")
        return
    
    for i, f in enumerate(report_files, 1):
        print(f"   {i}. {f}")
    
    try:
        choice = int(input("\n📌 اختر رقم التقرير: "))
        if choice < 1 or choice > len(report_files):
            print("❌ اختيار غير صحيح")
            return
        
        report_file = report_files[choice - 1]
    except ValueError:
        print("❌ الرجاء إدخال رقم صحيح")
        return
    
    print(f"\n📖 محتوى التقرير: {report_file}\n")
    print("=" * 80)
    
    with open(report_file, 'r', encoding='utf-8') as f:
        print(f.read())
    
    print("=" * 80)


# ============================================================================
# القائمة الرئيسية
# ============================================================================

def main_menu():
    """
    قائمة التطبيق الرئيسية
    """
    while True:
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "محرك المعالجة النهائي الشامل" + " " * 31 + "║")
        print("║" + " " * 15 + "Comprehensive Final Processing Engine" + " " * 27 + "║")
        print("╚" + "=" * 78 + "╝")
        
        print("\n📌 الخيارات المتاحة:")
        print("   1. معالجة بسيطة (Simple Processing)")
        print("   2. معالجة متقدمة (Advanced Processing)")
        print("   3. اختبار الأداء (Performance Test)")
        print("   4. عرض سجل العمليات (View Audit Log)")
        print("   5. خروج (Exit)")
        
        try:
            choice = input("\n📌 اختر خياراً: ").strip()
            
            if choice == '1':
                simple_processing()
            elif choice == '2':
                advanced_processing()
            elif choice == '3':
                test_large_dataset()
            elif choice == '4':
                view_audit_log()
            elif choice == '5':
                print("\n👋 شكراً لاستخدام محرك المعالجة النهائي!")
                print("   للمزيد من المعلومات: COMPREHENSIVE_ENGINE_DOCUMENTATION.txt")
                break
            else:
                print("❌ اختيار غير صحيح")
        
        except KeyboardInterrupt:
            print("\n\n⏹️  تم الإيقاف من قبل المستخدم")
            break
        except Exception as e:
            print(f"❌ خطأ: {e}")


# ============================================================================
# نقطة البداية
# ============================================================================

if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
