import os

# Mapeo de fragmentos corruptos a emojis reales
emoji_fixes = {
    "âšï¸": "⚠️",
}

file_path = 'app.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

fixed_count = 0
for old, new in emoji_fixes.items():
    if old in content:
        count = content.count(old)
        content = content.replace(old, new)
        fixed_count += count
        print(f"✓ '{old}' -> '{new}' ({count} veces)")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Total de reemplazos: {fixed_count}")
