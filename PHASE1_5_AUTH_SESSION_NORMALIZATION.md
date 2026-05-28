# PHASE 1.5 - Auth Session Normalization

## Resumen de extracción

Esta fase completa una extracción incremental del wiring post-login/post-logout sin tocar el render del login ni la navegación visible.

El foco fue centralizar en `app_core/auth.py` la normalización del estado autenticado para que `app.py` deje de corregir `view`, `user_role`, `public_mode` y contexto base en varios lugares.

## Funciones movidas o consolidadas

- `normalize_authenticated_session_state(default_barberia_id)`
  - normaliza `rol` y `user_role`
  - estabiliza `view` hacia el dashboard correcto cuando la sesión autenticada viene desde una vista pública o parcial
  - asegura `public_mode = False`
  - completa `user_id`, `barberia_id` y `barberia_context_id` cuando faltan
  - apaga `super_admin_all_barberias` para roles que no corresponden

- `login_and_prepare_session(...)`
  - sigue siendo el entry point de login reutilizable
  - ahora delega en `normalize_authenticated_session_state(...)` después de aplicar el contexto base

- `logout_and_reset_session(...)`
  - se mantiene como punto único de reset de sesión autenticada

## Funciones que quedaron en `app.py` y por qué

- Render del login y sus mensajes:
  - siguen en `app.py` porque son parte de la UI Streamlit y del flujo visible.

- Routing por `view`:
  - sigue en `app.py` porque todavía forma parte del shell principal de la app.

- Navegación y sidebar:
  - siguen ahí porque mezclan layout, permisos visibles y componentes premium.

## Riesgos pendientes

1. `app.py` todavía controla el router principal por `view`.
   - Ya no corrige manualmente el estado autenticado como antes, pero sigue siendo el coordinador del flujo global.

2. El estado de navegación no-auth todavía vive repartido.
   - Hay claves públicas, del booking y de registro que esta fase no toca a propósito.

3. `normalize_authenticated_session_state(...)` trabaja con convenciones actuales de sesión.
   - Si a futuro cambian nombres de claves, convendrá centralizarlas como constantes.

## Siguiente paso recomendado para Fase 1.6

Extraer una capa pequeña de routing/shell desde `app.py`:

- normalización de `view`
- redirección entre home/login/dashboard
- wrappers de navegación post-auth

Ese paso seguiría bajando acoplamiento sin entrar todavía en reservas, agenda o pagos.
