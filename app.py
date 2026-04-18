import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import logging
import os
import socket
from urllib.parse import urlparse
from dotenv import load_dotenv
import bcrypt
import psycopg2
from whatsapp import enviar_whatsapp as enviar_whatsapp_twilio

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


def get_connection(*, notify_missing_url: bool = True):
    global _db_url_missing_notified
    database_url = get_database_url()

    if not database_url:
        message = (
            "DATABASE_URL o SUPABASE_DB_URL no está configurada. "
            "Define una de estas variables de entorno en el sistema o en la configuración "
            "de despliegue (sin hardcodear credenciales en el código)."
        )
        logger.error(message)
        if notify_missing_url and not _db_url_missing_notified:
            _db_url_missing_notified = True
            st.error(message)
        return None

    try:
        database_url = database_url.strip()

        if "[YOUR-PASSWORD]" in database_url:
            st.error("You must replace [YOUR-PASSWORD] with your real Supabase password")
            return None

        parsed = urlparse(database_url)
        if parsed.scheme not in ("postgresql", "postgres"):
            st.error("DATABASE_URL must start with postgresql:// (Supabase Postgres)")
            return None

        host = parsed.hostname
        port = parsed.port or 5432
        dbname = (parsed.path or "").lstrip("/")

        if not host:
            st.error("DATABASE_URL is invalid: missing hostname")
            return None
        if not dbname:
            st.error("DATABASE_URL is invalid: missing database name in path (e.g. /postgres)")
            return None

        masked = _masked_postgres_url(parsed)
        logger.info("Postgres target: %s", masked)

        try:
            socket.getaddrinfo(host, port)
        except socket.gaierror:
            st.error(
                "Host cannot be resolved. Verify Supabase URL or try pooler connection"
            )
            return None

        return psycopg2.connect(
            database_url,
            sslmode="require",
            connect_timeout=5,
            options="-c statement_timeout=8000",
        )
    except psycopg2.OperationalError as e:
        logger.exception("Error al conectar con PostgreSQL (OperationalError)")
        st.error(str(e))
        return None
    except Exception as e:
        logger.exception("Error al conectar con PostgreSQL")
        st.error(str(e))
        return None


def is_db_available():
    """True if a PostgreSQL connection can be opened; closes the probe connection."""
    conn = None
    try:
        conn = get_connection(notify_missing_url=False)
        return conn is not None
    except Exception:
        logger.info("Base de datos no disponible (fallo de conexión).", exc_info=True)
        return False
    finally:
        if conn is not None:
            conn.close()

