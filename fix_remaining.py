# Reparación mejorada de mojibakes y emojis
import re

replacements = {
    "Ãndice": "índice",
    "Ãndices": "índices",
    "vÃ¡lido": "válido",
    "Ã³": "ó",
    "Ã¡": "á",
    "Ã©": "é",
    "Ã­": "í",
    "Ã±": "ñ",
    "ðŸ\"Œ": "📍",
    "âš ï¸": "⚠️",
    "âŒ": "❌",
    "ðŸ\"": "📋",
}

with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

count = 0
for old, new in replacements.items():
    if old in content:
        c = content.count(old)
        content = content.replace(old, new)
        count += c
        print(f"✓ Reparado: {old} -> {new} ({c} ocurrencias)")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Reparación completada ({count} cambios en total)")
