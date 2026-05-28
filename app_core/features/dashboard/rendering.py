from datetime import datetime

import streamlit as st

from app_core.db import safe_fetch_all
from app_core.metrics import (
    calcular_metricas_admin,
    calcular_metricas_header,
    calcular_metricas_operativas_admin,
    calcular_metricas_operativas_super_admin,
    calcular_metricas_super_admin,
)
from design_system import (
    Colors,
    render_alert,
    render_divider,
    render_metric_grid,
    render_panel_empty_state,
    render_panel_header,
    render_subsection_title,
)


def render_admin_dashboard_section(*, barberia_id, db_ok, barberia_name, render_upcoming_summary):
    render_panel_header(
        "Vision general",
        "Gestiona metricas, agenda y actividad diaria de tu barberia.",
        eyebrow="Panel administrativo",
        meta=barberia_name,
    )

    if not db_ok:
        render_alert("Metricas no disponibles sin base de datos", alert_type="info", title="Modo demo")
        return

    with st.spinner("Cargando metricas..."):
        total_hoy, pagadas_hoy, pendientes_hoy = calcular_metricas_header(barberia_id)
        total_reservas, hoy_reservas, total_ingresos, num_barberos = calcular_metricas_admin(barberia_id)
        creadas, completadas, canceladas, no_show, clientes_unicos = calcular_metricas_operativas_admin(barberia_id)

    render_metric_grid([
        ("Reservas Hoy", total_hoy, "Hoy", Colors.PRIMARY),
        ("Pagadas", pagadas_hoy, "Pago", Colors.SUCCESS),
        ("Pendientes", pendientes_hoy, "Pendiente", Colors.WARNING),
    ], columns=3)
    render_divider()
    render_subsection_title("Resumen general")
    render_metric_grid([
        ("Total Reservas", total_reservas, "Listado", Colors.SECONDARY),
        ("Hoy", hoy_reservas, "Agenda", Colors.PRIMARY),
        ("Ingresos", f"${total_ingresos}", "$", Colors.SUCCESS),
        ("Barberos", num_barberos, "Equipo", Colors.WARNING),
    ], columns=4)
    render_divider()
    render_subsection_title("Operacion")
    render_metric_grid([
        ("Creadas", creadas, "Reservas", Colors.PRIMARY),
        ("Completadas", completadas, "Estado", Colors.SUCCESS),
        ("Canceladas", canceladas, "Estado", Colors.WARNING),
        ("No show", no_show, "Estado", Colors.SECONDARY),
        ("Clientes unicos", clientes_unicos, "Clientes", Colors.PRIMARY),
    ], columns=5)
    render_divider()

    with st.spinner("Cargando proximas citas..."):
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
        render_upcoming_summary("Proximas citas (hoy)", hoy_reservas_list)
    else:
        render_panel_empty_state(
            "Sin citas para hoy",
            "No hay reservas programadas para hoy en el contexto actual.",
        )


def render_super_admin_dashboard_section(*, bid_ctx, db_ok, barberia_name):
    render_panel_header(
        "Vision global",
        "Supervisa metricas y operacion de todas las barberias.",
        eyebrow="Super admin",
        meta=barberia_name,
    )

    if not db_ok:
        render_alert("Metricas no disponibles sin base de datos", alert_type="info", title="Modo demo")
        return

    with st.spinner("Cargando metricas globales..."):
        total_hoy, pagadas_hoy, pendientes_hoy = calcular_metricas_header(bid_ctx) if bid_ctx else (0, 0, 0)
        num_barberias, num_usuarios, num_reservas, total_ingresos, hoy_count = calcular_metricas_super_admin(bid_ctx)
        creadas, completadas, canceladas, no_show, clientes_unicos, context_label = calcular_metricas_operativas_super_admin(bid_ctx)

    render_metric_grid([
        ("Reservas Hoy", total_hoy, "Hoy", Colors.PRIMARY),
        ("Pagadas", pagadas_hoy, "Pago", Colors.SUCCESS),
        ("Pendientes", pendientes_hoy, "Pendiente", Colors.WARNING),
    ], columns=3)
    render_divider()
    render_subsection_title("Resumen global")
    render_metric_grid([
        ("Barberias", num_barberias, "Barberias", Colors.PRIMARY),
        ("Usuarios", num_usuarios, "Usuarios", Colors.SECONDARY),
        ("Total", num_reservas, "Listado", Colors.PRIMARY),
        ("Hoy", hoy_count, "Agenda", Colors.SECONDARY),
        ("Ingresos", f"${total_ingresos}", "$", Colors.SUCCESS),
    ], columns=5)
    render_divider()
    render_subsection_title("Operacion")
    st.caption(f"Contexto mostrado: {context_label}")
    render_metric_grid([
        ("Creadas", creadas, "Reservas", Colors.PRIMARY),
        ("Completadas", completadas, "Estado", Colors.SUCCESS),
        ("Canceladas", canceladas, "Estado", Colors.WARNING),
        ("No show", no_show, "Estado", Colors.SECONDARY),
        ("Clientes unicos", clientes_unicos, "Clientes", Colors.PRIMARY),
    ], columns=5)

    if not num_reservas:
        render_panel_empty_state(
            "Sin actividad registrada",
            "Todavia no hay reservas en el contexto actual para mostrar en el dashboard.",
        )
