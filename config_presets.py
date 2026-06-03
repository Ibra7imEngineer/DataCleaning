"""
Configuration Template: Semantic Clustering Presets
Predefined configurations for common use cases
"""

from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class ClusteringConfig:
    """Configuration dataclass for semantic clustering"""
    fuzzy_threshold: int = 90
    max_unique_values: int = 500
    min_unique_values: int = 2
    normalize_func: Optional[Callable] = None
    description: str = ""


# ============================================================================
# PRESET CONFIGURATIONS FOR COMMON SCENARIOS
# ============================================================================

# 1. STRICT MODE (Avoid false positives)
STRICT_MODE = ClusteringConfig(
    fuzzy_threshold=95,
    max_unique_values=300,
    min_unique_values=2,
    description="Very strict matching - minimize false positives. Use for: precise categories, brand names"
)

# 2. BALANCED MODE (Default - recommended)
BALANCED_MODE = ClusteringConfig(
    fuzzy_threshold=90,
    max_unique_values=500,
    min_unique_values=2,
    description="Balanced approach - good for most use cases. Use for: general product names, addresses"
)

# 3. PERMISSIVE MODE (Catch all typos)
PERMISSIVE_MODE = ClusteringConfig(
    fuzzy_threshold=82,
    max_unique_values=500,
    min_unique_values=2,
    description="Permissive matching - catch most typos. Use for: user-entered data, manual entries"
)

# 4. ARABIC-OPTIMIZED MODE
ARABIC_OPTIMIZED = ClusteringConfig(
    fuzzy_threshold=90,
    max_unique_values=300,
    min_unique_values=2,
    description="Optimized for Arabic text. Use for: Arabic products, names, locations"
)

# 5. HIGH-CARDINALITY PROTECTION MODE
HIGH_CARDINALITY_PROTECTION = ClusteringConfig(
    fuzzy_threshold=90,
    max_unique_values=100,  # Protect more columns
    min_unique_values=3,
    description="Protect high-cardinality columns. Use for: datasets with IDs, emails, codes"
)

# 6. AGGRESSIVE MODE (Maximum harmonization)
AGGRESSIVE_MODE = ClusteringConfig(
    fuzzy_threshold=75,
    max_unique_values=500,
    min_unique_values=2,
    description="Aggressive harmonization. Use for: extremely messy data, heavy typo correction"
)

# 7. PRODUCTION MODE (Safe defaults)
PRODUCTION_MODE = ClusteringConfig(
    fuzzy_threshold=92,
    max_unique_values=200,
    min_unique_values=2,
    description="Production-safe settings. Recommended for: live data processing, business-critical systems"
)


# ============================================================================
# PRESET DESCRIPTIONS
# ============================================================================

