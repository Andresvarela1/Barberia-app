"""Public booking session state helpers."""

from datetime import datetime

import streamlit as st


def init_booking_state():
    if "booking_step" not in st.session_state:
        st.session_state.booking_step = 1
    if "booking_data" not in st.session_state:
        st.session_state.booking_data = {}
    if "selected_fecha" not in st.session_state:
        st.session_state.selected_fecha = datetime.now().date()


def reset_booking_flow():
    st.session_state.booking_step = 1
    st.session_state.booking_data = {}
    st.session_state.selected_fecha = datetime.now().date()


def go_to_booking_step(step):
    st.session_state.booking_step = step


def update_booking_data(key, value):
    st.session_state.booking_data[key] = value


def can_advance_to_step(step):
    data = st.session_state.get("booking_data", {})
    requirements = {
        2: ["servicio", "duracion", "precio"],
        3: ["servicio", "duracion", "precio", "barbero_id", "barbero_nombre"],
        4: ["servicio", "duracion", "precio", "barbero_id", "barbero_nombre", "fecha", "hora"],
        5: ["servicio", "duracion", "precio", "barbero_id", "barbero_nombre", "fecha", "hora", "nombre", "telefono"],
        6: ["reserva_id"],
    }
    return all(data.get(key) for key in requirements.get(step, []))
