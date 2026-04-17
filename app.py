import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import logging
import os
import bcrypt
import psycopg2
from whatsapp import enviar_whatsapp as enviar_whatsapp_twilio

st.set_page_config(layout="wide")

# ------------------ LOGGER ------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("barberia_app")

# ------------------ DB ------------------
def get_database_url():
    return os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")


def get_connection():
    database_url = get_database_url()
    
    if not database_url:
        logger.error("DATABASE_URL o SUPABASE_DB_URL no configurada")
        st.error("DATABASE_URL o SUPABASE_DB_URL no configurada")
        st.stop()
        
    return psycopg2.connect(database_url, sslmode="require")

def execute_query(query, params=None, fetch=None):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)

            if fetch == "one":
                data = cur.fetchone()
            elif fetch == "all":
                data = cur.fetchall()
            else:
                data = True

        conn.commit()
        return data

    except Exception:
        if conn:
            conn.rollback()
        logger.exception("Error en base de datos")
        st.error("Error en base de datos")
        return None
    finally:
        if conn:
            conn.close()


def fetch_one(query, params=None):
    return execute_query(query, params, fetch="one")


def fetch_all(query, params=None):
    return execute_query(query, params, fetch="all") or []


def execute_write(query, params=None, fetch_one_result=False):
    return execute_query(query, params, fetch="one" if fetch_one_result else None)

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


# ------------------ FUNCIONES ------------------

def normalizar_texto(valor):
    return valor.strip() if isinstance(valor, str) else ""


def es_hash_bcrypt(valor):
    return isinstance(valor, str) and valor.startswith(("$2a$", "$2b$", "$2y$"))


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password, password_guardada):
    if not password_guardada:
        return False

    if es_hash_bcrypt(password_guardada):
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                password_guardada.encode("utf-8"),
            )
        except ValueError:
            logger.exception("Hash de password inválido para bcrypt")
            return False

    return password == password_guardada


def login(usuario, password):
    usuario = normalizar_texto(usuario)
    password = normalizar_texto(password)

    if not usuario or not password:
        return None

    user = fetch_one(
        """
        SELECT id, usuario, password, rol, telefono, barberia_id, cortes_acumulados
        FROM usuarios
        WHERE usuario=%s
        """,
        (usuario,),
    )
    if not user or not verificar_password(password, user[2]):
        return None

    if not es_hash_bcrypt(user[2]):
        nuevo_hash = hash_password(password)
        if execute_write(
            "UPDATE usuarios SET password=%s WHERE id=%s",
            (nuevo_hash, user[0]),
        ):
            user = (user[0], user[1], nuevo_hash, user[3], user[4], user[5], user[6])

    return user
def crear_barberia_por_defecto():
    data = fetch_one("SELECT id FROM barberias LIMIT 1")

    if data:
        return data[0]

    result = execute_write(
        "INSERT INTO barberias (nombre) VALUES (%s) RETURNING id",
        ("Barbería Principal",),
        fetch_one_result=True
    )

    return result[0] if result else None

default_barberia_id = crear_barberia_por_defecto()

def registrar(usuario, password, rol, telefono=None, barberia_id=None):
    barberia_id = barberia_id or default_barberia_id

    if not barberia_id:
        st.error("No hay barbería configurada para registrar usuarios.")
        return False

    password_hash = hash_password(password)
    result = execute_write(
        "INSERT INTO usuarios (usuario, password, rol, telefono, barberia_id) VALUES (%s, %s, %s, %s, %s)",
        (usuario, password_hash, rol, telefono, barberia_id),
    )
    return bool(result)


def obtener_telefono_usuario(usuario):
    row = fetch_one("SELECT telefono FROM usuarios WHERE usuario=%s", (usuario,))
    return row[0] if row and row[0] else None


def get_default_barberia_id():
    row = fetch_one("SELECT id FROM barberias ORDER BY id LIMIT 1")
    return row[0] if row else None


def registrar_fidelizacion(usuario, barberia_id):
    row = execute_write(
        """
        UPDATE usuarios
        SET cortes_acumulados = COALESCE(cortes_acumulados, 0) + 1
        WHERE usuario = %s AND barberia_id = %s
        RETURNING cortes_acumulados
        """,
        (usuario, barberia_id),
        fetch_one_result=True,
    )
    return row[0] if row else None


def procesar_beneficio_fidelizacion(usuario, barberia_id):
    cortes_acumulados = registrar_fidelizacion(usuario, barberia_id)
    if cortes_acumulados is None or cortes_acumulados < 5:
        return

    execute_write(
        """
        UPDATE usuarios
        SET cortes_acumulados = 0
        WHERE usuario = %s AND barberia_id = %s
        """,
        (usuario, barberia_id),
    )

    telefono_cliente = obtener_telefono_usuario(usuario)
    if telefono_cliente:
        try:
            enviar_whatsapp_twilio(
                telefono_cliente,
                "🔥 ¡Tienes un descuento en tu próximo corte!",
            )
        except Exception as exc:
            logger.exception("Error al enviar beneficio de fidelizacion: %s", exc)


