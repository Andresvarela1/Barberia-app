#!/usr/bin/env python3
"""
Helper script to add test barberias with slugs for multi-barberia testing
Run this to populate sample barberia data
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "barberia_db")
DB_PORT = os.getenv("DB_PORT", "5432")

# Sample barberia data
BARBERIAS = [
    ("Leveling Spa", "leveling-spa"),
    ("Premium Cuts", "premium-cuts"),
    ("Modern Barber Shop", "modern-barber-shop"),
    ("Classic Barbershop", "classic-barbershop"),
]

def main():
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cur = conn.cursor()
        
        print("✅ Connected to database")
        print(f"   Host: {DB_HOST}")
        print(f"   Database: {DB_NAME}")
        print()
        
        # Insert sample barberias
        for nombre, slug in BARBERIAS:
            try:
                cur.execute(
                    """
                    INSERT INTO barberias (nombre, slug)
                    VALUES (%s, %s)
                    ON CONFLICT (nombre) DO UPDATE
                    SET slug = EXCLUDED.slug
                    """
                )
                print(f"✅ {nombre:25} → ?barberia={slug}")
            except Exception as e:
                print(f"⚠️  {nombre:25} - Error: {str(e)}")
        
        conn.commit()
        print()
        print("=" * 60)
        print("✅ TEST DATA ADDED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("🔗 Test URLs:")
        print("   Home Screen:")
        print("   → http://localhost:8502")
        print()
        print("   Public Booking (by barberia):")
        for _, slug in BARBERIAS:
            print(f"   → http://localhost:8502?barberia={slug}")
        print()
        print("📝 Notes:")
        print("   • Remove the ?barberia parameter to see the home screen")
        print("   • Use login credentials to access admin dashboard")
        print("   • Try different barberia URLs to test multi-barberia mode")
        print()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("   1. Check .env file has correct DB credentials")
        print("   2. Ensure PostgreSQL is running")
        print("   3. Verify barberias table exists")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
