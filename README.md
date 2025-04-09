# png2svg

A command-line utility to convert PNG images to SVG format using various conversion methods.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## What Does This Tool Do?

This tool takes your PNG images and converts them to SVG format. SVG files are vector-based, which means they can be scaled to any size without losing quality - perfect for logos, icons, and other graphics.

## Quick Start (The Easy Way)

This tool uses a modern Python package manager called `uv` to run without any complicated installation steps:

### 1. Install uv (if you don't have it already)

`uv` is a super-fast Python package manager written in Rust. It lets you run Python scripts without having to manually install dependencies or set up virtual environments - it handles all of that automatically.

```bash
# On macOS or Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, you might need to restart your terminal or add uv to your PATH.

### 2. Run the conversion tool directly

```bash
# Convert a single PNG file to SVG:
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert logo.png logo.svg
```

That's it! The command above will:
- Download the script
- Install all needed dependencies in an isolated environment
- Run the conversion
- Clean up afterward

No cloning repositories, no `pip install`, no mess left on your system!

## Features

- Convert individual PNG files to SVG
- Batch convert entire directories of PNG files
- Multiple conversion methods to choose from:
  - **Native** (default): Works everywhere with just Python packages
  - **AutoTrace**: Higher quality for simple images (if you have it installed)
  - **Potrace**: Great for photos and complex images (if you have it installed)
  - **Aspose.Words API**: Commercial-grade conversion
  - **ConvertAPI**: Web-based conversion service
- Smart fallback: Automatically uses the native method if external tools aren't available
- Built-in help and clear error messages

## Detailed Usage Examples

### Convert a Single File

```bash
# Basic conversion using the default method (works everywhere)
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg
```

### Using Different Conversion Methods

```bash
# Using AutoTrace (falls back to native if not installed)
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --method autotrace

# Using Potrace (falls back to native if not installed)
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --method potrace

# Using Aspose.Words API
uv run --with aspose-words https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --method aspose

# Using ConvertAPI (requires API key)
export CONVERTAPI_KEY="your-api-key"
uv run --with convertapi https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --method convertapi
```

### Batch Convert Multiple Files

```bash
# Convert all PNGs in a directory
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py batch input_dir/ output_dir/

# Convert recursively (including subdirectories)
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py batch input_dir/ output_dir/ --recursive
```

### Advanced Options

```bash
# Pass custom options to the converter (for external tools)
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --method autotrace --options "--filter-iterations 4 --dpi 300"

# Overwrite existing output files
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --overwrite

# Enable verbose logging
uv run https://raw.githubusercontent.com/nicobailon/png2svg/main/png2svg.py convert input.png output.svg --verbose
```

## How It Works

### What Makes This Tool Special?

This tool leverages several modern Python features:

1. **PEP 723 Inline Script Metadata**: The script includes its own dependency information, making it fully self-contained
2. **uv Package Manager**: Automatically handles dependencies without global installation
3. **Pure Python Fallbacks**: Always works even if you don't have external tools installed

### Conversion Methods Explained

1. **Native**: Pure Python conversion using PIL and svgwrite libraries (default, always works)
2. **AutoTrace**: Uses the AutoTrace command-line tool for better quality tracing (optional)
3. **Potrace**: Uses Potrace for high-quality vector tracing (optional)
4. **Aspose.Words**: Professional conversion library
5. **ConvertAPI**: Web-based conversion service

The native method works everywhere without any additional software. The other methods can provide better quality in specific situations but require additional software or services.

## Optional External Tools

For the best conversion quality with the AutoTrace or Potrace methods, you might want to install additional software:

### On Ubuntu/Debian:
```bash
sudo apt-get install autotrace potrace imagemagick
```

### On macOS:
```bash
brew install autotrace potrace imagemagick
```

### On Windows:
These tools are available but installation is more complex. The native method is recommended on Windows.

If these tools aren't installed, the script will automatically use the pure Python method without any error.

## Why Use This Approach?

Traditional Python tools usually require you to:
1. Clone a repository
2. Create a virtual environment
3. Install dependencies
4. Remember how to activate the environment later

With this modern approach:
1. Run the command directly - no clone needed
2. Dependencies are automatically managed
3. Nothing is installed globally on your system
4. Clean, isolated execution every time

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.