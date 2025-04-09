#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "pathlib>=1.0.1",
#   "typer>=0.9.0",
#   "rich>=13.6.0",
#   "cairosvg>=2.7.0",
#   "Pillow>=10.0.0",
# ]
# [tool.uv]
# exclude-newer = "2025-04-09T00:00:00Z"
# ///
"""
PNG to SVG Converter

A command line tool to convert PNG images to SVG format using various methods.

Run with: uv run png2svg.py --help
"""

import os
import subprocess
import sys
import tempfile
import shutil
from enum import Enum
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any, Union
import logging
from datetime import datetime
import io

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.logging import RichHandler
from PIL import Image
import cairosvg

# Set up rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("png2svg")
console = Console()

# Create Typer app
app = typer.Typer(
    help="Convert PNG images to SVG format using various methods.",
    add_completion=False,
)

class ConversionMethod(str, Enum):
    """Conversion methods available for PNG to SVG conversion."""
    AUTOTRACE = "autotrace"
    POTRACE = "potrace"
    PILLOW = "pillow"
    ASPOSE = "aspose"
    CONVERTAPI = "convertapi"

def ensure_directory(file_path: Union[str, Path]) -> None:
    """
    Ensure the directory for the output file exists.
    
    Args:
        file_path: Path to the file
    """
    directory = os.path.dirname(str(file_path))
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def validate_file(file_path: Union[str, Path], check_exists: bool = True, 
                  check_extension: Optional[str] = None) -> Path:
    """
    Validate file path.
    
    Args:
        file_path: Path to the file
        check_exists: Whether to check if the file exists
        check_extension: Expected file extension
        
    Returns:
        Path object for the file
        
    Raises:
        FileNotFoundError: If file doesn't exist and check_exists is True
    """
    path = Path(file_path)
    
    if check_exists and not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if check_extension and path.suffix.lower() != check_extension.lower():
        logger.warning(f"File {file_path} does not have the expected extension {check_extension}")
    
    return path

def is_command_available(command: str) -> bool:
    """
    Check if a command is available on the system.
    
    Args:
        command: The command to check
        
    Returns:
        True if the command is available, False otherwise
    """
    return shutil.which(command) is not None

def convert_pillow(input_file: str, output_file: str, options: Optional[str] = None) -> bool:
    """
    Convert PNG to SVG using Pillow and CairoSVG.
    This is a native Python method that doesn't require external tools.
    
    Args:
        input_file: Path to input PNG file
        output_file: Path to output SVG file
        options: Custom options (not used for this method)
        
    Returns:
        True if conversion was successful, False otherwise
    """
    try:
        # Use Pillow to read the PNG and CairoSVG to write the SVG
        img = Image.open(input_file)
        
        # Save as an SVG using a simple path approach
        # We'll create a simple SVG with the image embedded as a data URL
        width, height = img.size
        
        # Convert to PNG data URL
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_data = img_buffer.getvalue()
        
        # Create a basic SVG with the image embedded
        svg_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
     width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <image width="{width}" height="{height}" x="0" y="0" 
         xlink:href="data:image/png;base64,{img_data.hex()}"/>
