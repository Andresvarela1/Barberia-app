# PHASE 1.3 - DB and Tenancy Extraction

## Resumen de extracción

Esta fase no reescribe la app ni mueve lógica de negocio grande. El cambio se enfocó en:

- dejar `app_core/db/` como fachada reutilizable para conexión y wrappers de query;
- crear `app_core/tenancy.py` como punto de entrada claro para contexto de sesión y multi-tenancy;
- recablear `app.py` para usar esos helpers en los puntos donde todavía concentraba wiring transversal.

El objetivo fue reducir acoplamiento real en `app.py` sin cambiar UX, flujos ni contratos de datos.

## Funciones movidas

### A `app_core/db/__init__.py`

Se centralizó la exportación de helpers ya existentes:

- `get_database_url`
- `get_connection`
- `create_fresh_connection`
- `is_db_available`
- `fetch_one`
- `fetch_all`
- `execute_write`
- `safe_fetch_one`
- `safe_fetch_all`
- `safe_execute`

### A `app_core/tenancy.py`

Nuevos helpers de contexto:

- `ensure_session_defaults`
- `apply_public_barberia_context`
- `reset_public_barberia_context`
- `apply_login_session_context`
- `get_cached_barberia_name`
- `load_super_admin_context_options`

Y se reexponen desde un solo lugar helpers ya existentes de `app_core.security.tenant_access`:

- `normalizar_rol`
- `session_barberia_for_write`
- `effective_barberia_id`
- `get_current_barberia_id`
- `enforce_access`
- `get_user_barberia_id`
- `get_user_role`
- `can_access_barberia`
- `enforce_barberia_access`
- `get_user_id`

## Funciones que quedaron en `app.py` y por qué

- Renderizado de sidebar y controles Streamlit:
  - sigue en `app.py` porque mezcla layout, componentes premium y navegación visible.

- Flujo visual de login:
  - sigue en `app.py` porque depende de formularios, spinners, mensajes y navegación.
  - solo se extrajo la parte reusable de aplicación de contexto post-login.

- Routing principal y view state:
  - sigue en `app.py` porque todavía es el entrypoint coordinador de la aplicación.

- Helpers de negocio no directamente ligados a DB/tenancy:
  - reservas, pagos, fidelización y UX quedaron fuera de esta fase para no mezclar responsabilidades.

## Riesgos pendientes

1. `app.py` sigue siendo el coordinador principal.
   - La extracción bajó acoplamiento transversal, pero todavía concentra navegación y bastante UI.

2. `tenant_access.py` y `tenancy.py` coexisten.
   - En esta fase fue intencional: `tenant_access.py` conserva validaciones de seguridad y `tenancy.py` agrega wiring de sesión.
   - En una fase posterior conviene decidir si convergen o si siguen como capas separadas.

3. Hay más contexto reusable todavía adentro de `app.py`.
   - Ejemplos: logout/reset de sesión, navegación por rol y ciertos caches de UI.
   - No se movieron para no aumentar riesgo.

4. La fachada `app_core/db` no cambia comportamiento interno.
   - Centraliza imports y reutilización, pero `connection.py` y `safe_queries.py` mantienen su implementación actual.

## Siguiente paso recomendado para Fase 1.4

Hacer una extracción pequeña del wiring de shell de aplicación:

- inicialización de sesión;
- transición de login/logout;
- selección de contexto `SUPER_ADMIN`;
- navegación principal por rol.

Ese recorte dejaría a `app.py` más claramente como entrypoint visual y reduciría todavía más el acoplamiento sin tocar reservas ni pagos.
