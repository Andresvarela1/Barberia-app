"""
Fix landing UI issues using correct CRLF+blank-line separators.
Each CSS property line is followed by \r\n\r\n inside the st.markdown blocks.
"""

with open('app.py', 'r', newline='', encoding='utf-8-sig') as f:
    content = f.read()

original = content

NL = '\r\n\r\n'  # blank-line separator between CSS lines in this file

# ---------------------------------------------------------------------------
# FIX 1: Add dark page background to render_hero_marketplace CSS
# Target: unique string at the start of that CSS block
# ---------------------------------------------------------------------------
OLD1 = '    <style>\r\n\r\n        /* Hero Container */\r\n\r\n        .hero-container {'
NEW1 = (
    '    <style>\r\n\r\n'
    '        .stApp {\r\n'
    '            background: #080808 !important;\r\n'
    '        }\r\n\r\n'
    '        .block-container,\r\n'
    '        [data-testid="stMainBlockContainer"] {\r\n'
    '            max-width: 1120px !important;\r\n'
    '            margin: 0 auto;\r\n'
    '            padding: 1.25rem 1.5rem 2rem !important;\r\n'
    '        }\r\n\r\n'
    '        /* Hero Container */\r\n\r\n'
    '        .hero-container {'
)

n1 = content.count(OLD1)
if n1 == 1:
    content = content.replace(OLD1, NEW1)
    print(f"FIX 1 applied: dark stApp background injected into hero CSS")
else:
    print(f"FIX 1 SKIPPED: found {n1} occurrences")

# ---------------------------------------------------------------------------
# FIX 2: Dark search container
# ---------------------------------------------------------------------------
OLD2 = (
    '        .search-container {\r\n\r\n'
    '            background: white;\r\n\r\n'
    '            padding: 25px;\r\n\r\n'
    '            border-radius: 16px;\r\n\r\n'
    '            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);\r\n\r\n'
    '            margin-top: 40px;\r\n\r\n'
    '            max-width: 1000px;\r\n\r\n'
    '            margin-left: auto;\r\n\r\n'
    '            margin-right: auto;\r\n\r\n'
    '            border: 1px solid rgba(197,159,85,0.2);\r\n\r\n'
    '        }'
)
NEW2 = (
    '        .search-container {\r\n\r\n'
    '            background: #111111;\r\n\r\n'
    '            padding: 20px;\r\n\r\n'
    '            border-radius: 16px;\r\n\r\n'
    '            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);\r\n\r\n'
    '            margin-top: 28px;\r\n\r\n'
    '            max-width: 900px;\r\n\r\n'
    '            margin-left: auto;\r\n\r\n'
    '            margin-right: auto;\r\n\r\n'
    '            border: 1px solid rgba(197,159,85,0.25);\r\n\r\n'
    '        }'
)

n2 = content.count(OLD2)
if n2 == 1:
    content = content.replace(OLD2, NEW2)
    print("FIX 2 applied: search container darkened")
else:
    print(f"FIX 2 SKIPPED: found {n2} occurrences")