def construir_mensaje_reserva(nombre, inicio, barbero, servicio):
    return (
        f"Hola {nombre}, tu reserva fue confirmada.\n"
        f"Fecha: {inicio.strftime('%d-%m-%Y')}\n"
        f"Hora: {inicio.strftime('%H:%M')}\n"
        f"Barbero: {barbero}\n"
        f"Servicio: {servicio}"
    )

def obtener_reservas_raw(barberia_id, barbero=None):
    if not barberia_id:
        return []

    if barbero:
        return fetch_all(
            """
            SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id
            FROM reservas
            WHERE barberia_id = %s AND barbero = %s
            ORDER BY inicio
            """,
            (barberia_id, barbero),
        )

    return fetch_all(
        """
        SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id
        FROM reservas
        WHERE barberia_id = %s
        ORDER BY inicio
        """,
        (barberia_id,),
    )


def construir_eventos_calendario(reservas):
    eventos = []

    for r in reservas:
        es_bloqueo = r[1] == "BLOQUEADO" or r[3] == "Bloqueo"
        eventos.append({
            "id": str(r[0]),
            "title": f"{r[1]} - {r[3]} ({r[2]})",
            "start": r[5].isoformat() if hasattr(r[5], "isoformat") else r[5],
            "end": r[6].isoformat() if hasattr(r[6], "isoformat") else r[6],
            "color": "#666666" if es_bloqueo else barberos.get(r[2], "#999"),
            "extendedProps": {
                "nombre": r[1],
                "barbero": r[2],
                "servicio": r[3],
                "precio": r[4],
                "bloqueo": es_bloqueo,
            },
        })

    return eventos


def obtener_reservas(barbero=None):
    barberia_id = st.session_state.get("barberia_id")
    if not barberia_id:
        return []

    return construir_eventos_calendario(obtener_reservas_raw(barberia_id, barbero))


def obtener_reserva(reserva_id, barberia_id):
    return fetch_one(
        """
        SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id
        FROM reservas
        WHERE id = %s AND barberia_id = %s
        """,
        (reserva_id, barberia_id),
    )


def normalizar_datetime(valor):
    if isinstance(valor, datetime):
        return valor.replace(tzinfo=None)
    if isinstance(valor, str):
        return datetime.fromisoformat(valor.replace("Z", "+00:00")).replace(tzinfo=None)
    return valor


