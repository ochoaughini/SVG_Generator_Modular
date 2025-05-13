# src/svg_generator/utils/text_utils.py
"""
Text utilities for SVG generation and manipulation.
"""
import re
import textwrap
import hashlib
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class TextUtils:
    """
    Utilities for text processing and manipulation in SVG contexts.
    
    This class provides methods for handling text in SVGs, including
    wrapping, fitting, and converting text to path data.
    """
    
    @staticmethod
    def wrap_text(text: str, max_width: int, font_size: float = 12.0,
                 font_family: str = 'Arial') -> List[str]:
        """
        Wrap text to fit within a maximum width.
        
        This is a simplified version that doesn't calculate actual text width,
        but approximates based on character count.
        
        Args:
            text: Text to wrap
            max_width: Maximum width in pixels
            font_size: Font size in pixels
            font_family: Font family name
            
        Returns:
            List of wrapped text lines
        """
        # Approximate characters per pixel based on font size
        # This is a rough estimate and should be refined for actual use
        chars_per_pixel = 1.8 / font_size  # Roughly estimated
        
        # Calculate maximum characters per line
        max_chars = int(max_width * chars_per_pixel)
        
        # Use textwrap module to wrap the text
        wrapped_lines = textwrap.wrap(text, width=max_chars)
        
        logger.debug(f"Wrapped text into {len(wrapped_lines)} lines")
        return wrapped_lines
    
    @staticmethod
    def truncate_text(text: str, max_length: int, ellipsis: str = '...') -> str:
        """
        Truncate text to a maximum length with ellipsis.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            ellipsis: Ellipsis string to add at the end
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
            
        # Truncate and add ellipsis
        return text[:max_length - len(ellipsis)] + ellipsis
    
    @staticmethod
    def generate_text_hash(text: str, length: int = 8) -> str:
        """
        Generate a hash from text, useful for IDs.
        
        Args:
            text: Text to hash
            length: Desired length of hash
            
        Returns:
            Hashed string
        """
        hash_obj = hashlib.md5(text.encode('utf-8'))
        return hash_obj.hexdigest()[:length]
    
    @staticmethod
    def sanitize_text_for_svg(text: str) -> str:
        """
        Sanitize text for use in SVG.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        # Replace XML special characters
        sanitized = text.replace('&', '&amp;')
        sanitized = sanitized.replace('<', '&lt;')
        sanitized = sanitized.replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;')
        sanitized = sanitized.replace("'", '&apos;')
        
        return sanitized
    
    @staticmethod
    def estimate_text_dimensions(text: str, font_size: float = 12.0,
                               font_family: str = 'Arial') -> Tuple[float, float]:
        """
        Estimate text dimensions based on character count and font size.
        
        This is a simplified estimate and not an actual measurement.
        
        Args:
            text: Text to measure
            font_size: Font size in pixels
            font_family: Font family name
            
        Returns:
            Tuple of (width, height) in pixels
        """
        # Count lines
        lines = text.split('\n')
        line_count = len(lines)
        
        # Find longest line
        longest_line = max(lines, key=len) if lines else ""
        
        # Estimate width based on character count and font size
        # This is a rough approximation
        char_width_factor = 0.6  # Approximation of average character width relative to font size
        estimated_width = len(longest_line) * font_size * char_width_factor
        
        # Estimate height based on line count and font size
        line_height_factor = 1.2  # Line height relative to font size
        estimated_height = line_count * font_size * line_height_factor
        
        return (estimated_width, estimated_height)
    
    @staticmethod
    def create_text_element(text: str, x: float, y: float, 
                          font_size: float = 12.0, font_family: str = 'Arial',
                          fill: str = '#000000', text_anchor: str = 'start',
                          dominant_baseline: str = 'auto',
                          additional_attributes: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a dictionary representing a text element for SVG.
        
        Args:
            text: Text content
            x: X-coordinate
            y: Y-coordinate
            font_size: Font size in pixels
            font_family: Font family name
            fill: Text color
            text_anchor: Text anchor ('start', 'middle', 'end')
            dominant_baseline: Dominant baseline ('auto', 'middle', 'hanging')
            additional_attributes: Additional attributes to add
            
        Returns:
            Dictionary representing text element
        """
        # Sanitize text for SVG
        sanitized_text = TextUtils.sanitize_text_for_svg(text)
        
        # Create base text element
        text_element = {
            'type': 'text',
            'x': str(x),
            'y': str(y),
            'font-size': str(font_size),
            'font-family': font_family,
            'fill': fill,
            'text-anchor': text_anchor,
            'dominant-baseline': dominant_baseline,
            '_text_content': sanitized_text
        }
        
        # Add additional attributes if provided
        if additional_attributes:
            text_element.update(additional_attributes)
            
        return text_element
    
    @staticmethod
    def split_text_by_tokens(text: str, max_tokens_per_chunk: int = 100) -> List[str]:
        """
        Split text into chunks based on token count.
        
        This is a simple approximation since actual tokenization
        depends on the specific model or algorithm used.
        
        Args:
            text: Text to split
            max_tokens_per_chunk: Maximum tokens per chunk
            
        Returns:
            List of text chunks
        """
        # Simple approximation of tokens as words plus punctuation
        tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
        
        chunks = []
        current_chunk = []
        current_count = 0
        
        for token in tokens:
            current_count += 1
            current_chunk.append(token)
            
            if current_count >= max_tokens_per_chunk:
                # Join the tokens back into text
                chunks.append(' '.join(current_chunk).replace(' ,', ',').replace(' .', '.'))
                current_chunk = []
                current_count = 0
                
        # Add any remaining tokens
        if current_chunk:
            chunks.append(' '.join(current_chunk).replace(' ,', ',').replace(' .', '.'))
            
        return chunks
    
    @staticmethod
    def create_multiline_text(lines: List[str], x: float, y: float,
                            font_size: float = 12.0, line_height: float = 1.2,
                            **text_attrs) -> List[Dict[str, Any]]:
        """
        Create multiple text elements for multiline text.
        
        Args:
            lines: List of text lines
            x: X-coordinate of the first line
            y: Y-coordinate of the first line
            font_size: Font size in pixels
            line_height: Line height as a multiple of font size
            **text_attrs: Additional attributes for text elements
            
        Returns:
            List of text element dictionaries
        """
        text_elements = []
        
        for i, line in enumerate(lines):
            # Calculate Y position for this line
            line_y = y + i * font_size * line_height
            
            # Create text element for this line
            text_element = TextUtils.create_text_element(
                text=line,
                x=x,
                y=line_y,
                font_size=font_size,
                **text_attrs
            )
            
            text_elements.append(text_element)
            
        return text_elements
