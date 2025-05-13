# src/svg_generator/utils/geometry.py
"""
Geometric utilities for SVG shape generation and manipulation.
"""
import math
from typing import Tuple, List, Dict, Any, Optional, Union
import random
import numpy as np
import logging

logger = logging.getLogger(__name__)

class GeometryUtils:
    """
    Provides geometric calculations and utilities for SVG generation.
    
    This class contains methods for calculating points, transformations,
    and other geometric operations needed for SVG shape generation.
    """
    
    @staticmethod
    def get_regular_polygon_points(cx: float, cy: float, radius: float, 
                                  sides: int, rotation: float = 0) -> List[Tuple[float, float]]:
        """
        Calculate points for a regular polygon.
        
        Args:
            cx: Center x-coordinate
            cy: Center y-coordinate
            radius: Radius of circumscribed circle
            sides: Number of sides
            rotation: Rotation in degrees
            
        Returns:
            List of (x, y) coordinate tuples
        """
        points = []
        rotation_rad = math.radians(rotation)
        
        for i in range(sides):
            angle = rotation_rad + i * 2 * math.pi / sides
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append((x, y))
            
        return points
    
    @staticmethod
    def get_star_points(cx: float, cy: float, outer_radius: float, inner_radius: float,
                       points: int, rotation: float = 0) -> List[Tuple[float, float]]:
        """
        Calculate points for a star shape.
        
        Args:
            cx: Center x-coordinate
            cy: Center y-coordinate
            outer_radius: Outer radius (points)
            inner_radius: Inner radius (valleys)
            points: Number of points
            rotation: Rotation in degrees
            
        Returns:
            List of (x, y) coordinate tuples
        """
        star_points = []
        rotation_rad = math.radians(rotation)
        
        for i in range(points * 2):
            angle = rotation_rad + i * math.pi / points
            radius = outer_radius if i % 2 == 0 else inner_radius
            
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            star_points.append((x, y))
            
        return star_points
    
    @staticmethod
    def get_rounded_rect_path(x: float, y: float, width: float, height: float, 
                             radius: Union[float, List[float]]) -> str:
        """
        Generate path data for a rounded rectangle.
        
        Args:
            x: Left coordinate
            y: Top coordinate
            width: Width of rectangle
            height: Height of rectangle
            radius: Corner radius or list of 4 radii [top-left, top-right, bottom-right, bottom-left]
            
        Returns:
            SVG path data string
        """
        # Normalize radius to a list of 4 values
        radii = [0, 0, 0, 0]
        
        if isinstance(radius, (int, float)):
            radii = [radius] * 4
        elif isinstance(radius, list):
            # Fill in missing radii if not all 4 are provided
            for i in range(min(4, len(radius))):
                radii[i] = radius[i]
        
        # Ensure radii are not too large
        max_radius_w = width / 2
        max_radius_h = height / 2
        
        for i in range(4):
            radii[i] = min(radii[i], max_radius_w, max_radius_h)
        
        # Create path with rounded corners
        path = []
        
        # Start at top-left after the corner
        path.append(f"M {x + radii[0]},{y}")
        
        # Top line and top-right corner
        path.append(f"H {x + width - radii[1]}")
        path.append(f"A {radii[1]},{radii[1]} 0 0 1 {x + width},{y + radii[1]}")
        
        # Right line and bottom-right corner
        path.append(f"V {y + height - radii[2]}")
        path.append(f"A {radii[2]},{radii[2]} 0 0 1 {x + width - radii[2]},{y + height}")
        
        # Bottom line and bottom-left corner
        path.append(f"H {x + radii[3]}")
        path.append(f"A {radii[3]},{radii[3]} 0 0 1 {x},{y + height - radii[3]}")
        
        # Left line and top-left corner
        path.append(f"V {y + radii[0]}")
        path.append(f"A {radii[0]},{radii[0]} 0 0 1 {x + radii[0]},{y}")
        
        # Close path
        path.append("Z")
        
        return " ".join(path)
    
    @staticmethod
    def get_arc_path(cx: float, cy: float, radius: float, 
                    start_angle: float, end_angle: float, 
                    clockwise: bool = True) -> str:
        """
        Generate path data for an arc.
        
        Args:
            cx: Center x-coordinate
            cy: Center y-coordinate
            radius: Radius of arc
            start_angle: Start angle in degrees
            end_angle: End angle in degrees
            clockwise: Direction of arc
            
        Returns:
            SVG path data string
        """
        # Convert angles to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        # Handle full circle case
        if abs(end_angle - start_angle) >= 360:
            # For a full circle, we need to use two arcs
            start_x = cx + radius * math.cos(start_rad)
            start_y = cy + radius * math.sin(start_rad)
            
            half_rad = start_rad + math.pi
            half_x = cx + radius * math.cos(half_rad)
            half_y = cy + radius * math.sin(half_rad)
            
            return (f"M {start_x},{start_y} "
                   f"A {radius},{radius} 0 1 {1 if clockwise else 0} {half_x},{half_y} "
                   f"A {radius},{radius} 0 1 {1 if clockwise else 0} {start_x},{start_y}")
        
        # Calculate start and end points
        start_x = cx + radius * math.cos(start_rad)
        start_y = cy + radius * math.sin(start_rad)
        
        end_x = cx + radius * math.cos(end_rad)
        end_y = cy + radius * math.sin(end_rad)
        
        # Determine large arc flag
        angle_diff = (end_angle - start_angle) % 360
        if clockwise:
            large_arc = 1 if angle_diff > 180 else 0
        else:
            large_arc = 1 if angle_diff < 180 else 0
            
        # Create arc path
        return (f"M {start_x},{start_y} "
               f"A {radius},{radius} 0 {large_arc} {1 if clockwise else 0} {end_x},{end_y}")
    
    @staticmethod
    def get_bezier_path(points: List[Tuple[float, float]], closed: bool = False) -> str:
        """
        Generate a cubic Bezier curve path through a set of points.
        
        Args:
            points: List of control points (x, y)
            closed: Whether to close the path
            
        Returns:
            SVG path data string
        """
        if len(points) < 2:
            return ""
            
        # Start at the first point
        path = [f"M {points[0][0]},{points[0][1]}"]
        
        # If only two points, draw a straight line
        if len(points) == 2:
            path.append(f"L {points[1][0]},{points[1][1]}")
        else:
            # For more points, calculate control points and create cubic curves
            for i in range(1, len(points)):
                # Simple method: use midpoints between adjacent points
                if i < len(points) - 1:
                    # Control points for current segment
                    cp1x = points[i][0] - (points[i][0] - points[i-1][0]) / 3
                    cp1y = points[i][1] - (points[i][1] - points[i-1][1]) / 3
                    
                    cp2x = points[i][0] + (points[i+1][0] - points[i][0]) / 3
                    cp2y = points[i][1] + (points[i+1][1] - points[i][1]) / 3
                    
                    path.append(f"C {cp1x},{cp1y} {cp2x},{cp2y} {points[i+1][0]},{points[i+1][1]}")
                else:
                    # Last segment
                    path.append(f"L {points[i][0]},{points[i][1]}")
        
        # Close the path if requested
        if closed:
            path.append("Z")
            
        return " ".join(path)
    
    @staticmethod
    def points_to_path_data(points: List[Tuple[float, float]], closed: bool = True) -> str:
        """
        Convert a list of points to SVG path data.
        
        Args:
            points: List of (x, y) coordinate tuples
            closed: Whether to close the path
            
        Returns:
            SVG path data string
        """
        if not points:
            return ""
            
        path_data = [f"M {points[0][0]},{points[0][1]}"]
        
        for x, y in points[1:]:
            path_data.append(f"L {x},{y}")
            
        if closed:
            path_data.append("Z")
            
        return " ".join(path_data)
    
    @staticmethod
    def get_random_points(num_points: int, min_x: float, max_x: float, 
                         min_y: float, max_y: float) -> List[Tuple[float, float]]:
        """
        Generate random points within specified bounds.
        
        Args:
            num_points: Number of points to generate
            min_x: Minimum x-coordinate
            max_x: Maximum x-coordinate
            min_y: Minimum y-coordinate
            max_y: Maximum y-coordinate
            
        Returns:
            List of (x, y) coordinate tuples
        """
        points = []
        
        for _ in range(num_points):
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            points.append((x, y))
            
        return points
    
    @staticmethod
    def transform_point(point: Tuple[float, float], 
                       translate: Optional[Tuple[float, float]] = None,
                       scale: Optional[Tuple[float, float]] = None,
                       rotate: Optional[float] = None,
                       center: Optional[Tuple[float, float]] = None) -> Tuple[float, float]:
        """
        Apply transformations to a point.
        
        Args:
            point: Point to transform (x, y)
            translate: Translation (dx, dy)
            scale: Scale factors (sx, sy)
            rotate: Rotation angle in degrees
            center: Center of rotation (cx, cy)
            
        Returns:
            Transformed point (x, y)
        """
        x, y = point
        
        # Apply translation
        if translate:
            dx, dy = translate
            x += dx
            y += dy
            
        # Apply scaling
        if scale:
            sx, sy = scale
            
            # Scale relative to origin or center
            if center:
                cx, cy = center
                x = cx + (x - cx) * sx
                y = cy + (y - cy) * sy
            else:
                x *= sx
                y *= sy
                
        # Apply rotation
        if rotate and rotate != 0:
            # Convert to radians
            angle_rad = math.radians(rotate)
            
            # Determine center of rotation
            if center:
                cx, cy = center
            else:
                cx, cy = 0, 0
                
            # Translate to origin, rotate, then translate back
            x_orig = x - cx
            y_orig = y - cy
            
            x_rot = x_orig * math.cos(angle_rad) - y_orig * math.sin(angle_rad)
            y_rot = x_orig * math.sin(angle_rad) + y_orig * math.cos(angle_rad)
            
            x = x_rot + cx
            y = y_rot + cy
            
        return (x, y)
    
    @staticmethod
    def get_grid_positions(cols: int, rows: int, cell_width: float, cell_height: float,
                          offset_x: float = 0, offset_y: float = 0) -> List[Tuple[float, float]]:
        """
        Calculate positions for a grid layout.
        
        Args:
            cols: Number of columns
            rows: Number of rows
            cell_width: Width of each cell
            cell_height: Height of each cell
            offset_x: X offset for the entire grid
            offset_y: Y offset for the entire grid
            
        Returns:
            List of (x, y) positions for cell centers
        """
        positions = []
        
        for row in range(rows):
            for col in range(cols):
                x = offset_x + (col + 0.5) * cell_width
                y = offset_y + (row + 0.5) * cell_height
                positions.append((x, y))
                
        return positions
    
    @staticmethod
    def get_radial_positions(cx: float, cy: float, radius: float, count: int,
                           start_angle: float = 0, end_angle: float = 360) -> List[Tuple[float, float]]:
        """
        Calculate positions arranged in a radial pattern.
        
        Args:
            cx: Center x-coordinate
            cy: Center y-coordinate
            radius: Radius of the circle
            count: Number of positions to generate
            start_angle: Start angle in degrees
            end_angle: End angle in degrees
            
        Returns:
            List of (x, y) positions
        """
        positions = []
        
        # Convert angles to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        # Calculate angular span
        span_rad = end_rad - start_rad
        
        for i in range(count):
            # Calculate angle for this position
            angle = start_rad + (span_rad * i / (count - 1 if count > 1 else 1))
            
            # Calculate coordinates
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            
            positions.append((x, y))
            
        return positions
