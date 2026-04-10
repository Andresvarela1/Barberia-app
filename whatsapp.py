import logging
import os

logger = logging.getLogger(__name__)

def enviar_whatsapp(numero, mensaje):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

    # Validar variables de entorno
    if not account_sid or not auth_token or not whatsapp_number:
        print("❌ Faltan variables de entorno de Twilio")
        return False

    # 🔥 EVITAR DOBLE "whatsapp:"
    if not whatsapp_number.startswith("whatsapp:"):
        whatsapp_number = f"whatsapp:{whatsapp_number}"

    if not numero.startswith("whatsapp:"):
        numero = f"whatsapp:{numero}"

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)

        print("📲 Enviando WhatsApp...")
        print("FROM:", whatsapp_number)
        print("TO:", numero)

        client.messages.create(
            from_=whatsapp_number,
            body=mensaje,
            to=numero,
        )

        print("✅ WhatsApp enviado correctamente")
        return True

    except ImportError:
        logger.error("Twilio no esta instalado en este entorno.")
        return False
    except Exception as e:
        print("❌ ERROR TWILIO:", e)
        return False