def execute_query(query, params=None, fetch=None):
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
            conn.rollback()
        logger.exception("Error en base de datos")
        st.error(str(e))
        return None
    finally:
        if conn:
            conn.close()


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

            # Add UNIQUE constraint on usuario if not exists
            try:
                # Check if constraint exists
                cur.execute(
                    """
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'usuarios_usuario_unique'
                    AND conrelid = (SELECT oid FROM pg_class WHERE relname = 'usuarios');
                    """
                )
                constraint_exists = cur.fetchone()
                
                if not constraint_exists:
                    cur.execute(
                        "ALTER TABLE usuarios ADD CONSTRAINT usuarios_usuario_unique UNIQUE (usuario);"
                    )
                    logger.info("✅ Restricción UNIQUE en 'usuario' añadida")
                else:
                    logger.info("✅ Restricción UNIQUE en 'usuario' ya existe")
                
                conn.commit()
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error creando restricción UNIQUE en 'usuario': {e}")
                st.error(f"Error creando restricción UNIQUE en 'usuario': {e}")

            # Index on usuarios
            try:
                cur.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_barberia ON usuarios(barberia_id);")
                conn.commit()
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
                conn.commit()
                logger.info("✅ Índice 'idx_reservas_barberia' creado o ya existe")
            except Exception as e:
                conn.rollback()
                all_ok = False
                logger.error(f"Error creando índice 'idx_reservas_barberia': {e}")
                st.error(f"Error creando índice 'idx_reservas_barberia': {e}")

            # Optional columns
            try:
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS cliente TEXT;")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS fecha DATE;")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS hora TIME;")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS estado TEXT DEFAULT 'activo';")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS pagado BOOLEAN NOT NULL DEFAULT FALSE;")
                cur.execute("ALTER TABLE reservas ADD COLUMN IF NOT EXISTS monto INTEGER;")
                cur.execute("UPDATE reservas SET monto = precio WHERE monto IS NULL;")
                conn.commit()
                logger.info("✅ Columnas opcionales en 'reservas' añadidas o actualizadas")
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
        st.error(str(e))
    finally:
        if conn:
            conn.close()


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
    if rol is None:
        return ""
    s = str(rol).strip()
    if not s:
        return ""
    low = s.lower()
    if low in _ROL_LEGACY:
        return _ROL_LEGACY[low]
    return s.upper()


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

    logger.info(f"✅ Login exitoso para: {usuario}")
    return user
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
            st.sidebar.error("SUPER_ADMIN no se pudo crear")
            return False
        except Exception as e:
            st.sidebar.error(f"Seed error: {str(e)}")
            return False

    except Exception as e:
        if conn:
            conn.rollback()
        logger.exception("❌ Error en seed_default_data")
        st.sidebar.error(f"Seed error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()


try:
    ensure_database_tables()
    
    st.sidebar.write("Running seed...")
    seed_result = seed_default_data()
    
    if seed_result:
        st.sidebar.success("SUPER_ADMIN listo")
    elif seed_result is False:
        st.sidebar.error("❌ Seed falló - SUPER_ADMIN NO garantizado")
    
    default_barberia_id = inicializar_barberia()
except Exception as e:
    logger.exception("Error inesperado inicializando la base de datos")
    st.error(str(e))
    default_barberia_id = None


def listar_usuarios_barberos(barberia_id):
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

def obtener_reservas_raw(barbero_filtro=None):
    if not st.session_state.get("db_available", True):
        return []

    user = st.session_state.get("user")
    if not user:
        return []

    rol = normalizar_rol(user[3])
    uid = user[1]
    bid = effective_barberia_id()
    super_all = rol == "SUPER_ADMIN" and st.session_state.get("super_admin_all_barberias")

    if not super_all and not bid:
        return []

    sql = """
        SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id
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
    try:
        return fetch_all(sql, tuple(params)) or []
    except Exception:
        logger.exception("obtener_reservas_raw")
        return []


def construir_eventos_calendario(reservas):
    """Construye eventos del calendario con información extendida."""
    eventos = []

    for r in reservas:
        es_bloqueo = r[1] == "BLOQUEADO" or r[3] == "Bloqueo"
        cliente = r[1]
        barbero = r[2]
        servicio = r[3]
        fecha_inicio = r[5]
        fecha_fin = r[6]
        
        # Crear título más informativo
        if es_bloqueo:
            titulo = "🚫 BLOQUEADO"
        else:
            titulo = f"👤 {cliente} - {servicio}"
        
        eventos.append({
            "id": str(r[0]),
            "title": titulo,
            "start": fecha_inicio.isoformat() if hasattr(fecha_inicio, "isoformat") else fecha_inicio,
            "end": fecha_fin.isoformat() if hasattr(fecha_fin, "isoformat") else fecha_fin,
            "color": "#666666" if es_bloqueo else barberos.get(barbero, "#999999"),
            "borderColor": "#000000",
            "textColor": "#FFFFFF",
            "extendedProps": {
                "id": r[0],
                "nombre": cliente,
                "barbero": barbero,
                "servicio": servicio,
                "precio": r[4],
                "bloqueo": es_bloqueo,
                "inicio": fecha_inicio,
                "fin": fecha_fin,
            },
        })

    return eventos


def mostrar_detalles_reserva(reserva_id):
    """Muestra detalles detallados de una reserva en un expander."""
    reserva = obtener_reserva_por_id(reserva_id)
    if not reserva:
        st.error("Reserva no encontrada")
        return
    
    with st.container(border=True):
        st.markdown("### 📋 Detalles de la Reserva")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🆔 ID:** {reserva[0]}")
            st.markdown(f"**👤 Cliente:** {reserva[1]}")
            st.markdown(f"**💇 Barbero:** {reserva[2]}")
        
        with col2:
            st.markdown(f"**✂️ Servicio:** {reserva[3]}")
            st.markdown(f"**💰 Precio:** ${reserva[4]}")
            st.markdown(f"**🆔 Barbería ID:** {reserva[7]}")
        
        st.markdown("---")
        st.markdown("**⏰ Horario:**")
        col_time1, col_time2 = st.columns(2)
        with col_time1:
            inicio_str = reserva[5].strftime("%d-%m-%Y %H:%M") if hasattr(reserva[5], "strftime") else str(reserva[5])
            st.caption(f"🕐 Inicio: {inicio_str}")
        with col_time2:
            fin_str = reserva[6].strftime("%d-%m-%Y %H:%M") if hasattr(reserva[6], "strftime") else str(reserva[6])
            st.caption(f"🕑 Fin: {fin_str}")
        
        return reserva


def obtener_reservas(barbero=None):
    return construir_eventos_calendario(obtener_reservas_raw(barbero))


def obtener_reserva_por_id(reserva_id):
    try:
        return fetch_one(
            """
            SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id, cliente
            FROM reservas
            WHERE id = %s
            """,
            (reserva_id,),
        )
    except Exception:
        logger.exception("obtener_reserva_por_id")
        return None


def obtener_reserva(reserva_id, barberia_id):
    try:
        return fetch_one(
            """
            SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id, cliente
            FROM reservas
            WHERE id = %s AND barberia_id = %s
            """,
            (reserva_id, barberia_id),
        )
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
                st.error("Ese horario ya está ocupado para el barbero seleccionado.")
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
        st.error(str(e))
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
                st.error("Horario no disponible")
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
                st.error("Horario no disponible")
                return False

            cur.execute(
                """
                INSERT INTO reservas (
                    nombre, barbero, servicio, precio, inicio, fin, barberia_id,
                    cliente, fecha, hora, estado, monto, pagado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)
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

        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        logger.exception("Error al insertar reserva (fecha/hora)")
        st.error(str(e))
        return False
    finally:
        if conn:
            conn.close()


def listar_reservas_filtradas(barberia_id_arg, rol_tag, usuario_login, filtro_barbero=None):
    """Listado con permisos: CLIENTE sus reservas; BARBERO solo su usuario en barbero; ADMIN barbería; SUPER_ADMIN todo o filtro."""
    nr = normalizar_rol(rol_tag)
    cols = (
        "id, barbero, servicio, fecha, hora, cliente, nombre, inicio, precio, estado, pagado, monto"
    )

    try:
        super_all = nr == "SUPER_ADMIN" and st.session_state.get("super_admin_all_barberias")

        if nr == "CLIENTE":
            bid = barberia_id_arg or effective_barberia_id()
            if not bid:
                return []
            return fetch_all(
                f"""
                SELECT {cols}
                FROM reservas
                WHERE barberia_id = %s
                  AND (cliente = %s OR nombre = %s)
                ORDER BY inicio DESC NULLS LAST
                """,
                (bid, usuario_login, usuario_login),
            ) or []

        if nr == "BARBERO":
            bid = barberia_id_arg or effective_barberia_id()
            if not bid:
                return []
            return fetch_all(
                f"""
                SELECT {cols}
                FROM reservas
                WHERE barberia_id = %s AND barbero = %s
                ORDER BY inicio DESC NULLS LAST
                """,
                (bid, usuario_login),
            ) or []

        if super_all:
            sql = f"SELECT {cols} FROM reservas WHERE 1=1"
            params = []
            if filtro_barbero and filtro_barbero != "Todos":
                sql += " AND barbero = %s"
                params.append(filtro_barbero)
            sql += " ORDER BY inicio DESC NULLS LAST"
            return fetch_all(sql, tuple(params)) or []

        bid = barberia_id_arg or effective_barberia_id()
        if not bid:
            return []

        sql = f"SELECT {cols} FROM reservas WHERE barberia_id = %s"
        params = [bid]
        if filtro_barbero and filtro_barbero != "Todos":
            sql += " AND barbero = %s"
            params.append(filtro_barbero)
        sql += " ORDER BY inicio DESC NULLS LAST"
        return fetch_all(sql, tuple(params)) or []

    except Exception:
        logger.exception("Error listando reservas")
        return []


def mostrar_reservas_dataframe(rows):
    if not rows:
        st.info("📭 No hay reservas para mostrar.")
        return

    display = []
    for r in rows:
        fecha_str = str(r[3]) if r[3] is not None else ""
        hora_str = str(r[4]) if r[4] is not None else ""
        cliente = r[5] or r[6]
        monto = r[11] if len(r) > 11 else r[8]
        pagado = "✅ Pagado" if (len(r) > 10 and r[10]) else "⏳ Pendiente"
        
        display.append({
            "🆔 ID": r[0],
            "💇 Barbero": r[1],
            "✂️ Servicio": r[2],
            "📅 Fecha": fecha_str,
            "🕐 Hora": hora_str,
            "👤 Cliente": cliente,
            "💰 Monto": f"${monto}" if monto else "-",
            "📊 Estado": pagado,
        })
    
    st.dataframe(display, use_container_width=True, hide_index=True)


def ui_marcar_pagado_reservas(rows, key_prefix):
    user = st.session_state.get("user")
    if not user or not rows:
        return
    nr = normalizar_rol(user[3])
    if nr == "CLIENTE":
        return

    pend = [r for r in rows if not (len(r) > 10 and r[10])]
    if not pend:
        return

    ids = [r[0] for r in pend]

    def _lab(i):
        row = next(x for x in pend if x[0] == i)
        return f"#{i} · {row[1]} · {row[7]}"

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

    ids = [r[0] for r in rows]

    def _label(i):
        row = next(x for x in rows if x[0] == i)
        return f"#{i} · {row[1]} · {row[2]} · {row[7]}"

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
    """Opciones mejoradas del calendario con mejor interactividad."""
    return {
        "initialView": initial_view,
        "editable": True,
        "selectable": True,
        "allDaySlot": False,
        "slotMinTime": "09:00:00",
        "slotMaxTime": "21:00:00",
        "height": 720,
        "contentHeight": "auto",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay",
        },
        "slotLabelInterval": "00:30:00",
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
    }


