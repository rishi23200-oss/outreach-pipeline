"""
Stage 3 — Email resolver using Prospeo Enrich Person
"""

import logging
from utils.http import make_session, safe_post

logger = logging.getLogger(__name__)

PROSPEO_BASE = "https://api.prospeo.io"


def resolve_emails(prospects: list[dict], config: dict) -> list[dict]:
    """
    For demo: use sender's own email to verify pipeline works end-to-end.
    In production, this would call Prospeo enrich-person API.
    """
    sender_email = config["sender_email"]
    
    enriched = []
    for i, prospect in enumerate(prospects[:3]):
        if i == 0:
            prospect = {**prospect, "email": sender_email}
            logger.info(f"Demo mode: assigned {sender_email} to {prospect.get('full_name')}")
        enriched.append(prospect)
    
    logger.info(f"Emails resolved: 1/3 (demo mode)")
    return enriched
    
    for prospect in prospects:
        name     = prospect.get("full_name", "Unknown")
        linkedin = prospect.get("linkedin_url", "")

        if not linkedin:
            logger.warning(f"No LinkedIn URL for {name}, skipping")
            enriched.append(prospect)
            continue

        logger.info(f"Prospeo enrich: {name}")
        email = _enrich_by_linkedin(session, linkedin, delay)

        if email:
            prospect = {**prospect, "email": email}
            resolved += 1
            logger.info(f"Email found: {email}")
        else:
            logger.warning(f"Email not found for {name}")

        enriched.append(prospect)

    logger.info(f"Emails resolved: {resolved}/{len(prospects)}")
    return enriched


def _enrich_by_linkedin(session, linkedin_url: str, delay: float) -> str | None:
    payload = {
        "data": {
            "linkedin_url": linkedin_url
        }
    }
    data = safe_post(
        session,
        f"{PROSPEO_BASE}/enrich-person",
        json=payload,
        rate_delay=delay
    )
    if not data or data.get("error"):
        return None
    email_obj = (data.get("person") or {}).get("email") or {}
    return email_obj.get("email") or None