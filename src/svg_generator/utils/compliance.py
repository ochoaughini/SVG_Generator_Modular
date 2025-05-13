# src/svg_generator/utils/compliance.py
"""
Utilities for ensuring SVG compliance with competition requirements.
"""
import re
import logging
from typing import List, Dict, Set, Optional, Union
import xml.etree.ElementTree as ET
from lxml import etree as lxml_etree

logger = logging.getLogger(__name__)

class ComplianceUtils:
    """
    Utilities for ensuring SVG compliance with competition requirements.
    
    This class contains methods to ensure that generated SVGs meet
    the specific requirements of various competitions.
    """
    
    @staticmethod
    def remove_unused_defs(svg_str: str) -> str:
        """
        Remove unused gradients, patterns, and other definitions from SVG.
        
        This is a critical optimization for competition SVGs to reduce file size
        by eliminating definitions that aren't actually used in the document.
        
        Args:
            svg_str: SVG string to process
            
        Returns:
            SVG string with unused definitions removed
        """
        try:
            # Use lxml for better feature support
            parser = lxml_etree.XMLParser(remove_blank_text=True)
            try:
                tree = lxml_etree.fromstring(svg_str.encode('utf-8'), parser)
            except lxml_etree.XMLSyntaxError:
                logger.error("Failed to parse SVG XML with lxml. Returning original SVG.")
                return svg_str
                
            namespaces = {'svg': 'http://www.w3.org/2000/svg'}
            
            # Find all defined IDs in defs section
            defined_ids = set()
            defs_elements = tree.xpath("//svg:defs", namespaces=namespaces)
            
            if not defs_elements:
                # No defs section found, nothing to clean
                logger.debug("No defs section found in SVG.")
                return svg_str
                
            # Collect all defined IDs in defs sections
            for defs in defs_elements:
                for element in defs.xpath(".//*[@id]", namespaces=namespaces):
                    defined_ids.add(element.get('id'))
            
            if not defined_ids:
                logger.debug("No defined IDs found in defs section.")
                return svg_str
                
            logger.debug(f"Found {len(defined_ids)} defined IDs: {', '.join(defined_ids)}")
            
            # Find all references to defined IDs
            used_ids = set()
            
            # Check url(#id) references in various attributes
            ref_attrs = ['fill', 'stroke', 'filter', 'clip-path', 'mask']
            for attr in ref_attrs:
                for element in tree.xpath(f"//*[@{attr}]", namespaces=namespaces):
                    attr_value = element.get(attr, '')
                    if 'url(#' in attr_value:
                        # Extract ID from url(#id)
                        match = re.search(r'url\(#([^)]+)\)', attr_value)
                        if match:
                            used_ids.add(match.group(1))
            
            # Check href/xlink:href references (e.g., in <use> elements)
            for element in tree.xpath("//*[@href or @*[local-name()='href']]", namespaces=namespaces):
                href = element.get('href') or element.get('{http://www.w3.org/1999/xlink}href', '')
                if href and href.startswith('#'):
                    used_ids.add(href[1:])  # Remove the leading '#'
            
            logger.debug(f"Found {len(used_ids)} used IDs: {', '.join(used_ids)}")
            
            # Determine unused IDs
            unused_ids = defined_ids - used_ids
            
            if not unused_ids:
                logger.debug("No unused definitions found.")
                return svg_str
                
            logger.info(f"Found {len(unused_ids)} unused definitions to remove: {', '.join(unused_ids)}")
            
            # Remove elements with unused IDs from defs
            for defs in defs_elements:
                for element in defs.xpath(".//*[@id]", namespaces=namespaces):
                    if element.get('id') in unused_ids:
                        parent = element.getparent()
                        if parent is not None:
                            parent.remove(element)
            
            # Convert back to string
            cleaned_svg = lxml_etree.tostring(tree, encoding='utf-8', pretty_print=False, 
                                          xml_declaration=True).decode('utf-8')
            
            logger.info(f"Successfully removed {len(unused_ids)} unused definitions.")
            return cleaned_svg
            
        except Exception as e:
            logger.error(f"Error removing unused defs: {e}. Returning original SVG.")
            return svg_str
    
    @staticmethod
    def check_competition_compliance(svg_str: str, max_size_bytes: int = 10240) -> Dict[str, Union[bool, str]]:
        """
        Check if SVG meets competition requirements.
        
        Args:
            svg_str: SVG string to validate
            max_size_bytes: Maximum allowed size in bytes
            
        Returns:
            Dict with validation results
        """
        results = {
            "is_valid": True,
            "issues": []
        }
        
        # Check size
        svg_bytes = svg_str.encode('utf-8')
        size_bytes = len(svg_bytes)
        if size_bytes > max_size_bytes:
            results["is_valid"] = False
            results["issues"].append(
                f"SVG size ({size_bytes} bytes) exceeds maximum allowed size ({max_size_bytes} bytes)"
            )
        
        # Check for script elements (often prohibited)
        if "<script" in svg_str.lower():
            results["is_valid"] = False
            results["issues"].append("SVG contains prohibited <script> elements")
        
        # Check for external references
        # For SVG inline images
        if "xlink:href" in svg_str and (
            "data:" in svg_str or 
            "http:" in svg_str or 
            "https:" in svg_str or 
            ".jpg" in svg_str.lower() or
            ".png" in svg_str.lower() or
            ".jpeg" in svg_str.lower()
        ):
            results["is_valid"] = False
            results["issues"].append("SVG contains external image references (data:, http:, or image files)")
        
        # Check for animation elements (often prohibited in competitions)
        animation_tags = ["<animate", "<animatetransform", "<animatemotion", "<set"]
        for tag in animation_tags:
            if tag in svg_str.lower():
                results["is_valid"] = False
                results["issues"].append(f"SVG contains animation elements ({tag})")
        
        return results
    
    @staticmethod
    def limit_decimal_precision(svg_str: str, precision: int = 1) -> str:
        """
        Limit decimal precision in SVG coordinates and values.
        
        Args:
            svg_str: SVG string to process
            precision: Number of decimal places to keep
            
        Returns:
            SVG with limited decimal precision
        """
        # Process numeric attributes
        def replace_numbers(match):
            attr_name = match.group(1)
            attr_val = match.group(2)
            
            # Don't process certain attributes
            if attr_name.lower() in ['opacity', 'fill-opacity', 'stroke-opacity']:
                return f'{attr_name}="{attr_val}"'
            
            # Process numbers in the attribute value
            def round_number(num_match):
                num_str = num_match.group(0)
                try:
                    num = float(num_str)
                    # Only round if it actually has decimals
                    if num == int(num):
                        return str(int(num))
                    else:
                        return str(round(num, precision))
                except ValueError:
                    return num_str
            
            processed = re.sub(r'-?\d+\.\d+', round_number, attr_val)
            return f'{attr_name}="{processed}"'
        
        # Process attributes with numeric values
        result = re.sub(r'([a-zA-Z\-:]+)="([^"]*\d+\.\d+[^"]*)"', replace_numbers, svg_str)
        
        # Process path data specially (d attribute)
        def process_path_data(match):
            d_attr = match.group(1)
            
            # Process numbers in path data
            def round_path_number(num_match):
                num_str = num_match.group(0)
                try:
                    num = float(num_str)
                    # Only round if it actually has decimals
                    if num == int(num):
                        return str(int(num))
                    else:
                        return str(round(num, precision))
                except ValueError:
                    return num_str
            
            processed = re.sub(r'-?\d+\.\d+', round_path_number, d_attr)
            return f'd="{processed}"'
        
        # Process path data
        result = re.sub(r'd="([^"]+)"', process_path_data, result)
        
        return result
    
    @staticmethod
    def ensure_viewbox(svg_str: str) -> str:
        """
        Ensure SVG has a proper viewBox attribute.
        
        Args:
            svg_str: SVG string to process
            
        Returns:
            SVG with proper viewBox
        """
        # Check if viewBox already exists
        viewbox_pattern = r'<svg[^>]*viewBox=["\'][^"\']*["\'][^>]*>'
        if re.search(viewbox_pattern, svg_str):
            return svg_str
            
        # Try to extract width and height
        width_match = re.search(r'<svg[^>]*width=["\'](\d+(?:\.\d+)?(?:px)?)["\'][^>]*>', svg_str)
        height_match = re.search(r'<svg[^>]*height=["\'](\d+(?:\.\d+)?(?:px)?)["\'][^>]*>', svg_str)
        
        if width_match and height_match:
            # Convert to numeric values
            width = width_match.group(1)
            height = height_match.group(1)
            
            # Remove px suffix if present
            width = width.replace('px', '')
            height = height.replace('px', '')
            
            # Create viewBox attribute
            viewbox = f'viewBox="0 0 {width} {height}"'
            
            # Add viewBox to SVG tag
            result = re.sub(r'<svg', f'<svg {viewbox}', svg_str, count=1)
            
            logger.info(f"Added viewBox attribute: {viewbox}")
            return result
        
        # If width and height not found, leave as is
        logger.warning("Could not add viewBox: width and/or height attributes not found")
        return svg_str
