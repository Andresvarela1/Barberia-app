# Layout Wrapper Functions - Quick Reference

## 6 New Functions for SaaS-Style Booking Flow

### 1️⃣ render_step_indicator()
Shows progress through multi-step flow

```python
render_step_indicator(
    current_step=1,
    total_steps=6,
    step_titles=["Service", "Barber", "Time", "Data", "Review", "Confirm"]
)
```

**Output:** Animated circles showing current, completed, and pending steps

---

### 2️⃣ render_booking_header()
Professional header with title, subtitle, and step info

```python
render_booking_header(
    title="Select Your Service",
    subtitle="Choose from our available options",
    step=1,
    total_steps=6
)
```

**Output:** Centered title + subtitle with optional step counter

---

### 3️⃣ render_booking_section()
Container for content sections with styling

```python
def my_content():
    st.write("Your content here")
    st.button("Click me")

render_booking_section(
    title="Section Title",
    content_func=my_content
)
```

**Output:** Styled section with gradient bg, border, shadow, and title

---

### 4️⃣ render_form_group()
Standardized form field with label + help/error text

```python
def my_input():
    return st.text_input("Email")

render_form_group(
    label="Email Address",
    input_func=my_input,
    help_text="We'll send a confirmation",
    error_text=None  # Show only if error
)
```

**Output:** Formatted form field with optional help/error messages

---

### 5️⃣ render_button_group()
Multiple buttons with consistent spacing

```python
buttons = [
    {'label': 'Cancel', 'primary': False, 'key': 'cancel', 'callback': cancel_func},
    {'label': 'Confirm', 'primary': True, 'key': 'confirm', 'callback': confirm_func}
]

render_button_group(buttons, layout="horizontal")  # or "vertical"
```

**Output:** Buttons in horizontal (side-by-side) or vertical (stacked) layout

---

### 6️⃣ render_booking_container()
Centered container with max-width 800px

```python
def my_booking_flow():
    render_step_indicator(1, 6)
    render_booking_header("Title", "Subtitle")
    st.write("Your content")

render_booking_container(my_booking_flow)
```

**Output:** Centered, professional container for full booking flow

---

## Complete Booking Flow Example

```python
import streamlit as st
from design_system import (
    render_booking_container,
    render_step_indicator,
    render_booking_header,
    render_booking_section,
    render_form_group,
    render_button_group,
    Spacing
)

# Initialize session state
if "booking_step" not in st.session_state:
    st.session_state.booking_step = 1

step_titles = ["Service", "Barber", "Time", "Data", "Review", "Confirm"]

def booking_flow():
    # STEP 1: Service Selection
    if st.session_state.booking_step == 1:
        render_step_indicator(1, 6, step_titles)
        render_booking_header(
            title="Select Your Service",
            subtitle="Choose from our available options",
            step=1,
            total_steps=6
        )
        
        def show_services():
            cols = st.columns(2)
            services = ["Haircut", "Beard", "Hair + Beard"]
            for idx, service in enumerate(services):
                with cols[idx % 2]:
                    if st.button(f"📚 {service}"):
                        st.session_state.booking_data = {"service": service}
                        st.session_state.booking_step = 2
                        st.rerun()
        
        render_booking_section(title=None, content_func=show_services)
    
    # STEP 2: Barber Selection
    elif st.session_state.booking_step == 2:
        render_step_indicator(2, 6, step_titles)
        render_booking_header(
            title="Choose Your Barber",
            subtitle="Who would you like to cut your hair?",
            step=2,
            total_steps=6
        )
        
        col1, col2 = st.columns([1, 9])
        with col1:
            if st.button("← Back"):
                st.session_state.booking_step = 1
                st.rerun()
        
        def show_barbers():
            barbers = ["Andrea", "Andres", "Yor", "Maikel"]
            cols = st.columns(3)
            for idx, barber in enumerate(barbers):
                with cols[idx % 3]:
                    if st.button(f"💼 {barber}"):
                        st.session_state.booking_data["barber"] = barber
                        st.session_state.booking_step = 3
                        st.rerun()
        
        render_booking_section(title=None, content_func=show_barbers)
    
    # STEP 3: Confirmation
    elif st.session_state.booking_step == 3:
        render_step_indicator(3, 6, step_titles)
        render_booking_header(
            title="Confirm Your Booking",
            subtitle="Review your appointment details",
            step=3,
            total_steps=6
        )
        
        def show_summary():
            data = st.session_state.booking_data
            st.write(f"**Service:** {data.get('service')}")
            st.write(f"**Barber:** {data.get('barber')}")
        
        render_booking_section(title="Your Appointment", content_func=show_summary)
        
        buttons = [
            {'label': 'Cancel', 'primary': False, 'key': 'cancel_booking', 
             'callback': lambda: setattr(st.session_state, 'booking_step', 1)},
            {'label': 'Confirm', 'primary': True, 'key': 'confirm_booking',
             'callback': lambda: st.success("Booking confirmed!")}
        ]
        render_button_group(buttons, layout="horizontal")

# Main app
st.set_page_config(page_title="Barbershop Booking", layout="wide")
render_booking_container(booking_flow)
```

