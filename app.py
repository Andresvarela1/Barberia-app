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
from whatsapp import enviar_whatsapp as enviar_whatsapp_twilio

try:
    import mercadopago
except ImportError:
    mercadopago = None

_dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=_dotenv_path)

st.set_page_config(
    page_title="Barbería Leveling",
    page_icon="💈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

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
        logger.info("📌 Creando conexión PostgreSQL: %s", masked)

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
        logger.info("✅ Conexión a DB creada exitosamente")
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
                logger.warning("⚠️ Error en base de datos, reintentando... (intento %d)", attempt + 1)
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
                        nombre TEXT NOT NULL UNIQUE
                    );
                    """
                )
                conn.commit()
                logger.info("✅ Tabla 'barberias' creada o ya existe")
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
                logger.info("✅ Tabla 'usuarios' creada o ya existe")
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
                logger.info("✅ Índice 'idx_usuarios_barberia' creado o ya existe")
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
                logger.info("✅ Tabla 'reservas' creada o ya existe")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error creando tabla 'reservas': {e}")
                st.error(f"Error creando tabla 'reservas': {e}")

            # Index on reservas
            try:
                cur.execute("CREATE INDEX IF NOT EXISTS idx_reservas_barberia ON reservas(barberia_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_reservas_barbero ON reservas(barbero);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_reservas_fecha ON reservas(fecha);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_reservas_inicio ON reservas(inicio);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_reservas_pagado ON reservas(pagado);")
                conn.commit()
                logger.info("✅ Índices de 'reservas' creados o ya existen")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error creando índices de 'reservas': {e}")
                st.error(f"Error creando índices de 'reservas': {e}")

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
                cur.execute("UPDATE reservas SET monto = precio WHERE monto IS NULL;")
                conn.commit()
                logger.info("✅ Columnas opcionales en 'reservas' añadidas o actualizadas")
                logger.info("✅ payment_id column ensured")
                logger.info("✅ updated_at column ensured")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error alterando tabla 'reservas': {e}")
                st.error(f"Error alterando tabla 'reservas': {e}")

        if all_ok:
            logger.info("✅ Todas las tablas y restricciones creadas correctamente")
        else:
            logger.warning("⚠️ Algunas operaciones de base de datos fallaron")
    except Exception as e:
        if conn:
            conn.rollback()
        logger.exception("Error al asegurar tablas de base de datos")
        st.error(f"Error de base de datos:\n{traceback.format_exc()}")
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
        logger.warning("❌ No hay contraseña guardada")
        return False

    if es_hash_bcrypt(password_guardada):
        try:
            # El hash está en formato bcrypt
            resultado = bcrypt.checkpw(
                password.encode("utf-8"),
                password_guardada.encode("utf-8"),
            )
            logger.info(f"✅ Verificación bcrypt: {resultado}")
            return resultado
        except ValueError as e:
            logger.exception("❌ Error en hash bcrypt: %s", str(e))
            return False
    else:
        # Fallback: comparar como plain text (para contraseñas antiguas)
        resultado = password == password_guardada
        logger.warning(f"⚠️ Usando comparación plain text (legacy): {resultado}")
        return resultado


def login(usuario, password):
    """Autentica usuario contra la base de datos."""
    usuario = normalizar_texto(usuario)
    password = normalizar_texto(password)

    if not usuario or not password:
        logger.warning(f"❌ Usuario o contraseña vacío. Usuario: '{usuario}'")
        return None

    if not st.session_state.get("db_available", True):
        logger.warning("❌ Base de datos no disponible")
        return None

    # Buscar usuario en base de datos
    user = fetch_one(
        """
        SELECT id, usuario, password, rol, telefono, barberia_id, cortes_acumulados
        FROM usuarios
        WHERE usuario=%s
        """,
        (usuario,),
    )
    
    if not user:
        logger.warning(f"❌ Usuario no encontrado: '{usuario}'")
        return None
    
    logger.info(f"✅ Usuario encontrado: {user[1]} (ID: {user[0]})")
    logger.info(f"📝 Hash format: {user[2][:20]}... (bcrypt: {es_hash_bcrypt(user[2])})")
    
    # Verificar contraseña
    if not verificar_password(password, user[2]):
        logger.warning(f"❌ Contraseña incorrecta para usuario: {usuario}")
        return None
    
    logger.info(f"✅ Contraseña verificada para: {usuario}")
    
    # Normalizar rol para asegurar que siempre sea válido
    rol_normalizado = normalizar_rol(user[3])
    if rol_normalizado != user[3]:
        logger.info(f"🔄 Normalizando rol de '{user[3]}' a '{rol_normalizado}' para: {usuario}")
        # Actualizar rol en la base de datos si es diferente
        if execute_write(
            "UPDATE usuarios SET rol=%s WHERE id=%s",
            (rol_normalizado, user[0]),
        ):
            user = (user[0], user[1], user[2], rol_normalizado, user[4], user[5], user[6])
            logger.info(f"✅ Rol actualizado en BD para: {usuario}")
        else:
            logger.warning(f"⚠️ No se pudo actualizar rol en BD, usando rol normalizado localmente")
            user = (user[0], user[1], user[2], rol_normalizado, user[4], user[5], user[6])

    # Si la contraseña es plain text, rehashearla con bcrypt
    if not es_hash_bcrypt(user[2]):
        logger.info(f"🔄 Rehasheando contraseña para: {usuario}")
        nuevo_hash = hash_password(password)
        if execute_write(
            "UPDATE usuarios SET password=%s WHERE id=%s",
            (nuevo_hash, user[0]),
        ):
            logger.info(f"✅ Contraseña rehashada para: {usuario}")
            user = (user[0], user[1], nuevo_hash, user[3], user[4], user[5], user[6])
        else:
            logger.warning(f"⚠️ No se pudo rehasear contraseña para: {usuario}")

    logger.info(f"✅ Login exitoso para: {usuario} con rol: {user[3]}")
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
        logger.warning("⚠️ DATABASE_URL no configurada - seed_default_data ignorado")
        return False

    conn = None
    try:
        conn = get_connection(notify_missing_url=False)
        if conn is None:
            logger.warning("⚠️ No se pudo conectar a la BD - seed_default_data ignorado")
            return False

        with conn.cursor() as cur:
            # 1. Crear barbería Leveling si no existe
            logger.info("📝 Verificando si barbería 'Barberia Leveling' existe...")
            cur.execute("SELECT id FROM barberias WHERE nombre = %s", ("Barberia Leveling",))
            barberia_row = cur.fetchone()

            if barberia_row:
                bid = barberia_row[0]
                logger.info(f"✅ Barbería Leveling ya existe (ID: {bid})")
            else:
                logger.info("⚠️ Barbería Leveling NO existe - creando...")
                cur.execute(
                    "INSERT INTO barberias (nombre) VALUES (%s) RETURNING id",
                    ("Barberia Leveling",),
                )
                barberia_row = cur.fetchone()
                if barberia_row and barberia_row[0]:
                    bid = barberia_row[0]
                    logger.info(f"✅ Barbería Leveling creada con ID: {bid}")
                else:
                    raise Exception("No se pudo crear la barbería por defecto")

            # 2. Crear SUPER_ADMIN si no existe
            logger.info("📝 Verificando si SUPER_ADMIN 'JoanBeatsAD' existe...")
            cur.execute("SELECT id FROM usuarios WHERE usuario = %s", ("JoanBeatsAD",))
            super_admin_row = cur.fetchone()

            if super_admin_row:
                logger.info(f"✅ SUPER_ADMIN 'JoanBeatsAD' ya existe (ID: {super_admin_row[0]})")
            else:
                logger.info("⚠️ SUPER_ADMIN 'JoanBeatsAD' NO existe - creando...")
                password_hash = hash_password("suguha09")
                cur.execute(
                    "INSERT INTO usuarios (usuario, password, rol, barberia_id) VALUES (%s, %s, %s, %s)",
                    ("JoanBeatsAD", password_hash, "SUPER_ADMIN", None),
                )
                logger.info("✅ INSERT SUPER_ADMIN ejecutado")

            # 3. Crear barberos si no existen
            logger.info("📝 Verificando barberos...")
            pwd_barb = hash_password("barbero123")
            for bu in ("Yor", "Andres", "Andrea", "Maikel"):
                cur.execute("SELECT id FROM usuarios WHERE usuario = %s", (bu,))
                if cur.fetchone():
                    logger.info(f"✅ Barbero '{bu}' ya existe")
                    continue

                cur.execute(
                    "INSERT INTO usuarios (usuario, password, rol, telefono, barberia_id, cortes_acumulados) VALUES (%s, %s, %s, %s, %s, %s)",
                    (bu, pwd_barb, "BARBERO", None, bid, 0),
                )
                logger.info(f"✅ Barbero '{bu}' creado")

        conn.commit()
        logger.info("✅ Commit exitoso - verificando SUPER_ADMIN...")

        try:
            user_check = fetch_one("SELECT id FROM usuarios WHERE usuario = %s", ("JoanBeatsAD",))
            if user_check:
                logger.info("✅ SUPER_ADMIN listo en la base de datos")
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
        logger.exception("❌ Error en seed_default_data")
        # st.sidebar.error(f"Seed error: {str(e)}")
        logger.error(f"Seed error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()


# Initialize app state and data only once
if "app_initialized" not in st.session_state:
    try:
        with st.spinner("🔄 Inicializando base de datos..."):
            ensure_database_tables()
            
            # Run seed only once
            if "seed_done" not in st.session_state:
                # Hidden seed debug output - use logger instead of st.sidebar
                logger.info("Running seed...")
                seed_result = seed_default_data()
                st.session_state.seed_done = True
                
                if seed_result:
                    logger.info("SUPER_ADMIN listo")
                elif seed_result is False:
                    logger.warning("❌ Seed falló - SUPER_ADMIN NO garantizado")
            
            default_barberia_id = inicializar_barberia()
            st.session_state.app_initialized = True
            st.session_state.default_barberia_id = default_barberia_id
    except Exception as e:
        logger.exception("Error inesperado inicializando la base de datos")
        st.error(str(e))
        default_barberia_id = None
        st.session_state.app_initialized = True  # Mark as initialized even on error
else:
    default_barberia_id = st.session_state.get("default_barberia_id")


@st.cache_data(ttl=120)
def listar_usuarios_barberos(barberia_id):
    """Fast cached barbers list with longer TTL for stability."""
    if not barberia_id:
        return []
    try:
        return fetch_all(
            """
            SELECT usuario, rol FROM usuarios
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
        if rol_u == "SUPER_ADMIN":
            return bool(
                execute_write(
                    """
                    UPDATE reservas
                    SET pagado = TRUE, monto = COALESCE(monto, precio)
                    WHERE id = %s
                    """,
                    (reserva_id,),
                )
            )
        return bool(
            execute_write(
                """
                UPDATE reservas
                SET pagado = TRUE, monto = COALESCE(monto, precio)
                WHERE id = %s AND barberia_id = %s
                """,
                (reserva_id, prev[7]),
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
        error_msg = "❌ MercadoPago SDK no está instalado. Ejecuta: pip install mercadopago"
        logger.error(error_msg)
        if show_errors:
            st.error(error_msg)
        return None
    
    # Load and validate access token
    access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not access_token or access_token.strip() == "":
        error_msg = "❌ MERCADOPAGO_ACCESS_TOKEN no configurado. Agrega a .env: MERCADOPAGO_ACCESS_TOKEN=tu_token"
        logger.error(error_msg)
        if show_errors:
            st.error(error_msg)
        return None
    
    # Debug: Show token was loaded (masked)
    token_preview = access_token[:10] + "..." if len(access_token) > 10 else access_token
    logger.info(f"🔑 Token cargado: {token_preview}")
    
    try:
        # Initialize SDK
        sdk = mercadopago.SDK(access_token)
        
        # Validate payment amount
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                raise ValueError("Monto debe ser mayor a 0")
        except (ValueError, TypeError) as e:
            error_msg = f"❌ Monto inválido: {monto}. Error: {str(e)}"
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
        
        logger.info(f"📤 Enviando preference a MercadoPago para reserva {reserva_id}...")
        
        # Create preference
        preference_response = sdk.preference().create(preference_data)
        logger.info(f"📥 Respuesta de MercadoPago: {preference_response}")
        
        # Validate response structure
        if not isinstance(preference_response, dict):
            error_msg = f"❌ Respuesta inválida de MercadoPago: tipo {type(preference_response)}"
            logger.error(error_msg)
            if show_errors:
                st.error(error_msg)
            return None
        
        # Check status code
        response_status = preference_response.get("status")
        if response_status != 201:
            error_msg = f"❌ MercadoPago error (status {response_status}): {preference_response}"
            logger.error(error_msg)
            if show_errors:
                st.error(error_msg)
            return None
        
        # Extract init_point
        if "response" not in preference_response:
            error_msg = f"❌ No 'response' en respuesta de MercadoPago: {preference_response}"
            logger.error(error_msg)
            if show_errors:
                st.error(error_msg)
            return None
        
        response_data = preference_response["response"]
        if "init_point" not in response_data:
            error_msg = f"❌ No 'init_point' en response de MercadoPago: {response_data}"
            logger.error(error_msg)
            if show_errors:
                st.error(error_msg)
            return None
        
        init_point = response_data.get("init_point")
        if not init_point:
            error_msg = "❌ init_point es vacío en respuesta de MercadoPago"
            logger.error(error_msg)
            if show_errors:
                st.error(error_msg)
            return None
        
        logger.info(f"✅ Pago creado para reserva {reserva_id}: {init_point}")
        return init_point
            
    except Exception as e:
        error_msg = f"❌ Error creando pago MercadoPago para reserva {reserva_id}: {str(e)}"
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
    
    st.markdown("### 💳 Pagar Reservas Pendientes")
    
    # DEBUG: Show token status (temporary, for troubleshooting)
    access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    token_status = "✅ Cargado" if access_token else "❌ No configurado"
    with st.expander(f"🔧 Debug - Token: {token_status}"):
        if access_token:
            st.info(f"Token cargado: {access_token[:10]}...")
        else:
            st.error("❌ MERCADOPAGO_ACCESS_TOKEN no está en .env")
    
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
            st.caption(f"📅 {fecha_label} {hora_label} · ✂️ {servicio}")
        
        with col2:
            st.metric("Monto", f"${monto}")
        
        with col3:
            if st.button(
                "💳 Generar Link",
                key=f"pagar_mp_{reserva_id}",
                use_container_width=True
            ):
                with st.spinner("⏳ Generando enlace de pago..."):
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
                        st.success(f"✅ Enlace generado para reserva #{reserva_id}")
                        st.balloons()
                    else:
                        st.error(f"❌ No se pudo generar el link para reserva #{reserva_id}")
        
        # Show payment link if generated (ALWAYS visible after generation)
        pago_key = f"pago_url_{reserva_id}"
        if pago_key in st.session_state:
            pago_url = st.session_state[pago_key]
            
            if pago_url:
                col_link1, col_link2 = st.columns([4, 1], gap="small")
                with col_link1:
                    st.link_button(
                        f"🔗 Ir a pagar ${monto} (MercadoPago)",
                        pago_url,
                        type="primary",
                        use_container_width=True
                    )
                with col_link2:
                    if st.button("Limpiar", key=f"clear_url_{reserva_id}", use_container_width=True):
                        del st.session_state[pago_key]
                        st.rerun()
                
                st.caption(
                    "⏱️ Serás redirigido a MercadoPago. Después de pagar, vuelve a esta página. "
                    "La confirmación puede tomar algunos minutos."
                )
            else:
                st.error(f"❌ El URL de pago no es válido")
        
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
                "🔥 ¡Tienes un descuento en tu próximo corte!",
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
    """Fast cached reservations query with minimal overhead - returns list of dicts."""
    if not st.session_state.get("db_available", True):
        return []
    
    try:
        user = st.session_state.get("user")
        if not user:
            return []

        rol = normalizar_rol(user[3])
        uid = user[1]
        bid = effective_barberia_id()
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
            sql += " AND barbero = %s"
            params.append(uid)
        elif barbero_filtro and rol in ("ADMIN", "SUPER_ADMIN"):
            sql += " AND barbero = %s"
            params.append(barbero_filtro)

        sql += " ORDER BY inicio"
        results = fetch_all(sql, tuple(params)) or []
        
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
            titulo = f"{cliente} • {servicio}"
        
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
        st.error("❌ Reserva no encontrada")
        return None
    
    # Extract details
    cliente = reserva.get('nombre', 'Desconocido')
    servicio = reserva.get('servicio', '')
    inicio = reserva.get("inicio")
    inicio_str = inicio.strftime("%H:%M") if hasattr(inicio, "strftime") else str(inicio)
    fecha_str = inicio.strftime("%d/%m/%Y") if hasattr(inicio, "strftime") else ""
    pagado = reserva.get("pagado", False)
    estado = "✅ Pagado" if pagado else "⏳ Pendiente"
    estado_color = "#16a34a" if pagado else "#f59e0b"
    monto = reserva.get('monto', 0)
    
    # AgendaPro-style card
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-left: 5px solid {estado_color};
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    ">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
            <div>
                <div style="font-size: 12px; color: #999; margin-bottom: 4px;">👤 CLIENTE</div>
                <div style="font-size: 18px; font-weight: 600; color: #fff;">{cliente}</div>
            </div>
            <div>
                <div style="font-size: 12px; color: #999; margin-bottom: 4px;">✂️ SERVICIO</div>
                <div style="font-size: 18px; font-weight: 600; color: #fff;">{servicio}</div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
            <div>
                <div style="font-size: 12px; color: #999; margin-bottom: 4px;">🕐 HORA</div>
                <div style="font-size: 18px; font-weight: 600; color: #fff;">{inicio_str}</div>
                <div style="font-size: 12px; color: #666;">{fecha_str}</div>
            </div>
            <div>
                <div style="font-size: 12px; color: #999; margin-bottom: 4px;">💰 MONTO</div>
                <div style="font-size: 18px; font-weight: 600; color: #fff;">${monto}</div>
            </div>
        </div>
        
        <div style="border-top: 1px solid #333; padding-top: 12px;">
            <div style="display: inline-block; background: {estado_color}20; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; color: {estado_color}; border: 1px solid {estado_color};">
                {estado}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Action buttons
    user = st.session_state.get("user")
    nr = normalizar_rol(user[3]) if user else ""
    
    # Only show buttons if user has permission
    if nr != "CLIENTE":
        col1, col2 = st.columns(2)
        
        # Mark as paid button
        if not pagado:
            with col1:
                if st.button(
                    "✅ Marcar Pagado",
                    key=f"btn_pagado_{reserva_id}",
                    use_container_width=True
                ):
                    if marcar_reserva_pagada(reserva_id):
                        st.success("✅ Pago registrado")
                        st.session_state.mostrar_detalles_reserva = False
                        st.rerun()
        
        # Cancel/Delete button
        with col2:
            if st.button(
                "❌ Cancelar",
                key=f"btn_cancelar_{reserva_id}",
                use_container_width=True,
                type="secondary"
            ):
                if eliminar_reserva(reserva_id):
                    st.success("✅ Reserva cancelada")
                    st.session_state.mostrar_detalles_reserva = False
                    st.rerun()
    
    return reserva


def agrupar_por_barbero(events):
    """Group calendar events by barber for multi-barber layout. Handle both events and raw reservations."""
    barberos_dict = {}
    
    for item in events:
        try:
            # Handle event dictionary format from construir_eventos_calendario
            if isinstance(item, dict):
                barbero_id = item.get("resourceId", "unknown")
                barber_name = item.get("title", "").split("•")[0].strip() or "Barbero"
                key = (barbero_id, barber_name)
                if key not in barberos_dict:
                    barberos_dict[key] = []
                barberos_dict[key].append(item)
            else:
                # Log unexpected format and skip
                logger.warning(f"Unexpected item format in agrupar_por_barbero: {type(item)}")
        except Exception as e:
            logger.warning(f"Error processing item in agrupar_por_barbero: {e}")
            continue
    
    return barberos_dict


def render_calendario_multi_barbero(reservas, read_only=False):
    """Render multiple calendars in columns, one per barber (AgendaPro style layout)."""
    if not reservas:
        st.info("📭 No hay reservas para mostrar en el calendario.")
        return
    
    # Group reservations by barber
    barberos_dict = agrupar_por_barbero(reservas)
    
    if not barberos_dict:
        st.info("📭 No hay reservas para mostrar.")
        return
    
    # Professional header with legend
    col_title, col_legend = st.columns([2, 1])
    with col_title:
        st.markdown(f"### 📅 Vista Multi-Barbero")
    
    with col_legend:
        st.markdown("""
        <div style="display: flex; gap: 12px; font-size: 11px; padding: 8px;">
            <div><span style="display: inline-block; width: 10px; height: 10px; background: #16a34a; border-radius: 2px; margin-right: 4px;"></span><strong>Pagado</strong></div>
            <div><span style="display: inline-block; width: 10px; height: 10px; background: #f59e0b; border-radius: 2px; margin-right: 4px;"></span><strong>Pendiente</strong></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create columns for each barber
    num_barbers = len(barberos_dict)
    cols = st.columns(num_barbers) if num_barbers <= 3 else st.columns(3)  # Max 3 columns
    
    for idx, (barbero_id, reservas_barbero) in enumerate(sorted(barberos_dict.items())):
        # Get barber name from first reservation
        barber_name = reservas_barbero[0][1] if reservas_barbero else f"Barbero {barbero_id}"
        
        col_index = idx % len(cols)
        with cols[col_index]:
            # Subheader for barber
            st.subheader(f"💈 {barber_name}")
            
            # Convert reservations to events for this barber
            eventos_barbero = construir_eventos_calendario(reservas_barbero)
            
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
                    key=f"calendario_barbero_{barbero_id}",
                )
                
                if calendar_state and calendar_state.get("eventClick"):
                    manejar_interaccion_calendario(calendar_state)
            except Exception as e:
                logger.exception(f"Error displaying calendar for barber {barbero_id}")
                st.error(f"Error al mostrar calendario para {barber_name}: {str(e)}")


def obtener_reservas(barbero=None):
    return construir_eventos_calendario(obtener_reservas_raw(barbero))


def obtener_reserva_por_id(reserva_id):
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
    cli = prev[8] if len(prev) > 8 else None

    if rol_u == "BARBERO" and prev[2] != uid:
        st.error("Sin permiso para eliminar esta reserva.")
        return False
    if rol_u == "ADMIN" and prev[7] != st.session_state.get("barberia_id"):
        st.error("Sin permiso para eliminar esta reserva.")
        return False
    if rol_u == "CLIENTE" and (cli or prev[1]) != uid:
        st.error("Sin permiso para eliminar esta reserva.")
        return False

    try:
        if rol_u == "SUPER_ADMIN":
            return bool(execute_write("DELETE FROM reservas WHERE id = %s", (reserva_id,)))
        return bool(
            execute_write(
                "DELETE FROM reservas WHERE id = %s AND barberia_id = %s",
                (reserva_id, prev[7]),
            )
        )
    except Exception as e:
        logger.exception("eliminar_reserva")
        st.error(f"Error eliminando reserva:\n{traceback.format_exc()}")
        return False


def insertar_reserva_con_fecha_hora(
    barberia_id,
    cliente_usuario,
    barbero,
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
                WHERE barberia_id = %s AND barbero = %s AND fecha = %s AND hora = %s
                LIMIT 1
                """,
                (barberia_id, barbero, fecha, hora),
            )
            if cur.fetchone():
                conn.rollback()
                st.error("Horario ocupado")
                return False

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
                INSERT INTO reservas (
                    nombre, barbero, servicio, precio, inicio, fin, barberia_id,
                    cliente, fecha, hora, estado, monto, pagado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)
                RETURNING id
                """,
                (
                    cliente_usuario,
                    barbero,
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
def listar_reservas_filtradas(barberia_id_arg, rol_tag, usuario_login, filtro_barbero=None):
    """Fast cached filtered reservations - returns normalized list of dicts."""
    nr = normalizar_rol(rol_tag)
    cols = (
        "id, barbero, servicio, fecha, hora, cliente, nombre, inicio, precio, estado, pagado, monto"
    )

    try:
        super_all = nr == "SUPER_ADMIN" and st.session_state.get("super_admin_all_barberias")

        # Pre-built queries for each role type
        if nr == "CLIENTE":
            bid = barberia_id_arg or effective_barberia_id()
            if not bid:
                return []
            results = fetch_all(
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
            bid = barberia_id_arg or effective_barberia_id()
            if not bid:
                return []
            results = fetch_all(
                f"""
                SELECT {cols}
                FROM reservas
                WHERE barberia_id = %s AND barbero = %s
                ORDER BY inicio DESC NULLS LAST
                """,
                (bid, usuario_login),
            ) or []
            return [normalizar_reserva(r) for r in results]

        if super_all:
            sql = f"SELECT {cols} FROM reservas WHERE 1=1"
            params = []
            if filtro_barbero and filtro_barbero != "Todos":
                sql += " AND barbero = %s"
                params.append(filtro_barbero)
            sql += " ORDER BY inicio DESC NULLS LAST"
            results = fetch_all(sql, tuple(params)) or []
            return [normalizar_reserva(r) for r in results]

        bid = barberia_id_arg or effective_barberia_id()
        if not bid:
            return []

        sql = f"SELECT {cols} FROM reservas WHERE barberia_id = %s"
        params = [bid]
        if filtro_barbero and filtro_barbero != "Todos":
            sql += " AND barbero = %s"
            params.append(filtro_barbero)
        sql += " ORDER BY inicio DESC NULLS LAST"
        results = fetch_all(sql, tuple(params)) or []
        return [normalizar_reserva(r) for r in results]

    except Exception as e:
        logger.exception("Error listando reservas")
        return []


def mostrar_reservas_dataframe(rows):
    if not rows:
        st.info("📭 No hay reservas para mostrar.")
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
        st.markdown(f"### 📅 {fecha_label}")
        
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

            st.markdown(f"""
<div style="border-radius: 12px; padding: 16px; margin-bottom: 12px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-left: 6px solid {estado_color}; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15); border: 1px solid rgba(255, 255, 255, 0.1); transition: all 0.3s ease;">
    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
        <h4 style="margin: 0; color: #ffffff; font-size: 18px; font-weight: 600;">{cliente}</h4>
        <span style="background-color: {estado_bg}; color: {estado_color}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; border: 1px solid {estado_color};">{estado_label}</span>
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-top: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;"><span style="font-size: 16px;">🕐</span><span style="color: #e0e0e0;"><strong>{hora_label}</strong></span></div>
        <div style="display: flex; align-items: center; gap: 8px;"><span style="font-size: 16px;">✂️</span><span style="color: #e0e0e0;"><strong>{servicio}</strong></span></div>
        <div style="display: flex; align-items: center; gap: 8px;"><span style="font-size: 16px;">💇</span><span style="color: #e0e0e0;"><strong>{barbero}</strong></span></div>
        <div style="display: flex; align-items: center; gap: 8px;"><span style="font-size: 16px;">Monto</span><span style="color: #e0e0e0;"><strong>${monto}</strong></span></div>
    </div>
</div>
""", unsafe_allow_html=True)



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
        return f"#{i} · {barbero_str} · {fecha_str} {hora_str}"

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
        return f"#{i} · {row.get('barbero')} · {row.get('servicio')} · {row.get('inicio')}"

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
        st.info("📭 No hay reservas para mostrar en el calendario.")
        return
    
    # Convert reservations to calendar events
    eventos = construir_eventos_calendario(reservas)
    
    if not eventos:
        st.info("📭 No hay eventos para mostrar.")
        return
    
    # Professional header with legend
    col_title, col_legend = st.columns([2, 1])
    with col_title:
        st.markdown(f"### 📅 Vista de Calendario (Semana)")
    
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
                with st.spinner("⏳ Actualizando reserva..."):
                    actualizar_reserva(
                        reserva[0],
                        reserva[1],
                        reserva[2],
                        reserva[3],
                        reserva[4],
                        normalizar_datetime(evento.get("start")),
                        normalizar_datetime(evento.get("end")),
                    )
                st.success("✅ Reserva actualizada")
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
        st.markdown(f"### 📅 Agenda de Reservas")
    
    with col_legend:
        st.markdown("""
        <div style="display: flex; gap: 12px; font-size: 12px; padding: 8px;">
            <div><span style="display: inline-block; width: 12px; height: 12px; background: #16a34a; border-radius: 2px; margin-right: 4px;"></span>Pagado</div>
            <div><span style="display: inline-block; width: 12px; height: 12px; background: #f59e0b; border-radius: 2px; margin-right: 4px;"></span>Pendiente</div>
        </div>
        <p style="font-size: 10px; color: #999;">💡 Haz clic en un evento para ver detalles</p>
        """, unsafe_allow_html=True)
    
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
        
        # Create a nice details container
        col_details_left, col_details_right = st.columns([2, 1])
        
        with col_details_left:
            mostrar_detalles_reserva(reserva_id)
        
        with col_details_right:
            if st.button("✕ Cerrar Detalles", key="btn_cerrar_detalles", use_container_width=True, type="secondary"):
                st.session_state.mostrar_detalles_reserva = False
                st.session_state.reserva_seleccionada_id = None
                st.rerun()
    else:
        st.info("📌 Haz clic en un evento del calendario para ver detalles y opciones")


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

    ids_reservas = [r[0] for r in reservas]
    reserva_id_guardada = st.session_state.get("reserva_seleccionada_id")
    index_inicial = ids_reservas.index(reserva_id_guardada) if reserva_id_guardada in ids_reservas else 0

    reserva_id = st.selectbox(
        "Reserva",
        ids_reservas,
        index=index_inicial,
        format_func=lambda rid: next(
            f"{r[5].strftime('%d-%m %H:%M') if hasattr(r[5], 'strftime') else r[5]} - {r[1]} ({r[2]})"
            for r in reservas
            if r[0] == rid
        ),
    )
    reserva = next(r for r in reservas if r[0] == reserva_id)
    st.session_state.reserva_seleccionada_id = reserva_id

    with st.form("editar_reserva_calendario"):
        servicio_idx = servicio_options.index(reserva[3]) if reserva[3] in servicio_options else 0
        barbero_idx = barbero_options.index(reserva[2]) if reserva[2] in barbero_options else 0
        nombre_editado = st.text_input("Cliente", value=reserva[1])
        servicio_editado = st.selectbox("Servicio", servicio_options, index=servicio_idx, key="agenda_servicio_editado")
        barbero_editado = st.selectbox("Barbero", barbero_options, index=barbero_idx, key="agenda_barbero_editado")
        inicio_editado = st.datetime_input("Inicio", value=reserva[5], key="agenda_inicio_editado")
        fin_editado = st.datetime_input("Fin", value=reserva[6], key="agenda_fin_editado")

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
            "**Modo sin base de datos** — No hay conexión PostgreSQL disponible. "
            "Inicio de sesión, registro, reservas y sincronización de agenda están desactivados. "
            "Puedes revisar la interfaz; configura `DATABASE_URL` o `SUPABASE_DB_URL` para el modo completo."
        )


# ================= MÉTRICAS HELPERS =================

def calcular_metricas_header(barberia_id):
    """Calculate quick dashboard header metrics for today."""
    if not barberia_id or not st.session_state.get("db_available", True):
        return 0, 0, 0
    
    try:
        hoy = datetime.now().date()
        
        # Single query for all today's metrics
        metrics = fetch_one(
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
def calcular_metricas_cliente(barberia_id, usuario):
    """Fast cached client metrics with optimized queries."""
    if not barberia_id or not st.session_state.get("db_available", True):
        return 0, 0, 0
    
    try:
        # Single query for all metrics
        hoy = datetime.now().date()
        metrics = fetch_one(
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
def calcular_metricas_barbero(barberia_id, usuario):
    """Fast cached barber metrics with optimized queries."""
    if not barberia_id or not st.session_state.get("db_available", True):
        return 0, 0, 0
    
    try:
        # Single query for all metrics
        hoy = datetime.now().date()
        metrics = fetch_one(
            """
            SELECT 
                COUNT(*) as total_reservas,
                COUNT(CASE WHEN fecha = %s THEN 1 END) as hoy_reservas,
                COALESCE(SUM(CASE WHEN pagado = TRUE THEN monto ELSE precio END), 0) as total_ingresos
            FROM reservas 
            WHERE barberia_id = %s AND barbero = %s
            """,
            (hoy, barberia_id, usuario),
        )
        
        if metrics:
            return metrics[0], metrics[1], metrics[2]
        return 0, 0, 0
    except Exception as e:
        logger.exception("Error calculando métricas barbero")
        return 0, 0, 0


@st.cache_data(ttl=45)
def calcular_metricas_admin(barberia_id):
    """Fast cached admin metrics with optimized queries."""
    if not barberia_id or not st.session_state.get("db_available", True):
        return 0, 0, 0, 0
    
    try:
        hoy = datetime.now().date()
        
        # Single query for all metrics
        metrics = fetch_one(
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
def calcular_metricas_super_admin(barberia_id):
    """Fast cached super admin metrics with optimized queries."""
    if not st.session_state.get("db_available", True):
        return 0, 0, 0, 0, 0
    
    try:
        hoy = datetime.now().date()
        
        # Single query for all global metrics
        metrics = fetch_one(
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


# ================= BOOKING WITHOUT LOGIN =================

def show_reserva_cliente():
    """Show booking form for unauthenticated clients."""
    st.markdown("### 📅 Reservar Cita")
    
    default_barberia_id = st.session_state.get("default_barberia_id")
    
    if not default_barberia_id:
        st.error("❌ No hay barbería disponible. Por favor, registra una barbería primero.")
        return
    
    db_ok = st.session_state.get("db_available", True)
    if not db_ok:
        st.warning("⚠️ No hay base de datos: no puedes crear reservas en modo demo.")
        return
    
    with st.container(border=True):
        st.markdown("#### Completa el formulario para reservar tu cita")
        
        with st.spinner("⏳ Cargando barberos disponibles..."):
            barber_list = listar_usuarios_barberos(default_barberia_id)
            barber_opts = [x[0] for x in barber_list] if barber_list else list(barberos.keys())
        
        with st.form("form_reserva_sin_login"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("👤 Nombre", placeholder="Tu nombre completo")
            with col2:
                telefono = st.text_input("📱 Teléfono", placeholder="Tu número de teléfono")
            
            col3, col4 = st.columns(2)
            with col3:
                barbero_sel = st.selectbox("💇 Barbero", barber_opts, key="cliente_barbero_sin_login")
            with col4:
                servicio_sel = st.selectbox("✂️ Servicio", list(servicios.keys()), key="cliente_servicio_sin_login")
            
            col5, col6 = st.columns(2)
            with col5:
                fecha_sel = st.date_input("📅 Fecha", key="cliente_fecha_sin_login")
            with col6:
                hora_sel = st.time_input("🕐 Hora", value=datetime.strptime("10:00", "%H:%M").time(), key="cliente_hora_sin_login")
            
            enviar = st.form_submit_button("✅ Reservar Cita", use_container_width=True)
        
        if enviar:
            if not nombre or not nombre.strip():
                st.error("❌ Por favor, ingresa tu nombre.")
                return
            
            if not telefono or not telefono.strip():
                st.error("❌ Por favor, ingresa tu teléfono.")
                return
            
            with st.spinner("⏳ Procesando reserva..."):
                duracion = servicios[servicio_sel]["duracion"]
                precio = servicios[servicio_sel]["precio"]
                
                reserva_id = insertar_reserva_con_fecha_hora(
                    default_barberia_id,
                    nombre.strip(),
                    barbero_sel,
                    servicio_sel,
                    fecha_sel,
                    hora_sel,
                    precio,
                    duracion,
                )
                
                if reserva_id:
                    # Send WhatsApp confirmation
                    try:
                        inicio_msg = datetime.combine(fecha_sel, hora_sel)
                        mensaje = construir_mensaje_reserva(
                            nombre.strip(), inicio_msg, barbero_sel, servicio_sel
                        )
                        enviar_whatsapp_twilio(telefono.strip(), mensaje)
                    except Exception as exc:
                        logger.exception("Error al enviar WhatsApp: %s", exc)
                    
                    st.success("✅ Reserva creada correctamente")
                    st.markdown("---")
                    
                    # Generate payment link
                    st.markdown("### 💳 Completar Pago")
                    url_pago = crear_pago_mercadopago(
                        reserva_id,
                        precio,
                        f"Reserva barbería - {servicio_sel}"
                    )
                    
                    if url_pago:
                        st.info("📌 Por favor, completa el pago para confirmar tu cita.")
                        st.link_button("💳 Pagar ahora", url_pago, use_container_width=True)
                    else:
                        st.warning("⚠️ No se pudo generar el enlace de pago. Tu reserva se ha creado sin pago.")


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

    st.session_state["db_available"] = is_db_available()
    db_ok = st.session_state["db_available"]
    render_modo_sin_db_banner()

    st.write("🔵 APP START")

    # ===== LOGIN SCREEN =====
    if not st.session_state.user:
        st.set_page_config(layout="wide")
        col_center = st.columns([1, 2, 1])
        with col_center[1]:
            st.markdown("# 💈 Barbería Leveling")
            st.markdown("**Tu plataforma de reservas profesional**")
            st.markdown("---")

            if not db_ok:
                st.warning(
                    "⚠️ Inicio de sesión y registro están desactivados: no hay base de datos (modo demo)."
                )

            opcion = st.radio("Selecciona una opción", [
                "🔑 Iniciar sesión",
                "✨ Registrar barbería",
                "📅 Reservar cita",
            ], key="login_option")

            if opcion == "🔑 Iniciar sesión":
                st.markdown("### Accede a tu cuenta")
                with st.form("login_form"):
                    usuario = st.text_input("👤 Usuario", placeholder="Tu usuario")
                    password = st.text_input("🔐 Contraseña", type="password", placeholder="Tu contraseña")
                    entrar = st.form_submit_button("✅ Entrar", use_container_width=True, disabled=not db_ok)

                if entrar:
                    try:
                        with st.spinner("🔍 Verificando credenciales..."):
                            user = login(usuario, password)
                            if user:
                                # Store session state before rerun
                                st.session_state.user = user
                                # Normalize and store role immediately
                                raw_rol = user[3] if len(user) > 3 else None
                                st.session_state.rol = normalizar_rol(raw_rol)
                                nr_login = st.session_state.rol
                                st.write("🟢 LOGIN OK")
                                if nr_login == "SUPER_ADMIN":
                                    st.session_state.barberia_id = None
                                    with st.spinner("⏳ Cargando barberías..."):
                                        fb = fetch_one("SELECT id FROM barberias ORDER BY id LIMIT 1")
                                    st.session_state.barberia_context_id = fb[0] if fb else None
                                    st.session_state.super_admin_all_barberias = False
                                else:
                                    bid_u = user[5] if len(user) > 5 else None
                                    st.session_state.barberia_id = bid_u or default_barberia_id
                                    st.session_state.barberia_context_id = st.session_state.barberia_id
                                st.success("✅ ¡Bienvenido!")
                                st.rerun()
                            else:
                                st.error("❌ Datos incorrectos. Intenta nuevamente.")
                    except Exception as e:
                        logger.exception("Error en login")
                        st.error(f"Error en login: {str(e)}")
            
            elif opcion == "📅 Reservar cita":
                show_reserva_cliente()

        # CRITICAL: Stop execution here ONLY when NOT logged in
        st.stop()

    # ===== MAIN APP (Only runs if logged in) =====
    st.write("🟡 MAIN APP STARTING")
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
        st.markdown("## 💈 Barbería Leveling")
        st.markdown(f"**{usuario or 'Invitado'}**")
        st.caption(f"Rol: {nr.replace('_', ' ')}")

        barberia_name = "Principal"
        if barberia_id:
            if "barberia_name" not in st.session_state or st.session_state.get("cached_barberia_id") != barberia_id:
                with st.spinner("⏳ Cargando barbería..."):
                    b_name_row = fetch_one("SELECT nombre FROM barberias WHERE id = %s", (barberia_id,))
                st.session_state.barberia_name = b_name_row[0] if b_name_row else "Principal"
                st.session_state.cached_barberia_id = barberia_id
            barberia_name = st.session_state.barberia_name
        st.markdown(f"**Barbería:** {barberia_name}")
        st.markdown("---")

        if nr == "SUPER_ADMIN":
            st.markdown("### 🏢 Contexto")
            try:
                if "barberias_list" not in st.session_state:
                    with st.spinner("⏳ Cargando barberías..."):
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

        st.markdown("### 🗺️ Navegación")
        nav_opts = ["Dashboard", "Agenda", "Barberos", "Configuración"]
        if nr == "CLIENTE":
            nav_opts = ["Dashboard", "Agenda"]
        seccion = st.radio("", nav_opts, key=f"nav_main_{nr}", label_visibility="collapsed")

        st.markdown("---")
        if st.button("🚪 Cerrar sesión", use_container_width=True, type="secondary"):
            st.session_state.user = None
            st.session_state.barberia_id = None
            st.session_state.barberia_context_id = None
            st.rerun()

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
            st.markdown("## 📊 Mi Panel")
            
            if not db_ok:
                st.info("📊 Métricas no disponibles sin base de datos.")
            else:
                with st.spinner("⏳ Cargando métricas..."):
                    total_hoy, pagadas_hoy, pendientes_hoy = calcular_metricas_header(barberia_id)
                    total_reservas, hoy_reservas, _ = calcular_metricas_cliente(barberia_id, usuario)
                    num_barberos_cached = len(listar_usuarios_barberos(barberia_id))
                
                # Dashboard header metrics
                col1, col2, col3 = st.columns(3, gap="large")
                col1.metric("📅 Reservas Hoy", total_hoy, delta=None)
                col2.metric("✅ Pagadas", pagadas_hoy, delta=None)
                col3.metric("⏳ Pendientes", pendientes_hoy, delta=None)
                st.markdown("---")
                
                render_dashboard_cards(4, [
                    {"label": "📅 Total Reservas", "value": total_reservas},
                    {"label": "🎯 Reservas Hoy", "value": hoy_reservas},
                    {"label": "💰 Ingresos", "value": "$0"},
                    {"label": "👥 Barberos", "value": num_barberos_cached},
                ])
                st.markdown("---")
                st.markdown("### 💡 Información Útil")
                col_tip1, col_tip2 = st.columns(2, gap="large")
                with col_tip1:
                    st.success("✨ Obtén descuento cada 5 cortes")
                with col_tip2:
                    st.info("⏰ Cancela con 1 hora de anticipación")

        elif seccion == "Agenda":
            st.markdown("## 📅 Mi Agenda")

            tab_calendario, tab_crear, tab_lista = st.tabs([
                "📅 Calendario",
                "✨ Nueva Reserva",
                "📋 Listado"
            ])

            # TAB: CALENDARIO
            with tab_calendario:
                if db_ok:
                    with st.spinner("⏳ Cargando tu calendario..."):
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
                        st.info("📭 No tienes reservas aún. ¡Crea una!")
                else:
                    st.warning("Calendario no disponible sin base de datos.")

            # TAB: CREAR NUEVA
            with tab_crear:
                with st.container(border=True):
                    st.markdown("### ✨ Nueva Reserva")
                    if not db_ok:
                        st.warning("No hay base de datos: no puedes crear reservas en modo demo.")
                    else:
                        with st.spinner("⏳ Cargando barberos disponibles..."):
                            barber_opts = [x[0] for x in listar_usuarios_barberos(barberia_id)] or list(barberos.keys())
                        with st.form("form_reserva_cliente"):
                            col1, col2 = st.columns(2)
                            with col1:
                                barbero_sel = st.selectbox("💇 Barbero", barber_opts, key="cliente_barbero_sel")
                            with col2:
                                servicio_sel = st.selectbox("✂️ Servicio", list(servicios.keys()), key="cliente_servicio_sel")
                            
                            col3, col4 = st.columns(2)
                            with col3:
                                fecha_sel = st.date_input("📅 Fecha", key="cliente_fecha_sel")
                            with col4:
                                hora_sel = st.time_input("🕐 Hora", value=datetime.strptime("10:00", "%H:%M").time(), key="cliente_hora_sel")
                            
                            st.caption(f"👤 Cliente: **{usuario}**")
                            enviar = st.form_submit_button("✅ Reservar", use_container_width=True)

                        if enviar:
                            with st.spinner("⏳ Procesando reserva..."):
                                duracion = servicios[servicio_sel]["duracion"]
                                precio = servicios[servicio_sel]["precio"]
                                ok = insertar_reserva_con_fecha_hora(
                                    barberia_id,
                                    usuario,
                                    barbero_sel,
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
                                            usuario, inicio_msg, barbero_sel, servicio_sel
                                        )
                                        try:
                                            enviar_whatsapp_twilio(telefono_cliente, mensaje)
                                        except Exception as exc:
                                            logger.exception("Error al ejecutar el envio de WhatsApp: %s", exc)
                                    st.success("✅ Reserva creada exitosamente")
                                    st.rerun()

            # TAB: LISTADO
            with tab_lista:
                st.markdown("### 📋 Tus Reservas")
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
                        st.info("📭 Aún no tienes reservas. ¡Crea una!")

    # ================= BARBERO =================
    elif nr == "BARBERO":
        if not barberia_id:
            st.warning("No hay barberia asociada a la sesión.")
            st.stop()

        if seccion == "Dashboard":
            st.markdown("## 📊 Mi Panel · Barbero")
            
            if not db_ok:
                st.info("📊 Métricas no disponibles sin base de datos.")
            else:
                with st.spinner("⏳ Cargando métricas..."):
                    total_hoy, pagadas_hoy, pendientes_hoy = calcular_metricas_header(barberia_id)
                    total_reservas, hoy_reservas, total_ingresos = calcular_metricas_barbero(barberia_id, usuario)
                
                # Dashboard header metrics
                col1, col2, col3 = st.columns(3, gap="large")
                col1.metric("📅 Reservas Hoy", total_hoy, delta=None)
                col2.metric("✅ Pagadas", pagadas_hoy, delta=None)
                col3.metric("⏳ Pendientes", pendientes_hoy, delta=None)
                st.markdown("---")
                
                render_dashboard_cards(3, [
                    {"label": "✂️ Total Cortes", "value": total_reservas},
                    {"label": "🎯 Hoy", "value": hoy_reservas},
                    {"label": "💰 Ingresos", "value": f"${total_ingresos}"},
                ])
                
                st.markdown("---")
                with st.spinner("⏳ Cargando próximas citas..."):
                    reservas_barbero = listar_reservas_filtradas(barberia_id, "BARBERO", usuario)
                    hoy = datetime.now().date()
                    hoy_reservas_list = [r for r in reservas_barbero if r[3] == hoy]
                
                if hoy_reservas_list:
                    st.markdown("### 📌 Próximas Citas (Hoy)")
                    for r in hoy_reservas_list[:5]:
                        hora_str = r[4].strftime("%H:%M") if hasattr(r[4], "strftime") else str(r[4])
                        cliente_str = r[5] or r[6]
                        st.caption(f"🕐 {hora_str} - {cliente_str} ({r[2]})")

        elif seccion == "Agenda":
            st.markdown("## 📅 Mi Agenda")
            
            tab_cal, tab_crear, tab_lista = st.tabs([
                "📆 Calendario",
                "➕ Crear/Editar",
                "📋 Listado"
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
                st.markdown("### 📋 Mis Reservas")
                
                # Toggle between card and calendar view
                view_type = st.radio(
                    "Modo de vista",
                    ["📇 Tarjetas", "📅 Calendario"],
                    horizontal=True,
                    key="barbero_view_type"
                )
                
                if not db_ok:
                    st.info("Tabla no disponible sin base de datos.")
                else:
                    with st.spinner("⏳ Cargando tus reservas..."):
                        rows_bar = listar_reservas_filtradas(barberia_id, "BARBERO", usuario)
                    
                    if rows_bar:
                        if view_type == "📇 Tarjetas":
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
                            st.caption("💡 Vista de calendario en formato semanal - usa las flechas para navegar")
                    else:
                        st.info("📭 No hay reservas")

        elif seccion == "Barberos":
            st.markdown("## 👥 Equipo")
            st.info("👨‍💼 Solo el administrador de la barbería gestiona el equipo de barberos.")

        elif seccion == "Configuración":
            st.markdown("## ⚙️ Configuración")
            st.info("✨ Preferencias y ajustes próximamente.")

    # ================= ADMIN =================
    elif nr == "ADMIN":
        if not barberia_id:
            st.warning("No hay barberia asociada a la sesión.")
            st.stop()

        if seccion == "Dashboard":
            st.markdown("## 📊 Panel Administrativo")
            
            if not db_ok:
                st.info("📊 Métricas no disponibles sin base de datos.")
            else:
                with st.spinner("⏳ Cargando métricas..."):
                    total_hoy, pagadas_hoy, pendientes_hoy = calcular_metricas_header(barberia_id)
                    total_reservas, hoy_reservas, total_ingresos, num_barberos = calcular_metricas_admin(barberia_id)
                
                # Dashboard header metrics
                col1, col2, col3 = st.columns(3, gap="large")
                col1.metric("📅 Reservas Hoy", total_hoy, delta=None)
                col2.metric("✅ Pagadas", pagadas_hoy, delta=None)
                col3.metric("⏳ Pendientes", pendientes_hoy, delta=None)
                st.markdown("---")
                
                render_dashboard_cards(4, [
                    {"label": "📅 Total Reservas", "value": total_reservas},
                    {"label": "🎯 Hoy", "value": hoy_reservas},
                    {"label": "💰 Ingresos (Pagadas)", "value": f"${total_ingresos}"},
                    {"label": "👥 Barberos", "value": num_barberos},
                ])
                
                st.markdown("---")
                with st.spinner("⏳ Cargando próximas citas..."):
                    todas_reservas = fetch_all(
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
                    st.markdown("### 📌 Próximas Citas (Hoy)")
                    for r in hoy_reservas_list[:5]:
                        hora_str = r[4].strftime("%H:%M") if hasattr(r[4], "strftime") else str(r[4])
                        cliente_str = r[5] or r[6]
                        st.caption(f"🕐 {hora_str} - {cliente_str} con {r[1]} ({r[2]})")

        elif seccion == "Agenda":
            st.markdown("## 📅 Agenda")
            
            # Fetch eventos for calendar
            eventos = []
            if db_ok:
                try:
                    eventos = obtener_reservas()
                except Exception as e:
                    logger.exception("Error fetching eventos for ADMIN")
                    eventos = []
            
            tab_cal, tab_crear, tab_lista, tab_ingresos = st.tabs([
                "📆 Calendario",
                "➕ Crear/Editar",
                "📋 Reservas",
                "💰 Ingresos"
            ])
            
            # TAB: CALENDARIO
            with tab_cal:
                if db_ok:
                    with st.spinner("⏳ Cargando calendario..."):
                        render_calendario_multi_barbero(eventos, read_only=not db_ok)
                else:
                    st.warning("Calendario no disponible sin base de datos (modo demo).")
            
            # TAB: CREAR/EDITAR
            with tab_crear:
                render_gestion_agenda()
            
            # TAB: RESERVAS
            with tab_lista:
                st.markdown("### 📋 Reservas")
                
                # Toggle between card and calendar view
                col_view1, col_view2 = st.columns(2)
                with col_view1:
                    view_type = st.radio(
                        "Modo de vista",
                        ["📇 Tarjetas", "📅 Calendario"],
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
                        if view_type == "📇 Tarjetas":
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
                            st.caption("💡 Vista de calendario en formato semanal - usa las flechas para navegar")
                    else:
                        st.info("📭 No hay reservas")
            
            # TAB: INGRESOS
            with tab_ingresos:
                st.markdown("### 💰 Ingresos")
                if db_ok:
                    with st.spinner("Cargando datos..."):
                        total_row = fetch_one(
                            "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND pagado = TRUE",
                            (barberia_id,),
                        )
                        total = total_row[0] if total_row and total_row[0] else 0
                    st.metric("💵 Ingresos Totales (Pagado)", f"${total}")
                    
                    st.markdown("---")
                    st.markdown("#### 📊 Desglose por Barbero")
                    with st.spinner("⏳ Cargando desglose..."):
                        barberos_list = listar_usuarios_barberos(barberia_id)
                        for barbero_name, _ in barberos_list:
                            barbero_ingresos = fetch_one(
                                "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND barbero = %s AND pagado = TRUE",
                                (barberia_id, barbero_name),
                            )
                            ingreso = barbero_ingresos[0] if barbero_ingresos and barbero_ingresos[0] else 0
                            st.caption(f"💇 {barbero_name}: ${ingreso}")

        elif seccion == "Barberos":
            st.markdown("## 👥 Gestión de Barberos")
            
            with st.container(border=True):
                st.markdown("### ➕ Nuevo Barbero")
                with st.form("crear_barbero_admin"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nu = st.text_input("👤 Usuario", placeholder="Ej: Andrea")
                    with col2:
                        np = st.text_input("🔐 Contraseña", type="password")
                    if st.form_submit_button("✅ Crear Barbero", use_container_width=True):
                        with st.spinner("⏳ Creando barbero..."):
                            if registrar(nu, np, "BARBERO", barberia_id=barberia_id):
                                st.success("✅ Barbero creado exitosamente")
                                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📋 Barberos Registrados")
            with st.spinner("⏳ Cargando barberos..."):
                barberos_data = listar_usuarios_barberos(barberia_id)
            if barberos_data:
                st.dataframe(
                    [{"👤 Usuario": r[0], "👥 Rol": r[1]} for r in barberos_data],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("📭 No hay barberos registrados aún")

        elif seccion == "Configuración":
            st.markdown("## ⚙️ Configuración")
            st.info("✨ Datos de la barbería y preferencias próximamente.")

    # ================= SUPER_ADMIN =================
    elif nr == "SUPER_ADMIN":
        if seccion == "Dashboard":
            st.markdown("## 📊 Panel Global (Super Admin)")
            
            if not db_ok:
                st.info("📊 Métricas no disponibles sin base de datos.")
            else:
                with st.spinner("⏳ Cargando métricas globales..."):
                    total_hoy, pagadas_hoy, pendientes_hoy = calcular_metricas_header(bid_ctx) if bid_ctx else (0, 0, 0)
                    num_barberias, num_usuarios, num_reservas, total_ingresos, hoy_count = calcular_metricas_super_admin(bid_ctx)
                
                # Dashboard header metrics
                col1, col2, col3 = st.columns(3, gap="large")
                col1.metric("📅 Reservas Hoy", total_hoy, delta=None)
                col2.metric("✅ Pagadas", pagadas_hoy, delta=None)
                col3.metric("⏳ Pendientes", pendientes_hoy, delta=None)
                st.markdown("---")
                
                render_dashboard_cards(5, [
                    {"label": "🏢 Barberías", "value": num_barberias},
                    {"label": "👥 Usuarios", "value": num_usuarios},
                    {"label": "📅 Total Reservas", "value": num_reservas},
                    {"label": "🎯 Hoy", "value": hoy_count},
                    {"label": "💰 Ingresos Totales", "value": f"${total_ingresos}"},
                ])

        elif seccion == "Agenda":
            st.markdown("## 📅 Agenda Global")
            
            # Fetch eventos for calendar
            eventos = []
            if db_ok:
                try:
                    eventos = obtener_reservas()
                except Exception as e:
                    logger.exception("Error fetching eventos for SUPER_ADMIN")
                    eventos = []
            
            tab_cal, tab_crear, tab_lista, tab_ingresos = st.tabs([
                "📆 Calendario",
                "➕ Crear/Editar",
                "📋 Reservas",
                "💰 Ingresos"
            ])
            
            # TAB: CALENDARIO
            with tab_cal:
                if db_ok:
                    with st.spinner("⏳ Cargando calendario..."):
                        render_calendario_multi_barbero(eventos, read_only=not db_ok)
                else:
                    st.warning("Calendario no disponible sin base de datos (modo demo).")
            
            # TAB: CREAR/EDITAR
            with tab_crear:
                render_gestion_agenda()

            # TAB: RESERVAS
            with tab_lista:
                st.markdown("### 📋 Reservas")
                
                # Toggle between card and calendar view
                view_type = st.radio(
                    "Modo de vista",
                    ["📇 Tarjetas", "📅 Calendario"],
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
                    with st.spinner("⏳ Cargando reservas..."):
                        rows_su = listar_reservas_filtradas(
                            bid_ctx, "SUPER_ADMIN", usuario, filtro_barbero=filtro_su
                        )
                    if rows_su:
                        if view_type == "📇 Tarjetas":
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
                            st.caption("💡 Vista de calendario en formato semanal - usa las flechas para navegar")
                    else:
                        st.info("📭 No hay reservas")

            # TAB: INGRESOS
            with tab_ingresos:
                st.markdown("### 💰 Ingresos (Barbería Activa)")
                if db_ok and bid_ctx:
                    with st.spinner("⏳ Cargando datos de ingresos..."):
                        total_row = fetch_one(
                            "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND pagado = TRUE",
                            (bid_ctx,),
                        )
                        total = total_row[0] if total_row and total_row[0] else 0
                    st.metric("💵 Ingresos Totales (Pagado)", f"${total}")
                    
                    st.markdown("---")
                    st.markdown("#### 📊 Desglose por Barbero")
                    with st.spinner("⏳ Cargando desglose..."):
                        barberos_list = listar_usuarios_barberos(bid_ctx)
                        for barbero_name, _ in barberos_list:
                            barbero_ingresos = fetch_one(
                                "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND barbero = %s AND pagado = TRUE",
                                (bid_ctx, barbero_name),
                            )
                            ingreso = barbero_ingresos[0] if barbero_ingresos and barbero_ingresos[0] else 0
                            st.caption(f"💇 {barbero_name}: ${ingreso}")
                else:
                    st.info("Selecciona una barbería para ver ingresos")

        elif seccion == "Barberos":
            st.markdown("## 👥 Barberos (Contexto)")
            if bid_ctx:
                with st.spinner("⏳ Cargando barberos..."):
                    barberos_data = listar_usuarios_barberos(bid_ctx)
                if barberos_data:
                    st.dataframe(
                        [{"👤 Usuario": r[0], "👥 Rol": r[1]} for r in barberos_data],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("📭 No hay barberos registrados")
            else:
                st.info("🏢 Selecciona una barbería en la barra lateral.")

        elif seccion == "Configuración":
            st.markdown("## ⚙️ Configuración Global")
            st.info("✨ Parámetros de plataforma próximamente.")

    else:
        st.error(f"Vista no disponible para el rol: {nr}")

except Exception as e:
    logger.exception("Unhandled exception in Streamlit app")
    st.error(f"Error en la aplicación: {str(e)}")
