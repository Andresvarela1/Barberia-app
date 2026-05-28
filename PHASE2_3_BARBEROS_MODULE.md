# Phase 2.3 - Barberos Module

## Resumen de la extracción

Se continuó la etapa 2 con una tercera extracción real por feature: la sección `Barberos` para `ADMIN` y `SUPER_ADMIN` se movió a un módulo propio:

- `app_core/features/barberos/rendering.py`

## Qué se movió

Se extrajo desde `app.py` la implementación concreta de la feature:

- formulario para agregar barberos
- listado de barberos registrados
- eliminación de barberos
- estados vacíos y validaciones visibles
- estilos locales usados por la sección

El módulo nuevo expone una sola entrada principal:

- `render_barberos_section(...)`

## Cómo quedó la integración

`app.py` ya no contiene la implementación concreta de `Barberos`.

Ahora sólo resuelve el contexto por rol y delega:

- `ADMIN`: pasa `barberia_id` y `barberia_name`
- `SUPER_ADMIN`: pasa `bid_ctx` y el mensaje de contexto activo

La lógica operativa sigue apoyándose en:

- `app_core.auth.registrar`
- `app_core.db.safe_execute`
- `app_core.services.availability_service.listar_usuarios_barberos`

## Qué no cambió

- No se modificó la UI ni el comportamiento visible.
- No se tocó auth/session, `resolve_*`, agenda, servicios, pagos ni tenancy.
- No se abrió una modularización masiva del resto de la app.

## Patrón que valida para etapa 2

Esta fase vuelve a confirmar el mismo patrón de modularización por feature:

1. `app.py` conserva la decisión de contexto por rol;
2. la feature vive en un módulo propio;
3. el módulo encapsula el render concreto y usa dependencias existentes sin disparar una refactorización mayor.

## Riesgos pendientes

- El módulo mantiene acoplamiento deliberado con el flujo actual de Streamlit y con las primitivas ya existentes de usuarios/DB, para preservar bajo riesgo.
- Si la etapa 2 sigue, ya hay evidencia suficiente para elegir otra feature operativa con frontera limpia o detener la modularización donde ya aporta valor real.