PRESET_DESCRIPTIONS = {
    'STRICT': """
    Threshold: 95 | Max Unique: 300 | Min Unique: 2
    
    ✅ Best for:
    • Brand names (Samsung, Iphone, etc.)
    • Category hierarchies
    • Status fields (Active, Pending, Completed)
    • Anything where precision > recall
    
    ❌ Not recommended for:
    • User-entered data with many typos
    • Addresses with variations
    • Product names from multiple sources
    
    Example Impact:
    apple, appl → NOT matched (different enough)
    ترابيزة, ترابيزه → MATCHED (normalized form very similar)
    """,
    
    'BALANCED': """
    Threshold: 90 | Max Unique: 500 | Min Unique: 2
    
    ✅ Best for:
    • General product names
    • Addresses with minor variations
    • Category descriptions
    • Most general-purpose use cases
    
    ✓ Good balance between:
    • Catching real typos
    • Avoiding false matches
    • Performance
    
    Example Impact:
    apple, appl → MATCHED (typo)
    table, cable → NOT matched (too different)
    """,
    
    'PERMISSIVE': """
    Threshold: 82 | Max Unique: 500 | Min Unique: 2
    
    ✅ Best for:
    • Heavily user-entered data
    • Multiple language/script sources
    • Data quality unknown
    • Manual entry from paper forms
    
    ⚠️  Watch out for:
    • May merge unrelated items
    • Higher false positive rate
    • Requires validation before use
    
    Example Impact:
    apple, aple → MATCHED (even transpositions)
    """,
    
    'ARABIC_OPTIMIZED': """
    Threshold: 90 | Max Unique: 300 | Min Unique: 2
    
    ✅ Best for:
    • Arabic product names
    • Arabic addresses
    • Mixed Arabic-English data
    • E-commerce with Arabic customers
    
    ✓ Features:
    • Arabic normalization included
    • Appropriate threshold for Arabic
    • Protects ID columns
    
    Example Impact:
    ترابيزة, ترابيزه → MATCHED ✓
    كنبة, ترابيزة → NOT matched ✓
    """,
    
    'HIGH_CARDINALITY_PROTECTION': """
    Threshold: 90 | Max Unique: 100 | Min Unique: 3
    
    ✅ Best for:
    • Datasets with many ID columns
    • Email address columns
    • Order ID columns
    • Date/timestamp columns
    
    ✓ Protection:
    • Columns with > 100 unique values = SKIPPED
    • Requires at least 3 unique values
    • Prevents accidental ID matching
    
    Example:
    EmailID (500 unique) → SKIPPED ✓
    ProductName (10 unique) → PROCESSED ✓
    """,
    
    'AGGRESSIVE': """
    Threshold: 75 | Max Unique: 500 | Min Unique: 2
    
    ✅ Best for:
    • Data entry from OCR
    • Extremely messy sources
    • Maximum harmonization needed
    • Quality-agnostic sources
    
    ⚠️  Strong warnings:
    • WILL merge some different items
    • ALWAYS review before use
    • Only for non-critical data
    • Requires human validation
    
    Example Impact:
    apple, opal → May be matched! (75% similarity)
    """,
    
    'PRODUCTION': """
    Threshold: 92 | Max Unique: 200 | Min Unique: 2
    
    ✅ Best for:
    • Live systems
    • Business-critical data
    • Automated pipelines
    • Data warehouse loading
    
    ✓ Safe design:
    • Higher threshold (fewer false positives)
    • Protects ID columns
    • Proven in production environments
    • Recommended by experts
    
    Example:
    table, tabel → MATCHED (real typo)
    Samsung, LG → NOT matched (different brands)
    """
}


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_using_presets():
    """Show how to use the preset configurations"""
    
    from semantic_clustering_arabic import semantic_clustering_harmonization
    import pandas as pd
    
    # Create sample data
    df = pd.DataFrame({
        'Product': ['iPhone', 'Iphone', 'IPHONE', 'Samsung', 'Samsng']
    })
    
    # Method 1: Use a preset directly
    print("Using BALANCED_MODE preset:")
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=BALANCED_MODE.fuzzy_threshold,
        max_unique_values=BALANCED_MODE.max_unique_values,
        min_unique_values=BALANCED_MODE.min_unique_values
    )
    print(df_clean)
    
    # Method 2: Customize a preset
    print("\nCustomizing STRICT_MODE:")
    custom_config = STRICT_MODE
    custom_config.fuzzy_threshold = 93  # Slightly more permissive
    
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=custom_config.fuzzy_threshold,
        max_unique_values=custom_config.max_unique_values,
        min_unique_values=custom_config.min_unique_values
    )
    print(df_clean)


