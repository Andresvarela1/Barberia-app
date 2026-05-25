# Phase 2.1 - Agenda Listing Module

## Resumen de la extracción

Se inició la etapa 2 con una primera extracción real por feature: el tab de listado de agenda de `ADMIN` y `SUPER_ADMIN` se movió a un módulo propio:

- `app_core/agenda/listing.py`

## Qué se movió

Se extrajeron desde `app.py`:

- `render_admin_agenda_list_tab(...)`
- `render_super_admin_agenda_list_tab(...)`
- sus helpers directos de filtros
- sus helpers de acciones sobre reservas
- el helper compartido de resultados en modo calendario

## Cómo quedó la integración

`app.py` conserva la orquestación de agenda y pasa dependencias explícitas al módulo nuevo:

- filtros
- callbacks de render de reservas
- acciones de pago/eliminación
- render de calendario
- nota visual compartida

No se tocó la resolución previa de sesión, vista o dispatch.

## Qué no cambió

- No se modificó la UI ni el comportamiento visible.
- No se movió todavía toda la agenda.
- No se tocó lógica profunda de reservas, pagos, multi-barbería o auth.

## Patrón que deja para etapa 2

Esta extracción deja un patrón claro para seguir modularizando por feature:

1. seleccionar una frontera funcional estable;
2. mover el bloque concreto a `app_core/<feature>/...`;
3. mantener `app.py` como orquestador con dependencias explícitas;
4. evitar en esta etapa una abstracción prematura del dominio.

## Riesgos pendientes

- El módulo nuevo todavía depende de varios callbacks del entrypoint, lo cual fue una decisión deliberada para mantener el cambio chico y reversible.
- Si la etapa 2 sigue, el siguiente corte natural sería otro sub-bloque de Agenda o alguna sección igualmente estable dentro de `ADMIN` / `SUPER_ADMIN`.
