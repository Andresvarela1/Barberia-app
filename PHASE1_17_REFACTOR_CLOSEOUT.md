# Phase 1.17 - Refactor Closeout

## Resumen de cierre

Esta fase cierra la serie incremental 1.x con una pasada conservadora de consistencia interna sobre `app.py`.

Se aplicaron dos limpiezas pequeñas y seguras:

- se simplificó el wiring del dispatch principal eliminando un branch redundante de `screen_group`;
- se removió el arrastre de `screen_key` dentro del render autenticado, donde ya no tenía uso real después de las fases previas.

## Estado final de la etapa 1.x

Quedó consolidada una separación incremental en estas capas:

- resolución de sesión/auth y acceso:
  - `login_and_prepare_session(...)`
  - `logout_and_reset_session(...)`
  - `normalize_authenticated_session_state(...)`
  - `resolve_authenticated_entry(...)`
  - `resolve_view_access(...)`
  - `resolve_render_view(...)`
  - `resolve_screen_dispatch(...)`
- render público:
  - `render_public_screen(...)`
- render autenticado:
  - `render_authenticated_screen(...)`
  - `render_authenticated_shell(...)`
  - `render_authenticated_content(...)`
- contenido autenticado segmentado por rol y por secciones internas
- agenda `ADMIN` y `SUPER_ADMIN` segmentada por tabs y por flujo de listado

## Qué no se siguió empujando

Para cerrar esta etapa con bajo riesgo, no se avanzó en:

- mover vistas a módulos por feature;
- consolidar toda la duplicación menor entre `ADMIN` y `SUPER_ADMIN`;
- extraer lógica de negocio de reservas, pagos o multi-barbería;
- tocar la cadena `resolve_*` más allá del wiring mínimo.

## Deuda explícita para una etapa 2

Si más adelante vale la pena una etapa 2, la deuda principal ya quedó localizada:

1. evaluar si conviene extraer módulos por feature para agenda, servicios y equipo;
2. revisar si parte del render de `ADMIN` y `SUPER_ADMIN` puede compartir shell/flows sin perder claridad;
3. decidir si el siguiente salto debe ser puramente de frontend, o si conviene pasar a una modularización más fuerte de dominio.

## Criterio de cierre

El objetivo de esta etapa ya quedó cubierto: `app.py` sigue siendo entrypoint, pero con bastante menos mezcla entre auth/session, routing, shell y contenido renderizado, sin cambiar comportamiento visible ni abrir una reestructuración mayor.
