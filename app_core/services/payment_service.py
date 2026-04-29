"""
Payment service: MercadoPago helpers and reservation payment marking.

Extracted from app.py. Business logic and side-effects unchanged.
"""
import logging
import os

import streamlit as st

from app_core.db.safe_queries import execute_write
from app_core.integrations.mercadopago_service import get_sdk, validate_monto, extract_init_point
from app_core.services.booking_service import obtener_reserva_por_id
from app_core.security.tenant_access import normalizar_rol, enforce_access

logger = logging.getLogger(__name__)


def marcar_reserva_pagada(reserva_id):

    if not st.session_state.get("db_available", True):

        return False

    user = st.session_state.get("user")

    if not user:

        return False

    prev = obtener_reserva_por_id(reserva_id)

    if not prev:

        st.error("Reserva no encontrada.")

        return False

    rol_u = normalizar_rol(user[3])

    uid = user[1]

    if rol_u == "BARBERO" and prev.get("barbero") != uid:

        st.error("Sin permiso.")

        return False

    if rol_u == "ADMIN" and prev.get("barberia_id") != st.session_state.get("barberia_id"):

        st.error("Sin permiso.")

        return False

    if rol_u == "CLIENTE":

        st.error("Sin permiso.")

        return False

    try:

        # ALL roles must update with barberia_id filter - NO EXCEPTIONS!

        barberia_id_from_reserva = prev.get("barberia_id")


        # CRITICAL: Enforce barberia context for SUPER_ADMIN too

        if rol_u == "SUPER_ADMIN":

            enforce_access(barberia_id_from_reserva)


        return bool(

            execute_write(

                """

                UPDATE reservas

                SET pagado = TRUE, monto = COALESCE(monto, precio)

                WHERE id = %s AND barberia_id = %s

                """,

                (reserva_id, barberia_id_from_reserva),

            )

        )

    except Exception as e:

        logger.exception("marcar_reserva_pagada")

        st.error(str(e))

        return False

def crear_pago_mercadopago(reserva_id, monto, descripcion, cliente_email=None, show_errors=True):

    """

    Create MercadoPago payment preference and return checkout URL.


    Args:

        reserva_id: Reservation ID

        monto: Payment amount in CLP

        descripcion: Service description

        cliente_email: Customer email (optional)

        show_errors: Whether to show st.error() messages (True for UI, False for backend)


    Returns:

        URL to MercadoPago checkout, or None if error

    """

    # Initialize SDK (validates token + SDK availability internally)

    sdk = get_sdk()

    if sdk is None:

        error_msg = "No se pudo inicializar MercadoPago SDK. Verifica MERCADOPAGO_ACCESS_TOKEN."

        logger.error(error_msg)

        if show_errors:

            st.error(error_msg)

        return None


    # Validate payment amount

    try:

        monto_float = validate_monto(monto)

    except (ValueError, TypeError) as e:

        error_msg = f"Monto inválido: {monto}. Error: {str(e)}"

        logger.error(error_msg)

        if show_errors:

            st.error(error_msg)

        return None


    try:


        # Build preference data

        preference_data = {

            "items": [

                {

                    "title": str(descripcion)[:256],  # MercadoPago title max 256 chars

                    "quantity": 1,

                    "currency_id": "CLP",

                    "unit_price": monto_float

                }

            ],

            "external_reference": str(reserva_id),

            "notification_url": "https://splendid-morphine-maximize.ngrok-free.dev/webhook",

        }


        # Add back URLs if configured

        success_url = os.getenv("MERCADOPAGO_SUCCESS_URL")

        failure_url = os.getenv("MERCADOPAGO_FAILURE_URL")

        pending_url = os.getenv("MERCADOPAGO_PENDING_URL")


        if success_url or failure_url or pending_url:

            preference_data["back_urls"] = {

                "success": success_url or "https://barberia-app.com/success",

                "failure": failure_url or "https://barberia-app.com/failure",

                "pending": pending_url or "https://barberia-app.com/pending"

            }


        # Add payer email if provided

        if cliente_email and "@" in str(cliente_email):

            preference_data["payer"] = {"email": str(cliente_email)}


        logger.info(f"Enviando preference a MercadoPago para reserva {reserva_id}...")


        # Create preference

        preference_response = sdk.preference().create(preference_data)

        logger.info(f"Respuesta de MercadoPago: {preference_response}")


        # Validate response and extract init_point

        init_point = extract_init_point(preference_response)

        if init_point is None:

            error_msg = f"Respuesta inválida de MercadoPago para reserva {reserva_id}: {preference_response}"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


        logger.info(f"[OK] Pago creado para reserva {reserva_id}: {init_point}")

        return init_point


    except Exception as e:

        error_msg = f"Error creando pago MercadoPago para reserva {reserva_id}: {str(e)}"

        logger.exception(error_msg)

        if show_errors:

            st.error(error_msg)

        return None
