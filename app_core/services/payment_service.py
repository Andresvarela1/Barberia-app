"""
Payment service: MercadoPago helpers and reservation payment marking.

Extracted from app.py. Business logic and side-effects unchanged.
"""
import logging
import os

import streamlit as st

try:
    import mercadopago
except ImportError:
    mercadopago = None

from app_core.db.safe_queries import execute_write
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

    if rol_u == "BARBERO" and prev[2] != uid:

        st.error("Sin permiso.")

        return False

    if rol_u == "ADMIN" and prev[7] != st.session_state.get("barberia_id"):

        st.error("Sin permiso.")

        return False

    if rol_u == "CLIENTE":

        st.error("Sin permiso.")

        return False

    try:

        # ALL roles must update with barberia_id filter - NO EXCEPTIONS!

        barberia_id_from_reserva = prev.get("barberia_id") or prev[7]


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

    # Validate SDK is available

    if not mercadopago:

        error_msg = "MercadoPago SDK no está instalado. Ejecuta: pip install mercadopago"

        logger.error(error_msg)

        if show_errors:

            st.error(error_msg)

        return None


    # Load and validate access token

    access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

    if not access_token or access_token.strip() == "":

        error_msg = "MERCADOPAGO_ACCESS_TOKEN no configurado. Agrega a .env: MERCADOPAGO_ACCESS_TOKEN=tu_token"

        logger.error(error_msg)

        if show_errors:

            st.error(error_msg)

        return None


    # Debug: Show token was loaded (masked)

    token_preview = access_token[:10] + "..." if len(access_token) > 10 else access_token

    logger.info(f"Token Token cargado: {token_preview}")


    try:

        # Initialize SDK

        sdk = mercadopago.SDK(access_token)


        # Validate payment amount

        try:

            monto_float = float(monto)

            if monto_float <= 0:

                raise ValueError("Monto debe ser mayor a 0")

        except (ValueError, TypeError) as e:

            error_msg = f"Monto inválido: {monto}. Error: {str(e)}"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


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


        # Validate response structure

        if not isinstance(preference_response, dict):

            error_msg = f"Respuesta inválida de MercadoPago: tipo {type(preference_response)}"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


        # Check status code

        response_status = preference_response.get("status")

        if response_status != 201:

            error_msg = f"MercadoPago error (status {response_status}): {preference_response}"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


        # Extract init_point

        if "response" not in preference_response:

            error_msg = f"No 'response' en respuesta de MercadoPago: {preference_response}"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


        response_data = preference_response["response"]

        if "init_point" not in response_data:

            error_msg = f"No 'init_point' en response de MercadoPago: {response_data}"

            logger.error(error_msg)

            if show_errors:

                st.error(error_msg)

            return None


        init_point = response_data.get("init_point")

        if not init_point:

            error_msg = "init_point es vacío en respuesta de MercadoPago"

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
