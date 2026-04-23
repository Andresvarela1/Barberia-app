"""
UI Loader - Central CSS management system
==========================================

This module provides a centralized way to load and manage CSS stylesheets
from the styles/ directory. It ensures clean separation of concerns and
easy maintainability of visual styles.

Usage:
    from components.ui_loader import load_css
    
    # Load default styles
    load_css()
    
    # Load specific styles
    load_css(["base", "sidebar", "forms"])
    
    # Load from custom path
    load_css(["base"], base_path="custom_styles/")
"""

import streamlit as st
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def load_css(
    files: Optional[List[str]] = None,
    base_path: str = "styles"
) -> None:
    """
    Load CSS files from the styles directory and apply them to Streamlit app.
    
    Args:
        files: List of CSS file names (without .css extension) to load.
               If None, loads all default stylesheets in recommended order.
               Default: ["base", "sidebar", "calendar", "forms", "cards", "booking"]
        base_path: Base directory path where CSS files are located.
                  Default: "styles"
    
    Returns:
        None
        
    Raises:
        FileNotFoundError: If a specified CSS file is not found.
        UnicodeDecodeError: If CSS file has encoding issues.
        
    Examples:
        # Load all default CSS files
        load_css()
        
        # Load only specific CSS files
        load_css(["base", "sidebar"])
        
        # Load from custom directory
        load_css(["custom"], base_path="custom_styles")
    """
    
    # Default CSS files in load order (base styles first, specific styles last)
    if files is None:
        files = [
            "base",          # Global theme and typography
            "sidebar",       # Sidebar navigation
            "calendar",      # Calendar and date pickers
            "forms",         # Form elements and inputs
            "cards",         # Card components
            "booking",       # Booking flow specific styles
        ]
    
    # Resolve base path
    base_dir = Path(__file__).parent.parent / base_path
    
    # Track successfully loaded files
    loaded_count = 0
    failed_count = 0
    
    for filename in files:
        try:
            # Ensure .css extension
            if not filename.endswith(".css"):
                filename_full = f"{filename}.css"
            else:
                filename_full = filename
            
            # Build full file path
            css_file = base_dir / filename_full
            
            # Verify file exists
            if not css_file.exists():
                logger.warning(f"CSS file not found: {css_file}")
                failed_count += 1
                continue
            
            # Read CSS file with UTF-8 encoding
            try:
                with open(css_file, "r", encoding="utf-8") as f:
                    css_content = f.read()
            except UnicodeDecodeError as e:
                logger.error(f"Encoding error reading {css_file}: {e}")
                failed_count += 1
                continue
            
            # Apply CSS to Streamlit
            st.markdown(
                f"<style>{css_content}</style>",
                unsafe_allow_html=True
            )
            
            loaded_count += 1
            logger.debug(f"CSS loaded successfully: {filename_full}")
            
        except Exception as e:
            logger.error(f"Error loading CSS file {filename}: {e}")
            failed_count += 1
            continue
    
    # Log summary
    if loaded_count > 0:
        logger.info(f"CSS UI Loader: {loaded_count} stylesheet(s) loaded successfully")
    
    if failed_count > 0:
        logger.warning(f"CSS UI Loader: {failed_count} stylesheet(s) failed to load")


def load_css_inline(css_content: str) -> None:
    """
    Load CSS from a string directly.
    
    Args:
        css_content: CSS code as a string.
        
    Returns:
        None
        
    Example:
        css = '''
        .my-class {
            color: red;
        }
        '''
        load_css_inline(css)
    """
    try:
        st.markdown(
            f"<style>{css_content}</style>",
            unsafe_allow_html=True
        )
        logger.debug("Inline CSS loaded successfully")
    except Exception as e:
        logger.error(f"Error loading inline CSS: {e}")


def load_css_file(filepath: str) -> None:
    """
    Load CSS from an absolute file path.
    
    Args:
        filepath: Absolute path to CSS file.
        
    Returns:
        None
        
    Raises:
        FileNotFoundError: If file doesn't exist.
        UnicodeDecodeError: If file has encoding issues.
        
    Example:
        load_css_file("/path/to/custom.css")
    """
    css_path = Path(filepath)
    
    if not css_path.exists():
        raise FileNotFoundError(f"CSS file not found: {filepath}")
    
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        
        st.markdown(
            f"<style>{css_content}</style>",
            unsafe_allow_html=True
        )
        logger.debug(f"CSS loaded from file: {filepath}")
        
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading {filepath}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading CSS from {filepath}: {e}")
        raise


def get_css_files_list(base_path: str = "styles") -> List[str]:
    """
    Get list of available CSS files in the styles directory.
    
    Args:
        base_path: Base directory path.
        
    Returns:
        List of CSS file names (without .css extension).
        
    Example:
        available_css = get_css_files_list()
        print(available_css)  # ['base', 'sidebar', 'forms', ...]
    """
    base_dir = Path(__file__).parent.parent / base_path
    
    if not base_dir.exists():
        logger.warning(f"Styles directory not found: {base_dir}")
        return []
    
    css_files = sorted([
        f.stem for f in base_dir.glob("*.css")
    ])
    
    return css_files


def validate_css_files(files: List[str], base_path: str = "styles") -> dict:
    """
    Validate that specified CSS files exist.
    
    Args:
        files: List of CSS file names to validate.
        base_path: Base directory path.
        
    Returns:
        Dictionary with 'valid' and 'missing' keys.
        
    Example:
        result = validate_css_files(["base", "sidebar", "nonexistent"])
        print(result)
        # {'valid': ['base', 'sidebar'], 'missing': ['nonexistent']}
    """
    base_dir = Path(__file__).parent.parent / base_path
    valid = []
    missing = []
    
    for filename in files:
        css_file = base_dir / (
            f"{filename}.css" if not filename.endswith(".css") else filename
        )
        
        if css_file.exists():
            valid.append(filename)
        else:
            missing.append(filename)
    
    return {
        "valid": valid,
        "missing": missing,
        "total": len(files),
        "loaded": len(valid)
    }


if __name__ == "__main__":
    # Quick test of available CSS files
    print("Available CSS files:")
    files = get_css_files_list()
    for f in files:
        print(f"  - {f}")
