from datetime import datetime, timedelta

import streamlit as st

from design_system import render_alert, render_panel_empty_state


def _render_agenda_calendar_results(rows, mostrar_calendario_reservas, render_public_note):
    reservas_calendar = []
    for row in rows:
        fecha = row.get("fecha")
        hora = row.get("hora")
        if fecha and hora:
            try:
                start_dt = datetime.combine(fecha, hora)
                end_dt = start_dt + timedelta(minutes=30)
                monto = row.get("monto") or row.get("precio") or 0
                pagado = bool(row.get("pagado", False))
                reservas_calendar.append(
                    (
                        row.get("id"),
                        row.get("cliente") or row.get("nombre"),
                        row.get("barbero"),
                        row.get("servicio"),
                        monto,
                        start_dt,
                        end_dt,
                        pagado,
                    )
                )
            except (TypeError, ValueError):
                continue

    mostrar_calendario_reservas(reservas_calendar)
    st.markdown("---")
    render_public_note("Vista semanal del calendario con navegación por flechas.")


def _render_admin_agenda_list_filters(barberia_id, opciones_filtro_barberos_ui):
    col_view1, _ = st.columns(2)
    with col_view1:
        view_type = st.radio(
            "Modo de vista",
            ["Tarjetas", "Calendario"],
            horizontal=True,
            key="admin_view_type",
        )

    filtro_adm = st.selectbox(
        "Filtrar por barbero",
        opciones_filtro_barberos_ui(barberia_id),
        key="tabla_admin_filtro",
    )
    return view_type, filtro_adm


def _render_admin_agenda_list_card_actions(
    rows_adm,
    mostrar_reservas_dataframe,
    ui_marcar_pagado_reservas,
    ui_eliminar_reserva_lista,
):
    mostrar_reservas_dataframe(rows_adm)
    ui_marcar_pagado_reservas(rows_adm, "admin_panel")
    ui_eliminar_reserva_lista(rows_adm, "admin_panel")


def _render_admin_agenda_list_results(
    view_type,
    rows_adm,
    mostrar_reservas_dataframe,
    ui_marcar_pagado_reservas,
    ui_eliminar_reserva_lista,
    mostrar_calendario_reservas,
    render_public_note,
):
    if not rows_adm:
        render_panel_empty_state(
            "Sin reservas para este filtro",
            "Ajusta el barbero o cambia el modo de vista para revisar otros resultados.",
        )
        return

    if view_type == "Tarjetas":
        _render_admin_agenda_list_card_actions(
            rows_adm,
            mostrar_reservas_dataframe,
            ui_marcar_pagado_reservas,
            ui_eliminar_reserva_lista,
        )
        return

    _render_agenda_calendar_results(
        rows_adm,
        mostrar_calendario_reservas,
        render_public_note,
    )


def render_admin_agenda_list_tab(
    *,
    barberia_id,
    usuario,
    db_ok,
    opciones_filtro_barberos_ui,
    listar_reservas_filtradas,
    mostrar_reservas_dataframe,
    ui_marcar_pagado_reservas,
    ui_eliminar_reserva_lista,
    mostrar_calendario_reservas,
    render_public_note,
):
    st.markdown("### Reservas")

    if not db_ok:
        render_alert(
            "No se puede cargar el listado de reservas mientras la base de datos no está disponible.",
            alert_type="info",
            title="Modo demo",
        )
        return

    view_type, filtro_adm = _render_admin_agenda_list_filters(
        barberia_id,
        opciones_filtro_barberos_ui,
    )
    with st.spinner("Cargando reservas..."):
        rows_adm = listar_reservas_filtradas(
            barberia_id,
            "ADMIN",
            usuario,
            filtro_barbero=filtro_adm,
        )

    _render_admin_agenda_list_results(
        view_type,
        rows_adm,
        mostrar_reservas_dataframe,
        ui_marcar_pagado_reservas,
        ui_eliminar_reserva_lista,
        mostrar_calendario_reservas,
        render_public_note,
    )


def _render_super_admin_agenda_list_filters(bid_ctx, opciones_filtro_barberos_ui, barberos):
    view_type = st.radio(
        "Modo de vista",
        ["Tarjetas", "Calendario"],
        horizontal=True,
        key="super_view_type",
    )

    filtro_su = st.selectbox(
        "Filtrar por barbero",
        opciones_filtro_barberos_ui(bid_ctx) if bid_ctx else ["Todos"] + list(barberos.keys()),
        key="tabla_super_filtro",
    )
    return view_type, filtro_su


def _render_super_admin_agenda_list_card_actions(
    rows_su,
    mostrar_reservas_dataframe,
    ui_marcar_pagado_reservas,
    ui_eliminar_reserva_lista,
):
    mostrar_reservas_dataframe(rows_su)
    ui_marcar_pagado_reservas(rows_su, "super_panel")
    ui_eliminar_reserva_lista(rows_su, "super_panel")


def _render_super_admin_agenda_list_results(
    view_type,
    rows_su,
    mostrar_reservas_dataframe,
    ui_marcar_pagado_reservas,
    ui_eliminar_reserva_lista,
    mostrar_calendario_reservas,
    render_public_note,
):
    if not rows_su:
        render_panel_empty_state(
            "Sin reservas para este filtro",
            "Revisa el contexto activo o cambia el filtro para consultar otros resultados.",
        )
        return

    if view_type == "Tarjetas":
        _render_super_admin_agenda_list_card_actions(
            rows_su,
            mostrar_reservas_dataframe,
            ui_marcar_pagado_reservas,
            ui_eliminar_reserva_lista,
        )
        return

    _render_agenda_calendar_results(
        rows_su,
        mostrar_calendario_reservas,
        render_public_note,
    )


def render_super_admin_agenda_list_tab(
    *,
    bid_ctx,
    usuario,
    db_ok,
    barberos,
    opciones_filtro_barberos_ui,
    listar_reservas_filtradas,
    mostrar_reservas_dataframe,
    ui_marcar_pagado_reservas,
    ui_eliminar_reserva_lista,
    mostrar_calendario_reservas,
    render_public_note,
):
    st.markdown("### Reservas")

    if not db_ok:
        render_alert(
            "No se puede cargar el listado de reservas mientras la base de datos no está disponible.",
            alert_type="info",
            title="Modo demo",
        )
        return

    view_type, filtro_su = _render_super_admin_agenda_list_filters(
        bid_ctx,
        opciones_filtro_barberos_ui,
        barberos,
    )
    with st.spinner("Cargando reservas..."):
        rows_su = listar_reservas_filtradas(
            bid_ctx,
            "SUPER_ADMIN",
            usuario,
            filtro_barbero=filtro_su,
        )

    _render_super_admin_agenda_list_results(
        view_type,
        rows_su,
        mostrar_reservas_dataframe,
        ui_marcar_pagado_reservas,
        ui_eliminar_reserva_lista,
        mostrar_calendario_reservas,
        render_public_note,
    )

