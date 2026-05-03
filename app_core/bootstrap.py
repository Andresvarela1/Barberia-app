"""Database bootstrap: DDL table creation, seed data, barberia initialisation.

Extracted from app.py.  All public names keep their original signatures so
existing callers in app.py and tests need no changes.
"""

import logging
import os

import streamlit as st

from app_core.db.connection import get_connection, get_database_url
from app_core.db.safe_queries import fetch_one, execute_write, safe_execute, safe_fetch_one
from app_core.auth import hash_password

logger = logging.getLogger("barberia_app")


# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------

def ensure_database_tables():
    """Create application tables if they are missing; commit on success."""
    conn = None
    all_ok = True
    try:
        conn = get_connection()
        if conn is None:
            st.warning("Base de datos no disponible, modo demo activo")
            return

        with conn.cursor() as cur:
            # 1. barberias table
            try:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS barberias (
                        id SERIAL PRIMARY KEY,
                        nombre TEXT NOT NULL UNIQUE,
                        slug TEXT UNIQUE
                    );
                    """
                )
                conn.commit()
                logger.info("[OK] Tabla 'barberias' creada o ya existe")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error creando tabla 'barberias': {e}")
                st.error(f"Error creando tabla 'barberias': {e}")

            # 2. usuarios table
            try:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id SERIAL PRIMARY KEY,
                        usuario TEXT NOT NULL,
                        password TEXT NOT NULL,
                        rol TEXT NOT NULL,
                        telefono TEXT,
                        cortes_acumulados INTEGER NOT NULL DEFAULT 0,
                        barberia_id INTEGER,
                        CONSTRAINT fk_usuarios_barberia
                            FOREIGN KEY (barberia_id)
                            REFERENCES barberias(id)
                            ON DELETE RESTRICT
                    );
                    """
                )
                conn.commit()
                logger.info("[OK] Tabla 'usuarios' creada o ya existe")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error creando tabla 'usuarios': {e}")
                st.error(f"Error creando tabla 'usuarios': {e}")

            # Add UNIQUE constraint on usuario if not exists
            try:
                cur.execute(
                    """
                    SELECT conname
                    FROM pg_constraint
                    WHERE conname = 'usuarios_usuario_unique'
                    AND conrelid = 'public.usuarios'::regclass
                    LIMIT 1;
                    """
                )
                constraint_exists = cur.fetchone()

                if not constraint_exists:
                    try:
                        cur.execute(
                            "ALTER TABLE usuarios ADD CONSTRAINT usuarios_usuario_unique UNIQUE (usuario);"
                        )
                        logger.info(" Restricción UNIQUE en 'usuario' añadida")
                    except Exception as constraint_error:
                        if "already exists" in str(constraint_error).lower() or "duplicate" in str(constraint_error).lower():
                            logger.info(" Restricción UNIQUE en 'usuario' ya existe (race condition handled)")
                        else:
                            raise constraint_error
                else:
                    logger.info(" Restricción UNIQUE en 'usuario' ya existe")

                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.warning(f"Advertencia creando restricción UNIQUE (continuando): {e}")
                if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
                    st.warning(f"Restricción UNIQUE no pudo crearse (app continuará): {e}")

            # Index on usuarios
            try:
                cur.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_barberia ON usuarios(barberia_id);")
                conn.commit()
                logger.info(" Índice 'idx_usuarios_barberia' creado o ya existe")
                logger.info("[OK] Índice 'idx_usuarios_barberia' creado o ya existe")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error creando índice 'idx_usuarios_barberia': {e}")
                st.error(f"Error creando índice 'idx_usuarios_barberia': {e}")

            # 3. reservas table
            try:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS reservas (
                        id SERIAL PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        barbero TEXT NOT NULL,
                        servicio TEXT NOT NULL,
                        precio INTEGER NOT NULL,
                        inicio TIMESTAMP NOT NULL,
                        fin TIMESTAMP NOT NULL,
                        barberia_id INTEGER NOT NULL,
                        CONSTRAINT fk_reservas_barberia
                            FOREIGN KEY (barberia_id)
                            REFERENCES barberias(id)
                            ON DELETE RESTRICT
                    );
                    """
                )
                conn.commit()
                logger.info("[OK] Tabla 'reservas' creada o ya existe")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error creando tabla 'reservas': {e}")
                st.error(f"Error creando tabla 'reservas': {e}")

            # 4. servicios table
            try:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS servicios (
                        id SERIAL PRIMARY KEY,
                        barberia_id INTEGER NOT NULL,
                        nombre TEXT NOT NULL,
                        duracion_minutos INTEGER NOT NULL,
                        precio INTEGER NOT NULL,
                        descripcion TEXT,
                        icono TEXT DEFAULT 'Servicio',
                        CONSTRAINT fk_servicios_barberia
                            FOREIGN KEY (barberia_id)
                            REFERENCES barberias(id)
                            ON DELETE CASCADE,
                        UNIQUE(barberia_id, nombre)
                    );
                    """
                )
                conn.commit()
                logger.info("[OK] Tabla 'servicios' creada o ya existe")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error creando tabla 'servicios': {e}")
                st.error(f"Error creando tabla 'servicios': {e}")

            # Index on servicios
            try:
                cur.execute("CREATE INDEX IF NOT EXISTS idx_servicios_barberia ON servicios(barberia_id);")
                conn.commit()
                logger.info("[OK] Índice 'idx_servicios_barberia' creado o ya existe")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error creando índice 'idx_servicios_barberia': {e}")
                st.error(f"Error creando índice 'idx_servicios_barberia': {e}")

            # Optional columns for barberias
            try:
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS slug TEXT UNIQUE;")
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS telefono TEXT;")
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS email TEXT;")
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS ciudad TEXT;")
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS direccion TEXT;")
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS latitud NUMERIC(10, 6);")
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS longitud NUMERIC(10, 6);")
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS logo_url TEXT;")
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS color_primario TEXT DEFAULT '#667eea';")
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS hora_apertura TIME DEFAULT '09:00:00';")
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS hora_cierre TIME DEFAULT '18:00:00';")
                cur.execute("ALTER TABLE barberias ADD COLUMN IF NOT EXISTS estado TEXT DEFAULT 'activa';")
                conn.commit()
                logger.info("[OK] Columnas en tabla 'barberias' aseguradas")
            except Exception as e:
                conn.rollback()
                logger.warning(f"[AVISO] Error añadiendo columnas a barberias: {e}")

            # Optional columns for usuarios
            try:
                cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS nombre TEXT;")
                cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS apellido TEXT;")
                conn.commit()
                logger.info("[OK] Columnas en tabla 'usuarios' aseguradas")
            except Exception as e:
                conn.rollback()
                logger.warning(f"[AVISO] Error añadiendo columnas a usuarios: {e}")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_reservas_barbero_id ON reservas(barbero_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_reservas_fecha ON reservas(fecha);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_reservas_inicio ON reservas(inicio);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_reservas_pagado ON reservas(pagado);")
                conn.commit()
                logger.info("[OK] Índices de 'reservas' creados o ya existen")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error creando índices de 'reservas': {e}")

            # Optional columns for reservas
            try:
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS cliente TEXT;")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS fecha DATE;")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS hora TIME;")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS estado TEXT DEFAULT 'activo';")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS pagado BOOLEAN NOT NULL DEFAULT FALSE;")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS monto INTEGER;")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS payment_id TEXT;")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS barbero_id INTEGER;")
                cur.execute("UPDATE reservas SET monto = precio WHERE monto IS NULL;")
                conn.commit()
                logger.info("[OK] Columnas opcionales en 'reservas' añadidas o actualizadas")
                logger.info("[OK] payment_id column ensured")
                logger.info("[OK] updated_at column ensured")
                logger.info("[OK] barbero_id column ensured")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error alterando tabla 'reservas': {e}")

            # Ensure servicios has all required columns for multi-tenant
            try:
                cur.execute("ALTER TABLE servicios ADD COLUMN IF NOT EXISTS icono TEXT DEFAULT 'Servicio';")
                cur.execute("ALTER TABLE servicios ADD COLUMN IF NOT EXISTS descripcion TEXT;")
                conn.commit()
                logger.info("[OK] Columnas en tabla 'servicios' aseguradas")
            except Exception as e:
                conn.rollback()
                logger.warning(f"[AVISO] Error añadiendo columnas a servicios: {e}")

        if all_ok:
            logger.info("[OK] Todas las tablas y restricciones creadas correctamente")
        else:
            logger.warning("[AVISO] Algunas operaciones de base de datos fallaron")

    except Exception as e:
        if conn:
            conn.rollback()
        logger.exception("Error al asegurar tablas de base de datos")
    finally:
        # Don't close connection - keep it in session state
        pass


