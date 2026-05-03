"""Servicios CRUD and barberia lookup queries.

Extracted from app.py.  All public names keep their original signatures.
"""

import logging

from app_core.db.safe_queries import fetch_one, safe_fetch_all, safe_execute
from app_core.security.tenant_access import get_current_barberia_id

logger = logging.getLogger("barberia_app")


def obtener_barberia_por_slug(slug):
    """Get barberia by slug for public booking."""
    if not slug:
        return None
    try:
        result = fetch_one(
            """SELECT id, nombre, slug, telefono, email, ciudad, direccion,
                      latitud, longitud, color_primario, logo_url,
                      hora_apertura, hora_cierre, estado
               FROM barberias WHERE slug = %s""",
            (slug,),
        )
        if result:
            return {
                "id": result[0],
                "nombre": result[1],
                "slug": result[2],
                "telefono": result[3],
                "email": result[4],
                "ciudad": result[5],
                "direccion": result[6],
                "latitud": result[7],
                "longitud": result[8],
                "color_primario": result[9],
                "logo_url": result[10],
                "hora_apertura": result[11],
                "hora_cierre": result[12],
                "estado": result[13],
            }
        return None
    except Exception as e:
        logger.exception(f"Error getting barberia by slug: {str(e)}")
        return None


def obtener_servicios(barberia_id=None):
    """Load services from database for a barberia.

    SECURITY: Always uses current barberia context - prevents service leakage
    between barberias.
    """
    barberia_id = get_current_barberia_id()
    if not barberia_id:
        return []
    try:
        results = safe_fetch_all(
            """SELECT id, nombre, duracion_minutos, precio, descripcion, icono
               FROM servicios
               WHERE barberia_id = %s
               ORDER BY id ASC""",
            (barberia_id,),
        )
        servicios_list = []
        for row in results:
            servicios_list.append({
                "id": row[0],
                "nombre": row[1],
                "duracion": row[2],
                "precio": row[3],
                "descripcion": row[4],
                "icono": row[5] or "Servicio",
            })
        return servicios_list
    except Exception as e:
        logger.exception(f"Error loading services for barberia {barberia_id}: {e}")
        return []


def crear_servicio(barberia_id, nombre, duracion, precio, descripcion, icono):
    """Insert a new service for a barberia. Returns True on success."""
    current = get_current_barberia_id()
    if int(barberia_id) != int(current):
        raise Exception("SECURITY: barberia_id mismatch in crear_servicio")
    try:
        safe_execute(
            """INSERT INTO servicios (barberia_id, nombre, duracion_minutos, precio, descripcion, icono)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (barberia_id, nombre) DO NOTHING""",
            (barberia_id, nombre.strip(), int(duracion), int(precio), descripcion.strip(), icono.strip()),
        )
        return True
    except Exception as e:
        logger.exception(f"Error creating service: {e}")
        return False


def actualizar_servicio(servicio_id, barberia_id, nombre, duracion, precio, descripcion, icono):
    """Update an existing service. Enforces barberia_id ownership."""
    current = get_current_barberia_id()
    if int(barberia_id) != int(current):
        raise Exception("SECURITY: barberia_id mismatch in actualizar_servicio")
    try:
        safe_execute(
            """UPDATE servicios
               SET nombre = %s, duracion_minutos = %s, precio = %s, descripcion = %s, icono = %s
               WHERE id = %s AND barberia_id = %s""",
            (nombre.strip(), int(duracion), int(precio), descripcion.strip(), icono.strip(), int(servicio_id), int(barberia_id)),
        )
        return True
    except Exception as e:
        logger.exception(f"Error updating service {servicio_id}: {e}")
        return False


def eliminar_servicio(servicio_id, barberia_id):
    """Delete a service. Enforces barberia_id ownership."""
    current = get_current_barberia_id()
    if int(barberia_id) != int(current):
        raise Exception("SECURITY: barberia_id mismatch in eliminar_servicio")
    try:
        safe_execute(
            "DELETE FROM servicios WHERE id = %s AND barberia_id = %s",
            (int(servicio_id), int(barberia_id)),
        )
        return True
    except Exception as e:
        logger.exception(f"Error deleting service {servicio_id}: {e}")
        return False