# ---------------------------------------------------------------------------
# FIX 3: Dark search input fields
# ---------------------------------------------------------------------------
OLD3 = (
    '        .search-input input {\r\n\r\n'
    '            border-radius: 10px !important;\r\n\r\n'
    '            border: 2px solid #e0e0e0 !important;\r\n\r\n'
    '            padding: 14px 16px !important;\r\n\r\n'
    '            font-size: 16px !important;\r\n\r\n'
    '            transition: all 0.3s ease !important;\r\n\r\n'
    '            height: 50px !important;\r\n\r\n'
    '        }\r\n\r\n'
    '        .search-input input:focus {\r\n\r\n'
    '            border-color: #c5a028 !important;\r\n\r\n'
    '            box-shadow: 0 0 0 3px rgba(197,160,40,0.2) !important;\r\n\r\n'
    '            outline: none !important;\r\n\r\n'
    '        }'
)
NEW3 = (
    '        .search-input input {\r\n\r\n'
    '            border-radius: 10px !important;\r\n\r\n'
    '            border: 1px solid rgba(197,159,85,0.3) !important;\r\n\r\n'
    '            background: #1a1a1a !important;\r\n\r\n'
    '            color: #f5f0e8 !important;\r\n\r\n'
    '            padding: 14px 16px !important;\r\n\r\n'
    '            font-size: 16px !important;\r\n\r\n'
    '            transition: all 0.25s ease !important;\r\n\r\n'
    '            height: 50px !important;\r\n\r\n'
    '        }\r\n\r\n'
    '        .search-input input:focus {\r\n\r\n'
    '            border-color: #c5a028 !important;\r\n\r\n'
    '            box-shadow: 0 0 0 3px rgba(197,160,40,0.22) !important;\r\n\r\n'
    '            outline: none !important;\r\n\r\n'
    '        }'
)

n3 = content.count(OLD3)
if n3 == 1:
    content = content.replace(OLD3, NEW3)
    print("FIX 3 applied: search inputs darkened")
else:
    print(f"FIX 3 SKIPPED: found {n3} occurrences")

# ---------------------------------------------------------------------------
# FIX 4: Search button - add higher-specificity selectors so 180px card rule
#         cannot override the 50px search button height
# ---------------------------------------------------------------------------
OLD4 = (
    '        /* Search Button Styling */\r\n\r\n'
    '        .search-button button {\r\n\r\n'
    '            background: linear-gradient(135deg, #c5a028 0%, #8a6e17 100%) !important;\r\n\r\n'
    '            color: #080808 !important;\r\n\r\n'
    '            border: none !important;\r\n\r\n'
    '            border-radius: 10px !important;\r\n\r\n'
    '            padding: 0 30px !important;\r\n\r\n'
    '            font-size: 16px !important;\r\n\r\n'
    '            font-weight: 700 !important;\r\n\r\n'
    '            height: 50px !important;\r\n\r\n'
    '            cursor: pointer !important;\r\n\r\n'
    '            transition: all 0.3s ease !important;\r\n\r\n'
    '            box-shadow: 0 4px 15px rgba(197,160,40,0.35) !important;\r\n\r\n'
    '            width: 100% !important;\r\n\r\n'
    '        }\r\n\r\n'
    '        .search-button button:hover {\r\n\r\n'
    '            transform: translateY(-2px) !important;\r\n\r\n'
    '            box-shadow: 0 8px 25px rgba(197,160,40,0.5) !important;\r\n\r\n'
    '        }\r\n\r\n'
    '        .search-button button:active {\r\n\r\n'
    '            transform: translateY(0) !important;\r\n\r\n'
    '        }'
)
NEW4 = (
    '        /* Search Button Styling */\r\n\r\n'
    '        div.search-button > div > button,\r\n'
    '        .search-button div.stButton > button,\r\n'
    '        .search-button button {\r\n\r\n'
    '            background: linear-gradient(135deg, #c5a028 0%, #8a6e17 100%) !important;\r\n\r\n'
    '            color: #080808 !important;\r\n\r\n'
    '            border: none !important;\r\n\r\n'
    '            border-radius: 10px !important;\r\n\r\n'
    '            padding: 0 16px !important;\r\n\r\n'
    '            font-size: 15px !important;\r\n\r\n'
    '            font-weight: 700 !important;\r\n\r\n'
    '            height: 50px !important;\r\n\r\n'
    '            min-height: 50px !important;\r\n\r\n'
    '            max-height: 54px !important;\r\n\r\n'
    '            cursor: pointer !important;\r\n\r\n'
    '            transition: all 0.25s ease !important;\r\n\r\n'
    '            box-shadow: 0 4px 15px rgba(197,160,40,0.35) !important;\r\n\r\n'
    '            width: 100% !important;\r\n\r\n'
    '        }\r\n\r\n'
    '        div.search-button > div > button:hover,\r\n'
    '        .search-button div.stButton > button:hover,\r\n'
    '        .search-button button:hover {\r\n\r\n'
    '            box-shadow: 0 8px 25px rgba(197,160,40,0.5) !important;\r\n\r\n'
    '        }\r\n\r\n'
    '        .search-button button:active {\r\n\r\n'
    '            transform: translateY(0) !important;\r\n\r\n'
    '        }'
)

