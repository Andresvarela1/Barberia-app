"""Session context and multi-tenant helpers reused by the Streamlit app."""

import logging

import streamlit as st

from app_core.db import safe_fetch_all, safe_fetch_one
from app_core.security.tenant_access import (
    can_access_barberia,
    effective_barberia_id,
    enforce_access,
    enforce_barberia_access,
    get_current_barberia_id,
    get_user_barberia_id,
    get_user_id,
    get_user_role,
    normalizar_rol,
    session_barberia_for_write,
)

logger = logging.getLogger("barberia_app")


def ensure_session_defaults(default_barberia_id, *, db_available):
    """Initialize the minimum session state required by the app."""

    defaults = {
        "user": None,
        "rol": "CLIENTE",
        "barberia_id": default_barberia_id,
        "barberia_context_id": default_barberia_id,
        "super_admin_all_barberias": False,
        "reserva_seleccionada_id": None,
        "mostrar_detalles_reserva": False,
        "view": "home",
        "public_mode": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    st.session_state["db_available"] = db_available
    return db_available


def apply_public_barberia_context(barberia_id):
    """Store temporary public booking context in the session."""

    st.session_state.barberia_id = barberia_id
    st.session_state.public_mode = True


def reset_public_barberia_context(default_barberia_id):
    """Restore the default barberia after leaving public booking routes."""

    st.session_state.barberia_id = default_barberia_id


def apply_login_session_context(user, default_barberia_id):
    """Populate session state after a successful login and return target view."""

    st.session_state["user"] = user
    st.session_state["user_id"] = user[0]

    raw_role = user[3] if len(user) > 3 else None
    normalized_role = normalizar_rol(raw_role)
    st.session_state["rol"] = normalized_role
    st.session_state["user_role"] = normalized_role
    st.session_state["public_mode"] = False

    if normalized_role == "SUPER_ADMIN":
        st.session_state["barberia_id"] = None
        first_barberia = safe_fetch_one("SELECT id FROM barberias ORDER BY id LIMIT 1")
        st.session_state["barberia_context_id"] = first_barberia[0] if first_barberia else None
        st.session_state["super_admin_all_barberias"] = False
        return normalized_role, "dashboard_admin"

    assigned_barberia_id = user[5] if len(user) > 5 else None
    current_barberia_id = assigned_barberia_id or default_barberia_id
    st.session_state["barberia_id"] = current_barberia_id
    st.session_state["barberia_context_id"] = current_barberia_id
    st.session_state["super_admin_all_barberias"] = False

    if normalized_role == "BARBERO":
        return normalized_role, "dashboard_barbero"

    return normalized_role, "dashboard"


def get_cached_barberia_name(barberia_id, default_name="Principal"):
    """Return the current barberia display name using a small session cache."""

    if not barberia_id:
        return default_name

    if st.session_state.get("cached_barberia_id") != barberia_id:
        row = safe_fetch_one("SELECT nombre FROM barberias WHERE id = %s", (barberia_id,))
        st.session_state["barberia_name"] = row[0] if row else default_name
        st.session_state["cached_barberia_id"] = barberia_id

    return st.session_state.get("barberia_name", default_name)


def load_super_admin_context_options():
    """Return cached barberia rows and selected index for SUPER_ADMIN context."""

    if "barberias_list" not in st.session_state:
        st.session_state["barberias_list"] = (
            safe_fetch_all("SELECT id, nombre FROM barberias ORDER BY nombre") or []
        )

    rows = st.session_state["barberias_list"]
    if not rows:
        return [], {}, [], 0

    labels = {row[1]: row[0] for row in rows}
    keys = list(labels.keys())
    barberia_ids = list(labels.values())

    current_context_id = st.session_state.get("barberia_context_id")
    if current_context_id in barberia_ids:
        selected_index = barberia_ids.index(current_context_id)
    else:
        selected_index = 0

    selected_index = min(selected_index, len(keys) - 1) if keys else 0
    return rows, labels, keys, selected_index
