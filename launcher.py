"""
Master Launcher: Semantic Clustering & Harmonization Platform
Central entry point for running tests, examples, and Streamlit UI
"""

import sys
import subprocess
import os
from pathlib import Path


def print_header():
    """Print colorful header"""
    header = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║     ✨ SEMANTIC CLUSTERING & HARMONIZATION PLATFORM ✨           ║
    ║     Independent Fuzzy Matching with Arabic Support               ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    print(header)


def print_menu():
    """Print main menu options"""
    menu = """
    CHOOSE AN OPTION:
    
    🧪 1. Run Test Suite
       └─ Validates Arabic normalization, clustering, and logging
       
    💡 2. Run Quick Start Examples
       └─ 7 practical examples (Arabic products, addresses, etc.)
       
    🌐 3. Launch Streamlit UI
       └─ Beautiful interactive web interface
       
    📋 4. Run Comprehensive Test + Examples
       └─ Full validation workflow
       
    ⚙️  5. Check Installation
       └─ Verify all dependencies are installed
       
    ❌ 0. Exit
    
    """
    print(menu)


def check_installation():
    """Check if all required packages are installed"""
    print("\n🔍 Checking Installation...\n")
    
    required_packages = {
        'pandas': 'pandas>=1.3.0',
        'rapidfuzz': 'rapidfuzz>=3.0.0',
    }
    
    optional_packages = {
        'openpyxl': 'openpyxl>=3.8.0 (for Excel support)',
        'streamlit': 'streamlit>=1.28.0 (for Streamlit UI)',
    }
    
    all_good = True
    
    print("📦 Required Packages:")
    for pkg_name, pkg_spec in required_packages.items():
        try:
            __import__(pkg_name)
            print(f"  ✅ {pkg_spec}")
        except ImportError:
            print(f"  ❌ {pkg_spec} - MISSING")
            all_good = False
    
    print("\n📦 Optional Packages:")
    for pkg_name, pkg_spec in optional_packages.items():
        try:
            __import__(pkg_name)
            print(f"  ✅ {pkg_spec}")
        except ImportError:
            print(f"  ⚠️  {pkg_spec} - Not installed")
    
    if all_good:
        print("\n✅ All required packages are installed!")
        return True
    else:
        print("\n❌ Some required packages are missing.")
        print("\nTo install missing packages, run:")
        print("  pip install pandas rapidfuzz openpyxl streamlit")
        return False


