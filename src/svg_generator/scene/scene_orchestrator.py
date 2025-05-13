# src/svg_generator/scene/scene_orchestrator.py
from typing import List, Dict, Any
from svg_generator.style.style_profiles import StyleProfile
import logging

logger = logging.getLogger(__name__)

class SceneOrchestrator:
    """
    Takes parsed semantic elements and a style profile to create
    a structured scene description ready for SVG generation.
    This involves layout, applying styles, resolving relationships, etc.
    """
    def __init__(self, style: StyleProfile):
        self.style = style
        logger.debug(f"SceneOrchestrator initialized with style: {style.name}")

    def build_scene(self, parsed_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Constructs a detailed scene description.

        Args:
            parsed_elements: Output from SemanticParser.

        Returns:
            A dictionary representing the scene, including objects with
            concrete properties (positions, sizes, colors from style, etc.).
            Example: {
                'width': 800, 'height': 600, 'background_color': '#EEEEEE',
                'elements': [
                    {'type': 'circle', 'cx': 100, 'cy': 100, 'r': 50, 'fill': 'blue', ...},
                    {'type': 'rect', 'x': 200, 'y': 200, 'width': 80, 'height': 60, 'fill': 'red', ...}
                ]
            }
        """
        logger.info(f"Orchestrating scene with {len(parsed_elements)} semantic elements and style '{self.style.name}'.")
        
        scene_description: Dict[str, Any] = {
            "width": 800,  # Default or from style
            "height": 600, # Default or from style
            "background_color": self.style.background_color,
            "elements": []
        }
        
        # --- Placeholder Logic ---
        # This needs complex logic for layout, collision detection, z-ordering, etc.
        # For now, naively convert parsed elements to scene elements.
        
        current_x, current_y = 50, 50 # Very basic layout progression
        color_index = 0

        for i, element_data in enumerate(parsed_elements):
            if element_data.get("type") == "object":
                name = element_data.get("name", "unknown")
                attributes = element_data.get("attributes", {})
                
                # Determine color: specific attribute > palette cycling
                fill_color = attributes.get("color")
                if not fill_color:
                    fill_color = self.style.get_color(color_index)
                    color_index += 1
                
                scene_element: Dict[str, Any] = {
                    "id": f"element_{i}", # Basic ID
                    "type": name, # e.g. "circle", "square"
                    "fill": fill_color,
                    "stroke": self.style.get_color(0), # Example: first palette color for stroke
                    "stroke-width": self.style.line_width,
                    "opacity": self.style.opacity
                }
                
                if name == "circle":
                    scene_element.update({
                        "cx": current_x + 25, # Naive positioning
                        "cy": current_y + 25,
                        "r": 25 if self.style.shape_complexity == "simple" else 40
                    })
                    current_x += 60
                elif name == "square": # Assuming 'square' implies 'rect' for SVG
                    scene_element["type"] = "rect" # Map to SVG rect
                    scene_element.update({
                        "x": current_x,
                        "y": current_y,
                        "width": 50 if self.style.shape_complexity == "simple" else 80,
                        "height": 50 if self.style.shape_complexity == "simple" else 80
                    })
                    current_x += 60 if self.style.shape_complexity == "simple" else 90
                elif name == "sun": # Special object
                    scene_element["type"] = "circle"
                    scene_element.update({
                        "cx": scene_description["width"] - 70,
                        "cy": 70,
                        "r": 50,
                        "fill": attributes.get("color", "yellow") # Sun is usually yellow
                    })
                else:
                    logger.warning(f"Unknown object name '{name}' in parsed elements. Skipping for scene.")
                    continue

                scene_description["elements"].append(scene_element)
            
            elif element_data.get("type") == "unknown":
                logger.info(f"Handling 'unknown' parsed element: {element_data.get('description')}")
                # Could try to generate a placeholder text or a generic shape
                scene_description["elements"].append({
                    "id": f"unknown_{i}",
                    "type": "rect", # Placeholder shape
                    "x": current_x, "y": current_y, "width": 100, "height": 20,
                    "fill": self.style.get_color(color_index),
                    # Here we'd ideally convert text to path, but <text> is disallowed
                })
                current_x += 110
                color_index += 1


        if not scene_description["elements"] and parsed_elements:
            # If parsing yielded something but orchestration failed to produce visual elements
             logger.warning("Scene orchestration resulted in no visual elements despite parsed input.")
             scene_description["elements"].append({
                 "id": "fallback_placeholder", "type": "rect", "x": 10, "y": 10,
                 "width": scene_description["width"] - 20, "height": scene_description["height"] - 20,
                 "fill": "none", "stroke": "#AAAAAA", "stroke-width": 2,
                 "stroke-dasharray": "5,5" # Dashed line for placeholder
             })


        logger.debug(f"Final scene description: {scene_description}")
        return scene_description
