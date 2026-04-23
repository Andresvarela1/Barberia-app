"""
Global Design System for Barberia App
Ensures consistent, modern, and premium UI across all screens
"""

import streamlit as st

# ==================== COLOR PALETTE ====================
class Colors:
    """Centralized color definitions for the entire app"""
    PRIMARY = "#7c3aed"  # Purple - main brand color
    PRIMARY_DARK = "#6d28d9"  # Darker purple for hover
    PRIMARY_LIGHT = "#a78bfa"  # Lighter purple for disabled
    
    SECONDARY = "#06b6d4"  # Cyan - accent color
    SECONDARY_DARK = "#0891b2"  # Darker cyan
    SECONDARY_LIGHT = "#22d3ee"  # Lighter cyan
    
    SUCCESS = "#22c55e"  # Green - success states
    SUCCESS_DARK = "#16a34a"  # Darker green
    
    WARNING = "#f59e0b"  # Amber - warnings
    WARNING_DARK = "#d97706"  # Darker amber
    
    DANGER = "#ef4444"  # Red - errors/delete
    DANGER_DARK = "#dc2626"  # Darker red
    
    # Background & Surface
    BACKGROUND = "#0f172a"  # Very dark blue (almost black)
    CARD = "#1e293b"  # Dark slate
    CARD_HOVER = "#334155"  # Lighter slate on hover
    BORDER = "#334155"  # Subtle borders
    
    # Text
    TEXT = "#f1f5f9"  # Main text - light slate
    TEXT_SECONDARY = "#cbd5e1"  # Secondary text - muted
    TEXT_TERTIARY = "#94a3b8"  # Tertiary text - lighter
    TEXT_DISABLED = "#64748b"  # Disabled text
    
    # Utility
    TRANSPARENT = "rgba(0, 0, 0, 0)"
    WHITE = "#ffffff"
    BLACK = "#000000"


# ==================== TYPOGRAPHY ====================
class Typography:
    """Typography system for consistent text styling"""
    
    # Font sizes
    H1 = "2.5rem"  # 40px - Page titles
    H2 = "2rem"    # 32px - Section titles
    H3 = "1.5rem"  # 24px - Subsection titles
    H4 = "1.25rem" # 20px - Card titles
    BODY = "1rem"  # 16px - Main text
    SMALL = "0.875rem"  # 14px - Small text
    TINY = "0.75rem"  # 12px - Captions
    
    # Font weights
    THIN = 100
    LIGHT = 300
    NORMAL = 400
    MEDIUM = 500
    SEMIBOLD = 600
    BOLD = 700


# ==================== SPACING ====================
class Spacing:
    """Consistent spacing values"""
    XS = "0.25rem"  # 4px
    SM = "0.5rem"   # 8px
    MD = "1rem"     # 16px
    LG = "1.5rem"   # 24px
    XL = "2rem"     # 32px
    XXL = "3rem"    # 48px


# ==================== BORDER RADIUS ====================
class BorderRadius:
    """Consistent border radius values"""
    NONE = "0px"
    SM = "6px"
    MD = "12px"
    LG = "16px"
    XL = "24px"
    FULL = "9999px"


# ==================== SHADOWS ====================
class Shadows:
    """Shadow definitions for depth"""
    NONE = "none"
    SM = "0 1px 2px 0 rgba(0, 0, 0, 0.25)"
    MD = "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)"
    LG = "0 10px 15px -3px rgba(0, 0, 0, 0.35), 0 4px 6px -2px rgba(0, 0, 0, 0.25)"
    XL = "0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3)"
    # Enhanced shadows for modern SaaS look
    GLOW_SOFT = "0 0 20px rgba(124, 58, 237, 0.15)"
    GLOW_STRONG = "0 0 30px rgba(124, 58, 237, 0.25)"
    INSET_SUBTLE = "inset 0 1px 2px rgba(255, 255, 255, 0.1)"
    ELEVATED = "0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 15px 20px -10px rgba(0, 0, 0, 0.3)"
    FLOATING = "0 30px 60px -12px rgba(0, 0, 0, 0.6), 0 8px 24px -4px rgba(0, 0, 0, 0.4)"


# ==================== GRADIENTS ====================
class Gradients:
    """Gradient definitions for modern SaaS aesthetic"""
    
    # Button gradients
    PRIMARY_BUTTON = f"linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)"
    PRIMARY_BUTTON_HOVER = f"linear-gradient(135deg, #6d28d9 0%, #5b21b6 100%)"
    SECONDARY_BUTTON = f"linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)"
    SUCCESS_BUTTON = f"linear-gradient(135deg, #22c55e 0%, #16a34a 100%)"
    DANGER_BUTTON = f"linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
    
    # Card gradients (subtle)
    CARD_SUBTLE = f"linear-gradient(135deg, #1e293b 0%, #1e293b 100%)"
    CARD_HOVER = f"linear-gradient(135deg, #1e293b 0%, rgba(124, 58, 237, 0.05) 100%)"
    CARD_SELECTED = f"linear-gradient(135deg, #1e293b 0%, rgba(124, 58, 237, 0.1) 100%)"
    
    # Premium card gradients
    PREMIUM = f"linear-gradient(135deg, #1e293b 0%, #0f172a 100%)"
    PREMIUM_ACCENT = f"linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%)"
    
    # CTA gradients (eye-catching)
    CTA_PRIMARY = f"linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%)"
    CTA_ACCENT = f"linear-gradient(135deg, #06b6d4 0%, #22c55e 100%)"
    
    # Background gradients
    HEADER = f"linear-gradient(135deg, #7c3aed 0%, #06b6d4 50%, #22c55e 100%)"
    HERO = f"linear-gradient(to bottom, rgba(124, 58, 237, 0.1) 0%, rgba(6, 182, 212, 0.05) 100%)"
    
    # Overlay gradients
    OVERLAY_SUBTLE = f"linear-gradient(135deg, rgba(124, 58, 237, 0.05) 0%, rgba(6, 182, 212, 0.05) 100%)"
    OVERLAY_MEDIUM = f"linear-gradient(135deg, rgba(124, 58, 237, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%)"


# ==================== TRANSITIONS ====================
class Transitions:
    """Smooth transition timing"""
    FAST = "0.15s ease-in-out"
    NORMAL = "0.3s ease-in-out"
    SLOW = "0.5s ease-in-out"
