"""
Global Design System for Barberia App
Ensures consistent, modern, and premium UI across all screens
"""

import streamlit as st

# ==================== COLOR PALETTE ====================
class Colors:
    """Centralized color definitions for the entire app"""
    PRIMARY = "#2563eb"  # Blue - main SaaS brand color
    PRIMARY_DARK = "#1d4ed8"  # Darker blue for hover
    PRIMARY_LIGHT = "#93c5fd"  # Lighter blue for disabled
    
    SECONDARY = "#0f766e"  # Teal - secondary accent
    SECONDARY_DARK = "#115e59"  # Darker teal
    SECONDARY_LIGHT = "#5eead4"  # Lighter teal
    
    SUCCESS = "#22c55e"  # Green - success states
    SUCCESS_DARK = "#16a34a"  # Darker green
    
    WARNING = "#f59e0b"  # Amber - warnings
    WARNING_DARK = "#d97706"  # Darker amber
    
    DANGER = "#ef4444"  # Red - errors/delete
    DANGER_DARK = "#dc2626"  # Darker red
    
    # Background & Surface
    BACKGROUND = "#f6f7fb"  # App canvas
    CARD = "#ffffff"  # Primary surface
    CARD_HOVER = "#f8fafc"  # Subtle hover surface
    BORDER = "#d8dee8"  # Subtle borders
    
    # Text
    TEXT = "#111827"  # Main text
    TEXT_SECONDARY = "#4b5563"  # Secondary text
    TEXT_TERTIARY = "#6b7280"  # Tertiary text
    TEXT_DISABLED = "#9ca3af"  # Disabled text
    
    # Utility
    TRANSPARENT = "rgba(0, 0, 0, 0)"
    WHITE = "#ffffff"
    BLACK = "#000000"


# ==================== TYPOGRAPHY ====================
class Typography:
    """Typography system for consistent text styling"""
    
    # Font sizes
    H1 = "2.25rem"  # 36px - Page titles
    H2 = "1.5rem"   # 24px - Section titles
    H3 = "1.25rem"  # 20px - Subsection titles
    H4 = "1.125rem" # 18px - Card titles
    BODY = "0.95rem"  # 15px - Main text
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
    LG = "1.25rem"  # 20px
    XL = "1.75rem"  # 28px
    XXL = "2.25rem" # 36px


# ==================== BORDER RADIUS ====================
class BorderRadius:
    """Consistent border radius values"""
    NONE = "0px"
    SM = "8px"
    MD = "10px"
    LG = "12px"
    XL = "16px"
    FULL = "9999px"


# ==================== SHADOWS ====================
class Shadows:
    """Shadow definitions for depth"""
    NONE = "none"
    SM = "0 1px 2px 0 rgba(15, 23, 42, 0.06)"
    MD = "0 8px 18px -12px rgba(15, 23, 42, 0.22), 0 2px 6px rgba(15, 23, 42, 0.06)"
    LG = "0 16px 32px -20px rgba(15, 23, 42, 0.28), 0 6px 14px rgba(15, 23, 42, 0.08)"
    XL = "0 24px 48px -28px rgba(15, 23, 42, 0.32), 0 10px 24px rgba(15, 23, 42, 0.10)"
    # Enhanced shadows for modern SaaS look
    GLOW_SOFT = "0 0 0 4px rgba(37, 99, 235, 0.10)"
    GLOW_STRONG = "0 0 0 4px rgba(37, 99, 235, 0.16)"
    INSET_SUBTLE = "inset 0 1px 0 rgba(255, 255, 255, 0.7)"
    ELEVATED = "0 24px 48px -24px rgba(15, 23, 42, 0.28)"
    FLOATING = "0 28px 60px -30px rgba(15, 23, 42, 0.32)"


# ==================== GRADIENTS ====================
class Gradients:
    """Gradient definitions for modern SaaS aesthetic"""
    
    # Button gradients
    PRIMARY_BUTTON = f"linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)"
    PRIMARY_BUTTON_HOVER = f"linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)"
    SECONDARY_BUTTON = f"linear-gradient(135deg, #0f766e 0%, #115e59 100%)"
    SUCCESS_BUTTON = f"linear-gradient(135deg, #22c55e 0%, #16a34a 100%)"
    DANGER_BUTTON = f"linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
    
    # Card gradients (subtle)
    CARD_SUBTLE = f"linear-gradient(135deg, #ffffff 0%, #ffffff 100%)"
    CARD_HOVER = f"linear-gradient(135deg, #ffffff 0%, rgba(37, 99, 235, 0.04) 100%)"
    CARD_SELECTED = f"linear-gradient(135deg, #ffffff 0%, rgba(37, 99, 235, 0.08) 100%)"
    
    # Premium card gradients
    PREMIUM = f"linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)"
    PREMIUM_ACCENT = f"linear-gradient(135deg, rgba(37, 99, 235, 0.08) 0%, rgba(15, 118, 110, 0.08) 100%)"
    
    # CTA gradients (eye-catching)
    CTA_PRIMARY = f"linear-gradient(135deg, #2563eb 0%, #0f766e 100%)"
    CTA_ACCENT = f"linear-gradient(135deg, #0f766e 0%, #22c55e 100%)"
    
    # Background gradients
    HEADER = f"linear-gradient(135deg, #2563eb 0%, #0f766e 100%)"
    HERO = f"linear-gradient(to bottom, rgba(37, 99, 235, 0.08) 0%, rgba(15, 118, 110, 0.04) 100%)"
    
    # Overlay gradients
    OVERLAY_SUBTLE = f"linear-gradient(135deg, rgba(37, 99, 235, 0.04) 0%, rgba(15, 118, 110, 0.04) 100%)"
    OVERLAY_MEDIUM = f"linear-gradient(135deg, rgba(37, 99, 235, 0.08) 0%, rgba(15, 118, 110, 0.08) 100%)"


# ==================== TRANSITIONS ====================
class Transitions:
    """Smooth transition timing"""
    FAST = "0.15s ease-in-out"
    NORMAL = "0.3s ease-in-out"
    SLOW = "0.5s ease-in-out"


