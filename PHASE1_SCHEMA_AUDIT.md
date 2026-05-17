# PHASE 1 - Schema Audit

## Resumen ejecutivo

El contrato de datos real **no coincide** con `schema.sql`.

Hoy existen tres fuentes de verdad parcialmente distintas:

1. `schema.sql` define un esquema minimo.
2. `app_core/bootstrap.py` expande tablas en runtime con `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.
3. `app.py`, `app_core/services/*` y `webhook.py` asumen columnas adicionales y ciertos estados/semanticas que no estan formalizados de forma unica.

Conclusion corta:

- `schema.sql` **no alcanza** para levantar la app con el comportamiento actual.
- El esquema efectivo real es: **`schema.sql` + runtime DDL de `app_core/bootstrap.py` + supuestos dispersos en codigo**.
- La tabla `reservas` concentra la mayor desalineacion.
- `webhook.py` depende de columnas que **no existen en `schema.sql`**.
- Hay inconsistencias de naming y semantica que deben resolverse antes de seguir con refactor grande:
  - `cliente` vs `nombre`
  - `precio` vs `monto`
  - `barbero` vs `barbero_id`
  - `estado = 'activo'` vs `estado = 'confirmada'`
  - `barberias.estado = 'activa'` vs consultas con `estado = 'active'`

---

## Tablas detectadas

Tablas principales auditadas:

- `barberias`
- `usuarios`
- `reservas`
- `servicios`

Fuentes revisadas:

- `app.py`
- `schema.sql`
- `webhook.py`
- `app_core/bootstrap.py`
- `app_core/services/booking_service.py`
- `app_core/services/payment_service.py`
- `app_core/services/servicios_service.py`
- `app_core/services/barberias_service.py`
- `app_core/metrics.py`
- `app_core/public_booking/steps.py`
- `requirements.txt`

---

## Columnas realmente usadas por entidad

### 1) `reservas`

#### Columnas definidas en `schema.sql`

| Columna | En schema.sql | Uso real |
|---|---:|---:|
| `id` | si | si |
| `nombre` | si | si |
| `barbero` | si | si |
| `servicio` | si | si |
| `precio` | si | si |
| `inicio` | si | si |
| `fin` | si | si |
| `barberia_id` | si | si |

#### Columnas agregadas en runtime por `app_core/bootstrap.py`

| Columna | En bootstrap runtime | Uso real |
|---|---:|---:|
| `cliente` | si | si |
| `fecha` | si | si |
| `hora` | si | si |
| `estado` | si | si |
| `pagado` | si | si |
| `monto` | si | si |
| `payment_id` | si | si |
| `updated_at` | si | si |
| `barbero_id` | si | si |

#### Columnas usadas por `app.py` en `reservas`

Uso directo o indirecto visible en consultas, inserts, filtros, UI, pagos y calendario:

- `id`
- `nombre`
- `cliente`
- `telefono`
- `email`
- `barbero`
- `barbero_id`
- `servicio`
- `precio`
- `monto`
- `pagado`
- `estado`
- `fecha`
- `hora`
- `inicio`
- `fin`
- `barberia_id`
- `payment_id` (indirecto por pagos/webhook)
- `updated_at` (indirecto por booking/webhook)

#### Columnas usadas por `webhook.py` en `reservas`

`webhook.py` hace:

- `UPDATE reservas SET pagado = %s, payment_id = %s, updated_at = %s WHERE id = %s`
- `RETURNING id, cliente, servicio, fecha`

Por lo tanto, `webhook.py` asume explicitamente:

- `id`
- `pagado`
- `payment_id`
- `updated_at`
- `cliente`
- `servicio`
- `fecha`

#### Columnas faltantes o sobrantes en `schema.sql` para `reservas`

**Faltan en `schema.sql` pero el codigo las usa:**

- `cliente`
- `fecha`
- `hora`
- `estado`
- `pagado`
- `monto`
- `payment_id`
- `updated_at`
- `barbero_id`

**Usadas en codigo pero no definidas ni en `schema.sql` ni en bootstrap runtime:**

- `telefono`
- `email`

Observacion critica:

- `app.py` contiene un insert directo desde el modal publico que intenta escribir `telefono` y `email` en `reservas`.
- Esas columnas **no existen** en `schema.sql`.
- Tampoco son creadas por `app_core/bootstrap.py`.
- Eso implica que ese flujo depende de una base alterada manualmente o esta roto contra el esquema controlado por repositorio.

#### Semantica actual observada en `reservas`

| Concepto | Implementacion actual |
|---|---|
| Cliente | duplicado entre `nombre` y `cliente` |
| Barbero | duplicado entre `barbero` (texto) y `barbero_id` (referencia logica) |
| Valor comercial | `precio` = precio del servicio |
| Valor de cobro | `monto` = valor finalmente cobrado / usado en metricas de pagos |
| Estado de pago | `pagado` boolean |
| Estado de reserva | `estado` texto libre (`activo`, `confirmada`, etc.) |
| Rango real | `inicio` / `fin` |
| Compatibilidad legacy | aun se filtra por `cliente OR nombre` y se resuelve conflicto por `barbero_id OR barbero` |

---

### 2) `usuarios`

#### Definidas en `schema.sql`

| Columna | En schema.sql | Uso real |
|---|---:|---:|
| `id` | si | si |
| `usuario` | si | si |
| `password` | si | si |
| `rol` | si | si |
| `telefono` | si | si |
| `cortes_acumulados` | si | si |
| `barberia_id` | si | si |

#### Agregadas en runtime por bootstrap

| Columna | En bootstrap runtime | Uso real |
|---|---:|---:|
| `nombre` | si | si |
| `apellido` | si | si |

#### Uso real detectado

- Autenticacion:
  - `id`, `usuario`, `password`, `rol`, `telefono`, `barberia_id`, `cortes_acumulados`
- Agenda / barberos:
  - `id`, `usuario`, `rol`, `barberia_id`
- Alta de barberos:
  - `usuario`, `password`, `rol`, `barberia_id`, `telefono`, `nombre`, `apellido`
- Fidelizacion:
  - `cortes_acumulados`

#### Inconsistencia importante

`schema.sql` define `usuarios.barberia_id INTEGER NOT NULL`, pero:

- `app_core/bootstrap.py` crea `usuarios.barberia_id INTEGER` (nullable) en runtime.
- `seed_default_data()` inserta `SUPER_ADMIN` con `barberia_id = None`.

Por lo tanto, el contrato real actual exige:

- `barberia_id` nullable para `SUPER_ADMIN`
- `barberia_id` requerido para roles de barberia (`ADMIN`, `BARBERO`, `CLIENTE`)

#### Riesgo multi-tenant

`usuario` es unico globalmente, no por barberia. Eso puede ser intencional, pero hoy es una decision estructural no documentada.

---

### 3) `barberias`

#### Definidas en `schema.sql`

| Columna | En schema.sql | Uso real |
|---|---:|---:|
| `id` | si | si |
| `nombre` | si | si |

#### Agregadas en runtime por bootstrap

| Columna | En bootstrap runtime | Uso real |
|---|---:|---:|
| `slug` | si | si |
| `telefono` | si | si |
| `email` | si | si |
| `ciudad` | si | si |
| `direccion` | si | si |
| `latitud` | si | si |
| `longitud` | si | si |
| `logo_url` | si | si |
| `color_primario` | si | si |
| `hora_apertura` | si | si |
| `hora_cierre` | si | si |
| `estado` | si | si |

#### Uso real detectado

La app publica y el marketplace usan:

- `id`
- `nombre`
- `slug`
- `telefono`
- `email`
- `ciudad`
- `direccion`
- `latitud`
- `longitud`
- `logo_url`
- `color_primario`
- `hora_apertura`
- `hora_cierre`
- `estado`

#### Inconsistencia critica de semantica

Hay un mismatch directo en el valor de `estado`:

- `bootstrap` define default `estado = 'activa'`
- `app_core/services/barberias_service.py` consulta `FROM barberias WHERE estado = 'active'`
- `create_barberia_in_db()` inserta `estado = 'activa'`

Resultado:

- el marketplace puede no devolver barberias creadas por la propia app si la base usa `activa` y la consulta filtra `active`.

---

### 4) `servicios`

#### Definidas en `schema.sql`

| Columna | En schema.sql | Uso real |
|---|---:|---:|
| `id` | si | si |
| `barberia_id` | si | si |
| `nombre` | si | si |
| `duracion_minutos` | si | si |
| `precio` | si | si |
| `descripcion` | si | si |
| `icono` | si | si |

#### Uso real detectado

- Catalogo y reserva publica:
  - `id`, `nombre`, `duracion_minutos`, `precio`, `descripcion`, `icono`, `barberia_id`
- CRUD:
  - `id`, `barberia_id`, `nombre`, `duracion_minutos`, `precio`, `descripcion`, `icono`

#### Estado actual

`servicios` es la entidad mas alineada entre schema estatico, bootstrap y codigo.

---

## Inconsistencias entre codigo y schema

### A. `schema.sql` vs runtime real

`schema.sql` define un esquema minimo. `app_core/bootstrap.py` expande en runtime:

- `barberias`: +11 columnas
- `usuarios`: +2 columnas
- `reservas`: +9 columnas
- indices adicionales sobre `reservas`

Si la app corre con `ALLOW_SCHEMA_MIGRATIONS=false` y la base solo fue creada con `schema.sql`, el codigo actual no tiene contrato suficiente para funcionar completo.

### B. `app.py` usa columnas de `reservas` no modeladas en `schema.sql`

Faltan en `schema.sql`:

- `cliente`
- `fecha`
- `hora`
- `estado`
- `pagado`
- `monto`
- `payment_id`
- `updated_at`
- `barbero_id`

### C. `app.py` usa columnas de `reservas` que no estan ni en `schema.sql` ni en bootstrap

Solo en el flujo modal:

- `telefono`
- `email`

### D. `webhook.py` depende de columnas ausentes en `schema.sql`

`webhook.py` necesita:

- `pagado`
- `payment_id`
- `updated_at`
- `cliente`
- `fecha`

Ninguna de esas columnas existe en `schema.sql`.

### E. `usuarios.barberia_id` tiene nullability inconsistente

- `schema.sql`: `NOT NULL`
- runtime / seed: se usa `NULL` para `SUPER_ADMIN`

### F. `barberias.estado` tiene semantica inconsistente

- escritura/default: `activa`
- lectura marketplace: `active`

### G. `reservas.estado` no tiene vocabulario canonico

Valores observados:

- `activo`
- `confirmada`

No hay enum ni contrato formal.

### H. `reservas.barbero` vs `reservas.barbero_id`

La app ya opera con ambas capas:

- `barbero` como snapshot / texto legacy
- `barbero_id` como referencia operativa real

Pero:

- `schema.sql` no define `barbero_id`
- bootstrap la agrega sin FK
- la restriccion `reservas_no_solapadas` del SQL estatico se basa en `barbero` texto, no `barbero_id`

Esto deja el control de agenda vulnerable a drift semantico si cambia el username del barbero.

### I. `precio` vs `monto`

Semantica actual:

- `precio`: precio del servicio
- `monto`: monto de cobro / pago / metricas

No esta documentado formalmente y parte del codigo usa fallback `monto OR precio`.

### J. Multi-tenancy parcialmente en aplicacion, no en modelo

La app endurecio bastante el uso de `barberia_id`, pero a nivel modelo aun faltan garantias:

- `reservas.barbero_id` no tiene FK a `usuarios.id`
- no hay garantia estructural de que `reservas.barbero_id` pertenezca a la misma `barberia_id`
- el webhook actualiza por `reserva_id` sin `barberia_id`; eso confia en PK global y en `external_reference`

---

## Riesgos tecnicos prioritarios

### Prioridad 1

1. **Contrato roto entre `schema.sql` y `webhook.py`**
   - El webhook escribe columnas no presentes en el schema estatico.

2. **Contrato roto entre `schema.sql` y reservas reales**
   - La app opera con `cliente`, `fecha`, `hora`, `pagado`, `monto`, `payment_id`, `updated_at`, `barbero_id`.

3. **Insert modal de reservas con columnas fantasma**
   - `telefono` y `email` en `reservas` no estan formalizadas.

### Prioridad 2

4. **`barberias.estado` inconsistente (`activa` vs `active`)**
   - Impacta marketplace y onboarding.

5. **`usuarios.barberia_id` nullability inconsistente**
   - Afecta `SUPER_ADMIN`.

6. **Solapamiento basado en `barbero` texto en `schema.sql`**
   - El contrato deberia migrar a `barbero_id` como referencia canonica.

### Prioridad 3

7. **Duplicacion semantica `nombre` / `cliente`**
8. **Duplicacion semantica `precio` / `monto`**
9. **`estado` de reserva sin catalogo canonico**
10. **Indices de `reservas` importantes solo en runtime**

---

## Esquema canonico propuesto para la siguiente fase

### `barberias` canonica propuesta

- `id`
- `nombre`
- `slug`
- `telefono`
- `email`
- `ciudad`
- `direccion`
- `latitud`
- `longitud`
- `logo_url`
- `color_primario`
- `hora_apertura`
- `hora_cierre`
- `estado`
- `created_at`
- `updated_at`

Propuesta semantica:

- usar un solo vocabulario para `estado`, por ejemplo: `active | inactive`
- normalizar codigo y seed al mismo valor

### `usuarios` canonica propuesta

- `id`
- `usuario`
- `password`
- `rol`
- `telefono`
- `nombre`
- `apellido`
- `cortes_acumulados`
- `barberia_id` nullable solo para `SUPER_ADMIN`
- `created_at`
- `updated_at`

Propuesta semantica:

- documentar si `usuario` es unico global o por barberia
- si debe seguir global, dejarlo explicito

### `servicios` canonica propuesta

- `id`
- `barberia_id`
- `nombre`
- `duracion_minutos`
- `precio`
- `descripcion`
- `icono`
- `estado` (opcional futuro)
- `created_at`
- `updated_at`

### `reservas` canonica propuesta

- `id`
- `barberia_id`
- `cliente_nombre` o mantener `cliente` como campo canonico
- `cliente_telefono` (si realmente se quiere persistir)
- `cliente_email` (si realmente se quiere persistir)
- `barbero_id`
- `barbero_nombre_snapshot` o mantener `barbero` como snapshot
- `servicio`
- `precio`
- `monto`
- `inicio`
- `fin`
- `fecha`
- `hora`
- `estado`
- `pagado`
- `payment_id`
- `created_at`
- `updated_at`

Propuesta semantica:

- elegir **un campo canonico** para cliente:
  - opcion A: `cliente`
  - opcion B: `nombre`
  - no seguir con ambos
- elegir si `telefono` y `email` de reserva se persisten o se eliminan del flujo modal
- usar `barbero_id` como referencia canonica de agenda
- mantener `barbero` solo como snapshot legible si hace falta

### Restricciones e indices canonicos propuestos

- FK `reservas.barberia_id -> barberias.id`
- FK `reservas.barbero_id -> usuarios.id` (si se mantiene `barbero_id`)
- indice `idx_reservas_barberia`
- indice `idx_reservas_barbero_id`
- indice `idx_reservas_fecha`
- indice `idx_reservas_inicio`
- indice `idx_reservas_pagado`
- exclusion / control de solapamiento basado en referencia canonica del barbero

Nota:

La restriccion de no solapamiento deberia replantearse en Fase 1.2 para depender de la identidad canonica del recurso (`barbero_id`) y no solo de `barbero` texto.

---

## Lista exacta de archivos a tocar en la Fase 1.2

Archivos minimos recomendados:

1. `schema.sql`
   - convertirlo en reflejo del contrato real minimo

2. `app_core/bootstrap.py`
   - alinear DDL runtime con el esquema canonico
   - idealmente reducir drift entre schema estatico y runtime

3. `app_core/services/booking_service.py`
   - ajustar al naming canonico de `reservas`

4. `app_core/services/payment_service.py`
   - alinear semantica `pagado` / `monto` / `payment_id`

5. `webhook.py`
   - alinear columnas reales y validar contrato de `reservas`

6. `app.py`
   - eliminar inserts directos a `reservas` que usen columnas no formalizadas
   - especialmente el flujo modal publico

7. `app_core/metrics.py`
   - alinear consultas con naming canonico de pagos y reservas

8. `app_core/services/barberias_service.py`
   - unificar semantica de `barberias.estado`

9. `app_core/services/servicios_service.py`
   - solo si la fase canonica incorpora timestamps o estado en `servicios`

10. `app_core/public_booking/steps.py`
    - ajustar al naming final si cambia el contrato de reservas/pagos

Archivos opcionales segun decision de alcance:

- `app_core/auth.py`
  - solo si se documenta o cambia el contrato de `usuarios.barberia_id`

---

## Riesgo por archivo

| Archivo | Riesgo | Motivo |
|---|---|---|
| `schema.sql` | alto | hoy no refleja el contrato real |
| `app_core/bootstrap.py` | alto | es la fuente runtime del drift |
| `webhook.py` | alto | depende de columnas ausentes en schema estatico |
| `app.py` | medio/alto | contiene al menos un insert directo de reservas fuera de la capa canonica |
| `booking_service.py` | medio | ya centraliza bastante, pero debe alinearse al esquema canonico |
| `metrics.py` | medio | depende de `pagado`, `monto`, `fecha`, `inicio` |
| `barberias_service.py` | medio | mismatch `active` vs `activa` |

---

## Recomendacion operativa para la siguiente fase

Orden sugerido para Fase 1.2:

1. Definir esquema canonico de `reservas`
2. Definir nullability y semantica real de `usuarios.barberia_id`
3. Unificar `barberias.estado`
4. Actualizar `schema.sql`
5. Actualizar `bootstrap.py`
6. Recien despues ajustar `webhook.py`, `booking_service.py`, `payment_service.py` y `app.py`

---

## Nota final

En esta fase **no se hicieron cambios funcionales** ni refactor grande.

Entregable creado:

- `PHASE1_SCHEMA_AUDIT.md`

Hallazgo mas importante para la siguiente corrida:

> El contrato real de `reservas` no esta formalizado en un solo lugar. Hoy vive repartido entre `schema.sql`, runtime DDL, `app.py`, `booking_service.py`, `payment_service.py` y `webhook.py`.
