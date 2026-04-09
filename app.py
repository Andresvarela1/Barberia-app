
import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import sqlite3

st.set_page_config(layout="wide")

# ------------------ MODO ------------------
modo = st.sidebar.radio("Modo", ["Cliente", "Barbería"])

# ------------------ BASE DE DATOS ------------------
conn = sqlite3.connect("barberia.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS reservas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    barbero TEXT,
    servicio TEXT,
    precio INTEGER,
    inicio TEXT,
    fin TEXT
)
""")
conn.commit()

# ------------------ BARBEROS ------------------
barberos = {
    "Andrea": "#FF5733",
    "Andres": "#33C1FF",
    "Yor": "#33FF57",
    "Maikel": "#F333FF"
}

# ------------------ SERVICIOS ------------------
servicios = {
    "Corte": {"duracion": 45, "precio": 10000},
    "Barba": {"duracion": 30, "precio": 7000},
    "Corte + Barba": {"duracion": 60, "precio": 15000}
}

# ------------------ FUNCIONES ------------------

def obtener_reservas():
    c.execute("SELECT * FROM reservas")
    data = c.fetchall()
    eventos = []
    for r in data:
        eventos.append({
            "id": r[0],
            "title": f"{r[1]} - {r[3]} ({r[2]})",
            "start": r[5],
            "end": r[6],
            "color": barberos[r[2]]
        })
    return eventos

def hay_conflicto(barbero, inicio, fin):
    c.execute("""
    SELECT * FROM reservas 
    WHERE barbero=? 
    AND (? < fin AND ? > inicio)
    """, (barbero, inicio, fin))
    
    return c.fetchone() is not None

def guardar_reserva(nombre, barbero, servicio, precio, inicio, fin):
    c.execute("""
    INSERT INTO reservas (nombre, barbero, servicio, precio, inicio, fin)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, barbero, servicio, precio, inicio, fin))
    conn.commit()

# ================== MODO CLIENTE ==================

if modo == "Cliente":
    st.title("📲 Reserva tu turno")

    nombre = st.text_input("Tu nombre")
    barbero = st.selectbox("Elige barbero", list(barberos.keys()))
    servicio = st.selectbox("Servicio", list(servicios.keys()))

    duracion = servicios[servicio]["duracion"]
    precio = servicios[servicio]["precio"]

    st.info(f"⏱️ Duración: {duracion} min | 💰 Precio: ${precio}")

    fecha = st.date_input("Selecciona día")

    horarios_disponibles = []
    inicio_dia = datetime.combine(fecha, datetime.strptime("09:00", "%H:%M").time())

    for i in range(24):
        hora = inicio_dia + timedelta(minutes=15 * i)
        fin = hora + timedelta(minutes=duracion)

        if hora.hour >= 21:
            break

        if not hay_conflicto(barbero, hora.isoformat(), fin.isoformat()):
            horarios_disponibles.append(hora)

    if horarios_disponibles:
        hora_seleccionada = st.selectbox(
            "Horarios disponibles",
            horarios_disponibles,
            format_func=lambda x: x.strftime("%H:%M")
        )

        if st.button("Reservar ahora"):
            inicio = hora_seleccionada
            fin = inicio + timedelta(minutes=duracion)

            guardar_reserva(
                nombre,
                barbero,
                servicio,
                precio,
                inicio.isoformat(),
                fin.isoformat()
            )

            st.success("✅ Reserva confirmada")
    else:
        st.warning("❌ No hay horarios disponibles")

# ================== MODO BARBERÍA ==================

elif modo == "Barbería":
    st.title("💈 Panel Barbería")

    calendar_options = {
        "initialView": "timeGridWeek",
        "locale": "es",
        "slotMinTime": "09:00:00",
        "slotMaxTime": "21:00:00",
        "allDaySlot": False,
        "editable": True,
        "selectable": True,
    }

    eventos = obtener_reservas()

    calendar(
        events=eventos,
        options=calendar_options,
    )

    # Mostrar ingresos
    st.subheader("💰 Ingresos")

    c.execute("SELECT SUM(precio) FROM reservas")
    total = c.fetchone()[0]

    st.metric("Total generado", f"${total if total else 0}")

import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import sqlite3

st.set_page_config(layout="wide")

# ------------------ MODO ------------------
modo = st.sidebar.radio("Modo", ["Cliente", "Barbería"])

