"""
Components Module
=================

Centralized module for UI components and utilities.

This module provides:
- UI Loader: Central CSS management
- Component functions: Reusable UI elements
- Layout utilities: Page structure helpers

Usage:
    from components import load_css
    load_css()
"""

from .ui_loader import (
    load_css,
    load_css_inline,
    load_css_file,
    get_css_files_list,
    validate_css_files,
)

__all__ = [
    "load_css",
    "load_css_inline",
    "load_css_file",
    "get_css_files_list",
    "validate_css_files",
]

__version__ = "1.0.0"
__author__ = "Barbería Dev Team"
