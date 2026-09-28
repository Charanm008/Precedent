"""
Tests for Phase 1 Deal Management API.
Run from repo root: pytest tests/test_deals.py -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.main import app

# ── In-memory SQLite: use StaticPool to share one connection across threads ───

@pytest.fixture
def client():
    """Return a TestClient wired to an isolated in-memory DB."""
    from backend.app.models import db_models  # noqa: F401

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


# ── Helper ─────────────────────────────────────────────────────────────────────

def create_sample_deal(client, stage="Prospecting"):
    return client.post("/deal", json={
        "customer_name": "Acme Corp",
        "customer_industry": "SaaS",
        "title": "Acme Enterprise Deal",
        "value": 500000,
        "stage": stage,
        "deal_score": 60,
        "risk_level": "LOW",
    })


# ── Health ─────────────────────────────────────────────────────────────────────

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── Deal CRUD ──────────────────────────────────────────────────────────────────

def test_create_deal(client):
    resp = create_sample_deal(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Acme Enterprise Deal"
    assert data["customer"]["name"] == "Acme Corp"
    assert data["stage"] == "Prospecting"
    assert data["deal_score"] == 60
    assert data["risk_level"] == "LOW"
    assert data["interaction_count"] == 0


def test_create_deal_reuses_existing_customer(client):
    create_sample_deal(client)
    resp = client.post("/deal", json={
        "customer_name": "Acme Corp",
        "title": "Second Deal",
        "value": 100000,
        "stage": "Discovery",
    })
    assert resp.status_code == 201
    assert resp.json()["customer"]["name"] == "Acme Corp"


def test_create_deal_invalid_stage(client):
    resp = client.post("/deal", json={
        "customer_name": "X",
        "title": "Bad Stage Deal",
        "value": 0,
        "stage": "FakeStage",
    })
    assert resp.status_code == 422


def test_create_deal_invalid_risk(client):
    resp = client.post("/deal", json={
        "customer_name": "X",
        "title": "Bad Risk Deal",
        "value": 0,
        "stage": "Prospecting",
        "risk_level": "VERY_HIGH",
    })
    assert resp.status_code == 422


def test_list_deals_empty(client):
    resp = client.get("/deals")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_deals(client):
    create_sample_deal(client)
    create_sample_deal(client)
    resp = client.get("/deals")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_deal(client):
    deal_id = create_sample_deal(client).json()["id"]
    resp = client.get(f"/deal/{deal_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == deal_id
    assert data["customer"]["name"] == "Acme Corp"
    assert "stakeholders" in data
    assert "interaction_count" in data


def test_get_deal_not_found(client):
    resp = client.get("/deal/9999")
    assert resp.status_code == 404


def test_patch_deal_stage(client):
    deal_id = create_sample_deal(client).json()["id"]
    resp = client.patch(f"/deal/{deal_id}", json={"stage": "Negotiation"})
    assert resp.status_code == 200
    assert resp.json()["stage"] == "Negotiation"


def test_patch_deal_score_and_risk(client):
    deal_id = create_sample_deal(client).json()["id"]
    resp = client.patch(f"/deal/{deal_id}", json={"deal_score": 90, "risk_level": "HIGH"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["deal_score"] == 90
    assert data["risk_level"] == "HIGH"


def test_patch_deal_invalid_stage(client):
    deal_id = create_sample_deal(client).json()["id"]
    resp = client.patch(f"/deal/{deal_id}", json={"stage": "NotReal"})
    assert resp.status_code == 422


def test_patch_deal_not_found(client):
    resp = client.patch("/deal/9999", json={"stage": "Discovery"})
    assert resp.status_code == 404


# ── Interaction ────────────────────────────────────────────────────────────────

def test_create_interaction(client):
    deal_id = create_sample_deal(client).json()["id"]
    resp = client.post("/interaction", json={
        "deal_id": deal_id,
        "type": "call",
        "summary": "Had a productive call about security requirements.",
        "sentiment": "positive",
        "strategy": "Follow up with SOC2 docs.",
        "outcome": "worked",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["deal_id"] == deal_id
    assert data["type"] == "call"
    assert data["sentiment"] == "positive"
    assert data["outcome"] == "worked"


def test_create_interaction_invalid_type(client):
    deal_id = create_sample_deal(client).json()["id"]
    resp = client.post("/interaction", json={
        "deal_id": deal_id,
        "type": "smoke_signal",
        "summary": "Smoke signals are not a valid type.",
        "sentiment": "neutral",
    })
    assert resp.status_code == 422


def test_create_interaction_invalid_sentiment(client):
    deal_id = create_sample_deal(client).json()["id"]
    resp = client.post("/interaction", json={
        "deal_id": deal_id,
        "type": "call",
        "summary": "Test",
        "sentiment": "meh",
    })
    assert resp.status_code == 422


def test_create_interaction_deal_not_found(client):
    resp = client.post("/interaction", json={
        "deal_id": 9999,
        "type": "call",
        "summary": "No such deal.",
        "sentiment": "neutral",
    })
    assert resp.status_code == 404


# ── Timeline ───────────────────────────────────────────────────────────────────

def test_timeline_empty(client):
    deal_id = create_sample_deal(client).json()["id"]
    resp = client.get(f"/timeline/{deal_id}")
    assert resp.status_code == 200
    assert resp.json() == []


def test_timeline_returns_newest_first(client):
    deal_id = create_sample_deal(client).json()["id"]

    for summary in ["first", "second", "third"]:
        client.post("/interaction", json={
            "deal_id": deal_id,
            "type": "note",
            "summary": summary,
            "sentiment": "neutral",
        })

    resp = client.get(f"/timeline/{deal_id}")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 3
    # newest first (by occurred_at)
    dates = [item["occurred_at"] for item in items]
    assert dates == sorted(dates, reverse=True)


def test_timeline_deal_not_found(client):
    resp = client.get("/timeline/9999")
    assert resp.status_code == 404


def test_interaction_count_updates(client):
    deal_id = create_sample_deal(client).json()["id"]
    assert client.get(f"/deal/{deal_id}").json()["interaction_count"] == 0

    client.post("/interaction", json={
        "deal_id": deal_id,
        "type": "email",
        "summary": "Sent proposal.",
        "sentiment": "neutral",
    })
    assert client.get(f"/deal/{deal_id}").json()["interaction_count"] == 1
