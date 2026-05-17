from unittest import TestCase, main
from unittest.mock import patch

from app_core import auth


class FakeStreamlit:
    def __init__(self):
        self.session_state = {}


class AuthSessionHelperTests(TestCase):
    def setUp(self):
        self.fake_streamlit = FakeStreamlit()
        self.streamlit_patcher = patch.object(auth, "st", self.fake_streamlit)
        self.streamlit_patcher.start()
        self.addCleanup(self.streamlit_patcher.stop)

    def test_login_and_prepare_session_success_sets_target_view(self):
        fake_user = (5, "admin", "hash", "ADMIN", None, 9, 0)

        with patch.object(auth, "login", return_value=fake_user), patch.object(
            auth,
            "apply_login_session_context",
            side_effect=lambda user, default_id: self.fake_streamlit.session_state.update(
                {
                    "user": user,
                    "user_id": user[0],
                    "rol": "ADMIN",
                    "user_role": "ADMIN",
                    "barberia_id": 9,
                    "barberia_context_id": 9,
                }
            ),
        ) as apply_mock:
            result = auth.login_and_prepare_session("admin", "secret", 9)

        self.assertEqual(result["user"], fake_user)
        self.assertEqual(result["target_view"], "dashboard")
        self.assertEqual(result["role"], "ADMIN")
        self.assertEqual(self.fake_streamlit.session_state["view"], "dashboard")
        apply_mock.assert_called_once_with(fake_user, 9)

    def test_login_and_prepare_session_failure_keeps_state_stable(self):
        self.fake_streamlit.session_state["view"] = "login"

        with patch.object(auth, "login", return_value=None):
            result = auth.login_and_prepare_session("admin", "bad", 9)

        self.assertIsNone(result)
        self.assertEqual(self.fake_streamlit.session_state["view"], "login")

    def test_logout_and_reset_session_restores_defaults(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (1, "super", "x", "SUPER_ADMIN"),
                "user_id": 1,
                "rol": "SUPER_ADMIN",
                "user_role": "SUPER_ADMIN",
                "barberia_id": None,
                "barberia_context_id": 33,
                "super_admin_all_barberias": True,
                "public_mode": True,
                "view": "dashboard_admin",
                "reserva_seleccionada_id": 99,
                "mostrar_detalles_reserva": True,
                "barberia_name": "Centro",
                "cached_barberia_id": 33,
                "barberias_list": [(33, "Centro")],
                "nav_dashboard_admin": "Agenda",
                "db_available": True,
            }
        )

        result = auth.logout_and_reset_session(7)

        self.assertTrue(result)
        self.assertIsNone(self.fake_streamlit.session_state["user"])
        self.assertIsNone(self.fake_streamlit.session_state["user_id"])
        self.assertEqual(self.fake_streamlit.session_state["rol"], "CLIENTE")
        self.assertEqual(self.fake_streamlit.session_state["user_role"], "CLIENTE")
        self.assertEqual(self.fake_streamlit.session_state["barberia_id"], 7)
        self.assertEqual(self.fake_streamlit.session_state["barberia_context_id"], 7)
        self.assertFalse(self.fake_streamlit.session_state["super_admin_all_barberias"])
        self.assertFalse(self.fake_streamlit.session_state["public_mode"])
        self.assertEqual(self.fake_streamlit.session_state["view"], "home")
        self.assertIsNone(self.fake_streamlit.session_state["reserva_seleccionada_id"])
        self.assertFalse(self.fake_streamlit.session_state["mostrar_detalles_reserva"])
        self.assertNotIn("barberia_name", self.fake_streamlit.session_state)
        self.assertNotIn("cached_barberia_id", self.fake_streamlit.session_state)
        self.assertNotIn("barberias_list", self.fake_streamlit.session_state)
        self.assertNotIn("nav_dashboard_admin", self.fake_streamlit.session_state)
        self.assertTrue(self.fake_streamlit.session_state["db_available"])

    def test_normalize_authenticated_session_state_repairs_partial_session(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (4, "barber", "hash", "BARBERO", None, 12, 0),
                "rol": "BARBERO",
                "view": "login",
                "public_mode": True,
                "super_admin_all_barberias": True,
            }
        )

        result = auth.normalize_authenticated_session_state(7)

        self.assertEqual(result["target_view"], "dashboard_barbero")
        self.assertEqual(self.fake_streamlit.session_state["view"], "dashboard_barbero")
        self.assertEqual(self.fake_streamlit.session_state["user_role"], "BARBERO")
        self.assertEqual(self.fake_streamlit.session_state["barberia_id"], 12)
        self.assertEqual(self.fake_streamlit.session_state["barberia_context_id"], 12)
        self.assertFalse(self.fake_streamlit.session_state["public_mode"])
        self.assertFalse(self.fake_streamlit.session_state["super_admin_all_barberias"])

    def test_resolve_authenticated_entry_redirects_public_view_to_role_dashboard(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (10, "client", "hash", "CLIENTE", None, 21, 0),
                "rol": "CLIENTE",
                "user_role": "CLIENTE",
                "view": "home",
                "barberia_id": 21,
                "barberia_context_id": 21,
            }
        )

        result = auth.resolve_authenticated_entry(7)

        self.assertEqual(result["target_view"], "dashboard")
        self.assertEqual(result["view"], "dashboard")
        self.assertTrue(result["should_rerun"])
        self.assertEqual(self.fake_streamlit.session_state["view"], "dashboard")

    def test_resolve_authenticated_entry_repairs_invalid_view(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (11, "barber", "hash", "BARBERO", None, 30, 0),
                "rol": "BARBERO",
                "user_role": "BARBERO",
                "view": "vista_rara",
            }
        )

        result = auth.resolve_authenticated_entry(7)

        self.assertEqual(result["target_view"], "dashboard_barbero")
        self.assertEqual(result["view"], "dashboard_barbero")
        self.assertTrue(result["should_rerun"])
        self.assertEqual(self.fake_streamlit.session_state["barberia_id"], 30)
        self.assertEqual(self.fake_streamlit.session_state["barberia_context_id"], 30)

    def test_resolve_authenticated_entry_preserves_super_admin_dashboard_context(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (1, "super", "hash", "SUPER_ADMIN", None, None, 0),
                "rol": "SUPER_ADMIN",
                "user_role": "SUPER_ADMIN",
                "view": "dashboard_admin",
                "barberia_context_id": 44,
                "super_admin_all_barberias": True,
            }
        )

        result = auth.resolve_authenticated_entry(7)

        self.assertEqual(result["target_view"], "dashboard_admin")
        self.assertEqual(result["view"], "dashboard_admin")
        self.assertFalse(result["should_rerun"])
        self.assertEqual(self.fake_streamlit.session_state["barberia_context_id"], 44)
        self.assertTrue(self.fake_streamlit.session_state["super_admin_all_barberias"])

    def test_resolve_view_access_redirects_unauthenticated_dashboard_to_home(self):
        self.fake_streamlit.session_state["view"] = "dashboard"

        result = auth.resolve_view_access(7)

        self.assertFalse(result["is_allowed"])
        self.assertEqual(result["resolved_view"], "home")
        self.assertTrue(result["should_rerun"])
        self.assertFalse(result["should_stop"])
        self.assertEqual(self.fake_streamlit.session_state["view"], "home")

    def test_resolve_view_access_stops_unauthenticated_public_view(self):
        self.fake_streamlit.session_state["view"] = "login"

        result = auth.resolve_view_access(7)

        self.assertTrue(result["is_allowed"])
        self.assertEqual(result["resolved_view"], "login")
        self.assertFalse(result["should_rerun"])
        self.assertTrue(result["should_stop"])

    def test_resolve_view_access_redirects_authenticated_public_view(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (6, "admin", "hash", "ADMIN", None, 19, 0),
                "rol": "ADMIN",
                "user_role": "ADMIN",
                "view": "login",
                "barberia_id": 19,
                "barberia_context_id": 19,
            }
        )

        result = auth.resolve_view_access(7)

        self.assertTrue(result["is_allowed"])
        self.assertEqual(result["resolved_view"], "dashboard")
        self.assertTrue(result["should_rerun"])
        self.assertFalse(result["should_stop"])

    def test_resolve_view_access_normalizes_partial_authenticated_session(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (12, "barber", "hash", "BARBERO", None, 41, 0),
                "rol": "BARBERO",
                "view": "",
            }
        )

        result = auth.resolve_view_access(7)

        self.assertTrue(result["is_allowed"])
        self.assertEqual(result["resolved_view"], "dashboard_barbero")
        self.assertTrue(result["should_rerun"])
        self.assertEqual(self.fake_streamlit.session_state["barberia_id"], 41)
        self.assertEqual(self.fake_streamlit.session_state["barberia_context_id"], 41)

    def test_resolve_view_access_preserves_super_admin_dashboard(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (1, "super", "hash", "SUPER_ADMIN", None, None, 0),
                "rol": "SUPER_ADMIN",
                "user_role": "SUPER_ADMIN",
                "view": "dashboard_admin",
                "barberia_context_id": 44,
                "super_admin_all_barberias": True,
            }
        )

        result = auth.resolve_view_access(7)

        self.assertTrue(result["is_allowed"])
        self.assertEqual(result["resolved_view"], "dashboard_admin")
        self.assertFalse(result["should_rerun"])
        self.assertFalse(result["should_stop"])
        self.assertEqual(self.fake_streamlit.session_state["barberia_context_id"], 44)
        self.assertTrue(self.fake_streamlit.session_state["super_admin_all_barberias"])

    def test_resolve_render_view_redirects_unauthenticated_dashboard(self):
        self.fake_streamlit.session_state["view"] = "dashboard"

        result = auth.resolve_render_view(7)

        self.assertEqual(result["resolved_view"], "home")
        self.assertTrue(result["should_rerun"])
        self.assertFalse(result["should_stop"])
        self.assertFalse(result["is_authenticated"])

    def test_resolve_render_view_keeps_public_login_for_guest(self):
        self.fake_streamlit.session_state["view"] = "login"

        result = auth.resolve_render_view(7)

        self.assertEqual(result["resolved_view"], "login")
        self.assertFalse(result["should_rerun"])
        self.assertTrue(result["should_stop"])
        self.assertFalse(result["is_authenticated"])

    def test_resolve_render_view_repairs_authenticated_public_residue(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (14, "admin", "hash", "ADMIN", None, 55, 0),
                "rol": "ADMIN",
                "user_role": "ADMIN",
                "view": "home",
                "barberia_id": 55,
                "barberia_context_id": 55,
            }
        )

        result = auth.resolve_render_view(7)

        self.assertEqual(result["resolved_view"], "dashboard")
        self.assertTrue(result["should_rerun"])
        self.assertFalse(result["should_stop"])
        self.assertTrue(result["is_authenticated"])

    def test_resolve_render_view_handles_partial_barbero_session(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (15, "barber", "hash", "BARBERO", None, 77, 0),
                "rol": "BARBERO",
                "view": "",
            }
        )

        result = auth.resolve_render_view(7)

        self.assertEqual(result["resolved_view"], "dashboard_barbero")
        self.assertTrue(result["should_rerun"])
        self.assertFalse(result["should_stop"])
        self.assertTrue(result["is_authenticated"])
        self.assertEqual(self.fake_streamlit.session_state["barberia_id"], 77)
        self.assertEqual(self.fake_streamlit.session_state["barberia_context_id"], 77)

    def test_resolve_render_view_preserves_super_admin_dashboard(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (1, "super", "hash", "SUPER_ADMIN", None, None, 0),
                "rol": "SUPER_ADMIN",
                "user_role": "SUPER_ADMIN",
                "view": "dashboard_admin",
                "barberia_context_id": 44,
                "super_admin_all_barberias": True,
            }
        )

        result = auth.resolve_render_view(7)

        self.assertEqual(result["resolved_view"], "dashboard_admin")
        self.assertFalse(result["should_rerun"])
        self.assertFalse(result["should_stop"])
        self.assertTrue(result["is_authenticated"])

    def test_resolve_screen_dispatch_maps_public_home(self):
        self.fake_streamlit.session_state["view"] = "home"

        result = auth.resolve_screen_dispatch(7)

        self.assertEqual(result["screen_key"], "home")
        self.assertEqual(result["screen_group"], "public")
        self.assertEqual(result["resolved_view"], "home")
        self.assertFalse(result["should_rerun"])
        self.assertTrue(result["should_stop"])

    def test_resolve_screen_dispatch_maps_public_login(self):
        self.fake_streamlit.session_state["view"] = "login"

        result = auth.resolve_screen_dispatch(7)

        self.assertEqual(result["screen_key"], "login")
        self.assertEqual(result["screen_group"], "public")
        self.assertEqual(result["resolved_view"], "login")
        self.assertFalse(result["should_rerun"])
        self.assertTrue(result["should_stop"])

    def test_resolve_screen_dispatch_maps_authenticated_dashboard(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (22, "admin", "hash", "ADMIN", None, 81, 0),
                "rol": "ADMIN",
                "user_role": "ADMIN",
                "view": "dashboard",
                "barberia_id": 81,
                "barberia_context_id": 81,
            }
        )

        result = auth.resolve_screen_dispatch(7)

        self.assertEqual(result["screen_key"], "dashboard")
        self.assertEqual(result["screen_group"], "authenticated")
        self.assertEqual(result["resolved_view"], "dashboard")
        self.assertFalse(result["should_rerun"])
        self.assertFalse(result["should_stop"])

    def test_resolve_screen_dispatch_maps_super_admin_dashboard(self):
        self.fake_streamlit.session_state.update(
            {
                "user": (1, "super", "hash", "SUPER_ADMIN", None, None, 0),
                "rol": "SUPER_ADMIN",
                "user_role": "SUPER_ADMIN",
                "view": "dashboard_admin",
                "barberia_context_id": 44,
                "super_admin_all_barberias": True,
            }
        )

        result = auth.resolve_screen_dispatch(7)

        self.assertEqual(result["screen_key"], "dashboard_admin")
        self.assertEqual(result["screen_group"], "authenticated")
        self.assertEqual(result["resolved_view"], "dashboard_admin")
        self.assertFalse(result["should_rerun"])
        self.assertFalse(result["should_stop"])

    def test_resolve_screen_dispatch_handles_unknown_view_safely(self):
        self.fake_streamlit.session_state["view"] = "vista_desconocida"

        result = auth.resolve_screen_dispatch(7)

        self.assertEqual(result["screen_key"], "home")
        self.assertEqual(result["screen_group"], "public")
        self.assertEqual(result["resolved_view"], "home")
        self.assertTrue(result["should_rerun"])
        self.assertFalse(result["should_stop"])

    def test_login_and_prepare_session_cleans_public_view_residue_on_relogin(self):
        fake_user = (8, "admin", "hash", "ADMIN", None, 15, 0)
        self.fake_streamlit.session_state.update(
            {
                "view": "reserva",
                "public_mode": True,
                "super_admin_all_barberias": True,
            }
        )

        with patch.object(auth, "login", return_value=fake_user), patch.object(
            auth,
            "apply_login_session_context",
            side_effect=lambda user, default_id: self.fake_streamlit.session_state.update(
                {
                    "user": user,
                    "user_id": user[0],
                    "rol": "ADMIN",
                    "user_role": "ADMIN",
                    "barberia_id": 15,
                    "barberia_context_id": 15,
                }
            ),
        ):
            result = auth.login_and_prepare_session("admin", "secret", 7)

        self.assertEqual(result["target_view"], "dashboard")
        self.assertEqual(self.fake_streamlit.session_state["view"], "dashboard")
        self.assertFalse(self.fake_streamlit.session_state["public_mode"])
        self.assertFalse(self.fake_streamlit.session_state["super_admin_all_barberias"])


if __name__ == "__main__":
    main()
