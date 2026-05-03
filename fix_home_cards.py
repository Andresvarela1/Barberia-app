"""Fix home screen card button gradients using regex to handle mixed line endings."""
import re

with open('app.py', 'r', encoding='utf-8', newline='') as f:
    content = f.read()

# Replace: color white -> #f5f0e8
content = re.sub(
    r'(text-align: center !important;[\r\n]+\s+color: )white( !important;[\r\n]+\s+cursor: pointer !important;[\r\n]+\s+\})',
    r'\g<1>#f5f0e8\2',
    content, count=1
)

# Change border: none -> gold border
content = re.sub(
    r'(height: 180px !important;.*?border: )none( !important;)',
    r'\g<1>1px solid rgba(197,159,85,0.22)\2',
    content, count=1, flags=re.DOTALL
)

# Add background: #141414 before closing brace of base button
content = re.sub(
    r'(cursor: pointer !important;)([\r\n]+\s+\}[\r\n]+[\r\n]+\s+/\* Hover effects)',
    r'\1\r\n\r\n            background: #141414 !important;\2',
    content, count=1
)

# Replace hover block - gold glow
content = re.sub(
    r'/\* Hover effects - scale and shadow \*/[\r\n]+\s+div\.stButton > button:hover \{[\r\n]+\s+transform: translateY\(-4px\) scale\(1\.02\) !important;[\r\n]+\s+box-shadow: 0 12px 28px rgba\(0, 0, 0, 0\.25\) !important;[\r\n]+\s+\}',
    '/* Hover effects - scale and gold glow */\r\n\r\n        div.stButton > button:hover {\r\n\r\n            transform: translateY(-4px) scale(1.02) !important;\r\n\r\n            border-color: #c5a028 !important;\r\n\r\n            background: #1e1a0e !important;\r\n\r\n            box-shadow: 0 12px 28px rgba(197,160,40,0.25) !important;\r\n\r\n        }',
    content, count=1
)

# Replace login card (purple gradient)
content = re.sub(
    r'/\* Login card - First button \*/[\r\n]+\s+div\.stButton:nth-of-type\(1\) > button \{[\r\n]+\s+background: linear-gradient\(135deg, #667eea 0%, #764ba2 100%\) !important;[\r\n]+\s+box-shadow: 0 8px 20px rgba\(102, 126, 234, 0\.3\) !important;[\r\n]+\s+\}[\r\n]+[\r\n]+\s+div\.stButton:nth-of-type\(1\) > button:hover \{[\r\n]+\s+box-shadow: 0 16px 32px rgba\(102, 126, 234, 0\.5\) !important;[\r\n]+\s+\}',
    '/* Login card */\r\n\r\n        div.stButton:nth-of-type(1) > button {\r\n\r\n            box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;\r\n\r\n        }',
    content, count=1
)

# Replace register card (pink gradient)
content = re.sub(
    r'/\* Register card - Second button \*/[\r\n]+\s+div\.stButton:nth-of-type\(2\) > button \{[\r\n]+\s+background: linear-gradient\(135deg, #f093fb 0%, #f5576c 100%\) !important;[\r\n]+\s+box-shadow: 0 8px 20px rgba\(245, 87, 108, 0\.3\) !important;[\r\n]+\s+\}[\r\n]+[\r\n]+\s+div\.stButton:nth-of-type\(2\) > button:hover \{[\r\n]+\s+box-shadow: 0 16px 32px rgba\(245, 87, 108, 0\.5\) !important;[\r\n]+\s+\}',
    '/* Register card */\r\n\r\n        div.stButton:nth-of-type(2) > button {\r\n\r\n            box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;\r\n\r\n        }',
    content, count=1
)

# Replace booking card (cyan gradient)
content = re.sub(
    r'/\* Booking card - Third button \*/[\r\n]+\s+div\.stButton:nth-of-type\(3\) > button \{[\r\n]+\s+background: linear-gradient\(135deg, #4facfe 0%, #00f2fe 100%\) !important;[\r\n]+\s+box-shadow: 0 8px 20px rgba\(79, 172, 254, 0\.3\) !important;[\r\n]+\s+\}[\r\n]+[\r\n]+\s+div\.stButton:nth-of-type\(3\) > button:hover \{[\r\n]+\s+box-shadow: 0 16px 32px rgba\(79, 172, 254, 0\.5\) !important;[\r\n]+\s+\}',
    '/* Booking card */\r\n\r\n        div.stButton:nth-of-type(3) > button {\r\n\r\n            box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;\r\n\r\n        }',
    content, count=1
)

remaining = [c for c in ['#f093fb', '#f5576c', '#4facfe', '#00f2fe'] if c in content]
if remaining:
    print(f'WARNING: still has colors: {remaining}')
else:
    print('All card gradients replaced OK')

