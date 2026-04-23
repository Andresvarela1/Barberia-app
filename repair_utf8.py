#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de reparación de UTF-8 mojibake
Detecta y repara corrupción de doble encoding
"""

import os
import re
import sys
from pathlib import Path
from typing import Tuple, Dict, List

# Patrones de corrupción UTF-8
MOJIBAKE_PATTERNS = {
    r'í': '',
    r'ó': '',
    r'á': '',
    r'é': '',
    r'ñ': '',
    r' ': '',
    r'🎯': '🎯',
    r'✅': '✅',
    r'✂️': '✂️',
    r'🎯š¨': '🚨',
    r'❌': '❌',
    r'🎯"Œ': '📌',
    r'⚠️': '⚠️',
}

def detect_mojibake(text: str) -> bool:
    """Detecta si hay mojibake en el texto"""
    return any(pattern in text for pattern in MOJIBAKE_PATTERNS.keys())

def repair_mojibake(text: str) -> str:
    """Repara mojibake usando los patrones conocidos"""
    result = text
    for corrupted, correct in MOJIBAKE_PATTERNS.items():
        result = result.replace(corrupted, correct)
    return result

def try_recover_mojibake(text: str) -> Tuple[str, bool]:
    """
    Intenta recuperar mojibake usando encode/decode
    Retorna: (texto_reparado, fue_necesario_reparar)
    """
    if not detect_mojibake(text):
        return text, False
    
    try:
        # Intentar recuperación usando latin1->utf8
        recovered = text.encode('latin1').decode('utf-8', errors='ignore')
        
        # Si el resultado es mejor, usar ese
        if detect_mojibake(text) and not detect_mojibake(recovered):
            return recovered, True
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    
    # Fallback: usar patrones conocidos
    recovered = repair_mojibake(text)
    return recovered, detect_mojibake(text) and recovered != text

def process_file(filepath: str, dry_run: bool = True) -> Dict:
    """
    Procesa un archivo para reparar UTF-8
    dry_run=True: no escribe cambios
    """
    result = {
        'file': filepath,
        'had_mojibake': False,
        'changes_made': 0,
        'lines_affected': [],
        'original_size': 0,
        'repaired_size': 0,
        'success': False,
        'error': None
    }
    
    try:
        # Leer archivo
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        result['original_size'] = len(original_content)
        
        if not detect_mojibake(original_content):
            result['success'] = True
            return result
        
        result['had_mojibake'] = True
        
        # Reparar línea por línea
        lines = original_content.split('\n')
        repaired_lines = []
        changes = 0
        
        for i, line in enumerate(lines, 1):
            if detect_mojibake(line):
                repaired_line, was_changed = try_recover_mojibake(line)
                if was_changed:
                    repaired_lines.append(repaired_line)
                    changes += 1
                    result['lines_affected'].append(i)
                else:
                    repaired_lines.append(line)
            else:
                repaired_lines.append(line)
        
        repaired_content = '\n'.join(repaired_lines)
        result['repaired_size'] = len(repaired_content)
        result['changes_made'] = changes
        
        # Verificar que no hay regresión
        if not detect_mojibake(repaired_content):
            if not dry_run:
                # Hacer backup
                backup_path = filepath + '.backup_utf8'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # Escribir archivo reparado
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(repaired_content)
                
                print(f"✅ {filepath}")
                print(f"   Backup: {backup_path}")
                print(f"   Cambios: {changes} líneas reparadas")
            else:
                print(f"🔍 DRY RUN - {filepath}")
                print(f"   Cambios necesarios: {changes} líneas")
            
            result['success'] = True
        else:
            result['error'] = "Aún contiene mojibake después de reparación"
            print(f"❌ {filepath}: {result['error']}")
    
    except Exception as e:
        result['error'] = str(e)
        print(f"❌ Error procesando {filepath}: {e}")
    
    return result

def scan_project(root_dir: str, dry_run: bool = True) -> None:
    """
    Escanea y repara todo el proyecto
    """
    print("=" * 70)
    print("REPARACIÓN DE UTF-8 MOJIBAKE")
    print("=" * 70)
    print(f"Root: {root_dir}")
    print(f"Modo: {'DRY RUN (sin cambios)' if dry_run else 'REPARACIÓN ACTIVA'}")
    print()
    
    # Extensiones a procesar
    extensions = ['.py', '.md', '.css', '.js', '.json']
    
    # Directorios a ignorar
    ignore_dirs = {'.git', '.venv', '__pycache__', '.cursor', 'backup_before_utf8_repair'}
    
    results = []
    total_changes = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Filtrar directorios
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            # Filtrar por extensión
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, root_dir)
                
                result = process_file(filepath, dry_run=dry_run)
                if result['had_mojibake']:
                    results.append(result)
                    total_changes += result['changes_made']
    
    # Resumen
    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    if results:
        print(f"Archivos con mojibake: {len(results)}")
        print(f"Total de cambios: {total_changes}")
        print()
        for r in results:
            if r['had_mojibake']:
                status = "✅" if r['success'] else "❌"
                print(f"{status} {r['file']}")
                print(f"   Líneas: {r['lines_affected']}")
    else:
        print("✅ No se encontró mojibake")
    
    if dry_run:
        print()
        print("🔍 Para aplicar reparaciones, ejecutar:")
        print(f"   python repair_utf8.py --apply")

if __name__ == '__main__':
    project_root = os.path.dirname(os.path.abspath(__file__))
    dry_run = '--apply' not in sys.argv
    
    scan_project(project_root, dry_run=dry_run)
