# Layout Reconstruction - New Functions Reference

## Quick API Reference

### Global CSS Functions

#### `apply_layout_css()`
Applies comprehensive CSS refinements for premium SaaS structure.

```python
from design_system import apply_layout_css

# Call once at app startup
apply_layout_css()
```

**What it does:**
- Refines global spacing (reduces excessive empty space)
- Removes excessive glow effects
- Standardizes button and input styling
- Improves visual hierarchy
- Sets up responsive behavior

---

#### `apply_calendar_refinement()`
Specialized CSS for calendar and table displays.

```python
from design_system import apply_calendar_refinement

# Call once at app startup
apply_calendar_refinement()
```

**What it does:**
- Styles calendar tables with proper borders
- Formats appointment cells
- Improves readability
- Sets hover effects

---

### Layout Container Components

#### `render_premium_card(content_html, on_hover_lift=True)`
Wraps HTML content in a premium card with consistent styling.

```python
from design_system import render_premium_card

# Render a card with any HTML content
card = render_premium_card(
    content_html="<h3>Service Name</h3><p>Details...</p>",
    on_hover_lift=True  # Subtle 2px lift on hover
)
st.markdown(card, unsafe_allow_html=True)
```

**Parameters:**
- `content_html` (str): HTML content to wrap
- `on_hover_lift` (bool, default=True): Whether to add hover lift effect

**Output:** Premium card with:
- Subtle 1px border
- Rounded corners (8px)
- Consistent padding (20px)
- Soft shadow (0 2px 8px)

---

#### `render_section_block(title, subtitle, content_callback, emoji="")`
Renders a standardized section with title, subtitle, and callback content.

```python
from design_system import render_section_block

def my_content():
    st.write("Section content here")
    st.metric("Label", 100)

render_section_block(
    title="Dashboard Overview",
    subtitle="Your business metrics",
    content_callback=my_content,
    emoji="📊"
)
```

**Parameters:**
- `title` (str): Section heading
- `subtitle` (str): Descriptive subtitle
- `content_callback` (callable): Function that renders content
- `emoji` (str): Leading emoji icon

**Output:** Section with:
- Emoji + title + subtitle header
- Content area with consistent padding
- Proper spacing separation
- Card-style container

---

#### `render_sidebar_section(title, items, active_item=None)`
Renders a premium sidebar navigation section.

```python
from design_system import render_sidebar_section

render_sidebar_section(
    title="Navigation",
    items=["Dashboard", "Bookings", "Barbers", "Analytics"],
    active_item="Dashboard"
)
```

**Parameters:**
- `title` (str): Section title
- `items` (list): Navigation item names
- `active_item` (str, optional): Currently active item

**Output:** Sidebar with:
- Clear section title
- Clickable items
- Active state highlighting (colored background)
- Consistent spacing

---

#### `render_booking_container()` / `close_booking_container()`
Context manager for booking flow steps - ensures consistency.

```python
from design_system import render_booking_container, close_booking_container
from contextlib import contextmanager

# Option 1: Using context manager
with render_booking_container():
    st.write("Step 1 content...")
    # Everything inside gets styled as a booking step

# Option 2: Manual control
render_booking_container()
st.write("Step content...")
close_booking_container()
```

**Output for each step:**
- Max-width container (900px, centered)
- Card styling
- Consistent padding (40px)
- Dark background (Colors.CARD)
- Border styling

---

#### `render_calendar_wrapper()`
Returns HTML for a properly styled calendar container.

```python
from design_system import render_calendar_wrapper

st.markdown(render_calendar_wrapper(), unsafe_allow_html=True)
# Then render your calendar content here
```

**Output:** Container styled for:
- Calendar tables
- Appointment listings
- Date grids

---

#### `render_appointment_block(time, service, barber, duration, status="scheduled")`
Renders a single appointment in premium style.

```python
from design_system import render_appointment_block

render_appointment_block(
    time="2:30 PM",
    service="Corte Clásico",
    barber="Juan García",
    duration=30,
    status="scheduled"  # Options: scheduled, completed, cancelled
)
```

**Parameters:**
- `time` (str): Appointment time
- `service` (str): Service name
- `barber` (str): Barber name
- `duration` (int): Duration in minutes
- `status` (str): Status for coloring