with open('app.py', 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('Done')

NL = '\r\n'

old_block = (
    f'            border: none !important;{NL}{NL}'
    f'            transition: all 0.3s ease !important;{NL}{NL}'
    f'            white-space: pre-line !important;{NL}{NL}'
    f'            line-height: 1.8 !important;{NL}{NL}'
    f'            padding: 40px 20px !important;{NL}{NL}'
    f'            display: flex !important;{NL}{NL}'
    f'            align-items: center !important;{NL}{NL}'
    f'            justify-content: center !important;{NL}{NL}'
    f'            flex-direction: column !important;{NL}{NL}'
    f'            text-align: center !important;{NL}{NL}'
    f'            color: white !important;{NL}{NL}'
    f'            cursor: pointer !important;{NL}{NL}'
    f'        }}{NL}{NL}{NL}{NL}'
    f'        /* Hover effects - scale and shadow */{NL}{NL}'
    f'        div.stButton > button:hover {{{NL}{NL}'
    f'            transform: translateY(-4px) scale(1.02) !important;{NL}{NL}'
    f'            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25) !important;{NL}{NL}'
    f'        }}{NL}{NL}{NL}{NL}'
    f'        /* Login card - First button */{NL}{NL}'
    f'        div.stButton:nth-of-type(1) > button {{{NL}{NL}'
    f'            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;{NL}{NL}'
    f'            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3) !important;{NL}{NL}'
    f'        }}{NL}{NL}{NL}{NL}'
    f'        div.stButton:nth-of-type(1) > button:hover {{{NL}{NL}'
    f'            box-shadow: 0 16px 32px rgba(102, 126, 234, 0.5) !important;{NL}{NL}'
    f'        }}{NL}{NL}{NL}{NL}'
    f'        /* Register card - Second button */{NL}{NL}'
    f'        div.stButton:nth-of-type(2) > button {{{NL}{NL}'
    f'            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;{NL}{NL}'
    f'            box-shadow: 0 8px 20px rgba(245, 87, 108, 0.3) !important;{NL}{NL}'
    f'        }}{NL}{NL}{NL}{NL}'
    f'        div.stButton:nth-of-type(2) > button:hover {{{NL}{NL}'
    f'            box-shadow: 0 16px 32px rgba(245, 87, 108, 0.5) !important;{NL}{NL}'
    f'        }}{NL}{NL}{NL}{NL}'
    f'        /* Booking card - Third button */{NL}{NL}'
    f'        div.stButton:nth-of-type(3) > button {{{NL}{NL}'
    f'            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;{NL}{NL}'
    f'            box-shadow: 0 8px 20px rgba(79, 172, 254, 0.3) !important;{NL}{NL}'
    f'        }}{NL}{NL}{NL}{NL}'
    f'        div.stButton:nth-of-type(3) > button:hover {{{NL}{NL}'
    f'            box-shadow: 0 16px 32px rgba(79, 172, 254, 0.5) !important;{NL}{NL}'
    f'        }}'
)

new_block = (
    f'            border: 1px solid rgba(197,159,85,0.22) !important;{NL}{NL}'
    f'            transition: all 0.3s ease !important;{NL}{NL}'
    f'            white-space: pre-line !important;{NL}{NL}'
    f'            line-height: 1.8 !important;{NL}{NL}'
    f'            padding: 40px 20px !important;{NL}{NL}'
    f'            display: flex !important;{NL}{NL}'
    f'            align-items: center !important;{NL}{NL}'
    f'            justify-content: center !important;{NL}{NL}'
    f'            flex-direction: column !important;{NL}{NL}'
    f'            text-align: center !important;{NL}{NL}'
    f'            color: #f5f0e8 !important;{NL}{NL}'
    f'            cursor: pointer !important;{NL}{NL}'
    f'            background: #141414 !important;{NL}{NL}'
    f'        }}{NL}{NL}{NL}{NL}'
    f'        /* Hover effects - scale and gold glow */{NL}{NL}'
    f'        div.stButton > button:hover {{{NL}{NL}'
    f'            transform: translateY(-4px) scale(1.02) !important;{NL}{NL}'
    f'            border-color: #c5a028 !important;{NL}{NL}'
    f'            background: #1e1a0e !important;{NL}{NL}'
    f'            box-shadow: 0 12px 28px rgba(197,160,40,0.25) !important;{NL}{NL}'
    f'        }}{NL}{NL}{NL}{NL}'
    f'        /* Login card */{NL}{NL}'
    f'        div.stButton:nth-of-type(1) > button {{{NL}{NL}'
    f'            box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;{NL}{NL}'
    f'        }}{NL}{NL}{NL}{NL}'
    f'        /* Register card */{NL}{NL}'
    f'        div.stButton:nth-of-type(2) > button {{{NL}{NL}'
    f'            box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;{NL}{NL}'
    f'        }}{NL}{NL}{NL}{NL}'
    f'        /* Booking card */{NL}{NL}'
    f'        div.stButton:nth-of-type(3) > button {{{NL}{NL}'
    f'            box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;{NL}{NL}'
    f'        }}'
)

if old_block in content:
    content = content.replace(old_block, new_block, 1)
    print('HOME CARDS: replaced OK')
else:
    print('HOME CARDS: NOT FOUND')
    # Find nearest match
    check = 'background: linear-gradient(135deg, #4facfe'
    idx = content.find(check)
    if idx != -1:
        print(f'cyan grad found at char {idx}: {repr(content[idx-200:idx+100])}')

with open('app.py', 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('Done')
