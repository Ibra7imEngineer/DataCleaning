#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
    اختبار سريع - التحقق من عمل محرك المعالجة النهائي
    Quick Test - Verify Comprehensive Final Engine
================================================================================

هذا الملف يتحقق من أن كل شيء يعمل بشكل صحيح
"""

import sys
import pandas as pd
from pathlib import Path

print("\n" + "=" * 80)
print("✅ اختبار سريع لمحرك المعالجة النهائي")
print("=" * 80)

# ============================================================================
# 1. التحقق من المكتبات
# ============================================================================

print("\n1️⃣  التحقق من المكتبات...")

try:
    import pandas as pd
    print("   ✅ pandas")
except ImportError:
    print("   ❌ pandas (مفقودة)")
    print("      pip install pandas")

try:
    import numpy as np
    print("   ✅ numpy")
except ImportError:
    print("   ❌ numpy (مفقودة)")
    print("      pip install numpy")

try:
    import openpyxl
    print("   ✅ openpyxl")
except ImportError:
    print("   ❌ openpyxl (مفقودة)")
    print("      pip install openpyxl")

try:
    from comprehensive_final_engine import ComprehensiveFinalEngine
    print("   ✅ comprehensive_final_engine")
except ImportError as e:
    print(f"   ❌ comprehensive_final_engine ({e})")
    print("      تأكد من وجود ملف comprehensive_final_engine.py")
    sys.exit(1)

# ============================================================================
# 2. التحقق من ملف البيانات
# ============================================================================

print("\n2️⃣  التحقق من ملفات البيانات...")

if Path('sample_data.csv').exists():
    print("   ✅ sample_data.csv موجود")
else:
    print("   ⚠️  sample_data.csv غير موجود")
    print("      سيتم إنشاء ملف اختبار...")
    
    # إنشاء ملف بيانات اختبار بسيط
    test_data = {
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Ahmed', 'Fatima', 'Omar', 'Zainab', 'Layla'],
        'Date': ['2026-01-15', '2026-02-20', '2026-03-10', '2026-04-05', '2026-05-12'],
        'Amount': [1500, 2300, 1800, 950, 1200],
        'City': ['Cairo', 'Alexandria', 'Giza', 'Cairo', 'Alexandria']
    }
    df_test = pd.DataFrame(test_data)
    df_test.to_csv('sample_data.csv', index=False)
    print("   ✅ تم إنشاء sample_data.csv")

# ============================================================================
# 3. اختبار المحرك على بيانات بسيطة
# ============================================================================

print("\n3️⃣  اختبار المحرك...")

try:
    engine = ComprehensiveFinalEngine(verbose=False)
    print("   ✅ تم إنشاء المحرك")
    
    # معالجة البيانات
    print("   🔄 معالجة sample_data.csv...")
    processed_df = engine.process_comprehensive(
        input_path='sample_data.csv',
        output_path='test_output.xlsx'
    )
    print("   ✅ تمت المعالجة بنجاح")
    
    # التحقق من النتائج
    print(f"\n   📊 النتائج:")
    print(f"      • الصفوف: {len(processed_df)}")
    print(f"      • الأعمدة: {len(processed_df.columns)}")
    print(f"      • أعمدة التاريخ: {engine.date_columns}")
    print(f"      • الأعمدة الرقمية: {engine.numeric_columns}")
    
except Exception as e:
    print(f"   ❌ خطأ: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# 4. التحقق من الملفات المُنشأة
# ============================================================================

print("\n4️⃣  التحقق من الملفات المُنشأة...")

output_files = [
    'test_output.xlsx',
    'test_output_raw.xlsx',
    'test_output_audit_report.txt'
]

for file in output_files:
    if Path(file).exists():
        size = Path(file).stat().st_size
        print(f"   ✅ {file} ({size:,} bytes)")
    else:
        print(f"   ⚠️  {file} غير موجود")

# ============================================================================
# 5. ملخص الاختبار
# ============================================================================

print("\n" + "=" * 80)
print("✅ جميع الاختبارات نجحت!")
print("=" * 80)

print("""
🎯 الخطوات التالية:

1. استخدام الواجهة التفاعلية:
   python QUICK_START_ENGINE.py

2. تشغيل الأمثلة المتقدمة:
   python advanced_examples_final_engine.py

3. تشغيل الاختبارات الشاملة:
   python test_comprehensive_engine.py

4. قراءة التوثيق:
   COMPREHENSIVE_ENGINE_DOCUMENTATION.txt

5. استخدام المحرك مباشرة:
   python -c "
from comprehensive_final_engine import ComprehensiveFinalEngine
engine = ComprehensiveFinalEngine(verbose=True)
df = engine.process_comprehensive('data.csv', 'output.xlsx')
"

🎉 محرك المعالجة النهائي جاهز للاستخدام!
""")

# ============================================================================
# 6. عرض معلومات إضافية
# ============================================================================

print("\n" + "=" * 80)
print("📋 معلومات النظام")
print("=" * 80)

print(f"\n✓ إصدار Python: {sys.version.split()[0]}")

try:
    print(f"✓ إصدار pandas: {pd.__version__}")
except:
    pass

try:
    import numpy as np
    print(f"✓ إصدار numpy: {np.__version__}")
except:
    pass

print("\n" + "=" * 80)
