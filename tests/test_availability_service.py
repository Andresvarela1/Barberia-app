from unittest import TestCase, main
from unittest.mock import patch

from app_core.services import availability_service


class AvailabilityServiceTests(TestCase):
    def test_listar_usuarios_barberos_uses_safe_fetch_all(self):
        with patch.object(
            availability_service,
            "get_current_barberia_id",
            return_value=4,
        ), patch.object(
            availability_service,
            "enforce_barberia_access",
            return_value=None,
        ), patch.object(
            availability_service,
            "safe_fetch_all",
            return_value=[(10, "Bob"), (11, "Ana")],
        ) as fetch_mock:
            result = availability_service.listar_usuarios_barberos()

        self.assertEqual(result, [(10, "Bob"), (11, "Ana")])
        fetch_mock.assert_called_once()


if __name__ == "__main__":
    main()