def manejar_interaccion_calendario(calendar_state):
    """Maneja interacciones del calendario: clicks, drag, resize."""
    if not isinstance(calendar_state, dict):
        return

    if not st.session_state.get("db_available", True):
        return

    # Manejo de clicks en eventos
    event_click = calendar_state.get("eventClick")
    if event_click and event_click.get("event"):
        event_id = int(event_click["event"]["id"])
        st.session_state.reserva_seleccionada_id = event_id
        st.session_state.mostrar_detalles_reserva = True

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
    """Renderiza calendario interactivo con manejo de eventos."""
    if "mostrar_detalles_reserva" not in st.session_state:
        st.session_state.mostrar_detalles_reserva = False
    
    col_cal, col_detalles = st.columns([3, 1])
    
    with col_cal:
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
    
    # Panel de detalles
    with col_detalles:
        if st.session_state.get("mostrar_detalles_reserva") and st.session_state.get("reserva_seleccionada_id"):
            reserva_id = st.session_state.get("reserva_seleccionada_id")
            mostrar_detalles_reserva(reserva_id)
            
            if st.button("✕ Cerrar", key="btn_cerrar_detalles", use_container_width=True):
                st.session_state.mostrar_detalles_reserva = False
                st.rerun()


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

def calcular_metricas_cliente(barberia_id, usuario):
    """Calcula métricas para cliente."""
    if not barberia_id or not st.session_state.get("db_available", True):
        return 0, 0, 0
    
    try:
        reservas = listar_reservas_filtradas(barberia_id, "CLIENTE", usuario)
        total = len(reservas)
        
        hoy = datetime.now().date()
        hoy_count = sum(1 for r in reservas if r[3] == hoy)
        
        return total, hoy_count, 0
    except Exception as e:
        logger.exception("Error calculando métricas cliente")
        return 0, 0, 0


