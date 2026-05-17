from pathlib import Path
from unittest import TestCase, main


ROOT = Path(__file__).resolve().parents[1]


class ReservasContractAlignmentTests(TestCase):
    def read_text(self, relative_path):
        return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")

    def test_schema_sql_declares_canonical_reservas_columns(self):
        schema = self.read_text("schema.sql")

        expected_fragments = (
            "barbero_id INTEGER",
            "cliente TEXT",
            "telefono TEXT",
            "email TEXT",
            "fecha DATE",
            "hora TIME",
            "estado TEXT NOT NULL DEFAULT 'activo'",
            "pagado BOOLEAN NOT NULL DEFAULT FALSE",
            "monto INTEGER",
            "payment_id TEXT",
            "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
        )

        for fragment in expected_fragments:
            self.assertIn(fragment, schema)

    def test_bootstrap_keeps_reservas_contract_in_sync(self):
        bootstrap = self.read_text("app_core/bootstrap.py")

        expected_fragments = (
            "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS telefono TEXT;",
            "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS email TEXT;",
            "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS payment_id TEXT;",
            "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;",
            "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS barbero_id INTEGER;",
            "UPDATE reservas SET cliente = COALESCE(cliente, nombre) WHERE cliente IS NULL;",
            "UPDATE reservas SET fecha = DATE(inicio) WHERE fecha IS NULL AND inicio IS NOT NULL;",
            "UPDATE reservas SET hora = CAST(inicio AS TIME) WHERE hora IS NULL AND inicio IS NOT NULL;",
        )

        for fragment in expected_fragments:
            self.assertIn(fragment, bootstrap)

    def test_modal_insert_uses_canonical_reservas_contract(self):
        app_text = self.read_text("app.py")

        self.assertIn("barbero_placeholder = \"Sin asignar\"", app_text)
        self.assertIn(
            "nombre, barbero, barbero_id, servicio, precio, inicio, fin, barberia_id,",
            app_text,
        )
        self.assertIn(
            "cliente, telefono, email, fecha, hora, estado, monto, pagado",
            app_text,
        )
        self.assertNotIn(
            "(barberia_id, cliente, telefono, email, servicio, fecha, hora, estado, pagado)",
            app_text,
        )

    def test_payment_and_webhook_use_supported_payment_columns(self):
        payment_service = self.read_text("app_core/services/payment_service.py")
        webhook = self.read_text("webhook.py")

        self.assertIn("updated_at = CURRENT_TIMESTAMP", payment_service)
        self.assertIn("payment_id = %s", webhook)
        self.assertIn("updated_at = %s", webhook)
        self.assertIn("RETURNING id, cliente, servicio, fecha", webhook)


if __name__ == "__main__":
    main()
