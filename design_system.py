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


# ==================== GLOBAL CSS ====================
def apply_global_theme():
    """Apply global CSS theme to the Streamlit app"""
    css = f"""
    <style>
        /* ==================== ROOT STYLES ==================== */
        :root {{
            --primary: {Colors.PRIMARY};
            --secondary: {Colors.SECONDARY};
            --success: {Colors.SUCCESS};
            --warning: {Colors.WARNING};
            --danger: {Colors.DANGER};
            --background: {Colors.BACKGROUND};
            --card: {Colors.CARD};
            --border: {Colors.BORDER};
            --text: {Colors.TEXT};
            --text-secondary: {Colors.TEXT_SECONDARY};
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
    button_key = f"barber_card_{barber_id}_{barber_name.replace(' ', '_')}"
    card_class = f"barber-card-{barber_id.replace(' ', '_').replace('-', '_').lower()}"
    
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
        @keyframes barber-check-pulse {{
            0% {{
                transform: scale(0.8);
                opacity: 0;
            }}
            50% {{
                transform: scale(1.15);
            }}
            100% {{
                transform: scale(1);
                opacity: 1;
            }}
        }}
        
        @keyframes barber-icon-float {{
            0%, 100% {{
                transform: translateY(0px);
            }}
            50% {{
                transform: translateY(-3px);
            }}
        }}
        
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
            transform: translateY(0px) scale(1);
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
            transform: translateY(-2px) scale(1.03);
            border-color: {Colors.PRIMARY};
            box-shadow: {Shadows.LG}, {Shadows.INSET_SUBTLE}, {Shadows.GLOW_SOFT};
            background: {Gradients.CARD_HOVER};
        }}
        
        .{card_class}:active {{
            transform: scale(0.97) translateY(0px);
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
            animation: barber-icon-float 3s ease-in-out infinite;
        }}
        
        .{card_class}:hover .barber-icon-container {{
            animation: barber-icon-float 2s ease-in-out infinite;
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
            text-transform: none;
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
            animation: barber-check-pulse 0.4s ease-out;
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
    
    # Render chips container
    st.markdown(f'<div class="time-chips-container">', unsafe_allow_html=True)
    
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
                    transform: scale(1.05);
                    border-color: {Colors.PRIMARY};
                    background-color: {"linear-gradient(135deg, " + Colors.PRIMARY + " 0%, " + Colors.PRIMARY_DARK + " 100%)" if is_selected else rgb_to_rgba(Colors.PRIMARY, 0.08)};
                    box-shadow: {Shadows.MD}, {Shadows.GLOW_SOFT};
                }}
                
                .chip-btn-{idx}:active {{
                    transform: scale(0.97);
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return selected


# ==================== SAAS LAYOUT WRAPPERS ====================

def render_booking_container(content_func=None):
    """
    Create a centered container for the booking flow (SaaS style).
    
    Features:
    - Max-width 800px for optimal readability
    - Centered with equal margins
    - Clean, professional appearance
    - Consistent padding
    
    Args:
        content_func: Optional function to call inside container
    
    Returns:
        None (renders directly to st)
    """
    st.markdown(
        f"""
        <style>
            .booking-container {{
                max-width: 800px;
                margin: 0 auto;
                padding: {Spacing.XL} 0;
            }}
        </style>
        <div class="booking-container">
        """,
        unsafe_allow_html=True
    )
    
    if content_func and callable(content_func):
        content_func()


def close_booking_container():
    """Close the booking container div."""
    st.markdown("</div>", unsafe_allow_html=True)


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
    header_html = f"""
    <div style="
        text-align: center;
        margin-bottom: {Spacing.XXL};
        padding-bottom: {Spacing.XL};
        border-bottom: 1px solid {Colors.BORDER};
    ">
        <h1 style="
            font-size: {Typography.H1};
            font-weight: {Typography.BOLD};
            color: {Colors.TEXT};
            margin: 0 0 {Spacing.MD} 0;
        ">{title}</h1>
    """
    
    if subtitle:
        header_html += f"""
        <p style="
            font-size: {Typography.BODY};
            color: {Colors.TEXT_SECONDARY};
            margin: 0 0 {Spacing.LG} 0;
            line-height: 1.6;
        ">{subtitle}</p>
        """
    
    if step and total_steps:
        header_html += f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: {Spacing.SM};
            margin-top: {Spacing.MD};
        ">
            <span style="
                font-size: {Typography.SMALL};
                color: {Colors.PRIMARY};
                font-weight: {Typography.BOLD};
            ">Paso {step}</span>
            <span style="
                color: {Colors.TEXT_TERTIARY};
            ">de {total_steps}</span>
        </div>
        """
    
    header_html += "</div>"
    st.markdown(header_html, unsafe_allow_html=True)


