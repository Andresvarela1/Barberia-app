#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reparación final exhaustiva de UTF-8 mojibake
"""

def repair_mojibake_aggressive(filepath):
    """
    Intenta reparar mojibake de múltiples formas
    """
    try:
        with open(filepath, 'rb') as f:
            raw_bytes = f.read()
        
        # Decodificar como UTF-8 (puede haber sustituciones)
        text = raw_bytes.decode('utf-8', errors='replace')
        
        # Buscar patrones conocidos de mojibake
        problematic = ['Ã', '', '', '', 'æ']
        count_before = sum(text.count(c) for c in problematic)
        
        if count_before > 0:
            # Intento 1: interpretar como latin1 y recodificar a utf8
            try:
                text_latin1_bytes = text.encode('latin1')
                text_utf8_fixed = text_latin1_bytes.decode('utf-8', errors='ignore')
                count_after = sum(text_utf8_fixed.count(c) for c in problematic)
                
                if count_after < count_before:
                    text = text_utf8_fixed
                    print(f"✅ {filepath}: Método latin1→utf8 ({count_before}→{count_after} chars)")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(text)
                    return True
            except:
                pass
            
            # Intento 2: reemplazar patrones conocidos directamente
            replacements = {
                'í': 'í', 'ó': 'ó', 'á': 'á', 'é': 'é',
                'ñ': 'ñ', 'Ã¹': 'ù', 'Ã': 'Á', 'é': 'É',
            }
            for bad, good in replacements.items():
                if bad in text:
                    text = text.replace(bad, good)
            
            count_final = sum(text.count(c) for c in problematic)
            if count_final < count_before:
                print(f"✅ {filepath}: Método reemplazos ({count_before}→{count_final} chars)")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text)
                return True
    
    except Exception as e:
        print(f"❌ Error en {filepath}: {e}")
    
    return False

if __name__ == '__main__':
    import os
    
    files = ['app.py', 'design_system.py', 'repair_utf8.py', 'repair_emojis_final.py']
    
    print("Reparando mojibake exhaustivamente...")
    for filename in files:
        if os.path.exists(filename):
            repair_mojibake_aggressive(filename)
        else:
            print(f"⚠  {filename} no encontrado")
    
    print("\n✅ Reparación finalizada")
