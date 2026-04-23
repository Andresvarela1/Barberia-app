#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

# Read the file
with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

original_length = len(content)
changes_made = 0

# Use binary to identify and handle 0xC3 patterns safely if needed, 
# but let's try a simpler character-based replacement first for the obvious ones.
# The SyntaxError was likely due to unbalanced quotes or weird characters in the dict key.

# We will use hex escapes to avoid the syntax error with literal mojibake
# ÃƒÂ (C3 83 C2 A1) -> Ã¡ (C3 A1)
# Spanish chars repair
replacements = {
    "\u00c3\u0083\u00c2\u00ad": "\u00c3\u00ad",   # ÃƒÂ -> Ã
    "\u00c3\u0083\u00c2\u00a9": "\u00c3\u00a9",   # ÃƒÂ© -> Ã©
    "\u00c3\u0083\u00c2\u00a1": "\u00c3\u00a1",   # ÃƒÂ¡ -> Ã¡
    "\u00c3\u0083\u00c2\u00b3": "\u00c3\u00b3",   # ÃƒÂ³ -> Ã³
    "\u00c3\u0083\u00c2\u00b1": "\u00c3\u00b1",   # ÃƒÂ± -> Ã±
    "\u00c3\u0083\u00c2\u00a2": "\u00c3\u00a2",   # ÃƒÂ¢ -> Ã¢
    "\u00c3\u0083\u00c2\u00af": "\u00c3\u00af",   # ÃƒÂ¯ -> Ã¯
    "\u00c3\u0083\u00c2\u00ab": "\u00c3\u00ab",   # ÃƒÂ« -> Ã«
    "\u00c3\u0083\u00c2\u00a4": "\u00c3\u00a4",   # ÃƒÂ¤ -> Ã¤
}

for mojibake, correct in replacements.items():
    if mojibake in content:
        count = content.count(mojibake)
        content = content.replace(mojibake, correct)
        changes_made += count
        print(f"Replaced {count} instances of {repr(mojibake)}")

# Emojis usually start with \u00c3\u00b0\u00c5\u00b8 (Ã°Å¸)
def fix_emoji(match):
    try:
        # Convert the string to bytes if it was wrongly interpreted as Latin-1/UTF-8
        # This is a bit tricky, let's just use replacement for common ones
        return match.group(0)
    except:
        return match.group(0)

# Replace remaining complex mojibake using regex for Ã°Å¸ following by something
# This is common for emojis like ðŸ“Œ
# Ã°Å¸ = \u00c3\u00b0\u00c5\u00b8
content, count = re.subn(r"\u00c3\u00b0\u00c5\u00b8[\u00c2\u00c3\u0080-\u00bf\u00a0-\u00af]+", "ðŸ“Œ", content)
changes_made += count

# Write back
with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nRepair complete. Total replacements: {changes_made}")

# Verify 0xC3
with open("app.py", "rb") as f:
    binary_content = f.read()
c3_count = binary_content.count(b"\xc3")
print(f"Remaining 0xC3 bytes: {c3_count}")
