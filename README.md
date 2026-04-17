# MJFlex Subscription System

This is a backend project built using Django and Django REST Framework that handles subscription and payment workflows similar to a SaaS product.

The system allows users to subscribe to plans, make payments, and track their subscription status.

---

## Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL (production)
* SQLite (local)
* Gunicorn
* Render (deployment)

---

## Features

* User authentication (basic)
* Plan management (admin can create/update)
* Subscription creation and tracking
* Prevent multiple active subscriptions per user
* Payment creation linked to subscription
* Prevent duplicate payments
* Status handling (PENDING, SUCCESS, FAILURE)

---

## API Overview

### Plans

* GET /api/plans/
* POST /api/plans/ (admin)

### Subscriptions

* POST /api/subscriptions/
* GET /api/subscriptions/

### Payments

* POST /api/payments/
* GET /api/payments/

---

## Core Logic

* A user can have only one active subscription at a time
* Payment is always linked to a subscription
* Payment amount is derived from selected plan
* User cannot pay for another user’s subscription
* Duplicate successful payments are prevented

---

## Database Models

Plan:

* name
* code
* price
* duration_days
* description

Subscription:

* user (FK)
* plan (FK)
* start_date
* end_date
* status
* auto_renew

Payment:

* user (FK)
* subscription (FK)
* amount
* status
* transaction_id
* created_at

---

## Running Locally

```bash
git clone <repo-url>
cd project-folder

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

---

## Deployment

The project is deployed on Render using:

* Gunicorn for serving
* PostgreSQL database
* Environment variables for configuration

Live URL:
https://saas-backend-4nsq.onrender.com/

---

## Notes

* Environment variables are used for SECRET_KEY and DATABASE_URL
* Local setup uses PostgreSQL (configured manually)
* Basic validation is handled in serializers and views

---

## Future Improvements

* JWT authentication
* Payment gateway integration
* Better error handling and logging
* Rate limiting

---

## Author

Munesh J