n4 = content.count(OLD4)
if n4 == 1:
    content = content.replace(OLD4, NEW4)
    print("FIX 4 applied: search button specificity boosted + resized")
else:
    print(f"FIX 4 SKIPPED: found {n4} occurrences")

# ---------------------------------------------------------------------------
# FIX 5: Home card buttons - reduce height + font + padding
# ---------------------------------------------------------------------------
OLD5_HEIGHT = '            height: 180px !important;\r\n\r\n'
NEW5_HEIGHT = '            min-height: 120px !important;\r\n\r\n'

n5h = content.count(OLD5_HEIGHT)
if n5h == 1:
    content = content.replace(OLD5_HEIGHT, NEW5_HEIGHT)
    print("FIX 5a applied: card height -> min-height 120px")
else:
    print(f"FIX 5a SKIPPED: found {n5h} occurrences of height: 180px")

OLD5_FONT = '            font-size: 20px !important;\r\n\r\n'
NEW5_FONT = '            font-size: 15px !important;\r\n\r\n'

n5f = content.count(OLD5_FONT)
if n5f == 1:
    content = content.replace(OLD5_FONT, NEW5_FONT)
    print("FIX 5b applied: card font-size -> 15px")
else:
    print(f"FIX 5b SKIPPED: found {n5f} occurrences")

OLD5_LH = '            line-height: 1.8 !important;\r\n\r\n'
NEW5_LH = '            line-height: 1.5 !important;\r\n\r\n'

n5l = content.count(OLD5_LH)
if n5l == 1:
    content = content.replace(OLD5_LH, NEW5_LH)
    print("FIX 5c applied: card line-height -> 1.5")
else:
    print(f"FIX 5c SKIPPED: found {n5l} occurrences")

OLD5_PAD = '            padding: 40px 20px !important;\r\n\r\n'
NEW5_PAD = '            padding: 1.25rem 1rem !important;\r\n\r\n'

n5p = content.count(OLD5_PAD)
if n5p == 1:
    content = content.replace(OLD5_PAD, NEW5_PAD)
    print("FIX 5d applied: card padding reduced")
else:
    print(f"FIX 5d SKIPPED: found {n5p} occurrences")

# ---------------------------------------------------------------------------
# FIX 6: Remove scale(1.02) from card hover
# ---------------------------------------------------------------------------
OLD6 = '            transform: translateY(-4px) scale(1.02) !important;\r\n\r\n'
NEW6 = ''  # Remove the transform entirely (no jump/scale on hover)

n6 = content.count(OLD6)
if n6 == 1:
    content = content.replace(OLD6, NEW6)
    print("FIX 6 applied: removed scale(1.02) from card hover")
else:
    print(f"FIX 6 SKIPPED: found {n6} occurrences")

# ---------------------------------------------------------------------------
# Write result
# ---------------------------------------------------------------------------
with open('app.py', 'w', newline='', encoding='utf-8-sig') as f:
    f.write(content)

changed = content != original
print(f"\nResult: {'MODIFIED' if changed else 'UNCHANGED'}. Size: {len(content)} chars (was {len(original)})")


