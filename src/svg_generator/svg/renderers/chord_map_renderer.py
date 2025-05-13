# src/svg_generator/svg/renderers/chord_map_renderer.py
"""
Chord map rendering for complex relationship visualization.
"""
from typing import List, Dict, Tuple, Any, Optional
import math
import logging

from svg_generator.svg.shapes import ShapeFactory

logger = logging.getLogger(__name__)

class ChordMapRenderer:
    """
    Renders chord maps for visualizing relationships between entities.
    
    Implements algorithms for creating aesthetically pleasing chord diagrams
    that efficiently represent complex relationships for competitions.
    """
    
    def __init__(self, width: float = 800, height: float = 600):
        """
        Initialize the chord map renderer.
        
        Args:
            width: Width of the SVG canvas
            height: Height of the SVG canvas
        """
        self.width = width
        self.height = height
        logger.debug(f"ChordMapRenderer initialized: {width}x{height}")
        
    def generate_chord_diagram_elements(self, data: List[Dict[str, Any]], radius: float = None,
                              **attributes) -> List[Dict[str, Any]]:
        """
        Generate a chord diagram based on relationship data.
        
        Args:
            data: List of dictionaries with 'source', 'target', and 'value' keys
            radius: Radius of the chord diagram, defaults to 40% of min(width, height)
            **attributes: Additional attributes for the chord elements
            
        Returns:
            A list of SVG element dictionaries
        """
        # Set default attributes if not provided
        attrs = {
            "stroke": "#333333",
            "stroke-width": "1",
            "entity_fill": "#666666",
            "text_fill": "#000000",
            "font_size": "12"
        }
        attrs.update(attributes)
        
        # Calculate center and radius
        cx = self.width / 2
        cy = self.height / 2
        if radius is None:
            radius = min(self.width, self.height) * 0.4
            
        elements = []
        
        # Extract unique entities and assign them positions around the circle
        entities = set()
        for item in data:
            entities.add(item["source"])
            entities.add(item["target"])
            
        entity_list = sorted(list(entities))
        entity_positions = {}
        
        for i, entity in enumerate(entity_list):
            angle = 2 * math.pi * i / len(entity_list)
            entity_positions[entity] = {
                "angle": angle,
                "x": cx + radius * math.cos(angle),
                "y": cy + radius * math.sin(angle)
            }
            
        # Draw entity markers (circles for entities)
        for i, (entity, pos) in enumerate(entity_positions.items()):
            # Draw circle for entity
            circle = ShapeFactory.create_circle(
                pos["x"], pos["y"], 5,
                fill=attrs.get("entity_fill"),
                id=f"entity_marker_{i}"
            )
            elements.append(circle)
            
            # Text labels would typically go here, but text elements are often not
            # allowed in competition SVGs. In a real implementation, you might:
            # 1. Use SVG <text> elements if allowed
            # 2. Create text as paths
            # 3. Omit labels entirely
            
            # For those not using this for competitions, here's how you'd add text:
            # (This part would be converted to actual SVG during generation)
            text_x = cx + (radius + 15) * math.cos(pos["angle"])
            text_y = cy + (radius + 15) * math.sin(pos["angle"])
            
            # Note: this dictionary representation would need special handling
            # in the SVGGenerator to be converted to proper <text> elements
            text = {
                "type": "text",
                "id": f"entity_label_{i}",
                "x": text_x,
                "y": text_y,
                "text-anchor": "middle",
                "dominant-baseline": "middle",
                "font-size": attrs.get("font_size"),
                "fill": attrs.get("text_fill"),
                "_text_content": entity  # Special field for text content
            }
            
            # Add rotation for readability
            if pos["angle"] > math.pi/2 and pos["angle"] < 3*math.pi/2:
                text["transform"] = f"rotate({180 + pos['angle']*180/math.pi}, {text_x}, {text_y})"
            else:
                text["transform"] = f"rotate({pos['angle']*180/math.pi}, {text_x}, {text_y})"
                
            # This would be used if text elements are allowed
            if attrs.get("include_text", False):
                elements.append(text)
            
        # Draw the chords (relationship lines/curves)
        for i, item in enumerate(data):
            source_pos = entity_positions[item["source"]]
            target_pos = entity_positions[item["target"]]
            value = item.get("value", 1)
            
            # Scale value to determine chord width
            max_width = 10
            width = max(1, min(max_width, value))
            
            # Create a Bezier curve representing the chord
            # Control points for the curve (toward the center)
            cp1x = cx + (source_pos["x"] - cx) * 0.5
            cp1y = cy + (source_pos["y"] - cy) * 0.5
            cp2x = cx + (target_pos["x"] - cx) * 0.5
            cp2y = cy + (target_pos["y"] - cy) * 0.5
            
            # Create the path data
            path_data = f"M {source_pos['x']},{source_pos['y']} "
            path_data += f"C {cp1x},{cp1y} {cp2x},{cp2y} {target_pos['x']},{target_pos['y']}"
            
            # Create the path element
            path_attrs = {
                "id": f"chord_{i}",
                "d": path_data,
                "fill": "none",
                "stroke": attrs.get("stroke"),
                "stroke-width": width
            }
            
            # Add opacity based on value
            opacity = 0.3 + (0.7 * min(1, value / 10))
            path_attrs["opacity"] = opacity
            
            path = ShapeFactory.create_path(path_data, **path_attrs)
            elements.append(path)
            
        return elements
        
    def generate_matrix_chord_elements(self, matrix: List[List[float]], 
                            labels: List[str] = None, 
                            radius: float = None,
                            **attributes) -> List[Dict[str, Any]]:
        """
        Generate a chord diagram from a matrix of relationships.
        
        Args:
            matrix: Square matrix where [i][j] represents relationship from i to j
            labels: Optional list of labels for entities
            radius: Radius of the chord diagram, defaults to 40% of min(width, height)
            **attributes: Additional attributes for the chord elements
            
        Returns:
            A list of SVG element dictionaries
        """
        # Set default attributes
        attrs = {
            "stroke": "#333333",
            "stroke-width": "1",
            "entity_fill": "#cccccc",
            "text_fill": "#000000",
            "font_size": "12",
            "forward_color": "#3366cc",
            "backward_color": "#cc3366",
            "equal_color": "#666666"
        }
        attrs.update(attributes)
        
        # Calculate center and radius
        cx = self.width / 2
        cy = self.height / 2
        if radius is None:
            radius = min(self.width, self.height) * 0.4
            
        elements = []
        
        # Ensure matrix is square
        n = len(matrix)
        if not all(len(row) == n for row in matrix):
            logger.error("Matrix must be square")
            return []
            
        # Create default labels if not provided
        if labels is None:
            labels = [f"Entity {i+1}" for i in range(n)]
        elif len(labels) != n:
            logger.error("Number of labels must match matrix dimensions")
            return []
            
        # Calculate entity positions
        entity_positions = []
        for i in range(n):
            angle = 2 * math.pi * i / n
            entity_positions.append({
                "angle": angle,
                "x": cx + radius * math.cos(angle),
                "y": cy + radius * math.sin(angle)
            })
            
        # Draw entity markers and arcs
        for i, pos in enumerate(entity_positions):
            # Draw arc segment for entity
            arc_width = 2 * math.pi / n
            
            # Draw arc
            start_angle = pos["angle"] - arc_width/2
            end_angle = pos["angle"] + arc_width/2
            
            # Create arc path
            large_arc_flag = 0 if arc_width <= math.pi else 1
            
            start_x = cx + radius * math.cos(start_angle)
            start_y = cy + radius * math.sin(start_angle)
            end_x = cx + radius * math.cos(end_angle)
            end_y = cy + radius * math.sin(end_angle)
            
            path_data = f"M {cx},{cy} "
            path_data += f"L {start_x},{start_y} "
            path_data += f"A {radius},{radius} 0 {large_arc_flag},1 {end_x},{end_y} "
            path_data += f"Z"
            
            # Create the arc element
            entity_color = attrs.get(f"entity_fill_{i}", attrs.get("entity_fill"))
            arc_path = ShapeFactory.create_path(
                path_data,
                fill=entity_color,
                stroke="none",
                id=f"entity_segment_{i}"
            )
            elements.append(arc_path)
            
            # Add text label (if using text elements)
            text_x = cx + (radius + 20) * math.cos(pos["angle"])
            text_y = cy + (radius + 20) * math.sin(pos["angle"])
            
            # Similar to the chord diagram, text handling would depend on requirements
            if attrs.get("include_text", False):
                text = {
                    "type": "text",
                    "id": f"entity_label_{i}",
                    "x": text_x,
                    "y": text_y,
                    "text-anchor": "middle",
                    "dominant-baseline": "middle",
                    "font-size": attrs.get("font_size"),
                    "fill": attrs.get("text_fill"),
                    "_text_content": labels[i]
                }
                
                # Add rotation for readability
                if pos["angle"] > math.pi/2 and pos["angle"] < 3*math.pi/2:
                    text["transform"] = f"rotate({180 + pos['angle']*180/math.pi}, {text_x}, {text_y})"
                else:
                    text["transform"] = f"rotate({pos['angle']*180/math.pi}, {text_x}, {text_y})"
                    
                elements.append(text)
            
        # Draw chords based on matrix values
        for i in range(n):
            for j in range(i+1, n):  # Only process each pair once (i->j)
                value_ij = matrix[i][j]
                value_ji = matrix[j][i]
                
                # Skip if no relationship exists in either direction
                if value_ij <= 0 and value_ji <= 0:
                    continue
                    
                # Draw chord based on combined values
                combined_value = value_ij + value_ji
                
                # Scale value to determine chord width
                max_width = 10
                width = max(1, min(max_width, combined_value))
                
                source_pos = entity_positions[i]
                target_pos = entity_positions[j]
                
                # Control points for the curve
                cp1x = cx + (source_pos["x"] - cx) * 0.5
                cp1y = cy + (source_pos["y"] - cy) * 0.5
                cp2x = cx + (target_pos["x"] - cx) * 0.5
                cp2y = cy + (target_pos["y"] - cy) * 0.5
                
                # Create the path data
                path_data = f"M {source_pos['x']},{source_pos['y']} "
                path_data += f"C {cp1x},{cp1y} {cp2x},{cp2y} {target_pos['x']},{target_pos['y']}"
                
                # Determine color based on relationship direction
                chord_color = attrs.get("equal_color")
                if value_ij > value_ji:
                    chord_color = attrs.get("forward_color")
                elif value_ji > value_ij:
                    chord_color = attrs.get("backward_color")
                
                # Add opacity based on value
                opacity = 0.3 + (0.7 * min(1, combined_value / 10))
                
                # Create the path element
                path = ShapeFactory.create_path(
                    path_data,
                    id=f"chord_{i}_{j}",
                    fill="none",
                    stroke=chord_color,
                    stroke_width=width,
                    opacity=opacity
                )
                elements.append(path)
                
        return elements
