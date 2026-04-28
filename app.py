import streamlit as st

from streamlit_calendar import calendar

from datetime import datetime, timedelta

import logging

import os

import socket

import traceback

from urllib.parse import urlparse

from dotenv import load_dotenv

import bcrypt

import psycopg2

import pandas as pd

from whatsapp import enviar_whatsapp as enviar_whatsapp_twilio

# ==================== DESIGN SYSTEM ====================

from design_system import (

    apply_global_theme,

    apply_layout_css,

    apply_calendar_refinement,

    apply_internal_panel_css,

    apply_public_booking_css,

    Colors,

    Typography,

    Spacing,

    BorderRadius,

    Shadows,

    Gradients,

    render_card,

    render_section_title,

    render_subsection_title,

    render_badge,

    render_stat_box,

    render_alert,

    render_divider,

    render_barber_card,

    render_barber_selector,

    render_time_chips,

    render_metric_grid,

    render_status_legend,

    render_reservation_card,

    render_preview_card,

    render_success_hero,

    render_hero_banner,

    render_loading_panel,

    # Layout wrappers

    render_booking_container,

    close_booking_container,

    render_booking_header,

    render_booking_section,

    render_form_group,

    render_button_group,

    render_step_indicator,

    render_panel_header,

    render_panel_empty_state,

    render_public_landing_hero,

    render_public_section_heading,

    render_public_payment_notice,

    render_public_booking_summary,

    render_public_note,

)

# ==================== UI COMPONENTS ====================

from components.ui_loader import load_css

try:

    import mercadopago

except ImportError:

    mercadopago = None

try:

    from geopy.geocoders import Nominatim

    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

except ImportError:

    Nominatim = None

    GeocoderTimedOut = None

    GeocoderUnavailable = None

_dotenv_path = os.path.join(os.path.dirname(__file__), ".env")

load_dotenv(dotenv_path=_dotenv_path)

st.set_page_config(

    page_title="Barbería Leveling",

    page_icon="Barberia",

    layout="wide",

    initial_sidebar_state="expanded"

)

# ==================== APPLY GLOBAL DESIGN SYSTEM ====================

apply_global_theme()

# ==================== LOAD MODULAR CSS STYLESHEETS ====================

# CSS files loaded in order:

# 1. base.css - Global typography, spacing, buttons, inputs

# 2. sidebar.css - Sidebar navigation and styling

# 3. calendar.css - Calendar and date picker styling

# 4. forms.css - Form components and layouts

# 5. cards.css - Card and container components

# 6. booking.css - Booking flow and step styling

load_css()

apply_layout_css()

apply_calendar_refinement()

# ------------------ LOGGER ------------------

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("barberia_app")

# ------------------ DB ------------------

_db_url_missing_notified = False

def get_database_url():

    return os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")

def _masked_postgres_url(parsed):

    username = parsed.username or ""

    host = parsed.hostname or ""

    port = parsed.port or 5432

    dbname = (parsed.path or "").lstrip("/") or ""

    auth = f"{username}:***@" if username else ""

    db_part = f"/{dbname}" if dbname else ""

    return f"{parsed.scheme}://{auth}{host}:{port}{db_part}"

def create_fresh_connection():

    """Create a fresh database connection."""

    global _db_url_missing_notified

    database_url = get_database_url()

    if not database_url:

        message = (

            "DATABASE_URL o SUPABASE_DB_URL no está configurada. "

            "Define una de estas variables de entorno en el sistema o en la configuración "

            "de despliegue (sin hardcodear credenciales en el código)."

        )

        logger.error(message)

        if not _db_url_missing_notified:

            _db_url_missing_notified = True

        return None

    try:

        database_url = database_url.strip()

        if "[YOUR-PASSWORD]" in database_url:

            return None

        parsed = urlparse(database_url)

        if parsed.scheme not in ("postgresql", "postgres"):

            return None

        host = parsed.hostname

        port = parsed.port or 5432

        dbname = (parsed.path or "").lstrip("/")

        if not host or not dbname:

            return None

        masked = _masked_postgres_url(parsed)

        logger.info("📍 Creando conexión PostgreSQL: %s", masked)

        try:

            socket.getaddrinfo(host, port)

        except socket.gaierror:

            logger.error("Host resolution failed")

            return None

        conn = psycopg2.connect(

            database_url,

            sslmode="require",

            connect_timeout=5,

            options="-c statement_timeout=8000",

        )

        logger.info("[OK] Conexión a DB creada exitosamente")

        return conn

    except Exception as e:

        logger.exception("Error al conectar con PostgreSQL")

        return None

def get_connection(*, notify_missing_url: bool = True):

    """Get safe database connection using session state with minimal overhead."""

    try:

        # Fast path: return existing connection if available and valid

        conn = st.session_state.get("db_connection")

        if conn is not None and not conn.closed:

            return conn


        # Create new connection only when needed

        conn = create_fresh_connection()

        if conn is not None:

            st.session_state.db_connection = conn

        elif notify_missing_url and not _db_url_missing_notified:

            message = (

                "DATABASE_URL o SUPABASE_DB_URL no está configurada. "

                "Define una de estas variables de entorno en el sistema o en la configuración "

                "de despliegue (sin hardcodear credenciales en el código)."

            )

            st.error(message)


        return conn

    except Exception as e:

        logger.exception("Error crítico en get_connection")

        if notify_missing_url:

            st.error("Error de conexión a la base de datos")

        return None

def is_db_available():

    """True if a PostgreSQL connection can be opened."""

    try:

        conn = get_connection(notify_missing_url=False)

        return conn is not None

    except Exception:

        logger.info("Base de datos no disponible (fallo de conexión).", exc_info=True)

        return False

def execute_query(query, params=None, fetch=None):

    """Execute query with safe connection handling."""

    max_retries = 2

    for attempt in range(max_retries):

        conn = None

        try:

            conn = get_connection()

            if conn is None:

                return None


            with conn.cursor() as cur:

                cur.execute(query, params)

                if fetch == "one":

                    data = cur.fetchone()

                elif fetch == "all":

                    data = cur.fetchall()

                else:

                    data = True

            conn.commit()

            return data

        except Exception as e:

            if conn:

                try:

                    conn.rollback()

                except:

                    pass  # Connection might be closed


            if attempt == max_retries - 1:

                logger.exception("Error en base de datos después de reintentos")

                st.error(f"Error en base de datos:\n{traceback.format_exc()}")

                return None

            else:

                logger.warning("[AVISO] Error en base de datos, reintentando... (intento %d)", attempt + 1)

                # Force connection recreation on next attempt

                if "db_connection" in st.session_state:

                    try:

                        st.session_state.db_connection.close()

                    except:

                        pass

                    st.session_state.db_connection = None

        finally:

            # Don't close connection - keep it in session state

            pass

def fetch_one(query, params=None):

    return execute_query(query, params, fetch="one")

def fetch_all(query, params=None):

    return execute_query(query, params, fetch="all") or []

def execute_write(query, params=None, fetch_one_result=False):

    return execute_query(query, params, fetch="one" if fetch_one_result else None)

# ================= STEP 1: SAFE QUERY WRAPPERS WITH BARBERIA_ID ENFORCEMENT =================

def safe_fetch_one(query, params=()):

    """CRITICAL: Query wrapper that ENFORCES barberia_id presence.


    Rule: Every query MUST include 'barberia_id' filter or it raises exception.

    This makes data leakage mathematically impossible.

    """

    query_lower = query.lower()


    # Skip validation for system queries that don't need barberia_id

    system_queries = [

        "SELECT id FROM barberias",

        "SELECT COUNT(*) FROM barberias",

        "SELECT * FROM barberias WHERE estado",

        "FROM barberias WHERE slug",

        "hashtext",  # pg_advisory_xact_lock calls

        "SELECT nombre FROM barberias",

        "SELECT id, nombre FROM barberias",

        "INSERT INTO barberias",

        "SELECT COUNT(*) FROM usuarios WHERE usuario",  # Login query (before barberia context)

        "SELECT * FROM usuarios WHERE usuario",

        "SELECT COUNT(*) FROM usuarios) as num_usuarios",  # Super admin global metrics

        "SELECT COUNT(*) FROM reservas) as num_reservas",  # Super admin global metrics

        "SELECT SUM(monto) FROM reservas WHERE pagado",  # Super admin global metrics

    ]


    # If it's a safe system query, allow it

    if any(safe in query_lower for safe in system_queries):

        return fetch_one(query, params)


    # Otherwise: MUST include barberia_id filter

    if "barberia_id" not in query_lower:

        error_msg = f"🚨 SECURITY VIOLATION: Query missing barberia_id filter!\nQuery: {query[:100]}..."

        logger.error(error_msg)

        raise Exception(error_msg)


    return fetch_one(query, params)

def safe_fetch_all(query, params=()):

    """CRITICAL: Query wrapper that ENFORCES barberia_id presence.


    Rule: Every query MUST include 'barberia_id' filter or it raises exception.

    This makes data leakage mathematically impossible.


    Exception: SUPER_ADMIN with super_admin_all_barberias=True is allowed global queries.

    """

    query_lower = query.lower()


    # Skip validation for system queries

    system_queries = [

        "SELECT id FROM barberias",

        "SELECT id, nombre FROM barberias",

        "SELECT COUNT(*) FROM barberias",

        "FROM barberias WHERE estado",

        "SELECT COUNT(*) FROM usuarios WHERE usuario",

        "ORDER BY nombre",  # Barberia dropdown list

    ]


    if any(safe in query_lower for safe in system_queries):

        return fetch_all(query, params)


    # SUPER_ADMIN global view is allowed

    rol = st.session_state.get("rol")

    super_all = rol == "SUPER_ADMIN" and st.session_state.get("super_admin_all_barberias", False)

    if super_all and "WHERE 1=1" in query:  # Indicates global query pattern

        return fetch_all(query, params)


    # Otherwise: MUST include barberia_id filter

    if "barberia_id" not in query_lower:

        error_msg = f"🚨 SECURITY VIOLATION: Query missing barberia_id filter!\nQuery: {query[:100]}..."

        logger.error(error_msg)

        raise Exception(error_msg)


    return fetch_all(query, params)

def safe_execute(query, params=(), fetch_one_result=False):

    """CRITICAL: Write operation wrapper that ENFORCES barberia_id presence.


    Rule: Every INSERT/UPDATE/DELETE MUST include 'barberia_id' or it raises exception.

    """

    query_lower = query.lower()


    # System operations that don't need barberia_id

    system_ops = [

        "INSERT INTO barberias",

        "INSERT INTO usuarios WHERE barberia_id",

        "CREATE TABLE",

        "ALTER TABLE",

        "INSERT INTO servicios",

    ]


    if any(safe in query_lower for safe in system_ops):

        return execute_write(query, params, fetch_one_result)


    # For user operations: MUST include barberia_id

    if "INSERT INTO" in query_lower or "UPDATE" in query_lower or "DELETE FROM" in query_lower:

        if "barberia_id" not in query_lower:

            error_msg = f"🚨 SECURITY VIOLATION: Write operation missing barberia_id!\nQuery: {query[:100]}..."

            logger.error(error_msg)

            raise Exception(error_msg)


    return execute_write(query, params, fetch_one_result)

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

            # Add UNIQUE constraint on usuario if not exists - safe approach

            try:

                # Check if constraint exists using safer query

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

                    # Use IF NOT EXISTS syntax for PostgreSQL 9.1+ or handle gracefully

                    try:

                        cur.execute(

                            "ALTER TABLE usuarios ADD CONSTRAINT usuarios_usuario_unique UNIQUE (usuario);"

                        )

                        logger.info(" Restricción UNIQUE en 'usuario' añadida")

                    except Exception as constraint_error:

                        # If constraint already exists (race condition), ignore safely

                        if "already exists" in str(constraint_error).lower() or "duplicate" in str(constraint_error).lower():

                            logger.info(" Restricción UNIQUE en 'usuario' ya existe (race condition handled)")

                        else:

                            raise constraint_error

                else:

                    logger.info(" Restricción UNIQUE en 'usuario' ya existe")


                conn.commit()

            except Exception as e:

                conn.rollback()

                # Don't fail the entire table creation for a constraint issue

                logger.warning(f"Advertencia creando restricción UNIQUE (continuando): {e}")

                # Only show error to user if it's a critical issue

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

            # Optional columns

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

# ------------------ DATOS ------------------

barberos = {

    "Andrea": "#FF5733",

    "Andres": "#33C1FF",

    "Yor": "#33FF57",

    "Maikel": "#F333FF"

}

servicios = {

    "Corte": {"duracion": 45, "precio": 15000},

    "Barba": {"duracion": 30, "precio": 10000},

    "Corte + Barba": {"duracion": 60, "precio": 20000}

}

_ROL_LEGACY = {

    "cliente": "CLIENTE",

    "barbero": "BARBERO",

    "admin": "ADMIN",

    "super_admin": "SUPER_ADMIN",

}

def normalizar_rol(rol):

    """Normalize role to always return a valid role."""

    if not rol:

        return "CLIENTE"


    s = str(rol).strip()

    if not s:

        return "CLIENTE"


    low = s.lower()

    mapping = {

        "cliente": "CLIENTE",

        "barbero": "BARBERO", 

        "admin": "ADMIN",

        "super_admin": "SUPER_ADMIN",

        "superadmin": "SUPER_ADMIN",

        "super admin": "SUPER_ADMIN",

        "super-admin": "SUPER_ADMIN"

    }


    return mapping.get(low, "CLIENTE")

def session_barberia_for_write():

    u = st.session_state.get("user")

    if not u:

        return st.session_state.get("barberia_id")

    if normalizar_rol(u[3]) == "SUPER_ADMIN":

        return st.session_state.get("barberia_context_id")

    return st.session_state.get("barberia_id")

def effective_barberia_id():

    u = st.session_state.get("user")

    if not u:

        return st.session_state.get("barberia_id")

    if normalizar_rol(u[3]) == "SUPER_ADMIN":

        return st.session_state.get("barberia_context_id")

    return st.session_state.get("barberia_id")

# ================= STEP 1: SINGLE SOURCE OF TRUTH =================

def get_current_barberia_id():

    """CRITICAL: Single source of truth for barberia_id.


    STEP 5: BLOCK SUPER_ADMIN without context

    - Returns barberia_id or raises exception

    - SUPER_ADMIN MUST have valid context selected

    - Prevents accidental data access to wrong barberia


    Rules:

    - SUPER_ADMIN: MUST have barberia_context_id set (enforced)

    - Others: Use their assigned barberia_id

    - If None: Execution stops immediately

    """

    rol = st.session_state.get("rol")


    if rol == "SUPER_ADMIN":

        context_id = st.session_state.get("barberia_context_id")

        if not context_id:

            error_msg = "🚨 SUPER_ADMIN: Debes seleccionar una barbería antes de continuar"

            logger.error(f"SECURITY BLOCK: SUPER_ADMIN tried to access without context")

            st.error(error_msg)

            st.stop()

        return context_id


    # For non-SUPER_ADMIN users

    barberia_id = st.session_state.get("barberia_id")

    if not barberia_id:

        error_msg = f"🚨 {rol}: No barberia assigned to this user"

        logger.error(f"SECURITY BLOCK: {rol} has no barberia_id")

        st.error(error_msg)

        st.stop()


    return barberia_id

# ================= STEP 2: ACCESS ENFORCEMENT =================

def enforce_access(target_barberia_id):

    """CRITICAL: Block unauthorized barberia access.


    Call this BEFORE every query that uses barberia_id.


    Args:

        target_barberia_id: The barberia_id being accessed


    Raises:

        st.error() + st.stop() if unauthorized

    """

    current_id = get_current_barberia_id()

    if not current_id:

        st.error("No barbería seleccionada")

        st.stop()

    if target_barberia_id != current_id:

        st.error("No tienes permiso para acceder a esta barbería")

        logger.warning(f"🚨 ACCESS DENIED: Current={current_id}, Target={target_barberia_id}, Role={st.session_state.get('rol')}")

        st.stop()

# ================= DATA ISOLATION & MULTI-TENANT SECURITY =================

def get_user_barberia_id():

    """Get the barberia_id of the current user. Returns None if not set."""

    return st.session_state.get("barberia_id")

def get_user_role():

    """Get the normalized role of the current user."""

    return st.session_state.get("rol", "CLIENTE")

def can_access_barberia(target_barberia_id):

    """Check if current user can access a specific barberia.


    Returns True if:

    - User is SUPER_ADMIN

    - User's barberia_id matches target_barberia_id

    """

    user_role = get_user_role()

    if user_role == "SUPER_ADMIN":

        return True


    user_barberia = get_user_barberia_id()

    if not user_barberia or not target_barberia_id:

        return False


    return user_barberia == target_barberia_id

def enforce_barberia_access(target_barberia_id):

    """Enforce barberia access control. Raises error if user cannot access.


    Args:

        target_barberia_id: The barberia_id to check access for


    Raises:

        PermissionError: If user doesn't have access

    """

    if not can_access_barberia(target_barberia_id):

        user_role = get_user_role()

        user_barberia = get_user_barberia_id()

        logger.warning(f"🚨 UNAUTHORIZED ACCESS ATTEMPT: Role={user_role}, UserBarberia={user_barberia}, TargetBarberia={target_barberia_id}")

        st.error(f"No tienes permiso para acceder a esta barbería")

        st.stop()

def get_user_id():

    """Get the user_id of the current user from session state."""

    return st.session_state.get("user_id")

# ------------------ FUNCIONES ------------------

def normalizar_texto(valor):

    return valor.strip() if isinstance(valor, str) else ""

def es_hash_bcrypt(valor):

    return isinstance(valor, str) and valor.startswith(("$2a$", "$2b$", "$2y$"))

def hash_password(password):

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verificar_password(password, password_guardada):

    """Verifica contraseña contra hash bcrypt o plain text."""

    if not password_guardada:

        logger.warning("[ERROR] No hay contraseña guardada")

        return False

    if es_hash_bcrypt(password_guardada):

        try:

            # El hash está en formato bcrypt

            resultado = bcrypt.checkpw(

                password.encode("utf-8"),

                password_guardada.encode("utf-8"),

            )

            logger.info(f"[OK] Verificación bcrypt: {resultado}")

            return resultado

        except ValueError as e:

            logger.exception("[ERROR] Error en hash bcrypt: %s", str(e))

            return False

    else:

        # Fallback: comparar como plain text (para contraseñas antiguas)

        resultado = password == password_guardada

        logger.warning(f"[AVISO] Usando comparación plain text (legacy): {resultado}")

        return resultado

def login(usuario, password):

    """Autentica usuario contra la base de datos."""

    usuario = normalizar_texto(usuario)

    password = normalizar_texto(password)

    if not usuario or not password:

        logger.warning(f"[ERROR] Usuario o contraseña vacío. Usuario: '{usuario}'")

        return None

    if not st.session_state.get("db_available", True):

        logger.warning("[ERROR] Base de datos no disponible")

        return None

    # Buscar usuario en base de datos - uses safe wrapper for audit trail

    user = safe_fetch_one(

        """

        SELECT id, usuario, password, rol, telefono, barberia_id, cortes_acumulados

        FROM usuarios

        WHERE usuario=%s

        """,

        (usuario,),

    )


    if not user:

        logger.warning(f"[ERROR] Usuario no encontrado: '{usuario}'")

        return None


    logger.info(f"[OK] Usuario encontrado: {user[1]} (ID: {user[0]})")

    logger.info(f"Verificando Hash format: {user[2][:20]}... (bcrypt: {es_hash_bcrypt(user[2])})")


    # Verificar contraseña

    if not verificar_password(password, user[2]):

        logger.warning(f"[ERROR] Contraseña incorrecta para usuario: {usuario}")

        return None


    logger.info(f"[OK] Contraseña verificada para: {usuario}")


    # Normalizar rol para asegurar que siempre sea válido

    rol_normalizado = normalizar_rol(user[3])

    if rol_normalizado != user[3]:

        logger.info(f"Procesando Normalizando rol de '{user[3]}' a '{rol_normalizado}' para: {usuario}")

        # Actualizar rol en la base de datos si es diferente

        if execute_write(

            "UPDATE usuarios SET rol=%s WHERE id=%s",

            (rol_normalizado, user[0]),

        ):

            user = (user[0], user[1], user[2], rol_normalizado, user[4], user[5], user[6])

            logger.info(f"[OK] Rol actualizado en BD para: {usuario}")

        else:

            logger.warning(f"[AVISO] No se pudo actualizar rol en BD, usando rol normalizado localmente")

            user = (user[0], user[1], user[2], rol_normalizado, user[4], user[5], user[6])

    # Si la contraseña es plain text, rehashearla con bcrypt

    if not es_hash_bcrypt(user[2]):

        logger.info(f"Procesando Rehasheando contraseña para: {usuario}")

        nuevo_hash = hash_password(password)

        if execute_write(

            "UPDATE usuarios SET password=%s WHERE id=%s",

            (nuevo_hash, user[0]),

        ):

            logger.info(f"[OK] Contraseña rehashada para: {usuario}")

            user = (user[0], user[1], nuevo_hash, user[3], user[4], user[5], user[6])

        else:

            logger.warning(f"[AVISO] No se pudo rehasear contraseña para: {usuario}")

    logger.info(f"[OK] Login exitoso para: {usuario} con rol: {user[3]}")

    return user

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

def registrar(usuario, password, rol, telefono=None, barberia_id=None):

    if not st.session_state.get("db_available", True):

        st.warning("No hay base de datos: el registro no está disponible en modo demo.")

        return False

    if barberia_id is None:

        barberia_id = st.session_state["barberia_id"]

    if not barberia_id:

        st.error("No hay barbería configurada para registrar usuarios.")

        return False

    password_hash = hash_password(password)

    rol_db = normalizar_rol(rol) if rol else ""

    try:

        result = execute_write(

            "INSERT INTO usuarios (usuario, password, rol, telefono, barberia_id) VALUES (%s, %s, %s, %s, %s)",

            (usuario, password_hash, rol_db, telefono, barberia_id),

        )

        return bool(result)

    except Exception as e:

        logger.exception("registrar")

        st.error(str(e))

        return False

def registrar_barberia(nombre_barberia, admin_usuario, admin_password):

    """Crea barbería y usuario ADMIN dueño (multi-tenant)."""

    if not st.session_state.get("db_available", True):

        st.warning("No hay base de datos.")

        return False

    nombre_barberia = normalizar_texto(nombre_barberia)

    admin_usuario = normalizar_texto(admin_usuario)

    admin_password = normalizar_texto(admin_password)

    if not nombre_barberia or not admin_usuario or not admin_password:

        st.error("Completa nombre de barbería, usuario y contraseña.")

        return False

    conn = None

    try:

        conn = get_connection()

        if conn is None:

            return False

        with conn.cursor() as cur:

            cur.execute(

                "INSERT INTO barberias (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING RETURNING id",

                (nombre_barberia,),

            )

            row = cur.fetchone()

            if row and row[0]:

                bid = row[0]

            else:

                cur.execute("SELECT id FROM barberias WHERE nombre = %s", (nombre_barberia,))

                bid = cur.fetchone()[0]

            cur.execute("SELECT id FROM usuarios WHERE usuario = %s", (admin_usuario,))

            if cur.fetchone():

                conn.rollback()

                st.error("Ese usuario administrador ya existe.")

                return False

            cur.execute(

                """

                INSERT INTO usuarios (usuario, password, rol, telefono, barberia_id, cortes_acumulados)

                VALUES (%s, %s, %s, %s, %s, 0)

                """,

                (admin_usuario, hash_password(admin_password), "ADMIN", None, bid),

            )

        conn.commit()

        st.success("Barbería registrada. Ya puedes iniciar sesión como administrador.")

        return True

    except Exception as e:

        if conn:

            conn.rollback()

        logger.exception("registrar_barberia")

        st.error(str(e))

        return False

    finally:

        if conn:

            conn.close()

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

            # st.sidebar.error("SUPER_ADMIN no se pudo crear")

            logger.error("SUPER_ADMIN no se pudo crear")

            return False

        except Exception as e:

            # st.sidebar.error(f"Seed error: {str(e)}")

            logger.error(f"Seed error: {str(e)}")

            return False

    except Exception as e:

        if conn:

            conn.rollback()

        logger.exception("[ERROR] Error en seed_default_data")

        # st.sidebar.error(f"Seed error: {str(e)}")

        logger.error(f"Seed error: {str(e)}")

        return False

    finally:

        if conn:

            conn.close()

# ---------------------------------------------------------------------------
# Migration guard: only run DDL (CREATE/ALTER/INDEX) when explicitly enabled.
# Set ALLOW_SCHEMA_MIGRATIONS=true in the environment (server-side) to run them.
# In public / read-only mode the variable is absent, so DDL is skipped.
# ---------------------------------------------------------------------------
_ALLOW_MIGRATIONS = os.getenv("ALLOW_SCHEMA_MIGRATIONS", "false").strip().lower() == "true"

# Initialize app state and data only once

if "app_initialized" not in st.session_state:

    try:

        with st.spinner("Procesando Inicializando base de datos..."):

            if _ALLOW_MIGRATIONS:
                ensure_database_tables()
            else:
                logger.info(
                    "[SKIP] ensure_database_tables() omitida: "
                    "ALLOW_SCHEMA_MIGRATIONS no está activado. "
                    "Las migraciones no se ejecutan en modo público/read-only."
                )


            # Run seed only once

            if "seed_done" not in st.session_state:

                # Hidden seed debug output - use logger instead of st.sidebar

                logger.info("Running seed...")

                seed_result = seed_default_data()

                st.session_state.seed_done = True


                if seed_result:

                    logger.info("SUPER_ADMIN listo")

                elif seed_result is False:

                    logger.warning("[ERROR] Seed falló - SUPER_ADMIN NO garantizado")


            default_barberia_id = inicializar_barberia()

            st.session_state.app_initialized = True

            st.session_state.default_barberia_id = default_barberia_id

    except Exception as e:

        logger.exception("Error inesperado inicializando la base de datos")

        # Do NOT expose technical DDL/migration errors in the public UI.
        # Log the full detail server-side; show nothing to the visitor.
        _err_lower = str(e).lower()
        _is_ddl_error = any(
            kw in _err_lower
            for kw in ("create table", "create index", "alter table", "read-only transaction")
        )
        if not _is_ddl_error:
            st.error(str(e))
        else:
            logger.error(
                "[READ-ONLY] La base de datos rechazó una operación DDL. "
                "Active ALLOW_SCHEMA_MIGRATIONS=true en el entorno del servidor para ejecutar migraciones. "
                f"Detalle: {e}"
            )

        default_barberia_id = None

        st.session_state.app_initialized = True  # Mark as initialized even on error

