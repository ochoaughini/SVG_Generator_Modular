# src/svg_generator/config.py
"""Global constants and configuration settings."""

from typing import Set

# Kaggle-like competition constraints
MAX_SVG_SIZE_BYTES: int = 10 * 1024  # 10KB
ALLOWED_SVG_TAGS: Set[str] = {
    "svg", "path", "circle", "rect", "polygon", "g", "defs",
    "linearGradient", "radialGradient", "stop", "pattern"
}
PROHIBITED_SVG_ATTRIBUTES: Set[str] = {"style", "filter", "href", "class", "id"} # Allow 'id' for defs
# Note: 'id' is needed for defs, so sanitize.py needs to be smart about it.
# `xlink:href` is also often prohibited, `href` is the SVG 2 replacement.

MAX_DEPTH_LAYERS: int = 5
Z_INDEX_RANGE: tuple[int, int] = (0, 1000)

MAX_RECURSION_DEPTH_GENERATION: int = 3
SHAPE_COMPLEXITY_PATH_POINTS_CAP: int = 100

# Default style profile if none specified
DEFAULT_STYLE_PROFILE_NAME: str = "default"
STYLE_PROFILES_DIR: str = "style_profiles" # Relative to package or absolute path

# Optimization settings
SCOUR_OPTIONS = {
    "remove_metadata": True,
    "strip_xml_prolog": True,
    "strip_comments": True,
    "shorten_ids": True, # Be careful if IDs are referenced in a specific way
    "enable_viewboxing": True,
    "indent_type": "none", # No indentation for smaller size
    "strip_graphical_attributes": "all", # Can be aggressive
    "protect_ids_prefixes": ["gradient-", "pattern-"] # Example prefixes to protect
}
