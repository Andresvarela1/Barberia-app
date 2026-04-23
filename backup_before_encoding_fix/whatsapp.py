import logging
import os

logger = logging.getLogger(__name__)

def enviar_whatsapp(numero, mensaje):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

    if not account_sid or not auth_token or not whatsapp_number:
        logger.error(
            "Faltan variables de entorno de Twilio: "
            "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN y/o TWILIO_WHATSAPP_NUMBER"
        )
        return False

    if not whatsapp_number.startswith("whatsapp:"):
        whatsapp_number = f"whatsapp:{whatsapp_number}"

    if not numero.startswith("whatsapp:"):
        numero = f"whatsapp:{numero}"

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)

        logger.info("Enviando WhatsApp desde %s hacia %s", whatsapp_number, numero)

        client.messages.create(
            from_=whatsapp_number,
            body=mensaje,
            to=numero,
        )

        logger.info("WhatsApp enviado correctamente")
        return True

    except ImportError:
        logger.error("Twilio no esta instalado en este entorno.")
        return False
    except Exception as e:
        logger.exception("Error Twilio: %s", e)
        return False
