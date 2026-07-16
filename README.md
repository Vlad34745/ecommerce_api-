# E-Commerce REST API

A production-style REST API built with **FastAPI** and **SQLAlchemy**, connected to a cloud-hosted **PostgreSQL** database (Neon.tech). Provides full CRUD operations for products, nested order/product lookups, and API-key protected write endpoints.

Built as a companion API layer for the [sql-ecommerce-pipeline](https://github.com/Vlad34745/sql-ecommerce-pipeline) project, reusing the same underlying database schema (`users`, `products`, `orders`).

## 🛠 Tech Stack
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL (Neon.tech)
- **Validation:** Pydantic
- **Auth:** API Key via custom HTTP header (`X-API-Key`)
- **Server:** Uvicorn (ASGI)

## ✨ Features
- **Full CRUD for products** (`GET`, `POST`, `PUT`, `DELETE`)
- **Nested relational data:** `/users/{id}/orders` returns each order together with its full product details in a single response, using SQLAlchemy `relationship()`
- **API-key protected write operations:** creating, updating, or deleting products requires a valid `X-API-Key` header; read endpoints stay public
- **Proper error handling:** meaningful `404`/`400`/`401` responses instead of raw server errors — including graceful handling of database foreign-key constraints (e.g. you can't delete a product that still has orders referencing it)
- **Auto-generated interactive docs** via Swagger UI at `/docs`

## 📚 API Endpoints

| Method | Endpoint | Auth required | Description |
|---|---|---|---|
| GET | `/` | No | Health check |
| GET | `/products` | No | List all products |
| GET | `/products/{product_id}` | No | Get a single product by ID |
| POST | `/products` | Yes | Create a new product |
| PUT | `/products/{product_id}` | Yes | Update an existing product |
| DELETE | `/products/{product_id}` | Yes | Delete a product (blocked if it has linked orders) |
| GET | `/users/{user_id}/orders` | No | List all orders for a user, with full product details nested in each order |

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Vlad34745/ecommerce_api-.git
   cd ecommerce_api
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file based on `.env.example`:
   ```
   DATABASE_URL=postgresql://user:password@host/neondb?sslmode=require
   API_KEY=your_secret_api_key_here
   ```

5. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

6. **Explore the API:**
   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger UI. To test protected endpoints, click **Authorize** and enter your `API_KEY`.

## 📐 Project Structure
```text
ecommerce_api/
│
├── main.py         # API routes and request handling
├── models.py        # SQLAlchemy ORM models (database tables)
├── schemas.py        # Pydantic schemas (request/response validation)
├── database.py         # Database connection and session management
├── security.py           # API key authentication
├── .env.example            # Template for required environment variables
└── requirements.txt          # Python dependencies
```