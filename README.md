# Event Management System (Flask + MongoDB)

First mini-project by a 5th-semester CSE student. Building this taught me end‑to‑end web development: backend APIs, templates, persistence, payments, and deployment hygiene. It was a great experience converting requirements into a working app and wiring real tools (MongoDB, PDFs, payments).

## Overview
A modern Flask application to plan and manage events:
- Role-based access: User, Admin, SubAdmin, SuperAdmin
- Modules: Hotels (venues), Catering (buffets), Vendors, Bookings
- Payments: Razorpay order + signature verification (optional)
- Receipts: PDF (paid) or Proforma (unpaid) via xhtml2pdf
- Admin tools: Import/Export MongoDB collections as JSON (data/*.json)
- Bootstrap UI

## Stack
- Backend: Flask 3, PyMongo 4 (MongoDB)
- Templates: Jinja2, Bootstrap 4
- Utilities: xhtml2pdf, Razorpay SDK

## Features
- Auth and sessions with role-aware navigation
- CRUD for venues, catering, vendors, bookings
- Secure server-side total calculation for bookings
- PDF receipt download
- Admin JSON import/export (backup/restore)

## Screenshots
- Home: Carousel with venue and buffet images
- Admin: Users, Hotels, Catering, Vendors, Bookings
- Booking: Create/Edit, status, receipt

## Requirements
- Python 3.9+
- MongoDB (mongod + mongosh)

## Quick Start (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```
Open http://127.0.0.1:5000

## MongoDB Config
- Defaults: `MONGO_URI=mongodb://localhost:27017`, `MONGO_DB_NAME=event_management`
- Set via environment variables if needed.

### Seed Examples
```powershell
mongosh --quiet --eval "db = db.getSiblingDB('event_management'); db.events.insertMany([{eventname:'Wedding'},{eventname:'Birthday Party'}])"
mongosh --quiet --eval "db = db.getSiblingDB('event_management'); db.users.insertOne({email:'admin@example.com', first_name:'Admin', last_name:'User', password:'admin123', role:'Admin'})"
```

## Import/Export JSON (Admin)
- Export: POST `/admin/export-json` → writes to `data/*.json`
- Import: POST `/admin/import-json` → loads from `data/*.json`

## Project Structure
app/
init.py # Flask app + Mongo client
routes/ # Blueprints (user, booking, hotel, vendor, catering, payment, receipt)
templates/ # Jinja2 templates
static/ # css, js, images
scripts/
export_to_json.py
import_from_json.py
data/ # exported JSON snapshots
run.py # entry point
requirements.txt
README.md

## Notes
- SQLAlchemy was removed; all persistence uses MongoDB.
- Images: `app/static/images/Catering.png`, `Wedding.png` used on home/buffet.
- For production, run behind a WSGI server and configure secrets via env vars.

## Roadmap
- Email notifications
- Advanced payments/webhooks
- Pagination + search
- Tests and CI

## License
Educational project; use freely for learning.
