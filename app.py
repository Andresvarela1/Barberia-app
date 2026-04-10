import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import logging
import os
import psycopg2
from whatsapp import enviar_whatsapp as enviar_whatsapp_twilio
st.write("SUPABASE ACTIVADO")
st.set_page_config(layout="wide")

logger = logging.getLogger("barberia_app")

if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# ------------------ DB ------------------
def get_database_url():
    return os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")


@st.cache_resource
def get_connection():
    database_url = get_database_url()
    if not database_url:
        raise RuntimeError("Falta DATABASE_URL o SUPABASE_DB_URL para conectar PostgreSQL.")
    return psycopg2.connect(database_url)


conn = get_connection()
c = conn.cursor()

def get_default_barberia_id():
    c.execute("SELECT id FROM barberias ORDER BY id LIMIT 1")
    row = c.fetchone()
    return row[0] if row else None


default_barberia_id = get_default_barberia_id()

# ------------------ DATOS ------------------
barberos = {
    "Andrea": "#FF5733",
    "Andres": "#33C1FF",
    "Yor": "#33FF57",
    "Maikel": "#F333FF"
}

servicios = {
    "Corte": {"duracion": 45, "precio": 15000},
    "Barba": {"duracion": 30, "precio": 10000},
    "Corte + Barba": {"duracion": 60, "precio": 20000}
}

# ------------------ FUNCIONES ------------------

def login(usuario, password):
    c.execute("SELECT * FROM usuarios WHERE usuario=%s AND password=%s", (usuario, password))
    return c.fetchone()

def registrar(usuario, password, rol, telefono=None, barberia_id=None):
    barberia_id = barberia_id or default_barberia_id
    c.execute(
        "INSERT INTO usuarios (usuario, password, rol, telefono, barberia_id) VALUES (%s, %s, %s, %s, %s)",
        (usuario, password, rol, telefono, barberia_id),
    )
    conn.commit()


def obtener_telefono_usuario(usuario):
    c.execute("SELECT telefono FROM usuarios WHERE usuario=%s", (usuario,))
    row = c.fetchone()
    return row[0] if row and row[0] else None


def registrar_fidelizacion(usuario, barberia_id):
    c.execute(
        """
        UPDATE usuarios
        SET cortes_acumulados = COALESCE(cortes_acumulados, 0) + 1
        WHERE usuario = %s AND barberia_id = %s
        RETURNING cortes_acumulados
        """,
        (usuario, barberia_id),
    )
    row = c.fetchone()
    conn.commit()
    return row[0] if row else None


def procesar_beneficio_fidelizacion(usuario, barberia_id):
    cortes_acumulados = registrar_fidelizacion(usuario, barberia_id)
    if cortes_acumulados is None or cortes_acumulados < 5:
        return

    c.execute(
        """
        UPDATE usuarios
        SET cortes_acumulados = 0
        WHERE usuario = %s AND barberia_id = %s
        """,
        (usuario, barberia_id),
    )
    conn.commit()

    telefono_cliente = obtener_telefono_usuario(usuario)
    if telefono_cliente:
        try:
            enviar_whatsapp_twilio(
                telefono_cliente,
                "🔥 ¡Tienes un descuento en tu próximo corte!",
            )
        except Exception as exc:
            logger.error("Error al enviar beneficio de fidelizacion: %s", exc)


def construir_mensaje_reserva(nombre, inicio, barbero, servicio):
    return (
        f"Hola {nombre}, tu reserva fue confirmada.\n"
        f"Fecha: {inicio.strftime('%d-%m-%Y')}\n"
        f"Hora: {inicio.strftime('%H:%M')}\n"
        f"Barbero: {barbero}\n"
        f"Servicio: {servicio}"
    )

def obtener_reservas():
    barberia_id = st.session_state.get("barberia_id")
    if not barberia_id:
        return []

    c.execute(
        "SELECT * FROM reservas WHERE barberia_id = %s",
        (barberia_id,),
    )
    data = c.fetchall()
    eventos = []

    for r in data:
        eventos.append({
            "id": r[0],
            "title": f"{r[1]} - {r[3]} ({r[2]})",
            "start": r[5],
            "end": r[6],
            "color": barberos.get(r[2], "#999")
        })

    return eventos

