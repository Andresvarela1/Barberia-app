# PHASE 1.2 - Reservas Alignment

## Resumen

Esta iteracion alinea el contrato de datos de `reservas` entre:

- `schema.sql`
- `app_core/bootstrap.py`
- `app.py`
- `app_core/services/booking_service.py`
- `app_core/services/payment_service.py`
- `webhook.py`

El objetivo fue cerrar contradicciones obvias sin reescribir el flujo de reservas ni mover arquitectura.

## Contrato final de `reservas`

Columnas canonicas formalizadas en `schema.sql` y aseguradas por bootstrap runtime:

| Columna | Tipo | Uso actual |
| --- | --- | --- |
| `id` | `SERIAL PRIMARY KEY` | identificador de reserva |
| `nombre` | `TEXT NOT NULL` | nombre legacy del cliente; se mantiene por compatibilidad |
| `barbero` | `TEXT NOT NULL` | nombre legacy del barbero o marcador de compatibilidad |
| `barbero_id` | `INTEGER` | referencia operativa del barbero en agenda |
| `servicio` | `TEXT NOT NULL` | nombre del servicio |
| `precio` | `INTEGER NOT NULL` | precio base de la reserva |
| `inicio` | `TIMESTAMP NOT NULL` | inicio real del bloque de agenda |
| `fin` | `TIMESTAMP NOT NULL` | fin real del bloque de agenda |
| `barberia_id` | `INTEGER NOT NULL` | aislamiento multi-barberia |
| `cliente` | `TEXT` | nombre canonico usado por app/webhook/reportes |
| `telefono` | `TEXT` | compatibilidad para captura publica/modal |
| `email` | `TEXT` | compatibilidad para captura publica/modal/pagos |
| `fecha` | `DATE` | compatibilidad para filtros, metricas y UI |
| `hora` | `TIME` | compatibilidad para listados y formularios |
| `estado` | `TEXT NOT NULL DEFAULT 'activo'` | estado funcional actual |
| `pagado` | `BOOLEAN NOT NULL DEFAULT FALSE` | estado de pago |
| `monto` | `INTEGER` | monto final/cobrable |
| `payment_id` | `TEXT` | referencia externa de MercadoPago |
| `updated_at` | `TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP` | auditoria de cambios |

## Columnas agregadas o reconciliadas

Agregadas formalmente a `schema.sql`:

- `barbero_id`
- `cliente`
- `telefono`
- `email`
- `fecha`
- `hora`
- `estado`
- `pagado`
- `monto`
- `payment_id`
- `updated_at`

Indices formalizados en `schema.sql` y bootstrap:

- `idx_reservas_barbero_id`
- `idx_reservas_fecha`
- `idx_reservas_inicio`
- `idx_reservas_pagado`

Backfills agregados en bootstrap:

- `cliente = COALESCE(cliente, nombre)`
- `fecha = DATE(inicio)` cuando falta
- `hora = CAST(inicio AS TIME)` cuando falta
- `monto = precio` cuando falta
- `updated_at = CURRENT_TIMESTAMP` cuando falta

## Decisiones de compatibilidad

1. `nombre` y `cliente` se mantienen juntos.
   - `booking_service.py` y varias vistas ya usan `cliente`, pero hay codigo legacy que sigue leyendo `nombre`.
   - No se renombra ni elimina nada en esta fase.

2. `precio` y `monto` se mantienen juntos.
   - `precio` sigue siendo el valor base.
   - `monto` queda formalizado para pagos y metricas.

3. `telefono` y `email` se agregan formalmente.
   - Existian en inserts reales del modal publico, pero no en el schema estatico ni en bootstrap.
   - Se formalizan para evitar depender de columnas fantasma.

4. `fecha` y `hora` se mantienen aunque `inicio` y `fin` sean el rango canonico real.
   - Esto evita romper filtros, metricas, UI y reportes existentes.

5. El modal publico sigue funcionando sin seleccionar barbero.
   - Para compatibilidad incremental, esas reservas se guardan con:
     - `barbero_id = NULL`
     - `barbero = 'Sin asignar'`
   - Tambien se calculan `inicio`, `fin`, `precio` y `monto` para cumplir el contrato canonico.

6. Pagos quedan alineados al mismo contrato.
   - `payment_service.py` actualiza `pagado`, `monto` y `updated_at`.
   - `webhook.py` sigue usando `pagado`, `payment_id`, `updated_at`, `cliente`, `servicio`, `fecha`, ahora todas formalizadas.

## Cambios aplicados

### `schema.sql`

- Se amplio la definicion estatica de `reservas` al contrato canonico actual.
- Se agregaron indices usados por agenda, filtros y pagos.

### `app_core/bootstrap.py`

- El `CREATE TABLE IF NOT EXISTS reservas` ya nace con el contrato alineado.
- Los `ALTER TABLE` cubren columnas de compatibilidad faltantes.
- Se agregaron backfills de datos derivados.
- Se separo correctamente la creacion de indices de `reservas`.

### `app.py`

- Se corrigio el insert directo del modal publico.
- Ya no intenta escribir una fila parcial incompatible.
- Ahora escribe contra el contrato canonico completo de `reservas`.

### `app_core/services/payment_service.py`

- Se actualiza `updated_at` junto con `pagado` y `monto`.

## Riesgos pendientes para la siguiente fase

1. `barbero` texto sigue siendo parte de la restriccion `reservas_no_solapadas`.
   - La app operativa valida por `barbero_id` cuando lo tiene.
   - La restriccion SQL aun usa `barbero` texto.
   - Migrar esa restriccion a `barbero_id` requiere una fase separada por riesgo de datos legacy.

2. El valor `'Sin asignar'` evita romper el modal publico, pero no resuelve la politica de asignacion real.
   - Si se acumulan reservas sin barbero asignado, la semantica de agenda sigue siendo limitada.
   - Esta decision se tomo por estabilidad y compatibilidad.

3. `nombre` y `cliente` siguen duplicando semantica.
   - Se mantuvieron ambos para no romper reportes, vistas y rutas legacy.

4. No se agrego FK de `barbero_id -> usuarios.id` en esta fase.
   - Puede haber datos legacy que hoy no cumplan esa relacion.
   - Conviene validar primero consistencia real antes de endurecer la DB.

## Verificacion hecha

- Validacion estatica de referencias activas a columnas de `reservas`
- `py_compile` sobre archivos tocados
- tests focalizados de alineacion del contrato

## Archivos tocados en esta fase

- `schema.sql`
- `app_core/bootstrap.py`
- `app.py`
- `app_core/services/payment_service.py`
- `tests/test_reservas_contract_alignment.py`

## Siguiente write set recomendado

Para una fase siguiente, los archivos mas probables son:

- `app_core/services/booking_service.py`
- `app_core/services/availability_service.py`
- `app_core/metrics.py`
- `webhook.py`
- `app.py`

En esa siguiente fase convendria decidir si `barbero_id` pasa a ser la identidad estructural unica de agenda y si `nombre/cliente` y `precio/monto` pueden empezar a converger.
