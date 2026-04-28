"""
Booking service: reservation CRUD and helpers extracted from app.py.

Imports are identical to what app.py used; business logic is unchanged.
"""
import logging
import traceback
from datetime import datetime, timedelta

import streamlit as st

from app_core.db.connection import get_connection
from app_core.db.safe_queries import fetch_one, execute_write
from app_core.security.tenant_access import (
    normalizar_rol,
    session_barberia_for_write,
    enforce_barberia_access,
)

logger = logging.getLogger(__name__)


def normalizar_reserva(r):

    """

    Normalize reservation tuple to dict.

    Handles schema: id, barbero, servicio, fecha, hora, cliente, nombre, inicio, precio, estado, pagado, monto

    Indices:      0    1        2          3      4     5        6       7       8       9       10       11

    """

    if isinstance(r, dict):

        return r

    if not r or len(r) < 6:

        return {}


    return {

        "id": r[0],

        "barbero": r[1],

        "servicio": r[2],

        "fecha": r[3],

        "hora": r[4],

        "cliente": r[5],

        "pagado": r[10] if len(r) > 10 else False,

        "monto": r[11] if len(r) > 11 else (r[8] if len(r) > 8 else 0),

    }

def obtener_reserva_por_id(reserva_id):

    """Get reservation by ID with multi-tenant isolation - must verify access."""

    try:

        result = fetch_one(

            """

            SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id, cliente, pagado, monto

            FROM reservas

            WHERE id = %s

            """,

            (reserva_id,),

        )

        if not result:

            return None


        # Extract barberia_id and verify access

        barberia_id = result[7]

        enforce_barberia_access(barberia_id)


        # Convert tuple to dictionary

        return {

            "id": result[0],

            "nombre": result[1],

            "barbero": result[2],

            "servicio": result[3],

            "precio": result[4],

            "inicio": result[5],

            "fin": result[6],

            "barberia_id": result[7],

            "cliente": result[8],

            "pagado": result[9] if len(result) > 9 else False,

            "monto": result[10] if len(result) > 10 else result[4],

        }

    except Exception:

        logger.exception("obtener_reserva_por_id")

        return None

def obtener_reserva(reserva_id, barberia_id):

    try:

        result = fetch_one(

            """

            SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id, cliente, pagado, monto

            FROM reservas

            WHERE id = %s AND barberia_id = %s

            """,

            (reserva_id, barberia_id),

        )

        if not result:

            return None


        # Convert tuple to dictionary

        return {

            "id": result[0],

            "nombre": result[1],

            "barbero": result[2],

            "servicio": result[3],

            "precio": result[4],

            "inicio": result[5],

            "fin": result[6],

            "barberia_id": result[7],

            "cliente": result[8],

            "pagado": result[9] if len(result) > 9 else False,

            "monto": result[10] if len(result) > 10 else result[4],

        }

    except Exception:

        logger.exception("obtener_reserva")

        return None

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

        if conn is None:

            return False

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

                st.error("Horario ocupado")

                return False

            cur.execute(

                """

                INSERT INTO reservas (nombre, barbero, servicio, precio, inicio, fin, barberia_id, monto, pagado)

                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE)

                """,

                (nombre, barbero, servicio, precio, inicio, fin, barberia_id, precio),

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

    barberia_id = session_barberia_for_write()

    if not barberia_id:

        return False

    if not st.session_state.get("db_available", True):

        st.warning("No hay base de datos: no se pueden guardar reservas en modo demo.")

        return False

    inicio = normalizar_datetime(inicio)

    fin = normalizar_datetime(fin)

    if not inicio or not fin or inicio >= fin:

        st.error("El horario de término debe ser posterior al inicio.")

        return False

    return _guardar_reserva_tx(nombre, barbero, servicio, precio, inicio, fin, barberia_id)

def actualizar_reserva(reserva_id, nombre, barbero, servicio, precio, inicio, fin):

    if not st.session_state.get("db_available", True):

        st.warning("No hay base de datos: no se pueden actualizar reservas en modo demo.")

        return False

    inicio = normalizar_datetime(inicio)

    fin = normalizar_datetime(fin)

    if not inicio or not fin or inicio >= fin:

        st.error("El horario de término debe ser posterior al inicio.")

        return False

    user = st.session_state.get("user")

    rol_u = normalizar_rol(user[3]) if user else ""

    prev = obtener_reserva_por_id(reserva_id)

    if not prev:

        st.error("Reserva no encontrada.")

        return False

    bid_tx = prev[7]

    sw = session_barberia_for_write()

    if rol_u != "SUPER_ADMIN" and not sw:

        return False

    if rol_u == "BARBERO" and prev[2] != user[1]:

        st.error("Sin permiso para modificar esta reserva.")

        return False

    if rol_u == "ADMIN" and bid_tx != st.session_state.get("barberia_id"):

        st.error("Sin permiso para modificar esta reserva.")

        return False

    if rol_u == "CLIENTE":

        st.error("Sin permiso para modificar esta reserva.")

        return False

    conn = None

    try:

        conn = get_connection()

        if conn is None:

            return False

        with conn.cursor() as cur:

            cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (f"{bid_tx}:{barbero}",))

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

                (bid_tx, barbero, reserva_id, fin, inicio),

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

                (nombre, barbero, servicio, precio, inicio, fin, reserva_id, bid_tx),

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

    if not st.session_state.get("db_available", True):

        st.warning("No hay base de datos: no se pueden eliminar reservas en modo demo.")

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

    cli = prev.get("cliente")

    if rol_u == "BARBERO" and prev.get("barbero") != uid:

        st.error("Sin permiso para eliminar esta reserva.")

        return False

    if rol_u == "ADMIN" and prev.get("barberia_id") != st.session_state.get("barberia_id"):

        st.error("Sin permiso para eliminar esta reserva.")

        return False

    if rol_u == "CLIENTE" and (cli or prev.get("nombre")) != uid:

        st.error("Sin permiso para eliminar esta reserva.")

        return False

    try:

        if rol_u == "SUPER_ADMIN":

            return bool(execute_write("DELETE FROM reservas WHERE id = %s", (reserva_id,)))

        return bool(

            execute_write(

                "DELETE FROM reservas WHERE id = %s AND barberia_id = %s",

                (reserva_id, prev.get("barberia_id")),

            )

        )

    except Exception as e:

        logger.exception("eliminar_reserva")

        st.error(f"Error eliminando reserva:\n{traceback.format_exc()}")

        return False

