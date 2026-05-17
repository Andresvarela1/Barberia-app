# Phase 1.15 - Agenda Subhelpers

## Resumen de extracción

Se dividieron las secciones de agenda de `ADMIN` y `SUPER_ADMIN` en subhelpers locales más pequeños dentro de `app.py`.

Para `ADMIN` se extrajeron:

- `render_admin_agenda_calendar_tab(...)`
- `render_admin_agenda_list_tab(...)`
- `render_admin_agenda_income_tab(...)`

Para `SUPER_ADMIN` se extrajeron:

- `render_super_admin_agenda_calendar_tab(...)`
- `render_super_admin_agenda_list_tab(...)`
- `render_super_admin_agenda_income_tab(...)`

## Qué cambió

- `render_admin_agenda_section(...)` y `render_super_admin_agenda_section(...)` ahora coordinan tabs y delegan el contenido.
- Los bloques de calendario, listado e ingresos se movieron casi de forma mecánica a helpers explícitos.
- Se mantuvieron filtros, claves de widgets, consultas y acciones sin cambiar su comportamiento.

## Qué no cambió

- No se tocó `app_core/auth.py`.
- No se modificó la cadena `resolve_*`.
- No se alteró la lógica de negocio de reservas, pagos, disponibilidad o multi-barbería.
- No se movieron vistas a módulos por feature.

## Riesgos pendientes

- El bloque de listado en agenda sigue siendo el más denso porque concentra filtros, selección de vista y acciones sobre reservas.
- La siguiente decisión natural sería separar dentro de esos listados la parte de filtros y la parte de render de resultados, sin salir todavía de `app.py`.

## Siguiente paso recomendado

Extraer subhelpers adicionales para listados de agenda, por ejemplo filtros y render de resultados, manteniendo el mismo enfoque incremental y reversible.
