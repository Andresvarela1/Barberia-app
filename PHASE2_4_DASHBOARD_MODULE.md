# Phase 2.4 - Dashboard Module

## Resumen de la extracción

Se continuó la etapa 2 con una extracción real por feature limitada al dashboard `ADMIN`:

- `app_core/features/dashboard/rendering.py`

## Qué se movió

Se extrajo desde `app.py` la implementación concreta del dashboard `ADMIN`:

- encabezado del dashboard
- métricas principales
- resumen general
- carga de próximas citas
- render del bloque de próximas citas mediante callback explícito

El módulo nuevo expone una sola entrada principal:

- `render_admin_dashboard_section(...)`

## Cómo quedó la integración

`app.py` ya no contiene la implementación concreta del dashboard `ADMIN`.

Ahora sólo resuelve el contexto activo y delega:

- `barberia_id`
- `db_ok`
- `barberia_name`
- callback `render_upcoming_appointments_summary`

Se dejó a `SUPER_ADMIN` fuera de esta extracción para mantener el riesgo controlado.

## Qué no cambió

- No se modificó la UI ni el comportamiento visible.
- No se tocó auth/session, `resolve_*`, agenda, servicios, barberos, pagos ni tenancy.
- No se abrió una modularización masiva del resto de dashboards.

## Patrón que valida para etapa 2

Esta fase confirma que también es viable modularizar una feature con algo más de acoplamiento visual y de métricas, siempre que el corte se mantenga acotado:

1. `app.py` conserva sólo el wiring contextual;
2. la feature vive en un módulo propio;
3. los bloques compartidos o más sensibles se pasan como callbacks explícitos en vez de forzar una generalización temprana.

## Riesgos pendientes

- `SUPER_ADMIN dashboard` sigue en `app.py`, lo cual fue intencional para no mezclar una variante más acoplada en esta misma fase.
- Si la etapa 2 sigue, el siguiente paso natural sería decidir entre:
  - extraer `SUPER_ADMIN dashboard` como fase separada;
  - o consolidar sólo subbloques claramente compartidos de dashboards si el costo/riesgo sigue siendo bajo.