def calcular_metricas_barbero(barberia_id, usuario):
    """Calcula métricas para barbero."""
    if not barberia_id or not st.session_state.get("db_available", True):
        return 0, 0, 0
    
    try:
        reservas = listar_reservas_filtradas(barberia_id, "BARBERO", usuario)
        total = len(reservas)
        
        hoy = datetime.now().date()
        hoy_count = sum(1 for r in reservas if r[3] == hoy)
        
        total_ingresos = sum(r[11] if len(r) > 11 else r[8] for r in reservas if len(r) > 11 and r[10])
        
        return total, hoy_count, total_ingresos
    except Exception as e:
        logger.exception("Error calculando métricas barbero")
        return 0, 0, 0


def calcular_metricas_admin(barberia_id):
    """Calcula métricas para admin."""
    if not barberia_id or not st.session_state.get("db_available", True):
        return 0, 0, 0, 0
    
    try:
        num_barberos = len(listar_usuarios_barberos(barberia_id))
        
        # Obtener todas las reservas sin filtro de usuario
        reservas = fetch_all(
            """
            SELECT id, barbero, servicio, fecha, hora, cliente, nombre, inicio, precio, estado, pagado, monto
            FROM reservas
            WHERE barberia_id = %s
            ORDER BY inicio DESC
            """,
            (barberia_id,),
        ) or []
        
        total_reservas = len(reservas)
        
        hoy = datetime.now().date()
        hoy_count = sum(1 for r in reservas if r[3] == hoy)
        
        total_ingresos = sum(r[11] if len(r) > 11 else r[8] for r in reservas if len(r) > 11 and r[10])
        
        return total_reservas, hoy_count, total_ingresos, num_barberos
    except Exception as e:
        logger.exception("Error calculando métricas admin")
        return 0, 0, 0, 0


