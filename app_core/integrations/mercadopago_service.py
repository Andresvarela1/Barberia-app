"""
MercadoPago integration helpers.

Provides token loading, SDK initialization, amount validation, and
preference-response parsing utilities used by payment_service.

NOTE: webhook.py is a separate FastAPI runtime (no Streamlit, own psycopg2
pool) and intentionally does NOT import from app_core to avoid mixing
runtimes. It reads MERCADOPAGO_ACCESS_TOKEN directly via os.getenv().
"""

import logging
import os

logger = logging.getLogger(__name__)

try:
    import mercadopago as _mp_sdk
except ImportError:
    _mp_sdk = None


def get_sdk():
    """
    Load MERCADOPAGO_ACCESS_TOKEN from env and return an initialized SDK.

    Returns:
        mercadopago.SDK instance, or None if SDK unavailable or token missing.
    """
    if _mp_sdk is None:
        logger.error(
            "MercadoPago SDK no está instalado. Ejecuta: pip install mercadopago"
        )
        return None

    access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "").strip()
    if not access_token:
        logger.error(
            "MERCADOPAGO_ACCESS_TOKEN no configurado. "
            "Agrega a .env: MERCADOPAGO_ACCESS_TOKEN=tu_token"
        )
        return None

    token_preview = access_token[:10] + "..." if len(access_token) > 10 else access_token
    logger.info(f"Token cargado: {token_preview}")
    return _mp_sdk.SDK(access_token)


def validate_monto(monto):
    """
    Validate and coerce a payment amount to a positive float.

    Args:
        monto: Raw amount value (str, int, or float).

    Returns:
        Positive float value.

    Raises:
        ValueError: If monto cannot be converted or is <= 0.
    """
    value = float(monto)
    if value <= 0:
        raise ValueError("Monto debe ser mayor a 0")
    return value


def extract_init_point(preference_response):
    """
    Extract the checkout URL (init_point) from a MercadoPago preference response.

    Args:
        preference_response: Raw dict returned by sdk.preference().create(...)

    Returns:
        init_point URL string, or None if the response structure is invalid.
        Callers should check for None and surface an appropriate error.
    """
    if not isinstance(preference_response, dict):
        logger.error(
            f"Respuesta inválida de MercadoPago: tipo {type(preference_response)}"
        )
        return None

    response_status = preference_response.get("status")
    if response_status != 201:
        logger.error(
            f"MercadoPago error (status {response_status}): {preference_response}"
        )
        return None

    response_data = preference_response.get("response")
    if response_data is None:
        logger.error(
            f"No 'response' en respuesta de MercadoPago: {preference_response}"
        )
        return None

    init_point = response_data.get("init_point")
    if not init_point:
        logger.error(
            f"No 'init_point' en response de MercadoPago: {response_data}"
        )
        return None

    return init_point