**Output:** Premium appointment display with:
- Color-coded status indicator
- Organized information layout
- Consistent styling

---

## Integration Checklist

- [ ] Import new functions in app.py
- [ ] Add `apply_layout_css()` call after `apply_global_theme()`
- [ ] Add `apply_calendar_refinement()` call right after `apply_layout_css()`
- [ ] Replace booking flow headers with `render_section_header()`
- [ ] Wrap booking steps with `render_booking_container()`
- [ ] Update home screen with `render_section_block()`
- [ ] Apply `render_sidebar_section()` to navigation
- [ ] Update appointment displays with `render_appointment_block()`
- [ ] Test full app with `streamlit run app.py`
- [ ] Verify premium SaaS look and feel
- [ ] Check mobile responsiveness

---

## Color Tokens Reference

Use these semantic colors from the design system:

```python
from design_system import Colors

# Text
Colors.TEXT              # Primary text (#f1f5f9)
Colors.TEXT_SECONDARY    # Secondary text (#cbd5e1)
Colors.TEXT_TERTIARY     # Muted text (#94a3b8)

# Semantic
Colors.SUCCESS           # Green (#22c55e)
Colors.DANGER            # Red (#ef4444)
Colors.WARNING           # Orange (#f97316)
Colors.INFO              # Blue (#3b82f6)
Colors.PRIMARY           # Purple (#7c3aed)
Colors.SECONDARY         # Cyan (#06b6d4)

# UI
Colors.CARD              # Dark card (#1e293b)
Colors.CARD_HOVER        # Card hover (#334155)
Colors.BORDER            # Subtle border (#334155)
Colors.DIVIDER           # Light divider (#475569)
```

---

## Spacing Tokens Reference

```python
from design_system import Spacing

Spacing.XS               # 4px
Spacing.SM               # 8px
Spacing.MD               # 12px
Spacing.LG               # 16px (standard)
Spacing.XL               # 24px
Spacing.XXL              # 32px (sections)
```

---

## Typography Tokens Reference

```python
from design_system import Typography

Typography.H1            # Page title (32px, 700)
Typography.H2            # Section heading (24px, 600)
Typography.H3            # Subsection (20px, 600)
Typography.H4            # Card title (16px, 600)
Typography.BODY          # Regular text (14px, 400)
Typography.SMALL         # Small text (12px, 400)
Typography.TINY          # Tiny text (10px, 400)
```

---

## Testing the Integration

```python
# Quick test script
from design_system import (
    apply_layout_css,
    apply_calendar_refinement,
    render_section_block,
    render_premium_card,
)
import streamlit as st

st.set_page_config(layout="wide")

# Apply styles
apply_layout_css()
apply_calendar_refinement()

# Test section block
def test_content():
    st.info("This is a test section")

render_section_block(
    title="Test Section",
    subtitle="Testing layout functions",
    content_callback=test_content,
    emoji="✨"
)

# Test premium card
st.markdown(render_premium_card(
    "<h3>Premium Card</h3><p>This is a test card</p>"
), unsafe_allow_html=True)

st.success("Layout reconstruction functions working!")
```

---

## Common Patterns

### Pattern 1: Centered Content Block
```python
with render_booking_container():
    render_section_header("✂️", "Title", "Subtitle")
    # Content here
```

### Pattern 2: Dashboard Section
```python
render_section_block(
    title="Dashboard",
    subtitle="Overview",
    content_callback=lambda: (
        st.metric("Appointments", 42),
        st.metric("Revenue", "$1,200")
    ),
    emoji="📊"
)
```

### Pattern 3: Sidebar Navigation
```python
render_sidebar_section(
    title="Menu",
    items=["Home", "Bookings", "Settings"],
    active_item="Home"
)
```

---

## Design Principles

✅ **Consistency**: All components use same color/spacing/typography
✅ **Hierarchy**: Clear size and weight differentiation
✅ **Whitespace**: Proper spacing reduces cognitive load
✅ **Premium**: Subtle effects, not excessive glow
✅ **Responsive**: Mobile-friendly layouts
✅ **Accessible**: Sufficient contrast ratios

