# Vivekanand Library Management

A Flask-based starter project for a library management system with:
- Home page
- Student registration
- Student login with OTP-based verification
- Admin login and dashboard
- Student dashboard with fee and payment sections
- Basic database models for students, admin, payment, and AutoPay status

## Features included
- Role-based access: Student and Admin
- OTP verification flow for prototype login
- SQLite database setup with SQLAlchemy
- Basic dashboard pages
- Security-first layout for future enhancements
- Ready for adding real payment gateway and OTP integration

## Tech stack
- Python 3
- Flask
- Flask-SQLAlchemy
- Bootstrap-inspired CSS

## Run locally

1. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Start the app
   ```bash
   python run.py
   ```

4. Open in browser
   ```text
   http://127.0.0.1:5000/
   ```

## Default admin credentials
```text
Username: admin
Password: admin123
```

## OTP flow for demo
When you log in, the app validates the username/mobile and password, then generates a demo OTP and asks you to verify it. This is a prototype OTP flow for development and demonstration.

This is a starter prototype for the library system; you can extend it with real SMS/OTP providers, payment gateway integration, audits, seat protection, and AutoPay features.
