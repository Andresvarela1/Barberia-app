"""Database facade for shared connection and query helpers."""

from app_core.db.connection import (
    _masked_postgres_url,
    create_fresh_connection,
    get_connection,
    get_database_url,
    is_db_available,
)
from app_core.db.safe_queries import (
    execute_write,
    fetch_all,
    fetch_one,
    safe_execute,
    safe_fetch_all,
    safe_fetch_one,
)

__all__ = [
    "_masked_postgres_url",
    "create_fresh_connection",
    "execute_write",
    "fetch_all",
    "fetch_one",
    "get_connection",
    "get_database_url",
    "is_db_available",
    "safe_execute",
    "safe_fetch_all",
    "safe_fetch_one",
]
