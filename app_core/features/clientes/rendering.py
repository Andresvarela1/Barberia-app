from collections import Counter

import pandas as pd
import streamlit as st

from app_core.db import safe_fetch_all
from design_system import (
    render_alert,
    render_divider,
    render_panel_empty_state,
    render_panel_header,
    render_subsection_title,
)


def _normalize_client_value(value, fallback=""):
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _build_client_summary_rows(rows):
    service_counts = Counter()
    barber_counts = Counter()
    latest_rows = []

    for row in rows:
        service_name = _normalize_client_value(row.get("servicio"), "Sin servicio")
        barber_name = _normalize_client_value(row.get("barbero"), "Sin asignar")
        service_counts[service_name] += 1
        barber_counts[barber_name] += 1
        latest_rows.append(
            {
                "Fecha": row.get("fecha"),
                "Hora": row.get("hora"),
                "Servicio": service_name,
                "Barbero": barber_name,
                "Estado": _normalize_client_value(row.get("estado"), "pendiente"),
                "Pago": "Pagada" if row.get("pagado") else "Pendiente",
            }
        )

    latest_rows.sort(
        key=lambda item: (
            _normalize_client_value(item.get("Fecha"), ""),
            _normalize_client_value(item.get("Hora"), ""),
        ),
        reverse=True,
    )

    return {
        "latest_rows": latest_rows[:8],
        "services_used": service_counts.most_common(5),
        "favorite_barber": barber_counts.most_common(1)[0][0] if barber_counts else None,
    }


def _fetch_clients(barberia_id, search_query):
    sql = """
        SELECT
            COALESCE(NULLIF(TRIM(nombre), ''), NULLIF(TRIM(cliente), ''), 'Cliente sin nombre') AS cliente_nombre,
            COALESCE(NULLIF(TRIM(telefono), ''), '') AS telefono,
            COUNT(*) AS total_reservas,
            MAX(inicio) AS ultima_reserva
        FROM reservas
        WHERE barberia_id = %s
    """
    params = [barberia_id]

    if search_query:
        search_token = f"%{search_query.strip().lower()}%"
        sql += """
          AND (
                LOWER(COALESCE(NULLIF(TRIM(nombre), ''), NULLIF(TRIM(cliente), ''), '')) LIKE %s
             OR LOWER(COALESCE(NULLIF(TRIM(telefono), ''), '')) LIKE %s
          )
        """
        params.extend([search_token, search_token])

    sql += """
        GROUP BY 1, 2
        ORDER BY MAX(inicio) DESC NULLS LAST, 1 ASC
    """

    rows = safe_fetch_all(sql, tuple(params)) or []
    return [
        {
            "name": row[0],
            "phone": row[1] or "Sin telefono",
            "phone_key": row[1] or "",
            "total_reservas": int(row[2] or 0),
            "ultima_reserva": row[3],
        }
        for row in rows
    ]


def _fetch_client_history(barberia_id, client_name, phone_key):
    rows = safe_fetch_all(
        """
        SELECT
            fecha,
            hora,
            servicio,
            barbero,
            estado,
            pagado
        FROM reservas
        WHERE barberia_id = %s
          AND COALESCE(NULLIF(TRIM(nombre), ''), NULLIF(TRIM(cliente), ''), 'Cliente sin nombre') = %s
          AND COALESCE(NULLIF(TRIM(telefono), ''), '') = %s
        ORDER BY inicio DESC NULLS LAST
        """,
        (barberia_id, client_name, phone_key),
    ) or []

    return [
        {
            "fecha": row[0],
            "hora": row[1],
            "servicio": row[2],
            "barbero": row[3],
            "estado": row[4],
            "pagado": row[5],
        }
        for row in rows
    ]


def _format_client_option(client):
    phone = client.get("phone") or "Sin telefono"
    total = client.get("total_reservas", 0)
    return f"{client['name']} | {phone} | {total} reservas"


def render_clientes_section(
    *,
    barberia_id,
    db_ok,
    meta,
    no_context_message,
    no_db_message="Vista de clientes no disponible sin base de datos",
    search_key="clientes_busqueda",
    picker_key="clientes_selector",
):
    render_panel_header(
        "Clientes",
        "Consulta clientes, busca por nombre o telefono y revisa su historial reciente.",
        eyebrow="CRM",
        meta=meta,
    )

    if not db_ok:
        render_alert(no_db_message, alert_type="info", title="Modo demo")
        return

    if not barberia_id:
        render_alert(no_context_message, alert_type="info", title="Contexto requerido")
        return

    search_query = st.text_input(
        "Buscar cliente",
        placeholder="Nombre o telefono",
        key=search_key,
    ).strip()

    with st.spinner("Cargando clientes..."):
        clients = _fetch_clients(barberia_id, search_query)

    if not clients:
        if search_query:
            render_panel_empty_state(
                "Sin coincidencias",
                "No encontramos clientes con ese nombre o telefono en la barberia activa.",
            )
        else:
            render_panel_empty_state(
                "Sin clientes aun",
                "Los clientes apareceran aqui cuando existan reservas registradas en esta barberia.",
            )
        return

    metric_cols = st.columns(2)
    metric_cols[0].metric("Clientes visibles", len(clients))
    metric_cols[1].metric("Con telefono", sum(1 for client in clients if client.get("phone_key")))

    col_list, col_detail = st.columns([1.1, 1.6], gap="large")

    with col_list:
        render_subsection_title("Listado")
        selected_index = st.radio(
            "Clientes disponibles",
            options=list(range(len(clients))),
            format_func=lambda idx: _format_client_option(clients[idx]),
            key=picker_key,
            label_visibility="collapsed",
        )
        selected_client = clients[selected_index]

    with col_detail:
        render_subsection_title(selected_client["name"])
        st.caption(f"Telefono: {selected_client['phone']}")

        with st.spinner("Cargando historial..."):
            history_rows = _fetch_client_history(
                barberia_id,
                selected_client["name"],
                selected_client["phone_key"],
            )

        if not history_rows:
            render_panel_empty_state(
                "Sin historial reciente",
                "No encontramos reservas historicas para este cliente dentro del contexto activo.",
            )
            return

        summary = _build_client_summary_rows(history_rows)
        overview_cols = st.columns(3)
        overview_cols[0].metric("Reservas", selected_client["total_reservas"])
        overview_cols[1].metric(
            "Ultima visita",
            str(selected_client["ultima_reserva"].date()) if hasattr(selected_client["ultima_reserva"], "date") else (
                str(selected_client["ultima_reserva"]) if selected_client["ultima_reserva"] else "Sin fecha"
            ),
        )
        overview_cols[2].metric(
            "Barbero frecuente",
            summary["favorite_barber"] or "Sin dato",
        )

        render_divider()
        render_subsection_title("Servicios usados")
        if summary["services_used"]:
            for service_name, count in summary["services_used"]:
                st.write(f"- {service_name}: {count}")
        else:
            render_alert(
                "Todavia no hay servicios historicos para mostrar.",
                alert_type="info",
                title="Sin datos",
            )

        render_divider()
        render_subsection_title("Ultimas reservas")
        st.dataframe(pd.DataFrame(summary["latest_rows"]), use_container_width=True, hide_index=True)
