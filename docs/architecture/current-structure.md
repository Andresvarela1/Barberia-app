# Current Structure

This document captures the current repository layout before moving any
business logic. It is intentionally brief and based only on files visible in
the repo at this point.

## Runtime Entry Points

- `app.py`: main Streamlit application. Current imports show Streamlit,
  `streamlit_calendar`, environment loading, bcrypt, psycopg2, pandas,
  `whatsapp.enviar_whatsapp`, and many UI helpers from `design_system.py`.
  The README describes this file as covering customer, barber, admin and super
  admin flows, including reservations, agenda, payments and public booking.
- `webhook.py`: FastAPI server for MercadoPago payment notifications. It loads
  environment variables, configures logging to `webhook.log`, creates a
  psycopg2 connection pool and exposes webhook request/response models.
- `whatsapp.py`: WhatsApp/Twilio integration helper imported by `app.py`.

## UI And Styling

- `design_system.py`: centralized Streamlit design system with color,
  typography, spacing and render helper definitions.
- `components/ui_loader.py`: CSS loader for Streamlit. It loads styles from the
  `styles/` directory in a defined order.
- `components/__init__.py`: existing package marker for shared UI components.
- `styles/`: CSS modules currently include `base.css`, `sidebar.css`,
  `calendar.css`, `forms.css`, `cards.css`, `booking.css` and `theme.css`.

## Data And Setup Files

- `schema.sql`: database schema file.
- `seed_barberias.py` and `seed_servicios.py`: seed scripts.
- Local database files such as `*.db` and `*.db-journal` exist in the workspace
  and are now ignored by `.gitignore`.
- `requirements.txt`: Python dependencies for Streamlit, PostgreSQL, Twilio,
  MercadoPago, FastAPI, Uvicorn, geopy and pandas.

## Documentation And QA Artifacts

- `README.md`: project overview, setup, environment variables and local run
  commands.
- `docs/`: existing runtime/QA documentation.
- Root-level implementation, audit and upgrade notes document prior UI,
  encoding and deployment work.
- `qa_screenshots/` and log files are runtime artifacts and are now ignored.

## Refactor Staging Packages

These packages were added as empty placeholders only. No logic has been moved
into them yet:

- `app_core/db`
- `app_core/security`
- `app_core/services`
- `app_core/integrations`
- `app_core/public_booking`

Intended future ownership:

- `app_core/db`: connection and persistence boundaries.
- `app_core/security`: authentication, authorization and credential helpers.
- `app_core/services`: application use cases and orchestration.
- `app_core/integrations`: MercadoPago, Twilio and other external providers.
- `app_core/public_booking`: public booking flow extraction target.

## Current Constraint

No SQL, visible text, app behavior or existing business logic has been changed
as part of this preparation step.