# ------------------ BASE DE DATOS ------------------
conn = sqlite3.connect("barberia.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS reservas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    barbero TEXT,
    servicio TEXT,
    precio INTEGER,
    inicio TEXT,
    fin TEXT
)
""")
conn.commit()

# ------------------ BARBEROS ------------------
barberos = {
    "Andrea": "#FF5733",
    "Andres": "#33C1FF",
    "Yor": "#33FF57",
    "Maikel": "#F333FF"
}

# ------------------ SERVICIOS ------------------
servicios = {
    "Corte": {"duracion": 45, "precio": 10000},
    "Barba": {"duracion": 30, "precio": 7000},
    "Corte + Barba": {"duracion": 60, "precio": 15000}
}

# ------------------ FUNCIONES ------------------

def obtener_reservas():
    c.execute("SELECT * FROM reservas")
    data = c.fetchall()
    eventos = []
    for r in data:
        eventos.append({
            "id": r[0],
            "title": f"{r[1]} - {r[3]} ({r[2]})",
            "start": r[5],
            "end": r[6],
            "color": barberos[r[2]]
        })
    return eventos

def hay_conflicto(barbero, inicio, fin):
    c.execute("""
    SELECT * FROM reservas 
    WHERE barbero=? 
    AND (? < fin AND ? > inicio)
    """, (barbero, inicio, fin))
    
    return c.fetchone() is not None

def guardar_reserva(nombre, barbero, servicio, precio, inicio, fin):
    c.execute("""
    INSERT INTO reservas (nombre, barbero, servicio, precio, inicio, fin)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, barbero, servicio, precio, inicio, fin))
    conn.commit()

# ================== MODO CLIENTE ==================

if modo == "Cliente":
    st.title("📲 Reserva tu turno")

    nombre = st.text_input("Tu nombre")
    barbero = st.selectbox("Elige barbero", list(barberos.keys()))
    servicio = st.selectbox("Servicio", list(servicios.keys()))
    telefono = st.text_input("Tu WhatsApp (ej: +56912345678)")

    duracion = servicios[servicio]["duracion"]
    precio = servicios[servicio]["precio"]

    st.info(f"⏱️ Duración: {duracion} min | 💰 Precio: ${precio}")

    fecha = st.date_input("Selecciona día")

    horarios_disponibles = []
    inicio_dia = datetime.combine(fecha, datetime.strptime("09:00", "%H:%M").time())

    for i in range(24):
        hora = inicio_dia + timedelta(minutes=15 * i)
        fin = hora + timedelta(minutes=duracion)

        if hora.hour >= 21:
            break

        if not hay_conflicto(barbero, hora.isoformat(), fin.isoformat()):
            horarios_disponibles.append(hora)

    if horarios_disponibles:
        hora_seleccionada = st.selectbox(
            "Horarios disponibles",
            horarios_disponibles,
            format_func=lambda x: x.strftime("%H:%M")
        )

if st.button("Reservar ahora"):
    inicio = hora_seleccionada
    fin = inicio + timedelta(minutes=duracion)

    guardar_reserva(
        nombre,
        barbero,
        servicio,
        precio,
        inicio.isoformat(),
        fin.isoformat()
    )

    mensaje = f"""
Hola {nombre} 👋

Tu reserva está confirmada 💈

📅 Fecha: {inicio.strftime("%d/%m/%Y")}
⏰ Hora: {inicio.strftime("%H:%M")}
💈 Barbero: {barbero}
✂️ Servicio: {servicio}

Te esperamos 🔥
"""

    enviar_whatsapp(telefono, mensaje)

    st.success("✅ Reserva confirmada y enviada por WhatsApp")
else:
    st.warning("❌ No hay horarios disponibles")

# ================== MODO BARBERÍA ==================

elif modo == "Barbería":
    st.title("💈 Panel Barbería")

    calendar_options = {
        "initialView": "timeGridWeek",
        "locale": "es",
        "slotMinTime": "09:00:00",
        "slotMaxTime": "21:00:00",
        "allDaySlot": False,
        "editable": True,
        "selectable": True,
    }

    eventos = obtener_reservas()

    calendar(
        events=eventos,
        options=calendar_options,
    )

    # Mostrar ingresos
    st.subheader("💰 Ingresos")

    c.execute("SELECT SUM(precio) FROM reservas")
    total = c.fetchone()[0]

    st.metric("Total generado", f"${total if total else 0}")

    from twilio.rest import Client

def enviar_whatsapp(numero, mensaje):
    account_sid = "ACf57bce8040ff3d2f855f99cf92bfa936"
    auth_token = "1790316f37081d770911d94b598d07f0"
    
    client = Client(account_sid, auth_token)

    client.messages.create(
        body=mensaje,
        from_='whatsapp:+14155238886',  # número sandbox
        to=f'whatsapp:{numero}'
    )

