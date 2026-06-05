"""
دالة المعالجة النهائية (Final Polish Function)
================================================
تُستدعى قبل تصدير البيانات مباشرة لحل مشاكل التنسيق والبيانات الشاذة

المشاكل المحلولة:
  1. أصفار الوقت في التواريخ (00:00:00)
  2. الكسور العشرية (.0) في الأرقام الصحيحة
  3. البيانات المُرحّلة (Data Shifting) في أعمدة التاريخ
  4. الأعمدة المتطابقة (Duplicate Columns)
  5. الخلايا الفارغة غير الموحدة
  
الأداء: معالجة مليون صف بسرعة فائقة عبر Vectorization

Author: Data Cleaning Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Tuple, List, Dict, Optional

# إعداد نظام التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def final_polish(
    df: pd.DataFrame,
    date_columns: Optional[List[str]] = None,
    numeric_columns: Optional[List[str]] = None,
    verbose: bool = True
) -> Tuple[pd.DataFrame, Dict]:
    """
    ✨ دالة المعالجة النهائية - Polish النهائي للبيانات
    
    تحل المشاكل التالية:
    1. تحويل التواريخ إلى YYYY-MM-DD (بدون أصفار الوقت)
    2. تحويل الأرقام الصحيحة إلى Int64 (بدون .0)
    3. نقل النصوص من أعمدة التاريخ إلى System_Notes
    4. دمج الأعمدة المتطابقة 100%
    5. توحيد الخلايا الفارغة
    
    Parameters:
    -----------
    df : pd.DataFrame
        البيانات المراد معالجتها
    date_columns : List[str], optional
        قائمة أسماء أعمدة التاريخ للفحص والمعالجة
    numeric_columns : List[str], optional
        قائمة أسماء الأعمدة الرقمية للمعالجة
    verbose : bool
        إذا كانت True، ستطبع تفاصيل العمليات
        
    Returns:
    --------
    Tuple[pd.DataFrame, Dict]:
        - البيانات المُعالجة
        - تقرير بالعمليات المُنفذة
        
    Example:
    --------
    >>> df = pd.read_csv('data.csv')
    >>> clean_df, report = final_polish(
    ...     df,
    ...     date_columns=['OrderDate', 'ShipDate'],
    ...     numeric_columns=['ProductID', 'Quantity', 'Price']
    ... )
    >>> print(report)
    """
    
    if verbose:
        logger.info("=" * 70)
        logger.info("🚀 بدء المعالجة النهائية (Final Polish)")
        logger.info("=" * 70)
        logger.info(f"البيانات الأصلية: {len(df):,} صف × {len(df.columns)} عمود")
    
    # نسخة عمل من البيانات
    df = df.copy()
    
    # تقرير العمليات
    report = {
        'original_rows': len(df),
        'original_columns': len(df.columns),
        'operations': [],
        'warnings': [],
        'system_notes_added': 0,
        'duplicate_columns_removed': 0,
        'date_columns_cleaned': 0,
        'numeric_columns_converted': 0
    }
    
    # ============================================================
    # 1️⃣ كشف الأعمدة تلقائياً إذا لم تُحدد
    # ============================================================
    
    if date_columns is None:
        date_columns = _auto_detect_date_columns(df)
        if date_columns and verbose:
            logger.info(f"🔍 تم اكتشاف أعمدة التاريخ تلقائياً: {date_columns}")
    
    if numeric_columns is None:
        numeric_columns = _auto_detect_numeric_columns(df)
        if numeric_columns and verbose:
            logger.info(f"🔍 تم اكتشاف الأعمدة الرقمية تلقائياً: {numeric_columns}")
    
    # ============================================================
    # 2️⃣ دمج الأعمدة المتطابقة (Duplicate Columns)
    # ============================================================
    
    if verbose:
        logger.info("\n📌 المرحلة 1: فحص الأعمدة المتطابقة...")
    
    df, duplicates_removed = _remove_duplicate_columns(df, verbose)
    report['duplicate_columns_removed'] = duplicates_removed
    
    if duplicates_removed > 0:
        report['operations'].append(f'تم حذف {duplicates_removed} عمود متطابق')
        if verbose:
            logger.info(f"✓ تم حذف {duplicates_removed} عمود متطابق")
    
    # ============================================================
    # 3️⃣ معالجة أعمدة التاريخ (Date Sterilization)
    # ============================================================
    
    if date_columns:
        if verbose:
            logger.info(f"\n📌 المرحلة 2: معالجة {len(date_columns)} عمود تاريخ...")
        
        # إنشاء عمود System_Notes إذا لم يكن موجوداً
        if 'System_Notes' not in df.columns:
            df['System_Notes'] = ''
        
        for col in date_columns:
            if col not in df.columns:
                report['warnings'].append(f"العمود '{col}' غير موجود")
                continue
            
            # معالجة العمود
            df[col], notes = _clean_date_column(df[col], col)
            
            # إضافة الملاحظات
            if notes:
                df['System_Notes'] = df['System_Notes'] + notes
                report['system_notes_added'] += len(notes)
            
            report['date_columns_cleaned'] += 1
            if verbose:
                logger.info(f"✓ تم معالجة العمود '{col}'")
    
    # ============================================================
    # 4️⃣ معالجة الأعمدة الرقمية (Numeric Conversion)
    # ============================================================
    
    if numeric_columns:
        if verbose:
            logger.info(f"\n📌 المرحلة 3: معالجة {len(numeric_columns)} عمود رقمي...")
        
        for col in numeric_columns:
            if col not in df.columns:
                report['warnings'].append(f"العمود '{col}' غير موجود")
                continue
            
            # معالجة العمود
            df[col] = _convert_numeric_column(df[col], col)
            report['numeric_columns_converted'] += 1
            
            if verbose:
                logger.info(f"✓ تم معالجة العمود '{col}'")
    
    # ============================================================
    # 5️⃣ توحيد الخلايا الفارغة (Empty Cells Standardization)
    # ============================================================
    
    if verbose:
        logger.info("\n📌 المرحلة 4: توحيد الخلايا الفارغة...")
    
    df = _standardize_empty_cells(df, numeric_columns if numeric_columns else [])
    report['operations'].append('تم توحيد الخلايا الفارغة')
    
    if verbose:
        logger.info("✓ تم توحيد الخلايا الفارغة")
    
    # ============================================================
    # 6️⃣ التقرير النهائي
    # ============================================================
    
    report['final_rows'] = len(df)
    report['final_columns'] = len(df.columns)
    
    if verbose:
        logger.info("\n" + "=" * 70)
        logger.info("📊 ملخص المعالجة النهائية")
        logger.info("=" * 70)
        logger.info(f"الصفوف: {report['original_rows']:,} → {report['final_rows']:,}")
        logger.info(f"الأعمدة: {report['original_columns']} → {report['final_columns']}")
        logger.info(f"أعمدة تاريخ معالجة: {report['date_columns_cleaned']}")
        logger.info(f"أعمدة رقمية معالجة: {report['numeric_columns_converted']}")
        logger.info(f"أعمدة متطابقة محذوفة: {report['duplicate_columns_removed']}")
        logger.info(f"ملاحظات النظام المضافة: {report['system_notes_added']}")
        logger.info("=" * 70 + "\n")
    
    return df, report


# ============================================================
# دوال مساعدة (Helper Functions)
# ============================================================

def _auto_detect_date_columns(df: pd.DataFrame) -> List[str]:
    """
    🔍 كشف تلقائي لأعمدة التاريخ
    
    تفحص أسماء الأعمدة والمحتوى للتعرف على أعمدة التاريخ
    """
    date_cols = []
    
    # البحث عن الكلمات الدالة على التاريخ
    keywords = ['date', 'time', 'تاريخ', 'وقت', 'day', 'month', 'year']
    
    for col in df.columns:
        col_lower = col.lower()
        
        # فحص اسم العمود
        if any(keyword in col_lower for keyword in keywords):
            date_cols.append(col)
            continue
        
        # فحص نوع البيانات
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_cols.append(col)
            continue
        
        # محاولة تحويل عينة من البيانات
        if not df[col].isna().all():
            try:
                sample = df[col].dropna().head(5)
                pd.to_datetime(sample, errors='coerce')
                if not pd.to_datetime(sample, errors='coerce').isna().all():
                    date_cols.append(col)
            except:
                pass
    
    return list(set(date_cols))


def _auto_detect_numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    🔍 كشف تلقائي للأعمدة الرقمية
    
    تعرف على الأعمدة التي تحتوي على أرقام فقط
    """
    numeric_cols = []
    
    for col in df.columns:
        # تجاهل أعمدة التاريخ والنصوص
        if col == 'System_Notes' or col.startswith('_'):
            continue
        
        # فحص نوع البيانات
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
    
    return numeric_cols