def choose_preset_by_scenario(scenario: str) -> ClusteringConfig:
    """
    Helper function to choose appropriate preset based on scenario
    
    Parameters:
        scenario: 'arabic', 'ecommerce', 'addresses', 'ids', 'strict', 'aggressive'
    
    Returns:
        ClusteringConfig object with appropriate settings
    """
    
    scenario = scenario.lower().strip()
    
    presets = {
        'arabic': ARABIC_OPTIMIZED,
        'ecommerce': BALANCED_MODE,
        'addresses': BALANCED_MODE,
        'ids': HIGH_CARDINALITY_PROTECTION,
        'strict': STRICT_MODE,
        'aggressive': AGGRESSIVE_MODE,
        'production': PRODUCTION_MODE,
        'permissive': PERMISSIVE_MODE,
    }
    
    if scenario in presets:
        return presets[scenario]
    else:
        print(f"Unknown scenario: {scenario}")
        print(f"Available: {list(presets.keys())}")
        return BALANCED_MODE  # Default


# ============================================================================
# QUICK REFERENCE
# ============================================================================

def print_preset_quick_reference():
    """Print quick reference for all presets"""
    
    presets = {
        'STRICT': STRICT_MODE,
        'BALANCED': BALANCED_MODE,
        'PERMISSIVE': PERMISSIVE_MODE,
        'ARABIC': ARABIC_OPTIMIZED,
        'HIGH_CARDINALITY': HIGH_CARDINALITY_PROTECTION,
        'AGGRESSIVE': AGGRESSIVE_MODE,
        'PRODUCTION': PRODUCTION_MODE,
    }
    
    print("\n" + "="*70)
    print("SEMANTIC CLUSTERING - PRESET QUICK REFERENCE")
    print("="*70 + "\n")
    
    for name, config in presets.items():
        print(f"📌 {name}")
        print(f"   Threshold: {config.fuzzy_threshold} | Max: {config.max_unique_values} | Min: {config.min_unique_values}")
        print(f"   {config.description}")
        print()


def get_recommendation(data_source: str) -> ClusteringConfig:
    """
    Get recommended preset based on data source
    
    Parameters:
        data_source: 'user_input', 'manual_entry', 'ocr', 'database', 'api', 'mixed'
    
    Returns:
        Recommended ClusteringConfig
    """
    
    recommendations = {
        'user_input': PERMISSIVE_MODE,
        'manual_entry': PERMISSIVE_MODE,
        'ocr': AGGRESSIVE_MODE,
        'database': PRODUCTION_MODE,
        'api': BALANCED_MODE,
        'mixed': BALANCED_MODE,
        'arabic': ARABIC_OPTIMIZED,
        'production': PRODUCTION_MODE,
    }
    
    if data_source.lower() in recommendations:
        return recommendations[data_source.lower()]
    else:
        return BALANCED_MODE


# ============================================================================
# EXAMPLE WORKFLOWS
# ============================================================================

def workflow_example_1_ecommerce():
    """Workflow for e-commerce product data"""
    from semantic_clustering_arabic import semantic_clustering_harmonization
    import pandas as pd
    
    # Use BALANCED_MODE for general product names
    config = BALANCED_MODE
    
    print(f"\n🛒 E-Commerce Workflow (using {config.description})")
    print("="*70)
    
    # Simulate loading data
    df = pd.DataFrame({
        'ProductName': ['Samsung', 'Samsng', 'Samsnug', 'iPhone', 'Iphone']
    })
    
    print("Original data:")
    print(df)
    
    # Apply harmonization
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=config.fuzzy_threshold,
        max_unique_values=config.max_unique_values,
        min_unique_values=config.min_unique_values
    )
    
    print("\nCleaned data:")
    print(df_clean)
    print(f"\nReduced from {df['ProductName'].nunique()} to {df_clean['ProductName'].nunique()} unique values")


