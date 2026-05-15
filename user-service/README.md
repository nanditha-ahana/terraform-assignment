# User Service

FastAPI microservice for user profile and account management using OAuth2 + JWT.

## Features
- User profile management
- Admin user management
- Role & account status updates
- Pagination & filtering
- OAuth2 JWT authentication
- PostgreSQL + SQLAlchemy

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/users/` | List users |
| POST | `/api/v1/users/` | Create user |
| GET | `/api/v1/users/me` | Get current user profile |
| POST | `/api/v1/users/me` | Update current user profile |
| GET | `/api/v1/users/{user_id}` | Get user by ID |
| POST | `/api/v1/users/{user_id}` | Delete user |
| POST | `/api/v1/users/update-user` | Admin update user |
| POST | `/api/v1/users/{user_id}/deactivate` | Deactivate user |
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
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL database URL |
| `SECRET_KEY` | JWT signing key |
| `ALGORITHM` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry |
| `AUTH_SERVICE_URL` | Auth service URL |