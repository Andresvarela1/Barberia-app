# Reparación directa
import sys

# Forzar salida en utf-8 para ver los caracteres en consola
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

replacements = {
    "Ãndice": "índice",
    "Ãndices": "índices",
    "vÃ¡lido": "válido",
    "Ã³": "ó",
    "Ã¡": "á",
    "Ã©": "é",
    "Ã­": "í",
    "Ã±": "ñ"
}

try:
    with open('app.py', 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            print(f"Reparado: {old}")

    with open('app.py', 'wb') as f:
        f.write(content.encode('utf-8'))
    print("Fin")
except Exception as e:
    print(f"Error: {e}")
