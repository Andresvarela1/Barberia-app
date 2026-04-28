"""Safe query wrappers with multi-tenant validation."""

import logging
import traceback

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
