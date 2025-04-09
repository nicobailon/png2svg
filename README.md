# png2svg

A command-line utility to convert PNG images to SVG format using various conversion methods.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Features

- Convert individual PNG files to SVG
- Batch convert entire directories of PNG files
- Recursive directory processing
- Multiple conversion methods:
  - AutoTrace (default)
  - Potrace
  - Aspose.Words API
  - ConvertAPI
- Custom conversion options
- Comprehensive error handling
- Detailed logging

## Installation

```bash
# Clone the repository
git clone https://github.com/nicobailon/png2svg.git
cd png2svg

# Install dependencies
pip install -r requirements.txt

# Install external dependencies (for AutoTrace and Potrace methods)
# On Debian/Ubuntu:
apt-get install autotrace potrace imagemagick

# On macOS with Homebrew:
brew install autotrace potrace imagemagick
```

## Usage

### Basic Usage

Convert a single PNG file to SVG:

```bash
python png2svg.py input.png output.svg
```

### Using Different Conversion Methods

```bash
# Using Potrace
python png2svg.py input.png output.svg --method potrace

# Using Aspose.Words API
python png2svg.py input.png output.svg --method aspose

# Using ConvertAPI (requires API key)
export CONVERTAPI_KEY="your-api-key"
python png2svg.py input.png output.svg --method convertapi
```

### Batch Convert Multiple Files

```bash
# Convert all PNGs in a directory
python png2svg.py --batch input_dir/ output_dir/

# Convert recursively
python png2svg.py --batch input_dir/ output_dir/ --recursive
```

### Advanced Options

```bash
# Pass custom options to the converter
python png2svg.py input.png output.svg --options "--filter-iterations 4 --dpi 300"

# Overwrite existing output files
python png2svg.py input.png output.svg --overwrite

# Enable verbose logging
python png2svg.py input.png output.svg --verbose
```

## Full Command Reference

```
usage: png2svg.py [-h] (--batch | [input_file]) [output_file] 
                  [--method {autotrace,potrace,aspose,convertapi}]
                  [--options OPTIONS] [--overwrite] [--verbose] [--recursive]

Convert PNG images to SVG format.

positional arguments:
  input_file            Path to the input PNG file
  output_file           Path to the output SVG file

options:
  -h, --help            show this help message and exit
  --batch               Batch convert PNG files in a directory
  --method {autotrace,potrace,aspose,convertapi}
                        Conversion method to use (default: autotrace)
  --options OPTIONS     Custom options to pass to the converter (e.g., '--filter-iterations 4')
  --overwrite           Overwrite output file if it exists
  --verbose, -v         Enable verbose logging
  --recursive, -r       Recursively process directories (batch mode only)
```

## Examples

```bash
# Convert a simple icon
python png2svg.py icon.png icon.svg

# Convert a photo with optimized settings
python png2svg.py photo.png photo.svg --method potrace --options "--dpi 300 --filter-iterations 4"

# Batch convert website assets
python png2svg.py --batch assets/images/ assets/vectors/ --recursive
```

## How It Works

This tool uses different methods to convert PNG raster images to SVG vector graphics:

1. **AutoTrace**: Uses the AutoTrace command-line tool to trace bitmap images
2. **Potrace**: Uses Potrace (with ImageMagick for preprocessing) for high-quality vector tracing
3. **Aspose.Words**: Uses the Aspose.Words Python library for conversion
4. **ConvertAPI**: Uses the ConvertAPI web service for conversion

The best method depends on your specific image and needs:
- AutoTrace works well for simple images and logos
- Potrace often provides better results for complex images
- The API-based methods can be useful when you can't install external tools

## Dependencies

- Python 3.6+
- For `autotrace` method: AutoTrace (external program)
- For `potrace` method: Potrace and ImageMagick (external programs)
- For `aspose` method: aspose-words Python library
- For `convertapi` method: convertapi Python library and API key

## Development

### Testing

Run the tests with:

```bash
pytest
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.