# ---------------------------------------------------------------------------
# FIX 1: Add dark page background + container centering to render_hero_marketplace CSS
# Target: the <style> tag that opens inside render_hero_marketplace st.markdown block
# This string appears uniquely at the start of render_hero_marketplace CSS
# ---------------------------------------------------------------------------
OLD1 = (
    '    <style>\r\n'
    '        /* Hero Container */\r\n'
    '        .hero-container {'
)
NEW1 = (
    '    <style>\r\n'
    '        .stApp {\r\n'
    '            background: #080808 !important;\r\n'
    '        }\r\n'
    '\r\n'
    '        .block-container,\r\n'
    '        [data-testid="stMainBlockContainer"] {\r\n'
    '            max-width: 1120px !important;\r\n'
    '            margin: 0 auto;\r\n'
    '            padding: 1.25rem 1.5rem 2rem !important;\r\n'
    '        }\r\n'
    '\r\n'
    '        /* Hero Container */\r\n'
    '        .hero-container {'
)

if OLD1 in content:
    content = content.replace(OLD1, NEW1, 1)
    print("FIX 1 applied: dark page background added")
else:
    print("FIX 1 SKIPPED: pattern not found")

# ---------------------------------------------------------------------------
# FIX 2: Dark search container (was background: white)
# ---------------------------------------------------------------------------
OLD2 = (
    '        .search-container {\r\n'
    '            background: white;\r\n'
    '            padding: 25px;\r\n'
    '            border-radius: 16px;\r\n'
    '            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);\r\n'
    '            margin-top: 40px;\r\n'
    '            max-width: 1000px;\r\n'
    '            margin-left: auto;\r\n'
    '            margin-right: auto;\r\n'
    '            border: 1px solid rgba(197,159,85,0.2);\r\n'
    '        }'
)
NEW2 = (
    '        .search-container {\r\n'
    '            background: #111111;\r\n'
    '            padding: 20px;\r\n'
    '            border-radius: 16px;\r\n'
    '            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);\r\n'
    '            margin-top: 32px;\r\n'
    '            max-width: 900px;\r\n'
    '            margin-left: auto;\r\n'
    '            margin-right: auto;\r\n'
    '            border: 1px solid rgba(197,159,85,0.25);\r\n'
    '        }'
)

if OLD2 in content:
    content = content.replace(OLD2, NEW2, 1)
    print("FIX 2 applied: search container darkened")
else:
    print("FIX 2 SKIPPED: pattern not found")

# ---------------------------------------------------------------------------
# FIX 3: Dark search input fields (was light border, no dark bg)
# ---------------------------------------------------------------------------
OLD3 = (
    '        /* Input Field Styling */\r\n'
    '        .search-input input {\r\n'
    '            border-radius: 10px !important;\r\n'
    '            border: 2px solid #e0e0e0 !important;\r\n'
    '            padding: 14px 16px !important;\r\n'
    '            font-size: 16px !important;\r\n'
    '            transition: all 0.3s ease !important;\r\n'
    '            height: 50px !important;\r\n'
    '        }\r\n'
    '\r\n'
    '        .search-input input:focus {\r\n'
    '            border-color: #c5a028 !important;\r\n'
    '            box-shadow: 0 0 0 3px rgba(197,160,40,0.2) !important;\r\n'
    '            outline: none !important;\r\n'
    '        }'
)
NEW3 = (
    '        /* Input Field Styling */\r\n'
    '        .search-input input {\r\n'
    '            border-radius: 10px !important;\r\n'
    '            border: 1px solid rgba(197,159,85,0.3) !important;\r\n'
    '            background: #1a1a1a !important;\r\n'
    '            color: #f5f0e8 !important;\r\n'
    '            padding: 14px 16px !important;\r\n'
    '            font-size: 16px !important;\r\n'
    '            transition: all 0.3s ease !important;\r\n'
    '            height: 50px !important;\r\n'
    '        }\r\n'
    '\r\n'
    '        .search-input input:focus {\r\n'
    '            border-color: #c5a028 !important;\r\n'
    '            box-shadow: 0 0 0 3px rgba(197,160,40,0.22) !important;\r\n'
    '            outline: none !important;\r\n'
    '        }'
)

