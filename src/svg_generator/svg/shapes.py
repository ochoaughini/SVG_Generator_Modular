# src/svg_generator/svg/shapes.py
"""
Element factory for building SVG shapes with customization options.
This module adapts and extends the original ElementFactory functionality.
"""
from typing import Dict, Any, List, Tuple, Optional
import xml.etree.ElementTree as ET
import math
import logging

logger = logging.getLogger(__name__)

class ShapeFactory:
    """
    Factory for creating SVG shape elements with optimized attributes.
    
    This class provides standardized methods to create different SVG shapes
    and is adapted from the original ElementFactory in Project A.
    """
    
    @staticmethod
    def create_element_dict(element_type: str, **attributes) -> Dict[str, Any]:
        """
        Create a dictionary representation of an SVG element.
        
        Args:
            element_type: The type of SVG element (e.g., 'circle', 'rect')
            **attributes: Key-value pairs of attributes for the element
            
        Returns:
            Dictionary representation of the SVG element
        """
        element_dict = {"type": element_type}
        element_dict.update(attributes)
        return element_dict
        
    @staticmethod
    def create_circle(cx: float, cy: float, radius: float, **attributes) -> Dict[str, Any]:
        """
        Create a circle SVG element dictionary.
        
        Args:
            cx: x-coordinate of the center
            cy: y-coordinate of the center
            radius: Radius of the circle
            **attributes: Additional attributes for the circle
            
        Returns:
            Dictionary representation of the circle element
        """
        attributes.update({"cx": cx, "cy": cy, "r": radius})
        return ShapeFactory.create_element_dict("circle", **attributes)
        
    @staticmethod
    def create_rectangle(x: float, y: float, width: float, height: float, **attributes) -> Dict[str, Any]:
        """
        Create a rectangle SVG element dictionary.
        
        Args:
            x: x-coordinate of the top-left corner
            y: y-coordinate of the top-left corner
            width: Width of the rectangle
            height: Height of the rectangle
            **attributes: Additional attributes for the rectangle
            
        Returns:
            Dictionary representation of the rectangle element
        """
        attributes.update({"x": x, "y": y, "width": width, "height": height})
        return ShapeFactory.create_element_dict("rect", **attributes)
        
    @staticmethod
    def create_rounded_rectangle(x: float, y: float, width: float, height: float, 
                                rx: float, ry: Optional[float] = None, **attributes) -> Dict[str, Any]:
        """
        Create a rounded rectangle SVG element dictionary.
        
        Args:
            x: x-coordinate of the top-left corner
            y: y-coordinate of the top-left corner
            width: Width of the rectangle
            height: Height of the rectangle
            rx: x-radius of the corner rounding
            ry: y-radius of the corner rounding, defaults to rx if None
            **attributes: Additional attributes for the rectangle
            
        Returns:
            Dictionary representation of the rounded rectangle element
        """
        if ry is None:
            ry = rx
        attributes.update({"x": x, "y": y, "width": width, "height": height, "rx": rx, "ry": ry})
        return ShapeFactory.create_element_dict("rect", **attributes)
        
    @staticmethod
    def create_line(x1: float, y1: float, x2: float, y2: float, **attributes) -> Dict[str, Any]:
        """
        Create a line SVG element dictionary.
        
        Args:
            x1: x-coordinate of the start point
            y1: y-coordinate of the start point
            x2: x-coordinate of the end point
            y2: y-coordinate of the end point
            **attributes: Additional attributes for the line
            
        Returns:
            Dictionary representation of the line element
        """
        attributes.update({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
        return ShapeFactory.create_element_dict("line", **attributes)
        
    @staticmethod
    def create_polyline(points: List[Tuple[float, float]], **attributes) -> Dict[str, Any]:
        """
        Create a polyline SVG element dictionary.
        
        Args:
            points: List of (x, y) coordinate tuples
            **attributes: Additional attributes for the polyline
            
        Returns:
            Dictionary representation of the polyline element
        """
        attributes.update({"points": points})
        return ShapeFactory.create_element_dict("polyline", **attributes)
        
    @staticmethod
    def create_polygon(points: List[Tuple[float, float]], **attributes) -> Dict[str, Any]:
        """
        Create a polygon SVG element dictionary.
        
        Args:
            points: List of (x, y) coordinate tuples
            **attributes: Additional attributes for the polygon
            
        Returns:
            Dictionary representation of the polygon element
        """
        attributes.update({"points": points})
        return ShapeFactory.create_element_dict("polygon", **attributes)
        
    @staticmethod
    def create_path(d: str, **attributes) -> Dict[str, Any]:
        """
        Create a path SVG element dictionary.
        
        Args:
            d: Path data string
            **attributes: Additional attributes for the path
            
        Returns:
            Dictionary representation of the path element
        """
        attributes.update({"d": d})
        return ShapeFactory.create_element_dict("path", **attributes)
        
    @staticmethod
    def create_regular_polygon(cx: float, cy: float, radius: float, sides: int, 
                              rotation: float = 0, **attributes) -> Dict[str, Any]:
        """
        Create a regular polygon with specified number of sides.
        
        Args:
            cx: x-coordinate of the center
            cy: y-coordinate of the center
            radius: Distance from center to vertices
            sides: Number of sides
            rotation: Rotation angle in degrees
            **attributes: Additional attributes for the polygon
            
        Returns:
            Dictionary representation of the polygon element
        """
        if sides < 3:
            logger.warning(f"Regular polygon must have at least 3 sides, got {sides}. Using 3 instead.")
            sides = 3
            
        # Convert rotation to radians
        rotation_rad = math.radians(rotation)
        
        # Generate points
        points = []
        for i in range(sides):
            angle = rotation_rad + (2 * math.pi * i / sides)
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append((x, y))
            
        return ShapeFactory.create_polygon(points, **attributes)
        
    @staticmethod
    def create_star(cx: float, cy: float, outer_radius: float, inner_radius: float, 
                   points: int, rotation: float = 0, **attributes) -> Dict[str, Any]:
        """
        Create a star shape.
        
        Args:
            cx: x-coordinate of the center
            cy: y-coordinate of the center
            outer_radius: Distance from center to outer points
            inner_radius: Distance from center to inner points
            points: Number of points on the star
            rotation: Rotation angle in degrees
            **attributes: Additional attributes for the star
            
        Returns:
            Dictionary representation of the polygon element for the star
        """
        if points < 3:
            logger.warning(f"Star must have at least 3 points, got {points}. Using 3 instead.")
            points = 3
            
        # Convert rotation to radians
        rotation_rad = math.radians(rotation)
        
        # Generate star points
        star_points = []
        for i in range(points * 2):
            angle = rotation_rad + (2 * math.pi * i / (points * 2))
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            star_points.append((x, y))
            
        return ShapeFactory.create_polygon(star_points, **attributes)
        
    @staticmethod
    def create_ellipse(cx: float, cy: float, rx: float, ry: float, **attributes) -> Dict[str, Any]:
        """
        Create an ellipse SVG element dictionary.
        
        Args:
            cx: x-coordinate of the center
            cy: y-coordinate of the center
            rx: x-radius of the ellipse
            ry: y-radius of the ellipse
            **attributes: Additional attributes for the ellipse
            
        Returns:
            Dictionary representation of the ellipse element
        """
        attributes.update({"cx": cx, "cy": cy, "rx": rx, "ry": ry})
        return ShapeFactory.create_element_dict("ellipse", **attributes)
