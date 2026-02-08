# Hospital Management System

A Django-based Hospital Management System with role-based access control, OPD billing, pathology billing, and commission tracking.

## Features

- Role-based access for Super Admin, Admin, Receptionist, Doctor, Nurse, Pathologist, Pharmacist.
- Patient registration and tracking.
- OPD and Pathology billing with invoice numbering format `YYYYMM-XXXX`.
- Payment status tracking (paid/partial/due).
- Commission records for doctors, pathologists, and pharmacists.
- PDF invoice generation via ReportLab.
- JWT-enabled API authentication (DRF + SimpleJWT) and Django Admin UI.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

## Default Demo Credentials

- Username: `superadmin`
- Password: `admin123`

## Structure

- `hospital_mgmt/` Django project
- `hospital_mgmt/core/` Core app with models, views, billing logic
- `docs/` Database schema and ER diagram

## API Endpoints

- `POST /api/token/` (obtain JWT)
- `POST /api/token/refresh/`
- `GET /api/patients/`
- `GET /api/opd-bills/`
- `GET /api/pathology-bills/`

## Deployment

- Configure database env vars: `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
- Use `DJANGO_SECRET_KEY` and set `DJANGO_DEBUG=false` in production.
- Configure `ALLOWED_HOSTS` and static/media storage.
