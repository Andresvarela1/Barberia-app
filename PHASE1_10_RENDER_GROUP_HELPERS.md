# PHASE 1.10 - Render Group Helpers

## Resumen de extracción

Esta fase extrae de `app.py` un helper de render para el grupo de pantallas públicas y deja explícita la noción de grupo de pantalla en el dispatch.

El objetivo no fue mover todavía cada pantalla a módulos separados, sino adelgazar el entrypoint para que:

- la selección de pantalla siga viniendo de `resolve_screen_dispatch(...)`
- `app.py` orqueste `rerun/stop`
- y el render se delegue por grupo en lugar de mantener bloques inline largos mezclados.

## Cambios principales

- `app_core/auth.py`
  - `resolve_screen_dispatch(...)` ahora devuelve también `screen_group`
  - grupos actuales:
    - `public`
    - `authenticated`

- `app.py`
  - se agregó `render_public_screen(...)`
  - el router principal ahora usa:
    - `dispatch_decision`
    - `screen_key`
    - `screen_group`
  - las pantallas públicas (`home`, `login`, `registro`, `reserva`) dejaron de vivir inline en el bloque principal

## Qué quedó en `app.py` y por qué

- El render concreto de pantallas públicas
  - sigue en `app.py`, pero encapsulado en un helper local para reducir riesgo de imports y contexto.

- El bloque autenticado principal
  - sigue inline porque todavía contiene mucho render y lógica cercana al dominio.
  - moverlo entero en esta fase habría aumentado demasiado el riesgo.

## Riesgos pendientes

1. El grupo autenticado todavía es grande.
   - Esta fase sólo separó claramente el grupo público y dejó listo el terreno para aplicar la misma estrategia al shell autenticado.

2. `app.py` sigue siendo el orquestador principal.
   - Ahora es más lineal, pero todavía concentra bastante render.

3. El dispatch sigue basado en strings.
   - Está más ordenado y centralizado, pero no abstraído por completo.

## Siguiente paso recomendado para Fase 1.11

Extraer un helper equivalente para el shell autenticado, sin mover todavía la lógica profunda de dashboards o reservas. Eso dejaría a `app.py` muy cerca de un orquestador puro del flujo principal.
