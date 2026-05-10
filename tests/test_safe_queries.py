import unittest
from unittest.mock import patch

from app_core.db import safe_queries


class FakeStreamlit:
    def __init__(self):
        self.session_state = {}

    def error(self, *_args, **_kwargs):
        return None


class SafeQueriesTests(unittest.TestCase):
    def setUp(self):
        self.fake_streamlit = FakeStreamlit()
        self.streamlit_patcher = patch.object(safe_queries, "st", self.fake_streamlit)
        self.streamlit_patcher.start()
        self.addCleanup(self.streamlit_patcher.stop)

    def test_safe_fetch_one_allows_system_query_case_insensitive(self):
        with patch.object(safe_queries, "fetch_one", return_value=(1,)):
            result = safe_queries.safe_fetch_one(
                "SELECT ID FROM BARBERIAS ORDER BY ID LIMIT 1"
            )

        self.assertEqual(result, (1,))

    def test_safe_fetch_all_blocks_sensitive_read_without_barberia_id(self):
        with patch.object(safe_queries, "fetch_all", return_value=[]):
            with self.assertRaisesRegex(Exception, "missing barberia_id WHERE filter"):
                safe_queries.safe_fetch_all(
                    "SELECT id, nombre FROM reservas WHERE estado = %s",
                    ("x",),
                )

    def test_safe_fetch_all_requires_barberia_id_in_where_clause(self):
        with patch.object(safe_queries, "fetch_all", return_value=[]):
            with self.assertRaisesRegex(Exception, "missing barberia_id WHERE filter"):
                safe_queries.safe_fetch_all("SELECT id, barberia_id FROM reservas")

    def test_barberias_system_read_does_not_allow_tenant_join(self):
        with patch.object(safe_queries, "fetch_all", return_value=[]):
            with self.assertRaisesRegex(Exception, "missing barberia_id WHERE filter"):
                safe_queries.safe_fetch_all(
                    "SELECT b.id, r.id FROM barberias b JOIN reservas r ON r.barberia_id = b.id"
                )

    def test_safe_execute_allows_tenant_scoped_update(self):
        with patch.object(safe_queries, "execute_write", return_value=True) as execute_mock:
            ok = safe_queries.safe_execute(
                "UPDATE usuarios SET cortes_acumulados = 0 WHERE usuario = %s AND barberia_id = %s",
                ("cliente", 7),
            )

        self.assertTrue(ok)
        execute_mock.assert_called_once()

    def test_safe_execute_blocks_write_without_barberia_id(self):
        with patch.object(safe_queries, "execute_write", return_value=True):
            with self.assertRaisesRegex(Exception, "write missing barberia_id WHERE filter"):
                safe_queries.safe_execute(
                    "UPDATE usuarios SET rol = %s WHERE id = %s",
                    ("ADMIN", 1),
                )

    def test_safe_execute_allows_explicit_system_exception(self):
        with patch.object(safe_queries, "execute_write", return_value=True):
            ok = safe_queries.safe_execute(
                "UPDATE usuarios SET password = %s WHERE id = %s",
                ("hashed", 1),
                allow_system=True,
                system_reason="login legacy password rehash before tenant context",
            )

        self.assertTrue(ok)

    def test_safe_execute_blocks_barberia_insert_without_explicit_system_exception(self):
        with patch.object(safe_queries, "execute_write", return_value=True):
            with self.assertRaisesRegex(Exception, "insert missing barberia_id column"):
                safe_queries.safe_execute(
                    "INSERT INTO barberias (nombre, slug) VALUES (%s, %s)",
                    ("Demo", "demo"),
                )

    def test_safe_fetch_all_allows_super_admin_global_query(self):
        self.fake_streamlit.session_state["rol"] = "SUPER_ADMIN"
        self.fake_streamlit.session_state["super_admin_all_barberias"] = True

        with patch.object(safe_queries, "fetch_all", return_value=[(1,)]):
            result = safe_queries.safe_fetch_all("SELECT id FROM reservas WHERE 1=1")

        self.assertEqual(result, [(1,)])


if __name__ == "__main__":
    unittest.main()
