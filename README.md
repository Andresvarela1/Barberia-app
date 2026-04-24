# Barbería App

Aplicación SaaS de barbería construida principalmente con Streamlit. El proyecto combina reservas, autenticación por roles, agenda interactiva, pagos, notificaciones por WhatsApp y soporte multi-barbería.

Actualmente el repositorio incluye:
- App principal en Streamlit para clientes, barberos, admins y super admin.
- Base de datos PostgreSQL/Supabase.
- Webhook FastAPI para procesar pagos de MercadoPago.
- Sistema visual propio con CSS modular y `design_system.py`.

## Stack

- Python 3.11+ recomendado
- Streamlit
- PostgreSQL / Supabase
- `psycopg2-binary`
- `streamlit-calendar`
- Twilio
- MercadoPago SDK
- FastAPI + Uvicorn
- `bcrypt`
- `python-dotenv`
- `requests`
- `geopy`
- `pandas`

## Instalación

1. Clona el repositorio.
2. Crea un entorno virtual.
3. Instala dependencias.
4. Configura variables de entorno.
5. Ejecuta la app.

Ejemplo en Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Variables De Entorno

El proyecto carga variables desde `.env` cuando existe.

Variables principales:

```env
DATABASE_URL=
SUPABASE_DB_URL=

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_NUMBER=

MERCADOPAGO_ACCESS_TOKEN=
MERCADOPAGO_SUCCESS_URL=
MERCADOPAGO_FAILURE_URL=
MERCADOPAGO_PENDING_URL=

WEBHOOK_SECRET=
```

Notas:
- Usa `DATABASE_URL` como variable principal de base de datos.
- `SUPABASE_DB_URL` funciona como fallback en varios scripts.
- Si no configuras Twilio o MercadoPago, la app puede seguir levantando parcialmente, pero esas funciones no estarán completas.

## Cómo Correr La App Localmente

App principal:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

Webhook de MercadoPago:

```powershell
.venv\Scripts\python.exe webhook.py
```

Alternativa con Uvicorn:

```powershell
uvicorn webhook:app --reload --host 0.0.0.0 --port 8000
```

Verificación rápida sin dejar procesos vivos:

```powershell
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = (Resolve-Path ".\.venv\Scripts\python.exe").Path
$psi.Arguments = "-m streamlit run app.py --server.headless true --server.port 8501"
$psi.WorkingDirectory = (Get-Location).Path
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.CreateNoWindow = $true

$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $psi
$null = $proc.Start()

Start-Sleep -Seconds 10

if (-not $proc.HasExited) {
    $proc.Kill()
    $proc.WaitForExit()
    "STREAMLIT_STARTED_OK"
} else {
    "STREAMLIT_EXITED_EARLY"
}

$proc.StandardOutput.ReadToEnd()
$proc.StandardError.ReadToEnd()
```

## Base De Datos

El esquema PostgreSQL base está en:

- [schema.sql](/C:/Users/Joanb/OneDrive/Escritorio/barberia_app/schema.sql)

Incluye tablas principales:
- `barberias`
- `usuarios`
- `reservas`
- `servicios`

Importante:
- La app también contiene lógica de inicialización/migración defensiva dentro de `app.py`.
- Para entornos más controlados, conviene aplicar `schema.sql` antes de levantar la app.

## Estructura Del Proyecto

```text
barberia_app/
├── app.py
├── webhook.py
├── whatsapp.py
├── design_system.py
├── schema.sql
├── requirements.txt
├── .env
├── components/
│   ├── __init__.py
│   └── ui_loader.py
├── styles/
│   ├── base.css
│   ├── booking.css
│   ├── calendar.css
│   ├── cards.css
│   ├── forms.css
│   └── sidebar.css
├── seed_barberias.py
├── seed_servicios.py
└── docs y archivos de soporte varios
```

## Archivo Principal De Entrada

La app principal entra por:

- [app.py](/C:/Users/Joanb/OneDrive/Escritorio/barberia_app/app.py)

El webhook separado entra por:

- [webhook.py](/C:/Users/Joanb/OneDrive/Escritorio/barberia_app/webhook.py)

## Flujo Recomendado De Desarrollo

1. Activa el entorno virtual.
2. Configura `.env` con una base PostgreSQL/Supabase de desarrollo.
3. Aplica `schema.sql` o deja que la app complete parte de la inicialización.
4. Corre `streamlit run app.py`.
5. Si trabajas pagos, corre también `webhook.py`.
6. Valida cambios manualmente en:
   - login
   - reservas
   - agenda
   - dashboards por rol
   - pagos
   - WhatsApp
7. Antes de cambios grandes, revisa los helpers existentes en `app.py` para evitar duplicar lógica.

## Dependencias Críticas

- `streamlit`: runtime principal de UI.
- `psycopg2-binary`: conexión a PostgreSQL/Supabase.
- `bcrypt`: hashing de contraseñas.
- `streamlit-calendar`: agenda y calendario interactivo.
- `mercadopago`: generación de links y pagos.
- `twilio`: envío de WhatsApp.
- `fastapi` y `uvicorn`: webhook backend.

## Tests, Lint Y Build

Estado actual del repositorio:

- No hay suite formal de tests del proyecto.
- No hay configuración de linting visible del proyecto (`ruff`, `flake8`, `mypy`, etc.).
- No hay pipeline de build separada.
- La validación actual depende principalmente de pruebas manuales y logs.

## Troubleshooting

### La app muestra que no hay base de datos

Verifica:
- `DATABASE_URL`
- `SUPABASE_DB_URL`
- acceso de red a PostgreSQL/Supabase
- credenciales correctas

### MercadoPago no funciona

Verifica:
- `MERCADOPAGO_ACCESS_TOKEN`
- URLs de retorno
- que `webhook.py` esté corriendo si el flujo depende de confirmación asíncrona

### Twilio no envía mensajes

Verifica:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_NUMBER`
- formato del número destino con prefijo internacional

### Problemas de caracteres raros o emojis corruptos

El repo tiene historial de reparaciones de UTF-8. Si ves mojibake:
- revisa codificación UTF-8 del archivo
- evita editar con herramientas que cambien encoding
- compara con backups si el problema reaparece

### Git falla al crear ramas o escribir refs

Si el repo está dentro de OneDrive, puede haber bloqueos temporales sobre `.git`. Reintenta o pausa sincronización si vuelve a ocurrir.

## Scripts Útiles

Seeds:

```powershell
python seed_barberias.py
python seed_servicios.py
```

## Observaciones

- `app.py` concentra gran parte de la lógica del sistema.
- Hay varios archivos de documentación y backup en la raíz que sirven como historial técnico.
- Existen archivos SQLite antiguos en el repo, pero el flujo actual apunta a PostgreSQL/Supabase.
