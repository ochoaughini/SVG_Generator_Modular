#!/usr/bin/env python3
# examples/basic_svg_generation.py
"""
Basic example of generating SVGs using the svg-generator library.

This example demonstrates how to use the main components of the SVG generator
to create a simple visual based on a text prompt.
"""
import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path for easier imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.svg_generator.parsing.semantic_parser import SemanticParser
from src.svg_generator.scene.scene_orchestrator import SceneOrchestrator
from src.svg_generator.svg.generator import SVGGenerator
from src.svg_generator.utils.sanitize import Sanitizer
from src.svg_generator.utils.optimizer import Optimizer

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_svg_from_prompt(prompt, output_path=None):
    """Generate an SVG from a text prompt and optionally save it to a file."""
    logger.info(f"Generating SVG from prompt: '{prompt}'")
    
    # Parse the text prompt
    parser = SemanticParser()
    parsed_elements = parser.parse(prompt)
    logger.info(f"Parsed {len(parsed_elements)} elements from prompt")
    
    # Build the scene
    orchestrator = SceneOrchestrator()
    scene = orchestrator.build_scene(parsed_elements)
    logger.info("Scene built successfully")
    
    # Generate SVG
    generator = SVGGenerator()
    svg_string = generator.generate(scene)
    logger.info(f"Generated SVG with length: {len(svg_string)}")
    
    # Sanitize and optimize
    sanitizer = Sanitizer()
    optimizer = Optimizer()
    
    sanitized_svg = sanitizer.sanitize_svg_string(svg_string)
    optimized_svg = optimizer.optimize_svg_string(sanitized_svg)
    
    logger.info(f"Original size: {len(svg_string)}, Optimized size: {len(optimized_svg)}")
    
    # Save to file if output path provided
    if output_path:
        with open(output_path, 'w') as f:
            f.write(optimized_svg)
        logger.info(f"SVG saved to: {output_path}")
    
    return optimized_svg

def main():
    """Run the example."""
    # Create output directory if it doesn't exist
    output_dir = project_root / "examples" / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Example 1: Simple geometric scene
    prompt1 = "A blue circle above a red square"
    output_path1 = output_dir / "geometric_scene.svg"
    generate_svg_from_prompt(prompt1, output_path1)
    
    # Example 2: More complex description
    prompt2 = "A green mountain landscape with a yellow sun in the sky"
    output_path2 = output_dir / "landscape.svg"
    generate_svg_from_prompt(prompt2, output_path2)
    
    # Example 3: Abstract pattern
    prompt3 = "A pattern of alternating purple and orange hexagons"
    output_path3 = output_dir / "pattern.svg"
    generate_svg_from_prompt(prompt3, output_path3)
    
    logger.info("All examples completed successfully")

if __name__ == "__main__":
    main()