else:

    default_barberia_id = st.session_state.get("default_barberia_id")

@st.cache_data(ttl=120)

def listar_usuarios_barberos(barberia_id=None):

    """Get barbers for a specific barberia - enforces data isolation.


    SECURITY: Always uses current barberia context.

    """

    # SECURITY: Always use current context

    barberia_id = get_current_barberia_id()

    if not barberia_id:

        return []


    # Check if user can access this barberia

    enforce_barberia_access(barberia_id)


    try:

        return safe_fetch_all(

            """

            SELECT id, usuario FROM usuarios

            WHERE barberia_id = %s AND UPPER(TRIM(rol)) = 'BARBERO'

            ORDER BY usuario

            """,

            (barberia_id,),

        ) or []

    except Exception:

        logger.exception("listar_usuarios_barberos")

        return []

def opciones_filtro_barberos_ui(barberia_id):

    rows = listar_usuarios_barberos(barberia_id) if barberia_id else []

    nombres = [r[0] for r in rows]

    if not nombres:

        nombres = list(barberos.keys())

    return ["Todos"] + nombres

def marcar_reserva_pagada(reserva_id):

    if not st.session_state.get("db_available", True):

        return False

    user = st.session_state.get("user")

    if not user:

        return False

    prev = obtener_reserva_por_id(reserva_id)

    if not prev:

        st.error("Reserva no encontrada.")

        return False

    rol_u = normalizar_rol(user[3])

    uid = user[1]

    if rol_u == "BARBERO" and prev[2] != uid:

        st.error("Sin permiso.")

        return False

    if rol_u == "ADMIN" and prev[7] != st.session_state.get("barberia_id"):

        st.error("Sin permiso.")

        return False

    if rol_u == "CLIENTE":

        st.error("Sin permiso.")

        return False

    try:

        # ALL roles must update with barberia_id filter - NO EXCEPTIONS!

        barberia_id_from_reserva = prev.get("barberia_id") or prev[7]


        # CRITICAL: Enforce barberia context for SUPER_ADMIN too

        if rol_u == "SUPER_ADMIN":

            enforce_access(barberia_id_from_reserva)


        return bool(

            execute_write(

                """

                UPDATE reservas

                SET pagado = TRUE, monto = COALESCE(monto, precio)

                WHERE id = %s AND barberia_id = %s

                """,

                (reserva_id, barberia_id_from_reserva),

            )

        )

    except Exception as e:

        logger.exception("marcar_reserva_pagada")

        st.error(str(e))

        return False

# ==================== MERCADOPAGO PAYMENTS ====================

def crear_pago_mercadopago(reserva_id, monto, descripcion, cliente_email=None, show_errors=True):

    """

    Create MercadoPago payment preference and return checkout URL.


    Args:

        reserva_id: Reservation ID

        monto: Payment amount in CLP

        descripcion: Service description

        cliente_email: Customer email (optional)

        show_errors: Whether to show st.error() messages (True for UI, False for backend)


    Returns:

        URL to MercadoPago checkout, or None if error

    """

    # Validate SDK is available

    if not mercadopago:

        error_msg = "MercadoPago SDK no está instalado. Ejecuta: pip install mercadopago"

        logger.error(error_msg)

        if show_errors:

            st.error(error_msg)

        return None


    # Load and validate access token

    access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

    if not access_token or access_token.strip() == "":

        error_msg = "MERCADOPAGO_ACCESS_TOKEN no configurado. Agrega a .env: MERCADOPAGO_ACCESS_TOKEN=tu_token"

        logger.error(error_msg)

        if show_errors:

            st.error(error_msg)

        return None


    # Debug: Show token was loaded (masked)

    token_preview = access_token[:10] + "..." if len(access_token) > 10 else access_token

    logger.info(f"Token Token cargado: {token_preview}")


    try:

        # Initialize SDK

        sdk = mercadopago.SDK(access_token)


        # Validate payment amount

        try:

            monto_float = float(monto)

            if monto_float <= 0:

                raise ValueError("Monto debe ser mayor a 0")

        except (ValueError, TypeError) as e:

            error_msg = f"Monto inválido: {monto}. Error: {str(e)}"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


        # Build preference data

        preference_data = {

            "items": [

                {

                    "title": str(descripcion)[:256],  # MercadoPago title max 256 chars

                    "quantity": 1,

                    "currency_id": "CLP",

                    "unit_price": monto_float

                }

            ],

            "external_reference": str(reserva_id),

            "notification_url": "https://splendid-morphine-maximize.ngrok-free.dev/webhook",

        }


        # Add back URLs if configured

        success_url = os.getenv("MERCADOPAGO_SUCCESS_URL")

        failure_url = os.getenv("MERCADOPAGO_FAILURE_URL")

        pending_url = os.getenv("MERCADOPAGO_PENDING_URL")


        if success_url or failure_url or pending_url:

            preference_data["back_urls"] = {

                "success": success_url or "https://barberia-app.com/success",

                "failure": failure_url or "https://barberia-app.com/failure",

                "pending": pending_url or "https://barberia-app.com/pending"

            }


        # Add payer email if provided

        if cliente_email and "@" in str(cliente_email):

            preference_data["payer"] = {"email": str(cliente_email)}


        logger.info(f"Enviando preference a MercadoPago para reserva {reserva_id}...")


        # Create preference

        preference_response = sdk.preference().create(preference_data)

        logger.info(f"Respuesta de MercadoPago: {preference_response}")


        # Validate response structure

        if not isinstance(preference_response, dict):

            error_msg = f"Respuesta inválida de MercadoPago: tipo {type(preference_response)}"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


        # Check status code

        response_status = preference_response.get("status")

        if response_status != 201:

            error_msg = f"MercadoPago error (status {response_status}): {preference_response}"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


        # Extract init_point

        if "response" not in preference_response:

            error_msg = f"No 'response' en respuesta de MercadoPago: {preference_response}"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


        response_data = preference_response["response"]

        if "init_point" not in response_data:

            error_msg = f"No 'init_point' en response de MercadoPago: {response_data}"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


        init_point = response_data.get("init_point")

        if not init_point:

            error_msg = "init_point es vacío en respuesta de MercadoPago"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


        logger.info(f"[OK] Pago creado para reserva {reserva_id}: {init_point}")

        return init_point


    except Exception as e:

        error_msg = f"Error creando pago MercadoPago para reserva {reserva_id}: {str(e)}"

        logger.exception(error_msg)

        if show_errors:

            st.error(error_msg)

        return None

def ui_pagar_reserva(rows, barberia_id, usuario):

    """

    Display payment UI for unpaid reservations.

    Allows CLIENTE to generate MercadoPago payment links.


    Args:

        rows: List of reservations

        barberia_id: Barberia context ID

        usuario: Current user

    """

    if not rows:

        return


    user = st.session_state.get("user")

    if not user:

        return


    nr = normalizar_rol(user[3])

    if nr != "CLIENTE":

        return


    # Filter unpaid reservations

    unpaid = [r for r in rows if not r.get("pagado", False)]

    if not unpaid:

        return


    st.markdown("### Pagar reservas pendientes")


    # DEBUG: Show token status (temporary, for troubleshooting)

    access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

    token_status = "[OK] Cargado" if access_token else "[ERROR] No configurado"

    with st.expander(f"Debug - Token: {token_status}"):

        if access_token:

            st.info(f"Token cargado: {access_token[:10]}...")

        else:

            st.error("MERCADOPAGO_ACCESS_TOKEN no está en .env")


    for r in unpaid:

        reserva_id = r.get("id")

        servicio = r.get("servicio", "Servicio")

        monto = r.get("monto") or r.get("precio") or 0

        fecha = r.get("fecha")

        hora = r.get("hora")


        fecha_label = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)

        hora_label = hora.strftime("%H:%M") if hasattr(hora, "strftime") else str(hora)


        col1, col2, col3 = st.columns([2, 1, 1], gap="small")


        with col1:

            st.caption(f"{fecha_label} {hora_label} · {servicio}")


        with col2:

            st.metric("Monto", f"${monto}")


        with col3:

            if st.button(

                "Generar Link",

                key=f"pagar_mp_{reserva_id}",

                use_container_width=True

            ):

                with st.spinner("Generando enlace de pago..."):

                    descripcion = f"Barbería - {servicio} ({fecha_label})"

                    pago_url = crear_pago_mercadopago(

                        reserva_id,

                        monto,

                        descripcion,

                        cliente_email=None,

                        show_errors=True

                    )


                    if pago_url:

                        st.session_state[f"pago_url_{reserva_id}"] = pago_url

                        st.success(f"[OK] Enlace generado para reserva #{reserva_id}")

                        st.balloons()

                    else:

                        st.error(f"No se pudo generar el link para reserva #{reserva_id}")


        # Show payment link if generated (ALWAYS visible after generation)

        pago_key = f"pago_url_{reserva_id}"

        if pago_key in st.session_state:

            pago_url = st.session_state[pago_key]


            if pago_url:

                col_link1, col_link2 = st.columns([4, 1], gap="small")

                with col_link1:

                    st.link_button(

                        f"Ir a pagar ${monto} (MercadoPago)",

                        pago_url,

                        type="primary",

                        use_container_width=True

                    )

                with col_link2:

                    if st.button("Limpiar", key=f"clear_url_{reserva_id}", use_container_width=True):

                        del st.session_state[pago_key]

                        st.rerun()


                st.caption(

                    " Serás redirigido a MercadoPago. Después de pagar, vuelve a esta página. "

                    "La confirmación puede tomar algunos minutos."

                )

            else:

                st.error(f"El URL de pago no es válido")


        st.divider()


    st.markdown("---")

def obtener_telefono_usuario(usuario):

    row = fetch_one("SELECT telefono FROM usuarios WHERE usuario=%s", (usuario,))

    return row[0] if row and row[0] else None

def get_default_barberia_id():

    row = fetch_one("SELECT id FROM barberias ORDER BY id LIMIT 1")

    return row[0] if row else None

def registrar_fidelizacion(usuario, barberia_id):

    row = execute_write(

        """

        UPDATE usuarios

        SET cortes_acumulados = COALESCE(cortes_acumulados, 0) + 1

        WHERE usuario = %s AND barberia_id = %s

        RETURNING cortes_acumulados

        """,

        (usuario, barberia_id),

        fetch_one_result=True,

    )

    return row[0] if row else None

def procesar_beneficio_fidelizacion(usuario, barberia_id):

    cortes_acumulados = registrar_fidelizacion(usuario, barberia_id)

    if cortes_acumulados is None or cortes_acumulados < 5:

        return

    execute_write(

        """

        UPDATE usuarios

        SET cortes_acumulados = 0

        WHERE usuario = %s AND barberia_id = %s

        """,

        (usuario, barberia_id),

    )

    telefono_cliente = obtener_telefono_usuario(usuario)

    if telefono_cliente:

        try:

            enviar_whatsapp_twilio(

                telefono_cliente,

                "¡Tienes un descuento en tu próximo corte!",

            )

        except Exception as exc:

            logger.exception("Error al enviar beneficio de fidelizacion: %s", exc)

def construir_mensaje_reserva(nombre, inicio, barbero, servicio):

    return (

        f"Hola {nombre}, tu reserva fue confirmada.\n"

        f"Fecha: {inicio.strftime('%d-%m-%Y')}\n"

        f"Hora: {inicio.strftime('%H:%M')}\n"

        f"Barbero: {barbero}\n"

        f"Servicio: {servicio}"

    )

def normalizar_reserva(r):

    """

    Normalize reservation tuple to dict.

    Handles schema: id, barbero, servicio, fecha, hora, cliente, nombre, inicio, precio, estado, pagado, monto

    Indices:      0    1        2          3      4     5        6       7       8       9       10       11

    """

    if isinstance(r, dict):

        return r

    if not r or len(r) < 6:

        return {}


    return {

        "id": r[0],

        "barbero": r[1],

        "servicio": r[2],

        "fecha": r[3],

        "hora": r[4],

        "cliente": r[5],

        "pagado": r[10] if len(r) > 10 else False,

        "monto": r[11] if len(r) > 11 else (r[8] if len(r) > 8 else 0),

    }

@st.cache_data(ttl=30)

def obtener_reservas_raw(barbero_filtro=None):

    """Fast cached reservations query with minimal overhead - returns list of dicts.


    SECURITY: Always uses current barberia context and safe query wrapper.

    """

    if not st.session_state.get("db_available", True):

        return []


    try:

        user = st.session_state.get("user")

        if not user:

            return []

        rol = normalizar_rol(user[3])

        uid = user[1]

        # SECURITY: Use get_current_barberia_id for consistent context

        bid = get_current_barberia_id() if rol != "SUPER_ADMIN" or not st.session_state.get("super_admin_all_barberias") else None

        super_all = rol == "SUPER_ADMIN" and st.session_state.get("super_admin_all_barberias")

        if not super_all and not bid:

            return []

        # Optimized single query with proper indexing

        sql = """

            SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id, pagado, monto

            FROM reservas

            WHERE 1=1

        """

        params = []

        if not super_all:

            sql += " AND barberia_id = %s"

            params.append(bid)

        if rol == "BARBERO":

            sql += " AND barbero_id = %s"

            params.append(user[0])  # Use user ID instead of username

        elif barbero_filtro and rol in ("ADMIN", "SUPER_ADMIN"):

            sql += " AND barbero_id = %s"

            params.append(barbero_filtro)

        sql += " ORDER BY inicio"

        # SECURITY: Use safe wrapper to enforce barberia_id validation

        results = safe_fetch_all(sql, tuple(params)) or []


        # Convert tuples to dictionaries for consistent access

        reservas_dict = []

        for r in results:

            reservas_dict.append({

                "id": r[0],

                "nombre": r[1],

                "barbero": r[2],

                "servicio": r[3],

                "precio": r[4],

                "inicio": r[5],

                "fin": r[6],

                "barberia_id": r[7],

                "pagado": r[8] if len(r) > 8 else False,

                "monto": r[9] if len(r) > 9 else r[4],

            })

        return reservas_dict

    except Exception as e:

        logger.exception("Error en obtener_reservas_raw")

        return []

def construir_eventos_calendario(reservas):

    """Construye eventos del calendario con colores por estado de pago (AgendaPro style)."""

    eventos = []

    for r in reservas:

        # Handle both dict and tuple formats for backward compatibility

        if isinstance(r, dict):

            es_bloqueo = r.get("nombre", "") == "BLOQUEADO" or r.get("servicio", "") == "Bloqueo"

            cliente = r.get("nombre", "Desconocido")

            barbero_id = r.get("barbero", "unknown")

            servicio = r.get("servicio", "")

            fecha_inicio = r.get("inicio")

            fecha_fin = r.get("fin")

            pagado = r.get("pagado", False)

            reserva_id = r.get("id")

        else:

            # Legacy tuple format - try to unpack (id, nombre, barbero, servicio, precio, inicio, fin, barberia_id, pagado, monto)

            try:

                es_bloqueo = r[1] == "BLOQUEADO" or r[3] == "Bloqueo"

                cliente = r[1]

                barbero_id = r[2]

                servicio = r[3]

                fecha_inicio = r[5]

                fecha_fin = r[6]

                pagado = r[8] if len(r) > 8 else False

                reserva_id = r[0]

            except (IndexError, TypeError):

                logger.warning(f"Unexpected reservation format: {r}")

                continue


        # Crear título en formato moderno

        if es_bloqueo:

            titulo = "🚫 BLOQUEADO"

        else:

            titulo = f"{cliente} - {servicio}"


        # Color by payment status: Green for paid, Orange for pending

        if es_bloqueo:

            color = "#666666"

            border_color = "#4b5563"

        elif pagado:

            color = "#16a34a"  # Green for paid

            border_color = "#15803d"

        else:

            color = "#f59e0b"  # Orange for pending

            border_color = "#d97706"


        # Convert datetime to ISO format strings for JSON serialization

        inicio_iso = fecha_inicio.isoformat() if hasattr(fecha_inicio, "isoformat") else str(fecha_inicio)

        fin_iso = fecha_fin.isoformat() if hasattr(fecha_fin, "isoformat") else str(fecha_fin)


        eventos.append({

            "id": str(reserva_id),

            "title": titulo,

            "start": inicio_iso,

            "end": fin_iso,

            "resourceId": str(barbero_id),  # For resource-based calendar views

            "color": color,

            "borderColor": border_color,

            "textColor": "#FFFFFF",

            "extendedProps": {

                "id": reserva_id,

                "nombre": cliente,

                "barbero": barbero_id,

                "servicio": servicio,

                "monto": r.get("monto") if isinstance(r, dict) else (r[4] if len(r) > 4 else 0),

                "pagado": pagado,

                "bloqueo": es_bloqueo,

                "inicio": inicio_iso,

                "fin": fin_iso,

            },

        })

    return eventos

def mostrar_detalles_reserva(reserva_id):

    """Muestra detalles detallados de una reserva con opciones de interacción (estilo AgendaPro)."""

    reserva = obtener_reserva_por_id(reserva_id)

    if not reserva:

        st.error("Reserva no encontrada")

        return None


    # Extract details

    cliente = reserva.get('nombre', 'Desconocido')

    servicio = reserva.get('servicio', '')

    inicio = reserva.get("inicio")

    inicio_str = inicio.strftime("%H:%M") if hasattr(inicio, "strftime") else str(inicio)

    fecha_str = inicio.strftime("%d/%m/%Y") if hasattr(inicio, "strftime") else ""

    pagado = reserva.get("pagado", False)

    estado = "[OK] Pagado" if pagado else "Pendiente"

    estado_color = "#16a34a" if pagado else "#f59e0b"

    monto = reserva.get('monto', 0)


    render_reservation_card(
        cliente,
        servicio,
        inicio_str,
        fecha_str,
        monto,
        estado,
        estado_color,
    )


    return reserva

def agrupar_por_barbero(events):

    """Group calendar events by barber for multi-barber layout. Handle both events and raw reservations."""

    barberos_dict = {}


    if not events:

        return barberos_dict


    for item in events:

        try:

            # Handle event dictionary format from construir_eventos_calendario

            if isinstance(item, dict):

                barbero_id = item.get("resourceId", "unknown")

                barber_name = item.get("title", "").split("-")[0].strip() or "Barbero"

                key = (barbero_id, barber_name)

                if key not in barberos_dict:

                    barberos_dict[key] = []

                barberos_dict[key].append(item)

            else:

                # Log unexpected format and skip

                logger.warning(f"Unexpected item format in agrupar_por_barbero: {type(item)}")

        except Exception as e:

            logger.warning(f"Error processing item in agrupar_por_barbero: {traceback.format_exc()}")

            continue


    return barberos_dict

def render_calendario_multi_barbero(reservas, read_only=False):

    """Render multiple calendars in columns, one per barber (AgendaPro style layout)."""

    if not reservas:

        st.warning("No hay reservas para mostrar en el calendario.")

        return


    # Group reservations by barber

    try:

        barberos_dict = agrupar_por_barbero(reservas)

    except Exception as e:

        st.error(f"Error al agrupar reservas:\n{traceback.format_exc()}")

        return


    if not barberos_dict:

        st.warning("No hay reservas para mostrar. Verifique los datos.")

        return


    # Professional header with legend

    col_title, col_legend = st.columns([2, 1])

    with col_title:

        st.markdown(f"### Vista Multi-Barbero")


    with col_legend:

        render_status_legend(compact=True)


    st.markdown("---")


    # Create columns for each barber

    num_barbers = len(barberos_dict)

    cols = st.columns(num_barbers) if num_barbers <= 3 else st.columns(3)  # Max 3 columns


    for idx, (barbero_info, reservas_barbero) in enumerate(sorted(barberos_dict.items())):

        try:

            # Extract barber ID and name from key tuple

            barbero_id, barber_name = barbero_info if isinstance(barbero_info, tuple) else (barbero_info, str(barbero_info))


            if not reservas_barbero:

                continue


            col_index = idx % len(cols)

            with cols[col_index]:

                # Subheader for barber

                st.subheader(f"{barber_name}")


                # Convert reservations to events for this barber

                try:

                    eventos_barbero = construir_eventos_calendario(reservas_barbero)

                except Exception as e:

                    st.error(f"Error construyendo eventos para {barber_name}:\n{traceback.format_exc()}")

                    continue


                if not eventos_barbero:

                    st.info(f"Sin reservas para {barber_name}")

                    continue


                # Calendar options (no resources)

                options = {

                    "initialView": "timeGridWeek",

                    "editable": not read_only,

                    "selectable": not read_only,

                    "allDaySlot": False,

                    "slotMinTime": "09:00:00",

                    "slotMaxTime": "21:00:00",

                    "slotDuration": "00:30:00",

                    "slotLabelInterval": "00:30:00",

                    "height": 600,

                    "contentHeight": "auto",

                    "headerToolbar": {

                        "left": "prev,next today",

                        "center": "title",

                        "right": "dayGridMonth,timeGridWeek,timeGridDay",

                    },

                    "slotLabelFormat": {

                        "meridiem": False,

                        "hour": "2-digit",

                        "minute": "2-digit",

                    },

                    "eventDisplay": "block",

                    "eventTimeFormat": {

                        "meridiem": False,

                        "hour": "2-digit",

                        "minute": "2-digit",

                    },

                    "nowIndicator": True,

                    "scrollTime": "09:00:00",

                    "dayMaxEvents": 6,

                    "eventBackgroundColor": "transparent",

                    "eventBorderColor": "transparent",

                    "eventTextColor": "#FFFFFF",

                }


                try:

                    calendar_state = calendar(

                        events=eventos_barbero,

                        options=options,

                        key=f"calendario_barbero_{barbero_id}_{idx}",

                    )


                    if calendar_state and calendar_state.get("eventClick"):

                        manejar_interaccion_calendario(calendar_state)

                except Exception as e:

                    st.error(f"Error al mostrar calendario para {barber_name}:\n{traceback.format_exc()}")

        except Exception as e:

            logger.error(f"Error processing barber {barbero_info}: {traceback.format_exc()}")

            continue

def obtener_reservas(barbero=None):

    return construir_eventos_calendario(obtener_reservas_raw(barbero))

def obtener_reserva_por_id(reserva_id):

    """Get reservation by ID with multi-tenant isolation - must verify access."""

    try:

        result = fetch_one(

            """

            SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id, cliente, pagado, monto

            FROM reservas

            WHERE id = %s

            """,

            (reserva_id,),

        )

        if not result:

            return None


        # Extract barberia_id and verify access

        barberia_id = result[7]

        enforce_barberia_access(barberia_id)


        # Convert tuple to dictionary

        return {

            "id": result[0],

            "nombre": result[1],

            "barbero": result[2],

            "servicio": result[3],

            "precio": result[4],

            "inicio": result[5],

            "fin": result[6],

            "barberia_id": result[7],

            "cliente": result[8],

            "pagado": result[9] if len(result) > 9 else False,

            "monto": result[10] if len(result) > 10 else result[4],

        }

    except Exception:

        logger.exception("obtener_reserva_por_id")

        return None

def obtener_reserva(reserva_id, barberia_id):

    try:

        result = fetch_one(

            """

            SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id, cliente, pagado, monto

            FROM reservas

            WHERE id = %s AND barberia_id = %s

            """,

            (reserva_id, barberia_id),

        )

        if not result:

            return None


        # Convert tuple to dictionary

        return {

            "id": result[0],

            "nombre": result[1],

            "barbero": result[2],

            "servicio": result[3],

            "precio": result[4],

            "inicio": result[5],

            "fin": result[6],

            "barberia_id": result[7],

            "cliente": result[8],

            "pagado": result[9] if len(result) > 9 else False,

            "monto": result[10] if len(result) > 10 else result[4],

        }

    except Exception:

        logger.exception("obtener_reserva")

        return None

def normalizar_datetime(valor):

    if isinstance(valor, datetime):

        return valor.replace(tzinfo=None)

    if isinstance(valor, str):

        return datetime.fromisoformat(valor.replace("Z", "+00:00")).replace(tzinfo=None)

    return valor

def _guardar_reserva_tx(nombre, barbero, servicio, precio, inicio, fin, barberia_id):

    conn = None

    try:

        conn = get_connection()

        if conn is None:

            return False

        with conn.cursor() as cur:

            cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (f"{barberia_id}:{barbero}",))

            cur.execute(

                """

                SELECT id FROM reservas

                WHERE barberia_id = %s

                  AND barbero = %s

                  AND inicio < %s

                  AND fin > %s

                LIMIT 1

                """,

                (barberia_id, barbero, fin, inicio),

            )

            if cur.fetchone():

                conn.rollback()

                st.error("Horario ocupado")

                return False

            cur.execute(

                """

                INSERT INTO reservas (nombre, barbero, servicio, precio, inicio, fin, barberia_id, monto, pagado)

                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE)

                """,

                (nombre, barbero, servicio, precio, inicio, fin, barberia_id, precio),

            )

        conn.commit()

        return True

    except Exception:

        if conn:

            conn.rollback()

        logger.exception("Error al guardar reserva")

        st.error("No se pudo guardar la reserva.")

        return False

    finally:

        if conn:

            conn.close()

def guardar_reserva(nombre, barbero, servicio, precio, inicio, fin):

    barberia_id = session_barberia_for_write()

    if not barberia_id:

        return False

    if not st.session_state.get("db_available", True):

        st.warning("No hay base de datos: no se pueden guardar reservas en modo demo.")

        return False

    inicio = normalizar_datetime(inicio)

    fin = normalizar_datetime(fin)

    if not inicio or not fin or inicio >= fin:

        st.error("El horario de término debe ser posterior al inicio.")

        return False

    return _guardar_reserva_tx(nombre, barbero, servicio, precio, inicio, fin, barberia_id)

