"""Safe query wrappers with multi-tenant validation."""

import logging

import streamlit as st

from app_core.db.connection import get_connection


logger = logging.getLogger("barberia_app")


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

        except Exception:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass

            if attempt == max_retries - 1:
                logger.exception("Error en base de datos despues de reintentos")
                st.error("Error de base de datos. Por favor, intenta de nuevo.")
                return None

            logger.warning(
                "[AVISO] Error en base de datos, reintentando... (intento %d)",
                attempt + 1,
            )

            if "db_connection" in st.session_state:
                try:
                    st.session_state.db_connection.close()
                except Exception:
                    pass
                st.session_state.db_connection = None


def fetch_one(query, params=None):
    return execute_query(query, params, fetch="one")


def fetch_all(query, params=None):
    return execute_query(query, params, fetch="all") or []


def execute_write(query, params=None, fetch_one_result=False):
    return execute_query(query, params, fetch="one" if fetch_one_result else None)


# ================= STEP 1: SAFE QUERY WRAPPERS WITH BARBERIA_ID ENFORCEMENT =================

LOGIN_READ_PATTERNS = (
    "from usuarios where usuario",
    "from usuarios where lower(usuario)",
    "select count(*) from usuarios where usuario",
)

SYSTEM_WRITE_PATTERNS = (
    "insert into barberias",
    "create table",
    "alter table",
    "create index",
    "drop index",
)

TENANT_TABLE_PATTERNS = (
    "from reservas",
    "join reservas",
    "from usuarios",
    "join usuarios",
    "from servicios",
    "join servicios",
)


def _normalize_query(query):
    return " ".join(str(query).lower().split())


def _current_role():
    role = st.session_state.get("rol") or st.session_state.get("user_role")
    return str(role or "").strip().upper()


def _is_super_admin_global():
    return (
        _current_role() == "SUPER_ADMIN"
        and bool(st.session_state.get("super_admin_all_barberias", False))
    )


def _mentions_tenant_table(query_lower):
    return any(pattern in query_lower for pattern in TENANT_TABLE_PATTERNS)


def _is_system_read(query_lower):
    if "pg_advisory_xact_lock" in query_lower or "hashtext" in query_lower:
        return True
    return "from barberias" in query_lower and not _mentions_tenant_table(query_lower)


def _is_login_read(query_lower):
    return any(pattern in query_lower for pattern in LOGIN_READ_PATTERNS)


def _has_barberia_where_scope(query_lower):
    where_pos = query_lower.find(" where ")
    if where_pos == -1:
        return False
    return "barberia_id" in query_lower[where_pos:]


def _has_barberia_column(query_lower):
    return "barberia_id" in query_lower


def _security_error(message, query):
    error_msg = f"SECURITY VIOLATION: {message}\nQuery: {str(query)[:100]}..."
    logger.error(error_msg)
    raise Exception(error_msg)


def _validate_safe_read(query, *, fetch_many):
    query_lower = _normalize_query(query)

    if _is_system_read(query_lower) or _is_login_read(query_lower):
        return

    if _is_super_admin_global():
        return

    if not _has_barberia_where_scope(query_lower):
        label = "fetch_all" if fetch_many else "fetch_one"
        _security_error(f"{label} missing barberia_id WHERE filter", query)


def safe_fetch_one(query, params=()):
    """Read one row, enforcing tenant scope unless the query is explicitly global."""

    _validate_safe_read(query, fetch_many=False)
    return fetch_one(query, params)


def safe_fetch_all(query, params=()):
    """Read many rows, enforcing tenant scope unless the query is explicitly global."""

    _validate_safe_read(query, fetch_many=True)
    return fetch_all(query, params)


def _validate_safe_write(query, *, allow_system=False, system_reason=None):
    query_lower = _normalize_query(query)

    if allow_system:
        logger.info(
            "System write allowed by explicit reason: %s",
            system_reason or "unspecified",
        )
        return

    if any(pattern in query_lower for pattern in SYSTEM_WRITE_PATTERNS):
        return

    is_insert = "insert into" in query_lower
    is_update = query_lower.startswith("update ") or " update " in query_lower
    is_delete = "delete from" in query_lower

    if is_insert and not _has_barberia_column(query_lower):
        _security_error("insert missing barberia_id column", query)

    if (is_update or is_delete) and not _has_barberia_where_scope(query_lower):
        _security_error("write missing barberia_id WHERE filter", query)


def safe_execute(
    query,
    params=(),
    fetch_one_result=False,
    *,
    allow_system=False,
    system_reason=None,
):
    """Write wrapper that enforces tenant scope for sensitive mutations."""

    _validate_safe_write(
        query,
        allow_system=allow_system,
        system_reason=system_reason,
    )
    return execute_write(query, params, fetch_one_result)
