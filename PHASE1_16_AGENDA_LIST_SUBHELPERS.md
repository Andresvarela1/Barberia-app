# Phase 1.16 - Agenda List Subhelpers

## Resumen de extracción

Se dividió el tab de listado de agenda para `ADMIN` y `SUPER_ADMIN` en subhelpers locales más pequeños dentro de `app.py`.

Para `ADMIN` se extrajeron:

- `render_admin_agenda_list_filters(...)`
- `render_admin_agenda_list_card_actions(...)`
- `render_admin_agenda_list_results(...)`

Para `SUPER_ADMIN` se extrajeron:

- `render_super_admin_agenda_list_filters(...)`
- `render_super_admin_agenda_list_card_actions(...)`
- `render_super_admin_agenda_list_results(...)`

Además se consolidó el render de resultados en calendario en un helper compartido:

- `render_agenda_calendar_results(...)`

## Qué cambió

- `render_admin_agenda_list_tab(...)` y `render_super_admin_agenda_list_tab(...)` ahora coordinan el flujo del tab.
- Los bloques de filtros, modo de vista y acciones sobre reservas se movieron casi de forma mecánica a helpers explícitos.
- Se mantuvieron claves de widgets, filtros, consultas y acciones sin alterar su comportamiento.

## Qué no cambió

- No se tocó `app_core/auth.py`.
- No se modificó la cadena `resolve_*`.
- No se cambió la lógica de negocio de reservas, pagos, permisos o multi-barbería.
- No se movieron vistas a módulos separados.

## Riesgos pendientes

- Sigue habiendo algo de duplicación entre `ADMIN` y `SUPER_ADMIN` en el flujo del listado, pero ahora está más localizada y clara.
- Si más adelante conviene seguir, el siguiente paso natural sería evaluar una consolidación muy acotada de los flows de listado, sólo si sigue siendo segura y fácil de revisar.

## Siguiente paso recomendado

Hacer una pasada final de consolidación liviana o cerrar esta etapa de refactor incremental si el objetivo principal ya quedó cubierto.
