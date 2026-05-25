from unittest import TestCase, main

from streamlit.testing.v1 import AppTest


class AppAuthenticatedContextTests(TestCase):
    def test_authenticated_user_keeps_barberia_id_when_not_on_public_slug(self):
        at = AppTest.from_file("app.py")
        at.session_state["app_initialized"] = True
        at.session_state["default_barberia_id"] = 3
        at.session_state["user"] = (7, "admin_barberia-austral", "x", "ADMIN", None, 4, 0)
        at.session_state["user_id"] = 7
        at.session_state["rol"] = "ADMIN"
        at.session_state["user_role"] = "ADMIN"
        at.session_state["view"] = "dashboard"
        at.session_state["barberia_id"] = 4
        at.session_state["barberia_context_id"] = 4
        at.session_state["public_mode"] = True

        at.run(timeout=30)

        self.assertEqual(at.session_state["barberia_id"], 4)
        self.assertFalse(at.session_state["public_mode"])


if __name__ == "__main__":
    main()
