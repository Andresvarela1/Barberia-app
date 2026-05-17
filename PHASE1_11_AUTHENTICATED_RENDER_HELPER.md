# Phase 1.11 - Authenticated Render Helper

## Resumen de extracción

Se extrajo un helper local `render_authenticated_screen(...)` dentro de `app.py` para encapsular el bloque principal de render autenticado. La orquestación general no cambió:

1. `resolve_screen_dispatch(...)` sigue resolviendo `screen_key` y `screen_group`.
2. `app.py` sigue manejando `should_rerun` y `should_stop`.
3. El render público sigue yendo por `render_public_screen(...)`.
4. El render autenticado ahora se delega a `render_authenticated_screen(...)`.

## Qué se movió

- El bloque inline de render por rol para:
  - `CLIENTE`
  - `BARBERO`
  - `ADMIN`
  - `SUPER_ADMIN`
- La lógica de selección por `seccion` dentro de cada uno de esos roles.

## Qué no cambió

- No se movió lógica de negocio profunda fuera de `app.py`.
- No se cambió el dispatch previo ni la resolución de vistas.
- No se tocaron textos, navegación visible, permisos ni contratos.
- Los helpers internos como `render_equipo_barberos(...)`, `render_gestion_servicios(...)` y `_panel_ingresos(...)` siguen locales al mismo bloque de app.

## Riesgos pendientes

- El helper autenticado sigue siendo grande porque esta fase buscó un movimiento mecánico y reversible, no una partición por feature.
- El siguiente riesgo natural sigue estando en el tamaño interno de cada rama por rol, especialmente `ADMIN` y `SUPER_ADMIN`.

## Siguiente paso recomendado

Si conviene seguir con el mismo enfoque incremental, el próximo corte lógico es separar dentro del helper autenticado sub-helpers locales por rol o por secciones internas (`Agenda`, `Dashboard`, `Servicios`) sin sacar todavía esas pantallas a módulos nuevos.
