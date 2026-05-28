# QA Runtime Template

Plantilla manual para validar la app en runtime por rol, sin modificar código.

## Instrucciones De Uso
- Ejecutar cada caso con evidencia visible.
- Registrar `OK`, `WARN` o `FAIL`.
- Si un caso falla, indicar severidad y bloquear o no la liberación.
- Adjuntar captura de pantalla, mensaje visible y contexto mínimo.

## Escala De Severidad
- `Crítica`: impide usar el flujo principal o compromete datos/sesión.
- `Alta`: rompe una función importante del rol, pero no toda la app.
- `Media`: el flujo funciona parcialmente con errores visibles o inconsistencias.
- `Baja`: problema visual, textual o menor, sin impacto funcional fuerte.

## Plantilla De Registro
```md
- Fecha:
- Entorno:
- Rol:
- Caso:
- Resultado: OK / WARN / FAIL
- Severidad si falla: Crítica / Alta / Media / Baja
- Evidencia capturada:
- Observaciones:
```

---

## 1. Cliente

### Caso 1.1: Acceso al flujo de reserva
- Precondiciones:
  - La app está accesible localmente o en entorno de prueba.
  - Existe al menos una barbería visible.
- Pasos:
  1. Abrir la app.
  2. Entrar al flujo público o iniciar sesión como cliente.
  3. Intentar avanzar hacia la reserva.
- Resultado esperado:
  - El cliente puede entrar al flujo sin traceback.
  - La pantalla muestra opciones de reserva o navegación clara.
- Evidencia a capturar:
  - Pantalla inicial del flujo.
  - Cualquier mensaje visible.
- Severidad si falla:
  - `Alta`

### Caso 1.2: Selección de barbería
- Precondiciones:
  - Existen barberías configuradas en base de datos.
- Pasos:
  1. Abrir la vista donde se listan barberías.
  2. Seleccionar una barbería.
  3. Verificar que el contexto cambia a esa barbería.
- Resultado esperado:
  - La barbería seleccionada se refleja en el flujo siguiente.
  - No se muestran datos cruzados de otra barbería.
- Evidencia a capturar:
  - Pantalla antes y después de seleccionar barbería.
- Severidad si falla:
  - `Crítica`

### Caso 1.3: Selección de barbero y servicio
- Precondiciones:
  - La barbería seleccionada tiene barberos y servicios activos.
- Pasos:
  1. Elegir un barbero.
  2. Elegir un servicio.
  3. Confirmar que duración y precio se muestran correctamente.
- Resultado esperado:
  - El selector funciona sin errores.
  - Los datos del servicio son consistentes.
- Evidencia a capturar:
  - Pantalla con barbero y servicio seleccionados.
- Severidad si falla:
  - `Alta`

### Caso 1.4: Selección de fecha y hora
- Precondiciones:
  - Existen horarios disponibles para el barbero elegido.
- Pasos:
  1. Seleccionar una fecha.
  2. Seleccionar una hora disponible.
  3. Intentar avanzar.
- Resultado esperado:
  - Solo se muestran horarios válidos.
  - No aparecen errores de calendario o estado.
- Evidencia a capturar:
  - Pantalla de fecha y hora.
- Severidad si falla:
  - `Alta`

### Caso 1.5: Confirmación de reserva
- Precondiciones:
  - El cliente completó nombre, teléfono y campos obligatorios.
- Pasos:
  1. Revisar el resumen.
  2. Confirmar la reserva.
  3. Observar mensaje final.
- Resultado esperado:
  - La reserva se crea correctamente.
  - La app muestra confirmación clara.
  - Si hay pago o WhatsApp, el flujo no se rompe aunque falle una integración.
- Evidencia a capturar:
  - Resumen previo.
  - Mensaje final de éxito o error controlado.
- Severidad si falla:
  - `Crítica`

### Caso 1.6: Estado de sesión del cliente
- Precondiciones:
  - El cliente inició sesión.
- Pasos:
  1. Navegar entre secciones.
  2. Recargar la página.
  3. Cerrar sesión.
- Resultado esperado:
  - La sesión se mantiene donde corresponde.
  - Al cerrar sesión, desaparece el acceso al panel protegido.
