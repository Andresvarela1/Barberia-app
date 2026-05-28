from unittest import TestCase, main
from unittest.mock import patch

from app_core import metrics


class MetricsTests(TestCase):
    def test_calcular_metricas_operativas_admin_usa_contexto_actual(self):
        fake_st = type("FakeSt", (), {"session_state": {"db_available": True}})()

        with patch.object(metrics, "st", fake_st), patch.object(
            metrics,
            "get_current_barberia_id",
            return_value=7,
        ), patch.object(
            metrics,
            "safe_fetch_one",
            return_value=(12, 8, 2, 1, 6),
        ) as fetch_mock:
            result = metrics.calcular_metricas_operativas_admin(99)

        self.assertEqual(result, (12, 8, 2, 1, 6))
        fetch_mock.assert_called_once_with(
            metrics._build_operational_metrics_query(scope_all_barberias=False),
            (7,),
        )

    def test_calcular_metricas_operativas_super_admin_global(self):
        fake_st = type(
            "FakeSt",
            (),
            {"session_state": {"db_available": True, "super_admin_all_barberias": True}},
        )()

        with patch.object(metrics, "st", fake_st), patch.object(
            metrics,
            "safe_fetch_one",
            return_value=(40, 20, 5, 3, 18),
        ) as fetch_mock:
            result = metrics.calcular_metricas_operativas_super_admin()

        self.assertEqual(result, (40, 20, 5, 3, 18, "Global"))
        fetch_mock.assert_called_once_with(
            metrics._build_operational_metrics_query(scope_all_barberias=True)
        )


if __name__ == "__main__":
    main()
