from unittest import TestCase, main
from unittest.mock import patch

import app_core.features.barberos.rendering as rendering


class _FakeCtx:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeStreamlit:
    def __init__(self):
        self.errors = []

    def markdown(self, *args, **kwargs):
        return None

    def form(self, *args, **kwargs):
        return _FakeCtx()

    def columns(self, spec):
        size = spec if isinstance(spec, int) else len(spec)
        return [_FakeCtx() for _ in range(size)]

    def text_input(self, *args, **kwargs):
        return ""

    def form_submit_button(self, *args, **kwargs):
        return False

    def spinner(self, *args, **kwargs):
        return _FakeCtx()

    def button(self, *args, **kwargs):
        return True

    def success(self, *args, **kwargs):
        return None

    def rerun(self, *args, **kwargs):
        return None

    def error(self, message, *args, **kwargs):
        self.errors.append(message)


class BarberosRenderingTests(TestCase):
    def test_delete_error_path_surfaces_ui_error_without_crashing(self):
        fake_st = _FakeStreamlit()
        alerts = []

        def _capture_alert(message, *args, **kwargs):
            alerts.append((message, kwargs))

        with patch.object(rendering, "st", fake_st), patch.object(
            rendering, "render_panel_header", lambda *a, **k: None
        ), patch.object(rendering, "render_alert", _capture_alert), patch.object(
            rendering, "render_divider", lambda *a, **k: None
        ), patch.object(
            rendering, "render_subsection_title", lambda *a, **k: None
        ), patch.object(
            rendering, "render_panel_empty_state", lambda *a, **k: None
        ), patch.object(
            rendering, "listar_usuarios_barberos", lambda barberia_id: [(1, "Bob")]
        ), patch.object(
            rendering, "safe_execute", side_effect=Exception("db fail")
        ):
            rendering.render_barberos_section(
                barberia_id=1,
                db_ok=True,
                meta="Test",
                no_context_message="No context",
            )

        self.assertIn(
            ("Error al eliminar el barbero.", {"alert_type": "error", "title": "Accion no completada"}),
            alerts,
        )


if __name__ == "__main__":
    main()
