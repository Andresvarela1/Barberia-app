#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de reparación final de UTF-8 - Emojis corruptos
"""

import os
import re

# Mapeo de secuencias corruptas a caracteres correctos
CORRUPTION_MAP = {
    '⚠ ï¸': '⚠️',    # Variante con espacio
    '❌': '❌',       # Este ya está bien
    'Ÿš¨': '🚨',    # Security warning emoji
    'Ÿ': '🎯',      # Targeting emoji variante
}

def repair_file(filepath):
    """Repara emojis corruptos en un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Reemplazar secuencias corruptas conocidas
        for corrupt, correct in CORRUPTION_MAP.items():
            content = content.replace(corrupt, correct)
        
        # Si hubo cambios, guardar
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error en {filepath}: {e}")
        return False

# Archivos a reparar
target_files = [
    'app.py',
    'repair_utf8.py',
    'design_system.py',
]

project_root = os.path.dirname(os.path.abspath(__file__))

print("Reparando emojis corruptos...")
for filename in target_files:
    filepath = os.path.join(project_root, filename)
    if os.path.exists(filepath):
        if repair_file(filepath):
            print(f"✅ {filename}")
        else:
            print(f"✓ {filename} (sin cambios)")
    else:
        print(f"⚠ {filename} (no encontrado)")

print("\nDone!")