def actualizar_reserva(reserva_id, nombre, barbero, servicio, precio, inicio, fin):

    if not st.session_state.get("db_available", True):

        st.warning("No hay base de datos: no se pueden actualizar reservas en modo demo.")

        return False

    inicio = normalizar_datetime(inicio)

    fin = normalizar_datetime(fin)

    if not inicio or not fin or inicio >= fin:

        st.error("El horario de término debe ser posterior al inicio.")

        return False

    user = st.session_state.get("user")

    rol_u = normalizar_rol(user[3]) if user else ""

    prev = obtener_reserva_por_id(reserva_id)

    if not prev:

        st.error("Reserva no encontrada.")

        return False

    bid_tx = prev[7]

    sw = session_barberia_for_write()

    if rol_u != "SUPER_ADMIN" and not sw:

        return False

    if rol_u == "BARBERO" and prev[2] != user[1]:

        st.error("Sin permiso para modificar esta reserva.")

        return False

    if rol_u == "ADMIN" and bid_tx != st.session_state.get("barberia_id"):

        st.error("Sin permiso para modificar esta reserva.")

        return False

    if rol_u == "CLIENTE":

        st.error("Sin permiso para modificar esta reserva.")

        return False

    conn = None

    try:

        conn = get_connection()

        if conn is None:

            return False

        with conn.cursor() as cur:

            cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (f"{bid_tx}:{barbero}",))

            cur.execute(

                """

                SELECT id FROM reservas

                WHERE barberia_id = %s

                  AND barbero = %s

                  AND id <> %s

                  AND inicio < %s

                  AND fin > %s

                LIMIT 1

                """,

                (bid_tx, barbero, reserva_id, fin, inicio),

            )

            if cur.fetchone():

                conn.rollback()

                st.error("Ese cambio genera solapamiento con otra reserva.")

                return False

            cur.execute(

                """

                UPDATE reservas

                SET nombre = %s, barbero = %s, servicio = %s, precio = %s, inicio = %s, fin = %s

                WHERE id = %s AND barberia_id = %s

                """,

                (nombre, barbero, servicio, precio, inicio, fin, reserva_id, bid_tx),

            )

        conn.commit()

        return True

    except Exception:

        if conn:

            conn.rollback()

        logger.exception("Error al actualizar reserva")

        st.error("No se pudo actualizar la reserva.")

        return False

    finally:

        if conn:

            conn.close()

def eliminar_reserva(reserva_id):

    if not st.session_state.get("db_available", True):

        st.warning("No hay base de datos: no se pueden eliminar reservas en modo demo.")

        return False

    user = st.session_state.get("user")

    if not user:

        return False

    prev = obtener_reserva_por_id(reserva_id)

    if not prev:

        st.error("Reserva no encontrada.")

        return False

    rol_u = normalizar_rol(user[3])

    uid = user[1]

    cli = prev.get("cliente")

    if rol_u == "BARBERO" and prev.get("barbero") != uid:

        st.error("Sin permiso para eliminar esta reserva.")

        return False

    if rol_u == "ADMIN" and prev.get("barberia_id") != st.session_state.get("barberia_id"):

        st.error("Sin permiso para eliminar esta reserva.")

        return False

    if rol_u == "CLIENTE" and (cli or prev.get("nombre")) != uid:

        st.error("Sin permiso para eliminar esta reserva.")

        return False

    try:

        if rol_u == "SUPER_ADMIN":

            return bool(execute_write("DELETE FROM reservas WHERE id = %s", (reserva_id,)))

        return bool(

            execute_write(

                "DELETE FROM reservas WHERE id = %s AND barberia_id = %s",

                (reserva_id, prev.get("barberia_id")),

            )

        )

    except Exception as e:

        logger.exception("eliminar_reserva")

        st.error(f"Error eliminando reserva:\n{traceback.format_exc()}")

        return False

def insertar_reserva_con_fecha_hora(

    barberia_id,

    cliente_usuario,

    barbero_id,

    barbero_nombre,

    servicio,

    fecha,

    hora,

    precio,

    duracion_min,

):

    """Inserta reserva validando slot por fecha/hora y solapamiento por inicio/fin."""

    conn = None

    try:

        if not fecha or not hora:

            st.error("Selecciona fecha y hora.")

            return False

        inicio = datetime.combine(fecha, hora)

        fin = inicio + timedelta(minutes=duracion_min)

        conn = get_connection()

        if conn is None:

            return False

        with conn.cursor() as cur:

            cur.execute(

                """

                SELECT id FROM reservas

                WHERE barberia_id = %s AND barbero_id = %s AND fecha = %s AND hora = %s

                LIMIT 1

                """,

                (barberia_id, barbero_id, fecha, hora),

            )

            if cur.fetchone():

                conn.rollback()

                st.error("Horario ocupado")

                return False

            cur.execute(

                """

                SELECT id FROM reservas

                WHERE barberia_id = %s

                  AND barbero_id = %s

                  AND inicio < %s

                  AND fin > %s

                LIMIT 1

                """,

                (barberia_id, barbero_id, fin, inicio),

            )

            if cur.fetchone():

                conn.rollback()

                st.error("Horario ocupado")

                return False

            cur.execute(

                """

                INSERT INTO reservas (

                    nombre, barbero, barbero_id, servicio, precio, inicio, fin, barberia_id,

                    cliente, fecha, hora, estado, monto, pagado

                )

                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)

                RETURNING id

                """,

                (

                    cliente_usuario,

                    barbero_nombre,

                    barbero_id,

                    servicio,

                    precio,

                    inicio,

                    fin,

                    barberia_id,

                    cliente_usuario,

                    fecha,

                    hora,

                    "activo",

                    precio,

                ),

            )

            reserva_id = cur.fetchone()[0]

        conn.commit()

        return reserva_id

    except Exception as e:

        if conn:

            conn.rollback()

        logger.exception("Error al insertar reserva (fecha/hora)")

        st.error(str(e))

        return False

    finally:

        if conn:

            conn.close()

@st.cache_data(ttl=30)

def listar_reservas_filtradas(barberia_id_arg=None, rol_tag=None, usuario_login=None, filtro_barbero=None):

    """Fast cached filtered reservations - returns normalized list of dicts.


    SECURITY: Enforces barberia_id validation for all role types.

    """

    # Get user context from session

    user = st.session_state.get("user")

    if not user or not usuario_login:

        usuario_login = user[1] if user else None

    if not rol_tag:

        rol_tag = user[3] if user else None


    nr = normalizar_rol(rol_tag)

    cols = (

        "id, barbero, servicio, fecha, hora, cliente, nombre, inicio, precio, estado, pagado, monto"

    )

    try:

        super_all = nr == "SUPER_ADMIN" and st.session_state.get("super_admin_all_barberias")

        # Pre-built queries for each role type

        if nr == "CLIENTE":

            bid = get_current_barberia_id()  # SECURITY: Use current context

            if not bid:

                return []

            results = safe_fetch_all(

                f"""

                SELECT {cols}

                FROM reservas

                WHERE barberia_id = %s

                  AND (cliente = %s OR nombre = %s)

                ORDER BY inicio DESC NULLS LAST

                """,

                (bid, usuario_login, usuario_login),

            ) or []

            return [normalizar_reserva(r) for r in results]

        if nr == "BARBERO":

            bid = get_current_barberia_id()  # SECURITY: Use current context

            if not bid:

                return []

            user = st.session_state.get("user")

            user_id = user[0] if user else None

            if not user_id:

                return []

            results = safe_fetch_all(

                f"""

                SELECT {cols}

                FROM reservas

                WHERE barberia_id = %s AND barbero_id = %s

                ORDER BY inicio DESC NULLS LAST

                """,

                (bid, user_id),

            ) or []

            return [normalizar_reserva(r) for r in results]

        if super_all:

            # SUPER_ADMIN viewing all barberias - allow global query (exempted in safe_fetch_all)

            sql = f"SELECT {cols} FROM reservas WHERE 1=1"

            params = []

            if filtro_barbero and filtro_barbero != "Todos":

                sql += " AND barbero_id = %s"

                params.append(filtro_barbero)

            sql += " ORDER BY inicio DESC NULLS LAST"

            # SECURITY: safe_fetch_all will allow this because it detects SUPER_ADMIN global context

            results = safe_fetch_all(sql, tuple(params)) or []

            logger.info(f"Consulta SUPER_ADMIN global query - found {len(results)} reservations")

            return [normalizar_reserva(r) for r in results]

        # For ADMIN and other roles - must have barberia_id

        bid = get_current_barberia_id()  # SECURITY: Use current context

        if not bid:

            logger.warning(f"[AVISO] Query blocked: No barberia_id for role {nr}")

            return []


        # Enforce access control

        enforce_barberia_access(bid)

        sql = f"SELECT {cols} FROM reservas WHERE barberia_id = %s"

        params = [bid]

        if filtro_barbero and filtro_barbero != "Todos":

            sql += " AND barbero_id = %s"

            params.append(filtro_barbero)

        sql += " ORDER BY inicio DESC NULLS LAST"

        results = safe_fetch_all(sql, tuple(params)) or []

        return [normalizar_reserva(r) for r in results]

    except Exception as e:

        logger.exception("Error listando reservas")

        return []

