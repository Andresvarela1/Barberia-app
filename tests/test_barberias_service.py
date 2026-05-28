import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app_core.services import barberias_service


class BarberiasServiceTests(unittest.TestCase):
    def test_module_exports_expected_helpers(self):
        expected = [
            "get_default_barberia_id",
            "check_barberia_name_exists",
            "create_barberia_in_db",
            "create_admin_user_in_db",
            "create_services_in_db",
            "create_barbers_in_db",
            "obtener_todas_barberias",
        ]

        for name in expected:
            self.assertTrue(hasattr(barberias_service, name), name)

    def test_get_default_barberia_id_uses_safe_fetch_one(self):
        with patch.object(barberias_service, "safe_fetch_one", return_value=(7,)) as fetch_mock:
            result = barberias_service.get_default_barberia_id()

        self.assertEqual(result, 7)
        fetch_mock.assert_called_once_with("SELECT id FROM barberias ORDER BY id LIMIT 1")

    def test_obtener_todas_barberias_maps_rows(self):
        rows = [
            (
                3,
                "Studio",
                "studio",
                "123",
                "mail@example.com",
                "Bogota",
                "Calle 1",
                "4.1",
                "-74.1",
                "#111111",
                "logo.png",
                "09:00",
                "18:00",
                "active",
            )
        ]

        with patch.object(barberias_service, "safe_fetch_all", return_value=rows) as fetch_mock:
            result = barberias_service.obtener_todas_barberias(ciudad="Bog")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 3)
        self.assertEqual(result[0]["slug"], "studio")
        self.assertEqual(result[0]["latitud"], 4.1)
        self.assertEqual(result[0]["longitud"], -74.1)
        query, params = fetch_mock.call_args.args
        self.assertIn("FROM barberias WHERE estado = %s", query)
        self.assertIn("LOWER(ciudad) LIKE LOWER(%s)", query)
        self.assertEqual(params, ("active", "%Bog%"))

    def test_app_py_imports_barberias_service_and_no_duplicate_defs(self):
        source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")

        self.assertIn("from app_core.services.barberias_service import", source)

        duplicated = [
            "def get_default_barberia_id",
            "def check_barberia_name_exists",
            "def create_barberia_in_db",
            "def create_admin_user_in_db",
            "def create_services_in_db",
            "def create_barbers_in_db",
            "def obtener_todas_barberias",
        ]
        for fn in duplicated:
            self.assertNotIn(fn, source)


if __name__ == "__main__":
    unittest.main()