- Evidencia a capturar:
  - Estado antes y después de recargar.
  - Estado tras cerrar sesión.
- Severidad si falla:
  - `Alta`

### Caso 1.7: Textos visibles corruptos
- Precondiciones:
  - La app carga correctamente.
- Pasos:
  1. Recorrer home, marketplace y flujo de reserva.
  2. Buscar textos con `Ã`, `â`, `�`, `ðŸ`, `Â`.
- Resultado esperado:
  - No hay textos corruptos visibles o son mínimos y no bloqueantes.
- Evidencia a capturar:
  - Captura exacta del texto corrupto.
  - Pantalla y sección donde aparece.
- Severidad si falla:
  - `Baja` o `Media`, según impacto visual

---

## 2. Barbero

### Caso 2.1: Login de barbero
- Precondiciones:
  - Existe un usuario con rol `barbero`.
- Pasos:
  1. Ir a login.
  2. Ingresar credenciales válidas.
  3. Acceder al panel.
- Resultado esperado:
  - El login funciona.
  - El usuario entra al panel correcto.
- Evidencia a capturar:
  - Pantalla de login.
  - Pantalla del panel de barbero.
- Severidad si falla:
  - `Crítica`

### Caso 2.2: Visualización de agenda propia
- Precondiciones:
  - Existen reservas del barbero en su barbería.
- Pasos:
  1. Abrir agenda o calendario.
  2. Verificar eventos visibles.
- Resultado esperado:
  - El barbero ve solo sus reservas o su contexto permitido.
  - No ve reservas de otras barberías.
- Evidencia a capturar:
  - Vista calendario o listado.
- Severidad si falla:
  - `Crítica`

### Caso 2.3: Bloqueo de horario
- Precondiciones:
  - La barbería permite bloquear horarios.
- Pasos:
  1. Seleccionar un tramo libre.
  2. Crear bloqueo.
  3. Volver a abrir la agenda.
- Resultado esperado:
  - El bloqueo queda registrado como ocupado.
  - Ese tramo ya no puede reservarse como disponible.
- Evidencia a capturar:
  - Antes y después del bloqueo.
- Severidad si falla:
  - `Alta`

### Caso 2.4: Edición o revisión de reserva
- Precondiciones:
  - Existe al menos una reserva editable o visible.
- Pasos:
  1. Abrir una reserva desde agenda.
  2. Revisar detalles.
  3. Guardar cambios si la UI lo permite.
- Resultado esperado:
  - La app muestra detalles correctos.
  - Si se puede editar, no genera error ni solapa datos inválidos.
- Evidencia a capturar:
  - Modal o panel de detalle.
- Severidad si falla:
  - `Alta`

### Caso 2.5: Estado de sesión del barbero
- Precondiciones:
  - El barbero inició sesión.
- Pasos:
  1. Navegar entre vistas del panel.
  2. Recargar.
  3. Cerrar sesión.
- Resultado esperado:
  - La sesión se conserva.
  - Al salir, ya no se puede acceder al panel sin login.
- Evidencia a capturar:
  - Panel antes y después de recarga.
- Severidad si falla:
  - `Alta`

---

## 3. Admin

### Caso 3.1: Login de admin
- Precondiciones:
  - Existe un usuario con rol `admin`.
- Pasos:
  1. Ir a login.
  2. Ingresar credenciales válidas.
  3. Acceder al panel administrativo.
- Resultado esperado:
  - El admin entra al panel correcto.
- Evidencia a capturar:
  - Vista del panel administrativo.
- Severidad si falla:
  - `Crítica`

### Caso 3.2: Visualización de reservas de su barbería
- Precondiciones:
  - Existen reservas en la barbería del admin.
- Pasos:
  1. Abrir agenda del admin.
  2. Revisar calendario y listado.
- Resultado esperado:
  - Solo se muestran datos de la barbería asociada.
  - No hay mezcla con otras barberías.
- Evidencia a capturar:
  - Calendario y listado.
- Severidad si falla:
  - `Crítica`

### Caso 3.3: Gestión de barberos
- Precondiciones:
  - El módulo de gestión de barberos está visible para admin.
- Pasos:
  1. Abrir sección de barberos.
  2. Revisar lista actual.
  3. Crear un barbero si el flujo está disponible.
