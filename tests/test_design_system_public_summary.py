import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import design_system


class PublicBookingSummaryTests(unittest.TestCase):
    def test_render_public_booking_summary_escapes_customer_fields(self):
        data = {
            "servicio": "Corte</div>",
            "barbero_nombre": "<b>Juan</b>",
            "fecha": "2026-05-28",
            "hora": "18:30",
            "precio": 15000,
            "reserva_id": "42</strong>",
            "customer_fields": [
                ("Cliente", "Ana</div>", "N/A"),
                ("Telefono", "<script>alert(1)</script>", "N/A"),
                ("Email", "ana@example.com</div>", "-"),
            ],
        }

        with patch.object(design_system.st, "html") as html_mock:
            design_system.render_public_booking_summary(data)

        html_block = html_mock.call_args.args[0]
        self.assertIn("Ana&lt;/div&gt;", html_block)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html_block)
        self.assertIn("Corte&lt;/div&gt;", html_block)
        self.assertIn("&lt;b&gt;Juan&lt;/b&gt;", html_block)
        self.assertIn("#42&lt;/strong&gt;", html_block)
        self.assertNotIn("<script>alert(1)</script>", html_block)

    def test_render_public_booking_summary_keeps_legacy_keys_compatible(self):
        data = {
            "servicio": "Corte",
            "barbero_nombre": "Juan",
            "fecha": "2026-05-28",
            "hora": "18:30",
            "precio": 15000,
            "nombre": "Ana",
            "telefono": "56911111111",
            "email": "ana@example.com",
        }

        with patch.object(design_system.st, "html") as html_mock:
            design_system.render_public_booking_summary(data)

        html_block = html_mock.call_args.args[0]
        self.assertIn("<span>Cliente</span>", html_block)
        self.assertIn("Ana", html_block)


if __name__ == "__main__":
    unittest.main()