# ==================== GLOBAL CSS ====================
def apply_global_theme():
    """Apply global CSS theme to the Streamlit app"""
    css = f"""
    <style>
        /* ==================== ROOT STYLES ==================== */
        :root {{
            --primary: {Colors.PRIMARY};
            --primary-dark: {Colors.PRIMARY_DARK};
            --primary-light: {Colors.PRIMARY_LIGHT};
            --secondary: {Colors.SECONDARY};
            --secondary-dark: {Colors.SECONDARY_DARK};
            --success: {Colors.SUCCESS};
            --success-dark: {Colors.SUCCESS_DARK};
            --warning: {Colors.WARNING};
            --warning-dark: {Colors.WARNING_DARK};
            --danger: {Colors.DANGER};
            --danger-dark: {Colors.DANGER_DARK};
            --background: {Colors.BACKGROUND};
            --surface: {Colors.CARD};
            --card: {Colors.CARD};
            --surface-muted: {Colors.CARD_HOVER};
            --border: {Colors.BORDER};
            --text: {Colors.TEXT};
            --text-secondary: {Colors.TEXT_SECONDARY};
            --text-tertiary: {Colors.TEXT_TERTIARY};
            --text-disabled: {Colors.TEXT_DISABLED};
            --radius-sm: {BorderRadius.SM};
            --radius-md: {BorderRadius.MD};
            --radius-lg: {BorderRadius.LG};
            --radius-xl: {BorderRadius.XL};
            --shadow-sm: {Shadows.SM};
            --shadow-md: {Shadows.MD};
            --shadow-lg: {Shadows.LG};
            --space-1: {Spacing.XS};
            --space-2: {Spacing.SM};
            --space-4: {Spacing.MD};
            --space-5: {Spacing.LG};
            --space-6: {Spacing.XL};
            --space-7: {Spacing.XXL};
        }}

        /* ==================== BODY & MAIN STYLES ==================== */
        body {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            font-size: {Typography.BODY};
            line-height: 1.55;
        }}

        .stApp {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT};
        }}

        /* ==================== SIDEBAR STYLING ==================== */
        [data-testid="stSidebar"] {{
            background-color: {Colors.CARD};
            border-right: 1px solid {Colors.BORDER};
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: {Colors.TEXT};
        }}

        /* ==================== MAIN CONTENT AREA ==================== */
        .main {{
            background-color: {Colors.BACKGROUND};
            padding: {Spacing.LG};
            max-width: 1360px;
            margin: 0 auto;
        }}

        /* ==================== TEXT STYLING ==================== */
        h1, h2, h3, h4, h5, h6 {{
            color: {Colors.TEXT};
            font-weight: {Typography.SEMIBOLD};
            line-height: 1.2;
            letter-spacing: -0.01em;
        }}

        h1 {{
            font-size: {Typography.H1};
            margin: {Spacing.MD} 0 {Spacing.LG} 0;
        }}

        h2 {{
            font-size: {Typography.H2};
            margin: {Spacing.MD} 0 {Spacing.MD} 0;
        }}

        h3 {{
            font-size: {Typography.H3};
            margin: {Spacing.MD} 0 {Spacing.SM} 0;
        }}

        h4 {{
            font-size: {Typography.H4};
            margin: {Spacing.SM} 0;
        }}

        p {{
            color: {Colors.TEXT_SECONDARY};
            font-size: {Typography.BODY};
            line-height: 1.6;
            margin: {Spacing.SM} 0;
        }}

        .caption {{
            color: {Colors.TEXT_TERTIARY};
            font-size: {Typography.TINY};
        }}

        [data-testid="stWidgetLabel"],
        label,
        .stTextInput label,
        .stSelectbox label,
        .stDateInput label,
        .stTimeInput label,
        .stNumberInput label,
        .stTextArea label {{
            color: {Colors.TEXT};
            font-size: {Typography.SMALL};
            font-weight: {Typography.MEDIUM};
            line-height: 1.4;
            letter-spacing: 0;
        }}

        /* ==================== CONTAINER STYLING ==================== */
        [data-testid="stVerticalBlock"] > [style*="flex-direction"] > [data-testid="stVerticalBlock"] {{
            background: {Gradients.CARD_SUBTLE};
            border: 1px solid {Colors.BORDER};
            border-radius: {BorderRadius.MD};
            padding: {Spacing.LG};
            box-shadow: {Shadows.MD}, {Shadows.INSET_SUBTLE};
            transition: all {Transitions.NORMAL};
        }}

        div[data-testid="stVerticalBlock"] {{
            gap: {Spacing.MD};
        }}

        div[data-testid="stHorizontalBlock"] {{
            gap: {Spacing.MD};
        }}

        div[data-testid="column"] {{
            padding: 0 calc({Spacing.SM} + 2px);
        }}

        div[data-testid="column"]:first-child {{
            padding-left: 0;
        }}

        div[data-testid="column"]:last-child {{
            padding-right: 0;
        }}

        [data-testid="stVerticalBlock"] > [style*="flex-direction"] > [data-testid="stVerticalBlock"]:hover {{
            background: {Gradients.CARD_HOVER};
            box-shadow: {Shadows.LG}, {Shadows.INSET_SUBTLE}, {Shadows.GLOW_SOFT};
            border-color: {Colors.PRIMARY};
        }}

        /* ==================== BUTTON STYLING ==================== */
        button {{
            border-radius: {BorderRadius.MD};
            border: none;
            font-weight: {Typography.SEMIBOLD};
            transition: all {Transitions.NORMAL};
            font-size: {Typography.BODY};
            line-height: 1.35;
            letter-spacing: 0;
            text-transform: none;
            padding: 0.8rem 1.1rem;
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }}

        /* Primary Button - Strong CTA */
        .stButton > button {{
            background: {Gradients.PRIMARY_BUTTON};
            color: {Colors.WHITE};
            box-shadow: {Shadows.SM};
            border: 1px solid {Colors.PRIMARY};
            font-weight: {Typography.BOLD};
            position: relative;
            overflow: hidden;
            border-radius: {BorderRadius.MD};
        }}

        .stButton > button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: {Gradients.PRIMARY_BUTTON_HOVER};
            transition: left {Transitions.NORMAL};
            z-index: -1;
        }}

        .stButton > button::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.5);
            transform: translate(-50%, -50%);
            transition: width {Transitions.NORMAL}, height {Transitions.NORMAL};
            pointer-events: none;
        }}

        .stButton > button:hover {{
            transform: translateY(-3px);
            box-shadow: {Shadows.MD};
        }}

        .stButton > button:active {{
            transform: translateY(-1px) scale(0.98);
            box-shadow: {Shadows.SM};
        }}

        .stButton > button:active::after {{
            width: 300px;
            height: 300px;
        }}

        /* Secondary Button */
        .stButton > button[kind="secondary"] {{
            background: {Colors.CARD};
            color: {Colors.PRIMARY};
            border: 1px solid {Colors.PRIMARY};
            box-shadow: {Shadows.SM};
            font-weight: {Typography.SEMIBOLD};
        }}

        .stButton > button[kind="secondary"]:hover {{
            background: {Gradients.PRIMARY_BUTTON};
            color: {Colors.WHITE};
            box-shadow: {Shadows.MD}, {Shadows.GLOW_SOFT};
            transform: translateY(-2px);
        }}

        .stButton > button[kind="secondary"]:active {{
            transform: translateY(0) scale(0.97);
        }}

        /* Danger Button */
        .stButton > button[kind="secondary"]:has-text-danger {{
            color: {Colors.DANGER};
            border-color: {Colors.DANGER};
        }}

        .stButton > button[kind="secondary"]:has-text-danger:hover {{
            background: {Gradients.DANGER_BUTTON};
            color: {Colors.WHITE};
            border-color: {Colors.DANGER_DARK};
            box-shadow: {Shadows.MD}, 0 0 20px rgba(239, 68, 68, 0.3);
        }}

        /* ==================== INPUT STYLING ==================== */
        input, textarea, [role="textbox"] {{
            background-color: {Colors.CARD} !important;
            color: {Colors.TEXT} !important;
            border: 1px solid {Colors.BORDER} !important;
            border-radius: {BorderRadius.MD} !important;
            padding: 0.75rem {Spacing.MD} !important;
            transition: all {Transitions.FAST} !important;
            font-size: {Typography.BODY} !important;
            font-family: inherit !important;
        }}

        input:hover, textarea:hover {{
            border-color: {rgb_to_rgba(Colors.PRIMARY, 0.5)} !important;
            background-color: {rgb_to_rgba(Colors.PRIMARY, 0.05)} !important;
        }}

        input:focus, textarea:focus, [role="textbox"]:focus {{
            border-color: {Colors.PRIMARY} !important;
            box-shadow: 0 0 0 4px {rgb_to_rgba(Colors.PRIMARY, 0.2)}, inset 0 0 0 1px {rgb_to_rgba(Colors.PRIMARY, 0.1)} !important;
            background-color: {Colors.CARD} !important;
            outline: none !important;
        }}

        /* ==================== SELECT/DROPDOWN STYLING ==================== */
        [data-testid="stSelectbox"] > div > div {{
            background-color: {Colors.CARD} !important;
            border: 1px solid {Colors.BORDER} !important;
            border-radius: {BorderRadius.MD} !important;
            transition: all {Transitions.FAST} !important;
        }}

        [data-testid="stSelectbox"] > div > div:hover {{
            border-color: {rgb_to_rgba(Colors.PRIMARY, 0.5)} !important;
            background-color: {rgb_to_rgba(Colors.PRIMARY, 0.05)} !important;
        }}

        [data-testid="stSelectbox"] > div > div:focus-within {{
            border-color: {Colors.PRIMARY} !important;
            box-shadow: 0 0 0 4px {rgb_to_rgba(Colors.PRIMARY, 0.2)} !important;
        }}

        .stSelectbox [role="combobox"] {{
            color: {Colors.TEXT} !important;
            font-weight: {Typography.MEDIUM} !important;
        }}

        /* ==================== CHECKBOX & RADIO STYLING ==================== */
        [role="checkbox"], [role="radio"] {{
            accent-color: {Colors.PRIMARY} !important;
            cursor: pointer !important;
        }}

        [role="checkbox"]:hover, [role="radio"]:hover {{
            filter: brightness(1.2) !important;
        }}

        [role="checkbox"]:focus, [role="radio"]:focus {{
            box-shadow: 0 0 0 3px {rgb_to_rgba(Colors.PRIMARY, 0.3)} !important;
            outline: 2px solid {Colors.PRIMARY} !important;
        }}

        /* ==================== SLIDER STYLING ==================== */
        .stSlider [role="slider"] {{
            background-color: {Colors.PRIMARY} !important;
        }}

        .stSlider > div > div > div {{
            background-color: {Colors.BORDER} !important;
        }}

        /* ==================== METRIC STYLING ==================== */
        [data-testid="metric-container"] {{
            background: {Gradients.CARD_SUBTLE};
            border: 1px solid {Colors.BORDER};
            border-radius: {BorderRadius.MD};
            padding: {Spacing.MD};
            box-shadow: {Shadows.SM};
            transition: all {Transitions.NORMAL};
            position: relative;
            overflow: hidden;
        }}

        [data-testid="metric-container"]::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 150%;
            height: 150%;
            background: radial-gradient(circle, rgba(124, 58, 237, 0.1) 0%, transparent 70%);
            z-index: 0;
        }}

        [data-testid="metric-container"]:hover {{
            box-shadow: {Shadows.LG}, {Shadows.INSET_SUBTLE}, {Shadows.GLOW_SOFT};
            background: {Gradients.CARD_HOVER};
            border-color: {Colors.PRIMARY};
            transform: translateY(-2px);
        }}

        [data-testid="metric-container"] [data-testid="stMetricValue"] {{
            color: {Colors.PRIMARY};
            font-weight: {Typography.BOLD};
            font-size: {Typography.H2};
        }}

        [data-testid="metric-container"] [data-testid="stMetricLabel"] {{
            color: {Colors.TEXT_SECONDARY};
            font-weight: {Typography.MEDIUM};
            font-size: {Typography.SMALL};
            letter-spacing: 0;
            text-transform: none;
        }}

        /* ==================== TABS STYLING ==================== */
        [role="tablist"] {{
            border-bottom: 1px solid {Colors.BORDER};
        }}

        [role="tab"] {{
            color: {Colors.TEXT_SECONDARY};
            border-bottom: 2px solid transparent;
            transition: all {Transitions.NORMAL};
            padding: {Spacing.MD} {Spacing.LG};
        }}

        [role="tab"]:hover {{
            color: {Colors.TEXT};
            border-bottom-color: {Colors.PRIMARY};
        }}

        [role="tab"][aria-selected="true"] {{
            color: {Colors.PRIMARY};
            border-bottom-color: {Colors.PRIMARY};
        }}

        /* ==================== ALERT/MESSAGE STYLING ==================== */
        .stAlert {{
            border-radius: {BorderRadius.MD};
            padding: {Spacing.MD};
            border-left: 4px solid;
            border: 1px solid transparent;
            box-shadow: {Shadows.SM};
        }}

        .stSuccess {{
            background-color: rgba(34, 197, 94, 0.1);
            border-left-color: {Colors.SUCCESS};
            color: {Colors.SUCCESS};
        }}

        .stError {{
            background-color: rgba(239, 68, 68, 0.1);
            border-left-color: {Colors.DANGER};
            color: {Colors.DANGER};
        }}

        .stWarning {{
            background-color: rgba(245, 158, 11, 0.1);
            border-left-color: {Colors.WARNING};
            color: {Colors.WARNING};
        }}

        .stInfo {{
            background-color: rgba(6, 182, 212, 0.1);
            border-left-color: {Colors.SECONDARY};
            color: {Colors.SECONDARY};
        }}

        /* ==================== DATAFRAME STYLING ==================== */
        [data-testid="stDataFrame"] {{
            background-color: {Colors.CARD} !important;
            border-radius: {BorderRadius.LG} !important;
            border: 1px solid {Colors.BORDER} !important;
            overflow: hidden;
        }}

        [data-testid="stDataFrame"] thead {{
            background-color: {Colors.CARD_HOVER};
            border-bottom: 1px solid {Colors.BORDER};
        }}

        [data-testid="stDataFrame"] th {{
            color: {Colors.TEXT};
            font-weight: {Typography.SEMIBOLD};
            padding: {Spacing.MD};
        }}

        [data-testid="stDataFrame"] td {{
            color: {Colors.TEXT};
            padding: {Spacing.SM} {Spacing.MD};
            border-color: {Colors.BORDER};
        }}

        [data-testid="stDataFrame"] tbody tr:hover {{
            background-color: {Colors.CARD_HOVER};
        }}

        /* ==================== EXPANDER STYLING ==================== */
        [data-testid="stExpander"] {{
            background-color: {Colors.CARD};
            border: 1px solid {Colors.BORDER};
            border-radius: {BorderRadius.MD};
            box-shadow: {Shadows.SM};
        }}

        [data-testid="stExpander"]:hover {{
            border-color: {Colors.PRIMARY};
        }}

        [data-testid="stExpanderDetails"] {{
            background-color: {Colors.CARD};
            border-top: 1px solid {Colors.BORDER};
        }}

        /* ==================== SPINNER STYLING ==================== */
        .stSpinner > div {{
            color: {Colors.PRIMARY} !important;
        }}

        /* ==================== DIVIDER STYLING ==================== */
        .stDivider {{
            background-color: {Colors.BORDER};
        }}

        /* ==================== CUSTOM CONTAINERS ==================== */
        .card-container {{
            background: {Gradients.CARD_SUBTLE};
            border: 1px solid {Colors.BORDER};
            border-radius: {BorderRadius.MD};
            padding: {Spacing.MD};
            box-shadow: {Shadows.SM};
            margin-bottom: {Spacing.MD};
            transition: all {Transitions.NORMAL};
            cursor: pointer;
            position: relative;
        }}

        .card-container:hover {{
            box-shadow: {Shadows.MD};
            border-color: {Colors.PRIMARY};
            background: {Gradients.CARD_HOVER};
            transform: translateY(-2px);
        }}

        .card-container:active {{
            transform: translateY(-2px);
            box-shadow: {Shadows.MD}, {Shadows.INSET_SUBTLE};
        }}

        .premium-card {{
            background: {Gradients.PREMIUM};
            border: 1px solid transparent;
            background-clip: padding-box;
            border-image: linear-gradient(135deg, {Colors.PRIMARY} 0%, {Colors.SECONDARY} 100%) 1;
            border-radius: {BorderRadius.LG};
            padding: {Spacing.MD};
            box-shadow: {Shadows.MD};
            position: relative;
            overflow: hidden;
            cursor: pointer;
            transition: all {Transitions.NORMAL};
        }}

        .premium-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: {Gradients.PREMIUM_ACCENT};
            opacity: 0;
            transition: opacity {Transitions.NORMAL};
            z-index: 0;
        }}

        .premium-card:hover {{
            box-shadow: {Shadows.LG};
            transform: translateY(-2px);
        }}

        .premium-card:hover::before {{
            opacity: 1;
        }}

        .premium-card > * {{
            position: relative;
            z-index: 1;
        }}

        /* Clickable Card State */
        .card-container[data-clickable="true"]:active {{
            box-shadow: {Shadows.MD}, {Shadows.INSET_SUBTLE};
        }}

        .premium-card[data-clickable="true"]:active {{
            transform: translateY(-2px);
        }}

        .section-title {{
            font-size: {Typography.H2};
            font-weight: {Typography.BOLD};
            color: {Colors.TEXT};
            margin-bottom: {Spacing.LG};
            padding-bottom: {Spacing.MD};
            border-bottom: 3px solid transparent;
            background: linear-gradient({Colors.TEXT}, {Colors.TEXT}) left bottom no-repeat;
            background-size: 60px 3px;
            position: relative;
        }}

        .section-title::after {{
            content: '';
            position: absolute;
            bottom: -3px;
            left: 60px;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, {Colors.PRIMARY} 0%, transparent 100%);
        }}

        .subsection-title {{
            font-size: {Typography.H3};
            font-weight: {Typography.SEMIBOLD};
            color: {Colors.TEXT};
            margin-top: {Spacing.LG};
            margin-bottom: {Spacing.MD};
            padding-left: {Spacing.MD};
            border-left: 4px solid {Colors.PRIMARY};
            position: relative;
        }}

        .badge {{
            display: inline-block;
            background: {Gradients.PRIMARY_BUTTON};
            color: {Colors.WHITE};
            padding: {Spacing.SM} {Spacing.MD};
            border-radius: {BorderRadius.FULL};
            font-size: {Typography.SMALL};
            font-weight: {Typography.SEMIBOLD};
            box-shadow: {Shadows.SM};
            text-transform: none;
            letter-spacing: 0;
        }}

        .badge-success {{
            background: {Gradients.SUCCESS_BUTTON};
        }}

        .badge-warning {{
            background: linear-gradient(135deg, {Colors.WARNING} 0%, {Colors.WARNING_DARK} 100%);
        }}

        .badge-danger {{
            background: {Gradients.DANGER_BUTTON};
        }}
        }}

        /* ==================== ANIMATIONS ==================== */
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}

        .fade-in {{
            animation: fadeIn {Transitions.NORMAL};
        }}

        .slide-in {{
            animation: slideIn {Transitions.NORMAL};
        }}

        /* ==================== TIME CHIP STYLING ==================== */
        .time-chips-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
            gap: {Spacing.SM};
            margin: {Spacing.LG} 0;
        }}

        .time-chip {{
            background-color: {Colors.CARD};
            border: 2px solid {Colors.BORDER};
            border-radius: {BorderRadius.LG};
            padding: {Spacing.SM} {Spacing.MD};
            font-size: {Typography.SMALL};
            font-weight: {Typography.SEMIBOLD};
            color: {Colors.TEXT};
            text-align: center;
            cursor: pointer;
            transition: all {Transitions.NORMAL};
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 44px;
            position: relative;
            overflow: hidden;
        }}

        .time-chip:hover {{
            transform: scale(1.05);
            border-color: {Colors.PRIMARY};
            background-color: {rgb_to_rgba(Colors.PRIMARY, 0.08)};
            box-shadow: {Shadows.MD}, {Shadows.GLOW_SOFT};
        }}

        .time-chip:active {{
            transform: scale(0.97);
            box-shadow: {Shadows.SM}, inset 0 0 8px rgba(124, 58, 237, 0.1);
        }}

        .time-chip.selected {{
            background: {Gradients.PRIMARY_BUTTON};
            border-color: {Colors.PRIMARY};
            color: {Colors.WHITE};
            font-weight: {Typography.BOLD};
            box-shadow: {Shadows.MD}, {Shadows.GLOW_STRONG};
            transform: scale(1.08);
        }}

        .time-chip.selected:hover {{
            transform: scale(1.12);
            box-shadow: {Shadows.LG}, {Shadows.GLOW_STRONG};
        }}

        .time-chip.disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            pointer-events: none;
        }}

        .time-chip::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width {Transitions.NORMAL}, height {Transitions.NORMAL};
            pointer-events: none;
        }}

        .time-chip:active::before {{
            width: 150px;
            height: 150px;
        }}

        /* ==================== SCROLLBAR STYLING ==================== */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: {Colors.CARD};
        }}

        ::-webkit-scrollbar-thumb {{
            background: {Colors.BORDER};
            border-radius: {BorderRadius.FULL};
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: {Colors.PRIMARY};
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def apply_public_booking_css():
    """Apply public landing and booking styling without changing booking logic."""
    st.markdown(f"""
    <style>
    .stApp {{
        background: #f7f3ee !important;
    }}

    .block-container,
    [data-testid="stMainBlockContainer"] {{
        max-width: 1120px !important;
        margin: 0 auto;
        padding: 1.25rem 1.5rem 2rem !important;
    }}

    [data-testid="stVerticalBlock"] {{
        gap: 1rem;
    }}

    .public-topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: {Spacing.MD};
        margin: {Spacing.SM} 0 {Spacing.LG};
    }}

    .public-logo {{
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: grid;
        place-items: center;
        background: #111827;
        color: #f8d47a;
        font-size: 1.35rem;
        font-weight: {Typography.BOLD};
        box-shadow: {Shadows.MD};
    }}

    .public-brand-name {{
        color: #111827;
        font-size: 1rem;
        font-weight: {Typography.BOLD};
        margin: 0;
    }}

    .public-brand-meta {{
        color: #6b7280;
        font-size: {Typography.SMALL};
        margin: 0;
    }}

    .public-hero {{
        min-height: 480px;
        border-radius: 28px;
        padding: clamp(28px, 6vw, 72px);
        color: #ffffff;
        overflow: hidden;
        position: relative;
        display: flex;
        align-items: flex-end;
        background:
            radial-gradient(circle at 82% 18%, rgba(197, 159, 85, 0.34), transparent 34%),
            linear-gradient(135deg, #111827 0%, #2f241d 54%, #16110d 100%);
        box-shadow: 0 28px 70px -38px rgba(17, 24, 39, 0.7);
    }}

    .public-logo img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: inherit;
    }}

    .public-hero-content {{
        max-width: 690px;
        position: relative;
        z-index: 1;
    }}

    .public-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.14);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: {BorderRadius.FULL};
        padding: 8px 12px;
        font-size: {Typography.SMALL};
        font-weight: {Typography.SEMIBOLD};
        margin-bottom: {Spacing.MD};
        backdrop-filter: blur(8px);
    }}

    .public-hero h1 {{
        color: #ffffff !important;
        font-size: clamp(2.35rem, 6vw, 5rem);
        line-height: 0.98;
        margin: 0 0 {Spacing.MD};
        letter-spacing: 0 !important;
    }}

    .public-hero p {{
        color: rgba(255, 255, 255, 0.88) !important;
        font-size: clamp(1rem, 2.4vw, 1.2rem);
        line-height: 1.65;
        margin: 0 0 {Spacing.LG};
    }}

    .public-contact-grid,
    .public-trust-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: {Spacing.MD};
        margin: {Spacing.LG} 0 {Spacing.XL};
    }}

    .public-info-card,
    .public-trust-card {{
        background: #ffffff;
        border: 1px solid #e8dfd4;
        border-radius: {BorderRadius.XL};
        padding: {Spacing.LG};
        box-shadow: 0 16px 40px -32px rgba(17, 24, 39, 0.45);
    }}

    .public-info-card strong,
    .public-trust-card h3 {{
        display: block;
        color: #111827 !important;
        font-size: {Typography.H4};
        margin: 0 0 {Spacing.SM};
    }}

    .public-info-card span,
    .public-info-card p,
    .public-trust-card p {{
        color: #6b7280 !important;
        font-size: {Typography.SMALL};
        margin: 0;
    }}

    .public-section-heading {{
        text-align: center;
        margin: {Spacing.XXL} auto {Spacing.XL};
        max-width: 720px;
    }}

    .public-section-heading h2 {{
        color: #111827 !important;
        font-size: clamp(1.8rem, 4vw, 2.6rem);
        margin: 0 0 {Spacing.SM};
    }}

    .public-section-heading p {{
        color: #6b7280 !important;
        margin: 0;
    }}

    .public-service-button .stButton > button {{
        min-height: 150px !important;
        background: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #e8dfd4 !important;
        border-radius: 18px !important;
        text-align: left !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        padding: {Spacing.LG} !important;
        white-space: pre-line !important;
        box-shadow: 0 16px 40px -32px rgba(17, 24, 39, 0.45) !important;
    }}

    .public-service-button .stButton > button:hover {{
        border-color: #c59f55 !important;
        box-shadow: 0 22px 46px -34px rgba(17, 24, 39, 0.6) !important;
    }}

    .public-cta .stButton > button,
    .booking-panel .stButton > button,
    .booking-panel [data-testid="stFormSubmitButton"] button {{
        min-height: 52px !important;
        border-radius: 14px !important;
        background: linear-gradient(135deg, #111827 0%, #2f241d 100%) !important;
        border: 1px solid rgba(17, 24, 39, 0.16) !important;
        color: #ffffff !important;
        box-shadow: 0 14px 28px -22px rgba(17, 24, 39, 0.7) !important;
    }}

    .public-booking-shell {{
        max-width: 900px;
        margin: {Spacing.MD} auto {Spacing.XXL};
    }}

    .booking-panel,
    .booking-section {{
        background: #ffffff !important;
        border: 1px solid #e8dfd4 !important;
        border-radius: 22px !important;
        box-shadow: 0 22px 56px -42px rgba(17, 24, 39, 0.65) !important;
    }}

    .stProgress {{
        max-width: 960px;
        margin: 0 auto 1rem;
    }}

    .stProgress [data-testid="stProgressBar"] {{
        background: #c59f55;
    }}

    .stButton > button,
    [data-testid="stFormSubmitButton"] button,
    .stLinkButton > a {{
        min-height: 48px;
        border-radius: 12px;
        border: 1px solid #d9cdbc;
        background: #ffffff;
        color: #111827;
        font-weight: 700;
        white-space: pre-line;
        line-height: 1.35;
        padding: 0.75rem 1rem;
        box-shadow: 0 10px 26px -24px rgba(17, 24, 39, 0.5);
    }}

    .stButton > button:hover,
    [data-testid="stFormSubmitButton"] button:hover,
    .stLinkButton > a:hover {{
        border-color: #c59f55;
        background: #fffaf2;
        color: #111827;
        box-shadow: 0 14px 32px -24px rgba(17, 24, 39, 0.55);
    }}

    [data-testid="stForm"] {{
        background: #ffffff;
        border: 1px solid #eadfce;
        border-radius: 18px;
        padding: 1.25rem;
        box-shadow: 0 16px 42px -36px rgba(17, 24, 39, 0.55);
    }}

    [data-testid="stTextInput"] input,
    [data-testid="stDateInput"] input {{
        min-height: 46px;
        border-radius: 12px;
        border: 1px solid #d9cdbc;
        background: #fffdf9;
        color: #111827;
        font-size: 1rem;
    }}

    [data-testid="stTextInput"] input:focus,
    [data-testid="stDateInput"] input:focus {{
        border-color: #c59f55;
        box-shadow: 0 0 0 3px rgba(197, 159, 85, 0.18);
    }}

    [data-testid="stAlert"] {{
        border-radius: 14px;
    }}

    [data-testid="stExpander"] {{
        border: 1px solid #eadfce;
        border-radius: 16px;
        overflow: hidden;
        background: #ffffff;
    }}

    .public-payment-notice {{
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-left: 5px solid #c2410c;
        border-radius: 18px;
        padding: {Spacing.LG};
        margin: 0 0 {Spacing.LG};
        text-align: center;
    }}

    .public-payment-notice h3 {{
        color: #7c2d12 !important;
        margin: 0 0 {Spacing.SM};
        font-size: {Typography.H4};
    }}

    .public-payment-notice p {{
        color: #9a3412 !important;
        margin: 0;
        font-size: {Typography.SMALL};
        line-height: 1.55;
    }}

    .public-payment-helper {{
        color: #4b5563 !important;
        text-align: center;
        font-size: {Typography.SMALL};
        margin: {Spacing.SM} 0;
    }}

    .public-summary-card {{
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: {Spacing.LG};
    }}

    .public-summary-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: {Spacing.MD};
    }}

    .public-summary-item {{
        border-top: 1px solid rgba(22, 163, 74, 0.18);
        padding-top: {Spacing.SM};
    }}

    .public-summary-item span {{
        display: block;
        color: #15803d;
        font-size: {Typography.TINY};
        font-weight: {Typography.BOLD};
        margin-bottom: 4px;
    }}

    .public-summary-item strong {{
        color: #166534;
        font-size: {Typography.BODY};
    }}

    .public-note {{
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-left: 4px solid #2563eb;
        border-radius: 14px;
        padding: {Spacing.MD};
        margin: {Spacing.MD} 0;
        color: #1e40af;
        text-align: center;
        font-size: {Typography.SMALL};
        font-weight: {Typography.SEMIBOLD};
    }}

    .public-warning-note {{
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-left: 4px solid #f59e0b;
        border-radius: 14px;
        padding: {Spacing.MD};
        margin: {Spacing.MD} 0 {Spacing.LG};
        color: #92400e;
        font-size: {Typography.SMALL};
        line-height: 1.6;
    }}

    .step-indicator {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 960px;
        margin: 0 auto 1.25rem;
        gap: 10px;
        background: #ffffff;
        border: 1px solid #e8dfd4;
        border-radius: 18px;
        padding: 0.85rem;
        box-shadow: 0 12px 32px -28px rgba(17, 24, 39, 0.45);
        overflow-x: auto;
    }}

    .step-item {{
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
    }}

    .step-circle {{
        width: 42px;
        height: 42px;
        min-width: 42px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease-in-out;
    }}

    .step-circle.active {{
        background: #111827;
        color: white;
        box-shadow: 0 0 0 4px rgba(197, 159, 85, 0.18);
    }}

    .step-circle.completed {{
        background: #22c55e;
        color: white;
    }}

    .step-circle.pending {{
        background: #f8f4ee;
        color: #6b7280;
        border: 2px solid #eadfce;
    }}

    .step-connector {{
        flex: 1;
        height: 2px;
        min-width: 18px;
        background: #eadfce;
        margin-top: 22px;
    }}

    .step-connector.active {{
        background: #c59f55;
    }}

    .step-label {{
        font-size: 0.85rem;
        color: #4b5563;
        text-align: center;
        min-width: 72px;
        max-width: 92px;
        line-height: 1.25;
    }}

    .step-label.active {{
        color: #7c3aed;
        font-weight: 600;
    }}

    @media (max-width: 768px) {{
        .block-container,
        [data-testid="stMainBlockContainer"] {{
            padding: 1rem 1rem 1.5rem !important;
        }}

        .public-hero {{
            min-height: 560px;
            border-radius: 22px;
            background:
                radial-gradient(circle at 50% 0%, rgba(197, 159, 85, 0.28), transparent 38%),
                linear-gradient(180deg, #2f241d 0%, #111827 68%, #0b0f19 100%);
        }}

        .public-contact-grid,
        .public-trust-grid {{
            grid-template-columns: 1fr;
        }}

        .public-service-button .stButton > button {{
            min-height: 120px !important;
        }}

        .step-indicator {{
            overflow-x: auto;
            justify-content: flex-start !important;
            padding: 0.75rem;
        }}

        .step-item {{
            min-width: 78px;
        }}

        .step-label {{
            font-size: 0.85rem;
        }}

        .public-summary-grid {{
            grid-template-columns: 1fr;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


def render_public_landing_hero(barberia):
    """Render the public barberia hero using shared public CSS classes."""
    nombre = barberia.get("nombre", "Barbería")
    telefono = barberia.get("telefono") or "Teléfono por confirmar"
    direccion = barberia.get("direccion") or "Dirección por confirmar"
    ciudad = barberia.get("ciudad") or "Atención local"
    logo_url = barberia.get("logo_url")
    banner_url = barberia.get("banner_url") or barberia.get("imagen_url") or barberia.get("foto_url")
    logo_html = f'<img src="{logo_url}" alt="{nombre}">' if logo_url else "BL"
    hero_style = ""
    if banner_url:
        hero_style = (
            'style="background: linear-gradient(90deg, rgba(17, 24, 39, 0.92) 0%, '
            'rgba(17, 24, 39, 0.68) 52%, rgba(17, 24, 39, 0.24) 100%), '
            f'url(\'{banner_url}\') center/cover;"'
        )

    st.markdown(f"""
    <div class="public-topbar">
        <div style="display:flex; align-items:center; gap:12px;">
            <div class="public-logo">{logo_html}</div>
            <div>
                <p class="public-brand-name">{nombre}</p>
                <p class="public-brand-meta">Reserva online</p>
            </div>
        </div>
    </div>
    <section class="public-hero" {hero_style}>
        <div class="public-hero-content">
            <div class="public-badge">Barbería premium · Reserva simple</div>
            <h1>{nombre}</h1>
            <p>Cortes precisos, barberos expertos y horarios disponibles en segundos. Elige servicio, barbero y hora sin llamadas.</p>
        </div>
    </section>
    <div class="public-contact-grid">
        <div class="public-info-card"><strong>Teléfono</strong><span>{telefono}</span></div>
        <div class="public-info-card"><strong>Dirección</strong><span>{direccion}</span></div>
        <div class="public-info-card"><strong>Ciudad</strong><span>{ciudad}</span></div>
    </div>
    """, unsafe_allow_html=True)


def render_public_payment_notice():
    """Render public payment reminder without touching payment logic."""
    st.markdown("""
    <div class="public-payment-notice">
        <h3>Finaliza tu pago ahora</h3>
        <p>Tu hora está bloqueada temporalmente para ti. Completa el pago para asegurar tu cita.</p>
    </div>
    """, unsafe_allow_html=True)


def render_public_booking_summary(data):
    """Render public booking summary card."""
    st.markdown(f"""
    <div class="public-summary-card">
        <div class="public-summary-grid">
            <div class="public-summary-item">
                <span>Servicio</span>
                <strong>{data.get('servicio', 'N/A')}</strong>
            </div>
            <div class="public-summary-item">
                <span>Barbero</span>
                <strong>{data.get('barbero_nombre', 'N/A')}</strong>
            </div>
            <div class="public-summary-item">
                <span>Fecha y hora</span>
                <strong>{data.get('fecha', 'N/A')} · {data.get('hora', 'N/A')}</strong>
            </div>
            <div class="public-summary-item">
                <span>Monto</span>
                <strong>${data.get('precio', 0):,}</strong>
            </div>
            <div class="public-summary-item">
                <span>Reserva</span>
                <strong>#{data.get('reserva_id', 'N/A')}</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_public_note(message, warning=False):
    """Render a compact public note."""
    class_name = "public-warning-note" if warning else "public-note"
    st.markdown(f'<div class="{class_name}">{message}</div>', unsafe_allow_html=True)


def render_public_section_heading(title, subtitle=None):
    """Render a public-facing section heading."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div class="public-section-heading">
        <h2>{title}</h2>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def apply_internal_panel_css():
    """Apply SaaS styling for authenticated internal panels only."""
    st.markdown(f"""
    <style>
    .stApp {{
        background: {Colors.BACKGROUND} !important;
    }}

    .block-container {{
        max-width: 1380px !important;
        padding: {Spacing.LG} {Spacing.XL} {Spacing.XXL} !important;
    }}

    [data-testid="stSidebar"] {{
        background: {Colors.CARD} !important;
        border-right: 1px solid {Colors.BORDER} !important;
        box-shadow: 8px 0 28px -26px rgba(15, 23, 42, 0.35) !important;
    }}

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {{
        color: {Colors.TEXT} !important;
    }}

    [data-testid="stSidebar"] .stCaptionContainer {{
        color: {Colors.TEXT_TERTIARY} !important;
    }}

    [data-testid="stSidebar"] hr {{
        border: none !important;
        border-top: 1px solid {Colors.BORDER} !important;
        margin: {Spacing.MD} 0 !important;
    }}

    [data-testid="stSidebar"] [role="radiogroup"] {{
        display: flex;
        flex-direction: column;
        gap: 6px;
    }}

    [data-testid="stSidebar"] [role="radio"] {{
        border-radius: {BorderRadius.MD} !important;
        padding: 10px 12px !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        transition: all {Transitions.FAST} !important;
    }}

    [data-testid="stSidebar"] [role="radio"]:hover {{
        background: {rgb_to_rgba(Colors.PRIMARY, 0.07)} !important;
        border-color: {rgb_to_rgba(Colors.PRIMARY, 0.16)} !important;
    }}

    [data-testid="stSidebar"] [aria-checked="true"] {{
        background: {rgb_to_rgba(Colors.PRIMARY, 0.10)} !important;
        border-color: {rgb_to_rgba(Colors.PRIMARY, 0.22)} !important;
        color: {Colors.PRIMARY} !important;
        font-weight: {Typography.SEMIBOLD} !important;
    }}

    [data-testid="stSidebar"] .stButton > button {{
        justify-content: flex-start !important;
        background: {Colors.CARD_HOVER} !important;
        color: {Colors.TEXT} !important;
        border: 1px solid {Colors.BORDER} !important;
        box-shadow: none !important;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        background: {rgb_to_rgba(Colors.PRIMARY, 0.08)} !important;
        color: {Colors.PRIMARY} !important;
        border-color: {rgb_to_rgba(Colors.PRIMARY, 0.25)} !important;
        transform: none !important;
    }}

    .panel-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: {Spacing.LG};
        background: {Colors.CARD};
        border: 1px solid {Colors.BORDER};
        border-radius: {BorderRadius.XL};
        padding: {Spacing.XL};
        margin: 0 0 {Spacing.XL} 0;
        box-shadow: {Shadows.SM};
    }}

    .panel-eyebrow {{
        color: {Colors.PRIMARY};
        font-size: {Typography.TINY};
        font-weight: {Typography.BOLD};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: {Spacing.SM};
    }}

    .panel-title {{
        color: {Colors.TEXT};
        font-size: 2rem;
        font-weight: {Typography.BOLD};
        line-height: 1.12;
        margin: 0;
    }}

    .panel-subtitle {{
        color: {Colors.TEXT_SECONDARY};
        font-size: {Typography.BODY};
        margin: {Spacing.SM} 0 0 0;
        max-width: 760px;
    }}

    .panel-header-meta {{
        color: {Colors.TEXT_SECONDARY};
        background: {Colors.CARD_HOVER};
        border: 1px solid {Colors.BORDER};
        border-radius: {BorderRadius.FULL};
        padding: 8px 12px;
        font-size: {Typography.SMALL};
        font-weight: {Typography.MEDIUM};
        white-space: nowrap;
    }}

    [data-testid="metric-container"],
    div[data-testid="stForm"],
    [data-testid="stExpander"],
    div[data-testid="stVerticalBlockBorderWrapper"],
    .card-container,
    .premium-card {{
        background: {Colors.CARD} !important;
        border: 1px solid {Colors.BORDER} !important;
        border-radius: {BorderRadius.LG} !important;
        box-shadow: {Shadows.SM} !important;
    }}

    [data-testid="metric-container"] {{
        padding: {Spacing.LG} !important;
    }}

    [data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color: {Colors.TEXT} !important;
        font-weight: {Typography.BOLD} !important;
    }}

    .section-title {{
        color: {Colors.TEXT} !important;
        font-size: 1.45rem !important;
        font-weight: {Typography.BOLD} !important;
        margin: {Spacing.LG} 0 {Spacing.SM} 0 !important;
    }}

    .subsection-title {{
        color: {Colors.TEXT} !important;
        font-size: 1.05rem !important;
        font-weight: {Typography.SEMIBOLD} !important;
        margin: {Spacing.LG} 0 {Spacing.SM} 0 !important;
        border-left: 3px solid {Colors.PRIMARY};
        padding-left: {Spacing.SM};
    }}

    .stTabs [data-baseweb="tab-list"] {{
        background: {Colors.CARD};
        border: 1px solid {Colors.BORDER};
        border-radius: {BorderRadius.LG};
        padding: 6px;
        gap: 4px;
        box-shadow: {Shadows.SM};
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: {BorderRadius.MD};
        color: {Colors.TEXT_SECONDARY};
        font-weight: {Typography.MEDIUM};
        padding: 10px 14px;
    }}

    .stTabs [aria-selected="true"] {{
        background: {rgb_to_rgba(Colors.PRIMARY, 0.10)} !important;
        color: {Colors.PRIMARY} !important;
    }}

    [data-testid="stDataFrame"],
    [data-testid="stTable"],
    table {{
        background: {Colors.CARD} !important;
        border: 1px solid {Colors.BORDER} !important;
        border-radius: {BorderRadius.LG} !important;
        box-shadow: {Shadows.SM} !important;
        overflow: hidden !important;
    }}

    th {{
        background: {Colors.CARD_HOVER} !important;
        color: {Colors.TEXT} !important;
    }}

    td {{
        color: {Colors.TEXT_SECONDARY} !important;
    }}

    .fc, .fc-view-harness, .fc-scrollgrid {{
        background: {Colors.CARD} !important;
        border-color: {Colors.BORDER} !important;
        border-radius: {BorderRadius.LG} !important;
    }}

    .fc-toolbar-title {{
        color: {Colors.TEXT} !important;
        font-size: 1.25rem !important;
        font-weight: {Typography.BOLD} !important;
    }}

    .fc-button {{
        background: {Colors.CARD_HOVER} !important;
        color: {Colors.TEXT} !important;
        border: 1px solid {Colors.BORDER} !important;
        border-radius: {BorderRadius.MD} !important;
        box-shadow: none !important;
    }}

    .fc-button-primary:not(:disabled).fc-button-active,
    .fc-button-primary:not(:disabled):active {{
        background: {Colors.PRIMARY} !important;
        color: {Colors.WHITE} !important;
        border-color: {Colors.PRIMARY} !important;
    }}

    .panel-empty-state {{
        background: {Colors.CARD};
        border: 1px dashed {Colors.BORDER};
        border-radius: {BorderRadius.XL};
        padding: {Spacing.XXL};
        text-align: center;
        color: {Colors.TEXT_SECONDARY};
        box-shadow: {Shadows.SM};
    }}

    .panel-empty-state h3 {{
        color: {Colors.TEXT};
        margin: 0 0 {Spacing.SM} 0;
        font-size: {Typography.H3};
    }}

    @media (max-width: 768px) {{
        .block-container {{
            padding: {Spacing.MD} !important;
        }}

        .panel-header {{
            display: block;
            padding: {Spacing.LG};
        }}

        .panel-title {{
            font-size: 1.55rem;
        }}

        .panel-header-meta {{
            display: inline-block;
            margin-top: {Spacing.MD};
            white-space: normal;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


def render_panel_header(title, subtitle=None, eyebrow=None, meta=None):
    """Render a consistent header for authenticated internal panels."""
    eyebrow_html = f'<div class="panel-eyebrow">{eyebrow}</div>' if eyebrow else ""
    subtitle_html = f'<p class="panel-subtitle">{subtitle}</p>' if subtitle else ""
    meta_html = f'<div class="panel-header-meta">{meta}</div>' if meta else ""

    st.markdown(f"""
    <div class="panel-header">
        <div>
            {eyebrow_html}
            <h1 class="panel-title">{title}</h1>
            {subtitle_html}
        </div>
        {meta_html}
    </div>
    """, unsafe_allow_html=True)


def render_panel_empty_state(title, description):
    """Render a clean placeholder card for internal panel sections."""
    st.markdown(f"""
    <div class="panel-empty-state">
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)


# ==================== COMPONENT BUILDERS ====================
def render_card(content, title=None, bg_color=None, border_color=None, class_name="card-container"):
    """
    Render a styled card with optional title
    
    Args:
        content: Function or string to display inside card
        title: Optional card title
        bg_color: Optional background color override
        border_color: Optional border color override
        class_name: CSS class to apply (card-container or premium-card)
    """
    style = f"""
    <div class="{class_name}" style="
        {'background-color: ' + bg_color + ' !important;' if bg_color else ''}
        {'border-color: ' + border_color + ' !important;' if border_color else ''}
    ">
    """
    
    if title:
        style += f"""
        <h4 style="
            color: {Colors.TEXT};
            margin-top: 0;
            margin-bottom: {Spacing.MD};
            font-size: {Typography.H4};
            font-weight: {Typography.SEMIBOLD};
        ">{title}</h4>
        """
    
    st.markdown(style, unsafe_allow_html=True)
    if callable(content):
        content()
    else:
        st.markdown(content, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_section_title(title, subtitle=None):
    """Render a section title with optional subtitle"""
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        {'<p style="color: ' + Colors.TEXT_SECONDARY + '; margin: ' + Spacing.XS + ' 0 0 0;">' + subtitle + '</p>' if subtitle else ''}
        """,
        unsafe_allow_html=True
    )


def render_subsection_title(title):
    """Render a subsection title"""
    st.markdown(f"""<div class="subsection-title">{title}</div>""", unsafe_allow_html=True)


def render_badge(text, badge_type="primary"):
    """
    Render a styled badge
    
    Args:
        text: Badge text
        badge_type: 'primary', 'success', 'warning', or 'danger'
    """
    class_map = {
        "success": "badge-success",
        "warning": "badge-warning",
        "danger": "badge-danger",
    }
    badge_class = class_map.get(badge_type, "badge")
    st.markdown(f"""<span class="{badge_class}">{text}</span>""", unsafe_allow_html=True)


def render_divider(color=Colors.BORDER, height="2px", margin=Spacing.LG):
    """Render a custom divider line"""
    st.markdown(
        f"""
        <div style="
            background-color: {color};
            height: {height};
            margin: {margin} 0;
            border-radius: {BorderRadius.SM};
        "></div>
        """,
        unsafe_allow_html=True
    )


def render_stat_box(label, value, icon="📊", color=Colors.PRIMARY):
    """
    Render a stat box with icon and value
    
    Args:
        label: Stat label
        value: Stat value
        icon: Emoji icon
        color: Accent color
    """
    st.markdown(
        f"""
        <div style="
            background: {Gradients.CARD_SUBTLE};
            border: 2px solid {Colors.BORDER};
            border-radius: {BorderRadius.LG};
            padding: {Spacing.LG};
            text-align: center;
            transition: all {Transitions.NORMAL};
            box-shadow: {Shadows.MD}, {Shadows.INSET_SUBTLE};
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                right: -30px;
                width: 100px;
                height: 100px;
                background: {rgb_to_rgba(color, 0.1)};
                border-radius: 50%;
                z-index: 0;
            "></div>
            <div style="
                position: relative;
                z-index: 1;
            ">
                <div style="
                    font-size: 2.5rem;
                    margin-bottom: {Spacing.SM};
                ">{icon}</div>
                <div style="
                    color: {Colors.TEXT_SECONDARY};
                    font-size: {Typography.SMALL};
                    margin-bottom: {Spacing.SM};
                    text-transform: none;
                    letter-spacing: 0;
                    line-height: 1.4;
                ">{label}</div>
                <div style="
                    color: {color};
                    font-size: {Typography.H2};
                    font-weight: {Typography.BOLD};
                    background: linear-gradient(135deg, {color} 0%, {color} 50%, rgba(255,255,255,0.1) 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: {color};
                ">{value}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_grid(metrics, columns=None, gap="large"):
    """Render a row of stat boxes using the existing metric card style."""
    if not metrics:
        return

    column_count = columns or len(metrics)
    cols = st.columns(column_count, gap=gap)

    for index, metric in enumerate(metrics):
        if isinstance(metric, dict):
            label = metric.get("label", "")
            value = metric.get("value", "")
            icon = metric.get("icon", "📊")
            color = metric.get("color", Colors.PRIMARY)
        else:
            label, value, icon, color = metric

        with cols[index % column_count]:
            render_stat_box(label, value, icon, color)


def render_alert(message, alert_type="info", title=None):
    """
    Render a styled alert message
    
    Args:
        message: Alert message text
        alert_type: 'success', 'error', 'warning', or 'info'
        title: Optional alert title
    """
    color_map = {
        "success": Colors.SUCCESS,
        "error": Colors.DANGER,
        "warning": Colors.WARNING,
        "info": Colors.SECONDARY,
    }
    color = color_map.get(alert_type, Colors.SECONDARY)
    
    icon_map = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
    }
    icon = icon_map.get(alert_type, "ℹ️")
    
    st.markdown(
        f"""
        <div style="
            background-color: rgba({int(color.lstrip('#')[0:2], 16)}, {int(color.lstrip('#')[2:4], 16)}, {int(color.lstrip('#')[4:6], 16)}, 0.1);
            border-left: 4px solid {color};
            border-radius: {BorderRadius.LG};
            padding: {Spacing.MD};
            margin: {Spacing.MD} 0;
        ">
            <div style="
                display: flex;
                align-items: flex-start;
                gap: {Spacing.MD};
            ">
                <div style="
                    font-size: 1.5rem;
                    margin-top: 2px;
                ">{icon}</div>
                <div>
                    {f'<h4 style="margin: 0 0 {Spacing.SM} 0; color: {color};">{title}</h4>' if title else ''}
                    <p style="
                        color: {Colors.TEXT};
                        margin: 0;
                        line-height: 1.5;
                    ">{message}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_note(message, note_type="info", title=None):
    """Render a compact informational note using the existing alert style."""
    render_alert(message, alert_type=note_type, title=title)


def render_info_card(title, body, icon=None, class_name="card-container"):
    """Render a reusable informational card with optional icon and body text."""
    heading = f"{icon} {title}" if icon else title
    card_body = f'<div style="color: {Colors.TEXT_SECONDARY}; line-height: 1.6;">{body}</div>'
    render_card(card_body, title=heading, class_name=class_name)


def render_container(content, class_name=None, style="", unsafe_allow_html=True):
    """Render a lightweight HTML container wrapper for simple presentational blocks."""
    class_attr = f' class="{class_name}"' if class_name else ""
    st.markdown(
        f'<div{class_attr} style="{style}">{content}</div>',
        unsafe_allow_html=unsafe_allow_html,
    )


def render_hero_banner(title, subtitle, style, icon=None, icon_size="5em", title_size="2.8em", subtitle_size="1.2em", margin_bottom="50px"):
    """Render a reusable centered hero banner for simple presentational screens."""
    icon_html = f'<p style="font-size: {icon_size}; margin: 0;">{icon}</p>' if icon else ""
    content = f"""
        {icon_html}
        <h1 style="margin: 20px 0 0 0; font-size: {title_size}; font-weight: 700;">{title}</h1>
        <p style="margin: 15px 0 0 0; font-size: {subtitle_size}; opacity: 0.95;">{subtitle}</p>
    """
    render_container(
        content,
        style=f"{style}margin-bottom: {margin_bottom};",
    )


def render_preview_card(title, background_color, text_color="white", icon="Tijeras"):
    """Render the centered preview tile used in the registration flow."""
    content = f"""
            <p style="font-size: 2em; margin: 0;">{icon}</p>
            <p style="font-size: 0.9em; margin: 10px 0 0 0;">{title}</p>
    """
    render_container(
        content,
        style=(
            f"background: {background_color};"
            "padding: 60px;"
            "border-radius: 15px;"
            "text-align: center;"
            f"color: {text_color};"
        ),
    )


def render_success_hero(title, subtitle, icon="Exito"):
    """Render the success hero used on the final registration screen."""
    render_hero_banner(
        title,
        subtitle,
        "background: linear-gradient(135deg, #10b981 0%, #34d399 100%);padding: 80px 40px;border-radius: 20px;text-align: center;color: white;box-shadow: 0 20px 60px rgba(16, 185, 129, 0.2);",
        icon=icon,
        icon_size="5em",
        title_size="2.8em",
        subtitle_size="1.2em",
        margin_bottom="50px",
    )


def render_status_legend(paid_label="Pagado", pending_label="Pendiente", compact=False):
    """Render the calendar status legend used in reservation views."""
    font_size = "11px" if compact else "12px"
    icon_size = "10px" if compact else "12px"
    st.markdown(f"""
    <div style="display: flex; gap: 12px; font-size: {font_size}; padding: 8px;">
        <div><span style="display: inline-block; width: {icon_size}; height: {icon_size}; background: #16a34a; border-radius: 2px; margin-right: 4px;"></span><strong>{paid_label}</strong></div>
        <div><span style="display: inline-block; width: {icon_size}; height: {icon_size}; background: #f59e0b; border-radius: 2px; margin-right: 4px;"></span><strong>{pending_label}</strong></div>
    </div>
    """, unsafe_allow_html=True)


def render_loading_panel(message, icon="Espera", padding="20px", top_margin="0"):
    """Render a small centered loading panel with a short status message."""
    content = f"""
        <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
        <p style="color: #7c3aed; font-weight: 600; margin: 0;">{message}</p>
    """
    render_container(
        content,
        style=(
            f"text-align: center;"
            f"padding: {padding};"
            f"margin-top: {top_margin};"
            "display: inline-block;"
            "color: #7c3aed;"
            "font-weight: 600;"
        ),
    )


def render_reservation_card(cliente, servicio, inicio_str, fecha_str, monto, estado, estado_color):
    """Render the detailed reservation card used in reservation listings."""
    inner_card_html = f"""<div style="display: flex; justify-content: space-between; margin-bottom: 16px;"><div><div style="font-size: 12px; color: #999; margin-bottom: 4px;">CLIENTE</div><div style="font-size: 18px; font-weight: 600; color: #fff;">{cliente}</div></div><div><div style="font-size: 12px; color: #999; margin-bottom: 4px;">SERVICIO</div><div style="font-size: 18px; font-weight: 600; color: #fff;">{servicio}</div></div></div><div style="display: flex; justify-content: space-between; margin-bottom: 16px;"><div><div style="font-size: 12px; color: #999; margin-bottom: 4px;">HORA</div><div style="font-size: 18px; font-weight: 600; color: #fff;">{inicio_str}</div><div style="font-size: 12px; color: #666;">{fecha_str}</div></div><div><div style="font-size: 12px; color: #999; margin-bottom: 4px;">MONTO</div><div style="font-size: 18px; font-weight: 600; color: #fff;">${monto}</div></div></div><div style="border-top: 1px solid #333; padding-top: 12px;"><div style="display: inline-block; background: {estado_color}20; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; color: {estado_color}; border: 1px solid {estado_color};">{estado}</div></div>"""

    card_html = f"""<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 24px; border-radius: 16px; color: white; box-shadow: 0 10px 30px rgba(0,0,0,0.5);"><h3 style="margin: 0 0 20px 0; color: white; font-size: 20px;">Tu reserva</h3>{inner_card_html}</div>"""
    st.markdown(card_html, unsafe_allow_html=True)


def render_interactive_card(content, title=None, icon=None, clickable=True, on_click=None):
    """
    Render an interactive card with rounded corners, shadow, and hover lift.
    
    Features:
    - Rounded corners (16px)
    - Layered shadows for depth
    - Hover lift effect (-4px translateY)
    - Clickable appearance with pointer cursor
    - Active state feedback
    - Optional icon and title
    
    Args:
        content: Card content (string or callable)
        title: Optional card title
        icon: Optional emoji icon (appears beside title)
        clickable: Whether card should show clickable state
        on_click: Optional callback function
    
    Returns:
        True if card was clicked, False otherwise
    """
    card_id = f"card_{hash(str(content))}_{''.join(title.split() if title else [])}"
    
    card_html = f"""
    <style>
        .interactive-card-{card_id} {{
            background: {Gradients.CARD_SUBTLE};
            border: 1px solid {Colors.BORDER};
            border-radius: {BorderRadius.LG};
            padding: {Spacing.LG};
            box-shadow: {Shadows.MD}, {Shadows.INSET_SUBTLE};
            transition: all {Transitions.NORMAL};
            cursor: {'pointer' if clickable else 'default'};
            position: relative;
            overflow: hidden;
        }}
        
        .interactive-card-{card_id}:hover {{
            box-shadow: {Shadows.LG}, {Shadows.INSET_SUBTLE}, {Shadows.GLOW_SOFT};
            border-color: {Colors.PRIMARY};
            background: {Gradients.CARD_HOVER};
            transform: translateY(-4px);
        }}
        
        .interactive-card-{card_id}:active {{
            transform: translateY(-2px);
            box-shadow: {Shadows.MD}, {Shadows.INSET_SUBTLE};
        }}
        
        .card-header-{card_id} {{
            display: flex;
            align-items: center;
            gap: {Spacing.MD};
            margin-bottom: {Spacing.MD};
            padding-bottom: {Spacing.MD};
            border-bottom: 1px solid {rgb_to_rgba(Colors.PRIMARY, 0.2)};
        }}
        
        .card-icon-{card_id} {{
            font-size: 1.75rem;
            line-height: 1;
        }}
        
        .card-title-{card_id} {{
            font-size: {Typography.H4};
            font-weight: {Typography.SEMIBOLD};
            color: {Colors.TEXT};
            margin: 0;
        }}
        
        .card-content-{card_id} {{
            font-size: {Typography.BODY};
            color: {Colors.TEXT_SECONDARY};
            line-height: 1.6;
        }}
    </style>
    
    <div class="interactive-card-{card_id}">
    """
    
    if title or icon:
        card_html += f'<div class="card-header-{card_id}">'
        if icon:
            card_html += f'<span class="card-icon-{card_id}">{icon}</span>'
        if title:
            card_html += f'<h3 class="card-title-{card_id}">{title}</h3>'
        card_html += '</div>'
    
    card_html += f'<div class="card-content-{card_id}">'
    st.markdown(card_html, unsafe_allow_html=True)
    
    if callable(content):
        content()
    else:
        st.markdown(content, unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    if clickable and on_click:
        return st.button(
            "Select Card",
            key=card_id,
            use_container_width=True,
            help="Click to select this card"
        )
    return False


def render_action_button(label, primary=True, icon=None, full_width=True, size="medium", key=None):
    """
    Render an action button with strong CTA styling.
    
    Features:
    - Gradient background (primary/secondary)
    - Hover lift effect with shadow
    - Ripple effect on click
    - Optional icon
    - Multiple sizes
    - Smooth animations
    
    Args:
        label: Button text
        primary: True for primary button, False for secondary
        icon: Optional emoji icon
        full_width: Whether button spans full width
        size: 'small', 'medium', or 'large'
        key: Unique button key
    
    Returns:
        True if button clicked, False otherwise
    """
    size_styles = {
        "small": {
            "padding": "0.5rem 1rem",
            "font_size": Typography.SMALL,
            "height": "36px"
        },
        "medium": {
            "padding": "0.75rem 1.5rem",
            "font_size": Typography.BODY,
            "height": "44px"
        },
        "large": {
            "padding": "1rem 2rem",
            "font_size": Typography.H4,
            "height": "52px"
        }
    }
    
    style = size_styles.get(size, size_styles["medium"])
    gradient = Gradients.PRIMARY_BUTTON if primary else Gradients.SECONDARY_BUTTON
    
    button_html = f"""
    <style>
        .action-button-{key or label.replace(' ', '_')} {{
            display: {'block' if full_width else 'inline-block'};
            width: {'100%' if full_width else 'auto'};
        }}
    </style>
    """
    st.markdown(button_html, unsafe_allow_html=True)
    
    button_text = f"{icon} {label}" if icon else label
    
    return st.button(
        button_text,
        key=key or f"action_{label}",
        use_container_width=full_width,
        help=f"Click to {label.lower()}"
    )


def render_cta_section(title, description, button_text="Continuar", button_key=None, icon="🚀"):
    """
    Render a visually rich CTA (Call-To-Action) section with gradient background.
    
    Args:
        title: Section title
        description: Section description
        button_text: Button text
        button_key: Optional unique key for button
        icon: Emoji icon for the section
    
    Returns:
        True if button clicked, False otherwise
    """
    st.markdown(
        f"""
        <div style="
            background: {Gradients.CTA_PRIMARY};
            padding: {Spacing.XL};
            border-radius: {BorderRadius.XL};
            margin: {Spacing.XL} 0;
            box-shadow: {Shadows.FLOATING}, {Shadows.GLOW_STRONG};
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: shimmer 15s infinite;
                z-index: 0;
            "></div>
            <div style="
                position: relative;
                z-index: 2;
                color: {Colors.WHITE};
            ">
                <h2 style="
                    font-size: {Typography.H2};
                    font-weight: {Typography.BOLD};
                    margin: 0 0 {Spacing.MD} 0;
                    display: flex;
                    align-items: center;
                    gap: {Spacing.MD};
                    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                ">
                    <span style="font-size: 2.5rem;">{icon}</span>
                    {title}
                </h2>
                <p style="
                    font-size: {Typography.BODY};
                    margin: 0;
                    line-height: 1.6;
                    color: rgba(255, 255, 255, 0.95);
                    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
                ">
                    {description}
                </p>
            </div>
        </div>
        
        <style>
            @keyframes shimmer {{
                0% {{ transform: translate(-100%, -100%) rotate(45deg); }}
                100% {{ transform: translate(100%, 100%) rotate(45deg); }}
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        return st.button(
            button_text,
            key=button_key or f"cta_{title}",
            use_container_width=True,
            help=button_text
        )


def render_barber_card(barber_name, barber_id, availability="Disponible", icon="💈", is_selected=False, disabled=False):
    """
    Render a premium interactive barber selection card with smooth UX.
    
    Premium Features:
    - Smooth click feedback (scale 0.97, 100ms)
    - Hover depth effects (shadow lift, -2px translateY)
    - Improved visual hierarchy (3x icon, large bold name, lighter secondary)
    - Selected state with animated check mark
    - Smooth transitions (0.15-0.25s ease-in-out)
    - Responsive and accessible
    
    Args:
        barber_name: Name of the barber
        barber_id: Unique identifier for the barber
        availability: Availability status text (default: "Disponible")
        icon: Emoji icon for the barber (default: "💈")
        is_selected: Whether this barber is currently selected
        disabled: Whether the card is disabled
    
    Returns:
        True if card was clicked, False otherwise
    """
    
    # Generate unique key for this card's button
    barber_id_str = str(barber_id)
    button_key = f"barber_card_{barber_id_str}_{barber_name.replace(' ', '_')}"
    card_class = f"barber-card-{barber_id_str.replace(' ', '_').replace('-', '_').lower()}"
    
    # Determine colors and styles based on state
    if is_selected:
        border_color = Colors.PRIMARY
        border_width = "3px"
        bg_color = rgb_to_rgba(Colors.PRIMARY, 0.12)
        shadow = Shadows.LG
        check_mark = "✓"
        check_display = "flex"
    else:
        border_color = Colors.BORDER
        border_width = "2px"
        bg_color = Colors.CARD
        shadow = Shadows.MD
        check_mark = ""
        check_display = "none"
    
    if disabled:
        opacity = "0.6"
        cursor = "not-allowed"
        pointer_events = "none"
    else:
        opacity = "1"
        cursor = "pointer"
        pointer_events = "auto"
    
    # Build the enhanced card HTML with premium UX
    card_html = f"""
    <style>
        .{card_class} {{
            background: {Gradients.CARD_SUBTLE};
            border: {border_width} solid {border_color};
            border-radius: {BorderRadius.LG};
            padding: {Spacing.LG};
            text-align: center;
            cursor: {cursor};
            pointer-events: {pointer_events};
            transition: all 0.2s ease-in-out;
            box-shadow: {Shadows.MD}, {Shadows.INSET_SUBTLE};
            opacity: {opacity};
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 200px;
            position: relative;
            overflow: hidden;
            user-select: none;
            -webkit-user-select: none;
        }}
        
        .{card_class}:hover {{
            border-color: {Colors.PRIMARY};
            box-shadow: {Shadows.LG}, {Shadows.INSET_SUBTLE}, {Shadows.GLOW_SOFT};
            background: {Gradients.CARD_HOVER};
        }}
        
        .{card_class}:active {{
            transition: all 0.1s ease-in-out;
        }}
        
        .{card_class}.selected {{
            background: {Gradients.CARD_SELECTED};
            box-shadow: {Shadows.LG}, {Shadows.INSET_SUBTLE}, {Shadows.GLOW_STRONG};
        }}
        
        .barber-icon-container {{
            font-size: 3.5rem;
            margin-bottom: {Spacing.MD};
            display: block;
            line-height: 1;
        }}
        
        .barber-name {{
            font-size: 1.5rem;
            font-weight: {Typography.BOLD};
            color: {Colors.TEXT};
            margin: {Spacing.MD} 0 {Spacing.SM} 0;
            word-break: break-word;
            letter-spacing: 0.3px;
        }}
        
        .barber-divider {{
            width: 30px;
            height: 2px;
            background: {rgb_to_rgba(Colors.PRIMARY, 0.4)};
            margin: {Spacing.SM} auto {Spacing.SM} auto;
            border-radius: 1px;
        }}
        
        .barber-availability {{
            font-size: {Typography.TINY};
            color: {Colors.TEXT_SECONDARY};
            display: flex;
            align-items: center;
            justify-content: center;
            gap: {Spacing.SM};
            margin-top: {Spacing.SM};
            font-weight: {Typography.MEDIUM};
            letter-spacing: 0;
        }}
        
        .barber-availability::before {{
            content: "●";
            font-size: 0.4rem;
            color: {Colors.SUCCESS};
            animation: pulse-dot 2s ease-in-out infinite;
        }}
        
        @keyframes pulse-dot {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.6; }}
        }}
        
        .barber-check {{
            position: absolute;
            top: {Spacing.MD};
            right: {Spacing.MD};
            background: {Colors.SUCCESS};
            color: white;
            width: 40px;
            height: 40px;
            border-radius: {BorderRadius.FULL};
            display: {check_display};
            align-items: center;
            justify-content: center;
            font-weight: {Typography.BOLD};
            font-size: 1.5rem;
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
            z-index: 10;
        }}
    </style>
    
    <div class="{card_class}">
        {f'<div class="barber-check">{check_mark}</div>' if is_selected else ''}
        <span class="barber-icon-container">{icon}</span>
        <div class="barber-name">{barber_name}</div>
        <div class="barber-divider"></div>
        <div class="barber-availability">{availability}</div>
    </div>
    """
    
    # Render the card and button
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Create invisible button with the same width as the card container
    clicked = st.button(
        label="",
        key=button_key,
        use_container_width=True,
        disabled=disabled,
        help=f"Seleccionar a {barber_name}" if not disabled else "No disponible"
    )
    
    return clicked


def render_barber_selector(barbers, selected_id=None, icon="💈", on_select_callback=None):
    """
    Render a grid of barber selection cards with premium styling.
    
    Args:
        barbers: List of tuples (id, name) or dict with barber data
        selected_id: Currently selected barber ID
        icon: Emoji icon for all barber cards
        on_select_callback: Optional callback function called with (barber_id, barber_name)
    
    Returns:
        Selected barber ID, or None if nothing selected
    """
    
    if isinstance(barbers, dict):
        barbers = list(barbers.items())
    
    if not barbers:
        st.warning("No hay barberos disponibles")
        return None
    
    # Create responsive grid (3 columns on desktop, 2 on tablet, 1 on mobile)
    cols = st.columns(min(3, len(barbers)))
    selected_barber = None
    
    for idx, barber_info in enumerate(barbers):
        # Handle different input formats
        if isinstance(barber_info, (tuple, list)):
            barber_id, barber_name = barber_info[0], barber_info[1]
        else:
            barber_id = barber_info.get("id")
            barber_name = barber_info.get("name")
        
        with cols[idx % len(cols)]:
            is_selected = barber_id == selected_id
            clicked = render_barber_card(
                barber_name=barber_name,
                barber_id=barber_id,
                availability="✓ Disponible",
                icon=icon,
                is_selected=is_selected
            )
            
            if clicked:
                selected_barber = (barber_id, barber_name)
                if on_select_callback:
                    on_select_callback(barber_id, barber_name)
    
    return selected_barber


# ==================== UTILITY FUNCTIONS ====================
def get_gradient(start_color, end_color, angle="135deg"):
    """Generate a gradient CSS string"""
    return f"linear-gradient({angle}, {start_color} 0%, {end_color} 100%)"


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_rgba(hex_color, alpha=0.1):
    """Convert hex color to RGBA string"""
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r}, {g}, {b}, {alpha})"


def render_time_chips(available_times, selected_time=None, on_time_selected=None, columns=5):
    """
    Render available time slots as modern chip-style buttons.
    
    Features:
    - Chip-style buttons (small, rounded, spaced)
    - Grid layout (responsive, 3-5 columns)
    - Default: dark background, subtle border
    - Hover: scale 1.05, glow effect
    - Selected: gradient background, white text, bold, shadow
    - Click feedback: scale 0.97 on active
    - Ripple effect on click
    
    Args:
        available_times: List of time objects (datetime.time or datetime.datetime)
        selected_time: Currently selected time (datetime.time or datetime.datetime)
        on_time_selected: Optional callback function (time_obj) -> None
        columns: Number of columns (default 5, responsive)
    
    Returns:
        Selected time object, or None if nothing selected
    """
    
    if not available_times:
        st.warning("⏰ No hay horarios disponibles")
        return None
    
    # Normalize times for comparison
    selected_time_str = None
    if selected_time:
        if hasattr(selected_time, 'time'):  # datetime object
            selected_time_str = selected_time.time().strftime("%H:%M")
        elif hasattr(selected_time, 'strftime'):  # time object
            selected_time_str = selected_time.strftime("%H:%M")
        else:
            selected_time_str = str(selected_time)
    
    selected = None
    cols = st.columns(min(columns, len(available_times)))
    
    for idx, time_slot in enumerate(available_times):
        # Normalize time for display and comparison
        if hasattr(time_slot, 'time'):  # datetime object
            time_display = time_slot.time().strftime("%H:%M")
            time_obj = time_slot.time()
        elif hasattr(time_slot, 'strftime'):  # time object
            time_display = time_slot.strftime("%H:%M")
            time_obj = time_slot
        else:
            time_display = str(time_slot)
            time_obj = time_slot
        
        is_selected = time_display == selected_time_str
        
        # Create unique button key
        button_key = f"time_chip_{idx}_{time_display}"
        
        # Render button in column
        col_idx = idx % len(cols)
        with cols[col_idx]:
            # Create custom HTML button that looks like a chip
            chip_html = f"""
            <style>
                .chip-btn-{idx} {{
                    background-color: {"linear-gradient(135deg, " + Colors.PRIMARY + " 0%, " + Colors.PRIMARY_DARK + " 100%)" if is_selected else Colors.CARD};
                    border: 2px solid {"" + Colors.PRIMARY if is_selected else Colors.BORDER};
                    border-radius: {BorderRadius.LG};
                    padding: {Spacing.SM} {Spacing.MD};
                    font-size: {Typography.SMALL};
                    font-weight: {"bold" if is_selected else "600"};
                    color: {Colors.WHITE if is_selected else Colors.TEXT};
                    text-align: center;
                    cursor: pointer;
                    transition: all {Transitions.NORMAL};
                    width: 100%;
                    min-height: 44px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    position: relative;
                    overflow: hidden;
                }}
                
                .chip-btn-{idx}:hover {{
                    border-color: {Colors.PRIMARY};
                    background-color: {"linear-gradient(135deg, " + Colors.PRIMARY + " 0%, " + Colors.PRIMARY_DARK + " 100%)" if is_selected else rgb_to_rgba(Colors.PRIMARY, 0.08)};
                    box-shadow: {Shadows.MD}, {Shadows.GLOW_SOFT};
                }}
                
                .chip-btn-{idx}:active {{
                    box-shadow: {Shadows.SM}, inset 0 0 8px rgba(124, 58, 237, 0.1);
                }}
            </style>
            """
            
            st.markdown(chip_html, unsafe_allow_html=True)
            
            if st.button(
                f"🕐\n{time_display}",
                key=button_key,
                use_container_width=True,
                help=f"Seleccionar {time_display}"
            ):
                selected = time_obj
                if on_time_selected:
                    on_time_selected(time_obj)
    
    return selected


# ==================== SAAS LAYOUT WRAPPERS ====================

def render_booking_container(content_func=None):
    """
    Render a centered booking container.

    Supports both legacy callback usage:
        render_booking_container(lambda: ...)
    and current context-manager usage:
        with render_booking_container():
            ...
    """
    from contextlib import contextmanager

    @contextmanager
    def booking_container():
        st.markdown(
            f"""<style>
                .booking-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: {Spacing.XL} 0;
                }}
                .booking-panel {{
                    background: {Colors.CARD};
                    border: 1px solid {Colors.BORDER};
                    border-radius: {BorderRadius.LG};
                    padding: {Spacing.XL};
                    margin: {Spacing.LG} 0;
                    box-shadow: {Shadows.SM};
                }}
            </style>""",
            unsafe_allow_html=True
        )
        with st.container():
            yield

    if content_func and callable(content_func):
        with booking_container():
            content_func()
        return None

    return booking_container()


def close_booking_container():
    """Close a manually opened booking container div."""
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_booking_header(title, subtitle=None, step=None, total_steps=None):
    """
    Render booking flow header with title, subtitle, and optional step indicator.
    
    Args:
        title: Main title text
        subtitle: Optional subtitle/description
        step: Current step number (if showing progress)
        total_steps: Total number of steps
    
    Returns:
        None (renders directly to st)
    """
    subtitle_html = (
        f'<p style="font-size:{Typography.BODY};color:{Colors.TEXT_SECONDARY};'
        f'margin:0 0 {Spacing.LG} 0;line-height:1.6;">{subtitle}</p>'
    ) if subtitle else ""

    step_html = (
        f'<div style="display:flex;align-items:center;justify-content:center;'
        f'gap:{Spacing.SM};margin-top:{Spacing.MD};">'
        f'<span style="font-size:{Typography.SMALL};color:{Colors.PRIMARY};'
        f'font-weight:{Typography.BOLD};">Paso {step}</span>'
        f'<span style="color:{Colors.TEXT_TERTIARY};">de {total_steps}</span>'
        f'</div>'
    ) if (step and total_steps) else ""

    header_html = (
        f'<div style="text-align:center;margin-bottom:{Spacing.XXL};'
        f'padding-bottom:{Spacing.XL};border-bottom:1px solid {Colors.BORDER};">'
        f'<h1 style="font-size:{Typography.H1};font-weight:{Typography.BOLD};'
        f'color:{Colors.TEXT};margin:0 0 {Spacing.MD} 0;">{title}</h1>'
        f'{subtitle_html}'
        f'{step_html}'
        f'</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)


def render_booking_section(title=None, content_func=None):
    """
    Render a booking section.

    Supports both callback and context-manager usage.
    """
    from contextlib import contextmanager

    @contextmanager
    def booking_section():
        # Emit a self-contained title block (complete open+close in one st.markdown call)
        if title:
            title_html = (
                f'<div style="background:{Gradients.CARD_SUBTLE};'
                f'border:1px solid {Colors.BORDER};'
                f'border-radius:{BorderRadius.LG} {BorderRadius.LG} 0 0;'
                f'padding:{Spacing.LG} {Spacing.XL};'
                f'border-bottom:2px solid {rgb_to_rgba(Colors.PRIMARY, 0.2)};">'
                f'<h2 style="font-size:{Typography.H3};font-weight:{Typography.SEMIBOLD};'
                f'color:{Colors.TEXT};margin:0;">{title}</h2>'
                f'</div>'
            )
            st.markdown(title_html, unsafe_allow_html=True)
        # Use native st.container() — no open HTML tags left dangling
        with st.container():
            yield

    if content_func and callable(content_func):
        with booking_section():
            content_func()
        return None

    return booking_section()


def render_form_group(
    label,
    input_func=None,
    help_text=None,
    error_text=None,
    placeholder=None,
    key=None,
    help=None,
    value="",
    input_type="text",
    **input_kwargs,
):
    """
    Render a form input group with label and optional help/error text.

    If input_func is callable, it is rendered inside the group. If input_func is
    a string, current booking-flow calls treat it as placeholder text.
    """
    if isinstance(input_func, str):
        placeholder = placeholder or input_func
        input_func = None

    helper = help if help is not None else help_text

    st.markdown(
        f"""
        <div style="margin-bottom: {Spacing.LG};">
            <label style="
                display: block;
                font-size: {Typography.SMALL};
                font-weight: {Typography.SEMIBOLD};
                color: {Colors.TEXT};
                margin-bottom: {Spacing.SM};
                letter-spacing: 0;
            ">{label}</label>
        </div>
        """,
        unsafe_allow_html=True
    )

    if input_func and callable(input_func):
        result = input_func()
    else:
        result = st.text_input(
            help_text or label,
            value=value,
            placeholder=placeholder,
            key=key,
            type=input_type,
            help=helper,
            label_visibility="collapsed",
            **input_kwargs,
        )

    if helper:
        st.caption(helper)

    if error_text:
        st.markdown(
            f"""
            <p style="
                font-size: {Typography.SMALL};
                color: {Colors.DANGER};
                margin: {Spacing.SM} 0 0 0;
                font-weight: {Typography.SEMIBOLD};
            ">! {error_text}</p>
            """,
            unsafe_allow_html=True
        )

    return result


def render_button_group(buttons_config, layout="horizontal"):
    """
    Render a group of buttons with consistent spacing and alignment.
    
    Args:
        buttons_config: List of dicts with button config:
                       {'label': str, 'primary': bool, 'key': str, 'callback': callable}
        layout: 'horizontal' (side-by-side) or 'vertical' (stacked)
    
    Returns:
        None (renders directly to st)
    """
    if layout == "horizontal":
        cols = st.columns(len(buttons_config))
        for idx, btn_config in enumerate(buttons_config):
            with cols[idx]:
                label = btn_config.get('label', 'Button')
                primary = btn_config.get('primary', True)
                key = btn_config.get('key', f"btn_{idx}")
                
                if st.button(
                    label,
                    key=key,
                    use_container_width=True,
                    type="primary" if primary else "secondary"
                ):
                    callback = btn_config.get('callback')
                    if callback and callable(callback):
                        callback()
    else:  # vertical layout
        for btn_config in buttons_config:
            label = btn_config.get('label', 'Button')
            primary = btn_config.get('primary', True)
            key = btn_config.get('key', label)
            
            if st.button(
                label,
                key=key,
                use_container_width=True,
                type="primary" if primary else "secondary"
            ):
                callback = btn_config.get('callback')
                if callback and callable(callback):
                    callback()


def render_step_indicator(current_step, total_steps, step_titles=None):
    """
    Render a visual progress indicator for booking steps.
    
    Args:
        current_step: Current step number (1-indexed)
        total_steps: Total number of steps
        step_titles: Optional list of step names/titles
    
    Returns:
        None (renders directly to st)
    """
    indicator_html = '<div class="step-indicator">'
    
    for step_num in range(1, total_steps + 1):
        if step_num < current_step:
            status = "completed"
            symbol = "✓"
        elif step_num == current_step:
            status = "active"
            symbol = str(step_num)
        else:
            status = "pending"
            symbol = str(step_num)
        
        label = step_titles[step_num - 1] if step_titles and step_num <= len(step_titles) else f"Step {step_num}"
        
        indicator_html += f"""
        <div class="step-item">
            <div class="step-circle {status}">{symbol}</div>
            <div class="step-label {status}">{label}</div>
        </div>
        """
        
        if step_num < total_steps:
            connector_status = "active" if step_num < current_step else ""
            indicator_html += f'<div class="step-connector {connector_status}"></div>'
    
    indicator_html += "</div>"
    st.markdown(indicator_html, unsafe_allow_html=True)


# ==================== PHASE 1 REFACTORING COMPONENTS ====================

def render_section_header(emoji, title, subtitle, margin_bottom=Spacing.XL):
    """
    Render consistent section header for booking flow.
    
    Args:
        emoji: Emoji/icon to display
        title: Main title text
        subtitle: Subtitle/description text
        margin_bottom: Bottom margin spacing
    """
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: {margin_bottom};">
        <h1 style="
            margin: 0 0 {Spacing.MD} 0;
            color: {Colors.TEXT};
            font-size: {Typography.H2};
            font-weight: {Typography.BOLD};
        ">{emoji} {title}</h1>
        <p style="
            color: {Colors.TEXT_SECONDARY};
            margin: {Spacing.SM} 0 0 0;
            font-size: {Typography.BODY};
            line-height: 1.6;
        ">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_info_alert(message, alert_type="info", icon=None, title=None, margin_bottom=Spacing.LG):
    """
    Render styled info alert box with consistent design system colors.
    
    Args:
        message: Alert message text
        alert_type: 'info', 'success', 'warning', 'danger', 'payment'
        icon: Optional emoji/icon (auto-selected if not provided)
        title: Optional alert title
        margin_bottom: Bottom margin spacing
    """
    # Color and icon mapping
    type_config = {
        "info": {
            "bg": Gradients.OVERLAY_SUBTLE,
            "border": Colors.SECONDARY,
            "color": Colors.SECONDARY,
            "icon": "ℹ️"
        },
        "success": {
            "bg": "linear-gradient(135deg, rgba(34, 197, 94, 0.08) 0%, rgba(16, 163, 74, 0.05) 100%)",
            "border": Colors.SUCCESS,
            "color": Colors.SUCCESS,
            "icon": "✅"
        },
        "warning": {
            "bg": "linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(217, 119, 6, 0.05) 100%)",
            "border": Colors.WARNING,
            "color": Colors.WARNING,
            "icon": "⚠️"
        },
        "danger": {
            "bg": "linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(220, 38, 38, 0.05) 100%)",
            "border": Colors.DANGER,
            "color": Colors.DANGER,
            "icon": "❌"
        },
        "payment": {
            "bg": Gradients.CTA_PRIMARY,
            "border": Colors.DANGER,
            "color": Colors.WHITE,
            "icon": "💳"
        }
    }
    
    config = type_config.get(alert_type, type_config["info"])
    display_icon = icon or config["icon"]
    
    title_html = f'<p style="margin: 0 0 {Spacing.SM} 0; color: {config["color"]}; font-weight: {Typography.BOLD}; font-size: {Typography.SMALL};">{title}</p>' if title else ""
    
    st.markdown(f"""
    <div style="
        background: {config['bg']};
        padding: {Spacing.MD};
        border-radius: {BorderRadius.LG};
        border-left: 4px solid {config['border']};
        margin-bottom: {margin_bottom};
        text-align: center;
    ">
        {title_html}
        <p style="
            margin: 0;
            color: {Colors.TEXT if alert_type != 'payment' else Colors.WHITE};
            font-size: {Typography.BODY};
            line-height: 1.6;
            font-weight: {Typography.MEDIUM};
        ">{display_icon} {message}</p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label, value, delta=None, icon="📊", color=Colors.PRIMARY, size="medium"):
    """
    Render consistent metric card with design system styling.
    
    Args:
        label: Metric label text
        value: Metric value to display
        delta: Optional delta/change indicator
        icon: Emoji/icon for the metric
        color: Color for the metric accent (from Colors class)
        size: 'small', 'medium', or 'large'
    """
    size_config = {
        "small": {
            "icon_size": "32px",
            "label_size": Typography.SMALL,
            "value_size": Typography.H4,
            "padding": Spacing.MD
        },
        "medium": {
            "icon_size": "40px",
            "label_size": Typography.BODY,
            "value_size": Typography.H2,
            "padding": Spacing.LG
        },
        "large": {
            "icon_size": "48px",
            "label_size": Typography.H4,
            "value_size": "2.5rem",
            "padding": Spacing.XL
        }
    }
    
    config = size_config.get(size, size_config["medium"])
    
    delta_html = f"""
    <div style="
        margin-top: {Spacing.SM};
        font-size: {Typography.SMALL};
        color: {Colors.SUCCESS if str(delta).startswith('+') else Colors.DANGER};
        font-weight: {Typography.SEMIBOLD};
    ">{delta}</div>
    """ if delta else ""
    
    st.markdown(f"""
    <div style="
        background: {Gradients.CARD_SUBTLE};
        border: 2px solid {Colors.BORDER};
        border-radius: {BorderRadius.LG};
        padding: {config['padding']};
        box-shadow: {Shadows.MD}, {Shadows.INSET_SUBTLE};
        text-align: center;
        transition: all {Transitions.NORMAL};
    ">
        <div style="
            font-size: {config['icon_size']};
            margin-bottom: {Spacing.MD};
            display: inline-block;
        ">{icon}</div>
        <p style="
            margin: 0 0 {Spacing.SM} 0;
            font-size: {config['label_size']};
            color: {Colors.TEXT_SECONDARY};
            font-weight: {Typography.MEDIUM};
            text-transform: none;
            letter-spacing: 0;
            line-height: 1.4;
        ">{label}</p>
        <p style="
            margin: 0;
            font-size: {config['value_size']};
            font-weight: {Typography.BOLD};
            color: {color};
        ">{value}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


# ==================== LAYOUT RECONSTRUCTION COMPONENTS ====================

def apply_layout_css():
    """
    Apply refined CSS for premium SaaS layout.
    FOCUS: Structure, spacing, and hierarchy - NOT excessive effects.
    - Removes excessive glow and shadows
    - Standardizes vertical rhythm
    - Improves content centering
    - Fixes empty space issues
    - Enhances readability
    """
    st.markdown(f"""
    <style>
    /* ===== GLOBAL SPACING FIXES ===== */
    /* Reduce excessive vertical spacing between elements */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {{
        margin-bottom: {Spacing.SM} !important;
    }}
    
    /* Better spacing for containers */
    .main {{
        max-width: 1400px;
        margin: 0 auto;
        padding: {Spacing.LG} !important;
    }}
    
    /* ===== CONTENT CENTERING ===== */
    /* Center content columns properly */
    div[data-testid="column"] {{
        padding: 0 {Spacing.SM} !important;
    }}
    
    div[data-testid="column"]:first-child {{
        padding-left: 0 !important;
    }}
    
    div[data-testid="column"]:last-child {{
        padding-right: 0 !important;
    }}
    
    /* ===== REMOVE EXCESSIVE GLOW ===== */
    /* Tone down glowing effects - use subtle shadows instead */
    .stButton > button {{
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button:hover {{
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        transform: translateY(-1px) !important;
    }}
    
    /* ===== METRIC CARDS - REFINED ===== */
    [data-testid="metric-container"] {{
        background: {Colors.CARD} !important;
        border: 1px solid {Colors.BORDER} !important;
        border-radius: {BorderRadius.LG} !important;
        padding: {Spacing.MD} !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s ease !important;
    }}
    
    [data-testid="metric-container"]:hover {{
        border-color: {Colors.PRIMARY} !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-2px) !important;
    }}
    
    [data-testid="metric-container"]::before {{
        display: none !important;
    }}
    
    /* ===== TYPOGRAPHY REFINEMENT ===== */
    /* Tighter headings to reduce empty space */
    h1 {{
        margin: {Spacing.MD} 0 {Spacing.SM} 0 !important;
    }}
    
    h2 {{
        margin: {Spacing.MD} 0 {Spacing.SM} 0 !important;
        font-size: {Typography.H2} !important;
    }}
    
    h3 {{
        margin: {Spacing.MD} 0 {Spacing.SM} 0 !important;
    }}
    
    p {{
        margin: {Spacing.SM} 0 !important;
        line-height: 1.5 !important;
    }}
    
    /* ===== SECTION DIVIDERS ===== */
    hr {{
        border: none !important;
        border-top: 1px solid {Colors.BORDER} !important;
        margin: {Spacing.MD} 0 !important;
    }}
    
    /* ===== INPUT REFINEMENT ===== */
    /* Cleaner input styling - less visual noise */
    input, textarea, [role="textbox"] {{
        background-color: {Colors.CARD} !important;
        border: 1px solid {Colors.BORDER} !important;
        border-radius: {BorderRadius.MD} !important;
        padding: {Spacing.SM} {Spacing.MD} !important;
        transition: all 0.15s ease !important;
    }}
    
    input:focus, textarea:focus {{
        border-color: {Colors.PRIMARY} !important;
        box-shadow: 0 0 0 2px {rgb_to_rgba(Colors.PRIMARY, 0.1)} !important;
    }}
    
    /* ===== BUTTONS - CONSISTENT SIZING ===== */
    .stButton > button {{
        height: auto !important;
        padding: {Spacing.SM} {Spacing.LG} !important;
        font-weight: {Typography.SEMIBOLD} !important;
        border-radius: {BorderRadius.MD} !important;
        border: none !important;
    }}
    
    /* ===== EXPANDABLE SECTIONS ===== */
    .streamlit-expanderHeader {{
        background-color: {Colors.CARD} !important;
        border-radius: {BorderRadius.MD} !important;
        padding: {Spacing.MD} {Spacing.LG} !important;
    }}
    
    .streamlit-expanderHeader:hover {{
        background-color: {Colors.CARD_HOVER} !important;
    }}
    
    /* ===== CODE BLOCKS ===== */
    pre, code {{
        background-color: {Colors.BACKGROUND} !important;
        border: 1px solid {Colors.BORDER} !important;
        border-radius: {BorderRadius.SM} !important;
        padding: {Spacing.MD} !important;
        font-family: 'Monaco', 'Courier New', monospace !important;
    }}
    
    /* ===== SCROLLBAR STYLING ===== */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {Colors.BACKGROUND};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {Colors.BORDER};
        border-radius: {BorderRadius.SM};
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {Colors.PRIMARY};
    }}
    
    </style>
    """, unsafe_allow_html=True)


def apply_calendar_refinement():
    """
    Apply refined styling for calendar and appointment blocks.
    Improves readability and visual hierarchy without excessive effects.
    """
    st.markdown(f"""
    <style>
    /* ===== CALENDAR TABLE STYLING ===== */
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: {Spacing.LG} 0;
        background: {Colors.CARD};
        border-radius: {BorderRadius.MD};
        overflow: hidden;
        border: 1px solid {Colors.BORDER};
    }}
    
    th {{
        background: {Colors.CARD_HOVER};
        color: {Colors.TEXT};
        padding: {Spacing.MD};
        text-align: left;
        font-weight: {Typography.BOLD};
        border-bottom: 2px solid {Colors.BORDER};
        font-size: {Typography.SMALL};
        text-transform: none;
        letter-spacing: 0;
    }}
    
    td {{
        padding: {Spacing.MD};
        border: 1px solid {Colors.BORDER};
        font-size: {Typography.BODY};
        color: {Colors.TEXT};
        vertical-align: top;
        background: {Colors.CARD};
    }}
    
    tr:hover td {{
        background: {rgb_to_rgba(Colors.PRIMARY, 0.05)};
    }}
    
    /* ===== APPOINTMENT CELL STYLING ===== */
    .appointment-cell {{
        background: {Gradients.PRIMARY_BUTTON};
        color: {Colors.WHITE};
        border-radius: {BorderRadius.SM};
        padding: {Spacing.SM};
        margin: {Spacing.SM} 0;
        font-size: {Typography.SMALL};
        font-weight: {Typography.SEMIBOLD};
        border: 1px solid {rgb_to_rgba(Colors.PRIMARY_DARK, 0.3)};
    }}
    
    .appointment-cell:hover {{
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        transform: translateY(-1px);
    }}
    
    </style>
    """, unsafe_allow_html=True)


def render_premium_card(content_html, on_hover_lift=True):
    """
    Render a premium card wrapper with consistent styling.
    
    Args:
        content_html: HTML content to display inside the card
        on_hover_lift: Whether to add lift effect on hover
    """
    hover_class = "premium-card" if on_hover_lift else ""
    st.markdown(f"""
    <div class="{hover_class}" style="
        background: {Colors.CARD};
        border: 1px solid {Colors.BORDER};
        border-radius: {BorderRadius.LG};
        padding: {Spacing.LG};
        margin-bottom: {Spacing.LG};
        transition: all 0.3s ease;
    ">
        {content_html}
    </div>
    """, unsafe_allow_html=True)


def render_section_block(title, subtitle="", content_callback=None, emoji=""):
    """
    Render a standardized section block with title, subtitle, and content area.
    
    Args:
        title: Section title
        subtitle: Optional subtitle/description
        content_callback: Callback function that renders content (will be called within the section)
        emoji: Optional emoji to prepend to title
    """
    title_text = f"{emoji} {title}" if emoji else title
    
    st.markdown(f"""
    <div class="section-block">
        <h2 class="section-title">{title_text}</h2>
        {f'<p class="section-subtitle">{subtitle}</p>' if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)
    
    if content_callback:
        content_callback()


def render_sidebar_section(title, items, active_item=None):
    """
    Render a sidebar section with navigation items.
    
    Args:
        title: Section title
        items: List of (label, key, icon) tuples
        active_item: Current active item key
    """
    st.markdown(f"""
    <div class="sidebar-section">
        <h4 style="margin: 0 0 {Spacing.MD} 0; color: {Colors.TEXT}; font-size: {Typography.SMALL}; font-weight: {Typography.SEMIBOLD}; text-transform: none; letter-spacing: 0;">
            {title}
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    for label, key, icon in items:
        is_active = key == active_item
        st.markdown(f"""
        <div class="sidebar-item {'active' if is_active else ''}" style="
            background: {'linear-gradient(135deg, ' + Colors.PRIMARY + ' 0%, ' + Colors.PRIMARY_DARK + ' 100%)' if is_active else Colors.CARD_HOVER};
            color: {'white' if is_active else Colors.TEXT};
            border-left: 4px solid {Colors.SECONDARY if is_active else 'transparent'};
            padding: {Spacing.MD} {Spacing.LG};
            padding-left: {('calc(' + Spacing.LG + ' - 4px)') if is_active else Spacing.LG};
            margin-bottom: {Spacing.SM};
            cursor: pointer;
            border-radius: {BorderRadius.SM};
            transition: all 0.2s ease;
        ">
            <span>{icon}</span> <span style="margin-left: {Spacing.SM}; font-weight: {'bold' if is_active else 'normal'};">{label}</span>
        </div>
        """, unsafe_allow_html=True)


def render_calendar_wrapper():
    """
    Render a styled calendar wrapper with proper spacing and borders.
    """
    return f"""
    <div class="calendar-wrapper" style="
        background: {Colors.CARD};
        border: 1px solid {Colors.BORDER};
        border-radius: {BorderRadius.LG};
        padding: {Spacing.LG};
        margin-bottom: {Spacing.LG};
    ">
    """


def render_appointment_block(time, service, barber, duration, status="scheduled"):
    """
    Render a premium appointment block in calendar view.
    
    Args:
        time: Appointment time string (e.g., "2:30 PM")
        service: Service name
        barber: Barber name
        duration: Duration in minutes
        status: Appointment status
    """
    status_colors = {
        "scheduled": Colors.PRIMARY,
        "confirmed": Colors.SUCCESS,
        "completed": Colors.TEXT_SECONDARY,
        "cancelled": Colors.DANGER
    }
    
    color = status_colors.get(status, Colors.PRIMARY)
    
    st.markdown(f"""
    <div class="appointment-block" style="
        background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
        color: {Colors.WHITE};
        border-radius: {BorderRadius.MD};
        padding: {Spacing.MD};
        margin: {Spacing.SM} 0;
        box-shadow: {Shadows.SM};
        border-left: 4px solid {Colors.SECONDARY};
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <p style="margin: 0; font-size: {Typography.SMALL}; opacity: 0.9;">⏰ {time}</p>
                <p style="margin: {Spacing.SM} 0 0 0; font-size: {Typography.BODY}; font-weight: bold;">✂️ {service}</p>
                <p style="margin: {Spacing.SM} 0 0 0; font-size: {Typography.SMALL}; opacity: 0.85;">👤 {barber} • {duration} min</p>
            </div>
            <div style="font-size: {Typography.TINY}; opacity: 0.8; text-transform: none; font-weight: {Typography.SEMIBOLD};">
                {status.title()}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
