"""Authentication helpers: password hashing, login, user registration.

Extracted from app.py.  All public names are re-exported so callers that
already import from app.py can switch to importing from here without
changing their call-sites.
"""

import logging

import bcrypt
import streamlit as st

from app_core.db.connection import get_connection
from app_core.db.safe_queries import safe_fetch_one, safe_execute
from app_core.tenancy import apply_login_session_context
from app_core.security.tenant_access import normalizar_rol

logger = logging.getLogger("barberia_app")

PUBLIC_VIEWS = {"home", "login", "registro", "reserva"}
AUTHENTICATED_ENTRY_VIEWS = {"dashboard", "dashboard_admin", "dashboard_barbero"}
KNOWN_SCREEN_KEYS = PUBLIC_VIEWS | AUTHENTICATED_ENTRY_VIEWS


# ---------------------------------------------------------------------------
# Text / hash helpers
# ---------------------------------------------------------------------------

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
        resultado = password == password_guardada
        logger.warning(f"[AVISO] Usando comparación plain text (legacy): {resultado}")
        return resultado


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

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

    if not verificar_password(password, user[2]):
        logger.warning(f"[ERROR] Contraseña incorrecta para usuario: {usuario}")
        return None

    logger.info(f"[OK] Contraseña verificada para: {usuario}")

    rol_normalizado = normalizar_rol(user[3])
    if rol_normalizado != user[3]:
        logger.info(f"Procesando Normalizando rol de '{user[3]}' a '{rol_normalizado}' para: {usuario}")
        if safe_execute(
            "UPDATE usuarios SET rol=%s WHERE id=%s",
            (rol_normalizado, user[0]),
            allow_system=True,
            system_reason="login legacy role normalization before tenant context",
        ):
            user = (user[0], user[1], user[2], rol_normalizado, user[4], user[5], user[6])
            logger.info(f"[OK] Rol actualizado en BD para: {usuario}")
        else:
            logger.warning(f"[AVISO] No se pudo actualizar rol en BD, usando rol normalizado localmente")
            user = (user[0], user[1], user[2], rol_normalizado, user[4], user[5], user[6])

    if not es_hash_bcrypt(user[2]):
        logger.info(f"Procesando Rehasheando contraseña para: {usuario}")
        nuevo_hash = hash_password(password)
        if safe_execute(
            "UPDATE usuarios SET password=%s WHERE id=%s",
            (nuevo_hash, user[0]),
            allow_system=True,
            system_reason="login legacy password rehash before tenant context",
        ):
            logger.info(f"[OK] Contraseña rehashada para: {usuario}")
            user = (user[0], user[1], nuevo_hash, user[3], user[4], user[5], user[6])
        else:
            logger.warning(f"[AVISO] No se pudo rehasear contraseña para: {usuario}")

    logger.info(f"[OK] Login exitoso para: {usuario} con rol: {user[3]}")
    return user


def _target_view_for_role(user_role):
    normalized_role = normalizar_rol(user_role)
    if normalized_role == "SUPER_ADMIN":
        return "dashboard_admin"
    if normalized_role == "BARBERO":
        return "dashboard_barbero"
    return "dashboard"


def normalize_authenticated_session_state(default_barberia_id):
    """Normalize authenticated session defaults and dashboard target view."""

    user = st.session_state.get("user")
    if not user:
        return None

    user_role = st.session_state.get("user_role") or st.session_state.get("rol")
    normalized_role = normalizar_rol(user_role)
    target_view = _target_view_for_role(normalized_role)

    st.session_state["rol"] = normalized_role
    st.session_state["user_role"] = normalized_role
    st.session_state["public_mode"] = False
    st.session_state["reserva_seleccionada_id"] = st.session_state.get("reserva_seleccionada_id")
    st.session_state["mostrar_detalles_reserva"] = bool(
        st.session_state.get("mostrar_detalles_reserva", False)
    )
    st.session_state.setdefault("user_id", user[0] if len(user) > 0 else None)
    st.session_state.setdefault("super_admin_all_barberias", False)

    if normalized_role == "SUPER_ADMIN":
        if "barberia_id" not in st.session_state:
            st.session_state["barberia_id"] = None
    else:
        assigned_barberia_id = user[5] if len(user) > 5 else None
        current_barberia_id = assigned_barberia_id or default_barberia_id
        if not st.session_state.get("barberia_id"):
            st.session_state["barberia_id"] = current_barberia_id
        if not st.session_state.get("barberia_context_id"):
            st.session_state["barberia_context_id"] = st.session_state["barberia_id"]
        st.session_state["super_admin_all_barberias"] = False

    if st.session_state.get("view") in PUBLIC_VIEWS or not st.session_state.get("view"):
        st.session_state["view"] = target_view

    return {
        "user": user,
        "role": normalized_role,
        "target_view": target_view,
    }


