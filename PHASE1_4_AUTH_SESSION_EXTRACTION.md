# PHASE 1.4 - Auth and Session Extraction

## Resumen de extracción

Esta fase extrae de `app.py` la lógica reusable de autenticación y armado/reset de sesión, sin cambiar el render del login ni el flujo visible para el usuario.

El recorte se apoyó en dos capas ya existentes:

- `app_core/auth.py` como módulo natural para autenticación
- `app_core/tenancy.py` como capa ya responsable del contexto post-login

La idea fue centralizar login/logout de sesión sin reabrir todavía navegación completa, reservas ni pagos.

## Funciones movidas

### En `app_core/auth.py`

Se agregaron:

- `login_and_prepare_session`
  - autentica con `login(...)`
  - delega el armado de contexto a `apply_login_session_context(...)`
  - deja resuelto el `view` de destino

- `logout_and_reset_session`
  - limpia el estado autenticado
  - restaura defaults seguros de sesión
  - elimina caches y navegación dependiente de usuario/rol

### Reutilización de `app_core/tenancy.py`

No se duplicó lógica de contexto post-login.

`login_and_prepare_session(...)` reutiliza:

- `apply_login_session_context(...)`

para mantener una sola fuente de verdad sobre `barberia_id`, `barberia_context_id`, `user_role` y vista de destino.

## Funciones que quedaron en `app.py` y por qué

- Render del formulario de login:
  - sigue en `app.py` porque mezcla Streamlit, layout, estilos y mensajes visibles.

- `st.success`, `st.error`, `st.rerun()` del flujo visual:
  - siguen cerca del render para no mover comportamiento de interfaz ni timing de reruns.

- Navegación general de la app:
  - sigue en `app.py` porque todavía es parte del entrypoint principal.

- Registro y otras operaciones de auth no relacionadas con sesión visual:
  - se dejaron como estaban para mantener el cambio acotado.

## Riesgos pendientes

1. `app.py` todavía coordina navegación post-login.
   - Ya no arma directamente la sesión autenticada, pero sigue decidiendo la transición visual global.

2. Logout resetea claves base y caches conocidas, no toda la sesión.
   - Esto es intencional para no romper defaults que el arranque espera.
   - Puede quedar estado residual no crítico en features no tocadas.

3. El formulario de login sigue acoplado a Streamlit.
   - En esta fase sólo se extrajo la lógica reusable, no el rendering.

4. `app_core/auth.py` ahora mezcla autenticación y helpers de sesión.
   - Es aceptable en esta etapa porque evita abrir otro módulo innecesario.
   - Si la app sigue creciendo, más adelante podría separarse `session_auth.py`.

## Siguiente paso recomendado para Fase 1.5

Extraer una capa chica de routing/shell de aplicación desde `app.py`, por ejemplo:

- redirección por `view`
- transición entre home/login/dashboard
- logout redirect
- algunas reglas de navegación por rol

Eso permitiría que `app.py` quede más claramente como entrypoint visual y coordinador liviano, sin tocar todavía reservas o agenda.