---

## CSS Classes Available

All wrapper functions inject custom CSS. You can reference these classes:

- `.booking-container` - Main centered container
- `.booking-header` - Header section
- `.booking-section` - Content section wrapper
- `.step-indicator` - Progress circles
- `.step-circle` - Individual step circle
- `.step-connector` - Line between steps
- `.form-group` - Form field wrapper

---

## Design Tokens Reference

Use these in custom styling:

```python
from design_system import Colors, Typography, Spacing, Gradients, Shadows

# Example: Custom card with design tokens
st.markdown(f"""
<div style="
    background: {Gradients.CARD_SUBTLE};
    padding: {Spacing.XL};
    border-radius: 12px;
    box-shadow: {Shadows.MD};
">
    <h2 style="color: {Colors.TEXT};">Your Custom Card</h2>
</div>
""", unsafe_allow_html=True)
```

**Common Tokens:**
- `Colors.PRIMARY` - Brand purple (#7c3aed)
- `Colors.SECONDARY` - Accent cyan (#06b6d4)
- `Colors.SUCCESS` - Green (#22c55e)
- `Colors.DANGER` - Red (#ef4444)
- `Spacing.MD` - 16px
- `Spacing.LG` - 24px
- `Spacing.XL` - 32px

---

## Tips & Best Practices

✅ **DO:**
- Use layout wrappers for all booking flow pages
- Wrap content in functions passed to `content_func`
- Use design tokens for custom styling
- Call `st.rerun()` after step changes
- Define callbacks for button groups

❌ **DON'T:**
- Mix old inline HTML styles with new wrappers
- Use hardcoded colors (use design tokens instead)
- Forget to close render_booking_section before next step
- Use custom spacing (use Spacing tokens)
- Nest multiple render_booking_container calls

---

## Common Patterns

### Pattern 1: Back Button
```python
col_back, col_space = st.columns([1, 9])
with col_back:
    if st.button("← Back"):
        st.session_state.booking_step = previous_step
        st.rerun()
```

### Pattern 2: Form with Validation
```python
render_form_group(
    label="Your Email",
    input_func=lambda: st.text_input("Email"),
    help_text="Your confirmation will be sent here",
    error_text="Invalid email format" if error else None
)
```

### Pattern 3: Conditional Content
```python
def dynamic_content():
    if st.session_state.show_details:
        st.write("Details here")
    else:
        st.write("Summary view")

render_booking_section(title="Content", content_func=dynamic_content)
```

---

## Troubleshooting

**Q: Functions aren't imported?**  
A: Add to your imports: `from design_system import render_booking_header, ...`

**Q: Layout looks broken?**  
A: Make sure you're inside a `render_booking_container()` call

**Q: Styles not applying?**  
A: Verify `apply_global_theme()` was called at app start

**Q: Step indicator not showing?**  
A: Call `render_step_indicator()` BEFORE header and sections

**Q: Content not rendering?**  
A: Pass content as a function: `content_func=lambda: st.write("Hi")`

---

## Support

For questions:
1. Check `design_system.py` for function documentation
2. See `UI_REDESIGN_SAAS.md` for architecture overview  
3. Review booking flow in `app.py` for usage examples
4. Check this reference for common patterns
