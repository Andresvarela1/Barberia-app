# Observability Plan — Barberia App

> Status: baseline established (2026-04).  
> Scope: Streamlit app (`app.py` + `app_core/`) and FastAPI webhook (`webhook.py`).  
> Tools in scope: Python `logging` (stdlib), FastAPI `/health`.  
> Tools NOT yet in scope: Sentry, Prometheus, OpenTelemetry — added when scale justifies.

---

## 1. Error exposure policy

All `st.error()` and HTTP error responses shown to end-users must be generic.
Technical details (stack traces, SQL errors, internal state) must stay in `logger.exception()` or `logger.error()` only.

| Layer | What user sees | What logs contain |
|---|---|---|
| DB failure | "Error de base de datos. Por favor, intenta de nuevo." | `logger.exception(...)` with full traceback |
| Booking failure | "Error al guardar/eliminar la reserva. Por favor, intenta de nuevo." | `logger.exception(...)` |
| Payment failure | "Error al registrar el pago. Por favor, intenta de nuevo." | `logger.exception(...)` |
| Calendar rendering | "Error al mostrar el calendario. Por favor, recarga la página." | `logger.exception(...)` |
| Unhandled top-level | "Error inesperado en la aplicación. Por favor, recarga la página." | `logger.exception(...)` |
| Webhook HTTP error | FastAPI HTTPException detail (already minimal) | `logger.error(...)` |

---

## 2. Critical events to log

### 2.1 Reservations

| Event | Level | Key fields |
|---|---|---|
| Reservation created | `INFO` | `reserva_id`, `barberia_id`, `barbero_id`, `cliente`, `servicio`, `inicio` |
| Reservation updated | `INFO` | `reserva_id`, `barberia_id`, changed fields |
| Reservation deleted | `INFO` | `reserva_id`, `barberia_id`, `deleted_by_rol` |
| Reservation not found | `WARNING` | `reserva_id`, operation |
| Reservation insert failed | `ERROR` (exception) | `barberia_id`, `barbero_id`, error class |

### 2.2 Payments

| Event | Level | Key fields |
|---|---|---|
| MercadoPago preference created | `INFO` | `reserva_id`, `monto`, `init_point` (masked) |
| Payment marked as paid (Streamlit) | `INFO` | `reserva_id`, `barberia_id`, `rol` |
| MercadoPago webhook received | `INFO` | `payment_id`, `notification_type` |
| Payment approved (webhook) | `INFO` | `payment_id`, `reserva_id`, `transaction_amount` |
| Payment rejected/cancelled (webhook) | `WARNING` | `payment_id`, `reserva_id`, `status` |
| Payment details fetch failed | `ERROR` | `payment_id`, HTTP status |
| DB update failed (webhook) | `ERROR` (exception) | `reserva_id`, `payment_id` |

### 2.3 Authentication & tenant access

| Event | Level | Key fields |
|---|---|---|
| Login attempt (success) | `INFO` | `username`, `rol`, `barberia_id` |
| Login attempt (failure) | `WARNING` | `username` (no password logged) |
| Access denied (wrong barberia) | `WARNING` | `user_id`, `rol`, `barberia_id_requested` |
| Tenant context missing | `WARNING` | `user_id`, `rol`, operation |

### 2.4 Database

| Event | Level | Key fields |
|---|---|---|
| Connection obtained | `DEBUG` | — |
| Connection retry | `WARNING` | `attempt`, error class |
| All retries exhausted | `ERROR` (exception) | full traceback in log |
| Pool creation failed (webhook startup) | `ERROR` | error message |
| Health check DB ping failed | `WARNING` | — |

---

## 3. Recommended minimum metrics

These do not require Prometheus yet — they can be tracked as log counters via log aggregation (e.g., Datadog, Loki, CloudWatch Logs Insights):

| Metric | Derivation |
|---|---|
| `reservations.created` | Count `INFO` log lines for reservation creation |
| `reservations.failed` | Count `ERROR` log lines for booking insert failures |
| `payments.initiated` | Count `INFO` for MercadoPago preference creation |
| `payments.approved` | Count webhook approved events |
| `payments.failed` | Count webhook rejected/cancelled events |
| `db.retries` | Count `WARNING` lines for DB retry |
| `db.exhausted` | Count `ERROR` lines for retries exhausted |
| `webhook.received` | Count all POST /webhook calls |
| `health.db_error` | Count `/health` responses with `database: error` |

When Prometheus is added: expose via `/metrics` endpoint in `webhook.py` using `prometheus-fastapi-instrumentator`.

---

## 4. Health checks

### 4.1 Current: `GET /health` (webhook.py)

```
GET https://<webhook-host>/health
```

**Response — healthy:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-28T12:00:00.000000",
  "database": "connected"
}
```

**Response — degraded (DB unreachable):**
```json
{
  "status": "degraded",
  "timestamp": "2026-04-28T12:00:00.000000",
  "database": "error"
}
```

The endpoint performs a real `SELECT 1` probe on a pool connection. It does NOT return `200 healthy` if the DB is down — it returns `200 degraded`. HTTP status is always 200 so load balancers can read the body; use body `status` field for alerting.

### 4.2 Missing: Streamlit app health

Streamlit does not have a built-in `/health` endpoint. Options:
- Use `/_stcore/health` (Streamlit internal, returns 200 if app is serving).
- Add a lightweight FastAPI sidecar or use the Cloud Run health check URL.

Recommended next step: configure uptime monitoring (e.g., UptimeRobot, BetterUptime) to `GET /_stcore/health` every 60 seconds.

### 4.3 Missing: MercadoPago token validity check

Recommended: on startup, `GET /health` could optionally call `GET https://api.mercadopago.com/v1/payment_methods` with the configured token to verify it's valid. Return `token: valid|invalid|unconfigured` in the health response body. This is a future improvement (requires 1 HTTP call on startup).

---

## 5. Future integrations (when needed)

| Tool | Trigger to add |
|---|---|
| **Sentry** | First production incident with missing context |
| **Prometheus + Grafana** | When multiple webhook replicas are running |
| **OpenTelemetry** | When tracing across Streamlit + webhook + DB is needed |
| **Structured logging (JSON)** | When logs are shipped to a log aggregation service |

To add structured logging: replace `logging.basicConfig(format=...)` with a `python-json-logger` handler. All `logger.info(msg, extra={...})` calls already use the right pattern.
