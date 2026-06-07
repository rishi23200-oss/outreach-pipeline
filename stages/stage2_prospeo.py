"""
Stage 2 — Prospeo (new API)
Endpoint: https://api.prospeo.io/search-person
Auth: X-KEY header
"""

import logging
from utils.http import make_session, safe_post

logger = logging.getLogger(__name__)

PROSPEO_BASE = "https://api.prospeo.io"


def find_decision_makers(domains: list[str], config: dict) -> list[dict]:
    api_key    = config["prospeo_api_key"]
    per_domain = config.get("prospeo_limit", 5)
    delay      = config.get("rate_limit_delay", 1.0)

    session = make_session()
    session.headers.update({
        "X-KEY": api_key,
        "Content-Type": "application/json",
    })

    all_prospects = []
    seen = set()

    for domain in domains:
        logger.info(f"Prospeo: searching {domain} …")
        prospects = _search_people(session, domain, per_domain, delay)
        for p in prospects:
            key = p.get("linkedin_url") or p.get("full_name", "") + domain
            if key not in seen:
                seen.add(key)
                all_prospects.append(p)
        if not prospects:
            logger.warning(f"No decision-makers found for {domain}")

    logger.info(f"Prospeo total: {len(all_prospects)} unique prospects")
    return all_prospects

import json, os

def _load_cached(domain):
    cache_file = "prospeo_cache.json"
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            cache = json.load(f)
        return cache.get(domain, [])
    return []

def _search_people(session, domain, limit, delay) -> list[dict]:
    payload = {
        "page": 1,
        "filters": {
            "company": {
                "websites": {
                    "include": [domain]
                }
            },
            "person_seniority": {
                "include": ["C-Suite", "Director", "Founder/Owner"]
            }
        }
    }

    data = safe_post(
        session,
        f"{PROSPEO_BASE}/search-person",
        json=payload,
        rate_delay=delay
    )

    if not data or data.get("error"):
        logger.warning(f"Prospeo error: {data}")
        return []

    results = []
    for item in data.get("results", []):
        person  = item.get("person", {})
        company = item.get("company", {})

        first = person.get("first_name", "")
        last  = person.get("last_name", "")
        

        results.append({
            "full_name"     : f"{first} {last}".strip(),
            "first_name"    : first,
            "last_name"     : last,
            "job_title": person.get("current_job_title", ""),
            "company_domain": domain,
            "company_name"  : company.get("name", domain),
            "linkedin_url"  : person.get("linkedin_url", ""),
            "person_id": person.get("person_id", ""),
            "email"         : "",
        })

        if len(results) >= limit:
            break

    return results