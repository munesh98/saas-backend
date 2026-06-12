# MJFlex — Subscription-based SaaS Backend

A production-ready SaaS backend built with Django and Django REST Framework.
Handles user authentication, subscription lifecycle management, payment 
processing via Razorpay, automated email notifications, and background 
task scheduling.

---

## Tech Stack

- Python & Django 6
- Django REST Framework
- JWT Authentication (djangorestframework-simplejwt)
- Celery + Redis (async task processing & scheduling)
- Razorpay (payment gateway)
- PostgreSQL (production) / SQLite (local)
- Gunicorn
- drf-spectacular (API documentation)

---

## Live Demo

**API Base URL:** https://mjflex-backend.onrender.com

**Swagger UI:** https://mjflex-backend.onrender.com/api/docs/

**Plans endpoint (public):** https://mjflex-backend.onrender.com/api/plans/

---

## Features

**Authentication**
- Custom User model with email verification
- JWT authentication — register, login, token refresh
- Email verification required before login
- Password reset via email link
- Unverified users blocked at login

**Subscription Management**
- Plan listing — public endpoint
- Subscription creation with automatic date calculation
- One active/pending subscription per user enforced
- Subscription cancellation — access retained until billing period ends
- Auto renewal logic via Celery Beat
- Auto expiry of subscriptions at end date

**Payment Processing**
- Payment creation linked to subscription
- Razorpay order creation
- Webhook endpoint for payment confirmation
- Payment amount derived from plan — no client-side manipulation
- User-level access control — users can only manage their own payments
- Duplicate payment prevention

**Async Task Processing (Celery + Redis)**
- Subscription confirmation email on creation
- Renewal reminder email 24 hours before expiry
- Auto renewal of subscriptions via Celery Beat
- Auto expiry of subscriptions via Celery Beat
- Password reset email
- Email verification email

**API Quality**
- Swagger UI documentation — /api/docs/
- Pagination on list endpoints
- Rate limiting — 20 req/hour anonymous, 100 req/hour authenticated
- 19 automated tests — accounts, subscriptions, payments

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/register/ | Register new user |
| GET | /api/verify-email/ | Verify email address |
| POST | /api/token/ | Login — returns access & refresh tokens |
| POST | /api/token/refresh/ | Refresh access token |
| POST | /api/password-reset-email/ | Request password reset link |
| POST | /api/password-update/ | Reset password with token |

### Plans
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/plans/ | List all available plans (public) |

### Subscriptions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/subscriptions/ | Create a subscription |
| GET | /api/subscriptions/list/ | List user's subscriptions |
| PATCH | /api/subscriptions/{id}/cancel/ | Cancel a subscription |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/payments/ | Create a payment |
| POST | /api/payments/create-order/ | Create Razorpay order |
| POST | /api/payments/verify/ | Manual payment verification |
| POST | /api/payments/webhook/ | Razorpay webhook endpoint |
| GET | /api/payments/list/ | List user's payments |
| GET | /api/me/ | Get current user info |

---

## Celery Beat Schedule

All tasks run daily at midnight:

- `auto_expire_subscriptions` — expires/cancels subscriptions past end date
- `send_renewal_reminder_emails` — sends reminder 24hrs before expiry
- `auto_renewal_subscriptions` — auto renews subscriptions with auto_renew=True

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
python manage.py createsuperuser
python manage.py runserver
```

Start Celery worker (separate terminal):
```bash
celery -A MJFlex worker --loglevel=info --pool=solo
```

Start Celery Beat scheduler (separate terminal):
```bash
celery -A MJFlex beat --loglevel=info
```

---

## Running Tests

```bash
python manage.py test
```

19 tests covering authentication, subscription management, and payment flows.

---

## API Documentation

Swagger UI available at:
- **Local:** http://127.0.0.1:8000/api/docs/
- **Production:** https://mjflex-backend.onrender.com/api/docs/

---

## Environment Variables
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
REDIS_URL=your-redis-url
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

---

## Author

Munesh J
[github.com/munesh98](https://github.com/munesh98) |
[linkedin.com/in/muneshj](https://linkedin.com/in/muneshj)