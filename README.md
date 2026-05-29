# MJFlex — Subscription-based SaaS Backend

A production-ready SaaS backend built with Django and Django REST Framework.
Handles user authentication, subscription management, payment workflows,
and async email notifications.

---

## Tech Stack

- Python & Django
- Django REST Framework
- JWT Authentication (djangorestframework-simplejwt)
- Celery + Redis (async task processing)
- PostgreSQL (production) / SQLite (local)
- Gunicorn
- Render (deployment)

---

## Features

- JWT authentication — register, login, token refresh
- Plan management — admin can create and manage plans
- Subscription creation and tracking
- One active subscription per user enforced
- Payment flow linked to subscription
- Payment amount derived from plan — no client-side manipulation
- User-level access control — users can only manage their own data
- Duplicate payment prevention
- Async email notifications via Celery and Redis — confirmation
  email sent on subscription creation without blocking the API response

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/register/ | Register new user |
| POST | /api/token/ | Login — returns access & refresh tokens |
| POST | /api/token/refresh/ | Refresh access token |

### Subscriptions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/subscriptions/ | Create a subscription |
| GET | /api/subscriptions/list/ | List user's subscriptions |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/payments/ | Create a payment |
| POST | /api/payments/verify/ | Verify and update payment status |
| GET | /api/payments/list/ | List user's payments |
| GET | /api/me/ | Get current user info |

---

## Core Business Logic

- User must register and authenticate via JWT before accessing any endpoint
- A user can have only one active subscription at a time
- Payment is always linked to a subscription
- Payment amount is derived from the selected plan automatically
- Users cannot pay for another user's subscription
- Duplicate pending payments are prevented
- On successful payment, subscription status updates to ACTIVE automatically
- Subscription confirmation email is sent asynchronously via Celery + Redis

---

## Async Task Processing

Celery and Redis handle background tasks so API responses are never blocked:

- **Subscription confirmation email** — triggered automatically when a
  subscription is created, processed in the background by the Celery worker

---

## Database Models

**Plan** — name, code, price, duration_days, description

**Subscription** — user, plan, start_date, end_date, status, auto_renew

**Payment** — user, subscription, amount, status, transaction_id, created_at

---

## Running Locally

```bash
git clone https://github.com/munesh98/saas-backend
cd saas-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # add your environment variables
python manage.py migrate
python manage.py runserver
```

Start the Celery worker (separate terminal):
```bash
celery -A MJFlex worker --loglevel=info --pool=solo
```

---

## Environment Variables
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
REDIS_URL=your-redis-url

---

## Author

Munesh J
[github.com/munesh98](https://github.com/munesh98) |
[linkedin.com/in/muneshj](https://linkedin.com/in/muneshj)