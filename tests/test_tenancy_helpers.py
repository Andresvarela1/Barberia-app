from unittest import TestCase, main
from unittest.mock import patch

from app_core import tenancy


class FakeStreamlit:
    def __init__(self):
        self.session_state = {}


class TenancyHelpersTests(TestCase):
    def setUp(self):
        self.fake_streamlit = FakeStreamlit()
        self.streamlit_patcher = patch.object(tenancy, "st", self.fake_streamlit)
        self.streamlit_patcher.start()
        self.addCleanup(self.streamlit_patcher.stop)

    def test_ensure_session_defaults_initializes_minimum_context(self):
        result = tenancy.ensure_session_defaults(9, db_available=True)

        self.assertTrue(result)
        self.assertEqual(self.fake_streamlit.session_state["rol"], "CLIENTE")
        self.assertEqual(self.fake_streamlit.session_state["barberia_id"], 9)
        self.assertEqual(self.fake_streamlit.session_state["barberia_context_id"], 9)
        self.assertFalse(self.fake_streamlit.session_state["super_admin_all_barberias"])
        self.assertTrue(self.fake_streamlit.session_state["db_available"])

    def test_apply_login_session_context_for_super_admin(self):
        with patch.object(tenancy, "safe_fetch_one", return_value=(33,)):
            role, target_view = tenancy.apply_login_session_context(
                (7, "sa", "x", "SUPER_ADMIN", None, None),
                1,
            )

        self.assertEqual(role, "SUPER_ADMIN")
        self.assertEqual(target_view, "dashboard_admin")
        self.assertIsNone(self.fake_streamlit.session_state["barberia_id"])
        self.assertEqual(self.fake_streamlit.session_state["barberia_context_id"], 33)
        self.assertFalse(self.fake_streamlit.session_state["super_admin_all_barberias"])

    def test_apply_login_session_context_for_barbero(self):
        role, target_view = tenancy.apply_login_session_context(
            (9, "barber", "x", "BARBERO", None, 4),
            1,
        )

        self.assertEqual(role, "BARBERO")
        self.assertEqual(target_view, "dashboard_barbero")
        self.assertEqual(self.fake_streamlit.session_state["barberia_id"], 4)
        self.assertEqual(self.fake_streamlit.session_state["barberia_context_id"], 4)

    def test_get_cached_barberia_name_uses_session_cache(self):
        with patch.object(tenancy, "safe_fetch_one", return_value=("Downtown",)) as fetch_mock:
            first = tenancy.get_cached_barberia_name(5)
            second = tenancy.get_cached_barberia_name(5)

        self.assertEqual(first, "Downtown")
        self.assertEqual(second, "Downtown")
        fetch_mock.assert_called_once_with("SELECT nombre FROM barberias WHERE id = %s", (5,))

    def test_load_super_admin_context_options_returns_selected_index(self):
        self.fake_streamlit.session_state["barberia_context_id"] = 20

        with patch.object(
            tenancy,
            "safe_fetch_all",
            return_value=[(10, "Centro"), (20, "Norte")],
        ):
            rows, labels, keys, selected_index = tenancy.load_super_admin_context_options()

        self.assertEqual(rows, [(10, "Centro"), (20, "Norte")])
        self.assertEqual(labels, {"Centro": 10, "Norte": 20})
        self.assertEqual(keys, ["Centro", "Norte"])
        self.assertEqual(selected_index, 1)


if __name__ == "__main__":
    main()
