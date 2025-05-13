# src/svg_generator/svg/renderers/text_renderer.py
"""
Text renderer for SVG generation with advanced text layout features.
"""
from typing import List, Dict, Any, Tuple, Optional, Union
import math
import logging
import re

from svg_generator.utils.text_utils import TextUtils
from svg_generator.svg.shapes import ShapeFactory

logger = logging.getLogger(__name__)

class TextRenderer:
    """
    Renders text with advanced formatting and layout options.
    
    Provides methods for creating SVG text elements with various
    styles, alignments, and special effects.
    """
    
    def __init__(self, width: float = 800, height: float = 600):
        """
        Initialize the text renderer.
        
        Args:
            width: Width of the SVG canvas
            height: Height of the SVG canvas
        """
        self.width = width
        self.height = height
        logger.debug(f"TextRenderer initialized: {width}x{height}")
        
    def render_text(self, text: str, x: float, y: float, 
                   font_size: float = 16.0, font_family: str = 'Arial',
                   fill: str = '#000000', 
                   text_anchor: str = 'start',  # 'start', 'middle', 'end'
                   dominant_baseline: str = 'auto',  # 'auto', 'middle', 'hanging'
                   additional_attrs: Optional[Dict[str, str]] = None,
                   as_path: bool = False) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Render text as an SVG element.
        
        Args:
            text: Text content
            x: X-coordinate
            y: Y-coordinate
            font_size: Font size in pixels
            font_family: Font family name
            fill: Text color
            text_anchor: Text anchor ('start', 'middle', 'end')
            dominant_baseline: Dominant baseline ('auto', 'middle', 'hanging')
            additional_attrs: Additional attributes to add to the text element
            as_path: Whether to convert text to path (useful for competition compliance)
            
        Returns:
            Dictionary representing text element or list of path elements if as_path=True
        """
        if as_path:
            # For competition SVGs, text often needs to be converted to paths
            # This is a simplified version as true text-to-path conversion requires
            # actual font metrics and glyph outlines
            return self._render_text_as_path(text, x, y, font_size, font_family, 
                                            fill, text_anchor, additional_attrs)
        
        # Standard text element
        attrs = {
            'font-size': str(font_size),
            'font-family': font_family,
            'fill': fill,
            'text-anchor': text_anchor,
            'dominant-baseline': dominant_baseline
        }
        
        # Add additional attributes
        if additional_attrs:
            attrs.update(additional_attrs)
            
        return TextUtils.create_text_element(text, x, y, **attrs)
    
    def _render_text_as_path(self, text: str, x: float, y: float,
                           font_size: float, font_family: str,
                           fill: str, text_anchor: str,
                           additional_attrs: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Convert text to path elements (simplified approximation).
        
        Note: This is a simplified approximation. Real text-to-path conversion
        requires actual font metrics and glyph outlines.
        
        Args:
            text: Text content
            x: X-coordinate
            y: Y-coordinate
            font_size: Font size in pixels
            font_family: Font family name
            fill: Path fill color
            text_anchor: Text anchor ('start', 'middle', 'end')
            additional_attrs: Additional attributes for path elements
            
        Returns:
            List of path elements approximating the text
        """
        logger.info(f"Converting text to path: '{text}'")
        
        # This is a simplified approximation of text-to-path
        # Real implementations would use font metrics and glyph outlines
        
        # Estimate text dimensions
        text_width, _ = TextUtils.estimate_text_dimensions(text, font_size, font_family)
        
        # Adjust x position based on text anchor
        if text_anchor == 'middle':
            x -= text_width / 2
        elif text_anchor == 'end':
            x -= text_width
            
        # Create a group for the text paths
        paths = []
        
        # Character metrics (very simplified)
        char_width = font_size * 0.6  # Approximation
        
        # Create simplified path for each character
        for i, char in enumerate(text):
            char_x = x + i * char_width
            
            # Skip spaces
            if char == ' ':
                continue
                
            # Create a simplified character path
            # This is a very basic approximation
            # Real implementations would use actual font outlines
            if char.lower() in 'abcdefghijklmnopqrstuvwxyz0123456789':
                # Create a small rectangle for each character
                rect_width = char_width * 0.8
                rect_height = font_size * 0.8
                
                # Position the rectangle
                rect_x = char_x
                rect_y = y - rect_height * 0.7  # Align with baseline
                
                # Add some variation based on character
                if char.lower() in 'bdfhijklt':
                    # Tall characters
                    rect_height *= 1.2
                    rect_y -= rect_height * 0.1
                elif char.lower() in 'gpqy':
                    # Characters with descenders
                    rect_height *= 1.2
                    rect_y += rect_height * 0.1
                
                # Create path for character
                # In a real implementation, this would use actual glyph outlines
                if char.lower() in 'oq0':
                    # Round characters (approximate as circle)
                    circle_radius = min(rect_width, rect_height) / 2
                    
                    path = ShapeFactory.create_circle(
                        rect_x + rect_width / 2,
                        rect_y + rect_height / 2,
                        circle_radius,
                        fill=fill,
                        id=f"text_path_{i}"
                    )
                    
                    paths.append(path)
                else:
                    # Other characters (approximate as rectangle)
                    path = ShapeFactory.create_rect(
                        rect_x,
                        rect_y,
                        rect_width,
                        rect_height,
                        rx=rect_width * 0.2,  # Rounded corners
                        ry=rect_height * 0.2,
                        fill=fill,
                        id=f"text_path_{i}"
                    )
                    
                    paths.append(path)
                    
                    # For characters with horizontal strokes, add a line
                    if char.lower() in 'aefhtz':
                        line_y = rect_y + rect_height * 0.4
                        
                        line = ShapeFactory.create_line(
                            rect_x,
                            line_y,
                            rect_x + rect_width,
                            line_y,
                            stroke=fill,
                            stroke_width=font_size * 0.1,
                            id=f"text_path_{i}_stroke"
                        )
                        
                        paths.append(line)
        
        # Add additional attributes to each path if provided
        if additional_attrs:
            for path in paths:
                path.update(additional_attrs)
                
        return paths
    
    def render_text_block(self, text: str, x: float, y: float, width: float,
                        font_size: float = 16.0, line_height: float = 1.2,
                        text_align: str = 'left',  # 'left', 'center', 'right'
                        **text_attrs) -> List[Dict[str, Any]]:
        """
        Render a block of text with automatic wrapping.
        
        Args:
            text: Text content
            x: X-coordinate of the block
            y: Y-coordinate of the block
            width: Width of the block
            font_size: Font size in pixels
            line_height: Line height as a multiple of font size
            text_align: Text alignment ('left', 'center', 'right')
            **text_attrs: Additional attributes for text elements
            
        Returns:
            List of text elements
        """
        # Determine text anchor based on alignment
        text_anchor = 'start'  # Default for left alignment
        
        if text_align == 'center':
            text_anchor = 'middle'
            x += width / 2  # Adjust x for center alignment
        elif text_align == 'right':
            text_anchor = 'end'
            x += width  # Adjust x for right alignment
            
        # Wrap text to fit within width
        font_family = text_attrs.get('font_family', 'Arial')
        wrapped_lines = TextUtils.wrap_text(text, width, font_size, font_family)
        
        # Create text elements for each line
        text_attrs['text_anchor'] = text_anchor
        
        return TextUtils.create_multiline_text(
            wrapped_lines, x, y, font_size, line_height, **text_attrs
        )
    
    def render_curved_text(self, text: str, center_x: float, center_y: float, 
                         radius: float, start_angle: float = 0, 
                         clockwise: bool = True, **text_attrs) -> List[Dict[str, Any]]:
        """
        Render text along a circular path.
        
        Args:
            text: Text content
            center_x: X-coordinate of the circle center
            center_y: Y-coordinate of the circle center
            radius: Radius of the circle
            start_angle: Starting angle in degrees
            clockwise: Whether to curve text clockwise
            **text_attrs: Additional attributes for text elements
            
        Returns:
            List of text elements positioned along a circular path
        """
        # Get font size from attributes or use default
        font_size = float(text_attrs.get('font_size', 16.0))
        
        # Approximate character spacing
        char_angle = (font_size / (radius * math.pi * 2)) * 360
        
        # Sanitize text
        text = TextUtils.sanitize_text_for_svg(text)
        
        # Create elements for each character
        elements = []
        
        for i, char in enumerate(text):
            # Skip spaces in curved text
            if char == ' ':
                continue
                
            # Calculate angle for this character
            angle_dir = -1 if clockwise else 1
            angle = start_angle + (i * char_angle * angle_dir)
            
            # Calculate position
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))
            
            # Create text element
            char_element = TextUtils.create_text_element(
                text=char,
                x=x,
                y=y,
                **text_attrs
            )
            
            # Add rotation for proper orientation along the curve
            rotation = angle + (90 if clockwise else -90)
            char_element['transform'] = f"rotate({rotation}, {x}, {y})"
            
            elements.append(char_element)
            
        return elements
    
    def render_outlined_text(self, text: str, x: float, y: float, 
                           font_size: float = 16.0, 
                           stroke: str = '#000000', stroke_width: float = 1.0,
                           fill: str = '#ffffff', **text_attrs) -> List[Dict[str, Any]]:
        """
        Render text with an outline effect.
        
        Args:
            text: Text content
            x: X-coordinate
            y: Y-coordinate
            font_size: Font size in pixels
            stroke: Outline color
            stroke_width: Outline width
            fill: Text fill color
            **text_attrs: Additional attributes for text elements
            
        Returns:
            List containing background and foreground text elements
        """
        # Create base text attributes
        base_attrs = {
            'font-size': font_size,
            'text-anchor': text_attrs.get('text_anchor', 'start'),
            'dominant-baseline': text_attrs.get('dominant_baseline', 'auto'),
            'font-family': text_attrs.get('font_family', 'Arial')
        }
        
        # Add any other attributes
        for key, value in text_attrs.items():
            if key not in ['font_size', 'text_anchor', 'dominant_baseline', 'font_family']:
                base_attrs[key] = value
                
        # Create background (outline) element
        outline_attrs = base_attrs.copy()
        outline_attrs.update({
            'stroke': stroke,
            'stroke-width': stroke_width,
            'fill': 'none'
        })
        
        outline_element = TextUtils.create_text_element(
            text=text,
            x=x,
            y=y,
            **outline_attrs
        )
        
        # Create foreground (fill) element
        fill_attrs = base_attrs.copy()
        fill_attrs.update({
            'fill': fill,
            'stroke': 'none'
        })
        
        fill_element = TextUtils.create_text_element(
            text=text,
            x=x,
            y=y,
            **fill_attrs
        )
        
        return [outline_element, fill_element]
    
    def render_shadow_text(self, text: str, x: float, y: float, 
                         font_size: float = 16.0, 
                         shadow_color: str = 'rgba(0,0,0,0.5)', 
                         offset_x: float = 2.0, offset_y: float = 2.0,
                         fill: str = '#ffffff', **text_attrs) -> List[Dict[str, Any]]:
        """
        Render text with a shadow effect.
        
        Args:
            text: Text content
            x: X-coordinate
            y: Y-coordinate
            font_size: Font size in pixels
            shadow_color: Shadow color
            offset_x: Shadow x-offset
            offset_y: Shadow y-offset
            fill: Text fill color
            **text_attrs: Additional attributes for text elements
            
        Returns:
            List containing shadow and foreground text elements
        """
        # Create base text attributes
        base_attrs = {
            'font-size': font_size,
            'text-anchor': text_attrs.get('text_anchor', 'start'),
            'dominant-baseline': text_attrs.get('dominant_baseline', 'auto'),
            'font-family': text_attrs.get('font_family', 'Arial')
        }
        
        # Add any other attributes
        for key, value in text_attrs.items():
            if key not in ['font_size', 'text_anchor', 'dominant_baseline', 'font_family']:
                base_attrs[key] = value
                
        # Create shadow element
        shadow_attrs = base_attrs.copy()
        shadow_attrs.update({
            'fill': shadow_color,
            'filter': 'url(#shadow-filter)'  # This requires a filter definition
        })
        
        shadow_element = TextUtils.create_text_element(
            text=text,
            x=x + offset_x,
            y=y + offset_y,
            **shadow_attrs
        )
        
        # Create main text element
        text_attrs = base_attrs.copy()
        text_attrs.update({
            'fill': fill
        })
        
        text_element = TextUtils.create_text_element(
            text=text,
            x=x,
            y=y,
            **text_attrs
        )
        
        return [shadow_element, text_element]
        
    def get_text_path_effects(self, path_data: str, text: str, 
                            font_size: float = 12.0, 
                            font_family: str = 'Arial',
                            fill: str = '#000000', 
                            **text_attrs) -> Dict[str, Any]:
        """
        Create text that follows a path.
        
        Note: This creates SVG elements that may use textPath,
        which could be prohibited in some competitions.
        
        Args:
            path_data: SVG path data string
            text: Text content
            font_size: Font size in pixels
            font_family: Font family name
            fill: Text color
            **text_attrs: Additional attributes
            
        Returns:
            Dictionary containing path and text elements
        """
        # This implementation is intended to show the structure
        # for rendering text along a path, but may need adaptation
        # for competition requirements
        
        # Create a unique ID for the path
        path_id = f"text_path_{TextUtils.generate_text_hash(text)}"
        
        # Create the path element (invisible by default)
        path_element = {
            'type': 'path',
            'id': path_id,
            'd': path_data,
            'fill': 'none',
            'stroke': 'none'
        }
        
        # Create text and textPath elements
        # Note: textPath might be prohibited in some competitions
        text_element = {
            'type': 'text',
            'font-size': str(font_size),
            'font-family': font_family,
            'fill': fill
        }
        
        # Add any other text attributes
        for key, value in text_attrs.items():
            text_element[key] = value
            
        # For actually creating the textPath element, this would depend
        # on the SVG generator's implementation details
        
        # Return both elements
        return {
            'path': path_element,
            'text': text_element,
            'text_content': TextUtils.sanitize_text_for_svg(text),
            'path_id': path_id
        }