def render_booking_section(title=None, content_func=None):
    """
    Render a booking flow section with consistent spacing and styling.
    
    Args:
        title: Optional section title
        content_func: Optional function to call inside section
    
    Returns:
        None (renders directly to st)
    """
    section_html = f"""
    <div style="
        background: {Gradients.CARD_SUBTLE};
        border: 1px solid {Colors.BORDER};
        border-radius: {BorderRadius.LG};
        padding: {Spacing.XL};
        margin-bottom: {Spacing.XL};
        box-shadow: {Shadows.MD}, {Shadows.INSET_SUBTLE};
    ">
    """
    
    if title:
        section_html += f"""
        <h2 style="
            font-size: {Typography.H3};
            font-weight: {Typography.SEMIBOLD};
            color: {Colors.TEXT};
            margin: 0 0 {Spacing.LG} 0;
            padding-bottom: {Spacing.MD};
            border-bottom: 2px solid {rgb_to_rgba(Colors.PRIMARY, 0.2)};
        ">{title}</h2>
        """
    
    section_html += "</div>"
    st.markdown(section_html, unsafe_allow_html=True)
    
    if content_func and callable(content_func):
        content_func()
    
    # Note: Caller should close this with a matching </div> if needed
    return section_html


def render_form_group(label, input_func=None, help_text=None, error_text=None):
    """
    Render a form input group with label and optional help/error text.
    
    Args:
        label: Form field label
        input_func: Function that renders the input (e.g., st.text_input)
        help_text: Optional helper text
        error_text: Optional error message
    
    Returns:
        None (renders directly to st)
    """
    group_html = f"""
    <div style="
        margin-bottom: {Spacing.LG};
    ">
        <label style="
            display: block;
            font-size: {Typography.SMALL};
            font-weight: {Typography.SEMIBOLD};
            color: {Colors.TEXT};
            margin-bottom: {Spacing.SM};
            text-transform: none;
            letter-spacing: 0;
        ">{label}</label>
    """
    
    st.markdown(group_html, unsafe_allow_html=True)
    
    if input_func and callable(input_func):
        input_func()
    
    if help_text:
        st.markdown(
            f"""
            <p style="
                font-size: {Typography.TINY};
                color: {Colors.TEXT_TERTIARY};
                margin: {Spacing.SM} 0 0 0;
            ">{help_text}</p>
            """,
            unsafe_allow_html=True
        )
    
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
    
    st.markdown("</div>", unsafe_allow_html=True)


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
    indicator_html = """<style>
        .step-indicator {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            gap: 8px;
        }
        
        .step-item {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }
        
        .step-circle {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
            transition: all 0.3s ease-in-out;
        }
        
        .step-circle.active {
            background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
            color: white;
            box-shadow: 0 0 20px rgba(124, 58, 237, 0.3);
        }
        
        .step-circle.completed {
            background: #22c55e;
            color: white;
        }
        
        .step-circle.pending {
            background: #334155;
            color: #cbd5e1;
            border: 2px solid #475569;
        }
        
        .step-connector {
            flex: 1;
            height: 2px;
            background: #334155;
            margin-top: 22px;
        }
        
        .step-connector.active {
            background: #7c3aed;
        }
        
        .step-label {
            font-size: 12px;
            color: #cbd5e1;
            text-align: center;
            max-width: 80px;
        }
        
        .step-label.active {
            color: #7c3aed;
            font-weight: 600;
        }
    </style>
    
    <div class="step-indicator">
    """
    
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


def render_booking_container():
    """
    Render a centered container for booking flow steps.
    Returns a container context manager for consistent booking flow spacing.
    """
    from contextlib import contextmanager
    
    @contextmanager
    def booking_container():
        """Context manager for booking step styling."""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="
                background: {Colors.CARD};
                border: 1px solid {Colors.BORDER};
                border-radius: {BorderRadius.LG};
                padding: {Spacing.XL};
                margin: {Spacing.LG} 0;
            ">
            """, unsafe_allow_html=True)
            yield
            st.markdown("</div>", unsafe_allow_html=True)
    
    return booking_container()


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