def guardar_reserva(nombre, barbero, servicio, precio, inicio, fin):
    barberia_id = st.session_state.get("barberia_id")
    if not barberia_id:
        return

    c.execute(
        """
        INSERT INTO reservas (nombre, barbero, servicio, precio, inicio, fin, barberia_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (nombre, barbero, servicio, precio, inicio, fin, barberia_id),
    )
    conn.commit()

# ------------------ LOGIN ------------------

if "user" not in st.session_state:
    st.session_state.user = None
if "barberia_id" not in st.session_state:
    st.session_state.barberia_id = None

if not st.session_state.user:

    st.title("💈 Barbería Leveling")

    opcion = st.radio("Opción", [
        "Iniciar sesión",
        "Registrarse (Barbero)",
        "Registrarse (Cliente)"
    ])

    if opcion == "Iniciar sesión":
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Entrar"):
            user = login(usuario, password)
            if user:
                st.session_state.user = user
                st.session_state.barberia_id = user[5] if len(user) > 5 else None
                st.success("Bienvenido 🔥")
                st.rerun()
            else:
                st.error("Datos incorrectos")

    elif opcion == "Registrarse (Barbero)":
        nuevo_user = st.text_input("Usuario barbero")
        nuevo_pass = st.text_input("Contraseña", type="password")

        if st.button("Crear cuenta barbero"):
            registrar(nuevo_user, nuevo_pass, "barbero")
            st.success("Barbero creado")

    elif opcion == "Registrarse (Cliente)":
        st.subheader("Registro de cliente")

        nuevo_user = st.text_input("Usuario cliente")
        nuevo_pass = st.text_input("Contraseña", type="password")
        telefono = st.text_input("WhatsApp (+569XXXXXXXX)")

        if st.button("Crear cuenta cliente"):
            if not telefono.startswith("+") or len(telefono) < 10:
                st.error("Número inválido. Usa formato +569XXXXXXXX")
            else:
                registrar(nuevo_user, nuevo_pass, "cliente", telefono)
                st.success("Cliente creado con teléfono 📲")

# ------------------ APP ------------------

else:
    user = st.session_state.user
    rol = user[3]
    usuario = user[1]
    barberia_id = st.session_state.get("barberia_id")

    st.sidebar.write(f"👤 {usuario} ({rol})")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.user = None
        st.session_state.barberia_id = None
        st.rerun()

    eventos = obtener_reservas()

    # ================= CLIENTE =================
    if rol == "cliente":
        if not barberia_id:
            st.warning("No hay barberia asociada a la sesión.")
            st.stop()

        st.title("📲 Reservar hora")

        nombre = usuario
        barbero = st.selectbox("Barbero", list(barberos.keys()))
        servicio = st.selectbox("Servicio", list(servicios.keys()))

        fecha = st.date_input("Selecciona día")

        duracion = servicios[servicio]["duracion"]
        precio = servicios[servicio]["precio"]

        horarios_disponibles = []
        inicio_dia = datetime.combine(fecha, datetime.strptime("09:00", "%H:%M").time())

        for i in range(24):
            hora = inicio_dia + timedelta(minutes=15 * i)
            fin = hora + timedelta(minutes=duracion)

            if hora.hour >= 21:
                break

            c.execute(
                """
                SELECT * FROM reservas
                WHERE barberia_id = %s AND barbero = %s AND (%s < fin AND %s > inicio)
                """,
                (barberia_id, barbero, hora.isoformat(), fin.isoformat()),
            )

            if not c.fetchone():
                horarios_disponibles.append(hora)

        if horarios_disponibles:
            hora_sel = st.selectbox(
                "Horarios disponibles",
                horarios_disponibles,
                format_func=lambda x: x.strftime("%H:%M")
            )

            if st.button("Reservar"):
                inicio = hora_sel
                fin = inicio + timedelta(minutes=duracion)

                guardar_reserva(nombre, barbero, servicio, precio, inicio.isoformat(), fin.isoformat())
                procesar_beneficio_fidelizacion(usuario, barberia_id)
                telefono_cliente = user[4] if len(user) > 4 else obtener_telefono_usuario(usuario)
                if telefono_cliente:
                    mensaje = construir_mensaje_reserva(nombre, inicio, barbero, servicio)
                    try:
                        enviar_whatsapp_twilio(telefono_cliente, mensaje)
                    except Exception as exc:
                        logger.error("Error al ejecutar el envio de WhatsApp: %s", exc)
                st.success("Reserva creada ✅")

        else:
            st.warning("Sin horarios")

        # VER SUS RESERVAS
        st.subheader("📅 Mis reservas")
        c.execute(
            "SELECT * FROM reservas WHERE barberia_id = %s AND nombre = %s",
            (barberia_id, nombre),
        )
        for r in c.fetchall():
            st.write(f"{r[3]} con {r[2]} el {r[5]}")

    # ================= BARBERO =================
    elif rol == "barbero":
        if not barberia_id:
            st.warning("No hay barberia asociada a la sesión.")
            st.stop()

        st.title("✂️ Panel Barbero")

        eventos_filtrados = [e for e in eventos if usuario in e["title"]]

        calendar(events=eventos_filtrados)

        st.subheader("🔒 Bloquear horario")

        inicio = st.datetime_input("Desde")
        fin = st.datetime_input("Hasta")

        if st.button("Bloquear"):
            guardar_reserva("BLOQUEADO", usuario, "Bloqueo", 0, inicio.isoformat(), fin.isoformat())
            st.success("Bloqueado")

    # ================= ADMIN =================
    elif rol == "admin":
        if not barberia_id:
            st.warning("No hay barberia asociada a la sesión.")
            st.stop()

        st.title("💈 Panel Admin")

        calendar(events=eventos)

        st.subheader("💰 Ingresos")

        c.execute(
            "SELECT SUM(precio) FROM reservas WHERE barberia_id = %s",
            (barberia_id,),
        )
        total = c.fetchone()[0]

        st.metric("Total generado", f"${total if total else 0}")
