# Auth Service

FastAPI microservice for authentication using OAuth2 + JWT.

## Features
- User registration & login (OAuth2 Password Flow)
- JWT access tokens + refresh token rotation
- Password hashing with bcrypt
- Token verification endpoint (for other services)
- Role-based access control (admin / manager / user)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (OAuth2 form) |
| POST | `/api/v1/auth/logout` | Revoke refresh token |
| POST | `/api/v1/auth/verify-token` | Verify access token |
| GET | `/api/v1/auth/me` | Get current user |
| PUT | `/api/v1/auth/me/change-password` | Change password |
| GET | `/health` | Health check |

## Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env
cp .env .env.local
# Edit DATABASE_URL and SECRET_KEY

# 4. Run
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async URL (`postgresql+asyncpg://...`) |
| `SECRET_KEY` | JWT signing key (min 32 chars) |
| `ALGORITHM` | JWT algorithm (default: HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL |