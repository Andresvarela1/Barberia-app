"""Database connection helpers for the Streamlit app."""

import logging
import os
import socket
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
import streamlit as st
from dotenv import load_dotenv


_dotenv_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_dotenv_path)

logger = logging.getLogger("barberia_app")

_db_url_missing_notified = False


def get_database_url():

    return os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")


def _masked_postgres_url(parsed):

    username = parsed.username or ""

    host = parsed.hostname or ""

    port = parsed.port or 5432

    dbname = (parsed.path or "").lstrip("/") or ""

    auth = f"{username}:***@" if username else ""

    db_part = f"/{dbname}" if dbname else ""

    return f"{parsed.scheme}://{auth}{host}:{port}{db_part}"


def create_fresh_connection():

    """Create a fresh database connection."""

    global _db_url_missing_notified

    database_url = get_database_url()

    if not database_url:

        message = (

            "DATABASE_URL o SUPABASE_DB_URL no está configurada. "

            "Define una de estas variables de entorno en el sistema o en la configuración "

            "de despliegue (sin hardcodear credenciales en el código)."

        )

        logger.error(message)

        if not _db_url_missing_notified:

            _db_url_missing_notified = True

        return None

    try:

        database_url = database_url.strip()

        if "[YOUR-PASSWORD]" in database_url:

            return None

        parsed = urlparse(database_url)

        if parsed.scheme not in ("postgresql", "postgres"):

            return None

        host = parsed.hostname

        port = parsed.port or 5432

        dbname = (parsed.path or "").lstrip("/")

        if not host or not dbname:

            return None

        masked = _masked_postgres_url(parsed)

        logger.info("📍 Creando conexión PostgreSQL: %s", masked)

        try:

            socket.getaddrinfo(host, port)

        except socket.gaierror:

            logger.error("Host resolution failed")

            return None

        conn = psycopg2.connect(

            database_url,

            sslmode="require",

            connect_timeout=5,

            options="-c statement_timeout=8000",

        )

        logger.info("[OK] Conexión a DB creada exitosamente")

        return conn

    except Exception as e:

        logger.exception("Error al conectar con PostgreSQL")

        return None


def get_connection(*, notify_missing_url: bool = True):

    """Get safe database connection using session state with minimal overhead."""

    try:

        # Fast path: return existing connection if available and valid

        conn = st.session_state.get("db_connection")

        if conn is not None and not conn.closed:

            return conn


        # Create new connection only when needed

        conn = create_fresh_connection()

        if conn is not None:

            st.session_state.db_connection = conn

        elif notify_missing_url and not _db_url_missing_notified:

            message = (

                "DATABASE_URL o SUPABASE_DB_URL no está configurada. "

                "Define una de estas variables de entorno en el sistema o en la configuración "

                "de despliegue (sin hardcodear credenciales en el código)."

            )

            st.error(message)


        return conn

    except Exception as e:

        logger.exception("Error crítico en get_connection")

        if notify_missing_url:

            st.error("Error de conexión a la base de datos")

        return None


def is_db_available():

    """True if a PostgreSQL connection can be opened."""

    try:

        conn = get_connection(notify_missing_url=False)

        return conn is not None

    except Exception:

        logger.info("Base de datos no disponible (fallo de conexión).", exc_info=True)

        return False
