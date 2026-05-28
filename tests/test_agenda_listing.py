from datetime import date, time
from unittest import TestCase, main
from unittest.mock import patch

from app_core.agenda import listing


class _FakeStreamlit:
    def markdown(self, *args, **kwargs):
        return None


class AgendaListingTests(TestCase):
    def test_calendar_results_accept_public_note_default_signature(self):
        rows = [
            {
                "id": 1,
                "cliente": "Ana",
                "nombre": "Ana",
                "barbero": "Bob",
                "servicio": "Corte",
                "monto": 10000,
                "precio": 10000,
                "fecha": date.today(),
                "hora": time(10, 0),
                "pagado": False,
            }
        ]
        seen = {"calendar": None, "note": None}

        def mostrar_calendario_reservas(data):
            seen["calendar"] = data

        def render_public_note(message, warning=False):
            seen["note"] = (message, warning)

        with patch.object(listing, "st", _FakeStreamlit()):
            listing._render_agenda_calendar_results(
                rows,
                mostrar_calendario_reservas,
                render_public_note,
            )

        self.assertEqual(len(seen["calendar"]), 1)
        self.assertIsNotNone(seen["note"])
        self.assertIn("Vista semanal del calendario", seen["note"][0])
        self.assertFalse(seen["note"][1])


if __name__ == "__main__":
    main()
