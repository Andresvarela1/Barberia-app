"""Availability and barber slot helpers."""

import logging
from datetime import datetime, timedelta

import streamlit as st

from app_core.db.safe_queries import safe_fetch_all
from app_core.services.booking_service import resolver_barbero_agenda
from app_core.security.tenant_access import (
    enforce_barberia_access,
    get_current_barberia_id,
)


logger = logging.getLogger("barberia_app")


@st.cache_data(ttl=120)

def listar_usuarios_barberos(barberia_id=None):

    """Get barbers for a specific barberia - enforces data isolation.


    SECURITY: Always uses current barberia context.

    """

    # SECURITY: Always use current context

    barberia_id = get_current_barberia_id()

    if not barberia_id:

        return []


    # Check if user can access this barberia

    enforce_barberia_access(barberia_id)


    try:

        return safe_fetch_all(

            """

            SELECT id, usuario FROM usuarios

            WHERE barberia_id = %s AND UPPER(TRIM(rol)) = 'BARBERO'

            ORDER BY usuario

            """,

            (barberia_id,),

        ) or []

    except Exception:

        logger.exception("listar_usuarios_barberos")

        return []


def obtener_barberos_disponibles(barberia_id=None):

    """Get all active barbers for a barbershop with multi-tenant isolation.


    SECURITY: Always uses current barberia context - prevents barber leakage.

    """

    # SECURITY: Always use current context

    barberia_id = get_current_barberia_id()

    if not barberia_id:

        logger.warning("obtener_barberos_disponibles: No barberia_id in context")

        return []


    # Verify access to this barberia before returning data

    enforce_barberia_access(barberia_id)


    try:

        results = safe_fetch_all(

            """

            SELECT id, usuario AS nombre FROM usuarios 

            WHERE barberia_id = %s AND UPPER(TRIM(rol)) = 'BARBERO'

            ORDER BY usuario

            """,

            (barberia_id,)

        )

        logger.info(f"obtener_barberos_disponibles: barberia_id={barberia_id}, found {len(results) if results else 0} barbers")

        return results or []

    except Exception as e:

        logger.exception(f"Error getting barbers for barberia_id={barberia_id}: {str(e)}")

        return []


def obtener_horarios_disponibles(barberia_id=None, barbero_id=None, fecha=None, duracion_minutos=30):

    """

    Get available time slots for a barber on a specific date.

    Returns list of available times (30-min intervals from 09:00 to 20:30).


    SECURITY: Always validates barberia context before querying slots.

    """

    # SECURITY: Always use current context

    barberia_id = get_current_barberia_id()

    if not barberia_id or not barbero_id or not fecha:

        logger.warning(f"obtener_horarios_disponibles: missing params - barberia_id={barberia_id}, barbero_id={barbero_id}, fecha={fecha}")

        return []


    # SECURITY: Enforce access before querying

    enforce_barberia_access(barberia_id)


    try:

        from datetime import time as time_type

        identidad_barbero = resolver_barbero_agenda(barberia_id, barbero_id=barbero_id)

        if not identidad_barbero:

            logger.warning(
                "obtener_horarios_disponibles: invalid barber %s for barberia %s",
                barbero_id,
                barberia_id,
            )

            return []


        # Get all reservations for this barber on this date

        reservas = safe_fetch_all(

            """

            SELECT inicio, fin FROM reservas

            WHERE barberia_id = %s

              AND DATE(inicio) = %s

              AND (

                    barbero_id = %s

                    OR (barbero_id IS NULL AND barbero = %s)

              )

            ORDER BY inicio

            """,

            (
                barberia_id,
                fecha,
                identidad_barbero["barbero_id"],
                identidad_barbero["barbero"],
            )

        )


        logger.info(f"obtener_horarios_disponibles: found {len(reservas) if reservas else 0} existing reservations for barbero_id={barbero_id} on {fecha}")


        # Generate all 30-minute slots

        horarios_disponibles = []

        slot_time = datetime.combine(fecha, time_type(9, 0))  # Start at 09:00

        fin_dia = datetime.combine(fecha, time_type(21, 0))   # End at 21:00


        while slot_time < fin_dia:

            slot_end = slot_time + timedelta(minutes=duracion_minutos)


            # Check if this slot conflicts with any reservation

            disponible = True

            for res_inicio, res_fin in (reservas or []):

                # Check for overlap

                if slot_time < res_fin and slot_end > res_inicio:

                    disponible = False

                    break


            if disponible:

                horarios_disponibles.append(slot_time.time())


            slot_time += timedelta(minutes=30)


        logger.info(f"obtener_horarios_disponibles: returning {len(horarios_disponibles)} available slots for duration={duracion_minutos}min")

        return horarios_disponibles

    except Exception as e:

        logger.exception(f"Error getting available times for barbero={barbero_id}, fecha={fecha}: {str(e)}")

        return []
