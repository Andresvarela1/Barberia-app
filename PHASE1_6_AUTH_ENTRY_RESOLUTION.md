# PHASE 1.6 - Auth Entry Resolution

## Resumen de extracción

Esta fase saca de `app.py` la decisión reusable de entrada para usuarios ya autenticados.

El objetivo no fue mover el router completo, sino encapsular la respuesta a una pregunta puntual:

- si ya existe una identidad autenticada, ¿a qué vista inicial debe caer esa sesión y con qué contexto base?

La resolución quedó centralizada en `app_core/auth.py`, reutilizando la normalización de sesión agregada en fases anteriores.

## Funciones movidas o consolidadas

- `resolve_authenticated_entry(default_barberia_id)`
  - usa `normalize_authenticated_session_state(...)`
  - determina la vista inicial para un usuario autenticado
  - corrige vistas públicas o inválidas hacia el dashboard que corresponde por rol
  - devuelve una decisión clara y testeable:
    - `target_view`
    - `view`
    - `should_rerun`

- `login_and_prepare_session(...)`
  - ahora también usa `resolve_authenticated_entry(...)`
  - así el login recién exitoso y el reenganche de sesión autenticada comparten la misma decisión de destino

## Funciones que quedaron en `app.py` y por qué

- Router principal por `view`
  - sigue en `app.py` porque esta fase no busca mover toda la navegación.

- Render del login y sus mensajes
  - siguen en `app.py` porque pertenecen a la UI Streamlit y al flujo visible.

- Sidebar y navegación de paneles
  - siguen ahí porque mezclan layout, controles visuales y acciones del usuario.

## Riesgos pendientes

1. `app.py` todavía contiene el router global.
   - La decisión inicial ya está centralizada, pero la ejecución completa del flujo sigue en el entrypoint.

2. Existen más estados de UI fuera del alcance de auth/session.
   - Modales, booking público, registro y navegación interna todavía usan claves propias en `session_state`.

3. La resolución de entrada trabaja sobre los dashboards actuales.
   - Si el sistema cambia la taxonomía de vistas, habrá que actualizar esta lógica central.

## Siguiente paso recomendado para Fase 1.7

Extraer un helper pequeño de routing de shell para reducir aún más la lógica condicional de `app.py`, sin mover todavía la navegación completa ni las áreas de dominio.
