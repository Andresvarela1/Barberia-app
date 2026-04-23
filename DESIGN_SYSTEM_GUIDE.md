# Design System Integration Guide

## Overview
The `design_system.py` file provides a complete, modern design system for your Barberia app. All UI elements share a consistent visual identity with:
- **Unified color palette** (purple, cyan, dark theme)
- **Responsive typography** (H1-H6, body, captions)
- **Professional shadows and transitions**
- **Reusable component builders**

## Quick Start

### 1. Import the Design System
At the top of `app.py`, add:

```python
from design_system import (
    apply_global_theme,
    Colors,
    Typography,
    Spacing,
    render_card,
    render_section_title,
    render_badge,
    render_stat_box,
    render_alert,
    render_header,
    get_gradient,
)
```

### 2. Apply Global Theme
In your main app initialization (after `st.set_page_config()`), add:

```python
st.set_page_config(
    page_title="Barberia App",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global design system
apply_global_theme()
```

### 3. Use Components Throughout Your App

## Component Examples

### Section Titles
```python
render_section_title("📊 Dashboard", subtitle="Bienvenido a tu panel de control")
```

### Cards
```python
def card_content():
    st.write("Your content here")

render_card(card_content, title="Mis Reservas", class_name="premium-card")
```

### Statistics Boxes
```python
col1, col2, col3 = st.columns(3)
with col1:
    render_stat_box("Reservas Hoy", "12", "📅", color=Colors.PRIMARY)
with col2:
    render_stat_box("Pagadas", "10", "✅", color=Colors.SUCCESS)
with col3:
    render_stat_box("Pendientes", "2", "⏳", color=Colors.WARNING)
```

### Badges
```python
render_badge("Premium", badge_type="primary")
render_badge("Confirmado", badge_type="success")
render_badge("Cancelado", badge_type="danger")
```

### Alerts
```python
render_alert("Reserva creada exitosamente", alert_type="success", title="¡Éxito!")
render_alert("Este horario ya está ocupado", alert_type="warning", title="Aviso")
render_alert("Error al guardar los cambios", alert_type="error", title="Error")
render_alert("Tu barbero confirmó la cita", alert_type="info")
```

### Custom Dividers
```python
from design_system import render_divider
render_divider()  # Default divider
render_divider(color=Colors.PRIMARY, height="3px")  # Custom color
```

## Color Usage

### In Text
```python
st.markdown(f"<p style='color: {Colors.PRIMARY};'>Texto principal</p>", unsafe_allow_html=True)
st.markdown(f"<p style='color: {Colors.SUCCESS};'>Texto de éxito</p>", unsafe_allow_html=True)
```

### In Custom Containers
```python
st.markdown(f"""
<div style="
    background-color: {Colors.CARD};
    border-left: 4px solid {Colors.PRIMARY};
    padding: {Spacing.LG};
    border-radius: {BorderRadius.LG};
">
    Tu contenido aquí
</div>
""", unsafe_allow_html=True)
```

## Dashboard Example

```python
from design_system import apply_global_theme, render_section_title, render_stat_box, render_card

# Apply theme at startup
apply_global_theme()

# Render header
render_header()

# Section title
render_section_title("📊 Panel de Control", subtitle="Visualiza tus métricas en tiempo real")

# Metrics row
col1, col2, col3, col4 = st.columns(4, gap="large")
with col1:
    render_stat_box("Reservas", "24", "📅", color=Colors.PRIMARY)
with col2:
    render_stat_box("Clientes", "18", "👥", color=Colors.SECONDARY)
with col3:
    render_stat_box("Ingresos", "$480", "💰", color=Colors.SUCCESS)
with col4:
    render_stat_box("Barberos", "3", "✂️", color=Colors.WARNING)

# Card section
render_section_title("📋 Próximas Citas")
render_card(
    title="Hoy",
    content=lambda: st.write("Mostrar lista de citas"),
    class_name="premium-card"
)
```

## Typography Classes

Use these for consistent text sizing:

```python
st.markdown(f"""
<h1 style="font-size: {Typography.H1};">Main Title</h1>
<h2 style="font-size: {Typography.H2};">Section Title</h2>
<p style="font-size: {Typography.BODY}; color: {Colors.TEXT};">Body text</p>
<p style="font-size: {Typography.SMALL}; color: {Colors.TEXT_SECONDARY};">Small text</p>
<p style="font-size: {Typography.TINY}; color: {Colors.TEXT_TERTIARY};">Tiny caption</p>
""", unsafe_allow_html=True)
```

## Spacing Constants

Use these for consistent margins and padding:

```python
# XS (4px), SM (8px), MD (16px), LG (24px), XL (32px), XXL (48px)
st.markdown(f"<div style='margin-bottom: {Spacing.LG};'>Content</div>", unsafe_allow_html=True)
```

## Button Styling

Buttons automatically use the design system CSS:

```python
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("✅ Confirmar", use_container_width=True):
        st.success("Confirmado")

with col2:
    if st.button("❌ Cancelar", use_container_width=True):
        st.warning("Cancelado")

with col3:
    if st.button("🔄 Reintentar", use_container_width=True):
        st.rerun()
```

## Migration Path

### Phase 1: Global Theme
1. Add `from design_system import apply_global_theme`
2. Call `apply_global_theme()` at startup
3. All UI elements now use the unified color scheme

### Phase 2: Component Replacement
1. Replace dashboard sections with `render_section_title()` and `render_stat_box()`
2. Wrap cards with `render_card()`
3. Replace custom alerts with `render_alert()`

### Phase 3: Consistency
1. All text uses `Colors.TEXT` and `Colors.TEXT_SECONDARY`
2. All containers use `Colors.CARD` background
3. All accents use `Colors.PRIMARY`

## Customization

### Change Primary Color
Edit `design_system.py` Colors class:
```python
PRIMARY = "#your-color-here"
```

### Add Custom Component
```python
def render_custom_component(data):
    st.markdown(f"""
    <div class="card-container">
        <!-- Your HTML here -->
    </div>
    """, unsafe_allow_html=True)
```

### Extend Typography
```python
class Typography:
    H7 = "1rem"
    DISPLAY = "3.5rem"  # Display size
```

## Best Practices

1. ✅ Always use `Colors.*` constants instead of hardcoding hex values
2. ✅ Use `Spacing.*` for all margins and padding
3. ✅ Use `render_*` component functions for consistency
4. ✅ Use `BorderRadius.*` for all rounded corners
5. ✅ Use `Shadows.*` for depth effects
6. ✅ Use `Transitions.*` for animations

## Testing

To test the design system:

```python
# Create a test page
if st.session_state.get("show_design_system"):
    render_header()
    render_section_title("Design System Preview")
    
    st.markdown("### Colors")
    col1, col2, col3 = st.columns(3)
    for color_name, color_value in vars(Colors).items():
        with col1:
            st.color_picker(color_name, value=color_value)
    
    st.markdown("### Components")
    render_stat_box("Test Stat", "42", "🎯")
    render_badge("Test Badge", "primary")
    render_alert("Test Alert", alert_type="success", title="Success!")
```

## Support

For issues or questions about the design system, refer to the component docstrings in `design_system.py`.
