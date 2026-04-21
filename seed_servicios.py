"""
Seed script to populate servicios table with default services for barberias.

Usage:
    python seed_servicios.py

This script adds default services to all barberias in the database.
You can customize the servicios list to match your business needs.
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
_dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=_dotenv_path)

def get_database_url():
    return os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")

def get_connection():
    """Create database connection."""
    database_url = get_database_url()
    if not database_url:
        print("❌ ERROR: DATABASE_URL or SUPABASE_DB_URL not configured")
        return None
    
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

# Default services with icons and descriptions
DEFAULT_SERVICIOS = [
    {
        "nombre": "Corte",
        "duracion_minutos": 45,
        "precio": 15000,
        "descripcion": "Corte de cabello profesional",
        "icono": "✂️"
    },
    {
        "nombre": "Barba",
        "duracion_minutos": 30,
        "precio": 10000,
        "descripcion": "Arreglo y afeitada de barba",
        "icono": "💈"
    },
    {
        "nombre": "Corte + Barba",
        "duracion_minutos": 60,
        "precio": 20000,
        "descripcion": "Combo completo de servicios",
        "icono": "⭐"
    },
    {
        "nombre": "Fade",
        "duracion_minutos": 40,
        "precio": 12000,
        "descripcion": "Corte fade moderno y detallado",
        "icono": "🎯"
    },
    {
        "nombre": "Línea",
        "duracion_minutos": 15,
        "precio": 5000,
        "descripcion": "Perfilado y línea de entradas",
        "icono": "📏"
    }
]

def seed_servicios():
    """Add default services to all barberias."""
    conn = get_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cur:
            # Get all barberias
            cur.execute("SELECT id, nombre FROM barberias ORDER BY id")
            barberias = cur.fetchall()
            
            if not barberias:
                print("❌ No barberias found in database")
                return
            
            print(f"✅ Found {len(barberias)} barberia(s)")
            print("=" * 60)
            
            total_added = 0
            
            for barberia_id, barberia_name in barberias:
                print(f"\n📝 Processing: {barberia_name} (ID: {barberia_id})")
                
                # Check existing services
                cur.execute(
                    "SELECT COUNT(*) FROM servicios WHERE barberia_id = %s",
                    (barberia_id,)
                )
                existing_count = cur.fetchone()[0]
                
                if existing_count > 0:
                    print(f"   ⚠️  Already has {existing_count} service(s) - Skipping")
                    continue
                
                # Insert default services
                added_count = 0
                for servicio in DEFAULT_SERVICIOS:
                    try:
                        cur.execute(
                            """INSERT INTO servicios 
                               (barberia_id, nombre, duracion_minutos, precio, descripcion, icono)
                               VALUES (%s, %s, %s, %s, %s, %s)
                               ON CONFLICT (barberia_id, nombre) DO NOTHING""",
                            (
                                barberia_id,
                                servicio["nombre"],
                                servicio["duracion_minutos"],
                                servicio["precio"],
                                servicio["descripcion"],
                                servicio["icono"]
                            )
                        )
                        added_count += 1
                    except Exception as e:
                        print(f"   ❌ Error adding {servicio['nombre']}: {e}")
                
                conn.commit()
                print(f"   ✅ Added {added_count} service(s)")
                total_added += added_count
            
            print("\n" + "=" * 60)
            print(f"✅ TOTAL SERVICES ADDED: {total_added}")
            print("=" * 60)
            print("\n💡 Tips:")
            print("   • Services are now visible on public landing pages")
            print("   • You can edit services in the admin dashboard")
            print("   • Prices are in cents (15000 = $15,000 COP)")
            print("   • Durations in minutes affect booking time slots")
    
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🌱 Seeding servicios table with default services...")
    print()
    seed_servicios()