if OLD3 in content:
    content = content.replace(OLD3, NEW3, 1)
    print("FIX 3 applied: search inputs darkened")
else:
    print("FIX 3 SKIPPED: pattern not found")

# ---------------------------------------------------------------------------
# FIX 4: Search button - add high-specificity override so cards CSS can't
#         override it with height: 180px. Also reduce padding.
# ---------------------------------------------------------------------------
OLD4 = (
    '        /* Search Button Styling */\r\n'
    '        .search-button button {\r\n'
    '            background: linear-gradient(135deg, #c5a028 0%, #8a6e17 100%) !important;\r\n'
    '            color: #080808 !important;\r\n'
    '            border: none !important;\r\n'
    '            border-radius: 10px !important;\r\n'
    '            padding: 0 30px !important;\r\n'
    '            font-size: 16px !important;\r\n'
    '            font-weight: 700 !important;\r\n'
    '            height: 50px !important;\r\n'
    '            cursor: pointer !important;\r\n'
    '            transition: all 0.3s ease !important;\r\n'
    '            box-shadow: 0 4px 15px rgba(197,160,40,0.35) !important;\r\n'
    '            width: 100% !important;\r\n'
    '        }\r\n'
    '\r\n'
    '        .search-button button:hover {\r\n'
    '            transform: translateY(-2px) !important;\r\n'
    '            box-shadow: 0 8px 25px rgba(197,160,40,0.5) !important;\r\n'
    '        }\r\n'
    '\r\n'
    '        .search-button button:active {\r\n'
    '            transform: translateY(0) !important;\r\n'
    '        }'
)
NEW4 = (
    '        /* Search Button Styling */\r\n'
    '        div.search-button button,\r\n'
    '        .search-button .stButton > button,\r\n'
    '        .search-button button {\r\n'
    '            background: linear-gradient(135deg, #c5a028 0%, #8a6e17 100%) !important;\r\n'
    '            color: #080808 !important;\r\n'
    '            border: none !important;\r\n'
    '            border-radius: 10px !important;\r\n'
    '            padding: 0 20px !important;\r\n'
    '            font-size: 15px !important;\r\n'
    '            font-weight: 700 !important;\r\n'
    '            height: 50px !important;\r\n'
    '            min-height: 50px !important;\r\n'
    '            max-height: 54px !important;\r\n'
    '            cursor: pointer !important;\r\n'
    '            transition: all 0.25s ease !important;\r\n'
    '            box-shadow: 0 4px 15px rgba(197,160,40,0.35) !important;\r\n'
    '            width: 100% !important;\r\n'
    '        }\r\n'
    '\r\n'
    '        div.search-button button:hover,\r\n'
    '        .search-button .stButton > button:hover,\r\n'
    '        .search-button button:hover {\r\n'
    '            box-shadow: 0 8px 25px rgba(197,160,40,0.5) !important;\r\n'
    '            transform: none !important;\r\n'
    '        }\r\n'
    '\r\n'
    '        .search-button button:active {\r\n'
    '            transform: translateY(0) !important;\r\n'
    '        }'
)

if OLD4 in content:
    content = content.replace(OLD4, NEW4, 1)
    print("FIX 4 applied: search button high-specificity override")
else:
    print("FIX 4 SKIPPED: pattern not found")

