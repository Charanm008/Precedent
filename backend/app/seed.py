"""
Seed script: python -m backend.app.seed [--reset]

Creates Nexora Technologies with a $2.4M enterprise deal and sample interactions.
"""
import argparse
import sys
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

from .database import engine, SessionLocal, Base  # noqa: E402
from .models import db_models  # noqa: F401, E402
from .models.db_models import Customer, Deal, Stakeholder, Interaction  # noqa: E402

# Ensure tables exist
Base.metadata.create_all(bind=engine)


def reset_db(db):
    db.query(Interaction).delete()
    db.query(Stakeholder).delete()
    db.query(Deal).delete()
    db.query(Customer).delete()
    db.commit()
    print("Database reset.")


def seed(db):
    # Customer
    customer = Customer(
        name="Nexora Technologies",
        industry="Enterprise Software",
        website="https://nexora.example.com",
    )
    db.add(customer)
    db.flush()

    # Deal
    deal = Deal(
        customer_id=customer.id,
        title="Nexora Enterprise Platform Deal",
        value=2_400_000.0,
        stage="Negotiation",
        deal_score=82,
        risk_level="MEDIUM",
    )
    db.add(deal)
    db.flush()

    # Stakeholders
    cto = Stakeholder(deal_id=deal.id, name="Alex Chen", role="CTO", concern="security")
    cfo = Stakeholder(deal_id=deal.id, name="Maria Torres", role="CFO", concern="pricing")
    vp_eng = Stakeholder(
        deal_id=deal.id,
        name="James Park",
        role="VP Engineering",
        concern="deployment timeline",
    )
    procurement = Stakeholder(
        deal_id=deal.id,
        name="Sandra Lee",
        role="Procurement",
        concern="contract terms",
    )
    db.add_all([cto, cfo, vp_eng, procurement])
    db.flush()

    now = datetime.now(timezone.utc)

    # Interaction 1 – Initial call
    db.add(
        Interaction(
            deal_id=deal.id,
            stakeholder_id=None,
            type="call",
            summary=(
                "Initial discovery call with Nexora team. "
                "CTO Alex Chen raised concerns about data security and compliance. "
                "VP Engineering James Park indicated he needs deployment within 3 months. "
                "CFO Maria Torres stated our pricing feels high compared to budget."
            ),
            sentiment="neutral",
            strategy="Understand key priorities before proposing solutions.",
            outcome="neutral",
            occurred_at=now - timedelta(days=20),
        )
    )

    # Interaction 2 – CTO SOC2 response
    db.add(
        Interaction(
            deal_id=deal.id,
            stakeholder_id=cto.id,
            type="meeting",
            summary=(
                "Follow-up meeting with CTO. Generic security documentation did not engage him. "
                "However, when we walked through our SOC2 Type II compliance report and "
                "highlighted enterprise audit trail features, he responded very positively."
            ),
            sentiment="positive",
            strategy="Lead with SOC2 compliance and specific audit controls for CTO conversations.",
            outcome="worked",
            occurred_at=now - timedelta(days=14),
        )
    )

    # Interaction 3 – CFO discount rejection
    db.add(
        Interaction(
            deal_id=deal.id,
            stakeholder_id=cfo.id,
            type="meeting",
            summary=(
                "Pricing negotiation with CFO Maria Torres. "
                "Proposed a 10% discount on the annual license fee. "
                "She rejected it outright, stating the base price still exceeds their allocated budget "
                "and a flat discount alone is insufficient."
            ),
            sentiment="negative",
            strategy="Explore multi-year payment structures or phased rollout to fit budget constraints.",
            outcome="failed",
            occurred_at=now - timedelta(days=10),
        )
    )

    # Interaction 4 – VP Eng 3-month plan
    db.add(
        Interaction(
            deal_id=deal.id,
            stakeholder_id=vp_eng.id,
            type="meeting",
            summary=(
                "Presented the detailed 3-month deployment roadmap to VP Engineering James Park. "
                "He reviewed the milestone breakdown and expressed strong approval, "
                "confirming the timeline meets his team's constraints."
            ),
            sentiment="positive",
            strategy="Lock in the deployment timeline in the contract to maintain VP Eng's support.",
            outcome="worked",
            occurred_at=now - timedelta(days=7),
        )
    )

    # Interaction 5 – Competitor mention
    db.add(
        Interaction(
            deal_id=deal.id,
            stakeholder_id=None,
            type="call",
            summary=(
                "During a check-in call, Procurement mentioned that Competitor X has been "
                "positioned as a cheaper alternative. The team is evaluating whether the "
                "price differential justifies switching vendors."
            ),
            sentiment="negative",
            strategy=(
                "Prepare competitive battlecard vs Competitor X. "
                "Emphasise total cost of ownership, SOC2 compliance gap, and our deployment SLA."
            ),
            outcome="neutral",
            occurred_at=now - timedelta(days=3),
        )
    )

    db.commit()
    print(
        f"Seeded: Customer '{customer.name}' | Deal '{deal.title}' (id={deal.id}) | "
        f"4 stakeholders | 5 interactions"
    )


def main():
    parser = argparse.ArgumentParser(description="Seed the Precedent database.")
    parser.add_argument("--reset", action="store_true", help="Drop all data before seeding")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.reset:
            reset_db(db)

        # Check if already seeded
        existing = db.query(Customer).filter(Customer.name == "Nexora Technologies").first()
        if existing and not args.reset:
            print("Nexora Technologies already exists. Use --reset to re-seed.")
            sys.exit(0)

        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
