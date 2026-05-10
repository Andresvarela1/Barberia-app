"""Barberia lookup and registration helpers extracted from app.py."""

import logging

from app_core.auth import hash_password
from app_core.db.safe_queries import safe_execute, safe_fetch_all, safe_fetch_one

logger = logging.getLogger("barberia_app")


def get_default_barberia_id():
    row = safe_fetch_one("SELECT id FROM barberias ORDER BY id LIMIT 1")
    return row[0] if row else None


def check_barberia_name_exists(nombre):
    """Check if barber shop name already exists."""
    try:
        existing = safe_fetch_one(
            "SELECT id FROM barberias WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
            (nombre,),
        )
        return existing is not None
    except Exception as exc:
        logger.warning("Error checking barberia name: %s", str(exc))
        return False


def _build_barberia_slug(nombre):
    normalized = nombre.lower()
    slug = (
        normalized.replace(" ", "-")
        .replace("\u00e1", "a")
        .replace("\u00e9", "e")
        .replace("\u00ed", "i")
        .replace("\u00f3", "o")
        .replace("\u00fa", "u")
        .replace("\u00f1", "n")
    )
    return "".join(char for char in slug if char.isalnum() or char in "-_")


def create_barberia_in_db(data):
    """Create barberia record in database. Returns barberia_id or None."""
    slug = _build_barberia_slug(data["nombre"])

    try:
        result = safe_execute(
            """
            INSERT INTO barberias
            (nombre, slug, telefono, email, ciudad, direccion, latitud, longitud,
             color_primario, hora_apertura, hora_cierre, logo_url, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                data["nombre"],
                slug,
                data["telefono"],
                data["email"],
                data["ciudad"],
                data.get("direccion") or None,
                data.get("latitud"),
                data.get("longitud"),
                data["color_primario"],
                data["hora_apertura"],
                data["hora_cierre"],
                data["logo_url"] or None,
                "activa",
            ),
            fetch_one_result=True,
            allow_system=True,
            system_reason="super admin creates barberia record",
        )

        if result and result[0]:
            logger.info(
                "[OK] Barberia creada: %s (ID: %s, Slug: %s)",
                data["nombre"],
                result[0],
                slug,
            )
            return result[0]
        return None
    except Exception as exc:
        logger.exception("Error creating barberia: %s", str(exc))
        return None


def create_admin_user_in_db(barberia_id, slug, telefono):
    """Create admin user. Returns (username, password) or (None, None)."""
    admin_user = f"admin_{slug}"
    admin_password = "admin123"
    admin_hash = hash_password(admin_password)

    try:
        safe_execute(
            """
            INSERT INTO usuarios (usuario, password, rol, barberia_id, telefono)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (admin_user, admin_hash, "ADMIN", barberia_id, telefono),
        )
        logger.info("[OK] Admin user creado: %s", admin_user)
        return admin_user, admin_password
    except Exception as exc:
        logger.exception("Error creating admin user: %s", str(exc))
        return None, None


def create_services_in_db(barberia_id, services):
    """Create services. Returns count of created services."""
    count = 0

    try:
        for service in services:
            safe_execute(
                """
                INSERT INTO servicios
                (barberia_id, nombre, duracion_minutos, precio, icono)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    barberia_id,
                    service["nombre"],
                    service["duracion"],
                    int(service["precio"]),
                    "Servicio",
                ),
            )
            count += 1

        logger.info("[OK] Servicios creados: %s", count)
        return count
    except Exception as exc:
        logger.exception("Error creating services: %s", str(exc))
        return 0


def create_barbers_in_db(barberia_id, barbers):
    """Create barber users. Returns dict of username:password pairs."""
    barber_passwords = {}

    try:
        for barber in barbers:
            barber_password = f"barber_{barber['usuario'][:3]}123"
            barber_hash = hash_password(barber_password)

            safe_execute(
                """
                INSERT INTO usuarios (usuario, password, rol, barberia_id, telefono, nombre, apellido)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    barber["usuario"],
                    barber_hash,
                    "BARBERO",
                    barberia_id,
                    None,
                    barber["nombre"],
                    barber["apellido"],
                ),
            )
            barber_passwords[barber["usuario"]] = barber_password

        logger.info("[OK] Barberos creados: %s", len(barber_passwords))
        return barber_passwords
    except Exception as exc:
        logger.exception("Error creating barbers: %s", str(exc))
        return {}


def obtener_todas_barberias(ciudad=None, servicio=None):
    """Fetch all public barberias with optional filters."""
    try:
        query = (
            "SELECT id, nombre, slug, telefono, email, ciudad, direccion, latitud, "
            "longitud, color_primario, logo_url, hora_apertura, hora_cierre, estado "
            "FROM barberias WHERE estado = %s"
        )
        params = ["active"]

        if ciudad and ciudad.strip():
            query += " AND LOWER(ciudad) LIKE LOWER(%s)"
            params.append(f"%{ciudad.strip()}%")

        # TODO: Implement servicio filter by joining with servicios table
        # if servicio and servicio.strip():
        #     query += " AND id IN (SELECT DISTINCT barberia_id FROM servicios WHERE LOWER(nombre) LIKE LOWER(%s))"
        #     params.append(f"%{servicio.strip()}%")

        query += " ORDER BY nombre ASC"
        results = safe_fetch_all(query, tuple(params))

        barberias_list = []
        for row in results:
            barberias_list.append(
                {
                    "id": row[0],
                    "nombre": row[1],
                    "slug": row[2],
                    "telefono": row[3],
                    "email": row[4],
                    "ciudad": row[5],
                    "direccion": row[6],
                    "latitud": float(row[7]) if row[7] else None,
                    "longitud": float(row[8]) if row[8] else None,
                    "color_primario": row[9],
                    "logo_url": row[10],
                    "hora_apertura": row[11],
                    "hora_cierre": row[12],
                    "estado": row[13],
                }
            )

        return barberias_list
    except Exception as exc:
        logger.exception("Error fetching barberias: %s", exc)
        return []
