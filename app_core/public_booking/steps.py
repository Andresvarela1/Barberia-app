"""Step renderers for the public booking flow."""

import logging
from datetime import datetime, timedelta

import streamlit as st

from app_core.db.safe_queries import fetch_all
from app_core.public_booking.state import (
    go_to_booking_step,
    reset_booking_flow,
    update_booking_data,
)
from app_core.services.availability_service import (
    obtener_barberos_disponibles,
    obtener_horarios_disponibles,
)
from design_system import (
    render_barber_selector,
    render_booking_container,
    render_booking_header,
    render_booking_section,
    render_cta_section,
    render_form_group,
    render_loading_panel,
    render_public_booking_summary,
    render_public_note,
    render_public_payment_notice,
    render_step_indicator,
    render_time_chips,
)


logger = logging.getLogger("barberia_app")


def render_step_1_service_selection(servicios):
    render_step_indicator(1, 6, ["Servicio", "Barbero", "Hora", "Datos", "Revisar", "Confirmar"])
    render_booking_header(
        title="¿Qué servicio deseas?",
        subtitle="Elige una de nuestras especialidades",
        step=1,
        total_steps=6,
    )
    with render_booking_section():
        cols = st.columns(2)
        services = list(servicios.keys())
        if not services:
            st.info("No hay servicios disponibles para reservar en este momento.")
            return
        for idx, service in enumerate(services):
            with cols[idx % 2]:
                config = servicios[service]
                precio_fmt = f"${config['precio']:,}".replace(",", ".")
                if st.button(
                    f"{service}\n\n{config['duracion']} min · {precio_fmt}",
                    key=f"svc_{service}",
                    use_container_width=True,
                ):
                    update_booking_data("servicio", service)
                    update_booking_data("duracion", config["duracion"])
                    update_booking_data("precio", config["precio"])
                    go_to_booking_step(2)
                    st.rerun()


def render_step_2_barber_selection(barberia_id):
    render_step_indicator(2, 6, ["Servicio", "Barbero", "Hora", "Datos", "Resumen", "[OK] Listo!"])
    render_booking_header("Selecciona tu barbero", "¿Con quién quieres tu corte?", step=2, total_steps=6)
    with render_booking_container():
        if st.button("<- Cambiar servicio", key="back_to_svc"):
            go_to_booking_step(1)
            st.rerun()

    if st.session_state.booking_data.get("servicio"):
        servicio_nombre = st.session_state.booking_data["servicio"]
        servicio_duracion = st.session_state.booking_data.get("duracion", 0)
        servicio_precio = st.session_state.booking_data.get("precio", 0)
        precio_fmt = f"${servicio_precio:,}".replace(",", ".")
        st.info(f"Servicio: {servicio_nombre} | Duración: {servicio_duracion} min | Precio: {precio_fmt}")

    barberos = obtener_barberos_disponibles(barberia_id)
    if not barberos:
        st.info("Mostrando todos los barberos disponibles...")
        try:
            barberos = fetch_all(
                """
                SELECT id, usuario AS nombre FROM usuarios
                WHERE barberia_id = %s AND UPPER(TRIM(rol)) = 'BARBERO'
                ORDER BY usuario
                """,
                (barberia_id,),
            )
            logger.warning(f"Step 2 - Fallback query returned {len(barberos) if barberos else 0} barbers: {barberos}")
        except Exception as e:
            logger.exception(f"Step 2 - Fallback query failed: {str(e)}")
            barberos = []

    if not barberos:
        st.error("No hay barberos disponibles. Contacta al local.")
        st.stop()
        return

    st.markdown("### Selecciona tu barbero")
    if "barber_selection_loading" not in st.session_state:
        st.session_state.barber_selection_loading = False

    if st.session_state.barber_selection_loading:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            render_loading_panel("Seleccionando barbero...", padding="20px")
        import time

        time.sleep(0.2)
        go_to_booking_step(3)
        st.session_state.barber_selection_loading = False
        st.rerun()

    def on_barber_selected(barbero_id, barbero_nombre):
        update_booking_data("barbero_id", barbero_id)
        update_booking_data("barbero_nombre", barbero_nombre)
        st.session_state.barber_selection_loading = True

    selected = render_barber_selector(
        barbers=barberos,
        selected_id=st.session_state.booking_data.get("barbero_id"),
        icon="Tijeras",
        on_select_callback=on_barber_selected,
    )

    if selected:
        update_booking_data("barbero_id", selected[0])
        update_booking_data("barbero_nombre", selected[1])
        st.session_state.barber_selection_loading = True
        st.rerun()


