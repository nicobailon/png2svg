#!/usr/bin/env python3
"""
PNG to SVG Converter

A command line tool to convert PNG images to SVG format using various methods.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('png2svg')

def validate_file(file_path, check_exists=True, check_extension=None):
    """
    Validate file path.
    """
    path = Path(file_path)
    
    if check_exists and not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if check_extension and path.suffix.lower() != check_extension.lower():
        logger.warning(f"File {file_path} does not have the expected extension {check_extension}")
    
    return path

def ensure_directory(file_path):
    """
    Ensure the directory for the output file exists.
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def convert_autotrace(input_file, output_file, options=None):
    """
    Convert PNG to SVG using autotrace.
    """
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
    except FileNotFoundError:
        logger.error("Error: autotrace is not installed. Please install it first.")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during conversion with autotrace: {e}")
        if e.stderr:
            logger.error(f"Error details: {e.stderr}")
        return False

def convert_potrace(input_file, output_file, options=None):
    """
    Convert PNG to SVG using potrace.
    """
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
    except FileNotFoundError as e:
        logger.error(f"Required tool not found: {e.filename}")
        logger.error("Please install ImageMagick and potrace.")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during conversion with potrace: {e}")
        if e.stderr:
            logger.error(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def convert_with_library(input_file, output_file, method='aspose'):
    """
    Convert PNG to SVG using a Python library.
    """
    if method == 'aspose':
        try:
            import aspose.words as aw
            doc = aw.Document()
            builder = aw.DocumentBuilder(doc)
            shape = builder.insert_image(input_file)
            shape.get_shape_renderer().save(output_file, aw.saving.ImageSaveOptions(aw.SaveFormat.SVG))
            return True
        except ImportError:
            logger.error("Aspose.Words library not found. Install with: pip install aspose-words")
            return False
        except Exception as e:
            logger.error(f"Error during conversion with Aspose: {e}")
            return False
    elif method == 'convertapi':
        try:
            import convertapi
            api_key = os.environ.get('CONVERTAPI_KEY')
            if not api_key:
                logger.error("ConvertAPI key not found. Set the CONVERTAPI_KEY environment variable.")
                return False
            
            convertapi.api_secret = api_key
            result = convertapi.convert('svg', {'File': input_file})
            result.save_files(output_file)
            return True
        except ImportError:
            logger.error("ConvertAPI library not found. Install with: pip install convertapi")
            return False
        except Exception as e:
            logger.error(f"Error during conversion with ConvertAPI: {e}")
            return False
    else:
        logger.error(f"Unknown conversion method: {method}")
        return False

def png_to_svg(input_file, output_file, method='autotrace', options=None, overwrite=False):
    """
    Convert a PNG file to SVG using the specified method.
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
        success = False
        
        if method == 'autotrace':
            success = convert_autotrace(str(input_path), output_file, options)
        elif method == 'potrace':
            success = convert_potrace(str(input_path), output_file, options)
        elif method in ['aspose', 'convertapi']:
            success = convert_with_library(str(input_path), output_file, method)
        else:
            logger.error(f"Unknown conversion method: {method}")
            return False
        
        if success:
            logger.info(f"Conversion successful! SVG saved at: {output_file}")
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        return False

def batch_convert(input_dir, output_dir, method='autotrace', options=None, overwrite=False, recursive=False):
    """
    Batch convert PNG files in a directory to SVG.
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
    
    for png_file in png_files:
        # Determine the output file path
        rel_path = png_file.relative_to(input_path) if recursive else png_file.name
        output_file = Path(output_dir) / rel_path.with_suffix('.svg')
        
        # Ensure output directory exists
        ensure_directory(str(output_file))
        
        logger.info(f"Converting {png_file} to {output_file}")
        
        if png_to_svg(str(png_file), str(output_file), method, options, overwrite):
            success_count += 1
    
    logger.info(f"Conversion completed: {success_count} of {len(png_files)} files converted successfully")
    return success_count > 0

def main():
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(
        description="Convert PNG images to SVG format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single file
  png2svg input.png output.svg
  
  # Use a specific conversion method
  png2svg input.png output.svg --method potrace
  
  # Batch convert all PNGs in a directory
  png2svg --batch input_dir/ output_dir/
  
  # Batch convert with recursive search
  png2svg --batch input_dir/ output_dir/ --recursive
  
  # Pass custom options to the converter
  png2svg input.png output.svg --options "--filter-iterations 4 --dpi 300"
        """
    )
    
    # Mode selection (single file or batch)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    
    mode_group.add_argument("--batch", action="store_true", 
                         help="Batch convert PNG files in a directory")
    
    mode_group.add_argument("input_file", nargs="?", 
                         help="Path to the input PNG file")
    
    parser.add_argument("output_file", nargs="?",
                     help="Path to the output SVG file")
    
    # Options for both modes
    parser.add_argument("--method", choices=["autotrace", "potrace", "aspose", "convertapi"],
                     default="autotrace", help="Conversion method to use (default: autotrace)")
    
    parser.add_argument("--options", 
                     help="Custom options to pass to the converter (e.g., '--filter-iterations 4')")
    
    parser.add_argument("--overwrite", action="store_true",
                     help="Overwrite output file if it exists")
    
    parser.add_argument("--verbose", "-v", action="store_true",
                     help="Enable verbose logging")
    
    # Options for batch mode
    parser.add_argument("--recursive", "-r", action="store_true",
                     help="Recursively process directories (batch mode only)")
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Process based on mode
    if args.batch:
        if not args.input_file or not args.output_file:
            parser.error("--batch mode requires both input_dir and output_dir")
        
        return 0 if batch_convert(
            args.input_file, 
            args.output_file, 
            args.method, 
            args.options, 
            args.overwrite, 
            args.recursive
        ) else 1
    else:
        if not args.input_file or not args.output_file:
            parser.error("Single file mode requires both input_file and output_file")
        
        return 0 if png_to_svg(
            args.input_file, 
            args.output_file, 
            args.method, 
            args.options, 
            args.overwrite
        ) else 1

if __name__ == "__main__":
    sys.exit(main())