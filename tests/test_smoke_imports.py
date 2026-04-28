"""Smoke tests: verify that extracted modules import correctly and app.py parses."""

import ast
import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _add_repo_root_to_path():
    root_str = str(REPO_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def test_app_core_db_connection_importable():
    """app_core.db.connection must be importable and expose the five DB helpers."""
    _add_repo_root_to_path()

    # Use importlib so the test is independent of top-level side-effects in app.py
    spec = importlib.util.spec_from_file_location(
        "app_core.db.connection",
        REPO_ROOT / "app_core" / "db" / "connection.py",
    )
    assert spec is not None, "Could not locate app_core/db/connection.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    expected = [
        "get_database_url",
        "_masked_postgres_url",
        "create_fresh_connection",
        "get_connection",
        "is_db_available",
    ]
    for name in expected:
        assert hasattr(module, name), f"app_core.db.connection is missing: {name}"


def test_app_py_parses_as_valid_python():
    """app.py must parse without syntax errors."""
    # Use utf-8-sig to silently strip the UTF-8 BOM if present
    source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
    try:
        ast.parse(source)
    except SyntaxError as exc:
        raise AssertionError(f"app.py has a syntax error: {exc}") from exc


def test_app_py_imports_from_app_core():
    """app.py must contain an import from app_core.db.connection."""
    source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
    assert "from app_core.db.connection import" in source, (
        "app.py does not import from app_core.db.connection"
    )


def test_app_core_security_tenant_access_importable():
    """app_core.security.tenant_access must expose all 10 access helpers."""
    _add_repo_root_to_path()

    spec = importlib.util.spec_from_file_location(
        "app_core.security.tenant_access",
        REPO_ROOT / "app_core" / "security" / "tenant_access.py",
    )
    assert spec is not None, "Could not locate app_core/security/tenant_access.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    expected = [
        "normalizar_rol",
        "session_barberia_for_write",
        "effective_barberia_id",
        "get_current_barberia_id",
        "enforce_access",
        "get_user_barberia_id",
        "get_user_role",
        "can_access_barberia",
        "enforce_barberia_access",
        "get_user_id",
    ]
    for name in expected:
        assert hasattr(module, name), (
            f"app_core.security.tenant_access is missing: {name}"
        )


def test_app_py_imports_from_tenant_access():
    """app.py must import from app_core.security.tenant_access."""
    source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
    assert "from app_core.security.tenant_access import" in source, (
        "app.py does not import from app_core.security.tenant_access"
    )


def test_app_core_db_safe_queries_importable():
    """app_core.db.safe_queries must expose all 7 query helpers."""
    _add_repo_root_to_path()

    spec = importlib.util.spec_from_file_location(
        "app_core.db.safe_queries",
        REPO_ROOT / "app_core" / "db" / "safe_queries.py",
    )
    assert spec is not None, "Could not locate app_core/db/safe_queries.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    expected = [
        "execute_query",
        "fetch_one",
        "fetch_all",
        "execute_write",
        "safe_fetch_one",
        "safe_fetch_all",
        "safe_execute",
    ]
    for name in expected:
        assert hasattr(module, name), (
            f"app_core.db.safe_queries is missing: {name}"
        )


def test_app_py_imports_from_safe_queries():
    """app.py must import from app_core.db.safe_queries."""
    source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
    assert "from app_core.db.safe_queries import" in source, (
        "app.py does not import from app_core.db.safe_queries"
    )


def test_app_py_no_duplicate_db_helpers():
    """app.py must not define the extracted DB helpers itself."""
    source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
    duplicated = [
        "def execute_query",
        "def fetch_one",
        "def fetch_all",
        "def execute_write",
        "def safe_fetch_one",
        "def safe_fetch_all",
        "def safe_execute",
    ]
    for fn in duplicated:
        assert fn not in source, (
            f"app.py still defines {fn!r} — it should be imported from app_core.db.safe_queries"
        )


# ---------------------------------------------------------------------------
# app_core/services/booking_service
# ---------------------------------------------------------------------------

def test_app_core_services_booking_service_importable():
    """booking_service.py must exist and expose all 9 extracted functions."""
    _add_repo_root_to_path()

    spec = importlib.util.spec_from_file_location(
        "app_core.services.booking_service",
        REPO_ROOT / "app_core" / "services" / "booking_service.py",
    )
    assert spec is not None, "Could not locate app_core/services/booking_service.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    expected = [
        "normalizar_reserva",
        "normalizar_datetime",
        "_guardar_reserva_tx",
        "guardar_reserva",
        "actualizar_reserva",
        "eliminar_reserva",
        "insertar_reserva_con_fecha_hora",
        "obtener_reserva_por_id",
        "obtener_reserva",
    ]
    for name in expected:
        assert hasattr(module, name), (
            f"app_core.services.booking_service is missing: {name}"
        )


def test_app_py_imports_from_booking_service():
    """app.py must import from app_core.services.booking_service."""
    source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
    assert "from app_core.services.booking_service import" in source, (
        "app.py does not import from app_core.services.booking_service"
    )


def test_app_py_no_duplicate_booking_helpers():
    """app.py must not define any of the 9 extracted booking functions itself."""
    source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
    duplicated = [
        "def normalizar_reserva",
        "def normalizar_datetime",
        "def _guardar_reserva_tx",
        "def guardar_reserva",
        "def actualizar_reserva",
        "def eliminar_reserva",
        "def insertar_reserva_con_fecha_hora",
        "def obtener_reserva_por_id",
        "def obtener_reserva(",
    ]
    for fn in duplicated:
        assert fn not in source, (
            f"app.py still defines {fn!r} — it should be imported from app_core.services.booking_service"
        )


# ---------------------------------------------------------------------------
# app_core/services/availability_service
# ---------------------------------------------------------------------------

def test_app_core_services_availability_service_importable():
    """availability_service.py must expose all 3 extracted availability helpers."""
    _add_repo_root_to_path()

    spec = importlib.util.spec_from_file_location(
        "app_core.services.availability_service",
        REPO_ROOT / "app_core" / "services" / "availability_service.py",
    )
    assert spec is not None, "Could not locate app_core/services/availability_service.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    expected = [
        "listar_usuarios_barberos",
        "obtener_barberos_disponibles",
        "obtener_horarios_disponibles",
    ]
    for name in expected:
        assert hasattr(module, name), (
            f"app_core.services.availability_service is missing: {name}"
        )


def test_app_py_imports_from_availability_service():
    """app.py must import from app_core.services.availability_service."""
    source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
    assert "from app_core.services.availability_service import" in source, (
        "app.py does not import from app_core.services.availability_service"
    )


def test_app_py_no_duplicate_availability_helpers():
    """app.py must not define the 3 extracted availability functions itself."""
    source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
    duplicated = [
        "def listar_usuarios_barberos",
        "def obtener_barberos_disponibles",
        "def obtener_horarios_disponibles",
    ]
    for fn in duplicated:
        assert fn not in source, (
            f"app.py still defines {fn!r} — it should be imported from app_core.services.availability_service"
        )
