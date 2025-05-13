# src/svg_generator/svg/generator.py
from typing import Dict, Any, List, Tuple
from xml.etree.ElementTree import Element, SubElement, tostring as el_tostring
from svg_generator.style.style_profiles import StyleProfile
from svg_generator.config import MAX_RECURSION_DEPTH_GENERATION, SHAPE_COMPLEXITY_PATH_POINTS_CAP
import logging

logger = logging.getLogger(__name__)

class SVGGenerator:
    """
    Generates an SVG string from a structured scene description.
    This class incorporates logic from the previous ConstrainedGenerator,
    focusing on creating SVG elements based on the orchestrated scene.
    """
    def __init__(self, style: StyleProfile): # Generator can also be style-aware
        self.style = style
        self.ns = {"": "http://www.w3.org/2000/svg"} # Default namespace
        logger.debug(f"SVGGenerator initialized with style: {self.style.name}")

    def _element_to_str(self, element: Element) -> str:
        """Converts an ElementTree element to a string with XML declaration."""
        # ElementTree doesn't add XML declaration by default with tostring(encoding='unicode')
        # We need a proper SVG string.
        svg_str = el_tostring(element, encoding="unicode", method="xml")
        # Ensure it starts with <?xml ...?> if not already present,
        # and has the SVG doctype or namespace correctly for SVG viewers.
        # For competition SVGs, sometimes prolog and doctype are omitted to save space.
        # Let's create a minimal valid SVG for now.
        return svg_str

    def _create_svg_element(self, scene_desc: Dict[str, Any]) -> Element:
        """Creates the root <svg> element."""
        svg_attrs = {
            "width": str(scene_desc.get("width", 800)),
            "height": str(scene_desc.get("height", 600)),
            "viewBox": f"0 0 {scene_desc.get('width', 800)} {scene_desc.get('height', 600)}",
            "xmlns": self.ns[""]
            # "xmlns:xlink": "http://www.w3.org/1999/xlink" # For href if needed, but often prohibited
        }
        svg_root = Element("svg", attrib=svg_attrs)
        
        # Optional: Add a background rectangle if specified
        bg_color = scene_desc.get("background_color")
        if bg_color and bg_color.lower() != "none" and bg_color.lower() != "transparent":
            SubElement(svg_root, "rect", attrib={
                "width": "100%",
                "height": "100%",
                "fill": bg_color
            })
        return svg_root

    def _add_defs(self, svg_root: Element, scene_desc: Dict[str, Any]) -> None:
        """Adds a <defs> section for gradients, patterns, etc."""
        defs_elements = scene_desc.get("definitions", []) # Expecting structured defs
        if not defs_elements:
            return

        defs_tag = SubElement(svg_root, "defs")
        for definition in defs_elements:
            def_type = definition.get("type")
            def_id = definition.get("id")
            if not def_type or not def_id:
                continue

            if def_type == "linearGradient":
                grad_attrs = {"id": def_id}
                grad_attrs.update(definition.get("attributes", {})) # x1, y1, x2, y2, gradientTransform
                gradient_el = SubElement(defs_tag, "linearGradient", attrib=grad_attrs)
                for stop in definition.get("stops", []):
                    SubElement(gradient_el, "stop", attrib=stop) # offset, stop-color, stop-opacity
            elif def_type == "radialGradient":
                grad_attrs = {"id": def_id}
                grad_attrs.update(definition.get("attributes", {})) # cx, cy, r, fx, fy, gradientTransform
                gradient_el = SubElement(defs_tag, "radialGradient", attrib=grad_attrs)
                for stop in definition.get("stops", []):
                    SubElement(gradient_el, "stop", attrib=stop) # offset, stop-color, stop-opacity
            elif def_type == "pattern":
                pattern_attrs = {"id": def_id}
                pattern_attrs.update(definition.get("attributes", {})) # x, y, width, height, patternUnits
                pattern_el = SubElement(defs_tag, "pattern", attrib=pattern_attrs)
                # Add the pattern content from children
                for child in definition.get("children", []):
                    self._add_element(pattern_el, child)

    def _add_element(self, parent_el: Element, element_desc: Dict[str, Any], depth: int = 0) -> None:
        """Adds a single SVG element (shape, group) to the parent."""
        if depth > MAX_RECURSION_DEPTH_GENERATION:
            logger.warning(f"Max recursion depth {MAX_RECURSION_DEPTH_GENERATION} reached for element: {element_desc.get('id')}")
            return

        el_type = element_desc.get("type")
        if not el_type:
            logger.warning(f"Element description missing 'type': {element_desc}")
            return
        
        attrs = {"id": element_desc.get("id", f"shape_{depth}_{parent_el.tag}")} # Basic ID

        # Common attributes from description (fill, stroke, opacity, etc.)
        common_attrs_keys = ["fill", "stroke", "stroke-width", "opacity", "transform"]
        for key in common_attrs_keys:
            if key in element_desc:
                attrs[key] = str(element_desc[key])
        
        # Type-specific attributes
        if el_type == "rect":
            for key in ["x", "y", "width", "height", "rx", "ry"]:
                if key in element_desc: attrs[key] = str(element_desc[key])
        elif el_type == "circle":
            for key in ["cx", "cy", "r"]:
                if key in element_desc: attrs[key] = str(element_desc[key])
        elif el_type == "polygon" or el_type == "polyline":
            points_val = element_desc.get("points")
            if isinstance(points_val, list): # Assuming list of tuples/lists [(x1,y1), (x2,y2)]
                attrs["points"] = " ".join([f"{p[0]},{p[1]}" for p in points_val])
            elif isinstance(points_val, str): # Already formatted string
                attrs["points"] = points_val
        elif el_type == "path":
            path_d = element_desc.get("d", "")
            if len(path_d.split()) > SHAPE_COMPLEXITY_PATH_POINTS_CAP * 2: # Rough estimate
                 logger.warning(f"Path {element_desc.get('id')} data exceeds complexity cap. May be truncated by optimizer.")
            attrs["d"] = path_d
        elif el_type == "g": # Group
            group_el = SubElement(parent_el, "g", attrib=attrs)
            for child_desc in element_desc.get("children", []):
                self._add_element(group_el, child_desc, depth + 1)
            return # Group processed, return early
        else:
            logger.warning(f"Unsupported element type '{el_type}' for direct generation. Element ID: {element_desc.get('id')}")
            return

        SubElement(parent_el, el_type, attrib=attrs)


    def generate(self, scene_description: Dict[str, Any]) -> str:
        """
        Generates the full SVG string from the scene description.

        Args:
            scene_description: The output from SceneOrchestrator.

        Returns:
            A string containing the SVG XML.
        """
        logger.info("Generating SVG from scene description...")
        
        svg_root = self._create_svg_element(scene_description)
        self._add_defs(svg_root, scene_description) # Add definitions if any

        # Add main visual elements
        elements_to_draw = scene_description.get("elements", [])
        if not elements_to_draw:
            logger.warning("No elements to draw in the scene description.")
            # Add a placeholder comment or visual indicator in SVG?
            # For now, just an empty SVG if no elements.

        for element_desc in elements_to_draw:
            self._add_element(svg_root, element_desc)
            
        # Convert the ElementTree to a string
        # Using 'unicode' gives a string, 'bytes' for actual bytes.
        # Optimizer and sanitizer will likely work with strings.
        svg_string = self._element_to_str(svg_root)
        logger.debug(f"SVG generation complete. Raw string length: {len(svg_string)}")
        return svg_string
