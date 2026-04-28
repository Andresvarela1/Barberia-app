"""
Minimal fix: Change st.markdown(\"\"\"\\n\\n    <style> to st.markdown(\"\"\"<style>
so CommonMark renders CSS as raw HTML instead of an indented code block.
"""
with open('app.py', 'r', newline='', encoding='utf-8-sig') as f:
    content = f.read()

original = content

fixes_applied = []

# FIX 1: render_hero_marketplace — blank line + 4-space indent <style>
# Pattern: st.markdown("""\r\n\r\n    <style>
old1 = 'st.markdown("""\r\n\r\n    <style>'
new1 = 'st.markdown("""<style>'
if old1 in content:
    content = content.replace(old1, new1, 1)
    fixes_applied.append("FIX 1: render_hero_marketplace CSS start fixed")
else:
    print("WARN: FIX 1 pattern not found — searching for variant...")
    # Try with different line endings
    alt = 'st.markdown("""\n\n    <style>'
    if alt in content:
        content = content.replace(alt, new1, 1)
        fixes_applied.append("FIX 1 (LF variant): render_hero_marketplace CSS start fixed")
    else:
        print("WARN: FIX 1 not found at all")

# FIX 2: render_home_screen card buttons — blank line + 8-space indent <style>
# Pattern: st.markdown("""\r\n\r\n        <style>
old2 = 'st.markdown("""\r\n\r\n        <style>'
new2 = 'st.markdown("""<style>'
if old2 in content:
    count = content.count(old2)
    content = content.replace(old2, new2, 1)
    fixes_applied.append(f"FIX 2: home card buttons CSS start fixed (found {count} occurrence(s))")
else:
    print("WARN: FIX 2 pattern not found — searching for variant...")
    alt2 = 'st.markdown("""\n\n        <style>'
    if alt2 in content:
        content = content.replace(alt2, new2, 1)
        fixes_applied.append("FIX 2 (LF variant): home card buttons CSS start fixed")
    else:
        print("WARN: FIX 2 not found at all")

if content == original:
    print("ERROR: No changes made — all patterns missing")
    exit(1)

with open('app.py', 'w', newline='', encoding='utf-8-sig') as f:
    f.write(content)

print("Changes written to app.py")
for fix in fixes_applied:
    print(" -", fix)

# Validate with AST
import ast, sys
with open('app.py', 'r', encoding='utf-8-sig') as f:
    src = f.read()
try:
    ast.parse(src)
    print("AST: OK")
except SyntaxError as e:
    print(f"AST ERROR: {e}")
    sys.exit(1)

# Verify the fix is in place
print()
print("=== Verification ===")
idx = src.find('def render_hero_marketplace')
md_idx = src.find('st.markdown', idx)
print("render_hero_marketplace st.markdown start:", repr(src[md_idx:md_idx+30]))

idx2 = src.find('div.stButton > button {')
if idx2 >= 0:
    md_idx2 = src.rfind('st.markdown', 0, idx2)
    print("home cards st.markdown start:", repr(src[md_idx2:md_idx2+30]))
