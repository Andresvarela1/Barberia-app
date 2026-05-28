from unittest import TestCase, main

from app_core.features.clientes.rendering import _build_client_summary_rows


class ClientesRenderingTests(TestCase):
    def test_build_client_summary_rows_resume_historial(self):
        summary = _build_client_summary_rows(
            [
                {
                    "fecha": "2026-05-12",
                    "hora": "10:00",
                    "servicio": "Corte",
                    "barbero": "Nico",
                    "estado": "completada",
                    "pagado": True,
                },
                {
                    "fecha": "2026-05-20",
                    "hora": "09:30",
                    "servicio": "Corte",
                    "barbero": "Nico",
                    "estado": "pendiente",
                    "pagado": False,
                },
                {
                    "fecha": "2026-05-19",
                    "hora": "12:00",
                    "servicio": "Barba",
                    "barbero": "Lucho",
                    "estado": "cancelada",
                    "pagado": False,
                },
            ]
        )

        self.assertEqual(summary["favorite_barber"], "Nico")
        self.assertEqual(summary["services_used"][0], ("Corte", 2))
        self.assertEqual(summary["latest_rows"][0]["Fecha"], "2026-05-20")
        self.assertEqual(summary["latest_rows"][0]["Pago"], "Pendiente")


if __name__ == "__main__":
    main()
