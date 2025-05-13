# SVG Generator

Advanced SVG generator from text prompts, optimized for competitions and illustrative purposes.

## Features

* Semantic parsing of text prompts
* Scene orchestration with layering and composition
* Style profile management for consistent aesthetics
* Advanced SVG element generation (shapes, gradients, patterns)
* 3D perspective rendering for complex visualizations
* Chord map visualization for relationship data
* Output optimization and sanitization (Scour integration)
* Compliance with typical competition constraints (e.g., Kaggle)
* Command-Line Interface

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/svg-generator-merged.git
   cd svg-generator-merged
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```
4. (Optional) Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Usage

### Command Line Interface

```bash
svg-generator "A blue circle next to a red square under a yellow sun" --style vibrant --output my_scene.svg
```

For more options:
```bash
svg-generator --help
```

### Python API

```python
from svg_generator.parsing.semantic_parser import SemanticParser
from svg_generator.scene.scene_orchestrator import SceneOrchestrator
from svg_generator.style.style_profiles import StyleProfile
from svg_generator.svg.generator import SVGGenerator
from svg_generator.utils.optimizer import Optimizer

# Parse text prompt
parser = SemanticParser()
parsed_elements = parser.parse("A blue circle next to a red square under a yellow sun")

# Load style profile
style_profile = StyleProfile.load("vibrant")

# Orchestrate scene
orchestrator = SceneOrchestrator(style_profile)
scene_description = orchestrator.build_scene(parsed_elements)

# Generate SVG
generator = SVGGenerator(style_profile)
svg_content = generator.generate(scene_description)

# Optimize SVG
optimizer = Optimizer()
optimized_svg = optimizer.optimize_svg_string(svg_content)

# Save to file
with open("output.svg", "w", encoding="utf-8") as f:
    f.write(optimized_svg)
```

## Project Structure

```
svg-generator-merged/
├── src/
│   └── svg_generator/            # Main package
│       ├── parsing/              # Text prompt parsing
│       ├── scene/                # Scene orchestration
│       ├── style/                # Style profiles
│       ├── svg/                  # SVG generation
│       │   └── renderers/        # Specialized renderers
│       └── utils/                # Utilities
├── tests/                        # Test suite
├── examples/                     # Examples
└── docs/                         # Documentation
```

## Development

* Run tests: `pytest`
* Check formatting and linting: `black . && ruff check .`
* Type checking: `mypy src/`
* Build documentation: `cd docs && make html`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
