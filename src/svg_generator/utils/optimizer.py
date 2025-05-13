# src/svg_generator/utils/optimizer.py
"""
Optimization utilities for SVG content in competition contexts.
"""
import logging
from typing import Dict, Any, Tuple
import re

try:
    from scour import scourString
    from scour.scour import sanitizeOptions, scourDefaultOptions
    SCOUR_AVAILABLE = True
except ImportError:
    SCOUR_AVAILABLE = False
    logging.warning("Scour package not available. SVG optimization will be limited.")

from svg_generator.config import MAX_SVG_SIZE_BYTES, SCOUR_OPTIONS
from svg_generator.utils.sanitize import Sanitizer

logger = logging.getLogger(__name__)

class Optimizer:
    """
    Optimizes SVG content for competition submissions.
    
    Implements various strategies to minimize SVG file size while
    preserving visual quality for competition requirements.
    """
    
    def __init__(self):
        """Initialize the optimizer."""
        self.sanitizer = Sanitizer()
        
        # Initialize Scour options if available
        if SCOUR_AVAILABLE:
            self.scour_options = scourDefaultOptions()
            
            # Apply custom options from config
            for key, value in SCOUR_OPTIONS.items():
                setattr(self.scour_options, key, value)
            
            # Ensure critical options for size are set
            self.scour_options.remove_metadata = True
            self.scour_options.strip_xml_prolog = False # Keep prolog for validity
            self.scour_options.strip_comments = True
            self.scour_options.shorten_ids_prefix = 's' # Example prefix for shortened IDs
            self.scour_options.simple_colors = True
            self.scour_options.style_to_xml = True # Convert style attributes to XML attributes
            self.scour_options.group_collapse = True
            self.scour_options.digits = 2 # Max decimal places for numbers
            logger.debug("Optimizer initialized with Scour.")
        else:
            logger.warning("Optimizer initialized without Scour. Using fallback optimization.")
    
    def _apply_scour(self, svg_string: str) -> str:
        """
        Applies Scour optimization to the SVG string.
        
        Args:
            svg_string: The SVG string to optimize
            
        Returns:
            The optimized SVG string
        """
        if not SCOUR_AVAILABLE:
            logger.warning("Scour not available. Skipping Scour optimization.")
            return svg_string
        
        try:
            optimized_svg = scourString(svg_string, options=self.scour_options)
            if optimized_svg is None: # Scour can return None on failure
                logger.error("Scour returned None, optimization failed. Returning original string.")
                return svg_string
            logger.debug(f"SVG optimized with Scour. Original size: {len(svg_string)}, New size: {len(optimized_svg)}")
            return optimized_svg
        except Exception as e:
            logger.error(f"Error during Scour optimization: {e}. Returning original string.")
            return svg_string # Fallback
    
    def _apply_fallback_optimization(self, svg_string: str) -> str:
        """
        Applies fallback optimization techniques when Scour is not available.
        
        Args:
            svg_string: The SVG string to optimize
            
        Returns:
            The optimized SVG string
        """
        # Use the sanitizer methods for basic optimization
        result = self.sanitizer.remove_metadata(svg_string)
        result = self.sanitizer.minify_svg(result)
        result = self.sanitizer.simplify_paths(result, precision=1)
        
        # Remove unused attributes with regex
        default_attrs = [
            (r'\s+opacity="1"', ''),
            (r'\s+fill-opacity="1"', ''),
            (r'\s+stroke-opacity="1"', ''),
            (r'\s+stroke-linecap="butt"', ''),
            (r'\s+stroke-linejoin="miter"', '')
        ]
        
        for pattern, replacement in default_attrs:
            result = re.sub(pattern, replacement, result)
        
        logger.debug(f"Applied fallback optimization. Original size: {len(svg_string)}, New size: {len(result)}")
        return result
    
    def _apply_aggressive_optimization(self, svg_string: str) -> str:
        """
        Applies more aggressive optimization techniques if needed to meet size constraints.
        
        Args:
            svg_string: The SVG string to optimize further
            
        Returns:
            The aggressively optimized SVG string
        """
        logger.warning("Applying aggressive optimization to meet size constraints.")
        
        # If Scour is available, try with more aggressive settings
        if SCOUR_AVAILABLE:
            # Create a copy of options with more aggressive settings
            aggressive_options = scourDefaultOptions()
            
            # Copy current options
            for key, value in vars(self.scour_options).items():
                setattr(aggressive_options, key, value)
            
            # Set more aggressive options
            aggressive_options.remove_descriptive_elements = True
            aggressive_options.enable_viewboxing = True
            aggressive_options.indent_type = 'none'
            aggressive_options.strip_ids = True  # WARNING: This will break referenced elements
            aggressive_options.newlines = False
            aggressive_options.digits = 1  # Reduce precision further
            
            try:
                result = scourString(svg_string, options=aggressive_options)
                if result is not None:
                    return result
            except Exception as e:
                logger.error(f"Error during aggressive Scour optimization: {e}")
        
        # If Scour failed or is not available, use sanitizer with more aggressive settings
        result = self.sanitizer.remove_metadata(svg_string)
        result = self.sanitizer.minify_svg(result)
        result = self.sanitizer.simplify_paths(result, precision=0)  # Integer precision only
        
        # Additional aggressive optimization
        # Remove all newlines and extra spaces
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'>\s+<', '><', result)
        
        # Remove XML declaration if present
        result = re.sub(r'<\?xml[^>]+\?>', '', result)
        
        # Convert RGB colors to hex where possible
        result = re.sub(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', 
                        lambda m: '#{:02x}{:02x}{:02x}'.format(
                            int(m.group(1)), int(m.group(2)), int(m.group(3))), 
                        result)
        
        return result
    
    def optimize_svg_string(self, svg_string: str) -> str:
        """
        Optimizes an SVG string to reduce file size while preserving visual quality.
        
        Args:
            svg_string: The SVG string to optimize
            
        Returns:
            The optimized SVG string
        """
        logger.info("Starting SVG optimization process...")
        if not svg_string:
            logger.warning("Empty SVG string provided for optimization.")
            return ""
        
        # Apply initial optimization
        if SCOUR_AVAILABLE:
            current_svg = self._apply_scour(svg_string)
        else:
            current_svg = self._apply_fallback_optimization(svg_string)
        
        # Check size against limit
        current_size_bytes = len(current_svg.encode('utf-8'))
        logger.debug(f"Size after initial optimization: {current_size_bytes} bytes.")
        
        # If still too large, try aggressive optimization
        if current_size_bytes > MAX_SVG_SIZE_BYTES:
            logger.warning(
                f"SVG size ({current_size_bytes} bytes) exceeds max allowed size "
                f"({MAX_SVG_SIZE_BYTES} bytes) after initial optimization. "
                "Attempting aggressive optimization."
            )
            current_svg = self._apply_aggressive_optimization(current_svg)
            current_size_bytes = len(current_svg.encode('utf-8'))
            logger.info(f"Size after aggressive optimization: {current_size_bytes} bytes.")
            
            if current_size_bytes > MAX_SVG_SIZE_BYTES:
                logger.error(
                    f"CRITICAL: SVG size ({current_size_bytes} bytes) still exceeds max allowed size "
                    f"({MAX_SVG_SIZE_BYTES} bytes) after all optimization attempts."
                )
                # For competitions, this might be a critical issue
                # Depending on policy, either raise an error or return the oversized SVG with a warning
                
        logger.info(f"Optimization complete. Final SVG size: {current_size_bytes} bytes.")
        return current_svg
