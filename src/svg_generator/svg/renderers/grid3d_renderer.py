# src/svg_generator/svg/renderers/grid3d_renderer.py
"""
3D grid rendering for SVG with perspective effects.
"""
from typing import List, Dict, Any, Tuple
import math
import logging

from svg_generator.svg.shapes import ShapeFactory

logger = logging.getLogger(__name__)

class Grid3DRenderer:
    """
    Renders 3D grid structures in SVG with perspective effects.
    
    This class implements algorithms for 3D projections onto a 2D SVG canvas,
    with options for different viewpoints and rendering styles.
    """
    
    def __init__(self, width: float = 800, height: float = 600, 
                 fov: float = 60, z_near: float = 0.1, z_far: float = 100):
        """
        Initialize the 3D grid renderer.
        
        Args:
            width: Width of the view plane
            height: Height of the view plane
            fov: Field of view in degrees
            z_near: Near clipping plane distance
            z_far: Far clipping plane distance
        """
        self.width = width
        self.height = height
        self.fov = fov * math.pi / 180  # Convert to radians
        self.z_near = z_near
        self.z_far = z_far
        
        # Camera position and orientation
        self.camera_pos = [0, 0, -5]
        self.camera_target = [0, 0, 0]
        self.camera_up = [0, 1, 0]
        
        logger.debug(f"Grid3DRenderer initialized: {width}x{height}, FOV: {fov}")
        
    def _project_point(self, point: List[float]) -> Tuple[float, float]:
        """
        Project a 3D point onto the 2D canvas using perspective projection.
        
        Args:
            point: 3D point [x, y, z]
            
        Returns:
            2D projected point (x, y)
        """
        # Translate point relative to camera
        rel_x = point[0] - self.camera_pos[0]
        rel_y = point[1] - self.camera_pos[1]
        rel_z = point[2] - self.camera_pos[2]
        
        # Simple perspective projection
        if rel_z <= 0:  # Avoid division by zero and points behind camera
            rel_z = 0.0001
            
        # Perspective division
        aspect = self.width / self.height
        scale = math.tan(self.fov / 2)
        
        projected_x = (rel_x / (rel_z * scale * aspect)) * (self.width / 2) + (self.width / 2)
        projected_y = (-rel_y / (rel_z * scale)) * (self.height / 2) + (self.height / 2)
        
        return (projected_x, projected_y)
        
    def set_camera(self, position: List[float], target: List[float] = None, up: List[float] = None):
        """
        Set the camera position and orientation.
        
        Args:
            position: [x, y, z] camera position
            target: [x, y, z] point the camera is looking at, defaults to [0, 0, 0]
            up: [x, y, z] up vector, defaults to [0, 1, 0]
        """
        self.camera_pos = position
        if target is not None:
            self.camera_target = target
        if up is not None:
            self.camera_up = up
        logger.debug(f"Camera position set to {position}")
        
    def generate_cube_elements(self, center: List[float], size: float, **attributes) -> List[Dict[str, Any]]:
        """
        Generate a 3D cube as a list of SVG element dictionaries.
        
        Args:
            center: Center point of the cube [x, y, z]
            size: Size of the cube
            **attributes: Additional attributes for the cube lines
            
        Returns:
            A list of SVG element dictionaries
        """
        # Set default attributes if not provided
        attrs = {
            "stroke": "#000000",
            "stroke-width": "1",
            "fill": "none"
        }
        attrs.update(attributes)
        
        # Define the cube vertices
        half_size = size / 2
        vertices = [
            [center[0] - half_size, center[1] - half_size, center[2] - half_size],  # 0: front bottom left
            [center[0] + half_size, center[1] - half_size, center[2] - half_size],  # 1: front bottom right
            [center[0] + half_size, center[1] + half_size, center[2] - half_size],  # 2: front top right
            [center[0] - half_size, center[1] + half_size, center[2] - half_size],  # 3: front top left
            [center[0] - half_size, center[1] - half_size, center[2] + half_size],  # 4: back bottom left
            [center[0] + half_size, center[1] - half_size, center[2] + half_size],  # 5: back bottom right
            [center[0] + half_size, center[1] + half_size, center[2] + half_size],  # 6: back top right
            [center[0] - half_size, center[1] + half_size, center[2] + half_size]   # 7: back top left
        ]
        
        # Define the edges
        edges = [
            # Front face
            (0, 1), (1, 2), (2, 3), (3, 0),
            # Back face
            (4, 5), (5, 6), (6, 7), (7, 4),
            # Connecting edges
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        
        # Project vertices
        projected_vertices = [self._project_point(v) for v in vertices]
        
        # Create line elements
        elements = []
        for i, edge in enumerate(edges):
            start, end = edge
            line = ShapeFactory.create_line(
                projected_vertices[start][0],
                projected_vertices[start][1],
                projected_vertices[end][0],
                projected_vertices[end][1],
                **attrs,
                id=f"cube_edge_{i}"
            )
            elements.append(line)
            
        return elements
        
    def generate_grid_elements(self, center: List[float], size: float, 
                          divisions: int, **attributes) -> List[Dict[str, Any]]:
        """
        Generate a 3D grid as a list of SVG element dictionaries.
        
        Args:
            center: Center point of the grid [x, y, z]
            size: Size of the grid
            divisions: Number of divisions along each axis
            **attributes: Additional attributes for the grid lines
            
        Returns:
            A list of SVG element dictionaries
        """
        # Set default attributes if not provided
        attrs = {
            "stroke": "#888888",
            "stroke-width": "0.5",
            "fill": "none"
        }
        attrs.update(attributes)
        
        half_size = size / 2
        step = size / divisions
        
        elements = []
        line_count = 0
        
        # Create horizontal grid lines (along X-axis)
        for i in range(divisions + 1):
            z = center[2] - half_size + i * step
            for j in range(divisions + 1):
                y = center[1] - half_size + j * step
                
                # Create horizontal line along X
                start = [center[0] - half_size, y, z]
                end = [center[0] + half_size, y, z]
                
                # Project points and create line
                start_2d = self._project_point(start)
                end_2d = self._project_point(end)
                
                line = ShapeFactory.create_line(
                    start_2d[0], start_2d[1],
                    end_2d[0], end_2d[1],
                    **attrs,
                    id=f"grid_line_x_{line_count}"
                )
                elements.append(line)
                line_count += 1
                    
        # Create vertical grid lines (along Y-axis)
        for i in range(divisions + 1):
            z = center[2] - half_size + i * step
            for j in range(divisions + 1):
                x = center[0] - half_size + j * step
                
                # Create vertical line along Y
                start = [x, center[1] - half_size, z]
                end = [x, center[1] + half_size, z]
                
                # Project points and create line
                start_2d = self._project_point(start)
                end_2d = self._project_point(end)
                
                line = ShapeFactory.create_line(
                    start_2d[0], start_2d[1],
                    end_2d[0], end_2d[1],
                    **attrs,
                    id=f"grid_line_y_{line_count}"
                )
                elements.append(line)
                line_count += 1
                    
        return elements
        
    def generate_radial_pattern_elements(self, radius: float, segments: int = 36, 
                               rings: int = 5, **attributes) -> List[Dict[str, Any]]:
        """
        Generate a 3D radial pattern as a list of SVG element dictionaries.
        
        Args:
            radius: Maximum radius of the pattern
            segments: Number of angular segments
            rings: Number of concentric rings
            **attributes: Additional attributes for the pattern
            
        Returns:
            A list of SVG element dictionaries
        """
        # Set default attributes if not provided
        attrs = {
            "stroke": "#444444",
            "stroke-width": "0.5",
            "fill": "none"
        }
        attrs.update(attributes)
        
        elements = []
        
        # Create rings
        for r in range(1, rings + 1):
            current_radius = radius * r / rings
            
            # Create circle points
            points = []
            for s in range(segments):
                angle = 2 * math.pi * s / segments
                x = current_radius * math.cos(angle)
                y = 0
                z = current_radius * math.sin(angle)
                
                # Transform to camera space
                points.append([x, y, z])
                
            # Project points
            projected_points = [self._project_point(p) for p in points]
            
            # Create path for the ring
            path_data = f"M {projected_points[0][0]},{projected_points[0][1]}"
            for point in projected_points[1:]:
                path_data += f" L {point[0]},{point[1]}"
            path_data += " Z"  # Close the path
            
            path = ShapeFactory.create_path(
                path_data,
                **attrs,
                id=f"radial_ring_{r}"
            )
            elements.append(path)
                
        # Create radial lines
        for s in range(segments):
            angle = 2 * math.pi * s / segments
            
            start = [0, 0, 0]
            end = [radius * math.cos(angle), 0, radius * math.sin(angle)]
            
            # Project points
            start_2d = self._project_point(start)
            end_2d = self._project_point(end)
            
            line = ShapeFactory.create_line(
                start_2d[0], start_2d[1],
                end_2d[0], end_2d[1],
                **attrs,
                id=f"radial_line_{s}"
            )
            elements.append(line)
                
        return elements