</svg>
"""
        
        # Write the SVG file
        with open(output_file, 'w') as f:
            f.write(svg_content)
            
        return True
    except Exception as e:
        logger.error(f"Error during conversion with Pillow: {e}")
        return False

def convert_autotrace(input_file: str, output_file: str, options: Optional[str] = None) -> bool:
    """
    Convert PNG to SVG using autotrace.
    
    Args:
        input_file: Path to input PNG file
        output_file: Path to output SVG file
        options: Custom options to pass to autotrace
        
    Returns:
        True if conversion was successful, False otherwise
    """
    if not is_command_available("autotrace"):
        logger.warning("AutoTrace is not installed. It's recommended for best results.")
        logger.warning("Install on Ubuntu/Debian: sudo apt-get install autotrace")
        logger.warning("Install on macOS: brew install autotrace")
        logger.warning("Falling back to built-in method...")
        return convert_pillow(input_file, output_file, options)
    
    cmd = ["autotrace"]
    
    if options:
        for opt in options.split():
            cmd.append(opt)
    else:
        # Default options
        cmd.extend(["--output-format", "svg"])
    
    cmd.extend(["--output-file", output_file, input_file])
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during conversion with autotrace: {e}")
        if e.stderr:
            logger.error(f"Error details: {e.stderr}")
        return False

def convert_potrace(input_file: str, output_file: str, options: Optional[str] = None) -> bool:
    """
    Convert PNG to SVG using potrace.
    
    Args:
        input_file: Path to input PNG file
        output_file: Path to output SVG file
        options: Custom options to pass to potrace
        
    Returns:
        True if conversion was successful, False otherwise
    """
    if not is_command_available("potrace") or not is_command_available("convert"):
        logger.warning("Potrace or ImageMagick (convert) is not installed.")
        logger.warning("Install on Ubuntu/Debian: sudo apt-get install potrace imagemagick")
        logger.warning("Install on macOS: brew install potrace imagemagick")
        logger.warning("Falling back to built-in method...")
        return convert_pillow(input_file, output_file, options)
    
    # Potrace requires a bitmap file, so we need to convert PNG to PBM first
    pbm_file = f"{os.path.splitext(input_file)[0]}.pbm"
    
    try:
        # Convert PNG to PBM using ImageMagick
        subprocess.run(
            ["convert", input_file, pbm_file],
            check=True, capture_output=True, text=True
        )
        
        # Use potrace to convert PBM to SVG
        cmd = ["potrace"]
        
        if options:
            for opt in options.split():
                cmd.append(opt)
        else:
            # Default options
            cmd.extend(["-s", "--svg"])
        
        cmd.extend(["-o", output_file, pbm_file])
        
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Clean up temporary PBM file
        os.remove(pbm_file)
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during conversion with potrace: {e}")
        if e.stderr:
            logger.error(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def convert_with_library(input_file: str, output_file: str, method: str = 'aspose') -> bool:
    """
    Convert PNG to SVG using a Python library.
    
    Args:
        input_file: Path to input PNG file
        output_file: Path to output SVG file
        method: Library to use for conversion ('aspose' or 'convertapi')
        
    Returns:
        True if conversion was successful, False otherwise
    """
    if method == 'aspose':
        try:
            # Since we're not including aspose-words in the dependencies
            # by default, we'll need to import it dynamically
            import importlib
            try:
                aspose = importlib.import_module('aspose.words')
                doc = aspose.Document()
                builder = aspose.DocumentBuilder(doc)
                shape = builder.insert_image(input_file)
                shape.get_shape_renderer().save(output_file, aspose.saving.ImageSaveOptions(aspose.SaveFormat.SVG))
                return True
            except ImportError:
                logger.error("Aspose.Words library not found. Use uv run --with aspose-words png2svg.py for Aspose method.")
                logger.warning("Falling back to built-in method...")
                return convert_pillow(input_file, output_file)
        except Exception as e:
            logger.error(f"Error during conversion with Aspose: {e}")
            return False
    elif method == 'convertapi':
        try:
            # Since we're not including convertapi in the dependencies
            # by default, we'll need to import it dynamically
            import importlib
            try:
                convertapi = importlib.import_module('convertapi')
                api_key = os.environ.get('CONVERTAPI_KEY')
                if not api_key:
                    logger.error("ConvertAPI key not found. Set the CONVERTAPI_KEY environment variable.")
                    logger.warning("Falling back to built-in method...")
                    return convert_pillow(input_file, output_file)
                
                convertapi.api_secret = api_key
                result = convertapi.convert('svg', {'File': input_file})
                result.save_files(output_file)
                return True
            except ImportError:
                logger.error("ConvertAPI library not found. Use uv run --with convertapi png2svg.py for ConvertAPI method.")
                logger.warning("Falling back to built-in method...")
                return convert_pillow(input_file, output_file)
        except Exception as e:
            logger.error(f"Error during conversion with ConvertAPI: {e}")
            return False
    else:
        logger.error(f"Unknown conversion method: {method}")
        return False

def png_to_svg(
    input_file: str, 
    output_file: str, 
    method: str = 'autotrace', 
    options: Optional[str] = None, 
    overwrite: bool = False
) -> bool:
    """
    Convert a PNG file to SVG using the specified method.
    
    Args:
        input_file: Path to input PNG file
        output_file: Path to output SVG file
        method: Conversion method to use
        options: Custom options to pass to the converter
        overwrite: Whether to overwrite the output file if it exists
        
    Returns:
        True if conversion was successful, False otherwise
    """
    try:
        # Validate input file
        input_path = validate_file(input_file, check_exists=True, check_extension='.png')
        
        # Validate output file
        output_path = Path(output_file)
        if output_path.exists() and not overwrite:
            raise FileExistsError(f"Output file already exists: {output_file}. Use --overwrite to overwrite.")
        
        if output_path.suffix.lower() != '.svg':
            logger.warning(f"Output file {output_file} does not have .svg extension")
        
        # Ensure output directory exists
        ensure_directory(output_file)
        
        # Perform the conversion
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task(f"[green]Converting {input_path.name} to {output_path.name}...", total=None)
            
            if method == 'autotrace':
                success = convert_autotrace(str(input_path), output_file, options)
            elif method == 'potrace':
                success = convert_potrace(str(input_path), output_file, options)
            elif method == 'pillow':
                success = convert_pillow(str(input_path), output_file, options)
            elif method in ['aspose', 'convertapi']:
                success = convert_with_library(str(input_path), output_file, method)
            else:
                logger.error(f"Unknown conversion method: {method}")
                return False
        
        if success:
            console.print(f"[green]Conversion successful! SVG saved at: {output_file}")
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        return False

def batch_convert(
    input_dir: str, 
    output_dir: str, 
    method: str = 'autotrace', 
    options: Optional[str] = None, 
    overwrite: bool = False, 
    recursive: bool = False
) -> bool:
    """
    Batch convert PNG files in a directory to SVG.
    
    Args:
        input_dir: Input directory containing PNG files
        output_dir: Output directory for SVG files
        method: Conversion method to use
        options: Custom options to pass to the converter
        overwrite: Whether to overwrite existing output files
        recursive: Whether to recursively process subdirectories
        
    Returns:
        True if at least one file was converted successfully, False otherwise
    """
    input_path = Path(input_dir)
    
    if not input_path.is_dir():
        logger.error(f"Input path is not a directory: {input_dir}")
        return False
    
    # Get all PNG files
    if recursive:
        png_files = list(input_path.glob('**/*.png'))
    else:
        png_files = list(input_path.glob('*.png'))
    
    if not png_files:
        logger.warning(f"No PNG files found in {input_dir}")
        return False
    
    logger.info(f"Found {len(png_files)} PNG files to convert")
    
    success_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"[green]Converting files...", total=len(png_files))
        
        for png_file in png_files:
            # Determine the output file path
            rel_path = png_file.relative_to(input_path) if recursive else png_file.name
            output_file = Path(output_dir) / rel_path.with_suffix('.svg')
            
            # Ensure output directory exists
            ensure_directory(str(output_file))
            
            progress.update(task, description=f"[green]Converting {png_file.name}...")
            
            if png_to_svg(str(png_file), str(output_file), method, options, overwrite):
                success_count += 1
            
            progress.advance(task)
    
    console.print(f"[green]Conversion completed: {success_count} of {len(png_files)} files converted successfully")
    return success_count > 0

@app.command()
def convert(
    input_file: str = typer.Argument(..., help="Path to the input PNG file"),
    output_file: str = typer.Argument(..., help="Path to the output SVG file"),
    method: ConversionMethod = typer.Option(
        ConversionMethod.AUTOTRACE, 
        help="Conversion method to use"
    ),
    options: Optional[str] = typer.Option(
        None, 
        help="Custom options to pass to the converter (e.g., '--filter-iterations 4')"
    ),
    overwrite: bool = typer.Option(
        False, 
        help="Overwrite output file if it exists"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose logging"
    ),
) -> None:
    """Convert a single PNG file to SVG."""
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    if not png_to_svg(input_file, output_file, method.value, options, overwrite):
        sys.exit(1)

@app.command()
def batch(
    input_dir: str = typer.Argument(..., help="Directory containing PNG files"),
    output_dir: str = typer.Argument(..., help="Directory to save SVG files"),
    method: ConversionMethod = typer.Option(
        ConversionMethod.AUTOTRACE, 
        help="Conversion method to use"
    ),
    options: Optional[str] = typer.Option(
        None, 
        help="Custom options to pass to the converter (e.g., '--filter-iterations 4')"
    ),
    overwrite: bool = typer.Option(
        False, 
        help="Overwrite output files if they exist"
    ),
    recursive: bool = typer.Option(
        False, "--recursive", "-r",
        help="Recursively process subdirectories"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose logging"
    ),
) -> None:
    """Batch convert PNG files in a directory to SVG."""
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    if not batch_convert(input_dir, output_dir, method.value, options, overwrite, recursive):
        sys.exit(1)

def show_welcome() -> None:
    """Show a welcome message with information about the tool."""
    console.print(Panel.fit(
        "[bold blue]PNG to SVG Converter[/bold blue]\n\n"
        "A command line tool to convert PNG images to SVG format using various methods.\n\n"
        "[yellow]Methods available:[/yellow]\n"
        "- [green]autotrace[/green]: Uses the AutoTrace command-line tool (falls back to Pillow if not available)\n"
        "- [green]potrace[/green]: Uses Potrace with ImageMagick for preprocessing (falls back to Pillow if not available)\n"
        "- [green]pillow[/green]: Pure Python conversion using Pillow (always available)\n"
        "- [green]aspose[/green]: Uses the Aspose.Words Python library\n"
        "- [green]convertapi[/green]: Uses the ConvertAPI web service\n\n"
        "[yellow]Examples:[/yellow]\n"
        "[grey]# Convert a single file[/grey]\n"
        "uv run png2svg.py convert input.png output.svg\n\n"
        "[grey]# Batch convert all PNGs in a directory[/grey]\n"
        "uv run png2svg.py batch input_dir/ output_dir/",
        title="Welcome",
        border_style="blue",
    ))

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """PNG to SVG Converter main entry point."""
    if ctx.invoked_subcommand is None:
        show_welcome()
        sys.exit(0)

if __name__ == "__main__":
    # Add timestamp to startup log
    startup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.debug(f"PNG to SVG Converter started at {startup_time}")
    
    app()