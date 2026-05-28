# PHASE 1.8 - Render View Resolution

## Resumen de extracción

Esta fase extrae de `app.py` la resolución reusable de la vista final a renderizar.

No se movió el render concreto de pantallas ni el router completo. El objetivo fue que `app.py` deje de mezclar:

- la validación de acceso por sesión,
- la corrección de vista,
- y la elección final de la vista renderizable.

## Funciones movidas o consolidadas

- `resolve_render_view(default_barberia_id, current_view=None)`
  - vive en `app_core/auth.py`
  - reutiliza `resolve_view_access(...)`
  - devuelve una decisión explícita para el router:
    - `resolved_view`
    - `should_rerun`
    - `should_stop`
    - `is_authenticated`

## Funciones que quedaron en `app.py` y por qué

- El `if/elif` que renderiza `home`, `login`, `registro`, `reserva` y dashboards
  - sigue en `app.py` porque esta fase no busca mover el render de vistas.

- El `st.rerun()` y `st.stop()` finales
  - siguen en `app.py`, pero ahora obedecen una resolución centralizada.

## Riesgos pendientes

1. El router principal sigue viviendo en `app.py`.
   - Ya no decide tanto estado previo, pero todavía concentra el render.

2. La lista de vistas sigue expresada como strings.
   - Está más centralizada, pero no formalizada aún como un mapa/router separado.

3. Hay otras decisiones de navegación fuera de auth/session.
   - Ejemplo: booking público, registro escalonado y navegación interna del dashboard.

## Siguiente paso recomendado para Fase 1.9

Extraer una capa mínima de router shell que reciba la vista resuelta y ejecute el render correspondiente, dejando a `app.py` como entrypoint más lineal sin mover todavía cada pantalla a módulos separados.
