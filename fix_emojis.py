import re

# Reemplazos específicos de emojis corruptos
emoji_replacements = {
    "âœ‚ï¸": "✂️",   # Scissors
    "âœ…": "✅",      # Check mark
    "ðŸ\x8d\x8c": "📍",    # Location pin (Using hex to avoid escape issues)
    "ðŸš¨": "🚨",    # Siren/Alert
    "âš ï¸": "⚠️",   # Warning
}

# Add the specific corrupt string if hex isn't enough
# The previous error showed "ðŸ"Œ"
# Let's try raw strings or just fixing the file content directly
content = ""
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Manual string replacements for the most likely corruptions
content = content.replace("âœ‚ï¸", "✂️")
content = content.replace("âœ…", "✅")
content = content.replace("ðŸ\x8d\x8c", "📍")
content = content.replace("ðŸš¨", "🚨")
content = content.replace("âš ï¸", "⚠️")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Reparación de emojis completada")
