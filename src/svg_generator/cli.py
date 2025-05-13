# src/svg_generator/cli.py
import argparse
import json
import logging
import os
from typing import Dict, Any

from .config import DEFAULT_STYLE_PROFILE_NAME, STYLE_PROFILES_DIR
from .parsing.semantic_parser import SemanticParser
from .scene.scene_orchestrator import SceneOrchestrator
from .style.style_profiles import StyleProfile
from .svg.generator import SVGGenerator # Assuming this is the main generator class
from .utils.optimizer import Optimizer
from .utils.sanitize import Sanitizer

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main() -> None:
    """Main entry point for the SVG generator CLI."""
    parser = argparse.ArgumentParser(description="Generates illustrative SVG from text prompts.")
    parser.add_argument("prompt", help="Textual description of the scene to generate.")
    parser.add_argument(
        "--style",
        default=DEFAULT_STYLE_PROFILE_NAME,
        help=f"Name of the style profile to use (e.g., 'default', 'dreamy'). Looks in '{STYLE_PROFILES_DIR}/'. (default: {DEFAULT_STYLE_PROFILE_NAME})"
    )
    parser.add_argument(
        "--output",
        default="output.svg",
        help="Filename for the output SVG. (default: output.svg)"
    )
    parser.add_argument(
        "--style-dir",
        default=None,
        help=f"Custom directory to load style profiles from. Defaults to a pre-configured path within the package."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging."
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled.")

    logger.info(f"Received prompt: \"{args.prompt}\"")
    logger.info(f"Using style: {args.style}")
    logger.info(f"Output file: {args.output}")

    # 1. Load Style Profile
    try:
        # Determine style directory: argument > package default
        style_profiles_path = args.style_dir
        if not style_profiles_path:
            # Assume STYLE_PROFILES_DIR is relative to the package installation
            # This needs robust path handling, e.g., using importlib.resources
            base_path = os.path.dirname(__file__) # src/svg_generator
            style_profiles_path = os.path.join(base_path, "style", STYLE_PROFILES_DIR)
            logger.debug(f"Using default style profiles path: {style_profiles_path}")


        # Example: Create a dummy default style profile if it doesn't exist for demonstration
        dummy_default_style_file = os.path.join(style_profiles_path, "default.json")
        if not os.path.exists(style_profiles_path):
            os.makedirs(style_profiles_path)
        if not os.path.exists(dummy_default_style_file):
            with open(dummy_default_style_file, "w") as f_style:
                json.dump({
                    "name": "default",
                    "description": "A basic default style.",
                    "palette": ["#FF0000", "#00FF00", "#0000FF"], # Red, Green, Blue
                    "background_color": "#FFFFFF",
                    "line_width": 1,
                    "opacity": 1.0,
                    "shape_complexity": "simple" # simple, medium, complex
                }, f_style, indent=2)
            logger.info(f"Created dummy '{dummy_default_style_file}' as it was missing.")


        style_profile_data = StyleProfile.load(args.style, custom_profiles_dir=style_profiles_path)
        logger.info(f"Successfully loaded style profile: {style_profile_data.name}")
    except FileNotFoundError:
        logger.error(f"Style profile '{args.style}.json' not found in '{style_profiles_path}'. Exiting.")
        return
    except Exception as e:
        logger.error(f"Error loading style profile '{args.style}': {e}. Exiting.")
        return

    # 2. Semantic Parsing
    logger.debug("Initializing SemanticParser...")
    semantic_parser = SemanticParser()
    try:
        parsed_elements = semantic_parser.parse(args.prompt)
        logger.info(f"Parsed prompt into {len(parsed_elements)} semantic elements.")
        logger.debug(f"Parsed elements: {parsed_elements}")
    except Exception as e:
        logger.error(f"Error during semantic parsing: {e}. Exiting.")
        return

    # 3. Scene Orchestration
    logger.debug("Initializing SceneOrchestrator...")
    scene_orchestrator = SceneOrchestrator(style_profile_data)
    try:
        scene_description = scene_orchestrator.build_scene(parsed_elements)
        logger.info("Scene orchestrated successfully.")
        logger.debug(f"Scene description: {scene_description}") # This would be a complex object
    except Exception as e:
        logger.error(f"Error during scene orchestration: {e}. Exiting.")
        return

    # 4. SVG Generation
    logger.debug("Initializing SVGGenerator...")
    svg_generator = SVGGenerator(style_profile_data) # Generator might also need style context
    try:
        raw_svg_content = svg_generator.generate(scene_description)
        logger.info("SVG content generated.")
        logger.debug(f"Raw SVG length: {len(raw_svg_content)} bytes")
    except Exception as e:
        logger.error(f"Error during SVG generation: {e}. Exiting.")
        return

    # 5. Sanitization
    logger.debug("Initializing Sanitizer...")
    sanitizer = Sanitizer()
    try:
        sanitized_svg_content = sanitizer.sanitize_svg_string(raw_svg_content)
        logger.info("SVG content sanitized.")
        logger.debug(f"Sanitized SVG length: {len(sanitized_svg_content)} bytes")
    except Exception as e:
        logger.error(f"Error during SVG sanitization: {e}. Using raw SVG for optimizer.")
        sanitized_svg_content = raw_svg_content # Fallback for optimizer

    # 6. Optimization
    logger.debug("Initializing Optimizer...")
    optimizer = Optimizer()
    try:
        optimized_svg_content = optimizer.optimize_svg_string(sanitized_svg_content)
        logger.info("SVG content optimized.")
        final_svg_size_bytes = len(optimized_svg_content.encode('utf-8'))
        logger.info(f"Final optimized SVG size: {final_svg_size_bytes} bytes.")
    except Exception as e:
        logger.error(f"Error during SVG optimization: {e}. Using sanitized SVG for output.")
        optimized_svg_content = sanitized_svg_content # Fallback for output


    # 7. Output to file
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(optimized_svg_content)
        logger.info(f"Successfully wrote SVG to {args.output}")
    except IOError as e:
        logger.error(f"Error writing SVG to file '{args.output}': {e}")

if __name__ == "__main__":
    main()