def run_tests():
    """Run the test suite"""
    print("\n" + "="*70)
    print("🧪 RUNNING TEST SUITE")
    print("="*70)
    
    if not os.path.exists('test_semantic_clustering.py'):
        print("❌ test_semantic_clustering.py not found!")
        return
    
    try:
        result = subprocess.run(
            [sys.executable, 'test_semantic_clustering.py'],
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✅ Test Suite Completed Successfully!")
        else:
            print(f"\n❌ Test Suite Failed with code {result.returncode}")
            
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")


def run_examples():
    """Run the quick start examples"""
    print("\n" + "="*70)
    print("💡 RUNNING QUICK START EXAMPLES")
    print("="*70)
    
    if not os.path.exists('quick_start_examples.py'):
        print("❌ quick_start_examples.py not found!")
        return
    
    try:
        result = subprocess.run(
            [sys.executable, 'quick_start_examples.py'],
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✅ Examples Completed Successfully!")
        else:
            print(f"\n❌ Examples Failed with code {result.returncode}")
            
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")


def run_streamlit_ui():
    """Launch the Streamlit UI"""
    print("\n" + "="*70)
    print("🌐 LAUNCHING STREAMLIT UI")
    print("="*70)
    
    if not os.path.exists('streamlit_semantic_clustering.py'):
        print("❌ streamlit_semantic_clustering.py not found!")
        return
    
    print("\n📝 Starting Streamlit server...")
    print("   🌍 Access at: http://localhost:8501")
    print("   Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'streamlit', 'run', 'streamlit_semantic_clustering.py'],
            check=False
        )
    except KeyboardInterrupt:
        print("\n✋ Streamlit server stopped.")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {str(e)}")
        print("\nTo install Streamlit, run:")
        print("  pip install streamlit")


def run_full_workflow():
    """Run tests and examples in sequence"""
    print("\n" + "="*70)
    print("📋 RUNNING COMPREHENSIVE WORKFLOW (Tests + Examples)")
    print("="*70)
    
    print("\n[1/2] Running Test Suite...")
    run_tests()
    
    print("\n\n[2/2] Running Examples...")
    run_examples()
    
    print("\n" + "="*70)
    print("✅ COMPREHENSIVE WORKFLOW COMPLETED!")
    print("="*70)


def show_quick_reference():
    """Show quick reference guide"""
    reference = """
    
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                       QUICK REFERENCE GUIDE                       ║
    ╚═══════════════════════════════════════════════════════════════════╝
    
    1️⃣  BASIC USAGE (Python)
    ─────────────────────────────────────────────────────────────────────
    
    from semantic_clustering_arabic import semantic_clustering_harmonization
    
    # Load and clean your data
    df_clean, logs = semantic_clustering_harmonization(df)
    
    # Export results
    df_clean.to_csv('cleaned.csv', index=False)
    
    
    2️⃣  STREAMLIT WEB UI
    ─────────────────────────────────────────────────────────────────────
    
    streamlit run streamlit_semantic_clustering.py
    
    Then open: http://localhost:8501
    
    
    3️⃣  FINE-TUNING PARAMETERS
    ─────────────────────────────────────────────────────────────────────
    
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=90,        # 70-100 (higher = stricter)
        max_unique_values=500,     # Skip high-cardinality columns
        min_unique_values=2        # Skip low-cardinality columns
    )
    
    
    4️⃣  ARABIC NORMALIZATION
    ─────────────────────────────────────────────────────────────────────
    
    from semantic_clustering_arabic import normalize_arabic_text
    
    normalized = normalize_arabic_text('ترابيزة')  # → 'تربيزه'
    
    Transformations:
    • أ, إ, آ → ا    (hamza variants)
    • ة → ه           (taa marbuta)
    • ى → ي           (alef maksura)
    • Removes diacritics
    • Strips whitespace
    
    
    5️⃣  VIEWING LOGS
    ─────────────────────────────────────────────────────────────────────
    
    from semantic_clustering_arabic import format_logs_for_display
    
    formatted_logs = format_logs_for_display(logs)
    print(formatted_logs)
    
    
    📚 DOCUMENTATION
    ─────────────────────────────────────────────────────────────────────
    
    • README: SEMANTIC_CLUSTERING_README.md
    • API Reference: See docstrings in semantic_clustering_arabic.py
    • Examples: quick_start_examples.py
    • Tests: test_semantic_clustering.py
    
    
    🔗 FILES STRUCTURE
    ─────────────────────────────────────────────────────────────────────
    
    semantic_clustering_arabic.py      ← Main engine
    streamlit_semantic_clustering.py   ← Web UI
    test_semantic_clustering.py        ← Test suite
    quick_start_examples.py            ← Examples
    SEMANTIC_CLUSTERING_README.md      ← Full documentation
    launcher.py                        ← This file
    
    
    ⚡ QUICK TIPS
    ─────────────────────────────────────────────────────────────────────
    
    • Threshold too high? → Set fuzzy_threshold=85
    • Over-harmonizing? → Set fuzzy_threshold=95
    • Columns not processing? → Check unique value count
    • Need to skip IDs? → Set max_unique_values appropriately
    • Testing? → Run: python test_semantic_clustering.py
    • Examples? → Run: python quick_start_examples.py
    
    """
    print(reference)


def main():
    """Main menu loop"""
    print_header()
    
    while True:
        print_menu()
        
        try:
            choice = input("👉 Enter your choice (0-5): ").strip()
            
            if choice == '1':
                run_tests()
            elif choice == '2':
                run_examples()
            elif choice == '3':
                run_streamlit_ui()
            elif choice == '4':
                run_full_workflow()
            elif choice == '5':
                if not check_installation():
                    print("\n❌ Installation issues detected. Please fix before proceeding.")
            elif choice == '0':
                print("\n👋 Thank you for using Semantic Clustering & Harmonization Platform!")
                show_quick_reference()
                sys.exit(0)
            else:
                print("\n❌ Invalid choice. Please enter a number between 0-5.")
            
            input("\n Press Enter to continue...")
            print("\n" * 2)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            input("\n Press Enter to continue...")
            print("\n" * 2)


if __name__ == "__main__":
    # Check if any argument provided
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == '--test':
            run_tests()
        elif command == '--examples':
            run_examples()
        elif command == '--streamlit':
            run_streamlit_ui()
        elif command == '--check':
            check_installation()
        elif command == '--help':
            print("""
Usage:
  python launcher.py                    ← Interactive menu
  python launcher.py --test             ← Run tests only
  python launcher.py --examples         ← Run examples only
  python launcher.py --streamlit        ← Launch Streamlit UI
  python launcher.py --check            ← Check installation
  python launcher.py --help             ← Show this help
            """)
        else:
            print(f"Unknown command: {command}")
            print("Use --help for usage information")
    else:
        # Run interactive menu
        main()
