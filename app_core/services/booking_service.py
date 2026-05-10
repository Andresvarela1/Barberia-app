"""
Booking service: reservation CRUD and helpers extracted from app.py.

This module keeps the public function surface stable while centralizing
critical reservation validation and overlap checks.
"""

import logging
from datetime import datetime, timedelta

import psycopg2
import streamlit as st

from app_core.db.connection import get_connection
from app_core.db.safe_queries import safe_execute, safe_fetch_all, safe_fetch_one
from app_core.security.tenant_access import (
    enforce_barberia_access,
    normalizar_rol,
    session_barberia_for_write,
)

logger = logging.getLogger(__name__)

RESERVA_SOLAPADA_PGCODE = "23P01"
MSG_CONFLICTO_CREAR = "Horario ocupado para ese barbero en ese rango."
MSG_CONFLICTO_EDITAR = "Ese cambio genera solapamiento con otra reserva."
MSG_CONFLICTO_DB = "Ese horario se acaba de ocupar. Elige otro horario."


def normalizar_reserva(r):
    """
    Normalize reservation tuple to dict.

    Handles schema:
    id, barbero, servicio, fecha, hora, cliente, nombre, inicio,
    precio, estado, pagado, monto, barbero_id
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
        "nombre": r[6] if len(r) > 6 else r[5],
        "inicio": r[7] if len(r) > 7 else None,
        "precio": r[8] if len(r) > 8 else 0,
        "estado": r[9] if len(r) > 9 else None,
        "pagado": r[10] if len(r) > 10 else False,
        "monto": r[11] if len(r) > 11 else (r[8] if len(r) > 8 else 0),
        "barbero_id": r[12] if len(r) > 12 else None,
    }


def normalizar_datetime(valor):
    if isinstance(valor, datetime):
        return valor.replace(tzinfo=None)

    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor.replace("Z", "+00:00")).replace(
                tzinfo=None
            )
        except ValueError:
            return None

    return valor


def _reserva_desde_fila(result):
    if not result:
        return None

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
        "barbero_id": result[11] if len(result) > 11 else None,
    }


def resolver_barbero_agenda(barberia_id, barbero=None, barbero_id=None):
    """Resolve a barber reference to canonical barbero_id and username."""

    if not barberia_id:
        return None

    resolved_id = None

    if barbero_id not in (None, ""):
        try:
            resolved_id = int(barbero_id)
        except (TypeError, ValueError):
            resolved_id = None

    if resolved_id is None and isinstance(barbero, int):
        resolved_id = int(barbero)

    if (
        resolved_id is None
        and isinstance(barbero, str)
        and barbero.strip().isdigit()
    ):
        resolved_id = int(barbero.strip())

    if resolved_id is not None:
        row = safe_fetch_one(
            """
            SELECT id, usuario
            FROM usuarios
            WHERE barberia_id = %s
              AND id = %s
              AND UPPER(TRIM(rol)) = 'BARBERO'
            """,
            (barberia_id, resolved_id),
        )
        if row:
            return {"barbero_id": row[0], "barbero": row[1]}

    if barbero in (None, ""):
        return None

    row = safe_fetch_one(
        """
        SELECT id, usuario
        FROM usuarios
        WHERE barberia_id = %s
          AND usuario = %s
          AND UPPER(TRIM(rol)) = 'BARBERO'
        """,
        (barberia_id, str(barbero).strip()),
    )
    if not row:
        return None

    return {"barbero_id": row[0], "barbero": row[1]}


def _reservation_error(exc, generic_message):
    if getattr(exc, "pgcode", None) == RESERVA_SOLAPADA_PGCODE:
        st.error(MSG_CONFLICTO_DB)
        return

    constraint_name = getattr(getattr(exc, "diag", None), "constraint_name", None)
    if constraint_name == "reservas_no_solapadas":
        st.error(MSG_CONFLICTO_DB)
        return

    st.error(generic_message)


def _rangos_se_solapan(inicio_a, fin_a, inicio_b, fin_b):
    inicio_a = normalizar_datetime(inicio_a)
    fin_a = normalizar_datetime(fin_a)
    inicio_b = normalizar_datetime(inicio_b)
    fin_b = normalizar_datetime(fin_b)

    if not inicio_a or not fin_a or not inicio_b or not fin_b:
        return False

    return inicio_a < fin_b and fin_a > inicio_b


def _normalizar_rango_reserva(inicio, fin):
    inicio = normalizar_datetime(inicio)
    fin = normalizar_datetime(fin)

    if not inicio or not fin or inicio >= fin:
        st.error("El horario de termino debe ser posterior al inicio.")
        return None, None

    return inicio, fin


def _construir_payload_reserva(
    *,
    barberia_id,
    nombre,
    servicio,
    precio,
    inicio,
    fin,
    barbero=None,
    barbero_id=None,
):
    if not barberia_id:
        st.error("No hay barberia activa para la reserva.")
        return None

    inicio, fin = _normalizar_rango_reserva(inicio, fin)
    if not inicio or not fin:
        return None

    identidad_barbero = resolver_barbero_agenda(
        barberia_id,
        barbero=barbero,
        barbero_id=barbero_id,
    )
    if not identidad_barbero:
        st.error("El barbero seleccionado no es valido para esta barberia.")
        return None

    nombre = str(nombre or "").strip()
    servicio = str(servicio or "").strip()
    if not nombre or not servicio:
        st.error("Completa los datos obligatorios de la reserva.")
        return None

    try:
        precio_valor = int(precio)
    except (TypeError, ValueError):
        st.error("El precio de la reserva no es valido.")
        return None

    return {
        "barberia_id": int(barberia_id),
        "nombre": nombre,
        "cliente": nombre,
        "servicio": servicio,
        "precio": precio_valor,
        "inicio": inicio,
        "fin": fin,
        "fecha": inicio.date(),
        "hora": inicio.time(),
        "barbero_id": identidad_barbero["barbero_id"],
        "barbero": identidad_barbero["barbero"],
    }


def _ensure_db_available(message):
    if not st.session_state.get("db_available", True):
        st.warning(message)
        return False
    return True


def _lock_reserva(cur, barberia_id, barbero_id, barbero_nombre):
    lock_key = f"{barberia_id}:{barbero_id or barbero_nombre}"
    cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (lock_key,))


def _buscar_conflicto_reserva(cur, payload, exclude_reserva_id=None):
    query = """
        SELECT id FROM reservas
        WHERE barberia_id = %s
          AND inicio < %s
          AND fin > %s
          AND (
                barbero_id = %s
                OR (barbero_id IS NULL AND barbero = %s)
          )
    """
    params = [
        payload["barberia_id"],
        payload["fin"],
        payload["inicio"],
        payload["barbero_id"],
        payload["barbero"],
    ]

    if exclude_reserva_id is not None:
        query += " AND id <> %s"
        params.append(exclude_reserva_id)

    query += " LIMIT 1"
    cur.execute(query, tuple(params))
    return cur.fetchone()


def _actualizar_reserva_en_bd(cur, reserva_id, barberia_id, payload):
    cur.execute(
        """
        UPDATE reservas
        SET nombre = %s,
            cliente = %s,
            barbero = %s,
            barbero_id = %s,
            servicio = %s,
            precio = %s,
            inicio = %s,
            fin = %s,
            fecha = %s,
            hora = %s,
            monto = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND barberia_id = %s
        """,
        (
            payload["nombre"],
            payload["cliente"],
            payload["barbero"],
            payload["barbero_id"],
            payload["servicio"],
            payload["precio"],
            payload["inicio"],
            payload["fin"],
            payload["fecha"],
            payload["hora"],
            payload["precio"],
            reserva_id,
            barberia_id,
        ),
    )


def _lock_reserva_targets(cur, barberia_id, *targets):
    seen = set()

    for target in targets:
        if not target:
            continue

        key = (barberia_id, target.get("barbero_id"), target.get("barbero"))
        if key in seen:
            continue

        seen.add(key)
        _lock_reserva(
            cur,
            barberia_id,
            target.get("barbero_id"),
            target.get("barbero"),
        )


def _target_from_payload(payload):
    return {
        "barbero_id": payload.get("barbero_id"),
        "barbero": payload.get("barbero"),
    }


def _target_from_reserva(reserva):
    return {
        "barbero_id": reserva.get("barbero_id"),
        "barbero": reserva.get("barbero"),
    }


def _persistir_reserva_tx(
    *,
    payload,
    generic_error_message,
    conflict_message,
    reserva_id=None,
    previous_reserva=None,
    return_insert_id=False,
):
    conn = None

    try:
        conn = get_connection()
        if conn is None:
            return False

        with conn.cursor() as cur:
            current_target = _target_from_payload(payload)
            previous_target = _target_from_reserva(previous_reserva) if previous_reserva else None

            _lock_reserva_targets(
                cur,
                payload["barberia_id"],
                previous_target,
                current_target,
            )

            if _buscar_conflicto_reserva(cur, payload, exclude_reserva_id=reserva_id):
                conn.rollback()
                st.error(conflict_message)
                return False

            if reserva_id is None:
                result = _insertar_reserva(cur, payload)
            else:
                _actualizar_reserva_en_bd(cur, reserva_id, payload["barberia_id"], payload)
                result = True

        conn.commit()
        return result if return_insert_id else True
    except psycopg2.Error as exc:
        if conn:
            conn.rollback()
        logger.exception("Error en transaccion de reserva")
        _reservation_error(exc, generic_error_message)
        return False
    except Exception:
        if conn:
            conn.rollback()
        logger.exception("Error en transaccion de reserva")
        st.error(generic_error_message)
        return False
    finally:
        if conn:
            conn.close()


def _validar_permiso_reserva(prev, user):
    if not user:
        return "Sin permiso para modificar esta reserva."

    rol_u = normalizar_rol(user[3]) if len(user) > 3 else ""
    session_barberia_id = session_barberia_for_write()

    if rol_u != "SUPER_ADMIN" and not session_barberia_id:
        return "Sin permiso para modificar esta reserva."

    if (
        rol_u == "BARBERO"
        and prev.get("barbero_id") != user[0]
        and prev.get("barbero") != user[1]
    ):
        return "Sin permiso para modificar esta reserva."

    if rol_u == "ADMIN" and prev.get("barberia_id") != st.session_state.get("barberia_id"):
        return "Sin permiso para modificar esta reserva."

    if rol_u == "CLIENTE":
        return "Sin permiso para modificar esta reserva."

    return None


def _validar_permiso_eliminar(prev, user):
    if not user:
        return "Sin permiso para eliminar esta reserva."

    rol_u = normalizar_rol(user[3]) if len(user) > 3 else ""
    uid = user[1]
    cli = prev.get("cliente")

    if (
        rol_u == "BARBERO"
        and prev.get("barbero_id") != user[0]
        and prev.get("barbero") != uid
    ):
        return "Sin permiso para eliminar esta reserva."

    if rol_u == "ADMIN" and prev.get("barberia_id") != st.session_state.get("barberia_id"):
        return "Sin permiso para eliminar esta reserva."

    if rol_u == "CLIENTE" and (cli or prev.get("nombre")) != uid:
        return "Sin permiso para eliminar esta reserva."

    return None


def obtener_rangos_reservados(
    barberia_id,
    *,
    fecha=None,
    barbero=None,
    barbero_id=None,
    exclude_reserva_id=None,
):
    if not barberia_id:
        return []

    identidad_barbero = resolver_barbero_agenda(
        barberia_id,
        barbero=barbero,
        barbero_id=barbero_id,
    )
    if not identidad_barbero:
        return []

    query = """
        SELECT inicio, fin
        FROM reservas
        WHERE barberia_id = %s
          AND (
                barbero_id = %s
                OR (barbero_id IS NULL AND barbero = %s)
          )
    """
    params = [
        barberia_id,
        identidad_barbero["barbero_id"],
        identidad_barbero["barbero"],
    ]

    if fecha is not None:
        query += " AND DATE(inicio) = %s"
        params.append(fecha)

    if exclude_reserva_id is not None:
        query += " AND id <> %s"
        params.append(exclude_reserva_id)

    query += " ORDER BY inicio"
    return safe_fetch_all(query, tuple(params)) or []


def _insertar_reserva(cur, payload):
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
            payload["nombre"],
            payload["barbero"],
            payload["barbero_id"],
            payload["servicio"],
            payload["precio"],
            payload["inicio"],
            payload["fin"],
            payload["barberia_id"],
            payload["cliente"],
            payload["fecha"],
            payload["hora"],
            "activo",
            payload["precio"],
        ),
    )
    row = cur.fetchone()
    return row[0] if row else None


def obtener_reserva_por_id(reserva_id):
    """Get reservation by ID with multi-tenant isolation."""

    try:
        context_barberia_id = session_barberia_for_write()
        if not context_barberia_id:
            return None

        result = safe_fetch_one(
            """
            SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id,
                   cliente, pagado, monto, barbero_id
            FROM reservas
            WHERE id = %s AND barberia_id = %s
            """,
            (reserva_id, context_barberia_id),
        )
        if not result:
            return None

        barberia_id = result[7]
        enforce_barberia_access(barberia_id)

        return _reserva_desde_fila(result)
    except Exception:
        logger.exception("obtener_reserva_por_id")
        return None


def obtener_reserva(reserva_id, barberia_id):
    try:
        result = safe_fetch_one(
            """
            SELECT id, nombre, barbero, servicio, precio, inicio, fin, barberia_id,
                   cliente, pagado, monto, barbero_id
            FROM reservas
            WHERE id = %s AND barberia_id = %s
            """,
            (reserva_id, barberia_id),
        )
        return _reserva_desde_fila(result)
    except Exception:
        logger.exception("obtener_reserva")
        return None


def _guardar_reserva_tx(
    nombre,
    barbero,
    servicio,
    precio,
    inicio,
    fin,
    barberia_id,
    barbero_id=None,
):
    payload = _construir_payload_reserva(
        barberia_id=barberia_id,
        nombre=nombre,
        servicio=servicio,
        precio=precio,
        inicio=inicio,
        fin=fin,
        barbero=barbero,
        barbero_id=barbero_id,
    )
    if not payload:
        return False

    return _persistir_reserva_tx(
        payload=payload,
        generic_error_message="No se pudo guardar la reserva.",
        conflict_message=MSG_CONFLICTO_CREAR,
    )


def guardar_reserva(nombre, barbero, servicio, precio, inicio, fin, barbero_id=None):
    barberia_id = session_barberia_for_write()
    if not barberia_id:
        return False

    if not _ensure_db_available(
        "No hay base de datos: no se pueden guardar reservas en modo demo."
    ):
        return False

    return _guardar_reserva_tx(
        nombre,
        barbero,
        servicio,
        precio,
        inicio,
        fin,
        barberia_id,
        barbero_id=barbero_id,
    )


def actualizar_reserva(
    reserva_id,
    nombre,
    barbero,
    servicio,
    precio,
    inicio,
    fin,
    barbero_id=None,
):
    if not _ensure_db_available(
        "No hay base de datos: no se pueden actualizar reservas en modo demo."
    ):
        return False

    user = st.session_state.get("user")

    prev = obtener_reserva_por_id(reserva_id)
    if not prev:
        st.error("Reserva no encontrada.")
        return False

    bid_tx = prev.get("barberia_id")
    permission_error = _validar_permiso_reserva(prev, user)
    if permission_error:
        st.error(permission_error)
        return False

    payload = _construir_payload_reserva(
        barberia_id=bid_tx,
        nombre=nombre,
        servicio=servicio,
        precio=precio,
        inicio=inicio,
        fin=fin,
        barbero=barbero,
        barbero_id=barbero_id,
    )
    if not payload:
        return False

    return _persistir_reserva_tx(
        payload=payload,
        generic_error_message="No se pudo actualizar la reserva.",
        conflict_message=MSG_CONFLICTO_EDITAR,
        reserva_id=reserva_id,
        previous_reserva=prev,
    )


def eliminar_reserva(reserva_id):
    if not _ensure_db_available(
        "No hay base de datos: no se pueden eliminar reservas en modo demo."
    ):
        return False

    user = st.session_state.get("user")

    prev = obtener_reserva_por_id(reserva_id)
    if not prev:
        st.error("Reserva no encontrada.")
        return False

    permission_error = _validar_permiso_eliminar(prev, user)
    if permission_error:
        st.error(permission_error)
        return False

    try:
        return bool(
            safe_execute(
                "DELETE FROM reservas WHERE id = %s AND barberia_id = %s",
                (reserva_id, prev.get("barberia_id")),
            )
        )
    except Exception:
        logger.exception("eliminar_reserva")
        st.error("Error al eliminar la reserva. Por favor, intenta de nuevo.")
        return False


def insertar_reserva_con_fecha_hora(
    barberia_id,
    cliente_usuario,
    barbero_ref,
    servicio,
    fecha,
    hora,
    precio,
    duracion_min,
    barbero_nombre=None,
):
    """Insert reservation validating overlap by real start/end range."""

    if not _ensure_db_available(
        "No hay base de datos: no se pueden guardar reservas en modo demo."
    ):
        return False

    if not fecha or not hora:
        st.error("Selecciona fecha y hora.")
        return False

    try:
        duracion_valor = int(duracion_min)
    except (TypeError, ValueError):
        st.error("La duracion del servicio no es valida.")
        return False

    if duracion_valor <= 0:
        st.error("La duracion del servicio no es valida.")
        return False

    inicio = datetime.combine(fecha, hora)
    fin = inicio + timedelta(minutes=duracion_valor)

    payload = _construir_payload_reserva(
        barberia_id=barberia_id,
        nombre=cliente_usuario,
        servicio=servicio,
        precio=precio,
        inicio=inicio,
        fin=fin,
        barbero=barbero_nombre or barbero_ref,
        barbero_id=barbero_ref,
    )
    if not payload:
        return False

    return _persistir_reserva_tx(
        payload=payload,
        generic_error_message="Error al guardar la reserva. Por favor, intenta de nuevo.",
        conflict_message=MSG_CONFLICTO_CREAR,
        return_insert_id=True,
    )