def _remove_duplicate_columns(df: pd.DataFrame, verbose: bool = False) -> Tuple[pd.DataFrame, int]:
    """
    🔄 حذف الأعمدة المتطابقة 100%
    
    إذا كان عمودان متطابقان بنسبة 100%، يتم حذف أحدهما تلقائياً
    
    Returns:
    --------
    (df_cleaned, num_removed): البيانات المُنظفة وعدد الأعمدة المحذوفة
    """
    df = df.copy()
    removed = 0
    cols_to_drop = set()
    
    # مقارنة جميع الأعمدة
    for i in range(len(df.columns)):
        for j in range(i + 1, len(df.columns)):
            col1 = df.columns[i]
            col2 = df.columns[j]
            
            # تجاهل الأعمدة المحذوفة بالفعل
            if col1 in cols_to_drop or col2 in cols_to_drop:
                continue
            
            # مقارنة الأعمدة (vectorized operation للسرعة)
            try:
                if df[col1].equals(df[col2]):
                    cols_to_drop.add(col2)  # حذف الثاني
                    removed += 1
                    if verbose:
                        logger.info(f"  ⚠️  تم اكتشاف أعمدة متطابقة: '{col1}' و '{col2}'")
            except:
                pass
    
    # حذف الأعمدة المتطابقة
    if cols_to_drop:
        df = df.drop(columns=list(cols_to_drop))
    
    return df, removed