# ---------------------------------------------------------------------------
# Barberia initialisation (cached)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300)
def inicializar_barberia():
    if not get_database_url():
        return None

    row = fetch_one("SELECT id FROM barberias WHERE nombre = %s", ("Barberia Leveling",))
    if row and row[0]:
        return row[0]

    row = fetch_one("SELECT id FROM barberias ORDER BY id LIMIT 1")
    if row and row[0]:
        return row[0]

    created = execute_write(
        "INSERT INTO barberias (nombre) VALUES (%s) RETURNING id",
        ("Barbería Principal",),
        fetch_one_result=True,
    )
    if not created or not created[0]:
        logger.error(
            "No se pudo inicializar la barbería por defecto. "
            "Verifica la conexión/credenciales y que exista la tabla 'barberias'."
        )
        return None
    return created[0]


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

def seed_default_data():
    """Datos iniciales: super admin, barbería Leveling, barberos (solo si faltan)."""
    if not get_database_url():
        logger.warning("[AVISO] DATABASE_URL no configurada - seed_default_data ignorado")
        return False

    conn = None
    try:
        conn = get_connection(notify_missing_url=False)
        if conn is None:
            logger.warning("[AVISO] No se pudo conectar a la BD - seed_default_data ignorado")
            return False

        with conn.cursor() as cur:
            # 1. Crear barbería Leveling si no existe
            logger.info("Verificando Verificando si barbería 'Barberia Leveling' existe...")
            cur.execute("SELECT id FROM barberias WHERE nombre = %s", ("Barberia Leveling",))
            barberia_row = cur.fetchone()
            if barberia_row:
                bid = barberia_row[0]
                logger.info(f"[OK] Barbería Leveling ya existe (ID: {bid})")
            else:
                logger.info("[AVISO] Barbería Leveling NO existe - creando...")
                cur.execute(
                    "INSERT INTO barberias (nombre) VALUES (%s) RETURNING id",
                    ("Barberia Leveling",),
                )
                barberia_row = cur.fetchone()
                if barberia_row and barberia_row[0]:
                    bid = barberia_row[0]
                    logger.info(f"[OK] Barbería Leveling creada con ID: {bid}")
                else:
                    raise Exception("No se pudo crear la barbería por defecto")

            # 2. Crear SUPER_ADMIN si no existe
            logger.info("Verificando Verificando si SUPER_ADMIN 'JoanBeatsAD' existe...")
            cur.execute("SELECT id FROM usuarios WHERE usuario = %s", ("JoanBeatsAD",))
            super_admin_row = cur.fetchone()
            if super_admin_row:
                logger.info(f"[OK] SUPER_ADMIN 'JoanBeatsAD' ya existe (ID: {super_admin_row[0]})")
            else:
                logger.info("[AVISO] SUPER_ADMIN 'JoanBeatsAD' NO existe - creando...")
                password_hash = hash_password("suguha09")
                cur.execute(
                    "INSERT INTO usuarios (usuario, password, rol, barberia_id) VALUES (%s, %s, %s, %s)",
                    ("JoanBeatsAD", password_hash, "SUPER_ADMIN", None),
                )
                logger.info("[OK] INSERT SUPER_ADMIN ejecutado")

            # 3. Crear barberos si no existen
            logger.info("Verificando Verificando barberos...")
            pwd_barb = hash_password("barbero123")
            for bu in ("Yor", "Andres", "Andrea", "Maikel"):
                cur.execute("SELECT id FROM usuarios WHERE usuario = %s", (bu,))
                if cur.fetchone():
                    logger.info(f"[OK] Barbero '{bu}' ya existe")
                    continue
                cur.execute(
                    "INSERT INTO usuarios (usuario, password, rol, telefono, barberia_id, cortes_acumulados) VALUES (%s, %s, %s, %s, %s, %s)",
                    (bu, pwd_barb, "BARBERO", None, bid, 0),
                )
                logger.info(f"[OK] Barbero '{bu}' creado")

        conn.commit()
        logger.info("[OK] Commit exitoso - verificando SUPER_ADMIN...")

        try:
            user_check = fetch_one("SELECT id FROM usuarios WHERE usuario = %s", ("JoanBeatsAD",))
            if user_check:
                logger.info("[OK] SUPER_ADMIN listo en la base de datos")
                return True
            logger.error("SUPER_ADMIN no se pudo crear")
            return False
        except Exception as e:
            logger.error(f"Seed error: {str(e)}")
            return False

    except Exception as e:
        if conn:
            conn.rollback()
        logger.exception("[ERROR] Error en seed_default_data")
        logger.error(f"Seed error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()
