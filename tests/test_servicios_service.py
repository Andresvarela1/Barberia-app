import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app_core.services import servicios_service


class ServiciosServiceTests(unittest.TestCase):
    def test_obtener_barberia_por_slug_maps_public_fields(self):
        row = (
            7,
            "Barberia Austral",
            "barberia-austral",
            "+56911111111",
            "hola@austral.test",
            "Punta Arenas",
            "Av. Costanera 100",
            "-53.1638",
            "-70.9171",
            "#111111",
            "logo.png",
            "09:00",
            "20:00",
            "activa",
        )

        with patch.object(servicios_service, "fetch_one", return_value=row) as fetch_mock:
            result = servicios_service.obtener_barberia_por_slug("barberia-austral")

        self.assertEqual(result["id"], 7)
        self.assertEqual(result["nombre"], "Barberia Austral")
        self.assertEqual(result["slug"], "barberia-austral")
        self.assertEqual(result["estado"], "activa")
        fetch_mock.assert_called_once()

    def test_barberia_es_publicable_accepts_active_states(self):
        self.assertTrue(servicios_service.barberia_es_publicable({"estado": "activa"}))
        self.assertTrue(servicios_service.barberia_es_publicable({"estado": "active"}))
        self.assertTrue(servicios_service.barberia_es_publicable({"estado": ""}))

    def test_barberia_es_publicable_rejects_missing_or_inactive_barberias(self):
        self.assertFalse(servicios_service.barberia_es_publicable(None))
        self.assertFalse(servicios_service.barberia_es_publicable({"estado": "inactiva"}))
        self.assertFalse(servicios_service.barberia_es_publicable({"estado": "draft"}))


if __name__ == "__main__":
    unittest.main()
