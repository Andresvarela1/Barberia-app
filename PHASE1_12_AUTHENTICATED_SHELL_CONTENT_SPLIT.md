# Phase 1.12 - Authenticated Shell and Content Split

## Resumen de extracción

Se separó el render autenticado en dos responsabilidades locales dentro de `app.py`:

1. `render_authenticated_shell(...)`
2. `render_authenticated_content(...)`

`render_authenticated_screen(...)` quedó como coordinador liviano que arma el contexto común del usuario autenticado y delega el contenido interno por rol y sección.

## Qué cambió

- El shell autenticado común ahora encapsula:
  - `apply_internal_panel_css()`
  - carga de usuario/rol/contexto
  - aviso de modo demo sin DB
  - sidebar, navegación y logout
- El contenido autenticado mantiene intacta la lógica previa de dashboards y vistas internas.

## Qué no cambió

- No se tocó `app_core/auth.py`.
- No se modificó la cadena `resolve_*`.
- No se cambió la lógica de negocio de reservas, pagos, clientes, servicios o métricas.
- No se movieron vistas internas a módulos separados.

## Riesgos pendientes

- `render_authenticated_content(...)` sigue siendo grande porque todavía concentra las ramas por rol.
- La siguiente oportunidad natural, si sigue teniendo sentido, es separar sub-helpers por rol o por secciones internas (`Dashboard`, `Agenda`, `Servicios`) manteniendo el mismo enfoque incremental.

## Siguiente paso recomendado

Extraer dentro de `render_authenticated_content(...)` pequeños helpers locales por rol (`CLIENTE`, `BARBERO`, `ADMIN`, `SUPER_ADMIN`) o por secciones internas, sin tocar todavía la lógica de dominio.
