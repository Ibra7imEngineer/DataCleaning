"""Configuration presets package."""

from .config_presets import (
    ClusteringConfig,
    STRICT_MODE,
    BALANCED_MODE,
    PERMISSIVE_MODE,
    ARABIC_OPTIMIZED,
    HIGH_CARDINALITY_PROTECTION,
    AGGRESSIVE_MODE,
    PRODUCTION_MODE,
    PRESET_DESCRIPTIONS,
    choose_preset_by_scenario,
)

__all__ = [
    "ClusteringConfig",
    "STRICT_MODE",
    "BALANCED_MODE",
    "PERMISSIVE_MODE",
    "ARABIC_OPTIMIZED",
    "HIGH_CARDINALITY_PROTECTION",
    "AGGRESSIVE_MODE",
    "PRODUCTION_MODE",
    "PRESET_DESCRIPTIONS",
    "choose_preset_by_scenario",
]