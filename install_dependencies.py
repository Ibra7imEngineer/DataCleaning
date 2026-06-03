"""
═══════════════════════════════════════════════════════════════════════════════
    INSTALLATION GUIDE
    دليل التثبيت
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import subprocess

def install_packages():
    """
    محاولة ذكية لتثبيت الحزم
    """
    
    packages = [
        'streamlit',
        'pandas',
        'numpy',
        'openpyxl',
        'xlsxwriter',
        'plotly',
        'thefuzz',
        'python-Levenshtein',
        'chardet',
        'python-dateutil',
    ]
    
    print("🔧 إبدأ بتثبيت المتطلبات...")
    print("=" * 80)
    
    failed_packages = []
    
    for package in packages:
        print(f"\n📦 جاري تثبيت: {package}...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '--quiet', '--no-cache-dir', package
            ])
            print(f"✅ {package} تم تثبيته بنجاح")
        except Exception as e:
            print(f"⚠️ خطأ في تثبيت {package}: {e}")
            failed_packages.append(package)
    
    print("\n" + "=" * 80)
    if failed_packages:
        print(f"❌ فشل تثبيت: {', '.join(failed_packages)}")
        print("\n💡 حل بديل:")
        print("استخدم Anaconda:")
        print("  conda install -r requirements.txt")
    else:
        print("✅ تم تثبيت جميع المتطلبات بنجاح!")
    
    return len(failed_packages) == 0

if __name__ == "__main__":
    success = install_packages()
    sys.exit(0 if success else 1)
