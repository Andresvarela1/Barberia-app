# Controlado: SOLO reemplazos específicos de caracteres corruptos visibles
replacements = {
    "BarberÃ­a": "Barbería",
    "barberÃ­a": "barbería",
    "sesiÃ³n": "sesión",
    "configuraciÃ³n": "configuración",
    "cÃ³digo": "código",
    "conexiÃ³n": "conexión",
    "crÃ­tico": "crítico",
    "despuÃ©s": "después",
    "RestricciÃ³n": "Restricción",
    "restricciÃ³n": "restricción",
    "aÃ±adida": "añadida",
    "aÃ±adiendo": "añadiendo",
    "aÃ±adidas": "añadidas",
    "contraseÃ±a": "contraseña",
    "Ã­ndice": "índice",
    "Ã­ndices": "índices",
    "continuarÃ¡": "continuará",
    "IluminaciÃ³n": "Iluminación",
    "iluminaciÃ³n": "iluminación",
    "prestaciÃ³n": "prestación",
    "aÃ±os": "años",
    "taÃ±o": "taño",
}

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

for old, new in replacements.items():
    if old in content:
        content = content.replace(old, new)
        print(f"✓ Reemplazado: {old} → {new}")
    else:
        print(f"✗ No encontrado: {old}")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Reparación completada")
