from dataclasses import dataclass
from typing import Dict


@dataclass
class ClusteringConfig:
    fuzzy_threshold: int = 90
    max_unique_values: int = 500
    min_unique_values: int = 2
    description: str = ""


STRICT_MODE = ClusteringConfig(
    fuzzy_threshold=95,
    max_unique_values=300,
    min_unique_values=2,
    description="Very strict matching - minimize false positives. Use for precise categories and brand names.",
)

BALANCED_MODE = ClusteringConfig(
    fuzzy_threshold=90,
    max_unique_values=500,
    min_unique_values=2,
    description="Balanced default mode for general use cases.",
)

PERMISSIVE_MODE = ClusteringConfig(
    fuzzy_threshold=82,
    max_unique_values=500,
    min_unique_values=2,
    description="Permissive matching for noisy user-entered data.",
)

ARABIC_OPTIMIZED = ClusteringConfig(
    fuzzy_threshold=90,
    max_unique_values=300,
    min_unique_values=2,
    description="Optimized for Arabic text and mixed Arabic-English data.",
)

HIGH_CARDINALITY_PROTECTION = ClusteringConfig(
    fuzzy_threshold=90,
    max_unique_values=100,
    min_unique_values=3,
    description="Protects high-cardinality columns by limiting processing to smaller domains.",
)

AGGRESSIVE_MODE = ClusteringConfig(
    fuzzy_threshold=75,
    max_unique_values=500,
    min_unique_values=2,
    description="Aggressive normalization for very noisy data. Use with caution.",
)

PRODUCTION_MODE = ClusteringConfig(
    fuzzy_threshold=92,
    max_unique_values=200,
    min_unique_values=2,
    description="Production-safe defaults for business-critical pipelines.",
)

PRESET_DESCRIPTIONS: Dict[str, str] = {
    'STRICT': STRICT_MODE.description,
    'BALANCED': BALANCED_MODE.description,
    'PERMISSIVE': PERMISSIVE_MODE.description,
    'ARABIC_OPTIMIZED': ARABIC_OPTIMIZED.description,
    'HIGH_CARDINALITY_PROTECTION': HIGH_CARDINALITY_PROTECTION.description,
    'AGGRESSIVE': AGGRESSIVE_MODE.description,
    'PRODUCTION': PRODUCTION_MODE.description,
}


def choose_preset_by_scenario(scenario: str) -> ClusteringConfig:
    lookup = {
        'STRICT': STRICT_MODE,
        'BALANCED': BALANCED_MODE,
        'PERMISSIVE': PERMISSIVE_MODE,
        'ARABIC_OPTIMIZED': ARABIC_OPTIMIZED,
        'HIGH_CARDINALITY_PROTECTION': HIGH_CARDINALITY_PROTECTION,
        'AGGRESSIVE': AGGRESSIVE_MODE,
        'PRODUCTION': PRODUCTION_MODE,
    }
    return lookup.get(scenario.upper(), BALANCED_MODE)
