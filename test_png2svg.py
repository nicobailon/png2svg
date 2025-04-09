import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module to test
import png2svg

@pytest.fixture
def temp_png_file(tmp_path):
    """Create a temporary PNG file for testing."""
    png_file = tmp_path / "test.png"
    png_file.write_bytes(b"PNG test data")  # Not real PNG data, just for test
    return str(png_file)

@pytest.fixture
def temp_output_file(tmp_path):
    """Create a path for a temporary output file."""
    return str(tmp_path / "output.svg")

def test_validate_file_exists():
    """Test file validation when file exists."""
    with pytest.raises(FileNotFoundError):
        png2svg.validate_file("nonexistent_file.png", check_exists=True)

def test_ensure_directory(tmp_path):
    """Test directory creation."""
    nested_dir = tmp_path / "a" / "b" / "c"
    test_file = nested_dir / "test.svg"
    png2svg.ensure_directory(str(test_file))
    assert nested_dir.exists()

@patch("subprocess.run")
def test_convert_autotrace_success(mock_run, temp_png_file, temp_output_file):
    """Test successful conversion with autotrace."""
    mock_run.return_value = MagicMock(returncode=0)
    
    assert png2svg.convert_autotrace(temp_png_file, temp_output_file)
    mock_run.assert_called_once()

@patch("subprocess.run")
def test_convert_autotrace_not_installed(mock_run, temp_png_file, temp_output_file):
    """Test conversion when autotrace is not installed."""
    mock_run.side_effect = FileNotFoundError()
    
    assert not png2svg.convert_autotrace(temp_png_file, temp_output_file)

@patch("subprocess.run")
def test_convert_autotrace_error(mock_run, temp_png_file, temp_output_file):
    """Test conversion with autotrace error."""
    mock_run.side_effect = subprocess.CalledProcessError(1, "autotrace")
    
    assert not png2svg.convert_autotrace(temp_png_file, temp_output_file)

@patch("png2svg.convert_autotrace")
def test_png_to_svg_success(mock_convert, temp_png_file, temp_output_file):
    """Test successful PNG to SVG conversion."""
    mock_convert.return_value = True
    
    assert png2svg.png_to_svg(temp_png_file, temp_output_file, method="autotrace")
    mock_convert.assert_called_once()

@patch("png2svg.convert_autotrace")
def test_png_to_svg_error(mock_convert, temp_png_file, temp_output_file):
    """Test PNG to SVG conversion with error."""
    mock_convert.return_value = False
    
    assert not png2svg.png_to_svg(temp_png_file, temp_output_file, method="autotrace")
    mock_convert.assert_called_once()

@patch("png2svg.png_to_svg")
def test_batch_convert(mock_png_to_svg, tmp_path):
    """Test batch conversion."""
    # Create test directory structure with PNG files
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    
    # Create some test PNG files
    (input_dir / "test1.png").write_bytes(b"PNG test data")
    (input_dir / "test2.png").write_bytes(b"PNG test data")
    
    mock_png_to_svg.return_value = True
    
    assert png2svg.batch_convert(str(input_dir), str(output_dir))
    assert mock_png_to_svg.call_count == 2

@patch("argparse.ArgumentParser.parse_args")
@patch("png2svg.png_to_svg")
def test_main_single_file(mock_png_to_svg, mock_parse_args, temp_png_file, temp_output_file):
    """Test main function with single file."""
    mock_args = MagicMock(
        batch=False, 
        input_file=temp_png_file, 
        output_file=temp_output_file,
        method="autotrace",
        options=None,
        overwrite=False,
        verbose=False
    )
    mock_parse_args.return_value = mock_args
    mock_png_to_svg.return_value = True
    
    assert png2svg.main() == 0
    mock_png_to_svg.assert_called_once()

if __name__ == "__main__":
    pytest.main()