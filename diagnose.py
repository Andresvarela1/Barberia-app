"""Diagnostic script for landing CSS and barber card rendering issues."""
with open('app.py', 'r', newline='', encoding='utf-8-sig') as f:
    content = f.read()

print("=" * 60)
print("DIAGNOSTIC A: render_hero_marketplace CSS block format")
print("=" * 60)

idx_func = content.find('def render_hero_marketplace')
idx_md = content.find('st.markdown', idx_func)
snippet = content[idx_md:idx_md+200]
print(repr(snippet))

print()
print("=" * 60)
print("DIAGNOSTIC B: Does render_home_screen call apply_public_booking_css?")
print("=" * 60)

idx_home = content.find('def render_home_screen')
idx_end_home = content.find('\ndef ', idx_home + 10)
home_block = content[idx_home:idx_end_home]
print("apply_public_booking_css in render_home_screen:", 'apply_public_booking_css' in home_block)

print()
print("=" * 60)
print("DIAGNOSTIC C: All 'Buscar' buttons - full context")
print("=" * 60)

import re
for m in re.finditer(r'.{100}Buscar.{100}', content, re.DOTALL):
    print(repr(m.group()))
    print("---")

print()
print("=" * 60)
print("DIAGNOSTIC D: CSS that targets stApp background in home path")
print("=" * 60)

# Check if there's a stApp CSS rule in render_home_screen or render_hero_marketplace
for pattern in ['stApp', 'background: #080808', 'background:#080808']:
    positions = [m.start() for m in re.finditer(re.escape(pattern), content)]
    print(f"'{pattern}' found at lines:", [content[:p].count('\n') + 1 for p in positions])

print()
print("=" * 60)
print("DIAGNOSTIC E: CSS block rendering format in render_hero_marketplace")
print("=" * 60)

# Check if the CSS st.markdown block in render_hero_marketplace uses \r\n\r\n (broken) or \n (good)
idx_hero_style = content.find('<style>', content.find('def render_hero_marketplace'))
if idx_hero_style >= 0:
    style_snippet = content[idx_hero_style:idx_hero_style+100]
    print(repr(style_snippet))
    has_double_crlf = '\r\n\r\n' in style_snippet
    has_blank_lines = '\n\n' in style_snippet
    print(f"Has \\r\\n\\r\\n (broken in st.markdown): {has_double_crlf}")
    print(f"Has \\n\\n (blank lines): {has_blank_lines}")
else:
    print("No <style> found in render_hero_marketplace")

print()
print("=" * 60)
print("DIAGNOSTIC F: barber card - how is render_barber_card called in app.py")
print("=" * 60)

for m in re.finditer(r'.{0,100}render_barber_card.{0,100}', content):
    print(repr(m.group()))
    print(f"  Line: {content[:m.start()].count(chr(10)) + 1}")
    print()

print()
print("=" * 60)
print("DIAGNOSTIC G: design_system.py - does render_barber_card render internally?")
print("=" * 60)

with open('design_system.py', 'r', newline='', encoding='utf-8-sig') as f:
    ds = f.read()

idx_rbc = ds.find('def render_barber_card')
idx_rbc_end = ds.find('\ndef ', idx_rbc + 10)
rbc_body = ds[idx_rbc:idx_rbc_end]

print("st.markdown in render_barber_card body:", 'st.markdown' in rbc_body)
print("unsafe_allow_html in render_barber_card body:", 'unsafe_allow_html' in rbc_body)
print("textwrap.dedent used:", 'textwrap.dedent' in rbc_body)
print()

# Check for indentation before <style> or <div> in the card_html string
idx_card_html = rbc_body.find('card_html = ')
if idx_card_html >= 0:
    card_html_val = rbc_body[idx_card_html:idx_card_html+300]
    print("card_html start:")
    print(repr(card_html_val))

print()
print("=" * 60)
print("DIAGNOSTIC H: st.markdown call in render_barber_card")  
print("=" * 60)

for m in re.finditer(r'st\.markdown\([^\)]{0,200}\)', rbc_body, re.DOTALL):
    print(repr(m.group()))
    print()
