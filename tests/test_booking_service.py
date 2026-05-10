from datetime import date, datetime, time
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import patch

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


class BookingServiceTests(TestCase):
    def setUp(self):
        self.fake_streamlit = FakeStreamlit()
        self.streamlit_patcher = patch.object(booking_service, "st", self.fake_streamlit)
        self.streamlit_patcher.start()
        self.addCleanup(self.streamlit_patcher.stop)

        self.session_barberia_patcher = patch.object(
            booking_service,
            "session_barberia_for_write",
            lambda: self.fake_streamlit.session_state.get("barberia_context_id")
            or self.fake_streamlit.session_state.get("barberia_id"),
        )
        self.session_barberia_patcher.start()
        self.addCleanup(self.session_barberia_patcher.stop)

    def test_insertar_reserva_con_fecha_hora_valida(self):
        self.fake_streamlit.session_state["db_available"] = True

        with patch.object(
            booking_service,
            "resolver_barbero_agenda",
            return_value={"barbero_id": 7, "barbero": "nico"},
        ), patch.object(
            booking_service,
            "get_connection",
            return_value=FakeConnection(FakeCursor(fetchone_results=[None, (321,)])),
        ) as conn_mock:
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

        conn = conn_mock.return_value
        self.assertEqual(reserva_id, 321)
        self.assertTrue(conn.committed)
        self.assertEqual(self.fake_streamlit.errors, [])

    def test_insertar_reserva_con_fecha_hora_conflicto(self):
        self.fake_streamlit.session_state["db_available"] = True

        with patch.object(
            booking_service,
            "resolver_barbero_agenda",
            return_value={"barbero_id": 7, "barbero": "nico"},
        ), patch.object(
            booking_service,
            "get_connection",
            return_value=FakeConnection(FakeCursor(fetchone_results=[(55,)])),
        ) as conn_mock:
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

        conn = conn_mock.return_value
        self.assertFalse(reserva_id)
        self.assertTrue(any("Horario ocupado" in msg for msg in self.fake_streamlit.errors))
        self.assertTrue(conn.rolled_back)

    def test_actualizar_reserva_conflicto(self):
        self.fake_streamlit.session_state.update(
            {
                "db_available": True,
                "user": (5, "admin_user", "x", "ADMIN"),
                "barberia_id": 1,
            }
        )

        with patch.object(
            booking_service,
            "obtener_reserva_por_id",
            return_value={
                "id": 99,
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
        ), patch.object(
            booking_service,
            "resolver_barbero_agenda",
            return_value={"barbero_id": 8, "barbero": "lucho"},
        ), patch.object(
            booking_service,
            "get_connection",
            return_value=FakeConnection(FakeCursor(fetchone_results=[(88,)])),
        ) as conn_mock:
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

        conn = conn_mock.return_value
        self.assertFalse(ok)
        self.assertTrue(any("solapamiento" in msg for msg in self.fake_streamlit.errors))
        self.assertTrue(conn.rolled_back)

    def test_eliminar_reserva_valida(self):
        self.fake_streamlit.session_state.update(
            {
                "db_available": True,
                "user": (5, "admin_user", "x", "ADMIN"),
                "barberia_id": 1,
            }
        )

        with patch.object(
            booking_service,
            "obtener_reserva_por_id",
            return_value={
                "id": 55,
                "nombre": "juan",
                "cliente": "juan",
                "barbero": "nico",
                "barbero_id": 7,
                "barberia_id": 1,
            },
        ), patch.object(
            booking_service,
            "safe_execute",
            return_value=True,
        ) as execute_mock:
            ok = booking_service.eliminar_reserva(55)

        self.assertTrue(ok)
        execute_mock.assert_called_once_with(
            "DELETE FROM reservas WHERE id = %s AND barberia_id = %s",
            (55, 1),
        )

    def test_insertar_reserva_con_fecha_hora_maneja_rechazo_db(self):
        self.fake_streamlit.session_state["db_available"] = True

        with patch.object(booking_service.psycopg2, "Error", FakePsycopgError), patch.object(
            booking_service,
            "resolver_barbero_agenda",
            return_value={"barbero_id": 7, "barbero": "nico"},
        ):
            db_error = FakePsycopgError(
                pgcode="23P01",
                constraint_name="reservas_no_solapadas",
            )
            conn = FakeConnection(
                FakeCursor(fetchone_results=[None], execute_side_effects=[None, None, db_error])
            )

            with patch.object(booking_service, "get_connection", return_value=conn):
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

        self.assertFalse(ok)
        self.assertTrue(any("se acaba de ocupar" in msg for msg in self.fake_streamlit.errors))
        self.assertTrue(conn.rolled_back)


if __name__ == "__main__":
    main()
