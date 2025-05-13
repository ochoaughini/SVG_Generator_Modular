# src/svg_generator/svg/patterns.py
"""
Pattern generation for SVG compositions and backgrounds.
"""
from typing import List, Dict, Any, Tuple
import math
import logging

from svg_generator.svg.shapes import ShapeFactory

logger = logging.getLogger(__name__)

class PatternFactory:
    """
    Factory for creating SVG pattern definitions.
    
    This class provides methods to create pattern dictionaries that can be 
    included in the scene description's 'definitions' section.
    """
    
    @staticmethod
    def create_pattern(id: str, width: float, height: float, 
                     pattern_units: str = "userSpaceOnUse",
                     x: float = 0, y: float = 0,
                     children: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a basic pattern definition.
        
        Args:
            id: Unique identifier for the pattern
            width: Width of the pattern tile
            height: Height of the pattern tile
            pattern_units: Coordinate system for the pattern ('userSpaceOnUse' or 'objectBoundingBox')
            x: x-coordinate of the pattern tile
            y: y-coordinate of the pattern tile
            children: List of shape dictionaries to include in the pattern
            
        Returns:
            Dictionary representing the pattern definition
        """
        pattern_def = {
            "type": "pattern",
            "id": id,
            "attributes": {
                "width": str(width),
                "height": str(height),
                "patternUnits": pattern_units,
                "x": str(x),
                "y": str(y)
            },
            "children": children or []
        }
        
        return pattern_def
        
    @staticmethod
    def create_grid_pattern(id: str, grid_size: float, line_width: float = 1,
                          line_color: str = "#000000", background_color: str = "none") -> Dict[str, Any]:
        """
        Create a grid pattern definition.
        
        Args:
            id: Unique identifier for the pattern
            grid_size: Size of each grid cell
            line_width: Width of the grid lines
            line_color: Color of the grid lines
            background_color: Background color of the pattern
            
        Returns:
            Dictionary representing the grid pattern definition
        """
        # Create the background rectangle if needed
        children = []
        if background_color.lower() != "none" and background_color.lower() != "transparent":
            children.append(ShapeFactory.create_rectangle(
                0, 0, grid_size, grid_size, 
                fill=background_color
            ))
        
        # Create the grid lines
        # Horizontal line
        children.append(ShapeFactory.create_line(
            0, 0, grid_size, 0,
            stroke=line_color, 
            stroke_width=line_width
        ))
        
        # Vertical line
        children.append(ShapeFactory.create_line(
            0, 0, 0, grid_size,
            stroke=line_color, 
            stroke_width=line_width
        ))
        
        return PatternFactory.create_pattern(id, grid_size, grid_size, children=children)
        
    @staticmethod
    def create_dots_pattern(id: str, spacing: float, dot_radius: float = 2,
                          dot_color: str = "#000000", background_color: str = "none") -> Dict[str, Any]:
        """
        Create a pattern of dots.
        
        Args:
            id: Unique identifier for the pattern
            spacing: Distance between dots
            dot_radius: Radius of each dot
            dot_color: Color of the dots
            background_color: Background color of the pattern
            
        Returns:
            Dictionary representing the dots pattern definition
        """
        children = []
        
        # Create the background rectangle if needed
        if background_color.lower() != "none" and background_color.lower() != "transparent":
            children.append(ShapeFactory.create_rectangle(
                0, 0, spacing, spacing, 
                fill=background_color
            ))
        
        # Create the dot in the center
        children.append(ShapeFactory.create_circle(
            spacing/2, spacing/2, dot_radius,
            fill=dot_color
        ))
        
        return PatternFactory.create_pattern(id, spacing, spacing, children=children)
        
    @staticmethod
    def create_stripes_pattern(id: str, stripe_width: float, angle: float = 45,
                             colors: List[str] = None, background_color: str = "none") -> Dict[str, Any]:
        """
        Create a striped pattern definition.
        
        Args:
            id: Unique identifier for the pattern
            stripe_width: Width of each stripe
            angle: Angle of the stripes in degrees
            colors: List of colors for the stripes, alternating
            background_color: Background color of the pattern
            
        Returns:
            Dictionary representing the striped pattern definition
        """
        if colors is None or len(colors) < 1:
            colors = ["#000000", "#FFFFFF"]
        elif len(colors) == 1:
            colors = [colors[0], "none"]
            
        # Calculate pattern size based on angle to ensure repeating correctly
        # This is a simplified approach that works well for common angles
        angle_rad = math.radians(angle)
        pattern_size = stripe_width * len(colors) * max(abs(math.cos(angle_rad)), abs(math.sin(angle_rad))) * 2
        
        children = []
        
        # Create background if needed
        if background_color.lower() != "none" and background_color.lower() != "transparent":
            children.append(ShapeFactory.create_rectangle(
                0, 0, pattern_size, pattern_size, 
                fill=background_color
            ))
        
        # Create stripes
        # We'll create multiple stripes to cover the pattern area
        total_stripe_width = stripe_width * len(colors)
        for i in range(int(pattern_size / total_stripe_width) * 2 + 2):
            stripe_pos = i * total_stripe_width
            
            for j, color in enumerate(colors):
                # Skip transparent stripes
                if color.lower() == "none" or color.lower() == "transparent":
                    continue
                    
                offset = j * stripe_width
                
                # Create a rotated rectangle for each stripe
                # For simplicity, we'll use a path with larger dimensions to ensure coverage
                size_multiplier = 3  # Make the stripe much larger than pattern to ensure full coverage
                center_x = pattern_size / 2
                center_y = pattern_size / 2
                
                # Convert to path with rotation
                rect_width = pattern_size * size_multiplier
                rect_height = stripe_width
                
                # Calculate corner points of the rectangle
                left = -rect_width / 2
                right = rect_width / 2
                top = -rect_height / 2 + stripe_pos + offset - pattern_size / 2
                bottom = rect_height / 2 + stripe_pos + offset - pattern_size / 2
                
                # Create corners
                corners = [
                    (left, top),
                    (right, top),
                    (right, bottom),
                    (left, bottom)
                ]
                
                # Rotate corners
                rotated_corners = []
                for x, y in corners:
                    rotated_x = x * math.cos(angle_rad) - y * math.sin(angle_rad) + center_x
                    rotated_y = x * math.sin(angle_rad) + y * math.cos(angle_rad) + center_y
                    rotated_corners.append((rotated_x, rotated_y))
                
                # Create path
                children.append(ShapeFactory.create_polygon(rotated_corners, fill=color))
        
        return PatternFactory.create_pattern(id, pattern_size, pattern_size, children=children)
        
    @staticmethod
    def create_checkered_pattern(id: str, cell_size: float,
                               colors: List[str] = None) -> Dict[str, Any]:
        """
        Create a checkered pattern definition.
        
        Args:
            id: Unique identifier for the pattern
            cell_size: Size of each checkerboard cell
            colors: List of two colors for the checkerboard
            
        Returns:
            Dictionary representing the checkered pattern definition
        """
        if colors is None or len(colors) < 2:
            colors = ["#FFFFFF", "#000000"]
        elif len(colors) > 2:
            colors = colors[:2]
            
        children = []
        
        # Create the first square (top-left)
        children.append(ShapeFactory.create_rectangle(
            0, 0, cell_size, cell_size, 
            fill=colors[0]
        ))
        
        # Create the second square (top-right)
        children.append(ShapeFactory.create_rectangle(
            cell_size, 0, cell_size, cell_size, 
            fill=colors[1]
        ))
        
        # Create the third square (bottom-left)
        children.append(ShapeFactory.create_rectangle(
            0, cell_size, cell_size, cell_size, 
            fill=colors[1]
        ))
        
        # Create the fourth square (bottom-right)
        children.append(ShapeFactory.create_rectangle(
            cell_size, cell_size, cell_size, cell_size, 
            fill=colors[0]
        ))
        
        return PatternFactory.create_pattern(id, cell_size * 2, cell_size * 2, children=children)
    
    @staticmethod
    def create_pattern_reference(pattern_id: str) -> str:
        """
        Creates a reference string for using a pattern in a fill or stroke attribute.
        
        Args:
            pattern_id: ID of the pattern to reference
            
        Returns:
            Reference string to use in fill or stroke attributes
        """
        return f"url(#{pattern_id})"
