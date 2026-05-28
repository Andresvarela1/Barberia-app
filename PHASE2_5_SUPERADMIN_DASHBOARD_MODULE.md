# Phase 2.5 - Super Admin Dashboard Module

## Resumen de la extracción

Se cerró la etapa 2 extendiendo el módulo de dashboard para cubrir también el dashboard `SUPER_ADMIN`:

- `app_core/features/dashboard/rendering.py`

## Qué se movió

Se extrajo desde `app.py` la implementación concreta del dashboard `SUPER_ADMIN`:

- encabezado global
- métricas globales
- resumen visual de plataforma

El módulo ahora expone dos entradas explícitas:

- `render_admin_dashboard_section(...)`
- `render_super_admin_dashboard_section(...)`

## Cómo quedó la integración

`app.py` ya no contiene la implementación concreta de ninguno de los dashboards administrativos principales.

Ahora sólo resuelve el contexto y delega:

- `ADMIN`: `barberia_id`, `db_ok`, `barberia_name`, callback de próximas citas
- `SUPER_ADMIN`: `bid_ctx`, `db_ok`

## Qué no cambió

- No se modificó la UI ni el comportamiento visible.
- No se tocaron agenda, servicios, barberos, auth/session, `resolve_*`, pagos ni tenancy.
- No se abrió una modularización masiva de otros dashboards o métricas fuera de este alcance.

## Qué valida para el cierre de etapa 2

Con esta fase, el mapa administrativo principal ya quedó bastante cubierto bajo el patrón de feature modules:

- `Agenda` (listado)
- `Servicios`
- `Barberos`
- `Dashboard ADMIN`
- `Dashboard SUPER_ADMIN`

## Riesgos pendientes

- Quedan todavía otros bloques internos en `app.py`, pero ya no en el núcleo administrativo más obvio de esta etapa.
- Si más adelante existiera una etapa 3, ya sería una decisión de producto/arquitectura más selectiva, no una continuación automática del mismo patrón.