def mostrar_reservas_dataframe(rows):

    if not rows:

        st.info("No hay reservas para mostrar.")

        return

    ordered = sorted(

        rows,

        key=lambda r: (

            r.get("fecha") if r.get("fecha") is not None else datetime.min.date(),

            r.get("hora") if r.get("hora") is not None else datetime.min.time(),

        ),

    )

    grouped = {}

    for r in ordered:

        fecha_raw = r.get("fecha")

        if hasattr(fecha_raw, "strftime"):

            fecha_label = fecha_raw.strftime("%A, %d %b %Y")

        else:

            fecha_label = str(fecha_raw or "Sin fecha")

        grouped.setdefault(fecha_label, []).append(r)

    for fecha_label, items in grouped.items():

        st.markdown(f"### {fecha_label}")


        for r in items:

            hora_raw = r.get("hora")

            hora_label = hora_raw.strftime("%H:%M") if hasattr(hora_raw, "strftime") else str(hora_raw or "--:--")

            servicio = r.get("servicio", "")

            barbero = r.get("barbero", "")

            cliente = r.get("cliente") or r.get("nombre") or "Cliente desconocido"

            monto = r.get("monto") or r.get("precio") or 0

            estado = bool(r.get("pagado", False))

            estado_label = "Pagado" if estado else "Pendiente"

            estado_color = "#16a34a" if estado else "#f59e0b"

            estado_bg = "rgba(22, 163, 74, 0.1)" if estado else "rgba(245, 158, 11, 0.1)"

            # Single-line HTML avoids Markdown blank-line re-entry that causes
            # 4-space-indented inner tags to be rendered as <pre><code> blocks.
            card_html = (
                f'<div style="border-radius:12px;padding:16px;margin-bottom:12px;'
                f'background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);'
                f'border-left:6px solid {estado_color};'
                f'box-shadow:0 2px 8px rgba(0,0,0,0.15);'
                f'border:1px solid rgba(255,255,255,0.1);">'
                f'<div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:10px;">'
                f'<h4 style="margin:0;color:#ffffff;font-size:18px;font-weight:600;">{cliente}</h4>'
                f'<span style="background-color:{estado_bg};color:{estado_color};padding:4px 12px;'
                f'border-radius:20px;font-size:12px;font-weight:600;border:1px solid {estado_color};">'
                f'{estado_label}</span></div>'
                f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:12px;">'
                f'<div style="display:flex;align-items:center;gap:8px;"><span>Hora</span><span style="color:#e0e0e0;"><strong>{hora_label}</strong></span></div>'
                f'<div style="display:flex;align-items:center;gap:8px;"><span>Tijeras</span><span style="color:#e0e0e0;"><strong>{servicio}</strong></span></div>'
                f'<div style="display:flex;align-items:center;gap:8px;"><span>·</span><span style="color:#e0e0e0;"><strong>{barbero}</strong></span></div>'
                f'<div style="display:flex;align-items:center;gap:8px;"><span>Monto</span><span style="color:#e0e0e0;"><strong>${monto}</strong></span></div>'
                f'</div></div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

def ui_marcar_pagado_reservas(rows, key_prefix):

    user = st.session_state.get("user")

    if not user or not rows:

        return

    nr = normalizar_rol(user[3])

    if nr == "CLIENTE":

        return

    pend = [r for r in rows if not r.get("pagado", False)]

    if not pend:

        return

    ids = [r.get("id") for r in pend]

    def _lab(i):

        row = next(x for x in pend if x.get("id") == i)

        barbero_str = row.get("barbero", "")

        fecha_str = row.get("fecha", "")

        hora_str = row.get("hora", "")

        if hasattr(fecha_str, "strftime"):

            fecha_str = fecha_str.strftime("%Y-%m-%d")

        if hasattr(hora_str, "strftime"):

            hora_str = hora_str.strftime("%H:%M")

        return f"#{i} - {barbero_str} - {fecha_str} {hora_str}"

    rid = st.selectbox(

        "Marcar como pagado",

        ids,

        format_func=_lab,

        key=f"{key_prefix}_pago_sel",

    )

    if st.button("Marcar como pagado", key=f"{key_prefix}_pago_btn"):

        try:

            if marcar_reserva_pagada(rid):

                st.success("Pago registrado")

                st.rerun()

        except Exception as exc:

            logger.exception("%s", exc)

            st.error("No se pudo actualizar el pago.")

def ui_eliminar_reserva_lista(rows, key_prefix):

    if not rows:

        return

    ids = [r.get("id") for r in rows]

    def _label(i):

        row = next(x for x in rows if x.get("id") == i)

        return f"#{i} - {row.get('barbero')} - {row.get('servicio')} - {row.get('inicio')}"

    rid = st.selectbox(

        "Eliminar reserva",

        ids,

        format_func=_label,

        key=f"{key_prefix}_eliminar_sel",

    )

    if st.button("Eliminar reserva", key=f"{key_prefix}_eliminar_btn"):

        try:

            if eliminar_reserva(rid):

                st.success("Reserva eliminada")

                st.rerun()

        except Exception as exc:

            logger.exception("Error eliminando reserva: %s", exc)

            st.error("No se pudo eliminar la reserva.")

def opciones_calendario(initial_view="timeGridWeek"):

    """Opciones profesionales del calendario (AgendaPro style)."""

    return {

        "initialView": initial_view,

        "editable": True,

        "selectable": True,

        "allDaySlot": False,

        "slotMinTime": "09:00:00",

        "slotMaxTime": "21:00:00",

        "slotDuration": "00:30:00",

        "slotLabelInterval": "00:30:00",

        "height": 700,

        "contentHeight": "auto",

        "headerToolbar": {

            "left": "prev,next today",

            "center": "title",

            "right": "dayGridMonth,timeGridWeek,timeGridDay",

        },

        "slotLabelFormat": {

            "meridiem": False,

            "hour": "2-digit",

            "minute": "2-digit",

        },

        "eventDisplay": "block",

        "eventTimeFormat": {

            "meridiem": False,

            "hour": "2-digit",

            "minute": "2-digit",

        },

        "eventDurationEditable": True,

        "eventStartEditable": True,

        "nowIndicator": True,

        "scrollTime": "09:00:00",

        "eventBackgroundColor": "transparent",

        "eventBorderColor": "transparent",

        "eventTextColor": "#FFFFFF",

        "dayMaxEvents": 6,

        "dayMaxEventRows": 3,

    }

def mostrar_calendario_reservas(reservas):

    """Display reservations in professional calendar week view (AgendaPro style)."""

    if not reservas:

        st.info("No hay reservas para mostrar en el calendario.")

        return


    # Convert reservations to calendar events

    eventos = construir_eventos_calendario(reservas)


    if not eventos:

        st.info("No hay eventos para mostrar.")

        return


    # Professional header with legend

    col_title, col_legend = st.columns([2, 1])

    with col_title:

        st.markdown(f"### Vista de Calendario (Semana)")


    with col_legend:

        st.markdown("""

        <div style="display: flex; gap: 12px; font-size: 11px; padding: 8px;">

            <div><span style="display: inline-block; width: 10px; height: 10px; background: #16a34a; border-radius: 2px; margin-right: 4px;"></span><strong>Pagado</strong></div>

            <div><span style="display: inline-block; width: 10px; height: 10px; background: #f59e0b; border-radius: 2px; margin-right: 4px;"></span><strong>Pendiente</strong></div>

        </div>

        """, unsafe_allow_html=True)


    # Calendar options

    options = opciones_calendario(initial_view="timeGridWeek")

    options["editable"] = False

    options["selectable"] = False

    options["height"] = 650


    try:

        calendar(

            events=eventos,

            options=options,

            key="calendario_reservas_view",

        )

    except Exception as e:

        logger.exception("Error displaying reservation calendar")

        st.error(f"Error al mostrar el calendario:\\n{traceback.format_exc()}")

def manejar_interaccion_calendario(calendar_state):

    """Maneja interacciones del calendario: clicks, drag, resize."""

    if not isinstance(calendar_state, dict):

        return

    if not st.session_state.get("db_available", True):

        return

    # Manejo de clicks en eventos - mostrar detalles y opciones

    event_click = calendar_state.get("eventClick")

    if event_click and event_click.get("event"):

        event_id = int(event_click["event"]["id"])

        st.session_state.reserva_seleccionada_id = event_id

        st.session_state.mostrar_detalles_reserva = True

        st.rerun()  # Trigger re-render to show details panel

    # Manejo de drag & drop, resize, y cambios

    for key in ("eventDrop", "eventResize", "eventChange"):

        payload = calendar_state.get(key)

        evento = payload.get("event") if isinstance(payload, dict) else None

        if evento and evento.get("id"):

            u = st.session_state.get("user")

            rol_u = normalizar_rol(u[3]) if u else ""


            if rol_u == "SUPER_ADMIN" and st.session_state.get("super_admin_all_barberias"):

                reserva = obtener_reserva_por_id(int(evento["id"]))

            else:

                bid_cal = effective_barberia_id()

                if not bid_cal:

                    continue

                reserva = obtener_reserva(int(evento["id"]), bid_cal)


            if reserva:

                with st.spinner("Actualizando reserva..."):

                    actualizar_reserva(

                        reserva.get("id"),

                        reserva.get("nombre"),

                        reserva.get("barbero"),

                        reserva.get("servicio"),

                        reserva.get("precio"),

                        normalizar_datetime(evento.get("start")),

                        normalizar_datetime(evento.get("end")),

                    )

                st.success("Reserva actualizada")

                st.rerun()

def render_agenda_interactiva(eventos, barbero_actual=None, read_only=False):

    """Renderiza calendario interactivo profesional con manejo de eventos."""

    if "mostrar_detalles_reserva" not in st.session_state:

        st.session_state.mostrar_detalles_reserva = False

    if "reserva_seleccionada_id" not in st.session_state:

        st.session_state.reserva_seleccionada_id = None


    # Professional header with legend

    col_title, col_legend = st.columns([2, 1])

    with col_title:

        st.markdown(f"### Agenda de Reservas")


    with col_legend:

        render_status_legend()


    st.markdown("---")


    # Calendar area - full width

    options = opciones_calendario()

    if read_only:

        options["editable"] = False

        options["selectable"] = False


    calendar_state = calendar(

        events=eventos,

        options=options,

        key=f"agenda_{barbero_actual or 'todos'}",

    )

    manejar_interaccion_calendario(calendar_state)


    # Details panel below calendar - full width when selected

    st.markdown("---")

    if st.session_state.get("mostrar_detalles_reserva") and st.session_state.get("reserva_seleccionada_id"):

        reserva_id = st.session_state.get("reserva_seleccionada_id")


        # RENDER HTML OUTSIDE OF COLUMN CONTEXT - FULL WIDTH

        mostrar_detalles_reserva(reserva_id)


        # Action buttons below

        col_btn_left, col_btn_right = st.columns([1, 1])


        with col_btn_left:

            if st.button("Marcar Pagado", key="btn_pagado_action", use_container_width=True):

                if marcar_reserva_pagada(reserva_id):

                    st.success("Pago registrado")

                    st.session_state.mostrar_detalles_reserva = False

                    st.rerun()


        with col_btn_right:

            if st.button("Cerrar Detalles", key="btn_cerrar_detalles", use_container_width=True, type="secondary"):

                st.session_state.mostrar_detalles_reserva = False

                st.session_state.reserva_seleccionada_id = None

                st.rerun()

    else:

        st.info("📍 Haz clic en un evento del calendario para ver detalles y opciones")

def render_gestion_agenda(barbero_actual=None):

    u = st.session_state.get("user")

    rol_g = normalizar_rol(u[3]) if u else ""

    bid_eff = effective_barberia_id()

    super_all = rol_g == "SUPER_ADMIN" and st.session_state.get("super_admin_all_barberias")

    if not super_all and not bid_eff:

        st.warning("Selecciona una barbería o asocia tu sesión a una barbería.")

        return

    if not st.session_state.get("db_available", True):

        st.warning(

            "Gestión de reservas desactivada: no hay conexión a la base de datos (modo demo)."

        )

        return

    reservas = obtener_reservas_raw(barbero_actual)

    if barbero_actual:

        barbero_options = [barbero_actual]

    else:

        db_barbers = listar_usuarios_barberos(bid_eff) if bid_eff else []

        barbero_options = [r[0] for r in db_barbers] if db_barbers else list(barberos.keys())

    servicio_options = list(servicios.keys()) + ["Bloqueo"]

    with st.expander("Crear reserva o bloqueo", expanded=False):

        with st.form("crear_reserva_calendario"):

            servicio_nuevo = st.selectbox("Servicio", servicio_options, key="agenda_servicio_nuevo")

            nombre_default = "BLOQUEADO" if servicio_nuevo == "Bloqueo" else ""

            nombre_nuevo = st.text_input("Cliente", value=nombre_default)

            barbero_nuevo = st.selectbox("Barbero", barbero_options, key="agenda_barbero_nuevo")

            inicio_nuevo = st.datetime_input("Inicio", key="agenda_inicio_nuevo")

            fin_nuevo = st.datetime_input("Fin", value=inicio_nuevo + timedelta(minutes=30), key="agenda_fin_nuevo")

            if st.form_submit_button("Crear"):

                precio_nuevo = 0 if servicio_nuevo == "Bloqueo" else servicios[servicio_nuevo]["precio"]

                nombre_final = "BLOQUEADO" if servicio_nuevo == "Bloqueo" else normalizar_texto(nombre_nuevo)

                if not nombre_final:

                    st.error("El nombre del cliente es obligatorio.")

                elif guardar_reserva(

                    nombre_final,

                    barbero_nuevo,

                    servicio_nuevo,

                    precio_nuevo,

                    inicio_nuevo,

                    fin_nuevo,

                ):

                    st.success("Reserva creada")

                    st.rerun()

    st.subheader("Editar o eliminar reserva")

    if not reservas:

        st.info("No hay reservas para editar.")

        return

    ids_reservas = [r.get("id") for r in reservas]

    reserva_id_guardada = st.session_state.get("reserva_seleccionada_id")

    index_inicial = ids_reservas.index(reserva_id_guardada) if reserva_id_guardada in ids_reservas else 0

    reserva_id = st.selectbox(

        "Reserva",

        ids_reservas,

        index=index_inicial,

        format_func=lambda rid: next(

            f"{r.get('inicio').strftime('%d-%m %H:%M') if hasattr(r.get('inicio'), 'strftime') else r.get('inicio')} - {r.get('nombre')} ({r.get('barbero')})"

            for r in reservas

            if r.get("id") == rid

        ),

    )

    reserva = next(r for r in reservas if r.get("id") == reserva_id)

    st.session_state.reserva_seleccionada_id = reserva_id

    with st.form("editar_reserva_calendario"):

        servicio_idx = servicio_options.index(reserva.get("servicio")) if reserva.get("servicio") in servicio_options else 0

        barbero_idx = barbero_options.index(reserva.get("barbero")) if reserva.get("barbero") in barbero_options else 0

        nombre_editado = st.text_input("Cliente", value=reserva.get("nombre", ""))

        servicio_editado = st.selectbox("Servicio", servicio_options, index=servicio_idx, key="agenda_servicio_editado")

        barbero_editado = st.selectbox("Barbero", barbero_options, index=barbero_idx, key="agenda_barbero_editado")

        inicio_editado = st.datetime_input("Inicio", value=reserva.get("inicio"), key="agenda_inicio_editado")

        fin_editado = st.datetime_input("Fin", value=reserva.get("fin"), key="agenda_fin_editado")

        actualizar = st.form_submit_button("Guardar cambios")

        eliminar = st.form_submit_button("Eliminar reserva")

        if actualizar:

            precio_editado = 0 if servicio_editado == "Bloqueo" else servicios[servicio_editado]["precio"]

            nombre_final = "BLOQUEADO" if servicio_editado == "Bloqueo" else normalizar_texto(nombre_editado)

            if not nombre_final:

                st.error("El nombre del cliente es obligatorio.")

            elif actualizar_reserva(

                reserva_id,

                nombre_final,

                barbero_editado,

                servicio_editado,

                precio_editado,

                inicio_editado,

                fin_editado,

            ):

                st.success("Reserva actualizada")

                st.rerun()

        if eliminar:

            if eliminar_reserva(reserva_id):

                st.session_state.reserva_seleccionada_id = None

                st.success("Reserva eliminada")

                st.rerun()

def render_modo_sin_db_banner():

    if not st.session_state.get("db_available", True):

        st.info(

            "**Modo sin base de datos** -- No hay conexión PostgreSQL disponible. "

            "Inicio de sesión, registro, reservas y sincronización de agenda están desactivados. "

            "Puedes revisar la interfaz; configura `DATABASE_URL` o `SUPABASE_DB_URL` para el modo completo."

        )

# ================= PUBLIC BOOKING FLOW (NO LOGIN) =================

def obtener_barberos_disponibles(barberia_id=None):

    """Get all active barbers for a barbershop with multi-tenant isolation.


    SECURITY: Always uses current barberia context - prevents barber leakage.

    """

    # SECURITY: Always use current context

    barberia_id = get_current_barberia_id()

    if not barberia_id:

        logger.warning("obtener_barberos_disponibles: No barberia_id in context")

        return []


    # Verify access to this barberia before returning data

    enforce_barberia_access(barberia_id)


    try:

        results = safe_fetch_all(

            """

            SELECT id, usuario AS nombre FROM usuarios 

            WHERE barberia_id = %s AND UPPER(TRIM(rol)) = 'BARBERO'

            ORDER BY usuario

            """,

            (barberia_id,)

        )

        logger.info(f"obtener_barberos_disponibles: barberia_id={barberia_id}, found {len(results) if results else 0} barbers")

        return results or []

    except Exception as e:

        logger.exception(f"Error getting barbers for barberia_id={barberia_id}: {str(e)}")

        return []

def obtener_horarios_disponibles(barberia_id=None, barbero_id=None, fecha=None, duracion_minutos=30):

    """

    Get available time slots for a barber on a specific date.

    Returns list of available times (30-min intervals from 09:00 to 20:30).


    SECURITY: Always validates barberia context before querying slots.

    """

    # SECURITY: Always use current context

    barberia_id = get_current_barberia_id()

    if not barberia_id or not barbero_id or not fecha:

        logger.warning(f"obtener_horarios_disponibles: missing params - barberia_id={barberia_id}, barbero_id={barbero_id}, fecha={fecha}")

        return []


    # SECURITY: Enforce access before querying

    enforce_barberia_access(barberia_id)


    try:

        from datetime import time as time_type


        # Get all reservations for this barber on this date

        reservas = safe_fetch_all(

            """

            SELECT inicio, fin FROM reservas

            WHERE barberia_id = %s AND barbero_id = %s AND DATE(inicio) = %s

            ORDER BY inicio

            """,

            (barberia_id, barbero_id, fecha)

        )


        logger.info(f"obtener_horarios_disponibles: found {len(reservas) if reservas else 0} existing reservations for barbero_id={barbero_id} on {fecha}")


        # Generate all 30-minute slots

        horarios_disponibles = []

        slot_time = datetime.combine(fecha, time_type(9, 0))  # Start at 09:00

        fin_dia = datetime.combine(fecha, time_type(21, 0))   # End at 21:00


        while slot_time < fin_dia:

            slot_end = slot_time + timedelta(minutes=duracion_minutos)


            # Check if this slot conflicts with any reservation

            disponible = True

            for res_inicio, res_fin in (reservas or []):

                # Check for overlap

                if slot_time < res_fin and slot_end > res_inicio:

                    disponible = False

                    break


            if disponible:

                horarios_disponibles.append(slot_time.time())


            slot_time += timedelta(minutes=30)


        logger.info(f"obtener_horarios_disponibles: returning {len(horarios_disponibles)} available slots for duration={duracion_minutos}min")

        return horarios_disponibles

    except Exception as e:

        logger.exception(f"Error getting available times for barbero={barbero_id}, fecha={fecha}: {str(e)}")

        return []

def init_booking_state():
    if "booking_step" not in st.session_state:
        st.session_state.booking_step = 1
    if "booking_data" not in st.session_state:
        st.session_state.booking_data = {}
    if "selected_fecha" not in st.session_state:
        st.session_state.selected_fecha = datetime.now().date()


def reset_booking_flow():
    st.session_state.booking_step = 1
    st.session_state.booking_data = {}
    st.session_state.selected_fecha = datetime.now().date()


def go_to_booking_step(step):
    st.session_state.booking_step = step


def update_booking_data(key, value):
    st.session_state.booking_data[key] = value


def can_advance_to_step(step):
    data = st.session_state.get("booking_data", {})
    requirements = {
        2: ["servicio", "duracion", "precio"],
        3: ["servicio", "duracion", "precio", "barbero_id", "barbero_nombre"],
        4: ["servicio", "duracion", "precio", "barbero_id", "barbero_nombre", "fecha", "hora"],
        5: ["servicio", "duracion", "precio", "barbero_id", "barbero_nombre", "fecha", "hora", "nombre", "telefono"],
        6: ["reserva_id"],
    }
    return all(data.get(key) for key in requirements.get(step, []))


def render_step_1_service_selection(servicios):
    render_step_indicator(1, 6, ["Servicio", "Barbero", "Hora", "Datos", "Revisar", "Confirmar"])
    render_booking_header(
        title="¿Qué servicio deseas?",
        subtitle="Elige una de nuestras especialidades",
        step=1,
        total_steps=6,
    )
    with render_booking_section():
        cols = st.columns(2)
        services = list(servicios.keys())
        if not services:
            st.info("No hay servicios disponibles para reservar en este momento.")
            return
        for idx, service in enumerate(services):
            with cols[idx % 2]:
                config = servicios[service]
                precio_fmt = f"${config['precio']:,}".replace(",", ".")
                if st.button(
                    f"{service}\n\n{config['duracion']} min · {precio_fmt}",
                    key=f"svc_{service}",
                    use_container_width=True,
                ):
                    update_booking_data("servicio", service)
                    update_booking_data("duracion", config["duracion"])
                    update_booking_data("precio", config["precio"])
                    go_to_booking_step(2)
                    st.rerun()


def render_step_2_barber_selection(barberia_id):
    render_step_indicator(2, 6, ["Servicio", "Barbero", "Hora", "Datos", "Resumen", "[OK] Listo!"])
    render_booking_header("Selecciona tu barbero", "¿Con quién quieres tu corte?", step=2, total_steps=6)
    with render_booking_container():
        if st.button("<- Cambiar servicio", key="back_to_svc"):
            go_to_booking_step(1)
            st.rerun()

    if st.session_state.booking_data.get("servicio"):
        servicio_nombre = st.session_state.booking_data["servicio"]
        servicio_duracion = st.session_state.booking_data.get("duracion", 0)
        servicio_precio = st.session_state.booking_data.get("precio", 0)
        precio_fmt = f"${servicio_precio:,}".replace(",", ".")
        st.info(f"Servicio: {servicio_nombre} | Duración: {servicio_duracion} min | Precio: {precio_fmt}")

    barberos = obtener_barberos_disponibles(barberia_id)
    if not barberos:
        st.info("Mostrando todos los barberos disponibles...")
        try:
            barberos = fetch_all(
                """
                SELECT id, usuario AS nombre FROM usuarios
                WHERE barberia_id = %s AND UPPER(TRIM(rol)) = 'BARBERO'
                ORDER BY usuario
                """,
                (barberia_id,),
            )
            logger.warning(f"Step 2 - Fallback query returned {len(barberos) if barberos else 0} barbers: {barberos}")
        except Exception as e:
            logger.exception(f"Step 2 - Fallback query failed: {str(e)}")
            barberos = []

    if not barberos:
        st.error("No hay barberos disponibles. Contacta al local.")
        st.stop()
        return

    st.markdown("### Selecciona tu barbero")
    if "barber_selection_loading" not in st.session_state:
        st.session_state.barber_selection_loading = False

    if st.session_state.barber_selection_loading:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            render_loading_panel("Seleccionando barbero...", padding="20px")
        import time

        time.sleep(0.2)
        go_to_booking_step(3)
        st.session_state.barber_selection_loading = False
        st.rerun()

    def on_barber_selected(barbero_id, barbero_nombre):
        update_booking_data("barbero_id", barbero_id)
        update_booking_data("barbero_nombre", barbero_nombre)
        st.session_state.barber_selection_loading = True

    selected = render_barber_selector(
        barbers=barberos,
        selected_id=st.session_state.booking_data.get("barbero_id"),
        icon="Tijeras",
        on_select_callback=on_barber_selected,
    )

    if selected:
        update_booking_data("barbero_id", selected[0])
        update_booking_data("barbero_nombre", selected[1])
        st.session_state.barber_selection_loading = True
        st.rerun()


def render_step_3_datetime_selection(barberia_id):
    from datetime import time as time_type

    render_step_indicator(3, 6, ["Servicio", "Barbero", "Hora", "Datos", "Resumen", "[OK] Listo!"])
    render_booking_header("Elige tu fecha y hora", "Cuándo te gustaría venir?", step=3, total_steps=6)
    with render_booking_container():
        if st.button("<- Volver a barbero", key="back_to_brb"):
            go_to_booking_step(2)
            st.rerun()
        fecha = st.date_input(
            "Selecciona una fecha",
            value=st.session_state.selected_fecha,
            min_value=datetime.now().date(),
            max_value=datetime.now().date() + timedelta(days=30),
            key="booking_fecha_premium",
            label_visibility="collapsed",
        )

    st.session_state.selected_fecha = fecha
    horarios = obtener_horarios_disponibles(
        barberia_id,
        st.session_state.booking_data["barbero_id"],
        fecha,
        st.session_state.booking_data["duracion"],
    )

    if not horarios:
        st.warning("No hay horarios disponibles para esta fecha. Selecciona otra fecha.")
        st.stop()
        return

    num_slots = len(horarios)
    if num_slots <= 4:
        st.warning("Quedan pocos horarios disponibles hoy")

    st.markdown(f"Horarios disponibles ({num_slots})")
    if "booking_time_loading" not in st.session_state:
        st.session_state.booking_time_loading = False

    def on_time_selected_callback(time_obj):
        import time as time_module

        time_module.sleep(0.2)
        try:
            if isinstance(time_obj, datetime):
                hora_final = time_obj.time()
            elif isinstance(time_obj, time_type):
                hora_final = time_obj
            else:
                raise ValueError(f"Invalid hora type: {type(time_obj)}")

            update_booking_data("fecha", fecha)
            update_booking_data("hora", hora_final)
            logger.info(f"Booking time set: {type(time_obj).__name__} -> {hora_final}")
        except Exception as e:
            logger.error(f"Error setting booking time: {str(e)}")
            st.error(f"Error al seleccionar hora: {str(e)}")
            st.stop()
            return

        go_to_booking_step(4)
        st.rerun()

    render_time_chips(
        available_times=horarios,
        selected_time=st.session_state.booking_data.get("hora"),
        on_time_selected=on_time_selected_callback,
        columns=5,
    )


def render_step_4_customer_form():
    render_step_indicator(4, 6, ["Servicio", "Barbero", "Hora", "Datos", "Resumen", "[OK] Listo!"])
    render_booking_header("Tu información", "Necesitamos tus datos para la reserva", step=4, total_steps=6)
    with render_booking_container():
        if st.button("<- Volver a horario", key="back_to_time"):
            go_to_booking_step(3)
            st.rerun()
        with st.form("booking_form_premium"):
            nombre = render_form_group(
                "Nombre",
                "Ej: Juan Pérez",
                "Nombre completo",
                placeholder="Ej: Juan Pérez",
                key="booking_nombre_premium",
                help="Nombre como aparecerá en tu reserva",
            )
            telefono = render_form_group(
                "Teléfono",
                "Ej: +56 9 1234 5678",
                "Teléfono",
                placeholder="Ej: +56 9 1234 5678",
                key="booking_telefono_premium",
                help="Usaremos este número para confirmarte",
            )
            email = render_form_group(
                "Email",
                "Ej: tu@email.com",
                "Email (opcional)",
                placeholder="Ej: tu@email.com",
                key="booking_email_premium",
                help="Para recibir confirmación de tu reserva",
            )

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                submit_btn = st.form_submit_button("Ver resumen", use_container_width=True, type="primary")
                if submit_btn:
                    errors = []
                    if not nombre or len(nombre) < 3:
                        errors.append("Nombre debe tener al menos 3 caracteres")
                    if not telefono or len(telefono.replace("+", "").replace(" ", "").replace("-", "")) < 9:
                        errors.append("Teléfono debe tener al menos 9 dígitos")
                    if email and "@" not in email:
                        errors.append("Email no válido")

                    if errors:
                        st.error("Revisa los siguientes errores:\n" + "\n".join(errors))
                    else:
                        update_booking_data("nombre", nombre)
                        update_booking_data("telefono", telefono)
                        update_booking_data("email", email)
                        go_to_booking_step(5)
                        st.rerun()


def render_step_5_review(barberia_id):
    render_step_indicator(5, 6, ["Servicio", "Barbero", "Hora", "Datos", "Resumen", "[OK] Listo!"])
    render_booking_header("Revisa tu reserva", "Verifica que todo esté correcto", step=5, total_steps=6)
    with render_booking_container():
        with render_booking_section("Detalles de tu cita"):
            st.write(f"**Servicio:** {st.session_state.booking_data.get('servicio')}")
            st.write(f"**Barbero:** {st.session_state.booking_data.get('barbero_nombre')}")
            st.write(f"**Fecha:** {st.session_state.booking_data.get('fecha')} a las {st.session_state.booking_data.get('hora')}")
            st.write(f"**Precio:** ${st.session_state.booking_data.get('precio', 0):,}")
        data = st.session_state.booking_data

        st.markdown("## Tus datos")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Nombre", value=data.get('nombre', 'N/A'), disabled=True)
        with col2:
            st.text_input("Teléfono", value=data.get('telefono', 'N/A'), disabled=True)
        with col3:
            st.text_input("Email", value=data.get('email', 'N/A') or "-", disabled=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancelar", key="cancel_booking_step5", use_container_width=True):
                reset_booking_flow()
                st.rerun()

        with col2:
            if st.button("Agendar mi cita", key="confirm_booking_step5", use_container_width=True, type="primary", help="Confirma tu reserva"):
                with st.spinner("Creando tu reserva..."):
                    reserva_id = insertar_reserva_con_fecha_hora(
                        barberia_id,
                        normalizar_texto(data.get('nombre', '')),
                        data.get('barbero_id'),
                        data.get('barbero_nombre'),
                        data.get('servicio'),
                        data.get('fecha'),
                        data.get('hora'),
                        data.get('precio'),
                        data.get('duracion'),
                    )

                    if reserva_id:
                        with st.spinner("Generando enlace de pago..."):
                            pago_url = crear_pago_mercadopago(
                                reserva_id,
                                data.get('precio', 0),
                                f"Reserva barbería: {data.get('servicio')}",
                                data.get('email'),
                                show_errors=True,
                            )

                            if pago_url:
                                update_booking_data("pago_url", pago_url)
                                update_booking_data("pago_pendiente", False)
                                st.session_state.booking_data.pop("pago_mensaje", None)
                            else:
                                update_booking_data("pago_url", None)
                                update_booking_data("pago_pendiente", True)
                                update_booking_data("pago_mensaje", "Reserva creada, pago pendiente")
                            go_to_booking_step(6)
                            update_booking_data("reserva_id", reserva_id)
                            st.rerun()
                    else:
                        st.error("Error al crear la reserva. Intenta nuevamente.")


def render_step_6_confirmation():
    data = st.session_state.booking_data
    render_step_indicator(6, 6, ["Servicio", "Barbero", "Hora", "Datos", "Resumen", "[OK] Listo!"])
    render_booking_header("[OK] Reserva confirmada!", "Tu cita está lista", step=6, total_steps=6)
    with render_booking_container():
        st.balloons()
        render_cta_section(
            "[OK] Reserva confirmada!",
            "Tu cita ha sido programada con éxito. Te hemos enviado un WhatsApp con la confirmación.",
            "👍",
        )
        if data.get('pago_url'):
            render_public_payment_notice()
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.link_button(
                    "Pagar ahora",
                    url=data.get('pago_url', '#'),
                    use_container_width=True,
                    help="Finaliza el pago en MercadoPago",
                )
            st.markdown('<p class="public-payment-helper">Pago seguro con MercadoPago · No guardamos datos de tu tarjeta</p>', unsafe_allow_html=True)
        elif data.get("pago_pendiente"):
            st.warning("Reserva creada, pago pendiente. Contacta al local para coordinar el pago.")

    render_public_note("Te enviamos la confirmación a WhatsApp. Revisa tu teléfono para más detalles.")
    with st.expander("Ver detalles de tu cita", expanded=False):
        render_public_booking_summary(data)
    render_public_note("Más de 100 clientes ya reservaron online.", warning=False)
    render_public_note("Tu hora está reservada. Recibirás confirmación por WhatsApp y puedes cancelar hasta 24h antes.", warning=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Volver al inicio", key="home_booking_step6", use_container_width=True):
            reset_booking_flow()
            st.rerun()
    with col2:
        if st.button("Otra cita", key="new_booking_step6", use_container_width=True):
            reset_booking_flow()
            st.rerun()


def flujo_reserva_publica():
    """Premium public booking flow without login required (AgendaPro style)."""
    apply_public_booking_css()
    init_booking_state()

    if "preselected_service" in st.session_state and st.session_state.preselected_service:
        preselected = st.session_state.preselected_service
        if preselected.get("nombre"):
            if not st.session_state.booking_data.get("servicio"):
                update_booking_data("servicio", preselected["nombre"])
                update_booking_data("duracion", preselected["duracion"])
                update_booking_data("precio", preselected["precio"])
                go_to_booking_step(2)
                st.session_state.preselected_service = None
                st.rerun()

    barberia_id = effective_barberia_id()
    if not barberia_id:
        st.error("Barbería no disponible. Contacta al administrador.")
        return

    servicios_list = obtener_servicios(barberia_id)
    servicios = {
        s["nombre"]: {"duracion": s.get("duracion") or s.get("duracion_minutos"), "precio": s["precio"]}
        for s in servicios_list if isinstance(servicios_list, list) and len(s) > 0
    }
    if not servicios:
        servicios = {}

    total_booking_steps = 6
    progress = (st.session_state.booking_step - 1) / (total_booking_steps - 1) * 100
    st.progress(int(progress) / 100, text=f"Paso {st.session_state.booking_step} de {total_booking_steps}")

    if st.session_state.booking_step == 1:
        render_step_1_service_selection(servicios)
    elif st.session_state.booking_step == 2:
        render_step_2_barber_selection(barberia_id)
    elif st.session_state.booking_step == 3:
        render_step_3_datetime_selection(barberia_id)
    elif st.session_state.booking_step == 4:
        render_step_4_customer_form()
    elif st.session_state.booking_step == 5:
        render_step_5_review(barberia_id)
    elif st.session_state.booking_step == 6:
        render_step_6_confirmation()

# ================= MÉTRICAS HELPERS =================

def calcular_metricas_header(barberia_id=None):

    """Calculate quick dashboard header metrics for today.


    SECURITY: Always uses current barberia context.

    """

    # SECURITY: Always use current context

    barberia_id = get_current_barberia_id()

    if not barberia_id or not st.session_state.get("db_available", True):

        return 0, 0, 0


    try:

        hoy = datetime.now().date()


        # Single query for all today's metrics - SAFE wrapper ensures barberia_id filter

        metrics = safe_fetch_one(

            """

            SELECT 

                COUNT(*) as total_hoy,

                COUNT(CASE WHEN pagado = TRUE THEN 1 END) as pagadas_hoy,

                COUNT(CASE WHEN pagado = FALSE THEN 1 END) as pendientes_hoy

            FROM reservas 

            WHERE barberia_id = %s AND fecha = %s

            """,

            (barberia_id, hoy),

        )


        if metrics:

            return metrics[0], metrics[1], metrics[2]

        return 0, 0, 0

    except Exception as e:

        logger.exception("Error calculando métricas header")

        return 0, 0, 0

@st.cache_data(ttl=45)

def calcular_metricas_cliente(barberia_id=None, usuario=None):

    """Fast cached client metrics with optimized queries.


    SECURITY: Always uses current context and validates user access.

    """

    # SECURITY: Always use current context

    barberia_id = get_current_barberia_id()

    if not barberia_id or not usuario or not st.session_state.get("db_available", True):

        return 0, 0, 0


    try:

        # Single query for all metrics - SAFE wrapper ensures barberia_id filter

        hoy = datetime.now().date()

        metrics = safe_fetch_one(

            """

            SELECT 

                COUNT(*) as total_reservas,

                COUNT(CASE WHEN fecha = %s THEN 1 END) as hoy_reservas

            FROM reservas 

            WHERE barberia_id = %s 

              AND (cliente = %s OR nombre = %s)

            """,

            (hoy, barberia_id, usuario, usuario),

        )


        if metrics:

            return metrics[0], metrics[1], 0

        return 0, 0, 0

    except Exception as e:

        logger.exception("Error calculando métricas cliente")

        return 0, 0, 0

@st.cache_data(ttl=45)

def calcular_metricas_barbero(barberia_id=None, barbero_id=None):

    """Fast cached barber metrics with optimized queries.


    SECURITY: Always uses current context.

    """

    # SECURITY: Always use current context

    barberia_id = get_current_barberia_id()

    if not barberia_id or not barbero_id or not st.session_state.get("db_available", True):

        return 0, 0, 0


    try:

        # Single query for all metrics - SAFE wrapper ensures barberia_id filter

        hoy = datetime.now().date()

        metrics = safe_fetch_one(

            """

            SELECT 

                COUNT(*) as total_reservas,

                COUNT(CASE WHEN fecha = %s THEN 1 END) as hoy_reservas,

                COALESCE(SUM(CASE WHEN pagado = TRUE THEN monto ELSE precio END), 0) as total_ingresos

            FROM reservas 

            WHERE barberia_id = %s AND barbero_id = %s

            """,

            (hoy, barberia_id, barbero_id),

        )


        if metrics:

            return metrics[0], metrics[1], metrics[2]

        return 0, 0, 0

    except Exception as e:

        logger.exception("Error calculando métricas barbero")

        return 0, 0, 0

@st.cache_data(ttl=45)

def calcular_metricas_admin(barberia_id=None):

    """Fast cached admin metrics with optimized queries.


    SECURITY: Always uses current context.

    """

    # SECURITY: Always use current context

    barberia_id = get_current_barberia_id()

    if not barberia_id or not st.session_state.get("db_available", True):

        return 0, 0, 0, 0


    try:

        hoy = datetime.now().date()


        # Single query for all metrics - SAFE wrapper ensures barberia_id filter

        metrics = safe_fetch_one(

            """

            SELECT 

                COUNT(*) as total_reservas,

                COUNT(CASE WHEN fecha = %s THEN 1 END) as hoy_reservas,

                COALESCE(SUM(CASE WHEN pagado = TRUE THEN monto ELSE precio END), 0) as total_ingresos,

                (SELECT COUNT(*) FROM usuarios WHERE barberia_id = %s AND UPPER(TRIM(rol)) = 'BARBERO') as num_barberos

            FROM reservas 

            WHERE barberia_id = %s

            """,

            (hoy, barberia_id, barberia_id),

        )


        if metrics:

            return metrics[0], metrics[1], metrics[2], metrics[3]

        return 0, 0, 0, 0

    except Exception as e:

        logger.exception("Error calculando métricas admin")

        return 0, 0, 0, 0

@st.cache_data(ttl=60)

def calcular_metricas_super_admin(barberia_id=None):

    """Fast cached super admin metrics - respects context (single barberia or global).


    SECURITY: Uses current barberia context if set, otherwise respects super_admin_all_barberias flag.

    """

    if not st.session_state.get("db_available", True):

        return 0, 0, 0, 0, 0


    try:

        hoy = datetime.now().date()


        # Check if SUPER_ADMIN is viewing all barberias or specific context

        viewing_all = st.session_state.get("super_admin_all_barberias", False)


        if viewing_all:

            # GLOBAL metrics - no barberia_id filter (SUPER_ADMIN chose to view all)

            # This is authorized for SUPER_ADMIN role, uses safe_fetch_one which exempts global queries

            metrics = safe_fetch_one(

                """

                SELECT 

                    (SELECT COUNT(*) FROM barberias) as num_barberias,

                    (SELECT COUNT(*) FROM usuarios) as num_usuarios,

                    (SELECT COUNT(*) FROM reservas) as num_reservas,

                    COALESCE((SELECT SUM(monto) FROM reservas WHERE pagado = TRUE), 0) as total_ingresos,

                    (SELECT COUNT(*) FROM reservas WHERE DATE(inicio) = %s) as hoy_count

                """,

                (hoy,),

            )

        else:

            # CONTEXT metrics - filter by barberia_id (SUPER_ADMIN selected a specific barberia)

            # SECURITY: Use get_current_barberia_id() instead of parameter

            barberia_id = get_current_barberia_id()

            if not barberia_id:

                return 0, 0, 0, 0, 0


            metrics = safe_fetch_one(

                """

                SELECT 

                    (SELECT COUNT(*) FROM barberias WHERE id = %s) as num_barberias,

                    (SELECT COUNT(*) FROM usuarios WHERE barberia_id = %s) as num_usuarios,

                    (SELECT COUNT(*) FROM reservas WHERE barberia_id = %s) as num_reservas,

                    COALESCE((SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND pagado = TRUE), 0) as total_ingresos,

                    (SELECT COUNT(*) FROM reservas WHERE barberia_id = %s AND DATE(inicio) = %s) as hoy_count

                """,

                (barberia_id, barberia_id, barberia_id, barberia_id, barberia_id, hoy),

            )


        if metrics:

            return metrics[0], metrics[1], metrics[2], metrics[3], metrics[4]

        return 0, 0, 0, 0, 0

    except Exception as e:

        logger.exception("Error calculando métricas super admin")

        return 0, 0, 0, 0, 0

def render_dashboard_cards(col_count, cards_data):

    """Renderiza cards de métricas con layout flexible."""

    cols = st.columns(col_count)

    for idx, (col, card) in enumerate(zip(cols, cards_data)):

        with col:

            st.metric(card["label"], card["value"], card.get("delta", None))

# ================= MULTI-BARBERIA PUBLIC ACCESS =================

def obtener_barberia_por_slug(slug):

    """Get barberia by slug for public booking."""

    if not slug:

        return None

    try:

        result = fetch_one(

            """SELECT id, nombre, slug, telefono, email, ciudad, direccion, 

                      latitud, longitud, color_primario, logo_url, 

                      hora_apertura, hora_cierre, estado 

               FROM barberias WHERE slug = %s""",

            (slug,),

        )

        if result:

            return {

                "id": result[0],

                "nombre": result[1],

                "slug": result[2],

                "telefono": result[3],

                "email": result[4],

                "ciudad": result[5],

                "direccion": result[6],

                "latitud": result[7],

                "longitud": result[8],

                "color_primario": result[9],

                "logo_url": result[10],

                "hora_apertura": result[11],

                "hora_cierre": result[12],

                "estado": result[13],

            }

        return None

    except Exception as e:

        logger.exception(f"Error getting barberia by slug: {str(e)}")

        return None

def obtener_servicios(barberia_id=None):

    """Load services from database for a barberia.


    SECURITY: Always uses current barberia context - prevents service leakage between barberias.

    """

    # SECURITY: Always use current context

    barberia_id = get_current_barberia_id()

    if not barberia_id:

        return []

    try:

        results = safe_fetch_all(

            """SELECT id, nombre, duracion_minutos, precio, descripcion, icono 

               FROM servicios 

               WHERE barberia_id = %s 

               ORDER BY id ASC""",

            (barberia_id,),

        )

        servicios_list = []

        for row in results:

            servicios_list.append({

                "id": row[0],

                "nombre": row[1],

                "duracion": row[2],

                "precio": row[3],

                "descripcion": row[4],

                "icono": row[5] or "Servicio",

            })

        # If no services in DB, return empty list (UI will show message)

        return servicios_list

    except Exception as e:

        logger.exception(f"Error loading services for barberia {barberia_id}: {e}")

        return []


def crear_servicio(barberia_id, nombre, duracion, precio, descripcion, icono):

    """Insert a new service for a barberia. Returns True on success."""

    current = get_current_barberia_id()

    if int(barberia_id) != int(current):

        raise Exception("SECURITY: barberia_id mismatch in crear_servicio")

    try:

        execute_write(

            """INSERT INTO servicios (barberia_id, nombre, duracion_minutos, precio, descripcion, icono)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (barberia_id, nombre) DO NOTHING""",

            (barberia_id, nombre.strip(), int(duracion), int(precio), descripcion.strip(), icono.strip()),

        )

        return True

    except Exception as e:

        logger.exception(f"Error creating service: {e}")

        return False


def actualizar_servicio(servicio_id, barberia_id, nombre, duracion, precio, descripcion, icono):

    """Update an existing service. Enforces barberia_id ownership."""

    current = get_current_barberia_id()

    if int(barberia_id) != int(current):

        raise Exception("SECURITY: barberia_id mismatch in actualizar_servicio")

    try:

        execute_write(

            """UPDATE servicios
               SET nombre = %s, duracion_minutos = %s, precio = %s, descripcion = %s, icono = %s
               WHERE id = %s AND barberia_id = %s""",

            (nombre.strip(), int(duracion), int(precio), descripcion.strip(), icono.strip(), int(servicio_id), int(barberia_id)),

        )

        return True

    except Exception as e:

        logger.exception(f"Error updating service {servicio_id}: {e}")

        return False


def eliminar_servicio(servicio_id, barberia_id):

    """Delete a service. Enforces barberia_id ownership."""

    current = get_current_barberia_id()

    if int(barberia_id) != int(current):

        raise Exception("SECURITY: barberia_id mismatch in eliminar_servicio")

    try:

        execute_write(

            "DELETE FROM servicios WHERE id = %s AND barberia_id = %s",

            (int(servicio_id), int(barberia_id)),

        )

        return True

    except Exception as e:

        logger.exception(f"Error deleting service {servicio_id}: {e}")

        return False

# ================= BARBER SHOP REGISTRATION FLOW (PRODUCTION) =================

# --------- GEOCODING FUNCTIONS ---------

def geocode_address(direccion: str, ciudad: str = ""):

    """Convert address to latitude and longitude using Nominatim (OpenStreetMap)."""

    if not direccion or not direccion.strip():

        return None, None


    if Nominatim is None:

        logger.warning("geopy not installed, geocoding disabled")

        return None, None


    try:

        full_address = f"{direccion}, {ciudad}".strip()

        geolocator = Nominatim(user_agent="barberia_app_v2")

        location = geolocator.geocode(full_address, timeout=5)


        if location:

            logger.info(f"[OK] Geocoded address: {full_address} -> ({location.latitude}, {location.longitude})")

            return float(location.latitude), float(location.longitude)

        else:

            logger.warning(f"[AVISO] Could not geocode address: {full_address}")

            return None, None


    except (GeocoderTimedOut, GeocoderUnavailable) as e:

        logger.warning(f"[AVISO] Geocoding service unavailable: {e}")

        return None, None

    except Exception as e:

        logger.warning(f"[AVISO] Error geocoding address '{full_address}': {e}")

        return None, None

# --------- VALIDATION FUNCTIONS ---------

def validate_basic_info(data):

    """Validate Step 1 - Basic Information."""

    errors = []


    if not data.get("nombre", "").strip():

        errors.append("Nombre de barbería es requerido")


    if not data.get("ciudad", "").strip():

        errors.append("Ciudad es requerida")


    if not data.get("telefono", "").strip():

        errors.append("Teléfono es requerido")


    email = data.get("email", "").strip()

    if not email:

        errors.append("Email es requerido")

    elif "@" not in email or "." not in email:

        errors.append("Email inválido")


    if not data.get("direccion", "").strip():

        errors.append("Dirección del local es requerida")


    return errors

def validate_services(services):

    """Validate Step 3 - Services."""

    valid_services = [s for s in services if s.get("nombre", "").strip()]


    if not valid_services:

        return ["Agrega al menos un servicio"], []


    for service in valid_services:

        if service.get("precio", 0) <= 0:

            return [f"Servicio '{service['nombre']}' debe tener precio mayor a 0"], []

        if service.get("duracion", 0) < 15:

            return [f"Servicio '{service['nombre']}' debe tener al menos 15 minutos"], []


    return [], valid_services

def validate_barbers(barbers):

    """Validate Step 4 - Barbers."""

    valid_barbers = [

        b for b in barbers 

        if b.get("nombre", "").strip() and 

           b.get("apellido", "").strip() and 

           b.get("usuario", "").strip()

    ]


    if not valid_barbers:

        return ["Agrega al menos un barbero con nombre, apellido y usuario"], []


    # Check for duplicate usernames

    usernames = [b.get("usuario", "").lower() for b in valid_barbers]

    if len(usernames) != len(set(usernames)):

        return ["Los nombres de usuario deben ser únicos"], []


    return [], valid_barbers

def check_barberia_name_exists(nombre):

    """Check if barber shop name already exists."""

    try:

        existing = fetch_one(

            "SELECT id FROM barberias WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",

            (nombre,)

        )

        return existing is not None

    except Exception as e:

        logger.warning(f"Error checking barberia name: {str(e)}")

        return False

# --------- DATABASE FUNCTIONS ---------

def create_barberia_in_db(data):

    """Create barberia record in database. Returns barberia_id or None."""

    # Generate slug: lowercase, replace spaces with hyphens, handle special chars

    nombre = data["nombre"].lower()

    slug = nombre.replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("?", "u").replace("ñ", "n")

    slug = "".join(c for c in slug if c.isalnum() or c in "-_")  # Remove special chars


    try:

        result = execute_write(

            """

            INSERT INTO barberias 

            (nombre, slug, telefono, email, ciudad, direccion, latitud, longitud,

             color_primario, hora_apertura, hora_cierre, logo_url, estado)

            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

            RETURNING id

            """,

            (

                data["nombre"],

                slug,

                data["telefono"],

                data["email"],

                data["ciudad"],

                data.get("direccion") or None,

                data.get("latitud"),

                data.get("longitud"),

                data["color_primario"],

                data["hora_apertura"],

                data["hora_cierre"],

                data["logo_url"] or None,

                "activa"

            ),

            fetch_one_result=True

        )


        if result and result[0]:

            logger.info(f"[OK] Barbería creada: {data['nombre']} (ID: {result[0]}, Slug: {slug})")

            return result[0]

        return None

    except Exception as e:

        logger.exception(f"Error creating barberia: {str(e)}")

        return None

def create_admin_user_in_db(barberia_id, slug, telefono):

    """Create admin user. Returns (username, password) or (None, None)."""

    admin_user = f"admin_{slug}"

    admin_password = "admin123"

    admin_hash = hash_password(admin_password)


    try:

        execute_write(

            """

            INSERT INTO usuarios (usuario, password, rol, barberia_id, telefono)

            VALUES (%s, %s, %s, %s, %s)

            """,

            (admin_user, admin_hash, "ADMIN", barberia_id, telefono)

        )

        logger.info(f"[OK] Admin user creado: {admin_user}")

        return admin_user, admin_password

    except Exception as e:

        logger.exception(f"Error creating admin user: {str(e)}")

        return None, None

def create_services_in_db(barberia_id, services):

    """Create services. Returns count of created services."""

    count = 0

    try:

        for service in services:

            execute_write(

                """

                INSERT INTO servicios 

                (barberia_id, nombre, duracion_minutos, precio, icono)

                VALUES (%s, %s, %s, %s, %s)

                """,

                (

                    barberia_id,

                    service["nombre"],

                    service["duracion"],

                    int(service["precio"]),

                    "Servicio"

                )

            )

            count += 1

        logger.info(f"[OK] Servicios creados: {count}")

        return count

    except Exception as e:

        logger.exception(f"Error creating services: {str(e)}")

        return 0

def create_barbers_in_db(barberia_id, barbers):

    """Create barber users. Returns dict of username:password pairs."""

    barber_passwords = {}

    try:

        for barber in barbers:

            barber_password = f"barber_{barber['usuario'][:3]}123"

            barber_hash = hash_password(barber_password)

            nombre_completo = f"{barber['nombre']} {barber['apellido']}"


            execute_write(

                """

                INSERT INTO usuarios (usuario, password, rol, barberia_id, telefono, nombre, apellido)

                VALUES (%s, %s, %s, %s, %s, %s, %s)

                """,

                (

                    barber["usuario"],

                    barber_hash,

                    "BARBERO",

                    barberia_id,

                    None,

                    barber["nombre"],

                    barber["apellido"]

                )

            )

            barber_passwords[barber["usuario"]] = barber_password


        logger.info(f"[OK] Barberos creados: {len(barber_passwords)}")

        return barber_passwords

    except Exception as e:

        logger.exception(f"Error creating barbers: {str(e)}")

        return {}

# --------- UI RENDER FUNCTIONS ---------

def render_header_and_progress(step):

    """Render header with title and progress bar."""

    render_hero_banner(
        "Crea Tu Barbería",
        "En 5 simples pasos estarás listo",
        "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);padding: 40px;border-radius: 20px;text-align: center;color: white;",
        title_size="2.5em",
        subtitle_size="1.1em",
        margin_bottom="40px",
    )


    progress_pct = (step - 1) / 5

    st.progress(progress_pct, text=f"Paso {step} de 5")

def render_step_1_basic_info(data):

    """Render Step 1: Basic Information."""

    st.markdown("## Paso 1: Información Básica")

    st.markdown("Cuéntanos los datos de tu barbería")


    col1, col2 = st.columns(2)

    with col1:

        data["nombre"] = st.text_input(

            "Nombre de la barbería",

            value=data["nombre"],

            placeholder="Ej: Barbería El Clásico"

        )

    with col2:

        data["ciudad"] = st.text_input(

            "Ciudad",

            value=data["ciudad"],

            placeholder="Ej: Buenos Aires"

        )


    col1, col2 = st.columns(2)

    with col1:

        data["telefono"] = st.text_input(

            "Teléfono",

            value=data["telefono"],

            placeholder="Ej: +56912345678"

        )

    with col2:

        data["email"] = st.text_input(

            "Email",

            value=data["email"],

            placeholder="Ej: info@mibarber.com"

        )


    # Address input

    data["direccion"] = st.text_input(

        "Dirección del local",

        value=data["direccion"],

        placeholder="Ej: Av. Principal 123, Piso 2",

        help="Dirección completa para localizar tu barbería en el mapa"

    )


    # Geocode and show map preview if address is entered

    if data.get("direccion", "").strip():

        with st.spinner("Localizando dirección en el mapa..."):

            lat, lng = geocode_address(data["direccion"], data.get("ciudad", ""))

            if lat and lng:

                data["latitud"] = lat

                data["longitud"] = lng

                st.success(f"Ubicación encontrada: ({lat:.4f}, {lng:.4f})")

                # Display map with the location

                map_data = pd.DataFrame({

                    "latitude": [lat],

                    "longitude": [lng]

                })

                st.map(map_data)

            else:

                if Nominatim is not None:

                    st.warning("No se pudo encontrar la ubicación. Verifica la dirección e intenta de nuevo.")

                else:

                    st.info("Localización automática no disponible. Instala geopy para habilitar mapas.")


    # Validation and navigation

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:

        if st.button("Continuar", use_container_width=True, type="primary", key="step1_next"):

            errors = validate_basic_info(data)

            if errors:

                for error in errors:

                    st.error(f"{error}")

            elif check_barberia_name_exists(data["nombre"]):

                st.error("Este nombre de barbería ya existe")

            else:

                st.session_state.registration_step = 2

                st.rerun()

def render_step_2_branding(data):

    """Render Step 2: Branding."""

    st.markdown("## Paso 2: Branding")

    st.markdown("Personaliza la apariencia de tu barbería")


    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Color Primario")

        data["color_primario"] = st.color_picker(

            "Elige el color principal",

            value=data.get("color_primario", "#667eea"),

            label_visibility="collapsed"

        )


    with col2:

        st.subheader("Logo (Opcional)")

        data["logo_url"] = st.text_input(

            "URL del logo",

            value=data.get("logo_url", ""),

            placeholder="https://ejemplo.com/logo.png"

        )


    # Preview

    st.markdown("---")

    st.markdown("### Vista Previa")

    preview_col1, preview_col2 = st.columns([1, 2])

    with preview_col1:

        render_preview_card(data['nombre'], data['color_primario'])

    with preview_col2:

        st.info(f"{data['ciudad']} · {data['telefono']}")


    # Navigation

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button("Atrás", use_container_width=True, key="step2_back"):

            st.session_state.registration_step = 1

            st.rerun()

    with col3:

        if st.button("Continuar", use_container_width=True, type="primary", key="step2_next"):

            st.session_state.registration_step = 3

            st.rerun()

def render_step_3_services(data):

    """Render Step 3: Services."""

    st.markdown("## Paso 3: Servicios")

    st.markdown("Define los servicios que ofreces")


    if not data["servicios"]:

        data["servicios"] = [{"nombre": "", "precio": 0, "duracion": 30}]


    for idx, service in enumerate(data["servicios"]):

        col_name, col_price, col_duration, col_del = st.columns([2, 1, 1, 0.5])


        with col_name:

            data["servicios"][idx]["nombre"] = st.text_input(

                "Servicio",

                value=service["nombre"],

                placeholder="Ej: Corte",

                label_visibility="collapsed",

                key=f"service_name_{idx}"

            )

        with col_price:

            data["servicios"][idx]["precio"] = st.number_input(

                "Precio",

                value=service["precio"],

                min_value=0,

                label_visibility="collapsed",

                key=f"service_price_{idx}"

            )

        with col_duration:

            data["servicios"][idx]["duracion"] = st.number_input(

                "Min",

                value=service["duracion"],

                min_value=15,

                step=15,

                label_visibility="collapsed",

                key=f"service_duration_{idx}"

            )

        with col_del:

            if st.button("Eliminar", key=f"del_service_{idx}", use_container_width=True):

                data["servicios"].pop(idx)

                st.rerun()


    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:

        if st.button("Agregar Servicio", use_container_width=True, key="add_service"):

            data["servicios"].append({"nombre": "", "precio": 0, "duracion": 30})

            st.rerun()


    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button("Atrás", use_container_width=True, key="step3_back"):

            st.session_state.registration_step = 2

            st.rerun()

    with col3:

        if st.button("Continuar", use_container_width=True, type="primary", key="step3_next"):

            errors, valid_services = validate_services(data["servicios"])

            if errors:

                for error in errors:

                    st.error(f"{error}")

            else:

                data["servicios"] = valid_services

                st.session_state.registration_step = 4

                st.rerun()

def render_step_4_barbers(data):

    """Render Step 4: Barbers."""

    st.markdown("## Paso 4: Barberos")

    st.markdown("Agrega los barberos de tu equipo")


    if not data["barberos"]:

        data["barberos"] = [{"nombre": "", "apellido": "", "usuario": ""}]


    for idx, barber in enumerate(data["barberos"]):

        col_first, col_last, col_user, col_del = st.columns([1.5, 1.5, 1.5, 0.5])


        with col_first:

            data["barberos"][idx]["nombre"] = st.text_input(

                "Nombre",

                value=barber.get("nombre", ""),

                placeholder="Ej: Juan",

                label_visibility="collapsed",

                key=f"barber_first_{idx}"

            )

        with col_last:

            data["barberos"][idx]["apellido"] = st.text_input(

                "Apellido",

                value=barber.get("apellido", ""),

                placeholder="Ej: García",

                label_visibility="collapsed",

                key=f"barber_last_{idx}"

            )

        with col_user:

            data["barberos"][idx]["usuario"] = st.text_input(

                "Usuario",

                value=barber.get("usuario", ""),

                placeholder="Ej: juan.garcia",

                label_visibility="collapsed",

                key=f"barber_user_{idx}"

            )

        with col_del:

            if st.button("Eliminar", key=f"del_barber_{idx}", use_container_width=True):

                data["barberos"].pop(idx)

                st.rerun()


    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:

        if st.button("Agregar Barbero", use_container_width=True, key="add_barber"):

            data["barberos"].append({"nombre": "", "apellido": "", "usuario": ""})

            st.rerun()


    st.info("Los barberos cambiarán su contraseña al primer acceso")


    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button("Atrás", use_container_width=True, key="step4_back"):

            st.session_state.registration_step = 3

            st.rerun()

    with col3:

        if st.button("Continuar", use_container_width=True, type="primary", key="step4_next"):

            errors, valid_barbers = validate_barbers(data["barberos"])

            if errors:

                for error in errors:

                    st.error(f"[AVISO] {error}")

            else:

                data["barberos"] = valid_barbers

                st.session_state.registration_step = 5

                st.rerun()

def render_step_5_schedule(data):

    """Render Step 5: Schedule."""

    st.markdown("## Paso 5: Horario de funcionamiento")

    st.markdown("Define tu horario de atención")


    col1, col2 = st.columns(2)

    with col1:

        data["hora_apertura"] = st.time_input(

            "Apertura Apertura",

            value=datetime.strptime(data["hora_apertura"], "%H:%M").time(),

            label_visibility="collapsed"

        )

        data["hora_apertura"] = data["hora_apertura"].strftime("%H:%M")


    with col2:

        data["hora_cierre"] = st.time_input(

            "Cierre Cierre",

            value=datetime.strptime(data["hora_cierre"], "%H:%M").time(),

            label_visibility="collapsed"

        )

        data["hora_cierre"] = data["hora_cierre"].strftime("%H:%M")


    st.markdown("---")

    st.markdown("### Resumen")


    col1, col2 = st.columns(2)

    with col1:

        st.markdown(f"""

        **Ubicación**

        - {data['nombre']}

        - {data['ciudad']}

        """)

    with col2:

        st.markdown(f"""

        **Operaciones**

        - {data['hora_apertura']} a {data['hora_cierre']}

        - {len(data['servicios'])} servicios

        - {len(data['barberos'])} barberos

        """)


    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button("Atrás", use_container_width=True, key="step5_back"):

            st.session_state.registration_step = 4

            st.rerun()


    with col3:

        if st.button("Crear Barbería", use_container_width=True, type="primary", key="create_barberia"):

            create_barberia_and_transition(data)

def render_success_screen():

    """Render success screen with improved visual design."""

    barberia = st.session_state.get("barberia_created", {})

    data = st.session_state.get("registration_data", {})


    # Animated success header

    render_success_hero(
        "¡Tu Barbería está Lista!",
        "En menos de 2 minutos ya puedes recibir reservas",
    )


    # Main booking link section

    st.markdown("### Link de Reservas")

    booking_url = f"http://tudominio.com?barberia={barberia.get('slug')}"


    col_link, col_copy = st.columns([4, 1])

    with col_link:

        st.code(booking_url, language="text")

    with col_copy:

        st.info("Copia este link")


    st.success(f"Comparte este link con tus clientes para que agendan")


    # Credentials section

    st.markdown("---")

    st.markdown("### Acceso a Tu Panel")


    cred_col1, cred_col2 = st.columns(2)

    with cred_col1:

        st.markdown(f"""

        **Admin**


        Usuario: `{barberia.get('admin_user')}`


        Contraseña: `{barberia.get('admin_password')}`


        Cambia esta contraseña al primer acceso

        """)

        st.code(f"Usuario: {barberia.get('admin_user')}\nContraseña: {barberia.get('admin_password')}", language="text")


    with cred_col2:

        st.markdown("**Barberos**")

        for usuario, password in barberia.get('barber_passwords', {}).items():

            st.code(f"{usuario}: {password}", language="text")

        st.caption("📍 Cada barbero debe cambiar su contraseña al primer acceso")


    # Next steps

    st.markdown("---")

    st.markdown("### Próximos pasos")


    step_col1, step_col2, step_col3 = st.columns(3)

    with step_col1:

        st.markdown("""

        **1. Inicia sesión**


        Usa tus credenciales de admin para acceder

        """)

    with step_col2:

        st.markdown("""

        **2. Comparte el link**


        Envía a clientes por WhatsApp, email o redes

        """)

    with step_col3:

        st.markdown("""

        **3. Recibe reservas**


        Los clientes agendan sin crear cuenta

        """)


    # Action buttons

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        if st.button("Nueva barbería", use_container_width=True):

            st.session_state.registration_step = 1

            st.session_state.registration_data = {

                "nombre": "", "ciudad": "", "telefono": "", "email": "",

                "direccion": "", "latitud": None, "longitud": None,

                "color_primario": "#667eea", "logo_url": "",

                "servicios": [], "barberos": [],

                "hora_apertura": "09:00", "hora_cierre": "18:00"

            }

            st.rerun()


    with col4:

        if st.button("Ir a Login", use_container_width=True, type="primary"):

            st.session_state.view = "login"

            st.rerun()

# --------- MAIN CONTROLLER ---------

def create_barberia_and_transition(data):

    """Main orchestration: Create barberia and all related data."""

    with st.spinner("Cargando Creando tu barbería..."):

        try:

            # Step 1: Create barberia

            slug = data["nombre"].lower().replace(" ", "-").replace("ía", "ia")

            barberia_id = create_barberia_in_db(data)


            if not barberia_id:

                st.error("Error creando la barbería")

                return


            # Step 2: Create admin user

            admin_user, admin_password = create_admin_user_in_db(barberia_id, slug, data["telefono"])

            if not admin_user:

                st.error("Error creando usuario administrador")

                return


            # Step 3: Create services

            service_count = create_services_in_db(barberia_id, data["servicios"])

            if service_count == 0:

                st.error("Error creando servicios")

                return


            # Step 4: Create barbers

            barber_passwords = create_barbers_in_db(barberia_id, data["barberos"])

            if not barber_passwords:

                st.error("Error creando barberos")

                return


            # Success: Save to session and show success screen

            st.session_state.registration_step = "success"

            st.session_state.barberia_created = {

                "id": barberia_id,

                "slug": slug,

                "nombre": data["nombre"],

                "admin_user": admin_user,

                "admin_password": admin_password,

                "barber_passwords": barber_passwords

            }

            st.success("¡Barbería creada exitosamente!")

            st.rerun()


        except Exception as e:

            logger.exception(f"Error en create_barberia_and_transition: {str(e)}")

            st.error(f"Error: {str(e)}")

def render_registro_barberia():

    """Main registration flow controller."""

    # Initialize session state

    if "registration_step" not in st.session_state:

        st.session_state.registration_step = 1

    if "registration_data" not in st.session_state:

        st.session_state.registration_data = {

            "nombre": "",

            "ciudad": "",

            "telefono": "",

            "email": "",

            "direccion": "",

            "latitud": None,

            "longitud": None,

            "color_primario": "#667eea",

            "logo_url": "",

            "servicios": [],

            "barberos": [],

            "hora_apertura": "09:00",

            "hora_cierre": "18:00"

        }


    data = st.session_state.registration_data

    step = st.session_state.registration_step


    # Render header and progress

    render_header_and_progress(step if isinstance(step, int) else 1)


    # Route to appropriate step

    if step == 1:

        render_step_1_basic_info(data)

    elif step == 2:

        render_step_2_branding(data)

    elif step == 3:

        render_step_3_services(data)

    elif step == 4:

        render_step_4_barbers(data)

    elif step == 5:

        render_step_5_schedule(data)

    elif step == "success":

        render_success_screen()

def render_hero_marketplace():

    """Render marketplace-style hero section with search bar."""

    # Hero Section Styling

    st.markdown("""

    <style>

        .stApp {
            background: #080808 !important;
        }

        .block-container,
        [data-testid="stMainBlockContainer"] {
            max-width: 1120px !important;
            margin: 0 auto;
            padding: 1.25rem 1.5rem 2rem !important;
        }

        /* Hero Container */

        .hero-container {

            background: linear-gradient(135deg, #0f0f0f 0%, #1a1505 100%);

            padding: 80px 40px;

            border-radius: 20px;

            text-align: center;

            margin: 0 -40px 60px -40px;

            color: white;

            border: 1px solid rgba(197,159,85,0.2);

        }


        /* Hero Title */

        .hero-title {

            font-size: 48px;

            font-weight: 700;

            margin: 0 0 20px 0;

            line-height: 1.3;

            letter-spacing: -1px;

        }


        /* Hero Subtitle */

        .hero-subtitle {

            font-size: 18px;

            font-weight: 400;

            opacity: 0.95;

            margin: 0 0 50px 0;

            max-width: 600px;

            margin-left: auto;

            margin-right: auto;

            line-height: 1.6;

        }


        /* Search Bar Styling */

        .search-container {

            background: #111111;

            padding: 20px;

            border-radius: 16px;

            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);

            margin-top: 28px;

            max-width: 900px;

            margin-left: auto;

            margin-right: auto;

            border: 1px solid rgba(197,159,85,0.25);

        }


        /* Input Field Styling */

        .search-input input {

            border-radius: 10px !important;

            border: 2px solid #e0e0e0 !important;

            padding: 14px 16px !important;

            font-size: 16px !important;

            transition: all 0.3s ease !important;

            height: 50px !important;

        }


        .search-input input:focus {

            border-color: #c5a028 !important;

            box-shadow: 0 0 0 3px rgba(197,160,40,0.2) !important;

            outline: none !important;

        }


        /* Search Button Styling */

        .search-button button {

            background: linear-gradient(135deg, #c5a028 0%, #8a6e17 100%) !important;

            color: #080808 !important;

            border: none !important;

            border-radius: 10px !important;

            padding: 0 30px !important;

            font-size: 16px !important;

            font-weight: 700 !important;

            height: 50px !important;

            cursor: pointer !important;

            transition: all 0.3s ease !important;

            box-shadow: 0 4px 15px rgba(197,160,40,0.35) !important;

            width: 100% !important;

        }


        .search-button button:hover {

            transform: translateY(-2px) !important;

            box-shadow: 0 8px 25px rgba(197,160,40,0.5) !important;

        }


        .search-button button:active {

            transform: translateY(0) !important;

        }


        /* Responsive adjustments */

        @media (max-width: 768px) {

            .hero-title {

                font-size: 32px;

            }

            .hero-subtitle {

                font-size: 16px;

            }

            .search-container {

                padding: 20px;

            }

        }

    </style>

    """, unsafe_allow_html=True)


    # Hero Section

    st.title("Agenda servicios de barbería en segundos")

    st.markdown(
        "Encuentra las mejores barberías de tu zona y reserva tu corte con un solo click"
    )


    # Search Bar with 3 columns

    st.markdown('<div class="search-container">', unsafe_allow_html=True)


    col1, col2, col3 = st.columns([1.5, 1.5, 1], gap="medium")


    with col1:

        st.markdown('<div class="search-input">', unsafe_allow_html=True)

        servicio = st.text_input(

            "Servicio",

            placeholder="Ej: Corte, Barba...",

            label_visibility="collapsed"

        )

        st.markdown('</div>', unsafe_allow_html=True)


    with col2:

        st.markdown('<div class="search-input">', unsafe_allow_html=True)

        ubicacion = st.text_input(

            "Ubicación",

            placeholder="Tu ciudad o zona...",

            label_visibility="collapsed"

        )

        st.markdown('</div>', unsafe_allow_html=True)


    with col3:

        st.markdown('<div class="search-button">', unsafe_allow_html=True)

        search_clicked = st.button(

            "Buscar",

            use_container_width=True,

            key="hero_search_button"

        )

        st.markdown('</div>', unsafe_allow_html=True)


    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")  # Spacing


    return search_clicked, servicio, ubicacion

# ================= MARKETPLACE RESULTS - SPLIT SCREEN WITH MAP =================

def render_modal_booking(barberia):

    """Render booking as modal overlay without page navigation."""

    from datetime import time as time_type


    # Initialize modal state

    if "modal_booking_open" not in st.session_state:

        st.session_state.modal_booking_open = False

    if "modal_booking_step" not in st.session_state:

        st.session_state.modal_booking_step = 1

    if "modal_booking_data" not in st.session_state:

        st.session_state.modal_booking_data = {}

    if "modal_selected_fecha" not in st.session_state:

        st.session_state.modal_selected_fecha = datetime.now().date()


    barberia_id = barberia.get("id")


    # Modal overlay HTML/CSS

    modal_html = """

    <style>

        /* Modal Overlay Styles */

        .modal-overlay {

            position: fixed;

            top: 0;

            left: 0;

            right: 0;

            bottom: 0;

            background-color: rgba(0, 0, 0, 0.6);

            display: flex;

            align-items: center;

            justify-content: center;

            z-index: 9999;

            backdrop-filter: blur(4px);

        }


        .modal-container {

            background: white;

            border-radius: 20px;

            padding: 32px;

            max-width: 500px;

            width: 90%;

            max-height: 85vh;

            overflow-y: auto;

            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);

            animation: slideUp 0.3s ease-out;

        }


        @keyframes slideUp {

            from {

                opacity: 0;

                transform: translateY(30px);

            }

            to {

                opacity: 1;

                transform: translateY(0);

            }

        }


        .modal-header {

            display: flex;

            justify-content: space-between;

            align-items: center;

            margin-bottom: 24px;

            padding-bottom: 16px;

            border-bottom: 2px solid #f0f0f0;

        }


        .modal-title {

            font-size: 22px;

            font-weight: 700;

            margin: 0;

            color: #1a1a1a;

        }


        .modal-close-btn {

            background: none;

            border: none;

            font-size: 28px;

            cursor: pointer;

            color: #999;

            padding: 0;

            width: 32px;

            height: 32px;

            display: flex;

            align-items: center;

            justify-content: center;

            border-radius: 50%;

            transition: all 0.2s ease;

        }


        .modal-close-btn:hover {

            background: #f0f0f0;

            color: #333;

        }


        .modal-content {

            margin-bottom: 24px;

        }


        .modal-progress {

            background: #e0e0e0;

            height: 4px;

            border-radius: 2px;

            margin-bottom: 24px;

            overflow: hidden;

        }


        .modal-progress-bar {

            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);

            height: 100%;

            transition: width 0.3s ease;

        }


        .modal-section-title {

            font-size: 18px;

            font-weight: 600;

            margin-bottom: 16px;

            color: #1a1a1a;

        }


        .modal-service-card {

            background: #f8f9fa;

            border: 2px solid #e0e0e0;

            border-radius: 12px;

            padding: 16px;

            margin-bottom: 12px;

            cursor: pointer;

            transition: all 0.3s ease;

            text-align: center;

        }


        .modal-service-card:hover {

            border-color: #667eea;

            background: #f0f4ff;

            transform: translateY(-2px);

        }


        .modal-service-card.selected {

            border-color: #667eea;

            background: linear-gradient(135deg, #f0f4ff 0%, #f8f1ff 100%);

            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);

        }


        .modal-buttons {

            display: flex;

            gap: 12px;

            margin-top: 24px;

        }


        .modal-btn-secondary {

            flex: 1;

            padding: 12px;

            border: 2px solid #e0e0e0;

            background: white;

            border-radius: 10px;

            cursor: pointer;

            font-weight: 600;

            transition: all 0.2s ease;

        }


        .modal-btn-secondary:hover {

            border-color: #667eea;

            color: #667eea;

        }


        .modal-btn-primary {

            flex: 1;

            padding: 12px;

            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

            color: white;

            border: none;

            border-radius: 10px;

            cursor: pointer;

            font-weight: 600;

            transition: all 0.2s ease;

        }


        .modal-btn-primary:hover {

            transform: translateY(-2px);

            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);

        }


        .modal-btn-primary:disabled {

            opacity: 0.6;

            cursor: not-allowed;

            transform: none;

        }

    </style>

    """


    st.markdown(modal_html, unsafe_allow_html=True)


    # Load services

    servicios_list = obtener_servicios(barberia_id)

    servicios = {s["nombre"]: {"duracion": s["duracion"], "precio": s["precio"]} 

                 for s in servicios_list}


    # Modal content container

    st.markdown('<div class="modal-overlay"><div class="modal-container">', unsafe_allow_html=True)


    # Modal header with close button

    col_title, col_close = st.columns([10, 1])

    with col_title:

        st.markdown(f'<h2 class="modal-title">Reservar en {barberia.get("nombre", "Barbería")}</h2>', 

                   unsafe_allow_html=True)

    with col_close:

        if st.button("Cerrar", key="modal_close_btn", help="Cerrar"):

            st.session_state.modal_booking_open = False

            st.session_state.modal_booking_step = 1

            st.session_state.modal_booking_data = {}

            st.rerun()


    # Progress bar

    progress_pct = (st.session_state.modal_booking_step - 1) / 3 * 100

    st.markdown(f"""

    <div class="modal-progress">

        <div class="modal-progress-bar" style="width: {progress_pct}%"></div>

    </div>

    """, unsafe_allow_html=True)


    # ===== STEP 1: SELECT SERVICE =====

    if st.session_state.modal_booking_step == 1:

        st.markdown('<h3 class="modal-section-title">Elige tu servicio</h3>', unsafe_allow_html=True)


        for servicio_name, datos in servicios.items():

            is_selected = st.session_state.modal_booking_data.get("servicio") == servicio_name

            selected_class = "selected" if is_selected else ""


            card_html = f"""

            <div class="modal-service-card {selected_class}">

                <div style="font-weight: 600; margin-bottom: 4px;">{servicio_name}</div>

                <div style="font-size: 13px; color: #666;">{datos['duracion']} min · ${datos['precio']:,}</div>

            </div>

            """

            st.markdown(card_html, unsafe_allow_html=True)


            if st.button(f"Seleccionar {servicio_name}", key=f"modal_service_{servicio_name}", use_container_width=True):

                st.session_state.modal_booking_data["servicio"] = servicio_name

                st.session_state.modal_booking_data["duracion"] = datos["duracion"]

                st.session_state.modal_booking_data["precio"] = datos["precio"]

                st.session_state.modal_booking_step = 2

                st.rerun()


    # ===== STEP 2: SELECT DATE & TIME =====

    elif st.session_state.modal_booking_step == 2:

        st.markdown('<h3 class="modal-section-title">Fecha y hora</h3>', unsafe_allow_html=True)


        # Show selected service

        if st.session_state.modal_booking_data.get("servicio"):

            servicio = st.session_state.modal_booking_data["servicio"]

            precio = st.session_state.modal_booking_data.get("precio", 0)

            st.info(f"Servicio {servicio} - ${precio:,}")


        # Date picker

        fecha = st.date_input(

            "Fecha",

            value=st.session_state.modal_selected_fecha,

            min_value=datetime.now().date(),

            max_value=datetime.now().date() + timedelta(days=30),

            key="modal_booking_fecha",

            label_visibility="collapsed"

        )

        st.session_state.modal_selected_fecha = fecha


        # Time picker

        hora = st.time_input(

            "ð Hora",

            value=datetime.now().replace(hour=10, minute=0),

            key="modal_booking_hora",

            label_visibility="collapsed"

        )


        # Store selections

        st.session_state.modal_booking_data["fecha"] = str(fecha)

        st.session_state.modal_booking_data["hora"] = str(hora)


        # Navigation buttons

        col_back, col_next = st.columns(2)

        with col_back:

            if st.button("Atrás", key="modal_back_step2", use_container_width=True):

                st.session_state.modal_booking_step = 1

                st.rerun()

        with col_next:

            if st.button("Siguiente", key="modal_next_step2", use_container_width=True):

                st.session_state.modal_booking_step = 3

                st.rerun()


    # ===== STEP 3: ENTER DETAILS =====

    elif st.session_state.modal_booking_step == 3:

        st.markdown('<h3 class="modal-section-title">Tu información</h3>', unsafe_allow_html=True)


        # Show booking summary

        booking_summary = f"""

        <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 16px; font-size: 13px;">

        Servicio: <strong>{st.session_state.modal_booking_data.get('servicio', 'N/A')}</strong><br>

        Fecha y hora: <strong>{st.session_state.modal_booking_data.get('fecha', 'N/A')}</strong> @ <strong>{st.session_state.modal_booking_data.get('hora', 'N/A')}</strong>

        </div>

        """

        st.markdown(booking_summary, unsafe_allow_html=True)


        # Form fields

        nombre = st.text_input("Nombre", placeholder="Tu nombre completo", key="modal_nombre", label_visibility="collapsed")

        telefono = st.text_input("Teléfono", placeholder="Tu número de teléfono", key="modal_telefono", label_visibility="collapsed")

        email = st.text_input("Email (opcional)", placeholder="tu@email.com", key="modal_email", label_visibility="collapsed")


        st.session_state.modal_booking_data["nombre"] = nombre

        st.session_state.modal_booking_data["telefono"] = telefono

        st.session_state.modal_booking_data["email"] = email


        # Validation

        is_valid = nombre.strip() and telefono.strip()


        # Navigation buttons

        col_back, col_confirm = st.columns(2)

        with col_back:

            if st.button("Atrás", key="modal_back_step3", use_container_width=True):

                st.session_state.modal_booking_step = 2

                st.rerun()

        with col_confirm:

            if st.button("Confirmar reserva", key="modal_confirm_booking", use_container_width=True, disabled=not is_valid):

                # Save booking to database

                try:

                    reserva_id = execute_write(

                        """INSERT INTO reservas 

                        (barberia_id, cliente, telefono, email, servicio, fecha, hora, estado, pagado)

                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)

                        RETURNING id""",

                        (

                            barberia_id,

                            nombre,

                            telefono,

                            email or None,

                            st.session_state.modal_booking_data.get("servicio"),

                            st.session_state.modal_booking_data.get("fecha"),

                            st.session_state.modal_booking_data.get("hora"),

                            "confirmada",

                            False

                        ),

                        fetch_one_result=True

                    )


                    if reserva_id:

                        st.success(f"¡Reserva confirmada! ID: {reserva_id}")

                        st.session_state.modal_booking_open = False

                        st.session_state.modal_booking_step = 1

                        st.session_state.modal_booking_data = {}

                        st.balloons()

                        st.rerun()

                    else:

                        st.error("Error al guardar la reserva. Intenta de nuevo.")

                except Exception as e:

                    logger.exception("Error saving booking from modal")

                    st.error(f"Error: {str(e)}")


    st.markdown('</div></div>', unsafe_allow_html=True)

def obtener_todas_barberias(ciudad=None, servicio=None):

    """Fetch all public barberias with optional filters."""

    try:

        query = "SELECT id, nombre, slug, telefono, email, ciudad, direccion, latitud, longitud, color_primario, logo_url, hora_apertura, hora_cierre, estado FROM barberias WHERE estado = %s"

        params = ["active"]


        if ciudad and ciudad.strip():

            query += " AND LOWER(ciudad) LIKE LOWER(%s)"

            params.append(f"%{ciudad.strip()}%")


        # TODO: Implement servicio filter by joining with servicios table

        # if servicio and servicio.strip():

        #     query += " AND id IN (SELECT DISTINCT barberia_id FROM servicios WHERE LOWER(nombre) LIKE LOWER(%s))"

        #     params.append(f"%{servicio.strip()}%")


        query += " ORDER BY nombre ASC"


        results = fetch_all(query, tuple(params))

        barberias_list = []

        for row in results:

            barberias_list.append({

                "id": row[0],

                "nombre": row[1],

                "slug": row[2],

                "telefono": row[3],

                "email": row[4],

                "ciudad": row[5],

                "direccion": row[6],

                "latitud": float(row[7]) if row[7] else None,

                "longitud": float(row[8]) if row[8] else None,

                "color_primario": row[9],

                "logo_url": row[10],

                "hora_apertura": row[11],

                "hora_cierre": row[12],

                "estado": row[13],

            })

        return barberias_list

    except Exception as e:

        logger.exception(f"Error fetching barberias: {e}")

        return []

def render_barberia_card(barberia, index):

    """Render a marketplace card for a single barberia."""

    card_id = f"barberia_card_{index}"


    # Card styling

    st.markdown(f"""

    <style>

        .barberia-card-{index} {{

            background: white;

            border: 1px solid #e0e0e0;

            border-radius: 12px;

            padding: 16px;

            margin-bottom: 12px;

            transition: all 0.3s ease;

            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

        }}


        .barberia-card-{index}:hover {{

            transform: translateY(-4px);

            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);

            border-color: #667eea;

        }}


        .card-header-{index} {{

            display: flex;

            justify-content: space-between;

            align-items: start;

            margin-bottom: 12px;

        }}


        .card-title-{index} {{

            font-size: 18px;

            font-weight: 600;

            color: #1a1a1a;

            margin: 0;

        }}


        .card-rating-{index} {{

            background: #ffd700;

            color: #333;

            padding: 4px 8px;

            border-radius: 4px;

            font-size: 14px;

            font-weight: 600;

        }}


        .card-meta-{index} {{

            color: #666;

            font-size: 14px;

            margin: 8px 0;

            line-height: 1.5;

        }}


        .card-address-{index} {{

            display: flex;

            align-items: center;

            gap: 8px;

            color: #555;

            font-size: 13px;

            margin: 10px 0;

        }}


        .card-button-{index} {{

            width: 100%;

            padding: 10px;

            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

            color: white;

            border: none;

            border-radius: 8px;

            font-weight: 600;

            cursor: pointer;

            margin-top: 12px;

            transition: all 0.3s ease;

        }}


        .card-button-{index}:hover {{

            transform: scale(1.02);

            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);

        }}

    </style>

    """, unsafe_allow_html=True)


    # Card HTML - with rating stars (placeholder for future integration)

    rating_stars = "­" * min(5, max(1, 4))  # Placeholder: 4 stars


    card_html = f"""

    <div class="barberia-card-{index}">

        <div class="card-header-{index}">

            <h3 class="card-title-{index}">{barberia['nombre']}</h3>

            <span class="card-rating-{index}">{rating_stars} 4.5</span>

        </div>

        <div class="card-meta-{index}">

            Teléfono: {barberia.get('telefono', 'N/A')}

        </div>

        <div class="card-address-{index}">

            Dirección: {barberia.get('direccion', 'Dirección no disponible')}

        </div>

        <div class="card-meta-{index}">

            Ciudad: {barberia.get('ciudad', 'N/A')}

        </div>

        <div class="card-meta-{index}">

            Horario {barberia.get('hora_apertura', '--:--')} - {barberia.get('hora_cierre', '--:--')}

        </div>

    """


    st.markdown(card_html, unsafe_allow_html=True)


    # Agendar button - opens modal instead of navigating

    if st.button(

        "Agendar cita",

        key=f"btn_agendar_{index}_{barberia['id']}",

        use_container_width=True

    ):

        st.session_state.modal_booking_selected_barberia = barberia

        st.session_state.modal_booking_open = True

        st.session_state.modal_booking_step = 1

        st.session_state.modal_booking_data = {}

        st.rerun()

def render_marketplace_results(servicio_busqueda="", ubicacion_busqueda=""):

    """Render marketplace results with split screen: list (60%) + map (40%)."""

    st.markdown("---")


    # Filters Row

    col_filters = st.columns([1, 1, 1])

    with col_filters[0]:

        servicio_filter = st.text_input("Filtrar por servicio", value=servicio_busqueda, label_visibility="collapsed", placeholder="Ej: Corte")


    with col_filters[1]:

        ubicacion_filter = st.text_input("Filtrar por ciudad", value=ubicacion_busqueda, label_visibility="collapsed", placeholder="Tu ciudad")


    with col_filters[2]:

        aplicar_filtros = st.button("Actualizar", use_container_width=True, key="btn_filtros_update")


    # Fetch results

    barberias = obtener_todas_barberias(

        ciudad=ubicacion_filter or ubicacion_busqueda,

        servicio=servicio_filter or servicio_busqueda

    )


    if not barberias:

        st.warning("No se encontraron barberías que coincidan con tu búsqueda. Intenta con otros filtros.")

        return


    # Split screen: 60% list, 40% map

    col_left, col_right = st.columns([0.6, 0.4], gap="large")


    # ===== LEFT SIDE: BARBER SHOP LIST =====

    with col_left:

        st.markdown(f"### Resultados ({len(barberias)} barberías)")

        st.markdown("")


        for idx, barberia in enumerate(barberias):

            render_barberia_card(barberia, idx)


    # ===== RIGHT SIDE: MAP =====

    with col_right:

        st.markdown("### Mapa")

        st.markdown("")


        # Prepare map data (Streamlit's st.map expects lat/lon in dataframe)

        if any(b.get("latitud") and b.get("longitud") for b in barberias):

            map_data = []

            for barberia in barberias:

                if barberia.get("latitud") and barberia.get("longitud"):

                    map_data.append({

                        "lat": barberia["latitud"],

                        "lon": barberia["longitud"],

                        "nombre": barberia["nombre"],

                        "direccion": barberia.get("direccion", ""),

                    })


            if map_data:

                map_df = pd.DataFrame(map_data)


                # Rename columns to match st.map() requirements (latitude, longitude)

                map_df.rename(columns={"lat": "latitude", "lon": "longitude"}, inplace=True)


                # Display map

                st.map(map_df, zoom=12, use_container_width=True)

            else:

                st.info("Las barberías aún no tienen ubicaciones geocodificadas.")

        else:

            st.info("Las barberías aún no tienen ubicaciones geocodificadas.")


    # ===== MODAL BOOKING OVERLAY =====

    if st.session_state.get("modal_booking_open") and st.session_state.get("modal_booking_selected_barberia"):

        barberia = st.session_state.modal_booking_selected_barberia

        render_modal_booking(barberia)

def render_home_screen():

    """Render the home screen with marketplace hero section and 3 main options."""

    st.set_page_config(

        page_title="Barbería Leveling",

        page_icon="Barberia",

        layout="wide",

        initial_sidebar_state="collapsed"

    )


    # ===== MARKETPLACE HERO SECTION =====

    search_clicked, servicio, ubicacion = render_hero_marketplace()


    # If search button was clicked, handle the search

    if search_clicked:

        if servicio or ubicacion:

            # Show marketplace results with split screen

            render_marketplace_results(servicio_busqueda=servicio, ubicacion_busqueda=ubicacion)

        else:

            st.warning("Por favor, completa al menos un campo de búsqueda")

        return  # Don't show main options if showing results


    # ===== MAIN OPTIONS SECTION =====

    st.markdown("---")

    st.markdown("")


    col_center = st.columns([1, 2, 1])

    with col_center[1]:

        st.markdown("<h2 style='text-align: center;'>¿Qué deseas hacer?</h2>", unsafe_allow_html=True)

        st.markdown("")


        col1, col2, col3 = st.columns(3, gap="large")


        # CUSTOM CSS FOR PREMIUM CARD BUTTONS

        st.markdown("""

        <style>

        /* Base button styling for all card buttons */

        div.stButton > button {

            min-height: 120px !important;

            border-radius: 16px !important;

            font-size: 15px !important;

            font-weight: 600 !important;

            border: 1px solid rgba(197,159,85,0.22) !important;

            transition: all 0.3s ease !important;

            white-space: pre-line !important;

            line-height: 1.5 !important;

            padding: 1.25rem 1rem !important;

            display: flex !important;

            align-items: center !important;

            justify-content: center !important;

            flex-direction: column !important;

            text-align: center !important;

            color: #f5f0e8 !important;

            cursor: pointer !important;

            background: #141414 !important;

        }


        /* Hover effects - scale and gold glow */

        div.stButton > button:hover {

            border-color: #c5a028 !important;

            background: #1e1a0e !important;

            box-shadow: 0 12px 28px rgba(197,160,40,0.25) !important;

        }


        /* Login card */

        div.stButton:nth-of-type(1) > button {

            box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;

        }


        /* Register card */

        div.stButton:nth-of-type(2) > button {

            box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;

        }


        /* Booking card */

        div.stButton:nth-of-type(3) > button {

            box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;

        }

        </style>

        """, unsafe_allow_html=True)


        with col1:

            if st.button("Iniciar sesión\n\nAccede a tu cuenta", key="home_login", use_container_width=True):

                st.session_state.view = "login"

                st.rerun()


        with col2:

            if st.button("Registrar barbería\n\nCrea tu espacio", key="home_registro", use_container_width=True):

                st.session_state.view = "registro"

                st.rerun()


        with col3:

            if st.button("Reservar cita\n\nAgenda tu corte", key="home_reserva", use_container_width=True):

                st.session_state.view = "reserva"

                st.rerun()

def render_landing_publico(barberia):

    """Render authentic barberia landing page with barber-focused experience."""

    apply_public_booking_css()

    barberia_id = barberia["id"]

    barberia_name = barberia.get("nombre", "Barbería")


    # Initialize landing state - use barberia-specific key

    landing_key = f"show_landing_barberia_{barberia_id}"

    if landing_key not in st.session_state:

        st.session_state[landing_key] = True


    # Initialize pre-selected service (for clicking on cards)

    if "preselected_service" not in st.session_state:

        st.session_state.preselected_service = None


    # Load services from database

    servicios_list = obtener_servicios(barberia_id)


    col_back, _ = st.columns([1, 6], gap="small")

    with col_back:

        if st.button("Volver", key="back_landing", help="Volver al inicio", use_container_width=True):

            st.session_state.view = "home"

            st.session_state[landing_key] = True

            st.session_state.preselected_service = None

            st.rerun()


    render_public_landing_hero(barberia)

    st.markdown("""
    <div class="public-trust-grid">
        <div class="public-trust-card">
            <h3>Reserva en segundos</h3>
            <p>Elige servicio, barbero y horario desde tu teléfono.</p>
        </div>
        <div class="public-trust-card">
            <h3>Confirmación inmediata</h3>
            <p>Recibe el detalle de tu cita y mantén tu hora organizada.</p>
        </div>
        <div class="public-trust-card">
            <h3>Atención profesional</h3>
            <p>Una experiencia clara, rápida y confiable de principio a fin.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # Services Section - Interactive & Barber-Focused

    if servicios_list:

        render_public_section_heading(
            "Elige tu servicio",
            "Selecciona una categoría y continúa con tu barbero y horario.",
        )


        # Display services in responsive grid - CLICKABLE

        num_services = len(servicios_list)

        if num_services == 1:

            cols = st.columns(1)

            cols_list = [cols]

        elif num_services == 2:

            cols = st.columns(2, gap="large")

            cols_list = cols

        else:

            cols = st.columns(min(3, num_services), gap="large")

            cols_list = cols


        for idx, servicio in enumerate(servicios_list):

            col = cols_list[idx % len(cols_list)] if isinstance(cols_list[0], object) else cols_list[idx]


            with col:

                # Format price with thousand separator

                precio_formateado = f"${servicio['precio']:,}".replace(",", ".")


                # Clickable service button - looks like card, acts like button

                button_clicked = st.button(

                    label=f"{servicio.get('icono') or 'Servicio'}  {servicio['nombre']}\n\n{servicio.get('descripcion', '')}\n\n{servicio['duracion']} min · {precio_formateado}",

                    key=f"service_card_{servicio['id']}",

                    use_container_width=True,

                    help=f"Seleccionar {servicio['nombre']}"

                )

                if button_clicked:

                    st.session_state.preselected_service = {

                        "nombre": servicio["nombre"],

                        "duracion": servicio["duracion"],

                        "precio": servicio["precio"],

                    }

                    st.session_state[landing_key] = False

                    st.session_state.booking_step = 2  # Skip to barber selection

                    st.rerun()

    else:

        st.info("Los servicios se mostrarán aquí una vez configurados")


    render_public_section_heading(
        "Agenda tu próxima cita",
        "También puedes comenzar sin elegir servicio y decidir en el primer paso.",
    )


    col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 2, 1])

    with col_btn_2:

        st.markdown('<div class="public-cta">', unsafe_allow_html=True)

        cta_clicked = st.button(

            "Agendar mi cita",

            key="barberia_cta_button",

            use_container_width=True,

            help="Comienza tu reserva ahora",

        )

        st.markdown('</div>', unsafe_allow_html=True)


        if cta_clicked:

            st.session_state[landing_key] = False

            st.session_state.booking_step = 1  # Go to service selection

            st.rerun()


    st.caption("Barbería profesional · Barberos expertos · Reserva online")

def render_booking_publico(barberia_slug):

    """Render public booking interface for a specific barberia."""

    # Load barberia from slug

    barberia = obtener_barberia_por_slug(barberia_slug)

    if not barberia:

        st.error("Barbería no encontrada")

        st.stop()

        return


    barberia_id = barberia["id"]


    # Set page config

    st.set_page_config(

        page_title=f"Reserva en {barberia['nombre']}",

        page_icon="Barberia",

        layout="wide",

        initial_sidebar_state="collapsed"

    )


    # Store barberia context in session state temporarily

    st.session_state.barberia_id = barberia_id

    st.session_state.public_mode = True


    # Initialize landing page state - use barberia-specific key

    landing_key = f"show_landing_barberia_{barberia_id}"

    if landing_key not in st.session_state:

        st.session_state[landing_key] = True


    # Show landing page or booking flow

    if st.session_state.get(landing_key, True):

        render_landing_publico(barberia)

        # Don't show booking flow when landing page is visible

        return


    # Run the existing public booking flow (only shown after user clicks CTA)

    flujo_reserva_publica()

# ================= BOOKING WITHOUT LOGIN =================

# ------------------ LOGIN ------------------

try:

    if "user" not in st.session_state:

        st.session_state.user = None

    if "rol" not in st.session_state:

        st.session_state.rol = "CLIENTE"

    if "barberia_id" not in st.session_state:

        st.session_state.barberia_id = default_barberia_id

    if "barberia_context_id" not in st.session_state:

        st.session_state.barberia_context_id = default_barberia_id

    if "super_admin_all_barberias" not in st.session_state:

        st.session_state.super_admin_all_barberias = False

    if "reserva_seleccionada_id" not in st.session_state:

        st.session_state.reserva_seleccionada_id = None

    if "mostrar_detalles_reserva" not in st.session_state:

        st.session_state.mostrar_detalles_reserva = False

    if "view" not in st.session_state:

        st.session_state.view = "home"

    if "public_mode" not in st.session_state:

        st.session_state.public_mode = False

    st.session_state["db_available"] = is_db_available()

    db_ok = st.session_state["db_available"]

    render_modo_sin_db_banner()

    # ===== URL ROUTING =====

    # Check if accessing public booking via URL parameter

    barberia_slug = st.query_params.get("barberia")


    if barberia_slug:

        # Public booking mode - show booking interface directly

        render_booking_publico(barberia_slug)

        st.stop()

    else:

        # Reset barberia_id to default when no slug (to prevent carryover from previous public booking)

        st.session_state.barberia_id = default_barberia_id


    # ===== LOGIN SCREEN =====

    # Initialize view state if not set

    if "view" not in st.session_state:

        st.session_state.view = "home"


    # If user is already logged in, skip auth screens and go to main app

    if st.session_state.get("user") and st.session_state.view in ["home", "login", "registro", "reserva"]:

        st.session_state.view = st.session_state.get("view", "dashboard")

        # Force navigation to appropriate dashboard

        if st.session_state.get("user_role") == "SUPER_ADMIN":

            st.session_state.view = "dashboard_admin"

        elif st.session_state.get("user_role") == "BARBERO":

            st.session_state.view = "dashboard_barbero"

        else:

            st.session_state.view = "dashboard"


    # Route based on view state

    if st.session_state.view == "home":

        render_home_screen()


    elif st.session_state.view == "login":

        # Show login form

        st.markdown("""<style>
.stApp { background: #080808 !important; }
section[data-testid="stSidebar"] { display: none !important; }
div[data-testid="stForm"] { background: #141414 !important; border: 1px solid rgba(197,159,85,0.25) !important; border-radius: 12px !important; padding: 24px !important; }
div[data-testid="stTextInput"] input { background: #1a1a1a !important; color: #f5f0e8 !important; border: 1px solid rgba(197,159,85,0.3) !important; border-radius: 8px !important; }
div[data-testid="stTextInput"] label { color: #c5a028 !important; }
div[data-testid="stForm"] button[kind="primaryFormSubmit"] { background: linear-gradient(135deg, #c5a028 0%, #8a6e17 100%) !important; color: #080808 !important; font-weight: 700 !important; border: none !important; border-radius: 8px !important; }
h3 { color: #f5f0e8 !important; }
</style>""", unsafe_allow_html=True)

        col_center = st.columns([1, 2, 1])

        with col_center[1]:

            if st.button("Volver al inicio", key="back_to_home"):

                st.session_state.view = "home"

                st.rerun()

            st.markdown("### Accede a tu cuenta")

            with st.form("login_form"):

                usuario = st.text_input("Usuario", placeholder="Tu usuario")

                password = st.text_input("Contraseña", type="password", placeholder="Tu contraseña")

                entrar = st.form_submit_button("Entrar", use_container_width=True, disabled=not db_ok)

            if entrar:

                try:

                    with st.spinner("Verificando credenciales..."):

                        user = login(usuario, password)

                        if user:

                            st.session_state.user = user

                            st.session_state.user_id = user[0]

                            raw_rol = user[3] if len(user) > 3 else None

                            st.session_state.rol = normalizar_rol(raw_rol)

                            st.session_state.user_role = st.session_state.rol

                            nr_login = st.session_state.rol

                            if nr_login == "SUPER_ADMIN":

                                st.session_state.barberia_id = None

                                with st.spinner("Cargando barberías..."):

                                    fb = fetch_one("SELECT id FROM barberias ORDER BY id LIMIT 1")

                                st.session_state.barberia_context_id = fb[0] if fb else None

                                st.session_state.super_admin_all_barberias = False

                                st.session_state.view = "dashboard_admin"

                            elif nr_login == "BARBERO":

                                bid_u = user[5] if len(user) > 5 else None

                                st.session_state.barberia_id = bid_u or default_barberia_id

                                st.session_state.barberia_context_id = st.session_state.barberia_id

                                st.session_state.view = "dashboard_barbero"

                            else:

                                bid_u = user[5] if len(user) > 5 else None

                                st.session_state.barberia_id = bid_u or default_barberia_id

                                st.session_state.barberia_context_id = st.session_state.barberia_id

                                st.session_state.view = "dashboard"

                            st.success("¡Bienvenido!")

                            st.rerun()

                        else:

                            st.error("[ERROR] Datos incorrectos. Intenta nuevamente.")

                except Exception as e:

                    logger.exception("Error en login")

                    st.error(f"Error en login: {str(e)}")


    elif st.session_state.view == "registro":

        # Show professional barber registration flow

        render_registro_barberia()


    elif st.session_state.view == "reserva":

        # Show public booking

        st.set_page_config(layout="wide")

        col_center = st.columns([1, 2, 1])

        with col_center[1]:

            if st.button("Volver al inicio", key="back_to_home_res"):

                st.session_state.view = "home"

                st.rerun()

            flujo_reserva_publica()


    elif st.session_state.view in ["dashboard_admin", "dashboard_barbero", "dashboard"]:

        # User is logged in, proceed to main app

        pass


    else:

        # Default to home if view is unknown

        st.session_state.view = "home"

        st.rerun()


    # If user is logged in and has a valid dashboard view, proceed to main app

    # Otherwise, if user is logged in but no valid view, redirect to dashboard

    if st.session_state.get("user") and st.session_state.view not in ["home", "login", "registro", "reserva"]:

        # Proceed to main app (don't stop here)

        pass

    elif st.session_state.get("user") and st.session_state.view in ["home", "login", "registro", "reserva"]:

        # User logged in but on public view - redirect

        if st.session_state.get("user_role") == "SUPER_ADMIN":

            st.session_state.view = "dashboard_admin"

        elif st.session_state.get("user_role") == "BARBERO":

            st.session_state.view = "dashboard_barbero"

        else:

            st.session_state.view = "dashboard"

        st.rerun()

    elif not st.session_state.get("user"):

        # User not logged in, stop here

        st.stop()

    # ===== MAIN APP (Only runs if logged in) =====

    apply_internal_panel_css()

    user = st.session_state.get("user")

    usuario = user[1] if user and len(user) > 1 else None

    # Always use normalized role from session state

    nr = st.session_state.get("rol", "CLIENTE")

    if not nr:

        st.session_state.rol = "CLIENTE"

        nr = "CLIENTE"

    barberia_id = st.session_state.get("barberia_id")

    bid_ctx = effective_barberia_id()

    if not db_ok:

        st.warning(

            "La base de datos no está disponible. Estás en modo demo: la interfaz se muestra, "

            "pero no se pueden crear ni modificar reservas ni consultar datos en vivo."

        )

    # ===== SIDEBAR =====

    with st.sidebar:

        st.markdown("## Barbería Leveling")

        st.markdown(f"**{usuario or 'Invitado'}**")

        st.caption(f"Rol: {nr.replace('_', ' ')}")

        barberia_name = "Principal"

        if barberia_id:

            if "barberia_name" not in st.session_state or st.session_state.get("cached_barberia_id") != barberia_id:

                with st.spinner("Cargando barbería..."):

                    b_name_row = fetch_one("SELECT nombre FROM barberias WHERE id = %s", (barberia_id,))

                st.session_state.barberia_name = b_name_row[0] if b_name_row else "Principal"

                st.session_state.cached_barberia_id = barberia_id

            barberia_name = st.session_state.barberia_name

        st.markdown(f"**Barbería:** {barberia_name}")

        st.markdown("---")

        if nr == "SUPER_ADMIN":

            st.markdown("### Contexto")

            try:

                if "barberias_list" not in st.session_state:

                    with st.spinner("Cargando barberías..."):

                        b_list = fetch_all("SELECT id, nombre FROM barberias ORDER BY nombre") or []

                    st.session_state.barberias_list = b_list

                else:

                    b_list = st.session_state.barberias_list


                if b_list and len(b_list) > 0:

                    etiquetas = {f"{r[1]}": r[0] for r in b_list}

                    claves = list(etiquetas.keys())


                    # Ensure valid index

                    idx = 0

                    if st.session_state.barberia_context_id is not None:

                        barberia_ids = list(etiquetas.values())

                        if st.session_state.barberia_context_id in barberia_ids:

                            idx = barberia_ids.index(st.session_state.barberia_context_id)

                        else:

                            idx = 0 if len(barberia_ids) > 0 else 0


                    # Ensure index is within bounds

                    idx = min(idx, len(claves) - 1) if claves else 0


                    if len(claves) > 0:

                        sel_lab = st.selectbox("Barbería activa", claves, index=idx, key="super_sel_barb")

                        st.session_state.barberia_context_id = etiquetas[sel_lab]

                    else:

                        st.warning("No hay barberías disponibles")

                else:

                    st.warning("No hay barberías registradas en el sistema")

                    st.session_state.barberia_context_id = None

            except Exception as e:

                logger.exception("Error loading barberia context for SUPER_ADMIN")

                st.error(f"Error cargando contexto de barbería: {str(e)}")

                st.session_state.barberia_context_id = None


            try:

                st.session_state.super_admin_all_barberias = st.checkbox(

                    "Ver todas las barberías",

                    value=st.session_state.get("super_admin_all_barberias", False),

                    key="chk_super_all",

                )

            except Exception as e:

                logger.exception("Error in SUPER_ADMIN checkbox")

                st.session_state.super_admin_all_barberias = False


            st.markdown("---")


        # ===== DEBUG: VERIFY BARBERIA_ID ISOLATION =====

        st.markdown("### Navegación")

        nav_opts = ["Dashboard", "Agenda", "Barberos", "Configuración"]

        if nr in ("ADMIN", "SUPER_ADMIN"):

            nav_opts = [
                "Dashboard",
                "Agenda",
                "Barberos",
                "Servicios",
                "Clientes",
                "Sitio Web",
                "Complementos",
                "Configuración",
            ]

        elif nr == "BARBERO":

            nav_opts = ["Dashboard", "Agenda", "Configuración"]

        if nr == "CLIENTE":

            nav_opts = ["Dashboard", "Agenda"]

        nav_labels = {
            "Dashboard": "Visión general",
            "Agenda": "Agenda y calendario",
            "Barberos": "Equipo",
            "Servicios": "Servicios",
            "Clientes": "Clientes",
            "Sitio Web": "Sitio Web",
            "Complementos": "Complementos",
            "Configuración": "Configuración",
        }

        nav_key = f"nav_main_{nr}"

        if st.session_state.get(nav_key) not in nav_opts:

            st.session_state[nav_key] = nav_opts[0]

        seccion = st.radio(
            "Navegación principal",
            nav_opts,
            key=nav_key,
            label_visibility="collapsed",
            format_func=lambda item: nav_labels.get(item, item),
        )

        st.markdown("---")

        if st.button("Cerrar sesión", use_container_width=True, type="secondary"):

            st.session_state.user = None

            st.session_state.barberia_id = None

            st.session_state.barberia_context_id = None

            st.rerun()

    def render_equipo_barberos(barberia_id):

        """Render barber team as cards with create and delete actions."""

        if not db_ok or not barberia_id:

            render_alert("Gestión de equipo no disponible sin base de datos", alert_type="info")

            return

        # --- Card CSS ---

        st.markdown("""<style>
.barbero-card {
    background: #1a1a1a;
    border: 1px solid rgba(197,159,85,0.2);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.barbero-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #c5a028, #8a6e17);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 700;
    color: #080808;
    flex-shrink: 0;
    text-transform: uppercase;
}
.barbero-info { flex: 1; }
.barbero-nombre { font-size: 17px; font-weight: 600; color: #f5f0e8; margin: 0; }
.barbero-rol { font-size: 13px; color: rgba(197,159,85,0.8); margin: 2px 0 0 0; }
</style>""", unsafe_allow_html=True)

        # --- Create new barber form ---

        render_subsection_title("Agregar barbero")

        with st.form("form_crear_barbero_equipo", clear_on_submit=True):

            col_u, col_p = st.columns(2)

            with col_u:

                nuevo_usuario = st.text_input("Nombre de usuario", placeholder="Ej: carlos")

            with col_p:

                nueva_password = st.text_input("Contraseña", type="password")

            crear_btn = st.form_submit_button("Agregar al equipo", use_container_width=True, type="primary")

        if crear_btn:

            if not nuevo_usuario or not nuevo_usuario.strip():

                st.error("El nombre de usuario es obligatorio.")

            elif not nueva_password or len(nueva_password) < 4:

                st.error("La contraseña debe tener al menos 4 caracteres.")

            else:

                ok = registrar(nuevo_usuario.strip(), nueva_password, "BARBERO", barberia_id=barberia_id)

                if ok:

                    st.success(f"Barbero '{nuevo_usuario}' añadido al equipo.")

                    st.rerun()

        render_divider()

        # --- Barber cards ---

        render_subsection_title("Equipo registrado")

        with st.spinner("Cargando equipo..."):

            barberos_data = listar_usuarios_barberos(barberia_id)

        if not barberos_data:

            render_panel_empty_state(

                "Sin barberos aún",

                "Usa el formulario de arriba para añadir el primer barbero al equipo.",

            )

            return

        for row in barberos_data:

            bid_barber, bname = row[0], row[1]

            inicial = bname[0].upper() if bname else "B"

            st.markdown(

                f'<div class="barbero-card">'

                f'<div class="barbero-avatar">{inicial}</div>'

                f'<div class="barbero-info">'

                f'<p class="barbero-nombre">{bname}</p>'

                f'<p class="barbero-rol">Barbero</p>'

                f'</div></div>',

                unsafe_allow_html=True,

            )

            col_space, col_del = st.columns([4, 1])

            with col_del:

                if st.button("Eliminar", key=f"del_barbero_{bid_barber}", type="secondary", use_container_width=True):

                    try:

                        execute_write(

                            "DELETE FROM usuarios WHERE id = %s AND barberia_id = %s AND UPPER(TRIM(rol)) = 'BARBERO'",

                            (int(bid_barber), int(barberia_id)),

                        )

                        st.success(f"Barbero '{bname}' eliminado.")

                        st.rerun()

                    except Exception as _e:

                        logger.exception(f"Error eliminando barbero {bid_barber}")

                        st.error("Error al eliminar el barbero.")

    def render_gestion_servicios(barberia_id):

        """Render CRUD UI for services management in admin/super_admin panels."""

        if not db_ok or not barberia_id:

            render_alert("Gestión de servicios no disponible sin base de datos", alert_type="info")

            return

        # --- Load current services ---

        servicios_actuales = safe_fetch_all(

            "SELECT id, nombre, duracion_minutos, precio, descripcion, icono FROM servicios WHERE barberia_id = %s ORDER BY id ASC",

            (barberia_id,),

        )

        # --- Add new service form ---

        render_subsection_title("Agregar servicio")

        with st.form("form_crear_servicio", clear_on_submit=True):

            col_n, col_d, col_p = st.columns([3, 2, 2])

            with col_n:

                nuevo_nombre = st.text_input("Nombre del servicio", max_chars=80)

            with col_d:

                nueva_duracion = st.number_input("Duración (min)", min_value=5, max_value=480, value=30, step=5)

            with col_p:

                nuevo_precio = st.number_input("Precio ($)", min_value=0, max_value=999999, value=0, step=100)

            nueva_descripcion = st.text_input("Descripción (opcional)", max_chars=200)

            nuevo_icono = st.text_input("Icono / etiqueta (opcional)", value="Servicio", max_chars=40)

            guardar = st.form_submit_button("Agregar servicio", use_container_width=True, type="primary")

        if guardar:

            if not nuevo_nombre or not nuevo_nombre.strip():

                st.error("El nombre del servicio es obligatorio.")

            else:

                ok = crear_servicio(barberia_id, nuevo_nombre, nueva_duracion, nuevo_precio, nueva_descripcion or "", nuevo_icono or "Servicio")

                if ok:

                    st.success(f"Servicio '{nuevo_nombre}' creado correctamente.")

                    st.rerun()

                else:

                    st.error("Error al crear el servicio. Verifica que el nombre no esté duplicado.")

        render_divider()

        # --- List + edit/delete ---

        render_subsection_title("Servicios registrados")

        if not servicios_actuales:

            render_panel_empty_state(

                "Sin servicios aún",

                "Agrega un servicio con el formulario de arriba y aparecerá aquí y en el flujo de reservas.",

            )

            return

        for row in servicios_actuales:

            sid, snombre, sduracion, sprecio, sdesc, sicono = row

            with st.expander(f"{sicono or 'Servicio'} — {snombre} | {sduracion} min | ${sprecio}", expanded=False):

                with st.form(f"form_editar_{sid}", clear_on_submit=False):

                    col_en, col_ed, col_ep = st.columns([3, 2, 2])

                    with col_en:

                        edit_nombre = st.text_input("Nombre", value=snombre, max_chars=80, key=f"en_{sid}")

                    with col_ed:

                        edit_duracion = st.number_input("Duración (min)", min_value=5, max_value=480, value=int(sduracion or 30), step=5, key=f"ed_{sid}")

                    with col_ep:

                        edit_precio = st.number_input("Precio ($)", min_value=0, max_value=999999, value=int(sprecio or 0), step=100, key=f"ep_{sid}")

                    edit_desc = st.text_input("Descripción", value=sdesc or "", max_chars=200, key=f"edesc_{sid}")

                    edit_icono = st.text_input("Icono / etiqueta", value=sicono or "Servicio", max_chars=40, key=f"eico_{sid}")

                    col_save, col_del = st.columns(2)

                    with col_save:

                        update_btn = st.form_submit_button("Guardar cambios", use_container_width=True, type="primary")

                    with col_del:

                        delete_btn = st.form_submit_button("Eliminar servicio", use_container_width=True, type="secondary")

                if update_btn:

                    if not edit_nombre or not edit_nombre.strip():

                        st.error("El nombre no puede estar vacío.")

                    else:

                        ok = actualizar_servicio(sid, barberia_id, edit_nombre, edit_duracion, edit_precio, edit_desc or "", edit_icono or "Servicio")

                        if ok:

                            st.success("Servicio actualizado.")

                            st.rerun()

                        else:

                            st.error("Error al actualizar el servicio.")

                if delete_btn:

                    ok = eliminar_servicio(sid, barberia_id)

                    if ok:

                        st.success(f"Servicio '{snombre}' eliminado.")

                        st.rerun()

                    else:

                        st.error("Error al eliminar el servicio.")

    def _panel_ingresos(bid):

        if not db_ok or not bid:

            st.info("Métricas de ingresos no disponibles sin base de datos.")

            return

        total_row = fetch_one(

            "SELECT SUM(precio) FROM reservas WHERE barberia_id = %s",

            (bid,),

        )

        total = total_row[0] if total_row is not None else 0

        if total is None:

            total = 0

        st.metric("Total generado", f"${total if total else 0}")

    # ================= CLIENTE =================

    if nr == "CLIENTE":

        if not barberia_id:

            st.warning("No hay barberia asociada a la sesión.")

            st.stop()

        if seccion == "Dashboard":

            render_section_title("Mi panel", subtitle="Visualiza tus reservas y métricas")


            if not db_ok:

                render_alert("Métricas no disponibles sin base de datos", alert_type="info")

            else:

                with st.spinner("Cargando métricas..."):

                    total_hoy, pagadas_hoy, pendientes_hoy = calcular_metricas_header(barberia_id)

                    total_reservas, hoy_reservas, _ = calcular_metricas_cliente(barberia_id, usuario)

                    num_barberos_cached = len(listar_usuarios_barberos(barberia_id))


                # Dashboard metrics with new design system

                render_metric_grid([
                    ("Reservas Hoy", total_hoy, "Calendario", Colors.PRIMARY),
                    ("Pagadas", pagadas_hoy, "[OK]", Colors.SUCCESS),
                    ("Pendientes", pendientes_hoy, "Espera", Colors.WARNING),
                ], columns=3)


                render_divider()


                render_subsection_title("Resumen de actividad")

                render_metric_grid([
                    ("Total", total_reservas, "📊", Colors.SECONDARY),
                    ("Hoy", hoy_reservas, "📆", Colors.PRIMARY),
                    ("Ingresos", "$0", "Ingresos", Colors.SUCCESS),
                    ("Barberos", num_barberos_cached, "Tijeras", Colors.WARNING),
                ], columns=4)


                render_divider()


                render_subsection_title("Información útil")

                col_tip1, col_tip2 = st.columns(2, gap="large")

                with col_tip1:

                    render_alert("Obtén descuento cada 5 cortes", alert_type="success", title="Beneficio de fidelización")

                with col_tip2:

                    render_alert("Cancela con 1 hora de anticipación para evitar penalización", alert_type="info", title="Política de cancelación")

        elif seccion == "Agenda":

            render_section_title("Mi agenda", subtitle="Gestiona tus citas")

            tab_calendario, tab_crear, tab_lista = st.tabs([

                "Calendario",

                "Nueva reserva",

                "Listado"

            ])

            # TAB: CALENDARIO

            with tab_calendario:

                if db_ok:

                    with st.spinner("Cargando tu calendario..."):

                        mis_reservas_raw = listar_reservas_filtradas(barberia_id, "CLIENTE", usuario)

                        # Convertir a formato para calendario

                        mis_reservas_dict = []

                        for r in mis_reservas_raw:

                            fecha = r.get("fecha")

                            hora = r.get("hora")

                            if fecha and hora:

                                try:

                                    start_dt = datetime.combine(fecha, hora)

                                    end_dt = start_dt + timedelta(minutes=30)

                                    monto = r.get("monto") or r.get("precio") or 0

                                    pagado = bool(r.get("pagado", False))

                                    mis_reservas_dict.append((r.get("id"), r.get("cliente") or r.get("nombre"), r.get("barbero"), r.get("servicio"), monto, start_dt, end_dt, pagado))

                                except (TypeError, ValueError):

                                    continue


                        eventos_cliente = construir_eventos_calendario(mis_reservas_dict)


                    if eventos_cliente:

                        render_agenda_interactiva(eventos_cliente, read_only=True)

                    else:

                        st.info("No tienes reservas aún. ¡Crea una!")

                else:

                    st.warning("Calendario no disponible sin base de datos.")

            # TAB: CREAR NUEVA

            with tab_crear:

                with st.container(border=True):

                    st.markdown("### Nueva reserva")

                    if not db_ok:

                        st.warning("No hay base de datos: no puedes crear reservas en modo demo.")

                    else:

                        with st.spinner("Cargando barberos disponibles..."):

                            barber_opts = [x[0] for x in listar_usuarios_barberos(barberia_id)] or list(barberos.keys())


                        # Initialize session state for barber selection

                        if "cliente_barbero_sel_premium" not in st.session_state:

                            st.session_state.cliente_barbero_sel_premium = None

                        if "cliente_barber_loading" not in st.session_state:

                            st.session_state.cliente_barber_loading = False


                        # Premium barber selection cards

                        st.markdown("#### Elige tu barbero")

                        barberos_list = [(name, name) for name in barber_opts]


                        cols = st.columns(min(3, len(barberos_list)))

                        barber_clicked = False

                        for idx, (barber_id, barber_name) in enumerate(barberos_list):

                            with cols[idx % len(cols)]:

                                is_selected = st.session_state.cliente_barbero_sel_premium == barber_name

                                if render_barber_card(

                                    barber_name=barber_name,

                                    barber_id=barber_id,

                                    availability="Disponible",

                                    icon="Tijeras",

                                    is_selected=is_selected

                                ):

                                    st.session_state.cliente_barbero_sel_premium = barber_name

                                    st.session_state.cliente_barber_loading = True

                                    barber_clicked = True


                        # Show loading animation if a barber was just clicked

                        if st.session_state.cliente_barber_loading and not barber_clicked:

                            render_loading_panel(
                                "Preparando formulario...",
                                icon="Espera",
                                padding="15px",
                                top_margin="10px",
                            )

                            import time

                            time.sleep(0.15)

                            st.session_state.cliente_barber_loading = False

                            st.rerun()

                        elif barber_clicked:

                            st.rerun()


                        # Only show form if barber is selected

                        if st.session_state.cliente_barbero_sel_premium:

                            render_divider(color=Colors.BORDER, height="2px", margin=Spacing.MD)


                            with st.form("form_reserva_cliente"):

                                st.markdown("#### Detalles de la reserva")


                                # Barber (pre-selected and read-only display)

                                st.caption(f"**Barbero:** {st.session_state.cliente_barbero_sel_premium}")


                                col2 = st.columns(1)[0]

                                with col2:

                                    servicio_sel = st.selectbox("Servicio", list(servicios.keys()), key="cliente_servicio_sel")


                                col3, col4 = st.columns(2)

                                with col3:

                                    fecha_sel = st.date_input("Fecha", key="cliente_fecha_sel")

                                with col4:

                                    hora_sel = st.time_input("Hora", value=datetime.strptime("10:00", "%H:%M").time(), key="cliente_hora_sel")


                                st.caption(f"Cliente: **{usuario}**")

                                enviar = st.form_submit_button("Reservar", use_container_width=True)

                            if enviar:

                                with st.spinner("Procesando reserva..."):

                                    duracion = servicios[servicio_sel]["duracion"]

                                    precio = servicios[servicio_sel]["precio"]

                                    ok = insertar_reserva_con_fecha_hora(

                                        barberia_id,

                                        usuario,

                                        st.session_state.cliente_barbero_sel_premium,

                                        servicio_sel,

                                        fecha_sel,

                                        hora_sel,

                                        precio,

                                        duracion,

                                    )

                                    if ok:

                                        procesar_beneficio_fidelizacion(usuario, barberia_id)

                                        inicio_msg = datetime.combine(fecha_sel, hora_sel)

                                        telefono_cliente = user[4] if len(user) > 4 else obtener_telefono_usuario(usuario)

                                        if telefono_cliente:

                                            mensaje = construir_mensaje_reserva(

                                                usuario, inicio_msg, st.session_state.cliente_barbero_sel_premium, servicio_sel

                                            )

                                            try:

                                                enviar_whatsapp_twilio(telefono_cliente, mensaje)

                                            except Exception as exc:

                                                logger.exception("Error al ejecutar el envio de WhatsApp: %s", exc)

                                    st.success("Reserva creada exitosamente")

                                    st.rerun()

            # TAB: LISTADO

            with tab_lista:

                st.markdown("### Tus reservas")

                if not db_ok:

                    st.info("Lista de reservas no disponible sin base de datos.")

                else:

                    with st.spinner("Cargando datos..."):

                        mis_reservas = listar_reservas_filtradas(barberia_id, "CLIENTE", usuario)

                    if mis_reservas:

                        mostrar_reservas_dataframe(mis_reservas)


                        # Payment UI for unpaid reservations

                        ui_pagar_reserva(mis_reservas, barberia_id, usuario)


                        ui_eliminar_reserva_lista(mis_reservas, "cliente")

                    else:

                        st.info("Aún no tienes reservas. ¡Crea una!")

    # ================= BARBERO =================

    elif nr == "BARBERO":

        if not barberia_id:

            st.warning("No hay barberia asociada a la sesión.")

            st.stop()

        if seccion == "Dashboard":

            render_panel_header(
                "Visión general",
                "Panel de control de cortes, agenda e ingresos.",
                eyebrow="Panel barbero",
                meta=barberia_name,
            )


            if not db_ok:

                render_alert("Métricas no disponibles sin base de datos", alert_type="info")

            else:

                with st.spinner("Cargando métricas..."):

                    total_hoy, pagadas_hoy, pendientes_hoy = calcular_metricas_header(barberia_id)

                    total_reservas, hoy_reservas, total_ingresos = calcular_metricas_barbero(barberia_id, user[0])


                # Dashboard metrics

                col1, col2, col3 = st.columns(3, gap="large")

                with col1:

                    render_stat_box("Reservas Hoy", total_hoy, "Calendario", Colors.PRIMARY)

                with col2:

                    render_stat_box("Pagadas", pagadas_hoy, "[OK]", Colors.SUCCESS)

                with col3:

                    render_stat_box("Pendientes", pendientes_hoy, "Espera", Colors.WARNING)


                render_divider()


                render_subsection_title("Rendimiento")

                col_x, col_y, col_z = st.columns(3, gap="large")

                with col_x:

                    render_stat_box("Cortes", total_reservas, "Servicio", Colors.PRIMARY)

                with col_y:

                    render_stat_box("Hoy", hoy_reservas, "Hoy", Colors.SECONDARY)

                with col_z:

                    render_stat_box("Ingresos", f"${total_ingresos}", "$", Colors.SUCCESS)


                render_divider()


                with st.spinner("Cargando próximas citas..."):

                    reservas_barbero = listar_reservas_filtradas(barberia_id, "BARBERO", usuario)

                    hoy = datetime.now().date()

                    hoy_reservas_list = [r for r in reservas_barbero if r[3] == hoy]


                if hoy_reservas_list:

                    render_subsection_title("Próximas citas (hoy)")

                    for r in hoy_reservas_list[:5]:

                        hora_str = r[4].strftime("%H:%M") if hasattr(r[4], "strftime") else str(r[4])

                        cliente_str = r[5] or r[6]

                        servicio_str = r[2]

                        st.markdown(f"""

                        <div style="

                            background-color: {Colors.CARD};

                            border-left: 4px solid {Colors.PRIMARY};

                            padding: {Spacing.MD};

                            border-radius: {BorderRadius.MD};

                            margin-bottom: {Spacing.SM};

                        ">

                            <strong style="color: {Colors.PRIMARY};">Hora: {hora_str}</strong> - <span style="color: {Colors.TEXT};">{cliente_str}</span> ({servicio_str})
                        </div>

                        """, unsafe_allow_html=True)

        elif seccion == "Agenda":

            render_panel_header(
                "Agenda y calendario",
                "Gestiona tus reservas, disponibilidad y listado de citas.",
                eyebrow="Agenda",
                meta=barberia_name,
            )


            tab_cal, tab_crear, tab_lista = st.tabs([

                "Calendario Calendario",

                "Editar Crear/Editar",

                "Listado Listado"

            ])


            # TAB: CALENDARIO

            with tab_cal:

                if db_ok:

                    with st.spinner("Cargando datos..."):

                        eventos_barbero = obtener_reservas(usuario)

                    render_agenda_interactiva(eventos_barbero, usuario, read_only=False)

                else:

                    st.warning("Calendario no disponible sin base de datos (modo demo).")


            # TAB: CREAR/EDITAR

            with tab_crear:

                render_gestion_agenda(usuario)


            # TAB: LISTADO

            with tab_lista:

                st.markdown("### Mis reservas")


                # Toggle between card and calendar view

                view_type = st.radio(

                    "Modo de vista",

                    ["Tarjetas Tarjetas", "Calendario Calendario"],

                    horizontal=True,

                    key="barbero_view_type"

                )


                if not db_ok:

                    st.info("Tabla no disponible sin base de datos.")

                else:

                    with st.spinner("Cargando tus reservas..."):

                        rows_bar = listar_reservas_filtradas(barberia_id, "BARBERO", usuario)


                    if rows_bar:

                        if view_type == "Tarjetas Tarjetas":

                            mostrar_reservas_dataframe(rows_bar)

                            ui_marcar_pagado_reservas(rows_bar, "barbero_panel")

                            ui_eliminar_reserva_lista(rows_bar, "barbero_panel")

                        else:  # Calendar view

                            # Convert rows to calendar format

                            reservas_calendar = []

                            for r in rows_bar:

                                fecha = r.get("fecha")

                                hora = r.get("hora")

                                if fecha and hora:

                                    try:

                                        start_dt = datetime.combine(fecha, hora)

                                        end_dt = start_dt + timedelta(minutes=30)

                                        monto = r.get("monto") or r.get("precio") or 0

                                        pagado = bool(r.get("pagado", False))

                                        reservas_calendar.append((r.get("id"), r.get("cliente") or r.get("nombre"), r.get("barbero"), r.get("servicio"), monto, start_dt, end_dt, pagado))

                                    except (TypeError, ValueError):

                                        continue


                            mostrar_calendario_reservas(reservas_calendar)

                            st.markdown("---")

                            st.caption("Vista de calendario en formato semanal: usa las flechas para navegar")

                    else:

                        st.info("No hay reservas")

        elif seccion == "Barberos":

            render_section_title("Equipo", subtitle="Gestión de barberos")

            render_alert("Solo el administrador de la barbería puede gestionar el equipo de barberos", alert_type="info")

        elif seccion == "Configuración":

            render_panel_header(
                "Configuración",
                "Preferencias y ajustes disponibles para tu cuenta.",
                eyebrow="Ajustes",
                meta=nr.replace("_", " "),
            )

            render_alert("Preferencias y ajustes próximamente", alert_type="info")

    # ================= ADMIN =================

    elif nr == "ADMIN":

        if not barberia_id:

            st.warning("No hay barberia asociada a la sesión.")

            st.stop()

        if seccion == "Dashboard":

            render_panel_header(
                "Visión general",
                "Gestiona métricas, agenda y actividad diaria de tu barbería.",
                eyebrow="Panel administrativo",
                meta=barberia_name,
            )


            if not db_ok:

                render_alert("Métricas no disponibles sin base de datos", alert_type="info")

            else:

                with st.spinner("Cargando métricas..."):

                    total_hoy, pagadas_hoy, pendientes_hoy = calcular_metricas_header(barberia_id)

                    total_reservas, hoy_reservas, total_ingresos, num_barberos = calcular_metricas_admin(barberia_id)


                # Dashboard metrics

                render_metric_grid([
                    ("Reservas Hoy", total_hoy, "Calendario", Colors.PRIMARY),
                    ("Pagadas", pagadas_hoy, "[OK]", Colors.SUCCESS),
                    ("Pendientes", pendientes_hoy, "Cargando", Colors.WARNING),
                ], columns=3)


                render_divider()


                render_subsection_title("Resumen general")

                render_metric_grid([
                    ("Total Reservas", total_reservas, "Listado", Colors.SECONDARY),
                    ("Hoy", hoy_reservas, "Hoy", Colors.PRIMARY),
                    ("Ingresos", f"${total_ingresos}", "$", Colors.SUCCESS),
                    ("Barberos", num_barberos, "Servicio", Colors.WARNING),
                ], columns=4)


                render_divider()

                with st.spinner("Cargando próximas citas..."):

                    todas_reservas = safe_fetch_all(

                        """

                        SELECT id, barbero, servicio, fecha, hora, cliente, nombre, inicio, precio, estado, pagado, monto

                        FROM reservas

                        WHERE barberia_id = %s

                        ORDER BY inicio DESC

                        """,

                        (barberia_id,),

                    ) or []

                    hoy = datetime.now().date()

                    hoy_reservas_list = [r for r in todas_reservas if r[3] == hoy]


                if hoy_reservas_list:

                    st.markdown("### ð Próximas Citas (Hoy)")

                    for r in hoy_reservas_list[:5]:

                        hora_str = r[4].strftime("%H:%M") if hasattr(r[4], "strftime") else str(r[4])

                        cliente_str = r[5] or r[6]

                        st.caption(f"ð {hora_str} - {cliente_str} con {r[1]} ({r[2]})")

        elif seccion == "Agenda":

            render_panel_header(
                "Agenda y calendario",
                "Consulta reservas, crea citas y revisa ingresos desde una vista operativa.",
                eyebrow="Agenda",
                meta=barberia_name,
            )


            # Fetch eventos for calendar

            eventos = []

            if db_ok:

                try:

                    eventos = obtener_reservas()

                except Exception as e:

                    logger.exception("Error fetching eventos for ADMIN")

                    eventos = []


            tab_cal, tab_crear, tab_lista, tab_ingresos = st.tabs([

                "Calendario Calendario",

                "Editar Crear/Editar",

                "Listado Reservas",

                "$ Ingresos"

            ])


            # TAB: CALENDARIO

            with tab_cal:

                if db_ok:

                    with st.spinner("Cargando calendario..."):

                        render_calendario_multi_barbero(eventos, read_only=not db_ok)

                else:

                    st.warning("Calendario no disponible sin base de datos (modo demo).")


            # TAB: CREAR/EDITAR

            with tab_crear:

                render_gestion_agenda()


            # TAB: RESERVAS

            with tab_lista:

                st.markdown("### Reservas")


                # Toggle between card and calendar view

                col_view1, col_view2 = st.columns(2)

                with col_view1:

                    view_type = st.radio(

                        "Modo de vista",

                        ["Tarjetas Tarjetas", "Calendario Calendario"],

                        horizontal=True,

                        key="admin_view_type"

                    )


                if not db_ok:

                    st.info("Tabla no disponible sin base de datos.")

                else:

                    filtro_adm = st.selectbox(

                        "Filtrar por barbero",

                        opciones_filtro_barberos_ui(barberia_id),

                        key="tabla_admin_filtro",

                    )

                    with st.spinner("Cargando datos..."):

                        rows_adm = listar_reservas_filtradas(

                            barberia_id, "ADMIN", usuario, filtro_barbero=filtro_adm

                        )


                    if rows_adm:

                        if view_type == "Tarjetas Tarjetas":

                            mostrar_reservas_dataframe(rows_adm)

                            ui_marcar_pagado_reservas(rows_adm, "admin_panel")

                            ui_eliminar_reserva_lista(rows_adm, "admin_panel")

                        else:  # Calendar view

                            # Convert rows to calendar format

                            reservas_calendar = []

                            for r in rows_adm:

                                fecha = r.get("fecha")

                                hora = r.get("hora")

                                if fecha and hora:

                                    try:

                                        start_dt = datetime.combine(fecha, hora)

                                        end_dt = start_dt + timedelta(minutes=30)

                                        monto = r.get("monto") or r.get("precio") or 0

                                        pagado = bool(r.get("pagado", False))

                                        reservas_calendar.append((r.get("id"), r.get("cliente") or r.get("nombre"), r.get("barbero"), r.get("servicio"), monto, start_dt, end_dt, pagado))

                                    except (TypeError, ValueError):

                                        continue


                            mostrar_calendario_reservas(reservas_calendar)

                            st.markdown("---")

                            st.caption("Vista de calendario en formato semanal: usa las flechas para navegar")

                    else:

                        st.info("No hay reservas")


            # TAB: INGRESOS

            with tab_ingresos:

                st.markdown("### Ingresos")

                if db_ok:

                    with st.spinner("Cargando datos..."):

                        total_row = safe_fetch_one(

                            "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND pagado = TRUE",

                            (barberia_id,),

                        )

                        total = total_row[0] if total_row and total_row[0] else 0

                    st.metric("Ingresos totales (pagado)", f"${total}")


                    st.markdown("---")

                    st.markdown("#### Desglose por barbero")

                    with st.spinner("Cargando desglose..."):

                        barberos_list = listar_usuarios_barberos(barberia_id)

                        for barbero_id_val, barbero_name in barberos_list:

                            barbero_ingresos = safe_fetch_one(

                                "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND barbero_id = %s AND pagado = TRUE",

                                (barberia_id, barbero_id_val),

                            )

                            ingreso = barbero_ingresos[0] if barbero_ingresos and barbero_ingresos[0] else 0

                            st.caption(f"{barbero_name}: ${ingreso}")

        elif seccion == "Barberos":

            render_panel_header(
                "Equipo",
                "Crea y administra los barberos asociados a esta barbería.",
                eyebrow="Gestión",
                meta=barberia_name,
            )


            render_equipo_barberos(barberia_id)

        elif seccion == "Configuración":

            render_panel_header(
                "Configuración",
                "Datos de la barbería, preferencias y ajustes generales.",
                eyebrow="Ajustes",
                meta=barberia_name,
            )

            render_alert("Datos de la barbería y preferencias próximamente", alert_type="info")

        elif seccion == "Servicios":

            render_panel_header(
                "Servicios",
                "Crea, edita y elimina los servicios que ofrece tu barbería.",
                eyebrow="Catálogo",
                meta=barberia_name,
            )

            render_gestion_servicios(barberia_id)

        elif seccion == "Clientes":

            render_panel_header(
                "Clientes",
                "Centraliza la vista de clientes, historial y actividad.",
                eyebrow="CRM",
                meta=barberia_name,
            )

            render_panel_empty_state(
                "Vista de clientes pendiente",
                "Esta sección queda preparada visualmente para una futura pantalla de clientes sin cambiar consultas ni base de datos.",
            )

        elif seccion == "Sitio Web":

            render_panel_header(
                "Sitio Web",
                "Configura la experiencia pública de tu barbería desde el panel.",
                eyebrow="Presencia online",
                meta=barberia_name,
            )

            render_panel_empty_state(
                "Editor del sitio pendiente",
                "La sección está preparada para centralizar la configuración del sitio público en una fase posterior.",
            )

        elif seccion == "Complementos":

            render_panel_header(
                "Complementos",
                "Extensiones, integraciones y herramientas adicionales.",
                eyebrow="Add-ons",
                meta=barberia_name,
            )

            render_panel_empty_state(
                "Complementos pendiente",
                "No se detectó una lógica existente de complementos; se deja una pantalla visual segura sin efectos laterales.",
            )

    # ================= SUPER_ADMIN =================

    elif nr == "SUPER_ADMIN":

        if seccion == "Dashboard":

            render_panel_header(
                "Visión global",
                "Supervisa métricas y operación de todas las barberías.",
                eyebrow="Super admin",
                meta="Vista plataforma",
            )


            if not db_ok:

                render_alert("Métricas no disponibles sin base de datos", alert_type="info")

            else:

                with st.spinner("Cargando métricas globales..."):

                    total_hoy, pagadas_hoy, pendientes_hoy = calcular_metricas_header(bid_ctx) if bid_ctx else (0, 0, 0)

                    num_barberias, num_usuarios, num_reservas, total_ingresos, hoy_count = calcular_metricas_super_admin(bid_ctx)


                # Dashboard metrics

                col1, col2, col3 = st.columns(3, gap="large")

                with col1:

                    render_stat_box("Reservas Hoy", total_hoy, "Calendario", Colors.PRIMARY)

                with col2:

                    render_stat_box("Pagadas", pagadas_hoy, "[OK]", Colors.SUCCESS)

                with col3:

                    render_stat_box("Pendientes", pendientes_hoy, "Cargando", Colors.WARNING)


                render_divider()


                render_subsection_title("Resumen global")

                render_metric_grid([
                    ("Barberías", num_barberias, "Barberias", Colors.PRIMARY),
                    ("Usuarios", num_usuarios, "Rol", Colors.SECONDARY),
                    ("Total", num_reservas, "Listado", Colors.PRIMARY),
                    ("Hoy", hoy_count, "Hoy", Colors.SECONDARY),
                    ("Ingresos", f"${total_ingresos}", "$", Colors.SUCCESS),
                ], columns=5)

        elif seccion == "Agenda":

            render_panel_header(
                "Agenda global",
                "Vista consolidada de citas, reservas e ingresos.",
                eyebrow="Agenda",
                meta="Contexto global",
            )


            # Fetch eventos for calendar

            eventos = []

            if db_ok:

                try:

                    eventos = obtener_reservas()

                except Exception as e:

                    logger.exception("Error fetching eventos for SUPER_ADMIN")

                    eventos = []


            tab_cal, tab_crear, tab_lista, tab_ingresos = st.tabs([

                "Calendario Calendario",

                "Editar Crear/Editar",

                "Listado Reservas",

                "$ Ingresos"

            ])


            # TAB: CALENDARIO

            with tab_cal:

                if db_ok:

                    with st.spinner("Cargando calendario..."):

                        render_calendario_multi_barbero(eventos, read_only=not db_ok)

                else:

                    st.warning("Calendario no disponible sin base de datos (modo demo).")


            # TAB: CREAR/EDITAR

            with tab_crear:

                render_gestion_agenda()

            # TAB: RESERVAS

            with tab_lista:

                st.markdown("### Reservas")


                # Toggle between card and calendar view

                view_type = st.radio(

                    "Modo de vista",

                    ["Tarjetas Tarjetas", "Calendario Calendario"],

                    horizontal=True,

                    key="super_view_type"

                )


                if not db_ok:

                    st.info("Tabla no disponible sin base de datos.")

                else:

                    filtro_su = st.selectbox(

                        "Filtrar por barbero",

                        opciones_filtro_barberos_ui(bid_ctx) if bid_ctx else ["Todos"] + list(barberos.keys()),

                        key="tabla_super_filtro",

                    )

                    with st.spinner("Cargando reservas..."):

                        rows_su = listar_reservas_filtradas(

                            bid_ctx, "SUPER_ADMIN", usuario, filtro_barbero=filtro_su

                        )

                    if rows_su:

                        if view_type == "Tarjetas Tarjetas":

                            mostrar_reservas_dataframe(rows_su)

                            ui_marcar_pagado_reservas(rows_su, "super_panel")

                            ui_eliminar_reserva_lista(rows_su, "super_panel")

                        else:  # Calendar view

                            # Convert rows to calendar format

                            reservas_calendar = []

                            for r in rows_su:

                                fecha = r.get("fecha")

                                hora = r.get("hora")

                                if fecha and hora:

                                    try:

                                        start_dt = datetime.combine(fecha, hora)

                                        end_dt = start_dt + timedelta(minutes=30)

                                        monto = r.get("monto") or r.get("precio") or 0

                                        pagado = bool(r.get("pagado", False))

                                        reservas_calendar.append((r.get("id"), r.get("cliente") or r.get("nombre"), r.get("barbero"), r.get("servicio"), monto, start_dt, end_dt, pagado))

                                    except (TypeError, ValueError):

                                        continue


                            mostrar_calendario_reservas(reservas_calendar)

                            st.markdown("---")

                            st.caption("Vista de calendario en formato semanal: usa las flechas para navegar")

                    else:

                        st.info("No hay reservas")

            # TAB: INGRESOS

            with tab_ingresos:

                st.markdown("### Ingresos (barbería activa)")

                if db_ok and bid_ctx:

                    with st.spinner("Cargando datos de ingresos..."):

                        total_row = safe_fetch_one(

                            "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND pagado = TRUE",

                            (bid_ctx,),

                        )

                        total = total_row[0] if total_row and total_row[0] else 0

                    st.metric("Ingresos totales (pagado)", f"${total}")


                    st.markdown("---")

                    st.markdown("#### Desglose por barbero")

                    with st.spinner("Cargando desglose..."):

                        barberos_list = listar_usuarios_barberos(bid_ctx)

                        for barbero_id_val, barbero_name in barberos_list:

                            barbero_ingresos = safe_fetch_one(

                                "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND barbero_id = %s AND pagado = TRUE",

                                (bid_ctx, barbero_id_val),

                            )

                            ingreso = barbero_ingresos[0] if barbero_ingresos and barbero_ingresos[0] else 0

                            st.caption(f"{barbero_name}: ${ingreso}")

                else:

                    st.info("Selecciona una barbería para ver ingresos")

        elif seccion == "Barberos":

            render_panel_header(
                "Equipo",
                "Barberos del contexto de barbería seleccionado.",
                eyebrow="Gestión",
                meta="Contexto activo",
            )

            if bid_ctx:

                render_equipo_barberos(bid_ctx)

            else:

                st.info("Selecciona una barbería en la barra lateral.")

        elif seccion == "Configuración":

            render_panel_header(
                "Configuración global",
                "Parámetros generales de la plataforma.",
                eyebrow="Ajustes",
                meta="Super admin",
            )

            st.info("Parámetros de plataforma próximamente.")

        elif seccion == "Servicios":

            render_panel_header(
                "Servicios",
                "Administra los servicios de la barbería activa en contexto.",
                eyebrow="Catálogo",
                meta="Contexto activo",
            )

            if bid_ctx:

                render_gestion_servicios(bid_ctx)

            else:

                render_alert("Selecciona una barbería en la barra lateral para gestionar sus servicios.", alert_type="info")

        elif seccion == "Clientes":

            render_panel_header(
                "Clientes",
                "Vista preparada para clientes e historial por barbería.",
                eyebrow="CRM",
                meta="Contexto activo",
            )

            render_panel_empty_state(
                "Clientes pendiente",
                "No se agregaron consultas nuevas para respetar el alcance visual y no tocar base de datos.",
            )

        elif seccion == "Sitio Web":

            render_panel_header(
                "Sitio Web",
                "Sección preparada para gestionar presencia pública por barbería.",
                eyebrow="Presencia online",
                meta="Contexto activo",
            )

            render_panel_empty_state(
                "Configuración del sitio pendiente",
                "El sitio público no fue modificado; esta pantalla solo prepara el panel interno.",
            )

        elif seccion == "Complementos":

            render_panel_header(
                "Complementos",
                "Integraciones y herramientas adicionales de plataforma.",
                eyebrow="Add-ons",
                meta="Super admin",
            )

            render_panel_empty_state(
                "Complementos pendiente",
                "No se detectó una lógica existente de complementos; se deja una pantalla visual segura.",
            )

    else:

        st.error(f"Vista no disponible para el rol: {nr}")

except Exception as e:

    logger.exception("Unhandled exception in Streamlit app")

    st.error(f"Error en la aplicación:\n{traceback.format_exc()}")