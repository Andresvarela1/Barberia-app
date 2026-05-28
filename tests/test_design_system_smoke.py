import sys
from pathlib import Path
from unittest import TestCase, main


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import design_system


class DesignSystemSmokeTests(TestCase):
    def test_premium_helpers_are_importable(self):
        expected = [
            "render_metric_card",
            "render_metric_grid",
            "render_section_block",
            "render_sidebar_section",
            "render_cta_section",
            "render_appointment_block",
            "render_panel_header",
        ]

        for name in expected:
            self.assertTrue(hasattr(design_system, name), name)

    def test_app_uses_premium_helpers(self):
        source = (REPO_ROOT / "app.py").read_text(encoding="utf-8-sig")
        expected_snippets = [
            "render_metric_card",
            "render_section_block",
            "render_cta_section",
            "render_appointment_block",
            "render_sidebar_section",
        ]

        for snippet in expected_snippets:
            self.assertIn(snippet, source)


if __name__ == "__main__":
    main()