def _guardar_reserva_tx(nombre, barbero, servicio, precio, inicio, fin, barberia_id):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (f"{barberia_id}:{barbero}",))
            cur.execute(
                """
                SELECT id FROM reservas
                WHERE barberia_id = %s
                  AND barbero = %s
                  AND inicio < %s
                  AND fin > %s
                LIMIT 1
                """,
                (barberia_id, barbero, fin, inicio),
            )
            if cur.fetchone():
                conn.rollback()
                st.error("Ese horario ya está ocupado para el barbero seleccionado.")
                return False

            cur.execute(
                """
                INSERT INTO reservas (nombre, barbero, servicio, precio, inicio, fin, barberia_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (nombre, barbero, servicio, precio, inicio, fin, barberia_id),
            )

        conn.commit()
        return True
    except Exception:
        if conn:
            conn.rollback()
        logger.exception("Error al guardar reserva")
        st.error("No se pudo guardar la reserva.")
        return False
    finally:
        if conn:
            conn.close()

def guardar_reserva(nombre, barbero, servicio, precio, inicio, fin):
    barberia_id = st.session_state.get("barberia_id")
    if not barberia_id:
        return False

    inicio = normalizar_datetime(inicio)
    fin = normalizar_datetime(fin)
    if not inicio or not fin or inicio >= fin:
        st.error("El horario de término debe ser posterior al inicio.")
        return False

    return _guardar_reserva_tx(nombre, barbero, servicio, precio, inicio, fin, barberia_id)


def actualizar_reserva(reserva_id, nombre, barbero, servicio, precio, inicio, fin):
    barberia_id = st.session_state.get("barberia_id")
    if not barberia_id:
        return False

    inicio = normalizar_datetime(inicio)
    fin = normalizar_datetime(fin)
    if not inicio or not fin or inicio >= fin:
        st.error("El horario de término debe ser posterior al inicio.")
        return False

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (f"{barberia_id}:{barbero}",))
            cur.execute(
                """
                SELECT id FROM reservas
                WHERE barberia_id = %s
                  AND barbero = %s
                  AND id <> %s
                  AND inicio < %s
                  AND fin > %s
                LIMIT 1
                """,
                (barberia_id, barbero, reserva_id, fin, inicio),
            )
            if cur.fetchone():
                conn.rollback()
                st.error("Ese cambio genera solapamiento con otra reserva.")
                return False

            cur.execute(
                """
                UPDATE reservas
                SET nombre = %s, barbero = %s, servicio = %s, precio = %s, inicio = %s, fin = %s
                WHERE id = %s AND barberia_id = %s
                """,
                (nombre, barbero, servicio, precio, inicio, fin, reserva_id, barberia_id),
            )

        conn.commit()
        return True
    except Exception:
        if conn:
            conn.rollback()
        logger.exception("Error al actualizar reserva")
        st.error("No se pudo actualizar la reserva.")
        return False
    finally:
        if conn:
            conn.close()


def eliminar_reserva(reserva_id):
    barberia_id = st.session_state.get("barberia_id")
    if not barberia_id:
        return False

    return bool(execute_write(
        "DELETE FROM reservas WHERE id = %s AND barberia_id = %s",
        (reserva_id, barberia_id),
    ))


def opciones_calendario(initial_view="timeGridWeek"):
    return {
        "initialView": initial_view,
        "editable": True,
        "selectable": True,
        "allDaySlot": False,
        "slotMinTime": "09:00:00",
        "slotMaxTime": "21:00:00",
        "height": 720,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay",
        },
    }


def manejar_interaccion_calendario(calendar_state):
    if not isinstance(calendar_state, dict):
        return

    event_click = calendar_state.get("eventClick")
    if event_click and event_click.get("event"):
        st.session_state.reserva_seleccionada_id = int(event_click["event"]["id"])

    for key in ("eventDrop", "eventResize", "eventChange"):
        payload = calendar_state.get(key)
        evento = payload.get("event") if isinstance(payload, dict) else None
        if evento and evento.get("id"):
            reserva = obtener_reserva(int(evento["id"]), st.session_state.get("barberia_id"))
            if reserva:
                actualizar_reserva(
                    reserva[0],
                    reserva[1],
                    reserva[2],
                    reserva[3],
                    reserva[4],
                    normalizar_datetime(evento.get("start")),
                    normalizar_datetime(evento.get("end")),
                )
                st.rerun()


def render_agenda_interactiva(eventos, barbero_actual=None):
    calendar_state = calendar(
        events=eventos,
        options=opciones_calendario(),
        key=f"agenda_{barbero_actual or 'todos'}",
    )
    manejar_interaccion_calendario(calendar_state)


def render_gestion_agenda(barbero_actual=None):
    barberia_id = st.session_state.get("barberia_id")
    if not barberia_id:
        st.warning("No hay barberia asociada a la sesión.")
        return

    reservas = obtener_reservas_raw(barberia_id, barbero_actual)
    barbero_options = [barbero_actual] if barbero_actual else list(barberos.keys())
    servicio_options = list(servicios.keys()) + ["Bloqueo"]

    with st.expander("Crear reserva o bloqueo", expanded=False):
        with st.form("crear_reserva_calendario"):
            servicio_nuevo = st.selectbox("Servicio", servicio_options, key="agenda_servicio_nuevo")
            nombre_default = "BLOQUEADO" if servicio_nuevo == "Bloqueo" else ""
            nombre_nuevo = st.text_input("Cliente", value=nombre_default)
            barbero_nuevo = st.selectbox("Barbero", barbero_options, key="agenda_barbero_nuevo")
            inicio_nuevo = st.datetime_input("Inicio", key="agenda_inicio_nuevo")
            fin_nuevo = st.datetime_input("Fin", value=inicio_nuevo + timedelta(minutes=30), key="agenda_fin_nuevo")

            if st.form_submit_button("Crear"):
                precio_nuevo = 0 if servicio_nuevo == "Bloqueo" else servicios[servicio_nuevo]["precio"]
                nombre_final = "BLOQUEADO" if servicio_nuevo == "Bloqueo" else normalizar_texto(nombre_nuevo)

                if not nombre_final:
                    st.error("El nombre del cliente es obligatorio.")
                elif guardar_reserva(
                    nombre_final,
                    barbero_nuevo,
                    servicio_nuevo,
                    precio_nuevo,
                    inicio_nuevo,
                    fin_nuevo,
                ):
                    st.success("Reserva creada")
                    st.rerun()

    st.subheader("Editar o eliminar reserva")
    if not reservas:
        st.info("No hay reservas para editar.")
        return

    ids_reservas = [r[0] for r in reservas]
    reserva_id_guardada = st.session_state.get("reserva_seleccionada_id")
    index_inicial = ids_reservas.index(reserva_id_guardada) if reserva_id_guardada in ids_reservas else 0

    reserva_id = st.selectbox(
        "Reserva",
        ids_reservas,
        index=index_inicial,
        format_func=lambda rid: next(
            f"{r[5].strftime('%d-%m %H:%M') if hasattr(r[5], 'strftime') else r[5]} - {r[1]} ({r[2]})"
            for r in reservas
            if r[0] == rid
        ),
    )
    reserva = next(r for r in reservas if r[0] == reserva_id)
    st.session_state.reserva_seleccionada_id = reserva_id

    with st.form("editar_reserva_calendario"):
        servicio_idx = servicio_options.index(reserva[3]) if reserva[3] in servicio_options else 0
        barbero_idx = barbero_options.index(reserva[2]) if reserva[2] in barbero_options else 0
        nombre_editado = st.text_input("Cliente", value=reserva[1])
        servicio_editado = st.selectbox("Servicio", servicio_options, index=servicio_idx, key="agenda_servicio_editado")
        barbero_editado = st.selectbox("Barbero", barbero_options, index=barbero_idx, key="agenda_barbero_editado")
        inicio_editado = st.datetime_input("Inicio", value=reserva[5], key="agenda_inicio_editado")
        fin_editado = st.datetime_input("Fin", value=reserva[6], key="agenda_fin_editado")

        actualizar = st.form_submit_button("Guardar cambios")
        eliminar = st.form_submit_button("Eliminar reserva")

        if actualizar:
            precio_editado = 0 if servicio_editado == "Bloqueo" else servicios[servicio_editado]["precio"]
            nombre_final = "BLOQUEADO" if servicio_editado == "Bloqueo" else normalizar_texto(nombre_editado)

            if not nombre_final:
                st.error("El nombre del cliente es obligatorio.")
            elif actualizar_reserva(
                reserva_id,
                nombre_final,
                barbero_editado,
                servicio_editado,
                precio_editado,
                inicio_editado,
                fin_editado,
            ):
                st.success("Reserva actualizada")
                st.rerun()

        if eliminar:
            if eliminar_reserva(reserva_id):
                st.session_state.reserva_seleccionada_id = None
                st.success("Reserva eliminada")
                st.rerun()

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
            if registrar(nuevo_user, nuevo_pass, "barbero"):
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
                if registrar(nuevo_user, nuevo_pass, "cliente", telefono):
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

            reserva_existente = fetch_one(
                """
                SELECT * FROM reservas
                WHERE barberia_id = %s AND barbero = %s AND (%s < fin AND %s > inicio)
                """,
                (barberia_id, barbero, hora, fin),
            )

            if not reserva_existente:
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

                reserva_creada = guardar_reserva(nombre, barbero, servicio, precio, inicio, fin)
                if reserva_creada:
                    procesar_beneficio_fidelizacion(usuario, barberia_id)
                    telefono_cliente = user[4] if len(user) > 4 else obtener_telefono_usuario(usuario)
                    if telefono_cliente:
                        mensaje = construir_mensaje_reserva(nombre, inicio, barbero, servicio)
                        try:
                            enviar_whatsapp_twilio(telefono_cliente, mensaje)
                        except Exception as exc:
                            logger.exception("Error al ejecutar el envio de WhatsApp: %s", exc)
                    st.success("Reserva creada ✅")

        else:
            st.warning("Sin horarios")

        # VER SUS RESERVAS
        st.subheader("📅 Mis reservas")
        mis_reservas = fetch_all(
            "SELECT * FROM reservas WHERE barberia_id = %s AND nombre = %s",
            (barberia_id, nombre),
        )
        for r in mis_reservas:
            st.write(f"{r[3]} con {r[2]} el {r[5]}")

    # ================= BARBERO =================
    elif rol == "barbero":
        if not barberia_id:
            st.warning("No hay barberia asociada a la sesión.")
            st.stop()

        st.title("✂️ Panel Barbero")

        eventos_barbero = obtener_reservas(usuario)
        render_agenda_interactiva(eventos_barbero, usuario)
        render_gestion_agenda(usuario)

    # ================= ADMIN =================
    elif rol == "admin":
        if not barberia_id:
            st.warning("No hay barberia asociada a la sesión.")
            st.stop()

        st.title("💈 Panel Admin")

        render_agenda_interactiva(eventos)
        render_gestion_agenda()

        st.subheader("💰 Ingresos")

        total_row = fetch_one(
            "SELECT SUM(precio) FROM reservas WHERE barberia_id = %s",
            (barberia_id,),
        )
        total = total_row[0] if total_row else 0

        st.metric("Total generado", f"${total if total else 0}")
