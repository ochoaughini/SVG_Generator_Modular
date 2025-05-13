# src/svg_generator/style/style_profiles.py
import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class StyleProfile:
    """Represents a style profile loaded from a JSON configuration."""
    def __init__(self, data: Dict[str, Any]):
        self.name: str = data.get("name", "Unnamed Profile")
        self.description: str = data.get("description", "")
        self.palette: list[str] = data.get("palette", ["#000000"])
        self.background_color: str = data.get("background_color", "#FFFFFF")
        self.line_width: float = float(data.get("line_width", 1.0))
        self.opacity: float = float(data.get("opacity", 1.0))
        # Add more style attributes as needed (e.g., font, texture hints)
        self.shape_complexity: str = data.get("shape_complexity", "simple") # e.g. simple, detailed
        self.raw_data = data # Store raw data for access to custom fields
        logger.debug(f"StyleProfile '{self.name}' initialized.")

    @classmethod
    def load(cls, profile_name: str, custom_profiles_dir: Optional[str] = None) -> 'StyleProfile':
        """
        Loads a style profile from a JSON file.

        Args:
            profile_name: The name of the profile (without .json extension).
            custom_profiles_dir: Optional custom directory to look for profiles.
                                If None, uses a default path.

        Returns:
            An instance of StyleProfile.

        Raises:
            FileNotFoundError: If the profile JSON file is not found.
            json.JSONDecodeError: If the JSON is malformed.
        """
        filename = f"{profile_name}.json"
        
        if custom_profiles_dir:
            filepath = os.path.join(custom_profiles_dir, filename)
        else:
            # Default path: relative to this file, in a subdirectory 'style_profiles_data'
            # This needs robust path handling for installed packages (e.g. importlib.resources)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(base_dir, "style_profiles_data", filename)
            # For now, let's assume it's relative to where cli.py searched.
            # This part is tricky with packaging. The cli.py already attempts to find this.

        logger.info(f"Attempting to load style profile: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(data)
        except FileNotFoundError:
            logger.error(f"Style profile file not found: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from style profile '{filepath}': {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading style profile '{filepath}': {e}")
            raise

    def get_color(self, index: int = 0) -> str:
        """Returns a color from the palette, cycling if index is out of bounds."""
        if not self.palette:
            return "#000000" # Default fallback color
        return self.palette[index % len(self.palette)]

    def __repr__(self) -> str:
        return f"<StyleProfile name='{self.name}'>"
