"""Metrics queries for the dashboard.

Extracted from app.py.  All public names keep their original signatures.
"""

import logging
from datetime import datetime

import streamlit as st

from app_core.db.safe_queries import safe_fetch_one
from app_core.security.tenant_access import get_current_barberia_id

logger = logging.getLogger("barberia_app")


def calcular_metricas_header(barberia_id=None):
    """Calculate quick dashboard header metrics for today.

    SECURITY: Always uses current barberia context.
    """
    barberia_id = get_current_barberia_id()
    if not barberia_id or not st.session_state.get("db_available", True):
        return 0, 0, 0

    try:
        hoy = datetime.now().date()
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
    except Exception:
        logger.exception("Error calculando métricas header")
        return 0, 0, 0


@st.cache_data(ttl=45)
def calcular_metricas_cliente(barberia_id=None, usuario=None):
    """Fast cached client metrics with optimized queries.

    SECURITY: Always uses current context and validates user access.
    """
    barberia_id = get_current_barberia_id()
    if not barberia_id or not usuario or not st.session_state.get("db_available", True):
        return 0, 0, 0

    try:
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
    except Exception:
        logger.exception("Error calculando métricas cliente")
        return 0, 0, 0


@st.cache_data(ttl=45)
def calcular_metricas_barbero(barberia_id=None, barbero_id=None):
    """Fast cached barber metrics with optimized queries.

    SECURITY: Always uses current context.
    """
    barberia_id = get_current_barberia_id()
    if not barberia_id or not barbero_id or not st.session_state.get("db_available", True):
        return 0, 0, 0

    try:
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
    except Exception:
        logger.exception("Error calculando métricas barbero")
        return 0, 0, 0


@st.cache_data(ttl=45)
def calcular_metricas_admin(barberia_id=None):
    """Fast cached admin metrics with optimized queries.

    SECURITY: Always uses current context.
    """
    barberia_id = get_current_barberia_id()
    if not barberia_id or not st.session_state.get("db_available", True):
        return 0, 0, 0, 0

    try:
        hoy = datetime.now().date()
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
    except Exception:
        logger.exception("Error calculando métricas admin")
        return 0, 0, 0, 0


@st.cache_data(ttl=60)
def calcular_metricas_super_admin(barberia_id=None):
    """Fast cached super admin metrics.

    SECURITY: Uses current barberia context if set, otherwise respects
    super_admin_all_barberias flag.
    """
    if not st.session_state.get("db_available", True):
        return 0, 0, 0, 0, 0

    try:
        hoy = datetime.now().date()
        viewing_all = st.session_state.get("super_admin_all_barberias", False)

        if viewing_all:
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
    except Exception:
        logger.exception("Error calculando métricas super admin")
        return 0, 0, 0, 0, 0