def render_step_3_datetime_selection(barberia_id):
    from datetime import time as time_type

    render_step_indicator(3, 6, ["Servicio", "Barbero", "Hora", "Datos", "Resumen", "[OK] Listo!"])
    render_booking_header("Elige tu fecha y hora", "Cuándo te gustaría venir?", step=3, total_steps=6)
    with render_booking_container():
        if st.button("<- Volver a barbero", key="back_to_brb"):
            go_to_booking_step(2)
            st.rerun()
        fecha = st.date_input(
            "Selecciona una fecha",
            value=st.session_state.selected_fecha,
            min_value=datetime.now().date(),
            max_value=datetime.now().date() + timedelta(days=30),
            key="booking_fecha_premium",
            label_visibility="collapsed",
        )

    st.session_state.selected_fecha = fecha
    horarios = obtener_horarios_disponibles(
        barberia_id,
        st.session_state.booking_data["barbero_id"],
        fecha,
        st.session_state.booking_data["duracion"],
    )

    if not horarios:
        st.warning("No hay horarios disponibles para esta fecha. Selecciona otra fecha.")
        st.stop()
        return

    num_slots = len(horarios)
    if num_slots <= 4:
        st.warning("Quedan pocos horarios disponibles hoy")

    st.markdown(f"Horarios disponibles ({num_slots})")
    if "booking_time_loading" not in st.session_state:
        st.session_state.booking_time_loading = False

    def on_time_selected_callback(time_obj):
        import time as time_module

        time_module.sleep(0.2)
        try:
            if isinstance(time_obj, datetime):
                hora_final = time_obj.time()
            elif isinstance(time_obj, time_type):
                hora_final = time_obj
            else:
                raise ValueError(f"Invalid hora type: {type(time_obj)}")

            update_booking_data("fecha", fecha)
            update_booking_data("hora", hora_final)
            logger.info(f"Booking time set: {type(time_obj).__name__} -> {hora_final}")
        except Exception as e:
            logger.error(f"Error setting booking time: {str(e)}")
            st.error(f"Error al seleccionar hora: {str(e)}")
            st.stop()
            return

        go_to_booking_step(4)
        st.rerun()

    render_time_chips(
        available_times=horarios,
        selected_time=st.session_state.booking_data.get("hora"),
        on_time_selected=on_time_selected_callback,
        columns=5,
    )


def render_step_4_customer_form():
    render_step_indicator(4, 6, ["Servicio", "Barbero", "Hora", "Datos", "Resumen", "[OK] Listo!"])
    render_booking_header("Tu información", "Necesitamos tus datos para la reserva", step=4, total_steps=6)
    with render_booking_container():
        if st.button("<- Volver a horario", key="back_to_time"):
            go_to_booking_step(3)
            st.rerun()
        with st.form("booking_form_premium"):
            nombre = render_form_group(
                "Nombre",
                "Ej: Juan Pérez",
                "Nombre completo",
                placeholder="Ej: Juan Pérez",
                key="booking_nombre_premium",
                help="Nombre como aparecerá en tu reserva",
            )
            telefono = render_form_group(
                "Teléfono",
                "Ej: +56 9 1234 5678",
                "Teléfono",
                placeholder="Ej: +56 9 1234 5678",
                key="booking_telefono_premium",
                help="Usaremos este número para confirmarte",
            )
            email = render_form_group(
                "Email",
                "Ej: tu@email.com",
                "Email (opcional)",
                placeholder="Ej: tu@email.com",
                key="booking_email_premium",
                help="Para recibir confirmación de tu reserva",
            )

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                submit_btn = st.form_submit_button("Ver resumen", use_container_width=True, type="primary")
                if submit_btn:
                    errors = []
                    if not nombre or len(nombre) < 3:
                        errors.append("Nombre debe tener al menos 3 caracteres")
                    if not telefono or len(telefono.replace("+", "").replace(" ", "").replace("-", "")) < 9:
                        errors.append("Teléfono debe tener al menos 9 dígitos")
                    if email and "@" not in email:
                        errors.append("Email no válido")

                    if errors:
                        st.error("Revisa los siguientes errores:\n" + "\n".join(errors))
                    else:
                        update_booking_data("nombre", nombre)
                        update_booking_data("telefono", telefono)
                        update_booking_data("email", email)
                        go_to_booking_step(5)
                        st.rerun()


