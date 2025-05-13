# src/svg_generator/svg/gradients.py
"""
Gradient definitions for enhanced SVG visual effects.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class GradientFactory:
    """
    Factory for creating gradient definitions for SVG elements.
    
    This class provides methods to create gradient dictionaries that can be 
    included in the scene description's 'definitions' section.
    """
    
    @staticmethod
    def create_linear_gradient(id: str, x1: float = 0, y1: float = 0,
                              x2: float = 1, y2: float = 0,
                              stops: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a linear gradient definition.
        
        Args:
            id: Unique identifier for the gradient
            x1: x-coordinate of the start point (0-1)
            y1: y-coordinate of the start point (0-1)
            x2: x-coordinate of the end point (0-1)
            y2: y-coordinate of the end point (0-1)
            stops: List of dictionaries with 'offset', 'stop-color', and optional 'stop-opacity'
            
        Returns:
            Dictionary representing the linear gradient definition
        """
        gradient_def = {
            "type": "linearGradient",
            "id": id,
            "attributes": {
                "x1": str(x1),
                "y1": str(y1),
                "x2": str(x2),
                "y2": str(y2)
            },
            "stops": stops or [
                {"offset": "0%", "stop-color": "#000000"},
                {"offset": "100%", "stop-color": "#FFFFFF"}
            ]
        }
        
        return gradient_def
        
    @staticmethod
    def create_radial_gradient(id: str, cx: float = 0.5, cy: float = 0.5,
                              r: float = 0.5, fx: Optional[float] = None, fy: Optional[float] = None,
                              stops: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a radial gradient definition.
        
        Args:
            id: Unique identifier for the gradient
            cx: x-coordinate of the center (0-1)
            cy: y-coordinate of the center (0-1)
            r: Radius of the gradient (0-1)
            fx: x-coordinate of the focal point (0-1), defaults to cx if None
            fy: y-coordinate of the focal point (0-1), defaults to cy if None
            stops: List of dictionaries with 'offset', 'stop-color', and optional 'stop-opacity'
            
        Returns:
            Dictionary representing the radial gradient definition
        """
        attributes = {
            "cx": str(cx),
            "cy": str(cy),
            "r": str(r)
        }
        
        if fx is not None:
            attributes["fx"] = str(fx)
        if fy is not None:
            attributes["fy"] = str(fy)
            
        gradient_def = {
            "type": "radialGradient",
            "id": id,
            "attributes": attributes,
            "stops": stops or [
                {"offset": "0%", "stop-color": "#FFFFFF"},
                {"offset": "100%", "stop-color": "#000000"}
            ]
        }
        
        return gradient_def
        
    @staticmethod
    def rainbow_gradient(id: str, horizontal: bool = True) -> Dict[str, Any]:
        """
        Create a rainbow gradient definition.
        
        Args:
            id: Unique identifier for the gradient
            horizontal: If True, gradient is horizontal, otherwise vertical
            
        Returns:
            Dictionary representing the rainbow linear gradient
        """
        stops = [
            {"offset": "0%", "stop-color": "#ff0000"},
            {"offset": "16.67%", "stop-color": "#ffff00"},
            {"offset": "33.33%", "stop-color": "#00ff00"},
            {"offset": "50%", "stop-color": "#00ffff"},
            {"offset": "66.67%", "stop-color": "#0000ff"},
            {"offset": "83.33%", "stop-color": "#ff00ff"},
            {"offset": "100%", "stop-color": "#ff0000"}
        ]
        
        if horizontal:
            return GradientFactory.create_linear_gradient(id, 0, 0, 1, 0, stops)
        else:
            return GradientFactory.create_linear_gradient(id, 0, 0, 0, 1, stops)
            
    @staticmethod
    def metallic_gradient(id: str, base_color: str = "#888888") -> Dict[str, Any]:
        """
        Create a metallic effect gradient definition.
        
        Args:
            id: Unique identifier for the gradient
            base_color: Base color of the metallic effect
            
        Returns:
            Dictionary representing the metallic linear gradient
        """
        stops = [
            {"offset": "0%", "stop-color": "#ffffff", "stop-opacity": "0.7"},
            {"offset": "45%", "stop-color": base_color},
            {"offset": "55%", "stop-color": base_color},
            {"offset": "100%", "stop-color": "#000000", "stop-opacity": "0.3"}
        ]
        
        return GradientFactory.create_linear_gradient(id, 0, 0, 0, 1, stops)
    
    @staticmethod
    def create_gradient_reference(gradient_id: str) -> str:
        """
        Creates a reference string for using a gradient in a fill or stroke attribute.
        
        Args:
            gradient_id: ID of the gradient to reference
            
        Returns:
            Reference string to use in fill or stroke attributes
        """
        return f"url(#{gradient_id})"
