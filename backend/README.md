# FastAPI Boilerplate Documentation

This guide covers everything you need to know to run your application, manage database migrations, and configure your database and storage integrations.

## 🚀 Running the Server

FastAPI has a built-in CLI tool to run your application in development mode with hot-reloading.

```bash
# Ensure your virtual environment is active
.\venv\Scripts\activate

# Run the development server
fastapi dev
```
Your server will be running at `http://127.0.0.1:8000`. You can explore your API endpoints via the interactive Swagger documentation at `http://127.0.0.1:8000/docs`.

---

## 🗄️ Database Migrations

This project uses **Alembic** to manage database schema migrations. Since the application runs asynchronously, the migrations have been specifically configured to bridge the gap and run synchronously against your database.

### 1. Generating a New Migration
Whenever you modify your models (e.g., adding a new field or a new table in `app/models/`), you need to generate a migration script.

**Note on Individual vs. Multiple Models:** 
Because of our dynamic Alembic configuration in `alembic/env.py`, all model files placed inside the `app/models/` directory are automatically discovered. This means you **do not** need a special command to migrate a single model file versus a list of files. Whether you changed one file or ten, running the command below will automatically detect all the changes across your models and bundle them into the migration!

```bash
alembic revision --autogenerate -m "Description of your changes"
```

### 2. Applying Migrations
To apply pending migrations to your database:

```bash
alembic upgrade head
```

### 3. Rolling Back
If you need to undo the last migration:

```bash
alembic downgrade -1
```

---

## 🔀 Switching Databases

By default, the application is configured to use **SQLite** (specifically the `aiosqlite` async driver). Because of our modular architecture in `app/core/database.py` and `alembic/env.py`, switching to a production-grade database like **PostgreSQL** is incredibly seamless!

### Steps to Switch to PostgreSQL:

1. **Install the async Postgres driver**:
   ```bash
   pip install asyncpg psycopg2-binary
   ```
2. **Update your `.env` file**:
   Change your `DATABASE_URL` to point to your Postgres instance using the `postgresql+asyncpg` dialect.
   ```env
   # .env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
   ```
3. **Apply your schema**:
   Postgres will automatically be picked up by Alembic (which seamlessly strips the async driver dynamically for migrations) and by your `AsyncEngine`. Simply run `alembic upgrade head`.

> **Note:** If you ever switch back to SQLite, make sure to prefix it with `sqlite+aiosqlite:///` so the asynchronous engine knows how to talk to it!

---

## 📦 Switching Storage Providers

The project uses a unified storage abstraction located in `app/utils/storage.py`. All storage implementations (Local Storage, AWS S3, etc.) inherit from the same base class and expose identical methods (e.g., `save()`, `read()`, `delete()`).

### How to Switch

You don't need to rewrite your business logic when switching from Local Storage to Cloud Storage. You just need to instantiate the correct provider class.

For example, when initializing your storage layer, simply swap out the class being used:

```python
from app.utils.storage import LocalStorage, S3Storage

# ------------------------------
# Option A: Use Local Storage
# ------------------------------
storage_provider = LocalStorage(base_dir="./uploads")

# ------------------------------
# Option B: Use AWS S3 Storage
# ------------------------------
# Make sure to install boto3: pip install boto3
storage_provider = S3Storage(
    bucket_name="my-app-bucket", 
    region_name="us-east-1",
    aws_access_key_id="YOUR_ACCESS_KEY", 
    aws_secret_access_key="YOUR_SECRET_KEY"
)

# ------------------------------
# Usage remains exactly the same!
# ------------------------------
# filepath = await storage_provider.save(file_bytes, "users/1/avatar.png")
```

Because of this abstraction, the rest of your application does not need to know *where* the files are being saved, it just calls `storage_provider.save(...)` and it handles the rest based on what provider is configured!