def calcular_metricas_super_admin(barberia_id):
    """Calcula métricas globales para super admin."""
    if not st.session_state.get("db_available", True):
        return 0, 0, 0, 0, 0
    
    try:
        nb = fetch_one("SELECT COUNT(*) FROM barberias")
        num_barberias = nb[0] if nb else 0
        
        nu = fetch_one("SELECT COUNT(*) FROM usuarios")
        num_usuarios = nu[0] if nu else 0
        
        nr = fetch_one("SELECT COUNT(*) FROM reservas")
        num_reservas = nr[0] if nr else 0
        
        total_ingresos_row = fetch_one("SELECT SUM(monto) FROM reservas WHERE pagado = TRUE")
        total_ingresos = total_ingresos_row[0] if total_ingresos_row and total_ingresos_row[0] else 0
        
        hoy = datetime.now().date()
        hoy_row = fetch_one("SELECT COUNT(*) FROM reservas WHERE DATE(inicio) = %s", (hoy,))
        hoy_count = hoy_row[0] if hoy_row else 0
        
        return num_barberias, num_usuarios, num_reservas, total_ingresos, hoy_count
    except Exception as e:
        logger.exception("Error calculando métricas super admin")
        return 0, 0, 0, 0, 0


def render_dashboard_cards(col_count, cards_data):
    """Renderiza cards de métricas con layout flexible."""
    cols = st.columns(col_count)
    for idx, (col, card) in enumerate(zip(cols, cards_data)):
        with col:
            st.metric(card["label"], card["value"], card.get("delta", None))


# ------------------ LOGIN ------------------

