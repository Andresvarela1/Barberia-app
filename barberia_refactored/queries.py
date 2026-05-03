"""
queries.py
-----------

Define the raw SQL statements used throughout the application. Keeping
SQL in a dedicated module makes it easier to see and maintain the
database schema and queries in one place. Functions in
`database.py` can reference these constants when executing statements.

Only a subset of the original application's queries are included
here for demonstration purposes. Expand this module as needed to
cover all CRUD operations for your models.
"""

# DDL statements to create core tables if they do not exist. These
# definitions are simplified versions of the tables used in the original
# application. Adjust column names and constraints to match your
# production schema.

CREATE_BARBERIAS_TABLE = """
CREATE TABLE IF NOT EXISTS barberias (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);
"""


CREATE_USUARIOS_TABLE = """
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    contrasena TEXT NOT NULL,
    rol TEXT NOT NULL,
    barberia_id INTEGER NOT NULL REFERENCES barberias(id),
    created_at TIMESTAMP DEFAULT NOW()
);
"""


CREATE_SERVICIOS_TABLE = """
CREATE TABLE IF NOT EXISTS servicios (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    duracion INTEGER NOT NULL,
    precio INTEGER NOT NULL,
    icono TEXT,
    barberia_id INTEGER NOT NULL REFERENCES barberias(id)
);
"""


CREATE_RESERVAS_TABLE = """
CREATE TABLE IF NOT EXISTS reservas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    servicio_id INTEGER NOT NULL REFERENCES servicios(id),
    fecha TIMESTAMP NOT NULL,
    estado TEXT NOT NULL,
    barberia_id INTEGER NOT NULL REFERENCES barberias(id)
);
"""


# Example multi‑tenant select query. Note the explicit `barberia_id` in
# the WHERE clause – this is required when using the safe execution
# helpers defined in `database.py`.
GET_RESERVAS_BY_DATE = """
SELECT r.id, u.nombre AS cliente, s.nombre AS servicio, r.fecha, r.estado
FROM reservas r
JOIN usuarios u ON r.usuario_id = u.id
JOIN servicios s ON r.servicio_id = s.id
WHERE r.barberia_id = %s AND DATE(r.fecha) = %s
ORDER BY r.fecha;
"""


__all__ = [
    "CREATE_BARBERIAS_TABLE",
    "CREATE_USUARIOS_TABLE",
    "CREATE_SERVICIOS_TABLE",
    "CREATE_RESERVAS_TABLE",
    "GET_RESERVAS_BY_DATE",
]