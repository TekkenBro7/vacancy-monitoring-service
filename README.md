# Vacancy Monitoring Service

Vacancy Monitoring Service — A service for comparing and monitoring available vacancies and internships with integration of external data sources.

![FastAPI](https://img.shields.io/badge/FastAPI-0.122-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![React](https://img.shields.io/badge/React-18-61DAFB)
![Docker](https://img.shields.io/badge/Docker-✓-2496ED)
![Celery](https://img.shields.io/badge/Celery-✓-37814A)
![nginx](https://img.shields.io/badge/nginx-✓-009639)

---

⚙️ Tech Stack

- **FastAPI** — async REST API
- **PostgreSQL 16** — primary database
- **ORM**: SQLAlchemy + Alembic — ORM and migrations
- **Celery** + **Redis** + **RabbitMQ** — task queues and background jobs
- **Groq AI** — AI-powered data extraction
- **Playwright** — parsing JavaScript-heavy websites
- **Telethon** — Telegram client
- **Uvicorn (ASGI)** — backend server
- **Docker, Docker Compose** — containerization
- **uv** — dependency management
- **ruff**, **mypy** — linting and type checking
- **pytest** — testing
- **Makefile commands** — development utilities

---

## 🔌 Источники данных

| Source | Type | Description |
|---|---|---|
| **HH.ru** | REST API | Official API with application token |
| **SuperJob** | REST API | Official API with application token |
| **EPAM** | Parser | Playwright (JS rendering) |
| **Wargaming** | Parser | Playwright (JS rendering) |
| **Praca.by** | Parser | selectolax (HTML parsing) |
| **Telegram** | Telethon + AI | Channel parsing with AI extraction via Groq |

---

## 🚀 Quick Start

### 📁 Clone the Repository

```
git clone https://github.com/TekkenBro7/vacancy-monitoring-service.git
cd improve-api-service
```

### ⚙️ Setup `.env` File

Create a `.env` and `.env.docker` files based on `.env.example` and `.env.docker`

### Installing dependencies via Poetry

Install Uv if not already installed (Linux):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install project dependencies
```bash
uv sync
```

Before making any commits, run the following command to set up the pre-commit hooks:
```bash
uv run pre-commit install
```

To test pre-commit hooks without a commit, use
```bash
make lint
```
### 🛠️ Alembic Migrations
Once your database is configured and the **.env** file is ready, you need to apply migrations using Alembic to create the necessary tables and schema.

### 📌 Creating a New Migration
To generate a new migration after updating or adding models:
```bash
uv run alembic revision --autogenerate -m "your message here"
```
This will create a new file in the database/alembic/versions/ directory containing the migration script.

### ✅ Applying Migrations
To apply the latest migration to your database:

```bash
uv run alembic upgrade head
```
This ensures your database schema is up to date with the current models. If you run it through docker, it will automatically apply migrations.

### 🐳 Running with Docker

To start the app using Docker:
```bash
docker-compose up --build
```

Make sure `backend/.env.docker` contains:
```env
POSTGRES_HOST=db
REDIS_HOST=redis
RABBITMQ_HOST=rabbitmq
FRONTEND_URL=http://localhost
```

Also uou need to authorize Telegram once locally before running Docker

FastAPI will run on `http://localhost:8000` or `http://localhost`

### 🔧 Run Locally

1. Ensure PostgreSQL are installed and running
2. Create a PostgreSQL database and grant privileges users `.env` variables like
```bash
CREATE DATABASE 'your_db';
CREATE USER 'your_user' WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE 'your_db' TO 'your_user';
```
3. Apply migrations
4. Make sure `backend/.env` contains:
```env
POSTGRES_HOST=localhost
REDIS_HOST=localhost
RABBITMQ_HOST=localhost
FRONTEND_URL=http://localhost:3000
```
5. Start  services
```bash
# Terminal 1 — backend
cd backend
make runserver

# Terminal 2 — frontend
cd frontend
npm install
npm run dev

# Terminal 3 — Celery worker
cd backend
make celery

# Terminal 4 — Celery beat
cd backend
make celery_beat
```
For convenience, you can use the `make seed_data` command before starting the server to create test data.
