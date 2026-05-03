"""Coordinator for the public booking flow."""

import streamlit as st

from app_core.public_booking.state import (
    go_to_booking_step,
    init_booking_state,
    update_booking_data,
)
from app_core.public_booking.steps import (
    render_step_1_service_selection,
    render_step_2_barber_selection,
    render_step_3_datetime_selection,
    render_step_4_customer_form,
    render_step_5_review,
    render_step_6_confirmation,
)
from app_core.security.tenant_access import effective_barberia_id
from design_system import apply_public_booking_css


def flujo_reserva_publica(
    obtener_servicios,
    insertar_reserva_con_fecha_hora,
    crear_pago_mercadopago,
    normalizar_texto,
):
    """Premium public booking flow without login required (AgendaPro style)."""
    apply_public_booking_css()
    init_booking_state()

    if "preselected_service" in st.session_state and st.session_state.preselected_service:
        preselected = st.session_state.preselected_service
        if preselected.get("nombre"):
            if not st.session_state.booking_data.get("servicio"):
                update_booking_data("servicio", preselected["nombre"])
                update_booking_data("duracion", preselected["duracion"])
                update_booking_data("precio", preselected["precio"])
                go_to_booking_step(2)
                st.session_state.preselected_service = None
                st.rerun()

    barberia_id = effective_barberia_id()
    if not barberia_id:
        st.error("Barbería no disponible. Contacta al administrador.")
        return

    servicios_list = obtener_servicios(barberia_id)
    servicios = {
        s["nombre"]: {"duracion": s.get("duracion") or s.get("duracion_minutos"), "precio": s["precio"]}
        for s in servicios_list if isinstance(servicios_list, list) and len(s) > 0
    }
    if not servicios:
        servicios = {}

    total_booking_steps = 6
    progress = (st.session_state.booking_step - 1) / (total_booking_steps - 1) * 100
    st.progress(int(progress) / 100, text=f"Paso {st.session_state.booking_step} de {total_booking_steps}")

    if st.session_state.booking_step == 1:
        render_step_1_service_selection(servicios)
    elif st.session_state.booking_step == 2:
        render_step_2_barber_selection(barberia_id)
    elif st.session_state.booking_step == 3:
        render_step_3_datetime_selection(barberia_id)
    elif st.session_state.booking_step == 4:
        render_step_4_customer_form()
    elif st.session_state.booking_step == 5:
        render_step_5_review(
            barberia_id,
            insertar_reserva_con_fecha_hora,
            crear_pago_mercadopago,
            normalizar_texto,
        )
    elif st.session_state.booking_step == 6:
        render_step_6_confirmation()
