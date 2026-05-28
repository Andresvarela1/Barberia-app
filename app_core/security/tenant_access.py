"""Multi-tenant access helpers for barberia session context."""

import logging

import streamlit as st


logger = logging.getLogger("barberia_app")


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
