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


# ---------------------------------------------------------------------------
# app_core/services/payment_service
# ---------------------------------------------------------------------------

def test_app_core_services_payment_service_importable():
    """payment_service.py must expose the 2 extracted payment functions."""
    _add_repo_root_to_path()

    spec = importlib.util.spec_from_file_location(
        "app_core.services.payment_service",
        REPO_ROOT / "app_core" / "services" / "payment_service.py",
    )
    assert spec is not None, "Could not locate app_core/services/payment_service.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    expected = [
        "marcar_reserva_pagada",
        "crear_pago_mercadopago",
    ]
    for name in expected:
        assert hasattr(module, name), (
            f"app_core.services.payment_service is missing: {name}"
        )


def test_app_py_imports_from_payment_service():
    """app.py must import from app_core.services.payment_service."""
    source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
    assert "from app_core.services.payment_service import" in source, (
        "app.py does not import from app_core.services.payment_service"
    )


def test_app_py_no_duplicate_payment_helpers():
    """app.py must not define the extracted payment functions itself."""
    source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
    duplicated = [
        "def marcar_reserva_pagada",
        "def crear_pago_mercadopago",
    ]
    for fn in duplicated:
        assert fn not in source, (
            f"app.py still defines {fn!r} — it should be imported from app_core.services.payment_service"
        )


def test_marcar_reserva_pagada_uses_dict_access_only():
    """marcar_reserva_pagada must use only dict-key access on the reservation.

    obtener_reserva_por_id() always returns a dict. Any tuple-index access
    (e.g. prev[2], prev[7]) would silently succeed on a dict (integer key lookup)
    rather than raising, but would always return None — a latent permission bypass.
    This test guards against reintroducing that mixed access.
    """
    import re
    source = (REPO_ROOT / "app_core" / "services" / "payment_service.py").read_text(encoding="utf-8")

    # Extract only the body of marcar_reserva_pagada (stop at the next top-level def)
    fn_start = source.find("def marcar_reserva_pagada(")
    assert fn_start != -1, "marcar_reserva_pagada not found in payment_service.py"
    next_def = source.find("\ndef ", fn_start + 1)
    fn_body = source[fn_start:next_def] if next_def != -1 else source[fn_start:]

    # Detect tuple-index access pattern on `prev`: prev[<integer>]
    bad_accesses = re.findall(r"\bprev\s*\[\s*\d+\s*\]", fn_body)
    assert not bad_accesses, (
        f"marcar_reserva_pagada uses tuple-index access on dict 'prev': {bad_accesses}. "
        "Use dict key access (prev.get(...)) instead."
    )


# ---------------------------------------------------------------------------
# app_core.integrations.mercadopago_service
# ---------------------------------------------------------------------------

def test_app_core_integrations_mercadopago_service_importable():
    """app_core.integrations.mercadopago_service must be importable and expose the three helpers."""
    _add_repo_root_to_path()
    mod = importlib.import_module("app_core.integrations.mercadopago_service")
    for name in ("get_sdk", "validate_monto", "extract_init_point"):
        assert hasattr(mod, name), (
            f"app_core.integrations.mercadopago_service is missing '{name}'"
        )


def test_payment_service_uses_integration_helpers():
    """payment_service.py must import from the integration module, not inline the SDK."""
    source = (REPO_ROOT / "app_core" / "services" / "payment_service.py").read_text(encoding="utf-8")
    assert "from app_core.integrations.mercadopago_service import" in source, (
        "payment_service.py does not import from app_core.integrations.mercadopago_service"
    )
    # Inline SDK init must be gone
    assert "mercadopago.SDK(" not in source, (
        "payment_service.py still contains an inline mercadopago.SDK() call — "
        "delegate to get_sdk() from the integration module"
    )


def test_extract_init_point_logic():
    """extract_init_point must correctly validate MP preference responses."""
    _add_repo_root_to_path()
    from app_core.integrations.mercadopago_service import extract_init_point

    # Good response
    good = {"status": 201, "response": {"init_point": "https://mp.com/checkout"}}
    assert extract_init_point(good) == "https://mp.com/checkout"

    # Wrong status
    assert extract_init_point({"status": 400, "response": {"init_point": "x"}}) is None

    # Missing init_point
    assert extract_init_point({"status": 201, "response": {}}) is None

    # Not a dict
    assert extract_init_point("not-a-dict") is None
