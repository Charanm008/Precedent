# Precedent Backend API

FastAPI backend service powering the Precedent Persistent-Memory AI Sales Strategist.

## Features
- Modular FastAPI project structure (`app/core`, `app/api/v1/endpoints`)
- Configurable environment settings via `pydantic-settings` and `.env`
- Cross-Origin Resource Sharing (CORS) configured for frontend communication
- Interactive OpenAPI documentation available at `/docs`

## Setup & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` in project root:
```bash
cp ../.env.example ../.env
```

### 3. Run Backend Server
From the `backend` directory:
```bash
python -m uvicorn app.main:app --reload --port 8000
```
Or from root:
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

### 4. API Documentation
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- System Status: [http://localhost:8000/api/v1/status](http://localhost:8000/api/v1/status)
