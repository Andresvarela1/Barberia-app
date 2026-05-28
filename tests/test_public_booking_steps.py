import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app_core.public_booking.steps import _build_public_booking_summary_data


class PublicBookingStepsTests(unittest.TestCase):
    def test_build_public_booking_summary_data_uses_structured_customer_fields(self):
        payload = {
            "servicio": "Corte",
            "barbero_nombre": "Juan",
            "fecha": "2026-05-28",
            "hora": "18:30",
            "precio": 15000,
            "reserva_id": 42,
            "nombre": "Ana",
            "telefono": "56911111111",
            "email": "ana@example.com",
        }

        summary = _build_public_booking_summary_data(payload)

        self.assertEqual(summary["servicio"], "Corte")
        self.assertEqual(summary["barbero_nombre"], "Juan")
        self.assertNotIn("nombre", summary)
        self.assertEqual(
            summary["customer_fields"],
            [
                ("Cliente", "Ana", "N/A"),
                ("Telefono", "56911111111", "N/A"),
                ("Email", "ana@example.com", "-"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