def workflow_example_2_addresses():
    """Workflow for address data"""
    from semantic_clustering_arabic import semantic_clustering_harmonization
    import pandas as pd
    
    # Use BALANCED_MODE for addresses
    config = BALANCED_MODE
    
    print(f"\n📍 Address Workflow (using {config.description})")
    print("="*70)
    
    df = pd.DataFrame({
        'City': ['Cairo', 'Cairo', 'Cario', 'New Cairo', 'New Cairo', 'New Cario']
    })
    
    print("Original data:")
    print(df)
    
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=config.fuzzy_threshold,
        max_unique_values=config.max_unique_values,
        min_unique_values=config.min_unique_values
    )
    
    print("\nCleaned data:")
    print(df_clean)


def workflow_example_3_production():
    """Workflow for production systems"""
    from semantic_clustering_arabic import semantic_clustering_harmonization
    import pandas as pd
    
    config = PRODUCTION_MODE
    
    print(f"\n🏭 Production System Workflow (using {config.description})")
    print("="*70)
    
    # Large dataset with IDs
    df = pd.DataFrame({
        'OrderID': [f'ORD{i}' for i in range(1000, 1100)],  # Will be skipped
        'Status': ['Active', 'Activ'] * 50,                  # Will be processed
        'Category': ['Electronics', 'Electrncs'] * 50        # Will be processed
    })
    
    print(f"Dataset: {len(df)} rows")
    print(f"OrderID unique: {df['OrderID'].nunique()} (will be SKIPPED)")
    print(f"Status unique: {df['Status'].nunique()}")
    print(f"Category unique: {df['Category'].nunique()}")
    
    df_clean, logs = semantic_clustering_harmonization(
        df,
        fuzzy_threshold=config.fuzzy_threshold,
        max_unique_values=config.max_unique_values,
        min_unique_values=config.min_unique_values
    )
    
    print("\nAfter harmonization:")
    print(f"Status unique: {df_clean['Status'].nunique()}")
    print(f"Category unique: {df_clean['Category'].nunique()}")


# ============================================================================
# INTERACTIVE PRESET SELECTOR
# ============================================================================

def interactive_preset_selection():
    """Interactive menu to select appropriate preset"""
    
    print("\n" + "="*70)
    print("INTERACTIVE PRESET SELECTOR")
    print("="*70 + "\n")
    
    questions = [
        ("What type of data?", [
            "E-commerce products",
            "Addresses/Locations",
            "Customer names",
            "Status/Categories",
            "Arabic text",
            "Other"
        ]),
        ("What's your data quality?", [
            "Excellent (database)",
            "Good (API/structured)",
            "Fair (user-entered)",
            "Poor (OCR/manual)",
            "Unknown"
        ]),
        ("What's more important?", [
            "Precision (avoid false matches)",
            "Recall (catch all variations)",
            "Balance",
            "Production safety"
        ])
    ]
    
    print("Answer these questions to get a recommendation:\n")
    
    # Simulated answers
    answers = ["E-commerce products", "Good (API/structured)", "Balance"]
    
    print("Based on your answers:")
    print("✓ Data type: E-commerce products")
    print("✓ Data quality: Good")
    print("✓ Priority: Balance\n")
    
    print("🎯 RECOMMENDED PRESET: BALANCED_MODE")
    print(BALANCED_MODE.description)


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "█"*70)
    print("█" + " CONFIGURATION PRESETS FOR SEMANTIC CLUSTERING ".center(68) + "█")
    print("█"*70)
    
    # Print quick reference
    print_preset_quick_reference()
    
    # Print individual descriptions
    for preset_name, description in PRESET_DESCRIPTIONS.items():
        print(f"\n📖 {preset_name} MODE:")
        print(description)
    
    # Run example workflows
    print("\n" + "="*70)
    print("EXAMPLE WORKFLOWS")
    print("="*70)
    
    try:
        workflow_example_1_ecommerce()
        workflow_example_2_addresses()
        workflow_example_3_production()
    except Exception as e:
        print(f"Note: Workflows require semantic_clustering_arabic module: {e}")
    
    print("\n" + "█"*70)
    print("█" + " Configuration presets loaded successfully! ".center(68) + "█")
    print("█"*70 + "\n")
