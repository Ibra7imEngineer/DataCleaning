"""
Test Script: Verify Professional Arabic Name Normalization
Demonstrates how the enhanced normalization handles name variations
"""

import re

def _normalize_single_text(val) -> str:
    """
    Comprehensive Arabic text normalization for professional data cleaning.
    Handles name variations and spelling differences professionally.
    """
    if not isinstance(val, str):
        val = str(val)
    
    # Remove ALL Arabic Diacritical Marks
    diacritical_marks = [
        "\u064B",  # Fathatan
        "\u064C",  # Dammatan
        "\u064D",  # Kasratan
        "\u064E",  # Fatha
        "\u064F",  # Damma
        "\u0650",  # Kasra
        "\u0651",  # Shadda
        "\u0652",  # Sukun
        "\u0653",  # Maddah
        "\u0654",  # Hamza above
        "\u0655",  # Hamza below
        "\u0656",  # Subscript Alef
        "\u0657",  # Inverted Damma
        "\u0658",  # Mark Noon Ghunna
        "\u0670",  # Superscript Alef
    ]
    for mark in diacritical_marks:
        val = val.replace(mark, "")
    
    # Remove Zero-Width Characters
    val = val.replace("\u0640", "")  # Kashida / Tatweel
    val = val.replace("\u200C", "")  # Zero Width Non-Joiner
    val = val.replace("\u200D", "")  # Zero Width Joiner
    val = val.replace("\u200E", "")  # Left-to-Right Mark
    val = val.replace("\u200F", "")  # Right-to-Left Mark
    val = val.replace("\uFEFF", "")  # Zero Width No-Break Space
    
    # Standardize Alef Variants
    val = val.replace("أ", "ا")
    val = val.replace("إ", "ا")
    val = val.replace("آ", "ا")
    val = val.replace("ٱ", "ا")
    
    # Standardize Hamza on Waw and Yeh
    val = val.replace("ؤ", "و")
    val = val.replace("ئ", "ي")
    
    # Standardize Teh Marbuta to Heh
    val = val.replace("ة", "ه")
    
    # Standardize Yeh Variants
    val = val.replace("ى", "ي")
    
    # Normalize Whitespace
    val = re.sub(r"\s+", " ", val).strip()
    
    return val


# Test Cases
test_cases = [
    ("هبة", "هبه"),           # Teh Marbuta vs Heh
    ("هبَة", "هبه"),          # With Fatha mark
    ("هَبَة", "هبه"),         # With multiple Fatha marks
    ("محمَّد", "محمد"),       # With Shadda (doubling mark)
    ("أسماء", "اسماء"),       # Alef with Hamza
    ("إسلام", "اسلام"),       # Alef with Hamza below
    ("آمنة", "امنه"),         # Alef with Madda + Teh Marbuta
    ("فاطمـــة", "فاطمه"),    # Kashida removal + Teh Marbuta
    ("علـــي", "علي"),        # Kashida removal
    ("موسى", "موسي"),         # Alef Maksura
    ("ؤلد", "ولد"),           # Waw with Hamza → Waw
    ("سؤال", "سوال"),         # Waw with Hamza in word
    ("شئ", "شي"),             # Yeh with Hamza → Yeh
    ("مسئول", "مسيول"),       # Yeh with Hamza in word
]

print("=" * 60)
print("🧹 اختبار تطبيع الأسماء العربية المتقدم")
print("Testing Professional Arabic Name Normalization")
print("=" * 60)
print()

all_passed = True
for original, expected_normalized in test_cases:
    actual = _normalize_single_text(original)
    passed = actual == expected_normalized
    all_passed = all_passed and passed
    
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | '{original}' → '{actual}'")
    if not passed:
        print(f"         Expected: '{expected_normalized}'")

print()
print("=" * 60)
if all_passed:
    print("✅ All tests passed! Name normalization working professionally.")
else:
    print("⚠️  Some tests failed. Please review the normalization logic.")
print("=" * 60)

# Practical Example: Name Deduplication
print()
print("💡 PRACTICAL EXAMPLE: Name Deduplication")
print("-" * 60)

sample_names = [
    "هبة",      # Normal
    "هبه",      # Variant 1
    "هَبَة",    # Variant 2 with marks
    "محمد",     # Another person
    "محمَّد",   # Variant with Shadda
    "فاطمة",    # Another person
    "فاطمـــة", # Variant with Kashida
]

print("\nOriginal names (may contain duplicates):")
for name in sample_names:
    print(f"  - {name}")

normalized_names = list(set(_normalize_single_text(n) for n in sample_names))
print(f"\nAfter normalization ({len(sample_names)} → {len(normalized_names)} unique names):")
for name in sorted(normalized_names):
    print(f"  ✓ {name}")

print()
print(f"Result: {len(sample_names) - len(normalized_names)} duplicates identified and merged professionally!")
