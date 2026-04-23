# DETAILED UI INCONSISTENCIES - Line by Line Reference

## 1. BOOKING FLOW HEADERS (Duplicated Pattern)

### Header Pattern - Used 6+ times identically

```python
# Pattern appears at:
# - Line 2540-2546: Step 1 header
# - Line 2600-2606: Step 2 header  
# - Line 2703-2709: Step 3 header
# - Line 2838-2844: Step 4 header
# - Line 2871-2877: Step 5 header
# - Line 2943-2949: Step 6 header
```

**Issue:** Each time, slight text changes but identical structure:
```html
<div style="text-align: center; margin-bottom: 32px;">
    <h1 style="margin: 0; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;
               background-clip: text;">EMOJI Elige tu X</h1>
    <p style="color: #666; margin-top: 8px;">Subtitle text</p>
</div>
```

**Problems:**
- CSS `background-clip: text` + `-webkit-text-fill-color` doesn't work on all browsers
- Colors (#667eea, #764ba2) hardcoded, not in design system
- Text color #666 (gray) not in design system
- margin-bottom value hardcoded instead of using Spacing.XL
- Should be: Single reusable function

---

## 2. COLOR INCONSISTENCIES - Purple Gradient Variants

### Variant 1: Purple Gradient (home page, headers)
```python
background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
```

### Variant 2: Design System Primary
```python
Colors.PRIMARY = "#7c3aed"  # Different purple!
Colors.PRIMARY_BUTTON = "linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)"
```

**Issue:** #667eea ≠ #7c3aed
- Header gradients use different purple than button gradients
- Impossible to rebrand - would need to find all hardcoded instances

---

## 3. SPACING SCALE CHAOS

Hardcoded margin-bottom values (should use Spacing class):
```python
margin-bottom: 32px   # Spacing.XL = "2rem" = 32px ✓ BUT HARDCODED
margin-bottom: 28px   # NOT IN DESIGN SYSTEM
margin-bottom: 24px   # Spacing.LG = "1.5rem" = 24px ✓ BUT HARDCODED
margin-bottom: 20px   # NOT IN DESIGN SYSTEM
margin-bottom: 16px   # Spacing.MD = "1rem" = 16px ✓ BUT HARDCODED
margin-bottom: 14px   # NOT IN DESIGN SYSTEM
margin-bottom: 12px   # NOT IN DESIGN SYSTEM
margin-bottom: 8px    # Spacing.SM = "0.5rem" = 8px ✓ BUT HARDCODED
```

---

## 4. TYPOGRAPHY SCALE INCONSISTENCY

### Defined in design_system.py (not used):
```python
H1 = "2.5rem"    # 40px
H2 = "2rem"      # 32px
H3 = "1.5rem"    # 24px
H4 = "1.25rem"   # 20px
BODY = "1rem"    # 16px
SMALL = "0.875rem"  # 14px
TINY = "0.75rem"    # 12px
```

### Actually used in app.py:
```python
font-size: 80px;     # BIG emoji (line 2950)
font-size: 32px;     # Section headers (multiple)
font-size: 18px;     # Subheadings (multiple)
font-size: 15px;     # Body text variants (multiple)
font-size: 14px;     # Small text (multiple)
font-size: 13px;     # Extra small (multiple)
font-size: 12px;     # Tiny text (multiple)
```

**Problem:** Chaotic scale with no clear hierarchy

---

## 5. BUTTON STYLING - THREE DIFFERENT APPROACHES

### Approach 1: HOME PAGE (Custom CSS)
```python
# Lines 3476-3530 (home page buttons)
st.markdown("""
    <style>
    div.stButton > button { height: 180px !important; ... }
    </style>
""")
st.button("🔑\n\nIniciar Sesión", key="home_login")
```

**Result:** 180px tall buttons with custom styling

### Approach 2: BOOKING FLOW (Plain Streamlit)
```python
# Lines 2556-2590 (Step 1 buttons)
st.button(
    f"✂️  {servicio}\n\n⏱️ {datos['duracion']} min\n${datos['precio']:,}",
    key=f"service_btn_{servicio}",
    use_container_width=True
)
```

**Result:** Default Streamlit button height (varies)

### Approach 3: CONFIRMATION BUTTONS (Primary Type)
```python
# Line 2967 (Step 5 confirmation)
st.button("✅ Agendar mi cita ✂️", 
          key="confirm_booking_step5", 
          use_container_width=True, 
          type="primary")
```

**Result:** Primary button styling (blue-ish)

**Problem:** Three different visual styles for similar actions

---

## 6. INFO BOX STYLING - MULTIPLE VARIATIONS

### Variation A: Service Confirmation (Step 2, Line 2619)
```python
<div style="
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
    padding: 16px 20px;
    border-radius: 12px;
    border-left: 4px solid #667eea;
    margin-bottom: 24px;
">
    <p style="margin: 0; color: #333; font-size: 0.95em;">
        <strong>✂️ Servicio seleccionado:</strong> ...
```

### Variation B: Payment Urgent (Step 6, Line 2957)
```python
<div style="
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    padding: 24px;
    border-radius: 16px;
    border: 3px solid #dc2626;  // Different - 3px vs no border
    margin-bottom: 28px;
    text-align: center;
    box-shadow: 0 8px 24px rgba(220, 38, 38, 0.15);  // Shadow here
">
```

### Variation C: Next Steps (Step 6, Line 2978)
```python
<div style="
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    padding: 16px;
    border-radius: 12px;
    border-left: 4px solid #3b82f6;  // Border-left like A, but different color
    margin-bottom: 24px;
    text-align: center;
">
```

### Variation D: Info Section (Step 6, Line 3005)
```python
<div style="
    background: #fef3c7;  // SOLID color, not gradient!
    padding: 14px;
    border-radius: 8px;
    border-left: 3px solid #f59e0b;  // Solid color border
    margin-bottom: 24px;
">
    <p style="margin: 0; color: #92400e; ...">
```

**Problem:** Each box is styled completely differently despite serving similar purposes

---

## 7. CONTRAST & ACCESSIBILITY ISSUES

### Low Contrast Examples:

```python
# Line 2620: 
color: #333;  on background: linear-gradient(rgba(102, 126, 234, 0.1)...)
// Contrast ratio ~5:1 (acceptable) but not great

# Line 2625:
color: #666;  on white background
// Contrast ratio ~3.3:1 (BELOW WCAG AA minimum of 4.5:1) ❌

# Line 2747:
color: rgba(255,255,255,0.8);  on gradient background
// Variable contrast - some areas may fall below 4.5:1 ❌

# Line 3028:
color: rgba(255,255,255,0.95);
// Almost white - should be OK, but border
```

---

## 8. RESPONSIVE DESIGN ISSUES

### Only ONE media query in entire app (Line 2555):
```python
<style>
    .service-card-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin: 24px 0;
    }
    @media (max-width: 768px) {
        .service-card-container {
            grid-template-columns: 1fr;
        }
    }
</style>
```

### But fixed column layouts everywhere else:
```python
cols = st.columns(2)    # ALWAYS 2 - Line 2556, 2672, etc.
cols = st.columns(3)    # ALWAYS 3 - Line 2661, etc.
cols = st.columns([1, 2, 1])  # Fixed ratio - Line 2821
```

**Problem:** Only service cards responsive, everything else breaks on mobile

---

## 9. INCONSISTENT PADDING/BORDER VALUES

Padding used:
```python
padding: 40px 20px   # XL with side reduction
padding: 24px       # XL
padding: 20px       # L-ish
padding: 16px       # MD
padding: 14px       # Non-standard
padding: 8px        # SM
padding: 6px        # Extra small
```

Should use: Spacing.XXL, Spacing.XL, Spacing.LG, Spacing.MD, Spacing.SM, Spacing.XS

Border radius used:
```python
border-radius: 16px  # XL-ish
border-radius: 12px  # MD
border-radius: 10px  # Non-standard
border-radius: 8px   # SM
```

Should use: BorderRadius.XL, BorderRadius.LG, BorderRadius.MD, BorderRadius.SM

---

## 10. DESIGN SYSTEM NON-USAGE

### Defined in design_system.py but NOT used in app.py:

```python
# Colors class - has 30+ colors defined, hardcoded colors used instead
Colors.PRIMARY, Colors.SECONDARY, Colors.SUCCESS, Colors.DANGER, etc.

# Typography class - defined but unused
Typography.H1, Typography.H2, Typography.BODY, etc.

# Spacing class - defined but unused  
Spacing.XL, Spacing.LG, Spacing.MD, Spacing.SM, etc.

# BorderRadius class - defined but unused
BorderRadius.XL, BorderRadius.LG, BorderRadius.MD, etc.

# Shadows class - defined but minimally used
# Used: Shadows.MD, Shadows.GLOW_SOFT (rarely)
# Not used: Shadows.LG, Shadows.XL, Shadows.ELEVATED, etc.

# Gradients class - defined but different gradients used in app
Gradients.PRIMARY_BUTTON, Gradients.SECONDARY_BUTTON (defined)
But app uses: linear-gradient(90deg, #667eea, #764ba2) (hardcoded instead)

# Transitions class - defined but not used anywhere
Transitions.FAST, Transitions.NORMAL, Transitions.SLOW (unused)
```

---

## PATTERN DUPLICATION COUNT

| Pattern | Count | Lines | Solution |
|---------|-------|-------|----------|
| Section header | 6+ | 2540-2949 | render_section_header() |
| Info alert box | 8+ | 2619-3025 | render_alert_box() |
| Back button | 5+ | 2613, 2697, 2787, 2867 | render_back_button() |
| Color gradients | 10+ | throughout | Use Colors/Gradients class |
| Spacing values | 40+ | throughout | Use Spacing class |
| Font sizes | 20+ | throughout | Use Typography class |

---

## RECOMMENDED FUNCTION EXTRACTIONS

Create in design_system.py:

```python
def render_booking_header(step, emoji, title, subtitle):
    """Replace all 6 booking step headers"""

def render_alert(message, type="info", icon=None):
    """Replace all info/warning/success boxes"""

def render_booking_button(label, key, on_click=None, is_primary=False):
    """Consistent booking flow buttons"""

def render_confirmation_display(data_dict):
    """Replace service/date/time confirmation displays"""

def render_trust_signal(text, icon="⭐"):
    """Replace all trust signals"""
```

This would eliminate ~70% of duplicated code and ensure consistency.

