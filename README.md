# Precedent — AI Sales Strategist

Persistent-memory AI sales strategist built for **HackWithHyderabad 3.0**.

---

## 🚀 Overview
**Precedent** remembers deal history, learns from customer interactions, and recommends next-best actions using Hindsight persistent memory and Google ADK (Agent Development Kit).

---

## ⚡ Tech Stack
- **Frontend**: React 18, Custom Dark Glassmorphism CSS, Node HTTP Dev Server
- **Backend**: Python 3.13, FastAPI, Pydantic Settings, Uvicorn
- **Agent Subsystem**: Google ADK (Agent Development Kit) *(Phase 2)*
- **Memory Subsystem**: Hindsight Memory Engine *(Phase 1)*

---

## 📁 Project Structure
```text
Precedent-main/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   └── health.py    # Health & status endpoints
│   │   │       └── router.py       # API Router
│   │   ├── core/
│   │   │   └── config.py           # Pydantic environment configuration
│   │   └── main.py                 # FastAPI application entrypoint
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── index.html                  # Main React HTML shell
│   ├── app.js                      # React application dashboard & telemetry
│   ├── styles.css                  # Dark glassmorphism design system
│   ├── server.js                   # Node static web server
│   ├── package.json
│   └── README.md
├── data/                           # Structured datasets (competitors, customers, events, interactions)
├── memory/                         # Hindsight memory integration module
├── intelligence/                   # Strategy & deal reasoning module
├── agents/                         # Google ADK agent definitions
├── .env.example
├── .env
└── README.md
```

---

## 🚦 Quick Start Guide

### 1. Launch FastAPI Backend
From the root directory:
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
- API Docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- Detailed Status: [http://localhost:8000/api/v1/status](http://localhost:8000/api/v1/status)

### 2. Launch React Frontend
In a separate terminal, from the `frontend/` directory:
```bash
node server.js
```
- Application Web Dashboard: [http://localhost:5173](http://localhost:5173)

---

## 🛣️ Implementation Roadmap
- [x] **Phase 0 — Foundation**: FastAPI backend skeleton, React UI telemetry, CORS setup, project structure.
- [ ] **Phase 1 — Hindsight Memory Integration**: Persistent vector & deal memory store.
- [ ] **Phase 2 — Google ADK Reasoning Agent**: Multi-turn sales recommendation engine.
- [ ] **Phase 3 — Sales Deal Intelligence**: Customer, event, and competitor data ingest pipeline.
- [ ] **Phase 4 — Strategy & Recommendation UI**: Pitch optimizer & next-best-action view.
- [ ] **Phase 5 — Demo & Hackathon Packaging**: End-to-end deal scenario testing & showcase.
