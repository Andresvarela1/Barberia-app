import textwrap

with open('design_system.py', 'r', encoding='utf-8-sig') as f:
    ds = f.read()

idx = ds.find('def render_barber_card')
body_end = ds.find('\ndef ', idx + 10)
body = ds[idx:body_end]

# Extract card_html by finding the f-string
ch_idx = body.find('card_html = f"""')
# The f-string content starts after the opening triple-quote
content_start = ch_idx + len('card_html = f"""')
# Find the closing triple-quote
ch_end = body.find('"""', content_start)
raw_html_template = body[content_start:ch_end]

# Simulate rendering with is_selected=False (the problematic case)
# Replace the conditional expression with empty string (is_selected=False)
simulated = raw_html_template
# Replace the barber-check conditional with '' (as it would be when is_selected=False)
import re
simulated = re.sub(
    r"\{f'<div class=\"barber-check\">[^}]*</div>' if is_selected else ''\}",
    '',
    simulated
)
# Replace other f-string expressions with placeholders
simulated = re.sub(r'\{[^}]+\}', 'PLACEHOLDER', simulated)

result = textwrap.dedent(simulated).strip()

print("=== After dedent+strip (is_selected=False simulation) ===")
lines = result.splitlines()
print(f"Total lines: {len(lines)}")
print()

for i, line in enumerate(lines):
    is_blank = line.strip() == ''
    marker = " <-- BLANK LINE" if is_blank else ""
    print(f"  [{i:2d}] {repr(line)}{marker}")

print()
print("Starts with <style>:", result.startswith("<style>"))
print("Any blank lines inside div:", any(l.strip() == '' for l in lines[lines.index(next(l for l in lines if '<div class=' in l and 'PLACEHOLDER' in l)):]))