- Resultado esperado:
  - La sección carga.
  - La lista refleja datos reales.
  - La creación no rompe el panel.
- Evidencia a capturar:
  - Listado.
  - Formulario y resultado si se crea un barbero.
- Severidad si falla:
  - `Alta`

### Caso 3.4: Métricas e ingresos
- Precondiciones:
  - Existen reservas o pagos registrados.
- Pasos:
  1. Abrir sección de métricas.
  2. Revisar ingresos, reservas y totales.
- Resultado esperado:
  - Las métricas cargan sin error.
  - Los valores son coherentes con la barbería activa.
- Evidencia a capturar:
  - Tarjetas, métricas o tablas visibles.
- Severidad si falla:
  - `Media` o `Alta`, según impacto operativo

### Caso 3.5: Manejo de error sin base de datos
- Precondiciones:
  - Entorno de prueba sin `DATABASE_URL` ni `SUPABASE_DB_URL`.
- Pasos:
  1. Abrir la app.
  2. Intentar acceder al panel admin.
- Resultado esperado:
  - La app muestra error controlado.
  - No aparece traceback crudo.
- Evidencia a capturar:
  - Mensaje completo visible.
- Severidad si falla:
  - `Alta`

---

## 4. Super Admin

### Caso 4.1: Login de super admin
- Precondiciones:
  - Existe un usuario con rol `SUPER_ADMIN` o equivalente activo.
- Pasos:
  1. Ir a login.
  2. Ingresar credenciales válidas.
  3. Entrar al panel global.
- Resultado esperado:
  - Acceso correcto al panel global.
- Evidencia a capturar:
  - Pantalla principal del panel global.
- Severidad si falla:
  - `Crítica`

### Caso 4.2: Cambio de contexto entre barberías
- Precondiciones:
  - Existen varias barberías disponibles.
- Pasos:
  1. Seleccionar una barbería desde la barra lateral o selector.
  2. Revisar agenda, métricas y usuarios.
  3. Cambiar a otra barbería.
- Resultado esperado:
  - El contexto cambia correctamente.
  - Los datos se actualizan según la barbería elegida.
- Evidencia a capturar:
  - Captura antes y después del cambio de contexto.
- Severidad si falla:
  - `Crítica`

### Caso 4.3: Vista global de agenda
- Precondiciones:
  - Hay reservas en una o más barberías.
- Pasos:
  1. Abrir agenda global.
  2. Validar calendario y listado.
- Resultado esperado:
  - La vista global carga sin errores.
  - Los datos son consistentes con el contexto seleccionado o global permitido.
- Evidencia a capturar:
  - Agenda global.
- Severidad si falla:
  - `Alta`

### Caso 4.4: Métricas globales
- Precondiciones:
  - Existen barberías, usuarios y reservas cargadas.
- Pasos:
  1. Abrir panel de métricas globales.
  2. Revisar totales de barberías, usuarios, reservas e ingresos.
- Resultado esperado:
  - Las métricas se renderizan sin error.
  - Los datos no muestran cruces inconsistentes.
- Evidencia a capturar:
  - Captura de métricas globales.
- Severidad si falla:
  - `Alta`

### Caso 4.5: Estado de sesión y permisos globales
- Precondiciones:
  - El super admin inició sesión.
- Pasos:
  1. Navegar entre secciones globales.
  2. Cambiar de barbería activa.
  3. Recargar.
  4. Cerrar sesión.
- Resultado esperado:
  - La sesión conserva el contexto correctamente.
  - Los permisos siguen siendo de super admin.
  - Al cerrar sesión, se pierde acceso al panel global.
- Evidencia a capturar:
  - Estado antes y después de recargar.
  - Estado tras cerrar sesión.
- Severidad si falla:
  - `Crítica`

---

## Criterios De Cierre
- `Cliente`: debe poder reservar sin bloqueo funcional.
- `Barbero`: debe poder ver y gestionar agenda propia.
- `Admin`: debe poder administrar su barbería sin ver datos ajenos.
- `Super Admin`: debe poder supervisar contexto global y cambiar barbería activa.
- No deben aparecer tracebacks en UI.
- Los textos corruptos visibles deben quedar registrados como deuda si no bloquean.
