# Varnam Aesthetics

The e-commerce storefront and admin backend for Varnam Aesthetics, a jewellery/ornaments brand. Customers browse products, add to cart, and check out via direct UPI payment (QR code / GPay / PhonePe deep links, with a payment-screenshot upload for confirmation). No payment gateway or transaction fees involved.

## Features

- **Storefront** — home, shop, product detail, cart, checkout, contact, and custom-order-request pages
- **UPI checkout flow** — QR code + deep links to GPay/PhonePe, screenshot upload for order confirmation, order notification emails
- **Admin dashboard** — hidden behind an "Admin Portal" link in the footer; manage products, orders, and payment confirmations
- **Auth** — Flask-Login + bcrypt-hashed passwords, admin/customer roles

## Stack

- Flask + Flask-SQLAlchemy + Flask-Login + Flask-Bcrypt
- PostgreSQL in production (via Supabase), SQLite for local dev
- Supabase Storage for product images and payment screenshots
- Deployed as a Vercel serverless Flask app

## Documentation

- [`local_development_guide.md`](local_development_guide.md) — local setup, environment variables, running with SQLite
- [`hosting_guide.md`](hosting_guide.md) — Supabase + Vercel deployment
- [`client_walkthrough.md`](client_walkthrough.md) — plain-language guide to the storefront and admin flow, written for the store owner

## Quick start

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # fill in your own DB / Supabase / SMTP credentials — never commit real ones
python init_db.py
python -c "from api.index import create_app; create_app().run(debug=True)"
```

Visit `http://127.0.0.1:5000`.

> **Note:** this repo is public. Keep real credentials (DB URIs, Supabase keys, SMTP passwords, customer UPI IDs/emails) out of committed files — use environment variables and `.env` (already git-ignored) instead. See `.env.example` for what's needed.
