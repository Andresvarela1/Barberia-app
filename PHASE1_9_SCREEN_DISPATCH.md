# PHASE 1.9 - Screen Dispatch

## Resumen de extracción

Esta fase extrae de `app.py` la resolución reusable del despacho de vistas.

No se movió el render concreto de `home`, `login`, `registro`, `reserva` ni dashboards. El objetivo fue que `app.py` deje de usar directamente la vista resuelta como matriz de selección y pase a consumir una decisión explícita de dispatch.

## Funciones movidas o consolidadas

- `resolve_screen_dispatch(default_barberia_id, current_view=None)`
  - vive en `app_core/auth.py`
  - reutiliza `resolve_render_view(...)`
  - devuelve:
    - `screen_key`
    - `resolved_view`
    - `should_rerun`
    - `should_stop`
    - `is_authenticated`

## Funciones que quedaron en `app.py` y por qué

- El bloque `if/elif` que renderiza cada pantalla
  - sigue en `app.py` porque esta fase no mueve el render concreto.

- Los `st.rerun()` y `st.stop()`
  - siguen ejecutándose en `app.py`, pero ya salen de una resolución de dispatch centralizada.

## Riesgos pendientes

1. `app.py` todavía contiene el render principal.
   - La selección del bloque está más limpia, pero el código de cada pantalla sigue concentrado ahí.

2. El router sigue basado en strings de vista.
   - Ahora están mejor encapsulados, pero no convertidos aún en una capa de router separada.

3. Hay navegación interna de dashboards fuera del alcance de esta fase.
   - Esta extracción sólo cubre el despacho principal previo al render.

## Siguiente paso recomendado para Fase 1.10

Extraer una capa mínima de shell router que reciba `screen_key` y delegue el render a funciones ya existentes dentro de `app.py`, sin mover todavía esas funciones a otros módulos.