def resolve_authenticated_entry(default_barberia_id):
    """Resolve the initial destination for an already authenticated user."""

    incoming_view = st.session_state.get("view")
    normalized = normalize_authenticated_session_state(default_barberia_id)
    if not normalized:
        return None

    target_view = normalized["target_view"]
    corrected_view = False

    if st.session_state.get("view") not in AUTHENTICATED_ENTRY_VIEWS:
        st.session_state["view"] = target_view
        corrected_view = incoming_view not in (None, target_view)
    elif incoming_view not in AUTHENTICATED_ENTRY_VIEWS and incoming_view != target_view:
        corrected_view = True

    return {
        **normalized,
        "view": st.session_state.get("view"),
        "should_rerun": corrected_view,
    }


def resolve_view_access(default_barberia_id, current_view=None):
    """Resolve whether the current session can stay on the requested view."""

    resolved_view = current_view or st.session_state.get("view") or "home"

    if st.session_state.get("user"):
        entry = resolve_authenticated_entry(default_barberia_id)
        if not entry:
            return {
                "is_allowed": False,
                "resolved_view": "home",
                "should_rerun": True,
                "should_stop": False,
            }

        return {
            "is_allowed": entry["view"] in AUTHENTICATED_ENTRY_VIEWS,
            "resolved_view": entry["view"],
            "should_rerun": bool(entry.get("should_rerun")),
            "should_stop": False,
        }

    if resolved_view in AUTHENTICATED_ENTRY_VIEWS:
        st.session_state["view"] = "home"
        return {
            "is_allowed": False,
            "resolved_view": "home",
            "should_rerun": True,
            "should_stop": False,
        }

    if resolved_view not in PUBLIC_VIEWS:
        st.session_state["view"] = "home"
        return {
            "is_allowed": False,
            "resolved_view": "home",
            "should_rerun": True,
            "should_stop": False,
        }

    return {
        "is_allowed": True,
        "resolved_view": resolved_view,
        "should_rerun": False,
        "should_stop": True,
    }


def resolve_render_view(default_barberia_id, current_view=None):
    """Resolve the final view that app.py should render right now."""

    access = resolve_view_access(default_barberia_id, current_view=current_view)
    resolved_view = access["resolved_view"] if access else (current_view or "home")

    return {
        "resolved_view": resolved_view,
        "should_rerun": bool(access and access.get("should_rerun")),
        "should_stop": bool(access and access.get("should_stop")),
        "is_authenticated": bool(st.session_state.get("user")),
    }


def resolve_screen_dispatch(default_barberia_id, current_view=None):
    """Resolve the screen key app.py should dispatch to."""

    render_decision = resolve_render_view(
        default_barberia_id,
        current_view=current_view,
    )
    resolved_view = render_decision["resolved_view"]
    screen_key = resolved_view if resolved_view in KNOWN_SCREEN_KEYS else "home"
    screen_group = (
        "public"
        if screen_key in PUBLIC_VIEWS
        else "authenticated"
        if screen_key in AUTHENTICATED_ENTRY_VIEWS
        else "public"
    )

    return {
        **render_decision,
        "screen_key": screen_key,
        "screen_group": screen_group,
        "resolved_view": resolved_view,
    }


def login_and_prepare_session(usuario, password, default_barberia_id):
    """Authenticate user and populate session context for the app."""

    user = login(usuario, password)
    if not user:
        return None

    apply_login_session_context(user, default_barberia_id)
    return resolve_authenticated_entry(default_barberia_id)


def logout_and_reset_session(default_barberia_id):
    """Reset authenticated session state without breaking app defaults."""

    st.session_state["user"] = None
    st.session_state["user_id"] = None
    st.session_state["rol"] = "CLIENTE"
    st.session_state["user_role"] = "CLIENTE"
    st.session_state["barberia_id"] = default_barberia_id
    st.session_state["barberia_context_id"] = default_barberia_id
    st.session_state["super_admin_all_barberias"] = False
    st.session_state["public_mode"] = False
    st.session_state["view"] = "home"
    st.session_state["reserva_seleccionada_id"] = None
    st.session_state["mostrar_detalles_reserva"] = False

    for key in (
        "barberia_name",
        "cached_barberia_id",
        "barberias_list",
        "super_sel_barb",
        "chk_super_all",
    ):
        st.session_state.pop(key, None)

    for key in list(st.session_state.keys()):
        if str(key).startswith("nav_"):
            st.session_state.pop(key, None)

    return True


# ---------------------------------------------------------------------------
# User / barberia registration
# ---------------------------------------------------------------------------

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
        result = safe_execute(
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
