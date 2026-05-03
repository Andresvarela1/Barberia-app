from datetime import date, datetime, time
from types import SimpleNamespace

import pytest

from app_core.services import booking_service


class FakeStreamlit:
    def __init__(self):
        self.session_state = {}
        self.errors = []
        self.warnings = []

    def error(self, message):
        self.errors.append(message)

    def warning(self, message):
        self.warnings.append(message)


class FakeCursor:
    def __init__(self, fetchone_results=None, execute_side_effects=None):
        self.fetchone_results = list(fetchone_results or [])
        self.execute_side_effects = list(execute_side_effects or [])
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params=None):
        self.executed.append((query, params))
        if self.execute_side_effects:
            effect = self.execute_side_effects.pop(0)
            if effect is not None:
                raise effect

    def fetchone(self):
        if self.fetchone_results:
            return self.fetchone_results.pop(0)
        return None


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class FakePsycopgError(Exception):
    def __init__(self, pgcode=None, constraint_name=None):
        super().__init__("fake db error")
        self.pgcode = pgcode
        self.diag = SimpleNamespace(constraint_name=constraint_name)


@pytest.fixture(autouse=True)
def fake_streamlit(monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setattr(booking_service, "st", fake)
    monkeypatch.setattr(
        booking_service,
        "session_barberia_for_write",
        lambda: fake.session_state.get("barberia_context_id")
        or fake.session_state.get("barberia_id"),
    )
    return fake


def test_insertar_reserva_con_fecha_hora_valida(monkeypatch, fake_streamlit):
    fake_streamlit.session_state["db_available"] = True
    monkeypatch.setattr(
        booking_service,
        "resolver_barbero_agenda",
        lambda barberia_id, barbero=None, barbero_id=None: {
            "barbero_id": 7,
            "barbero": "nico",
        },
    )
    cursor = FakeCursor(fetchone_results=[None, (321,)])
    conn = FakeConnection(cursor)
    monkeypatch.setattr(booking_service, "get_connection", lambda: conn)

    reserva_id = booking_service.insertar_reserva_con_fecha_hora(
        1,
        "juan",
        7,
        "Corte",
        date(2026, 5, 4),
        time(10, 0),
        15000,
        30,
        barbero_nombre="nico",
    )

    assert reserva_id == 321
    assert conn.committed is True
    assert fake_streamlit.errors == []


def test_insertar_reserva_con_fecha_hora_conflicto(monkeypatch, fake_streamlit):
    fake_streamlit.session_state["db_available"] = True
    monkeypatch.setattr(
        booking_service,
        "resolver_barbero_agenda",
        lambda barberia_id, barbero=None, barbero_id=None: {
            "barbero_id": 7,
            "barbero": "nico",
        },
    )
    cursor = FakeCursor(fetchone_results=[(55,)])
    conn = FakeConnection(cursor)
    monkeypatch.setattr(booking_service, "get_connection", lambda: conn)

    reserva_id = booking_service.insertar_reserva_con_fecha_hora(
        1,
        "juan",
        7,
        "Corte",
        date(2026, 5, 4),
        time(10, 0),
        15000,
        30,
        barbero_nombre="nico",
    )

    assert reserva_id is False
    assert any("Horario ocupado" in msg for msg in fake_streamlit.errors)
    assert conn.rolled_back is True


def test_actualizar_reserva_conflicto(monkeypatch, fake_streamlit):
    fake_streamlit.session_state.update(
        {
            "db_available": True,
            "user": (5, "admin_user", "x", "ADMIN"),
            "barberia_id": 1,
        }
    )
    monkeypatch.setattr(
        booking_service,
        "obtener_reserva_por_id",
        lambda reserva_id: {
            "id": reserva_id,
            "nombre": "juan",
            "barbero": "nico",
            "barbero_id": 7,
            "servicio": "Corte",
            "precio": 15000,
            "inicio": datetime(2026, 5, 4, 10, 0),
            "fin": datetime(2026, 5, 4, 10, 30),
            "barberia_id": 1,
            "cliente": "juan",
        },
    )
    monkeypatch.setattr(
        booking_service,
        "resolver_barbero_agenda",
        lambda barberia_id, barbero=None, barbero_id=None: {
            "barbero_id": 8,
            "barbero": "lucho",
        },
    )
    cursor = FakeCursor(fetchone_results=[(88,)])
    conn = FakeConnection(cursor)
    monkeypatch.setattr(booking_service, "get_connection", lambda: conn)

    ok = booking_service.actualizar_reserva(
        99,
        "juan",
        "lucho",
        "Corte",
        15000,
        datetime(2026, 5, 4, 10, 15),
        datetime(2026, 5, 4, 10, 45),
        barbero_id=8,
    )

    assert ok is False
    assert any("solapamiento" in msg for msg in fake_streamlit.errors)
    assert conn.rolled_back is True


def test_insertar_reserva_con_fecha_hora_maneja_rechazo_db(monkeypatch, fake_streamlit):
    fake_streamlit.session_state["db_available"] = True
    monkeypatch.setattr(booking_service.psycopg2, "Error", FakePsycopgError)
    monkeypatch.setattr(
        booking_service,
        "resolver_barbero_agenda",
        lambda barberia_id, barbero=None, barbero_id=None: {
            "barbero_id": 7,
            "barbero": "nico",
        },
    )
    db_error = FakePsycopgError(pgcode="23P01", constraint_name="reservas_no_solapadas")
    cursor = FakeCursor(fetchone_results=[None], execute_side_effects=[None, None, db_error])
    conn = FakeConnection(cursor)
    monkeypatch.setattr(booking_service, "get_connection", lambda: conn)

    ok = booking_service.insertar_reserva_con_fecha_hora(
        1,
        "juan",
        7,
        "Corte",
        date(2026, 5, 4),
        time(10, 0),
        15000,
        30,
        barbero_nombre="nico",
    )

    assert ok is False
    assert any("se acaba de ocupar" in msg for msg in fake_streamlit.errors)
    assert conn.rolled_back is True
