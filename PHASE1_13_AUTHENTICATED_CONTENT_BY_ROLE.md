# Phase 1.13 - Authenticated Content by Role

## Resumen de extracción

Se separó `render_authenticated_content(...)` en helpers locales por rol dentro de `app.py`:

- `render_cliente_content(...)`
- `render_barbero_content(...)`
- `render_admin_content(...)`
- `render_super_admin_content(...)`

`render_authenticated_content(...)` quedó reducido a un dispatcher liviano por `nr`.

## Qué cambió

- Cada rama existente por rol se movió casi de forma mecánica a su helper correspondiente.
- Se mantuvieron argumentos explícitos para evitar depender de contexto implícito.
- El fallback por rol desconocido sigue devolviendo el mismo error visual.

## Qué no cambió

- No se tocó `app_core/auth.py`.
- No se modificó la cadena `resolve_*`.
- No se cambió la navegación, el shell autenticado ni la lógica de negocio profunda.
- No se movieron vistas internas a módulos separados.

## Riesgos pendientes

- Los helpers por rol siguen siendo grandes, especialmente `ADMIN` y `SUPER_ADMIN`.
- El próximo corte razonable sería separar dentro de esos helpers por secciones internas como `Dashboard`, `Agenda`, `Servicios` o `Configuración`, manteniendo el mismo enfoque incremental.

## Siguiente paso recomendado

Extraer sub-helpers locales por secciones internas de cada rol, priorizando `ADMIN` y `SUPER_ADMIN`, sin abrir todavía una modularización por feature.
