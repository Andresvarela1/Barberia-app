# Phase 1.14 - Admin and Super Admin Sections

## Resumen de extracción

Se dividieron `render_admin_content(...)` y `render_super_admin_content(...)` en helpers locales por secciones internas dentro de `app.py`.

Para `ADMIN` se extrajeron helpers como:

- `render_admin_dashboard_section(...)`
- `render_admin_agenda_section(...)`
- `render_admin_barberos_section(...)`
- `render_admin_servicios_section(...)`
- `render_admin_configuracion_section(...)`
- y equivalentes para `Clientes`, `Sitio Web` y `Complementos`

Para `SUPER_ADMIN` se siguió el mismo patrón con helpers por sección.

## Qué cambió

- Los coordinadores `render_admin_content(...)` y `render_super_admin_content(...)` ahora sólo despachan por `seccion`.
- El contenido interno por sección se movió casi de forma mecánica a helpers explícitos.
- Se conservaron argumentos simples y explícitos para no depender de contexto implícito.

## Qué no cambió

- No se tocó `app_core/auth.py`.
- No se modificó la cadena `resolve_*`.
- No se cambió el shell autenticado.
- No se movió lógica de negocio profunda ni se crearon módulos por feature.

## Riesgos pendientes

- `render_admin_agenda_section(...)` y `render_super_admin_agenda_section(...)` siguen siendo los bloques más pesados.
- La siguiente oportunidad natural es separar dentro de esas secciones sub-bloques como calendario, listado e ingresos, todavía sin modularizar por feature.

## Siguiente paso recomendado

Extraer sub-helpers locales para las secciones de agenda de `ADMIN` y `SUPER_ADMIN`, manteniendo el mismo enfoque incremental y reversible.
