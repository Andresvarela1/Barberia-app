# PHASE 1.7 - View Access Guards

## Resumen de extracción

Esta fase extrae de `app.py` la validación reusable de acceso entre vistas públicas y autenticadas.

No se movió el router completo. El objetivo fue encapsular la decisión de:

- si la vista actual es compatible con el estado de sesión,
- si debe corregirse,
- si corresponde `rerun`,
- y si el flujo público debe detenerse antes de entrar al área autenticada.

## Funciones movidas o consolidadas

- `resolve_view_access(default_barberia_id, current_view=None)`
  - vive en `app_core/auth.py`
  - reutiliza `resolve_authenticated_entry(...)`
  - resuelve para el estado actual:
    - `is_allowed`
    - `resolved_view`
    - `should_rerun`
    - `should_stop`

## Funciones que quedaron en `app.py` y por qué

- Router principal por `view`
  - sigue en `app.py` porque esta fase no busca mover la navegación completa.

- Render de vistas públicas y dashboards
  - siguen en `app.py` porque pertenecen a la capa visual y al flujo principal de Streamlit.

- Llamadas concretas a `st.rerun()` y `st.stop()`
  - siguen ocurriendo desde `app.py`, pero ahora derivadas de una decisión centralizada en vez de condicionales dispersos.

## Riesgos pendientes

1. El router global sigue siendo grande.
   - Ya no decide manualmente varios guards de acceso, pero todavía orquesta toda la navegación.

2. Existen estados de UI fuera del alcance de auth/session.
   - Booking público, modales y registro mantienen sus propias claves de sesión.

3. La taxonomía actual de vistas sigue implícita en helpers.
   - Si a futuro cambian nombres de vistas, habrá que ajustar esa lista central.

## Siguiente paso recomendado para Fase 1.8

Extraer una capa pequeña de routing shell para centralizar:

- validación de vista actual,
- transición entre vistas públicas,
- transición hacia dashboards autenticados.

Eso permitiría adelgazar `app.py` otro poco sin mover todavía lógica de dominio ni pantallas.