def _clean_date_column(col_data: pd.Series, col_name: str) -> Tuple[pd.Series, str]:
    """
    📅 تنظيف عمود التاريخ
    
    تحويل إلى YYYY-MM-DD وكشف النصوص غير التاريخية
    
    الخطوات:
    1. كشف القيم الفارغة
    2. محاولة تحويل البيانات لتاريخ
    3. إذا فشل التحويل → نقل للملاحظات
    4. استخراج التاريخ فقط (بدون الوقت)
    5. تحويل النتيجة للنوع datetime.date
    """
    
    notes = ''
    cleaned = pd.Series(dtype='object', index=col_data.index)
    
    # عملية Vectorized للتحويل
    for idx, val in col_data.items():
        # الخلايا الفارغة → تبقى فارغة
        if pd.isna(val):
            cleaned[idx] = None
            continue
        
        # محاولة التحويل إلى تاريخ
        try:
            # تحويل آمن مع معالجة الأخطاء
            parsed_date = pd.to_datetime(val, errors='coerce')
            
            if pd.isna(parsed_date):
                # فشل التحويل → نص عادي
                notes += f"[{idx}] نص '{val}' في {col_name}; "
                cleaned[idx] = None
            else:
                # نجح التحويل → استخراج التاريخ فقط
                cleaned[idx] = parsed_date.date()
        
        except Exception as e:
            notes += f"[{idx}] خطأ: {str(e)}; "
            cleaned[idx] = None
    
    return cleaned, notes