try:
    if "user" not in st.session_state:
        st.session_state.user = None
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
            ], key="login_option")

            if opcion == "🔑 Iniciar sesión":
                st.markdown("### Accede a tu cuenta")
                with st.form("login_form"):
                    usuario = st.text_input("👤 Usuario", placeholder="Tu usuario")
                    password = st.text_input("🔐 Contraseña", type="password", placeholder="Tu contraseña")
                    entrar = st.form_submit_button("✅ Entrar", use_container_width=True, disabled=not db_ok)

                if entrar:
                    with st.spinner("🔍 Verificando credenciales..."):
                        user = login(usuario, password)
                        if user:
                            st.session_state.user = user
                            nr_login = normalizar_rol(user[3])
                            if nr_login == "SUPER_ADMIN":
                                st.session_state.barberia_id = None
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
                            # Debug: Mostrar información para troubleshooting
                            with st.expander("🔧 Información de Depuración"):
                                st.write(f"📝 Usuario ingresado: `{usuario}`")
                                
                                # Buscar usuario en BD
                                debug_user = fetch_one(
                                    "SELECT id, usuario, password FROM usuarios WHERE usuario=%s",
                                    (usuario,),
                                )
                                
                                if debug_user:
                                    st.success(f"✅ Usuario encontrado en BD")
                                    st.write(f"  - ID: {debug_user[0]}")
                                    st.write(f"  - Usuario: {debug_user[1]}")
                                    st.write(f"  - Hash: {debug_user[2][:30]}...")
                                    st.write(f"  - Es bcrypt: {es_hash_bcrypt(debug_user[2])}")
                                    
                                    # Verificar password
                                    pwd_check = verificar_password(password, debug_user[2])
                                    if pwd_check:
                                        st.success("✅ Contraseña correcta")
                                    else:
                                        st.error("❌ Contraseña incorrecta")
                                        st.info("💡 Verifica que la contraseña sea correcta (respeta mayúsculas/minúsculas)")
                                else:
                                    st.error(f"❌ Usuario NO encontrado en BD")
                                    st.info("💡 Verifica el nombre de usuario")
                                    
                                # Verificar DB
                                st.write(f"🗄️ BD disponible: {db_ok}")

            elif opcion == "✨ Registrar barbería":
                st.markdown("### Crea tu barbería")
                with st.form("register_form"):
                    nb = st.text_input("🏢 Nombre de la barbería", placeholder="Ej: Barbería Premium")
                    ad_u = st.text_input("👤 Usuario administrador", placeholder="Tu usuario")
                    ad_p = st.text_input("🔐 Contraseña", type="password", placeholder="Contraseña segura")
                    crear = st.form_submit_button("✅ Crear barbería", use_container_width=True, disabled=not db_ok)
                
                if crear:
                    with st.spinner("⏳ Creando tu barbería..."):
                        registrar_barberia(nb, ad_u, ad_p)

