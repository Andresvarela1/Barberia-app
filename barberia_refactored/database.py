"""
database.py
------------

This module encapsulates all direct interactions with the PostgreSQL
database. By isolating database logic here, the rest of the application
can remain agnostic of the underlying database driver (psycopg2) and
focus on business logic. It also provides helper functions that
enforce multi‑tenant isolation by requiring a `barberia_id` in
queries.

Functions exposed by this module:

    create_connection() -> connection
        Create and return a new psycopg2 connection using the
        `DATABASE_URL` defined in `config.py`. Each call returns a
        fresh connection; callers are responsible for closing it.

    execute_query(query: str, params: tuple = None) -> list[dict]
        Execute a read‑only SQL query and return all rows as a list of
        dictionaries. Each dictionary maps column names to values.

    execute_write(query: str, params: tuple = None) -> None
        Execute a write query (INSERT/UPDATE/DELETE). Changes are
        committed automatically. Returns nothing.

    safe_execute_query(barberia_id: int, query: str, params: tuple = None) -> list[dict]
        Execute a read‑only query in a multi‑tenant safe way. Ensures
        that `barberia_id` is part of the WHERE clause by requiring a
        placeholder in the query text. Automatically prepends
        `barberia_id` to the parameters.

    safe_execute_write(barberia_id: int, query: str, params: tuple = None) -> None
        Execute a write query with the same multi‑tenant safety check as
        `safe_execute_query`.

Feel free to extend this module with additional helpers (for example,
transaction management or connection pooling) as the application grows.
"""

from __future__ import annotations

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Any, Iterable, List, Optional

from config import DATABASE_URL


def create_connection() -> psycopg2.extensions.connection:
    """Create a new database connection.

    Returns:
        psycopg2.extensions.connection: A new connection object.
    """
    # sslmode="require" enforces TLS encryption when connecting to
    # remote databases such as Supabase. Local development can omit
    # this parameter if desired. Additional connection arguments can be
    # configured here (e.g. connection timeout).
    return psycopg2.connect(DATABASE_URL, sslmode="require", cursor_factory=RealDictCursor)


def execute_query(query: str, params: Optional[Iterable[Any]] = None) -> List[dict]:
    """Execute a SELECT query and return all rows as dicts.

    Args:
        query (str): The SQL query to execute. Should use `%s`
            placeholders for parameters to avoid SQL injection.
        params (Iterable[Any] | None): Values to bind to the query
            placeholders. Defaults to `None`.

    Returns:
        List[dict]: A list of rows represented as dictionaries.
    """
    params = params or ()
    with create_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
    return [dict(row) for row in rows]


def execute_write(query: str, params: Optional[Iterable[Any]] = None) -> None:
    """Execute an INSERT/UPDATE/DELETE statement.

    Args:
        query (str): The SQL query to execute.
        params (Iterable[Any] | None): Values to bind to the query
            placeholders. Defaults to `None`.

    Returns:
        None

    Raises:
        Exception: Propagates exceptions from psycopg2 if the query
            fails. The caller should handle errors appropriately.
    """
    params = params or ()
    with create_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()


def _ensure_barberia_in_query(query: str) -> None:
    """Internal helper to check that barberia_id appears in the WHERE clause.

    Args:
        query (str): The SQL query to check.

    Raises:
        ValueError: If the query does not include a reference to
            `barberia_id` in its text.
    """
    lowered = query.lower()
    if "barberia_id" not in lowered:
        raise ValueError(
            "Multi‑tenant queries must include 'barberia_id' in the WHERE clause to prevent data leaks"
        )


def safe_execute_query(barberia_id: int, query: str, params: Optional[Iterable[Any]] = None) -> List[dict]:
    """Execute a SELECT query enforcing multi‑tenant isolation.

    The provided query must include a `barberia_id` placeholder in its
    WHERE clause, e.g., `... WHERE barberia_id = %s AND other_column = %s`.
    The `barberia_id` provided here will be prepended to the params
    sequence so that it binds to the first `%s` in the query.

    Args:
        barberia_id (int): The ID of the barberia (tenant) executing
            the query.
        query (str): The SQL query string with a `barberia_id` placeholder.
        params (Iterable[Any] | None): Additional parameters to bind to
            the query after `barberia_id`.

    Returns:
        List[dict]: A list of rows represented as dictionaries.
    """
    _ensure_barberia_in_query(query)
    params = params or ()
    combined_params = (barberia_id, *params)
    return execute_query(query, combined_params)


def safe_execute_write(barberia_id: int, query: str, params: Optional[Iterable[Any]] = None) -> None:
    """Execute a write query enforcing multi‑tenant isolation.

    Works like `safe_execute_query` but commits changes. Use this for
    INSERT/UPDATE/DELETE statements that must be scoped to a given
    barberia.

    Args:
        barberia_id (int): The tenant ID to scope the operation to.
        query (str): The SQL statement containing a `barberia_id`
            placeholder.
        params (Iterable[Any] | None): Additional parameters.
    """
    _ensure_barberia_in_query(query)
    params = params or ()
    combined_params = (barberia_id, *params)
    execute_write(query, combined_params)


__all__ = [
    "create_connection",
    "execute_query",
    "execute_write",
    "safe_execute_query",
    "safe_execute_write",
]