# ---------------------------------------------------------------------------
# FIX 5: Home card buttons - reduce size, remove scale hover
# ---------------------------------------------------------------------------
OLD5 = (
    '        /* Base button styling for all card buttons */\r\n'
    '        div.stButton > button {\r\n'
    '\r\n'
    '            height: 180px !important;\r\n'
    '\r\n'
    '            border-radius: 16px !important;\r\n'
    '\r\n'
    '            font-size: 20px !important;\r\n'
    '\r\n'
    '            font-weight: 600 !important;\r\n'
    '\r\n'
    '            border: 1px solid rgba(197,159,85,0.22) !important;\r\n'
    '\r\n'
    '            transition: all 0.3s ease !important;\r\n'
    '\r\n'
    '            white-space: pre-line !important;\r\n'
    '\r\n'
    '            line-height: 1.8 !important;\r\n'
    '\r\n'
    '            padding: 40px 20px !important;\r\n'
    '\r\n'
    '            display: flex !important;\r\n'
    '\r\n'
    '            align-items: center !important;\r\n'
    '\r\n'
    '            justify-content: center !important;\r\n'
    '\r\n'
    '            flex-direction: column !important;\r\n'
    '\r\n'
    '            text-align: center !important;\r\n'
    '\r\n'
    '            color: #f5f0e8 !important;\r\n'
    '\r\n'
    '            cursor: pointer !important;\r\n'
    '\r\n'
    '            background: #141414 !important;\r\n'
    '\r\n'
    '        }'
)
NEW5 = (
    '        /* Base button styling for all card buttons */\r\n'
    '        div.stButton > button {\r\n'
    '\r\n'
    '            min-height: 120px !important;\r\n'
    '\r\n'
    '            border-radius: 16px !important;\r\n'
    '\r\n'
    '            font-size: 15px !important;\r\n'
    '\r\n'
    '            font-weight: 600 !important;\r\n'
    '\r\n'
    '            border: 1px solid rgba(197,159,85,0.22) !important;\r\n'
    '\r\n'
    '            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;\r\n'
    '\r\n'
    '            white-space: pre-line !important;\r\n'
    '\r\n'
    '            line-height: 1.5 !important;\r\n'
    '\r\n'
    '            padding: 1.25rem 1rem !important;\r\n'
    '\r\n'
    '            display: flex !important;\r\n'
    '\r\n'
    '            align-items: center !important;\r\n'
    '\r\n'
    '            justify-content: center !important;\r\n'
    '\r\n'
    '            flex-direction: column !important;\r\n'
    '\r\n'
    '            text-align: center !important;\r\n'
    '\r\n'
    '            color: #f5f0e8 !important;\r\n'
    '\r\n'
    '            cursor: pointer !important;\r\n'
    '\r\n'
    '            background: #141414 !important;\r\n'
    '\r\n'
    '        }'
)

if OLD5 in content:
    content = content.replace(OLD5, NEW5, 1)
    print("FIX 5 applied: home card buttons resized")
else:
    print("FIX 5 SKIPPED: pattern not found")

# ---------------------------------------------------------------------------
# FIX 6: Remove scale(1.02) from home card hover
# ---------------------------------------------------------------------------
OLD6 = (
    '        /* Hover effects - scale and gold glow */\r\n'
    '        div.stButton > button:hover {\r\n'
    '\r\n'
    '            transform: translateY(-4px) scale(1.02) !important;\r\n'
    '\r\n'
    '            border-color: #c5a028 !important;\r\n'
    '\r\n'
    '            background: #1e1a0e !important;\r\n'
    '\r\n'
    '            box-shadow: 0 12px 28px rgba(197,160,40,0.25) !important;\r\n'
    '\r\n'
    '        }'
)
NEW6 = (
    '        /* Hover effects - gold glow, no scale */\r\n'
    '        div.stButton > button:hover {\r\n'
    '\r\n'
    '            border-color: #c5a028 !important;\r\n'
    '\r\n'
    '            background: #1e1a0e !important;\r\n'
    '\r\n'
    '            box-shadow: 0 8px 24px rgba(197,160,40,0.22) !important;\r\n'
    '\r\n'
    '        }'
)

if OLD6 in content:
    content = content.replace(OLD6, NEW6, 1)
    print("FIX 6 applied: removed scale(1.02) from card hover")
else:
    print("FIX 6 SKIPPED: pattern not found")

# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------
assert len(content) != original_len or True  # always write
with open('app.py', 'w', newline='', encoding='utf-8-sig') as f:
    f.write(content)

print(f"\nDone. File size: {len(content)} chars (was {original_len})")