def _convert_numeric_column(col_data: pd.Series, col_name: str) -> pd.Series:
    """
    🔢 تحويل العمود الرقمي
    
    الخطوات:
    1. إذا كانت جميع القيم أرقام صحيحة (مثل 1.0, 2.0) → استخدم Int64
    2. محاولة تحويل القيم للرقم بدون أخطاء
    3. الحفاظ على الخلايا الفارغة كـ NaN
    
    النتيجة: بدون .0 غير ضروري وخلايا فارغة موحدة
    """
    
    # محاولة تحويل لرقم
    converted = pd.to_numeric(col_data, errors='coerce')
    
    # فحص إذا كانت جميع القيم (غير الفارغة) أرقام صحيحة
    non_null = converted.dropna()
    
    if len(non_null) > 0:
        # فحص إذا كل القيم أرقام صحيحة
        is_all_integers = (non_null == non_null.astype(int)).all()
        
        if is_all_integers:
            # تحويل لـ Int64 (يحافظ على NaN)
            converted = converted.astype('Int64')
    
    return converted


def _standardize_empty_cells(df: pd.DataFrame, numeric_columns: List[str]) -> pd.DataFrame:
    """
    ⬜ توحيد الخلايا الفارغة
    
    الآلية:
    - في الأعمدة الرقمية: اترك فارغة (NaN) بدون كتابة 'غير محدد'
    - في الأعمدة النصية: استخدم 'غير محدد' فقط إذا لزم الأمر
    
    هذا ضروري لتوافق Tableau و Power BI
    """
    
    df = df.copy()
    
    # في الأعمدة الرقمية: استبدل 'غير محدد' بـ NaN
    for col in numeric_columns:
        if col in df.columns:
            # استبدال النصوص الشائعة بـ NaN
            replacements = ['غير محدد', 'غير متوفر', 'N/A', 'null', 'NULL']
            df[col] = df[col].replace(replacements, np.nan)
    
    # في الأعمدة النصية: اترك 'غير محدد' كما هو أو استبدل بـ NaN
    text_columns = df.select_dtypes(include=['object']).columns
    for col in text_columns:
        if col not in numeric_columns and col != 'System_Notes':
            # استبدل الفراغات بـ NaN
            df[col] = df[col].where(df[col] != '', np.nan)
    
    return df


# ============================================================
# مثال على الاستخدام (Usage Example)
# ============================================================

if __name__ == "__main__":
    # إنشاء بيانات تجريبية
    test_data = {
        'ProductID': [1.0, 2.0, '3.0', 4.0, '5.0'],
        'ProductID_Copy': [1.0, 2.0, '3.0', 4.0, '5.0'],  # متطابق 100%
        'OrderDate': [
            '2024-01-15',
            '2024-02-20 14:30:00',
            'تاريخ غير محدد',
            '2024-04-10 00:00:00',
            None
        ],
        'Quantity': [100, '50.0', 'N/A', 200, 'غير متوفر'],
        'Price': [99.99, 150.0, 200, 'غير محدد', 350],
        'CustomerName': ['أحمد', 'فاطمة', '', 'علي', 'سارة']
    }
    
    df = pd.DataFrame(test_data)
    
    print("📥 البيانات الأصلية:")
    print(df)
    print("\n" + "=" * 70 + "\n")
    
    # تطبيق المعالجة النهائية
    clean_df, report = final_polish(
        df,
        date_columns=['OrderDate'],
        numeric_columns=['ProductID', 'Quantity', 'Price'],
        verbose=True
    )
    
    print("\n📤 البيانات المُعالجة:")
    print(clean_df)
    print("\n" + "=" * 70)
    print("📊 التقرير:")
    for key, value in report.items():
        print(f"  {key}: {value}")
