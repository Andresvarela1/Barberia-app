"""
Refactored Streamlit application entry point.

This simplified version of the barbershop reservation system demonstrates
how to structure the application using separate modules for
configuration (`config.py`), database operations (`database.py`) and
SQL definitions (`queries.py`). By splitting responsibilities into
distinct files, the application becomes easier to maintain and extend.

To run this app locally, install the required dependencies (e.g.
`streamlit`, `psycopg2`, `python-dotenv`), set the `DATABASE_URL`
environment variable pointing to your PostgreSQL database, and then
execute:

    streamlit run barberia_refactored/app.py

The app will ensure core tables exist and display a simple list of
today's reservations for the selected barberia.
"""

import datetime
import streamlit as st

from database import execute_write, safe_execute_query
from queries import (
    CREATE_BARBERIAS_TABLE,
    CREATE_USUARIOS_TABLE,
    CREATE_SERVICIOS_TABLE,
    CREATE_RESERVAS_TABLE,
    GET_RESERVAS_BY_DATE,
)


def ensure_database_schema() -> None:
    """Create core tables if they do not already exist.

    This function runs unscoped DDL statements because table
    definitions themselves are shared across tenants. It is idempotent
    – running it multiple times has no side effects.
    """
    execute_write(CREATE_BARBERIAS_TABLE)
    execute_write(CREATE_USUARIOS_TABLE)
    execute_write(CREATE_SERVICIOS_TABLE)
    execute_write(CREATE_RESERVAS_TABLE)


def list_reservas_hoy(barberia_id: int) -> None:
    """Render today's reservations for a given barberia in the Streamlit UI.

    Args:
        barberia_id (int): The ID of the barberia to list reservations for.
    """
    today = datetime.date.today().isoformat()
    rows = safe_execute_query(barberia_id, GET_RESERVAS_BY_DATE, params=(today,))
    if rows:
        st.table(rows)
    else:
        st.info("No hay reservas para hoy.")


def main() -> None:
    st.set_page_config(page_title="Sistema de Barberías", page_icon="💈")
    st.title("Panel de Barbería")

    # Ensure tables exist before any other operations. In a more
    # sophisticated app, this could be done via a migration tool.
    ensure_database_schema()

    # Select the current barberia. In a full implementation this list
    # would come from the database. Here we use placeholder IDs for
    # demonstration.
    barberia_id = st.number_input(
        "ID de la barbería", min_value=1, max_value=100, value=1, step=1
    )

    st.subheader("Reservas de hoy")
    list_reservas_hoy(barberia_id)


if __name__ == "__main__":
    main()