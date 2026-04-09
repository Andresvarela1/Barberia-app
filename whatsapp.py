import logging
import os

from twilio.rest import Client


logger = logging.getLogger(__name__)


def enviar_whatsapp(numero, mensaje):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

    if not account_sid or not auth_token or not whatsapp_number:
        logger.error(
            "Faltan variables de entorno requeridas: "
            "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN y/o TWILIO_WHATSAPP_NUMBER."
        )
        return False

    try:
        client = Client(account_sid, auth_token)
        client.messages.create(
            from_=f"whatsapp:{whatsapp_number}",
            body=mensaje,
            to=f"whatsapp:{numero}",
        )
        return True
    except Exception as exc:
        logger.error("Error al enviar WhatsApp: %s", exc)
        return False
