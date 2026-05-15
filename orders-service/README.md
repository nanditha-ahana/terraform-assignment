# Inventory Service

FastAPI microservice for product catalog and inventory management using OAuth2 + JWT.

## Features
- Product & category management
- Inventory tracking
- Stock reservation & release
- Low stock monitoring
- Stock movement audit logs
- PostgreSQL + SQLAlchemy

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/products/categories` | List categories |
| POST | `/api/v1/products/categories` | Create category |
| POST | `/api/v1/products/categories-update` | Update category |
| POST | `/api/v1/products/categories-delete` | Delete category |
| GET | `/api/v1/products/list-products` | List products |
| POST | `/api/v1/products/products` | Create product |
| GET | `/api/v1/products/get-product-by-id` | Get product |
| POST | `/api/v1/products/update-product` | Update product |
| POST | `/api/v1/products/delete-product` | Delete product |
| GET | `/api/v1/inventory/low-stock` | Get low stock products |
| GET | `/api/v1/inventory/products` | Get inventory details |
| POST | `/api/v1/inventory/products-adjust` | Adjust stock |
| POST | `/api/v1/inventory/reserve` | Reserve stock |
| POST | `/api/v1/inventory/release` | Release stock |
| GET | `/api/v1/inventory/movements` | Stock movement history |
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
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL database URL |
| `SECRET_KEY` | JWT signing key |
| `ALGORITHM` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry |
| `AUTH_SERVICE_URL` | Auth service URL |