# ------------------ APP ------------------

    else:
        user = st.session_state.user
        rol = user[3] if user and len(user) > 3 else None
        usuario = user[1] if user and len(user) > 1 else None
        nr = normalizar_rol(rol)

        if not rol:
            st.error("Rol no definido")
            st.stop()

        barberia_id = st.session_state.get("barberia_id")
        bid_ctx = effective_barberia_id()

        if not db_ok:
            st.warning(
                "La base de datos no está disponible. Estás en modo demo: la interfaz se muestra, "
                "pero no se pueden crear ni modificar reservas ni consultar datos en vivo."
            )

        # ===== SIDEBAR =====
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 Cuenta")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**{usuario}**")
                st.caption(nr.replace("_", " "))
            with col2:
                st.markdown("✅")
            
            # Get barberia name
            barberia_name = "Principal"
            if barberia_id:
                b_name_row = fetch_one("SELECT nombre FROM barberias WHERE id = %s", (barberia_id,))
                if b_name_row:
                    barberia_name = b_name_row[0]
            
            st.markdown(f"**Barbería:** {barberia_name}")
            st.markdown("---")

            if nr == "SUPER_ADMIN":
                st.markdown("### 🏢 Contexto")
                b_list = fetch_all("SELECT id, nombre FROM barberias ORDER BY nombre") or []
                if b_list:
                    etiquetas = {f"{r[1]}": r[0] for r in b_list}
                    claves = list(etiquetas.keys())
                    idx = 0
                    if st.session_state.barberia_context_id in etiquetas.values():
                        idx = list(etiquetas.values()).index(st.session_state.barberia_context_id)
                    sel_lab = st.selectbox("Barbería activa", claves, index=idx, key="super_sel_barb")
                    st.session_state.barberia_context_id = etiquetas[sel_lab]
                st.session_state.super_admin_all_barberias = st.checkbox(
                    "Ver todas las barberías",
                    value=st.session_state.get("super_admin_all_barberias", False),
                    key="chk_super_all",
                )
                st.markdown("---")

            st.markdown("### 🗺️ Navegación")
            nav_opts = ["Dashboard", "Reservas", "Barberos", "Configuración"]
            if nr == "CLIENTE":
                nav_opts = ["Dashboard", "Reservas"]
            seccion = st.radio("", nav_opts, key=f"nav_main_{nr}", label_visibility="collapsed")

            st.markdown("---")
            if st.button("🚪 Cerrar sesión", use_container_width=True, type="secondary"):
                st.session_state.user = None
                st.session_state.barberia_id = None
                st.session_state.barberia_context_id = None
                st.rerun()

        eventos = obtener_reservas()

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
                st.markdown("# 📊 Mi Panel")
                
                if not db_ok:
                    st.info("📊 Métricas no disponibles sin base de datos.")
                else:
                    with st.spinner("⏳ Cargando tus métricas..."):
                        total_reservas, hoy_reservas, _ = calcular_metricas_cliente(barberia_id, usuario)
                    
                    render_dashboard_cards(2, [
                        {"label": "📅 Tus Reservas", "value": total_reservas},
                        {"label": "🎯 Hoy", "value": hoy_reservas},
                    ])
                    
                    st.markdown("---")
                    st.markdown("### 💡 Información Útil")
                    col_tip1, col_tip2 = st.columns(2)
                    with col_tip1:
                        st.success("✨ Obtén descuento cada 5 cortes")
                    with col_tip2:
                        st.info("⏰ Cancela con 1 hora de anticipación")

            if seccion == "Reservas":
                st.markdown("# 📱 Mis Reservas")

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
                                inicio = r[7] if len(r) > 7 else None
                                fin = inicio + timedelta(hours=1) if inicio else None
                                if inicio and fin:
                                    mis_reservas_dict.append((r[0], r[5] or r[6], r[1], r[2], r[4], inicio, fin))
                            
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
                        with st.spinner("⏳ Cargando tus reservas..."):
                            mis_reservas = listar_reservas_filtradas(barberia_id, "CLIENTE", usuario)
                        if mis_reservas:
                            mostrar_reservas_dataframe(mis_reservas)
                            ui_eliminar_reserva_lista(mis_reservas, "cliente")
                        else:
                            st.info("📭 Aún no tienes reservas. ¡Crea una!")

        # ================= BARBERO =================
        elif nr == "BARBERO":
            if not barberia_id:
                st.warning("No hay barberia asociada a la sesión.")
                st.stop()

            if seccion == "Dashboard":
                st.markdown("# 📊 Mi Panel · Barbero")
                
                if not db_ok:
                    st.info("📊 Métricas no disponibles sin base de datos.")
                else:
                    with st.spinner("⏳ Cargando tus métricas..."):
                        total_reservas, hoy_reservas, total_ingresos = calcular_metricas_barbero(barberia_id, usuario)
                    
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
                            st.caption(f"🕐 {r[4]} - {r[5] or r[6]} ({r[2]})")

            if seccion == "Reservas":
                st.markdown("# 📅 Mi Agenda")
                
                tab_cal, tab_crear, tab_lista = st.tabs([
                    "📆 Calendario",
                    "➕ Crear/Editar",
                    "📋 Listado"
                ])
                
                # TAB: CALENDARIO
                with tab_cal:
                    if db_ok:
                        with st.spinner("⏳ Cargando tu agenda..."):
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
                    if not db_ok:
                        st.info("Tabla no disponible sin base de datos.")
                    else:
                        with st.spinner("⏳ Cargando tus reservas..."):
                            rows_bar = listar_reservas_filtradas(barberia_id, "BARBERO", usuario)
                        if rows_bar:
                            mostrar_reservas_dataframe(rows_bar)
                            ui_marcar_pagado_reservas(rows_bar, "barbero_panel")
                            ui_eliminar_reserva_lista(rows_bar, "barbero_panel")
                        else:
                            st.info("📭 No hay reservas")

            if seccion == "Barberos":
                st.markdown("# 👥 Equipo")
                st.info("👨‍💼 Solo el administrador de la barbería gestiona el equipo de barberos.")

            if seccion == "Configuración":
                st.markdown("# ⚙️ Configuración")
                st.info("✨ Preferencias y ajustes próximamente.")

        # ================= ADMIN =================
        elif nr == "ADMIN":
            if not barberia_id:
                st.warning("No hay barberia asociada a la sesión.")
                st.stop()

            if seccion == "Dashboard":
                st.markdown("# 📊 Panel Administrativo")
                
                if not db_ok:
                    st.info("📊 Métricas no disponibles sin base de datos.")
                else:
                    with st.spinner("⏳ Cargando métricas de la barbería..."):
                        total_reservas, hoy_reservas, total_ingresos, num_barberos = calcular_metricas_admin(barberia_id)
                    
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
                            st.caption(f"🕐 {r[4]} - {r[5] or r[6]} con {r[1]} ({r[2]})")

            if seccion == "Reservas":
                st.markdown("# 📅 Agenda")
                
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
                            render_agenda_interactiva(eventos, read_only=not db_ok)
                    else:
                        st.warning("Calendario no disponible sin base de datos (modo demo).")
                
                # TAB: CREAR/EDITAR
                with tab_crear:
                    render_gestion_agenda()
                
                # TAB: RESERVAS
                with tab_lista:
                    st.markdown("### 📋 Reservas")
                    if not db_ok:
                        st.info("Tabla no disponible sin base de datos.")
                    else:
                        filtro_adm = st.selectbox(
                            "Filtrar por barbero",
                            opciones_filtro_barberos_ui(barberia_id),
                            key="tabla_admin_filtro",
                        )
                        with st.spinner("⏳ Cargando reservas..."):
                            rows_adm = listar_reservas_filtradas(
                                barberia_id, "ADMIN", usuario, filtro_barbero=filtro_adm
                            )
                        if rows_adm:
                            mostrar_reservas_dataframe(rows_adm)
                            ui_marcar_pagado_reservas(rows_adm, "admin_panel")
                            ui_eliminar_reserva_lista(rows_adm, "admin_panel")
                        else:
                            st.info("📭 No hay reservas")
                
                # TAB: INGRESOS
                with tab_ingresos:
                    st.markdown("### 💰 Ingresos")
                    if db_ok:
                        with st.spinner("⏳ Cargando datos de ingresos..."):
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

            if seccion == "Barberos":
                st.markdown("# 👥 Gestión de Barberos")
                
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

            if seccion == "Configuración":
                st.markdown("# ⚙️ Configuración")
                st.info("✨ Datos de la barbería y preferencias próximamente.")

        # ================= SUPER_ADMIN =================
        elif nr == "SUPER_ADMIN":
            if seccion == "Dashboard":
                st.markdown("# 📊 Panel Global (Super Admin)")
                
                if not db_ok:
                    st.info("📊 Métricas no disponibles sin base de datos.")
                else:
                    with st.spinner("⏳ Cargando métricas globales..."):
                        num_barberias, num_usuarios, num_reservas, total_ingresos, hoy_count = calcular_metricas_super_admin(bid_ctx)
                    
                    render_dashboard_cards(5, [
                        {"label": "🏢 Barberías", "value": num_barberias},
                        {"label": "👥 Usuarios", "value": num_usuarios},
                        {"label": "📅 Total Reservas", "value": num_reservas},
                        {"label": "🎯 Hoy", "value": hoy_count},
                        {"label": "💰 Ingresos Totales", "value": f"${total_ingresos}"},
                    ])

            if seccion == "Reservas":
                st.markdown("# 📅 Agenda Global")
                
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
                            render_agenda_interactiva(eventos, read_only=not db_ok)
                    else:
                        st.warning("Calendario no disponible sin base de datos (modo demo).")
                
                # TAB: CREAR/EDITAR
                with tab_crear:
                    render_gestion_agenda()

                # TAB: RESERVAS
                with tab_lista:
                    st.markdown("### 📋 Reservas")
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
                            mostrar_reservas_dataframe(rows_su)
                            ui_marcar_pagado_reservas(rows_su, "super_panel")
                            ui_eliminar_reserva_lista(rows_su, "super_panel")
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

            if seccion == "Barberos":
                st.markdown("# 👥 Barberos (Contexto)")
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

            if seccion == "Configuración":
                st.markdown("# ⚙️ Configuración Global")
                st.info("✨ Parámetros de plataforma próximamente.")

        else:
            st.error(f"Vista no disponible para el rol: {nr}")

except Exception as e:
    logger.exception("Unhandled exception in Streamlit app")
    st.error(str(e))