def render_step_5_review(
    barberia_id,
    insertar_reserva_con_fecha_hora,
    crear_pago_mercadopago,
    normalizar_texto,
):
    render_step_indicator(5, 6, ["Servicio", "Barbero", "Hora", "Datos", "Resumen", "[OK] Listo!"])
    render_booking_header("Revisa tu reserva", "Verifica que todo esté correcto", step=5, total_steps=6)
    with render_booking_container():
        with render_booking_section("Detalles de tu cita"):
            st.write(f"**Servicio:** {st.session_state.booking_data.get('servicio')}")
            st.write(f"**Barbero:** {st.session_state.booking_data.get('barbero_nombre')}")
            st.write(f"**Fecha:** {st.session_state.booking_data.get('fecha')} a las {st.session_state.booking_data.get('hora')}")
            st.write(f"**Precio:** ${st.session_state.booking_data.get('precio', 0):,}")
        data = st.session_state.booking_data

        st.markdown("## Tus datos")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Nombre", value=data.get('nombre', 'N/A'), disabled=True)
        with col2:
            st.text_input("Teléfono", value=data.get('telefono', 'N/A'), disabled=True)
        with col3:
            st.text_input("Email", value=data.get('email', 'N/A') or "-", disabled=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancelar", key="cancel_booking_step5", use_container_width=True):
                reset_booking_flow()
                st.rerun()

        with col2:
            if st.button("Agendar mi cita", key="confirm_booking_step5", use_container_width=True, type="primary", help="Confirma tu reserva"):
                with st.spinner("Creando tu reserva..."):
                    reserva_id = insertar_reserva_con_fecha_hora(
                        barberia_id,
                        normalizar_texto(data.get('nombre', '')),
                        data.get('barbero_id'),
                        data.get('barbero_nombre'),
                        data.get('servicio'),
                        data.get('fecha'),
                        data.get('hora'),
                        data.get('precio'),
                        data.get('duracion'),
                    )

                    if reserva_id:
                        with st.spinner("Generando enlace de pago..."):
                            pago_url = crear_pago_mercadopago(
                                reserva_id,
                                data.get('precio', 0),
                                f"Reserva barbería: {data.get('servicio')}",
                                data.get('email'),
                                show_errors=True,
                            )

                            if pago_url:
                                update_booking_data("pago_url", pago_url)
                                update_booking_data("pago_pendiente", False)
                                st.session_state.booking_data.pop("pago_mensaje", None)
                            else:
                                update_booking_data("pago_url", None)
                                update_booking_data("pago_pendiente", True)
                                update_booking_data("pago_mensaje", "Reserva creada, pago pendiente")
                            go_to_booking_step(6)
                            update_booking_data("reserva_id", reserva_id)
                            st.rerun()
                    else:
                        st.error("Error al crear la reserva. Intenta nuevamente.")


def render_step_6_confirmation():
    data = st.session_state.booking_data
    render_step_indicator(6, 6, ["Servicio", "Barbero", "Hora", "Datos", "Resumen", "[OK] Listo!"])
    render_booking_header("[OK] Reserva confirmada!", "Tu cita está lista", step=6, total_steps=6)
    with render_booking_container():
        st.balloons()
        render_cta_section(
            "[OK] Reserva confirmada!",
            "Tu cita ha sido programada con éxito. Te hemos enviado un WhatsApp con la confirmación.",
            "👍",
        )
        if data.get('pago_url'):
            render_public_payment_notice()
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.link_button(
                    "Pagar ahora",
                    url=data.get('pago_url', '#'),
                    use_container_width=True,
                    help="Finaliza el pago en MercadoPago",
                )
            st.markdown('<p class="public-payment-helper">Pago seguro con MercadoPago · No guardamos datos de tu tarjeta</p>', unsafe_allow_html=True)
        elif data.get("pago_pendiente"):
            st.warning("Reserva creada, pago pendiente. Contacta al local para coordinar el pago.")

    render_public_note("Te enviamos la confirmación a WhatsApp. Revisa tu teléfono para más detalles.")
    with st.expander("Ver detalles de tu cita", expanded=False):
        render_public_booking_summary(data)
    render_public_note("Más de 100 clientes ya reservaron online.", warning=False)
    render_public_note("Tu hora está reservada. Recibirás confirmación por WhatsApp y puedes cancelar hasta 24h antes.", warning=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Volver al inicio", key="home_booking_step6", use_container_width=True):
            reset_booking_flow()
            st.rerun()
    with col2:
        if st.button("Otra cita", key="new_booking_step6", use_container_width=True):
            reset_booking_flow()
            st.rerun()
