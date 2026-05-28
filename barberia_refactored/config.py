"""
config.py
------------

This module centralizes application configuration. It is responsible for
loading environment variables and exposing configuration constants that
other modules can import. Keeping configuration in a single place makes
the application easier to manage and reduces the risk of hard‑coding
values throughout the codebase.

Usage:
    from config import DATABASE_URL

The `DATABASE_URL` constant is pulled from either the `DATABASE_URL` or
`SUPABASE_DB_URL` environment variables. If neither is present the
application will raise an exception at import time. Additional
configuration values (such as API keys or feature flags) can be added
here as needed.
"""

import os
from dotenv import load_dotenv


# Load variables from a .env file if present. This makes local
# development more convenient while still supporting environment
# variables in production environments.
load_dotenv()


def _get_database_url() -> str:
    """Return the database connection string.

    The application supports two environment variable names for the
    database URL: `DATABASE_URL` and `SUPABASE_DB_URL`. The latter is
    provided for backwards compatibility with deployments on Supabase.

    Returns:
        str: The first non‑empty database URL found.

    Raises:
        RuntimeError: If neither environment variable is defined.
    """
    url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable must be set (or SUPABASE_DB_URL for legacy support)"
        )
    return url


# Expose the resolved database URL as a module‑level constant. This
# assignment happens at import time and will raise a clear error if no
# database URL is available. Downstream modules can simply do
# `from config import DATABASE_URL` and rely on this value being set.
DATABASE_URL: str = _get_database_url()


__all__ = ["DATABASE_URL"]