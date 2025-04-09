# png2svg

A command-line utility to convert PNG images to SVG format using various conversion methods, with built-in dependency management via uv.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Features

- Convert individual PNG files to SVG
- Batch convert entire directories of PNG files
- Recursive directory processing
- Multiple conversion methods:
  - AutoTrace (default, falls back to Pillow if not installed)
  - Potrace (falls back to Pillow if not installed)
  - Pillow (built-in, always available)
  - Aspose.Words API
  - ConvertAPI
- PEP 723 inline script metadata for easy dependency management with uv
- Rich progress indicators and better terminal output
- Comprehensive error handling
- Detailed logging

## Quick Start

This tool uses [uv](https://github.com/astral-sh/uv) and inline script metadata ([PEP 723](https://peps.python.org/pep-0723/)) for dependency management, making it extremely easy to run without manual installation:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the script directly without cloning the repository
# Dependencies will be installed automatically
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert logo.png logo.svg
```

**NEW!** The tool now includes a built-in Pillow-based converter that works without any external dependencies, ensuring you can always convert your PNG files to SVG directly!

## Usage

### Basic Usage

Convert a single PNG file to SVG:

```bash
# If you've downloaded the script locally:
uv run png2svg.py convert input.png output.svg

# Or run directly from GitHub:
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg
```

### Using Different Conversion Methods

```bash
# Using built-in Pillow method (no external dependencies)
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --method pillow

# Using Potrace (if installed, falls back to Pillow if not)
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --method potrace

# Using Aspose.Words API (will automatically add aspose-words dependency)
uv run --with aspose-words https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --method aspose

# Using ConvertAPI (requires API key)
export CONVERTAPI_KEY="your-api-key"
uv run --with convertapi https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --method convertapi
```

### Batch Convert Multiple Files

```bash
# Convert all PNGs in a directory
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py batch input_dir/ output_dir/

# Convert recursively
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py batch input_dir/ output_dir/ --recursive
```

### Advanced Options

```bash
# Pass custom options to the converter
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --options "--filter-iterations 4 --dpi 300"

# Overwrite existing output files
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --overwrite

# Enable verbose logging
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --verbose
```

## External Dependencies (Optional)

The script includes a built-in Pillow-based converter that works without any external tools. However, for better quality conversions, you may want to install the following tools:

### On Debian/Ubuntu:
```bash
apt-get install autotrace potrace imagemagick
```

### On macOS with Homebrew:
```bash
brew install autotrace potrace imagemagick
```

If these tools aren't installed, the script will automatically fall back to the built-in Pillow converter.

## How It Works

This tool uses different methods to convert PNG raster images to SVG vector graphics:

1. **AutoTrace**: Uses the AutoTrace command-line tool to trace bitmap images (falls back to Pillow if not installed)
2. **Potrace**: Uses Potrace (with ImageMagick for preprocessing) for high-quality vector tracing (falls back to Pillow if not installed)
3. **Pillow**: Pure Python conversion using Pillow and CairoSVG (always available)
4. **Aspose.Words**: Uses the Aspose.Words Python library for conversion
5. **ConvertAPI**: Uses the ConvertAPI web service for conversion

The best method depends on your specific image and needs:
- AutoTrace works well for simple images and logos
- Potrace often provides better results for complex images
- Pillow is always available and works without any external dependencies
- The API-based methods can be useful when you can't install external tools

## Dependency Management

This tool uses PEP 723 inline script metadata and uv for dependency management. The core dependencies (typer, rich, pathlib, pillow, cairosvg) are automatically installed when you run the script with `uv run`. 

For Aspose or ConvertAPI methods, the script will notify you if additional dependencies are needed. You can add them like this:

```bash
# For Aspose method
uv run --with aspose-words https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --method aspose

# For ConvertAPI method
uv run --with convertapi https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --method convertapi
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.