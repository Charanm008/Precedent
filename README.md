# Precedent

Persistent-memory AI sales strategist for HackWithHyderabad 3.0.

## Stack
- **Frontend**: React 18, Vite, Tailwind CSS 3, react-router-dom
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy (SQLite)
- **Memory** *(Phase 2)*: Hindsight
- **Agent** *(Phase 2)*: Google ADK

---

## Phase 1 — Deal Management

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend

```bash
# From repo root
pip install -r backend/requirements.txt

# Start dev server (runs from repo root so memory/ imports work)
uvicorn backend.app.main:app --reload --port 8000
```

The database (`backend/precedent.db`) is created automatically on first start.

#### Seed demo data

```bash
python -m backend.app.seed         # create Nexora Technologies deal
python -m backend.app.seed --reset # wipe and re-seed
```

#### API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/deals` | List all deals |
| POST | `/deal` | Create a deal |
| GET | `/deal/{id}` | Deal detail + stakeholders + interaction count |
| PATCH | `/deal/{id}` | Update stage / score / risk |
| POST | `/interaction` | Log an interaction |
| GET | `/timeline/{id}` | Timeline for a deal (newest first) |

Valid stages: `Prospecting`, `Discovery`, `Proposal`, `Negotiation`, `Closed Won`, `Closed Lost`

#### Tests

```bash
pytest tests/test_deals.py -v
```

---

### Frontend

```bash
cd frontend
npm install
npm run dev     # dev server at http://localhost:5173
npm run build   # production build
```

Set `VITE_API_URL` in `frontend/.env.local` to override the default backend URL.

---

## Environment variables

Copy `.env.example` to `.env` and fill in values.

```bash
cp .env.example .env
```

---

## Architecture

See `docs/architecture.md` for planned Phase 2 additions (AI agents, competitive intelligence, Hindsight memory).
