# Design System - Quick Reference Card

## Color Constants
```python
from design_system import Colors

Colors.PRIMARY              # Purple #7c3aed
Colors.SECONDARY            # Cyan #06b6d4
Colors.SUCCESS              # Green #22c55e
Colors.WARNING              # Amber #f59e0b
Colors.DANGER               # Red #ef4444
Colors.BACKGROUND           # Dark blue #0f172a
Colors.CARD                 # Dark slate #1e293b
Colors.CARD_HOVER           # Lighter slate #334155
Colors.BORDER               # Subtle borders #334155
Colors.TEXT                 # Main text #f1f5f9
Colors.TEXT_SECONDARY       # Muted text #cbd5e1
Colors.TEXT_TERTIARY        # Lighter text #94a3b8
```

## Typography
```python
from design_system import Typography

Typography.H1               # 2.5rem (40px)
Typography.H2               # 2rem (32px)
Typography.H3               # 1.5rem (24px)
Typography.BODY             # 1rem (16px)
Typography.SMALL            # 0.875rem (14px)
Typography.TINY             # 0.75rem (12px)
```

## Spacing
```python
from design_system import Spacing

Spacing.XS                  # 4px
Spacing.SM                  # 8px
Spacing.MD                  # 16px
Spacing.LG                  # 24px
Spacing.XL                  # 32px
Spacing.XXL                 # 48px
```

## Component Usage

### Section Titles
```python
render_section_title("📊 Dashboard", subtitle="Your subtitle")
```

### Stat Boxes (KPIs)
```python
render_stat_box("Reservas", "42", "📅", color=Colors.PRIMARY)
```

### Alerts
```python
render_alert("Success!", alert_type="success", title="✅ Éxito")
render_alert("Warning!", alert_type="warning")
render_alert("Error!", alert_type="error")
render_alert("Info", alert_type="info")
```

### Cards
```python
render_card(
    content=lambda: st.write("Content here"),
    title="Card Title",
    class_name="premium-card"
)
```

### Badges
```python
render_badge("Success", badge_type="primary")
render_badge("Confirmed", badge_type="success")
render_badge("Pending", badge_type="warning")
render_badge("Cancelled", badge_type="danger")
```

### Dividers
```python
render_divider()
render_divider(color=Colors.PRIMARY, height="3px")
```

### Subsection Titles
```python
render_subsection_title("📈 Metrics")
```

## CSS Classes

### Card Containers
```html
<div class="card-container">Your content</div>
<div class="premium-card">Premium content</div>
```

### Text Styles
```html
<div class="section-title">Section Title</div>
<div class="subsection-title">Subsection Title</div>
<span class="badge">Badge</span>
<span class="badge-success">Success</span>
```

## Animations
```css
.fade-in          /* Fade animation */
.slide-in         /* Slide up animation */
```

## Common Patterns

### Dashboard Layout
```python
render_section_title("📊 Dashboard", subtitle="Overview")

col1, col2, col3 = st.columns(3, gap="large")
with col1:
    render_stat_box("Label", "42", "🎯", Colors.PRIMARY)
with col2:
    render_stat_box("Label", "18", "👥", Colors.SECONDARY)
with col3:
    render_stat_box("Label", "$480", "💰", Colors.SUCCESS)

render_divider()

render_subsection_title("📋 Details")
# Your content here
```

### Info Card
```python
render_alert(
    "User registered successfully",
    alert_type="success",
    title="✅ Registration Complete"
)
```

### Metric Rows
```python
col1, col2, col3, col4 = st.columns(4, gap="large")
with col1:
    render_stat_box("Reservas", "24", "📅", Colors.PRIMARY)
with col2:
    render_stat_box("Clientes", "18", "👥", Colors.SECONDARY)
with col3:
    render_stat_box("Ingresos", "$480", "💰", Colors.SUCCESS)
with col4:
    render_stat_box("Barberos", "3", "✂️", Colors.WARNING)
```

## Utility Functions

### Get Gradient
```python
from design_system import get_gradient

gradient = get_gradient(Colors.PRIMARY, Colors.SECONDARY)
# Returns: "linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%)"
```

### Hex to RGBA
```python
from design_system import rgb_to_rgba

rgba = rgb_to_rgba(Colors.PRIMARY, alpha=0.1)
# Returns: "rgba(124, 58, 237, 0.1)"
```

## Best Practices

✅ **Always use** color constants from `Colors` class
✅ **Always use** spacing constants from `Spacing` class
✅ **Use** `render_*` functions for consistency
✅ **Use** `BorderRadius.*` for all rounded corners
✅ **Use** `Transitions.*` for animations

❌ **Never** hardcode hex colors
❌ **Never** use random spacing values
❌ **Never** mix design systems

## Responsive Grid

```python
# 2 Column
col1, col2 = st.columns(2, gap="large")

# 3 Column
col1, col2, col3 = st.columns(3, gap="large")

# 4 Column
col1, col2, col3, col4 = st.columns(4, gap="large")

# 5 Column (for super admin)
col1, col2, col3, col4, col5 = st.columns(5, gap="large")
```

## Default Implementation

All Streamlit components automatically use the design system:
- Buttons ✅
- Inputs ✅
- Selects ✅
- Dataframes ✅
- Expanders ✅
- Tabs ✅
- Alerts ✅

## Need to Customize?

Edit `design_system.py`:
1. Modify `Colors` class for colors
2. Modify `Typography` class for fonts
3. Modify CSS in `apply_global_theme()` for styles
4. Create new `render_*` functions for components

## File Structure
```
barberia_app/
├── app.py                      # Main app (uses design system)
├── design_system.py            # Design system definitions
├── DESIGN_SYSTEM_GUIDE.md      # Full integration guide
└── DESIGN_SYSTEM_QRC.md        # This file
```

## Quick Test
Add this to your app to preview the design system:

```python
if st.sidebar.checkbox("Show Design System Preview"):
    render_header()
    render_section_title("Design System Components")
    
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        render_stat_box("Components", "42", "🎨", Colors.PRIMARY)
    with col2:
        render_stat_box("Colors", "14", "🎭", Colors.SECONDARY)
    with col3:
        render_stat_box("Utilities", "∞", "⚙️", Colors.SUCCESS)
    
    render_divider()
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_alert("All set!", alert_type="success", title="✅ Design Ready")
    with col2:
        render_alert("Start building!", alert_type="info", title="Let's go!")
```

---

**Last Updated:** Design System Integration Complete
**Status:** Ready for Production
