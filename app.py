import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import sqlite3

st.set_page_config(layout="wide")

# ------------------ DB ------------------
conn = sqlite3.connect("barberia.db", check_same_thread=False)
c = conn.cursor()

# TABLA USUARIOS
c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    password TEXT,
    rol TEXT
)
""")

# TABLA RESERVAS
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

# ADMIN POR DEFECTO
c.execute("SELECT * FROM usuarios WHERE usuario='admin'")
if not c.fetchone():
    c.execute("INSERT INTO usuarios (usuario, password, rol) VALUES ('admin','1234','admin')")
    conn.commit()

# ------------------ DATOS ------------------
barberos = {
    "Andrea": "#FF5733",
    "Andres": "#33C1FF",
    "Yor": "#33FF57",
    "Maikel": "#F333FF"
}

servicios = {
    "Corte": {"duracion": 45, "precio": 10000},
    "Barba": {"duracion": 30, "precio": 7000},
    "Corte + Barba": {"duracion": 60, "precio": 15000}
}

# ------------------ FUNCIONES ------------------

def login(usuario, password):
    c.execute("SELECT * FROM usuarios WHERE usuario=? AND password=?", (usuario, password))
    return c.fetchone()

def registrar(usuario, password, rol):
    c.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)", (usuario, password, rol))
    conn.commit()

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
            "color": barberos.get(r[2], "#999")
        })

    return eventos

def guardar_reserva(nombre, barbero, servicio, precio, inicio, fin):
    c.execute("""INSERT INTO reservas (nombre, barbero, servicio, precio, inicio, fin)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, barbero, servicio, precio, inicio, fin))
    conn.commit()

# ------------------ LOGIN ------------------

if "user" not in st.session_state:
    st.session_state.user = None

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
        nuevo_user = st.text_input("Usuario cliente")
        nuevo_pass = st.text_input("Contraseña", type="password")

        if st.button("Crear cuenta cliente"):
            registrar(nuevo_user, nuevo_pass, "cliente")
            st.success("Cliente creado")

# ------------------ APP ------------------

else:
    user = st.session_state.user
    rol = user[3]
    usuario = user[1]

    st.sidebar.write(f"👤 {usuario} ({rol})")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.user = None
        st.rerun()

    eventos = obtener_reservas()

    # ================= CLIENTE =================
    if rol == "cliente":
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

            c.execute("""
            SELECT * FROM reservas 
            WHERE barbero=? AND (? < fin AND ? > inicio)
            """, (barbero, hora.isoformat(), fin.isoformat()))

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
                st.success("Reserva creada ✅")

        else:
            st.warning("Sin horarios")

        # VER SUS RESERVAS
        st.subheader("📅 Mis reservas")
        c.execute("SELECT * FROM reservas WHERE nombre=?", (nombre,))
        for r in c.fetchall():
            st.write(f"{r[3]} con {r[2]} el {r[5]}")

    # ================= BARBERO =================
    elif rol == "barbero":
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
        st.title("💈 Panel Admin")

        calendar(events=eventos)

        st.subheader("💰 Ingresos")

        c.execute("SELECT SUM(precio) FROM reservas")
        total = c.fetchone()[0]

        st.metric("Total generado", f"${total if total else 0}")
