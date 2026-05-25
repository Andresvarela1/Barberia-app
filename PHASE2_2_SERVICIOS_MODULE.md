# Phase 2.2 - Servicios Module

## Resumen de la extracción

Se continuó la etapa 2 con una segunda extracción real por feature: la sección `Servicios` para `ADMIN` y `SUPER_ADMIN` se movió a un módulo propio:

- `app_core/features/services/rendering.py`

## Qué se movió

Se extrajo desde `app.py` la implementación concreta del render de la feature:

- formulario de alta de servicio
- listado de servicios existentes
- edición de servicios
- eliminación de servicios
- estados vacíos y validaciones visibles

El módulo nuevo expone una sola entrada principal:

- `render_services_section(...)`

## Cómo quedó la integración

`app.py` ya no contiene la implementación concreta de `Servicios`.

Ahora sólo resuelve el contexto por rol y delega:

- `ADMIN`: pasa `barberia_id` y `barberia_name`
- `SUPER_ADMIN`: pasa `bid_ctx` y el mensaje de contexto activo

La lógica profunda CRUD sigue apoyándose en:

- `app_core.services.servicios_service`
- `app_core.db.safe_fetch_all`

## Qué no cambió

- No se modificó la UI ni el comportamiento visible.
- No se tocó auth/session, `resolve_*`, agenda, pagos ni tenancy.
- No se abrió una modularización masiva del resto de la app.

## Patrón que valida para etapa 2

Esta fase confirma que la modularización por feature funciona también fuera de Agenda:

1. `app.py` queda como orquestador contextual;
2. la feature vive en un módulo propio;
3. el módulo recibe lo mínimo necesario para renderizar sin disparar una refactorización paralela grande.

## Riesgos pendientes

- El módulo todavía depende del diseño actual de Streamlit y de funciones CRUD ya existentes, lo cual fue deliberado para mantener el cambio chico.
- Si la etapa 2 sigue, una siguiente candidata natural sería otra feature operativa con frontera limpia similar a `Servicios`.
