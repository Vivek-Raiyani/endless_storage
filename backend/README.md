# Endless Storage Backend

Endless Storage is a cloud storage abstraction platform that aggregates multiple Google Drive accounts into a single, seamless, and "endless" storage pool. 

This backend is built on **FastAPI** (Python) using modern asynchronous programming (SQLAlchemy async + `aiosqlite`/PostgreSQL) to handle robust file chunking, distributed storage placement, and background migrations.

## ✨ Current Features

- **Multi-Drive Aggregation**: Connect multiple Google Drive accounts via OAuth and pool their storage capacities together.
- **File Chunking System**: Uploads are automatically split into fixed physical chunks (default 256MB). This bypasses single-file upload limits and allows a single virtual file to span across multiple physical drives!
- **Dynamic Bin Packing Migrations**: When a user disconnects a drive, the system automatically runs a "Worst-Fit Decreasing" Bin Packing algorithm to pre-allocate chunks to remaining drives and then seamlessly migrates the files in the background without losing data.
- **Robust Background Scheduler**: Uses `APScheduler` to run background jobs for processing pending file chunk migrations and deleting files without tying up the web server.
- **Secure Token Storage**: Google Refresh Tokens are encrypted at rest using a symmetric Fernet key.
- **Soft Deletion**: Virtual files are softly deleted, allowing for easy recovery or trash bin implementation.

## 🚀 Performance & Limits

- **Chunk Size**: Fixed at 256MB (`CHUNK_SIZE_BYTES`). This ensures optimal resumable upload performance to Google Drive while keeping the database index small.
- **Migration Batching**: The background migration job (`migration.py`) processes a maximum of 20 chunks (~5GB) per account per execution to respect API quotas and prevent out-of-memory errors.
- **Deletion Throttling**: The background deletion task processes chunks in batches of 1000 with a 5-second `asyncio.sleep()` between batches to strictly prevent Google Drive API rate-limiting.
- **Polling Interval**: The background scheduler polls the database every 30 minutes for pending migrations.

## 🚧 Missing Features & Roadmap

- **No Backup / Redundancy Option**: Currently, each chunk is stored on exactly one drive (RAID 0 style). There is no "mirroring" or backup option yet. If a connected Google account gets banned or closed, that chunk is lost forever. Implementing erasure coding or 1:1 mirroring is a top priority.
- **Partial Downloads**: We do not yet support byte-range requests spanning across multiple chunks for streaming video directly from the UI.
- **Server-Side Migrations (No bandwidth costs)**: Migrations do NOT download chunks to the backend server. Instead, they leverage native Google Drive APIs to share the file from the old account to the new account, instruct the new account to make a native copy on Google's servers, and then delete the original. This means migrations cost 0 bandwidth!

---

## 🛠️ Complete Setup Instructions

### 1. Environment Setup
Make sure you have Python 3.10+ installed.

```bash
# Clone the repository and enter the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies (Assuming a requirements.txt exists)
pip install -r requirements.txt
```

### 2. Configuration (`.env`)
Create a `.env` file in the root of the backend directory. You will need a Google Cloud Console project with the Drive API enabled.

```env
# Server
PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./endless_storage.db

# Google OAuth Credentials
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Encryption Key (Must be a 32-byte url-safe base64 string)
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
TOKEN_ENCRYPTION_KEY=your_generated_fernet_key
```

### 3. Database Migrations
We use **Alembic** for database migrations. Initialize your database to the latest schema:

```bash
alembic upgrade head
```

### 4. Running the Application
The system consists of the API server and the Background Scheduler (which currently runs inside the app lifecycle).

```bash
# Run the development server with hot-reloading
fastapi dev
```
Your server will be running at `http://127.0.0.1:8000`. 
Swagger UI API Docs are available at `http://127.0.0.1:8000/docs`.

---

## 🧑‍💻 Contributing & Coding Guide

We welcome contributions! To make it easy for anyone to jump in, here is a quick map of the architecture:

- **`app/api/routes/`**: FastAPI endpoints. Keep these thin! They should mostly parse requests and call service functions.
- **`app/services/`**: The core business logic. 
  - `storage_account_service.py`: Handles Google OAuth, Drive quotas, and the complex Bin Packing logic for calculating migrations.
- **`app/models/`**: SQLAlchemy ORM models (`virtual_file.py` and `storage_account.py`).
- **`app/tasks/`**: Background jobs.
  - `scheduler.py`: Configures `APScheduler` to run jobs periodically.
  - `migration.py`: The worker script that executes the actual Google Drive API calls to move chunks and update the database.

### How to generate a new Database Migration
If you modify or add any models in `app/models/`, you must generate a new Alembic migration:
```bash
alembic revision --autogenerate -m "Add description of your changes"
alembic upgrade head
```

### Best Practices
- **Use Async**: Everything is async! Use `await db.execute(...)` for database queries, not `db.query(...)`.
- **Handle Google API Limits**: Google Drive is very aggressive with rate limits. Any loops that hit the Drive API must have batching and `asyncio.sleep()` built into them.
- **Avoid Loading All Rows**: If a user has 50,000 file chunks, `result.scalars().all()` will crash the server. Use `.limit()` and explicit `func.count()` queries for background tasks (as implemented in `migration.py`).