def insertar_reserva_con_fecha_hora(

    barberia_id,

    cliente_usuario,

    barbero_id,

    barbero_nombre,

    servicio,

    fecha,

    hora,

    precio,

    duracion_min,

):

    """Inserta reserva validando slot por fecha/hora y solapamiento por inicio/fin."""

    conn = None

    try:

        if not fecha or not hora:

            st.error("Selecciona fecha y hora.")

            return False

        inicio = datetime.combine(fecha, hora)

        fin = inicio + timedelta(minutes=duracion_min)

        conn = get_connection()

        if conn is None:

            return False

        with conn.cursor() as cur:

            cur.execute(

                """

                SELECT id FROM reservas

                WHERE barberia_id = %s AND barbero_id = %s AND fecha = %s AND hora = %s

                LIMIT 1

                """,

                (barberia_id, barbero_id, fecha, hora),

            )

            if cur.fetchone():

                conn.rollback()

                st.error("Horario ocupado")

                return False

            cur.execute(

                """

                SELECT id FROM reservas

                WHERE barberia_id = %s

                  AND barbero_id = %s

                  AND inicio < %s

                  AND fin > %s

                LIMIT 1

                """,

                (barberia_id, barbero_id, fin, inicio),

            )

            if cur.fetchone():

                conn.rollback()

                st.error("Horario ocupado")

                return False

            cur.execute(

                """

                INSERT INTO reservas (

                    nombre, barbero, barbero_id, servicio, precio, inicio, fin, barberia_id,

                    cliente, fecha, hora, estado, monto, pagado

                )

                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)

                RETURNING id

                """,

                (

                    cliente_usuario,

                    barbero_nombre,

                    barbero_id,

                    servicio,

                    precio,

                    inicio,

                    fin,

                    barberia_id,

                    cliente_usuario,

                    fecha,

                    hora,

                    "activo",

                    precio,

                ),

            )

            reserva_id = cur.fetchone()[0]

        conn.commit()

        return reserva_id

    except Exception as e:

        if conn:

            conn.rollback()

        logger.exception("Error al insertar reserva (fecha/hora)")

        st.error(str(e))

        return False

    finally:

        if conn:

            conn.close()
