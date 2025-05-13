# src/svg_generator/utils/sanitize.py
"""
Utilities for ensuring SVG compliance with competition requirements.
"""
import xml.etree.ElementTree as ET
import re
import logging
from typing import Set, Optional, Tuple

from svg_generator.config import ALLOWED_SVG_TAGS, PROHIBITED_SVG_ATTRIBUTES

logger = logging.getLogger(__name__)

class Sanitizer:
    """
    Sanitizes SVG strings to ensure compliance with specified rules
    (e.g., allowed tags, prohibited attributes).
    """
    def __init__(self,
                 allowed_tags: Optional[Set[str]] = None,
                 prohibited_attributes: Optional[Set[str]] = None):
        self.allowed_tags = allowed_tags if allowed_tags is not None else ALLOWED_SVG_TAGS
        # 'id' needs special handling for defs. We'll disallow it generally,
        # but the optimizer (Scour) might manage IDs. Or allow 'id' and Scour handles unused ones.
        # For now, let's use config but be aware 'id' for defs is necessary.
        self.prohibited_attrs_global = prohibited_attributes if prohibited_attributes is not None else PROHIBITED_SVG_ATTRIBUTES
        logger.debug("Sanitizer initialized.")

    def _strip_namespace_from_tag(self, tag: str) -> str:
        """Removes xmlns URI part from tag, e.g., '{http://www.w3.org/2000/svg}svg' -> 'svg'."""
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag

    def _sanitize_element(self, element: ET.Element) -> Optional[ET.Element]:
        """
        Recursively sanitizes an element and its children.
        Removes disallowed tags and attributes.
        """
        original_tag = element.tag
        tag_name = self._strip_namespace_from_tag(original_tag)

        if tag_name not in self.allowed_tags:
            logger.warning(f"Removing disallowed tag: '{original_tag}' (parsed as '{tag_name}')")
            return None # Remove this element

        # Sanitize attributes
        current_attrs = dict(element.attrib) # Make a copy to iterate over
        for attr_name_raw in current_attrs:
            # Strip namespace from attribute name if present (e.g. xlink:href)
            attr_name = self._strip_namespace_from_tag(attr_name_raw)
            
            # Special handling for 'id' if it's in prohibited_attrs_global
            # We allow 'id' on <defs> children if that's the policy
            is_def_child = False
            # This check is basic; a proper check would trace parentage up to <defs>
            # For now, assume if 'id' is on a gradient or pattern, it's okay.
            if tag_name in ["linearGradient", "radialGradient", "pattern", "stop"]:
                 is_def_child = True

            if attr_name in self.prohibited_attrs_global and not (attr_name == "id" and is_def_child):
                logger.warning(f"Removing prohibited attribute '{attr_name_raw}' from tag '{tag_name}'.")
                del element.attrib[attr_name_raw]
            elif ":" in attr_name_raw: # Check for any namespaced attributes like xlink:
                prefix = attr_name_raw.split(":",1)[0]
                if prefix == "xlink" and "href" in attr_name_raw: # Specifically block xlink:href
                    logger.warning(f"Removing prohibited attribute '{attr_name_raw}' from tag '{tag_name}'.")
                    del element.attrib[attr_name_raw]
                # Add other specific namespace checks if needed

        # Recursively sanitize children
        children_to_remove = []
        for i, child in enumerate(list(element)): # Iterate over a copy for safe removal
            sanitized_child = self._sanitize_element(child)
            if sanitized_child is None:
                children_to_remove.append(child) # Mark for removal
            elif sanitized_child is not child: # Child was replaced (not typical here, but good practice)
                element[i] = sanitized_child


        for child_to_remove in children_to_remove:
            element.remove(child_to_remove)
            
        return element

    def sanitize_svg_string(self, svg_string: str) -> str:
        """
        Parses an SVG string, sanitizes it, and returns the sanitized SVG string.
        """
        logger.info("Starting SVG sanitization...")
        if not svg_string.strip():
            logger.warning("Empty SVG string provided for sanitization.")
            return ""
        try:
            # ET.fromstring might struggle with XML declarations or DOCTYPEs if present.
            # A more robust parser like lxml.etree.fromstring might be better if issues arise.
            # For now, assume a relatively clean SVG fragment or full SVG.
            # A common trick is to wrap in a dummy root if it's a fragment
            # but here we expect a full SVG string.
            
            # Attempt to parse, trying to handle potential XML declaration
            if svg_string.startswith("<?xml"):
                # Find the end of the XML declaration to parse from there
                end_of_prolog = svg_string.find("?>")
                if end_of_prolog != -1:
                    svg_content_part = svg_string[end_of_prolog+2:]
                else:
                    svg_content_part = svg_string # Should not happen with valid XML
            else:
                svg_content_part = svg_string

            if not svg_content_part.strip(): # Check if only prolog was present
                 logger.warning("SVG string contains only XML prolog or is empty after prolog removal.")
                 return svg_string # Return original if only prolog

            root = ET.fromstring(svg_content_part)
            sanitized_root = self._sanitize_element(root)

            if sanitized_root is None:
                logger.error("Root SVG element was disallowed during sanitization. Returning empty SVG.")
                return '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><text>Error: Root SVG removed</text></svg>' # Fallback error SVG

            # Reconstruct the string. ET.tostring typically uses 'us-ascii' by default for bytes.
            # For string output good to specify 'unicode'.
            output_svg = ET.tostring(sanitized_root, encoding="unicode", method="xml")
            
            # If original string had an XML prolog, re-add it if Scour/optimizer doesn't.
            # Generally, for competition SVGs, prologs are often omitted.
            # For now, let Scour/Optimizer handle the final prolog.

            logger.info("SVG sanitization complete.")
            return output_svg

        except ET.ParseError as e:
            logger.error(f"XML ParseError during sanitization: {e}. Returning original SVG string.")
            return svg_string # Fallback to original if parsing fails
        except Exception as e:
            logger.error(f"Unexpected error during sanitization: {e}. Returning original SVG string.")
            return svg_string
            
    @staticmethod
    def remove_metadata(svg_str: str) -> str:
        """
        Remove metadata and unnecessary attributes from SVG.
        
        Args:
            svg_str: SVG string to clean
            
        Returns:
            Cleaned SVG string
        """
        # Remove metadata tags
        svg_str = re.sub(r'<metadata>.*?</metadata>', '', svg_str, flags=re.DOTALL)
        
        # Remove comments
        svg_str = re.sub(r'<!--.*?-->', '', svg_str, flags=re.DOTALL)
        
        # Remove inkscape and other editor-specific namespaces
        svg_str = re.sub(r'\s+xmlns:(inkscape|sodipodi|dc|cc|rdf)="[^"]+"', '', svg_str)
        
        # Remove inkscape and other editor-specific attributes
        svg_str = re.sub(r'\s+(inkscape|sodipodi|dc|cc|rdf):[a-z\-]+="[^"]+"', '', svg_str)
        
        return svg_str
        
    @staticmethod
    def minify_svg(svg_str: str) -> str:
        """
        Minify SVG by removing whitespace and optimizing structure.
        
        Args:
            svg_str: SVG string to minify
            
        Returns:
            Minified SVG string
        """
        # Remove newlines and reduce white space
        svg_str = re.sub(r'\s+', ' ', svg_str)
        svg_str = re.sub(r'>\s+<', '><', svg_str)
        svg_str = re.sub(r'"\s+', '"', svg_str)
        svg_str = re.sub(r'\s+="', '="', svg_str)
        
        # Remove unnecessary attributes
        svg_str = re.sub(r'\s+version="[^"]+"', '', svg_str)
        
        # Optimize common patterns
        svg_str = re.sub(r'stroke-width="1"', 'stroke-width="1"', svg_str)  # No real change but here as example
        
        return svg_str.strip()
        
    @staticmethod
    def simplify_paths(svg_str: str, precision: int = 1) -> str:
        """
        Simplify path data by reducing decimal precision.
        
        Args:
            svg_str: SVG string to simplify
            precision: Number of decimal places to retain
            
        Returns:
            SVG with simplified paths
        """
        def round_numbers(match: re.Match) -> str:
            """Round numbers in path data"""
            path_data = match.group(1)
            
            # Find all numbers in path data and round them
            def replace_number(num_match: re.Match) -> str:
                num = float(num_match.group(0))
                rounded = round(num, precision)
                # Convert back to string, avoiding trailing zeros
                if rounded == int(rounded):
                    return str(int(rounded))
                else:
                    return str(rounded)
                    
            return 'd="' + re.sub(r'[-+]?[0-9]*\.?[0-9]+', replace_number, path_data) + '"'
            
        # Apply path simplification
        return re.sub(r'd="([^"]+)"', round_numbers, svg_str)
        
    @staticmethod
    def validate_size(svg_str: str, max_size_kb: float = 10.0) -> Tuple[bool, float]:
        """
        Check if SVG meets size constraints.
        
        Args:
            svg_str: SVG string to validate
            max_size_kb: Maximum size in kilobytes
            
        Returns:
            Tuple of (is_valid, actual_size_kb)
        """
        size_bytes = len(svg_str.encode('utf-8'))
        size_kb = size_bytes / 1024
        
        return (size_kb <= max_size_kb, size_kb)
