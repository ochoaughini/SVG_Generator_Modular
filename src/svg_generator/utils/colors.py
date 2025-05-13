# src/svg_generator/utils/colors.py
"""
Color utilities for SVG generation.
"""
import random
import colorsys
import re
import math
import logging
from typing import Tuple, List, Dict, Union, Optional

logger = logging.getLogger(__name__)

class ColorUtils:
    """
    Color manipulation utilities for SVG generation.
    
    Provides methods for color transformations, palette generation,
    and other color-related operations.
    """
    
    # Web color constants
    WEB_COLORS = {
        "aliceblue": "#f0f8ff", "antiquewhite": "#faebd7", "aqua": "#00ffff",
        "aquamarine": "#7fffd4", "azure": "#f0ffff", "beige": "#f5f5dc",
        "bisque": "#ffe4c4", "black": "#000000", "blanchedalmond": "#ffebcd",
        "blue": "#0000ff", "blueviolet": "#8a2be2", "brown": "#a52a2a",
        "burlywood": "#deb887", "cadetblue": "#5f9ea0", "chartreuse": "#7fff00",
        "chocolate": "#d2691e", "coral": "#ff7f50", "cornflowerblue": "#6495ed",
        "cornsilk": "#fff8dc", "crimson": "#dc143c", "cyan": "#00ffff",
        "darkblue": "#00008b", "darkcyan": "#008b8b", "darkgoldenrod": "#b8860b",
        "darkgray": "#a9a9a9", "darkgreen": "#006400", "darkkhaki": "#bdb76b",
        "darkmagenta": "#8b008b", "darkolivegreen": "#556b2f", "darkorange": "#ff8c00",
        "darkorchid": "#9932cc", "darkred": "#8b0000", "darksalmon": "#e9967a",
        "darkseagreen": "#8fbc8f", "darkslateblue": "#483d8b", "darkslategray": "#2f4f4f",
        "darkturquoise": "#00ced1", "darkviolet": "#9400d3", "deeppink": "#ff1493",
        "deepskyblue": "#00bfff", "dimgray": "#696969", "dodgerblue": "#1e90ff",
        "firebrick": "#b22222", "floralwhite": "#fffaf0", "forestgreen": "#228b22",
        "fuchsia": "#ff00ff", "gainsboro": "#dcdcdc", "ghostwhite": "#f8f8ff",
        "gold": "#ffd700", "goldenrod": "#daa520", "gray": "#808080",
        "green": "#008000", "greenyellow": "#adff2f", "honeydew": "#f0fff0",
        "hotpink": "#ff69b4", "indianred": "#cd5c5c", "indigo": "#4b0082",
        "ivory": "#fffff0", "khaki": "#f0e68c", "lavender": "#e6e6fa",
        "lavenderblush": "#fff0f5", "lawngreen": "#7cfc00", "lemonchiffon": "#fffacd",
        "lightblue": "#add8e6", "lightcoral": "#f08080", "lightcyan": "#e0ffff",
        "lightgoldenrodyellow": "#fafad2", "lightgray": "#d3d3d3", "lightgreen": "#90ee90",
        "lightpink": "#ffb6c1", "lightsalmon": "#ffa07a", "lightseagreen": "#20b2aa",
        "lightskyblue": "#87cefa", "lightslategray": "#778899", "lightsteelblue": "#b0c4de",
        "lightyellow": "#ffffe0", "lime": "#00ff00", "limegreen": "#32cd32",
        "linen": "#faf0e6", "magenta": "#ff00ff", "maroon": "#800000",
        "mediumaquamarine": "#66cdaa", "mediumblue": "#0000cd", "mediumorchid": "#ba55d3",
        "mediumpurple": "#9370db", "mediumseagreen": "#3cb371", "mediumslateblue": "#7b68ee",
        "mediumspringgreen": "#00fa9a", "mediumturquoise": "#48d1cc", "mediumvioletred": "#c71585",
        "midnightblue": "#191970", "mintcream": "#f5fffa", "mistyrose": "#ffe4e1",
        "moccasin": "#ffe4b5", "navajowhite": "#ffdead", "navy": "#000080",
        "oldlace": "#fdf5e6", "olive": "#808000", "olivedrab": "#6b8e23",
        "orange": "#ffa500", "orangered": "#ff4500", "orchid": "#da70d6",
        "palegoldenrod": "#eee8aa", "palegreen": "#98fb98", "paleturquoise": "#afeeee",
        "palevioletred": "#db7093", "papayawhip": "#ffefd5", "peachpuff": "#ffdab9",
        "peru": "#cd853f", "pink": "#ffc0cb", "plum": "#dda0dd",
        "powderblue": "#b0e0e6", "purple": "#800080", "rebeccapurple": "#663399",
        "red": "#ff0000", "rosybrown": "#bc8f8f", "royalblue": "#4169e1",
        "saddlebrown": "#8b4513", "salmon": "#fa8072", "sandybrown": "#f4a460",
        "seagreen": "#2e8b57", "seashell": "#fff5ee", "sienna": "#a0522d",
        "silver": "#c0c0c0", "skyblue": "#87ceeb", "slateblue": "#6a5acd",
        "slategray": "#708090", "snow": "#fffafa", "springgreen": "#00ff7f",
        "steelblue": "#4682b4", "tan": "#d2b48c", "teal": "#008080",
        "thistle": "#d8bfd8", "tomato": "#ff6347", "turquoise": "#40e0d0",
        "violet": "#ee82ee", "wheat": "#f5deb3", "white": "#ffffff",
        "whitesmoke": "#f5f5f5", "yellow": "#ffff00", "yellowgreen": "#9acd32"
    }
    
    @classmethod
    def parse_color(cls, color: str) -> Tuple[int, int, int]:
        """
        Parse color string to RGB tuple.
        
        Args:
            color: Color string (hex, rgb, or name)
            
        Returns:
            RGB tuple (0-255 for each component)
        """
        color = color.lower().strip()
        
        # Check if it's a named color
        if color in cls.WEB_COLORS:
            color = cls.WEB_COLORS[color]
        
        # Check if it's a hex color
        if color.startswith('#'):
            color = color.lstrip('#')
            
            # Convert shorthand (3 chars) to full form (6 chars)
            if len(color) == 3:
                color = ''.join([c + c for c in color])
                
            return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
        # Check if it's an RGB color
        rgb_match = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color)
        if rgb_match:
            return tuple(map(int, rgb_match.groups()))
            
        # If we get here, we couldn't parse the color
        logger.warning(f"Couldn't parse color: {color}. Defaulting to black.")
        return (0, 0, 0)
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """
        Convert RGB tuple to hex color string.
        
        Args:
            rgb: RGB tuple (0-255 for each component)
            
        Returns:
            Hex color string (#RRGGBB)
        """
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple.
        
        Args:
            hex_color: Hex color string (#RRGGBB or #RGB)
            
        Returns:
            RGB tuple (0-255 for each component)
        """
        hex_color = hex_color.lstrip('#')
        
        # Convert shorthand (3 chars) to full form (6 chars)
        if len(hex_color) == 3:
            hex_color = ''.join([c + c for c in hex_color])
            
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hsl(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """
        Convert RGB to HSL.
        
        Args:
            rgb: RGB tuple (0-255 for each component)
            
        Returns:
            HSL tuple (H: 0-360, S: 0-100, L: 0-100)
        """
        r, g, b = [x / 255.0 for x in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s * 100, l * 100)
    
    @staticmethod
    def hsl_to_rgb(hsl: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """
        Convert HSL to RGB.
        
        Args:
            hsl: HSL tuple (H: 0-360, S: 0-100, L: 0-100)
            
        Returns:
            RGB tuple (0-255 for each component)
        """
        h, s, l = hsl
        h /= 360
        s /= 100
        l /= 100
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    @classmethod
    def darken(cls, color: str, amount: float = 0.2) -> str:
        """
        Darken a color by the specified amount.
        
        Args:
            color: Color to darken (hex, rgb, or name)
            amount: Amount to darken (0-1)
            
        Returns:
            Darkened color (hex)
        """
        rgb = cls.parse_color(color)
        hsl = cls.rgb_to_hsl(rgb)
        
        # Reduce lightness
        hsl = (hsl[0], hsl[1], max(0, hsl[2] - amount * 100))
        
        rgb = cls.hsl_to_rgb(hsl)
        return cls.rgb_to_hex(rgb)
    
    @classmethod
    def lighten(cls, color: str, amount: float = 0.2) -> str:
        """
        Lighten a color by the specified amount.
        
        Args:
            color: Color to lighten (hex, rgb, or name)
            amount: Amount to lighten (0-1)
            
        Returns:
            Lightened color (hex)
        """
        rgb = cls.parse_color(color)
        hsl = cls.rgb_to_hsl(rgb)
        
        # Increase lightness
        hsl = (hsl[0], hsl[1], min(100, hsl[2] + amount * 100))
        
        rgb = cls.hsl_to_rgb(hsl)
        return cls.rgb_to_hex(rgb)
    
    @classmethod
    def adjust_opacity(cls, color: str, opacity: float) -> str:
        """
        Adjust the opacity of a color (for CSS/SVG usage).
        
        Args:
            color: Color to adjust (hex, rgb, or name)
            opacity: Target opacity (0-1)
            
        Returns:
            RGBA color string (rgba(r, g, b, a))
        """
        rgb = cls.parse_color(color)
        return f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})'
    
    @classmethod
    def generate_palette(cls, base_color: str, count: int = 5, 
                         scheme: str = 'analogous') -> List[str]:
        """
        Generate a color palette based on a base color.
        
        Args:
            base_color: Base color for palette
            count: Number of colors to generate
            scheme: Palette scheme ('analogous', 'complementary', 'triadic', 'monochromatic')
            
        Returns:
            List of hex color strings
        """
        rgb = cls.parse_color(base_color)
        hsl = cls.rgb_to_hsl(rgb)
        h, s, l = hsl
        
        palette = []
        
        if scheme == 'analogous':
            # Analogous colors are next to each other on the color wheel
            for i in range(count):
                angle = 360 / count
                new_h = (h + i * angle) % 360
                new_rgb = cls.hsl_to_rgb((new_h, s, l))
                palette.append(cls.rgb_to_hex(new_rgb))
                
        elif scheme == 'complementary':
            # Complementary colors are opposite on the color wheel
            palette.append(cls.rgb_to_hex(rgb))
            
            for i in range(1, count):
                # Generate shades between base and complement
                ratio = i / (count - 1)
                new_h = (h + ratio * 180) % 360
                new_rgb = cls.hsl_to_rgb((new_h, s, l))
                palette.append(cls.rgb_to_hex(new_rgb))
                
        elif scheme == 'triadic':
            # Triadic colors are evenly spaced on the color wheel
            for i in range(count):
                new_h = (h + i * 120) % 360
                new_rgb = cls.hsl_to_rgb((new_h, s, l))
                palette.append(cls.rgb_to_hex(new_rgb))
                
        elif scheme == 'monochromatic':
            # Monochromatic colors vary in lightness or saturation
            for i in range(count):
                # Vary lightness
                new_l = max(0, min(100, l - 40 + (i * 80 / (count - 1 or 1))))
                new_rgb = cls.hsl_to_rgb((h, s, new_l))
                palette.append(cls.rgb_to_hex(new_rgb))
                
        else:
            # Default to a simple color list if scheme not recognized
            palette.append(cls.rgb_to_hex(rgb))
            for i in range(1, count):
                new_h = (h + i * 360 / count) % 360
                new_rgb = cls.hsl_to_rgb((new_h, s, l))
                palette.append(cls.rgb_to_hex(new_rgb))
        
        return palette[:count]  # Ensure we return exactly 'count' colors
    
    @classmethod
    def random_color(cls, mode: str = 'bright') -> str:
        """
        Generate a random color.
        
        Args:
            mode: Color mode ('bright', 'pastel', 'dark', 'light', 'any')
            
        Returns:
            Hex color string
        """
        if mode == 'bright':
            # Bright colors have high saturation and medium to high lightness
            h = random.random() * 360
            s = random.uniform(70, 100)
            l = random.uniform(45, 65)
            rgb = cls.hsl_to_rgb((h, s, l))
            
        elif mode == 'pastel':
            # Pastel colors have lower saturation and high lightness
            h = random.random() * 360
            s = random.uniform(20, 55)
            l = random.uniform(70, 90)
            rgb = cls.hsl_to_rgb((h, s, l))
            
        elif mode == 'dark':
            # Dark colors have medium to high saturation and low lightness
            h = random.random() * 360
            s = random.uniform(50, 100)
            l = random.uniform(5, 35)
            rgb = cls.hsl_to_rgb((h, s, l))
            
        elif mode == 'light':
            # Light colors have low to medium saturation and high lightness
            h = random.random() * 360
            s = random.uniform(15, 40)
            l = random.uniform(75, 95)
            rgb = cls.hsl_to_rgb((h, s, l))
            
        else:  # 'any' or unrecognized mode
            # Any mode gives a completely random color
            rgb = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            
        return cls.rgb_to_hex(rgb)
    
    @classmethod
    def blend_colors(cls, color1: str, color2: str, ratio: float = 0.5) -> str:
        """
        Blend two colors together.
        
        Args:
            color1: First color
            color2: Second color
            ratio: Blend ratio (0-1, where 0 is all color1, 1 is all color2)
            
        Returns:
            Blended color (hex)
        """
        rgb1 = cls.parse_color(color1)
        rgb2 = cls.parse_color(color2)
        
        blended = tuple(
            int(c1 * (1 - ratio) + c2 * ratio)
            for c1, c2 in zip(rgb1, rgb2)
        )
        
        return cls.rgb_to_hex(blended)
    
    @classmethod
    def is_dark(cls, color: str, threshold: float = 0.5) -> bool:
        """
        Determine if a color is 'dark' (for contrast purposes).
        
        Args:
            color: Color to check
            threshold: Lightness threshold (0-1)
            
        Returns:
            True if the color is dark, False otherwise
        """
        rgb = cls.parse_color(color)
        
        # Calculate perceived brightness
        # Using the formula: (0.299*R + 0.587*G + 0.114*B) / 255
        brightness = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        
        return brightness < threshold
    
    @classmethod
    def get_contrast_color(cls, color: str) -> str:
        """
        Get a contrasting color (black or white) for text on given background.
        
        Args:
            color: Background color
            
        Returns:
            '#ffffff' for dark backgrounds, '#000000' for light backgrounds
        """
        return '#ffffff' if cls.is_dark(color) else '#000000'
