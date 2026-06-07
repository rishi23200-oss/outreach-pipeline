"""
Stage 1 — Apollo.io (replacement for Ocean.io)
Input : seed company domain (str)
Output: list of lookalike company domains (list[str])

Apollo.io API docs: https://apolloio.github.io/apollo-api-docs/
No company email required — free tier works fine.
"""

import logging
from utils.http import make_session, safe_post

logger = logging.getLogger(__name__)

APOLLO_BASE = "https://api.apollo.io/v1"


def find_lookalike_companies(seed_domain: str, config: dict) -> list[str]:
    api_key = config["ocean_api_key"]   # reuse same key name — just put Apollo key here in .env
    limit   = config.get("ocean_limit", 10)
    delay   = config.get("rate_limit_delay", 1.0)

    session = make_session()
    session.headers.update({
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "X-Api-Key": api_key,
    })

    # Step 1: get seed company's industry + employee count
    seed_info = _get_company_info(session, seed_domain, api_key, delay)
    if not seed_info:
        logger.warning(f"Could not find seed domain {seed_domain} in Apollo — using domain search only")

    industries    = seed_info.get("industries", [])       if seed_info else []
    employee_range = seed_info.get("employee_ranges", []) if seed_info else []

    # Step 2: search for similar companies
    domains = _search_similar(session, api_key, industries, employee_range, limit, delay)

    # Exclude seed itself
    domains = [d for d in domains if d and d.lower() != seed_domain.lower()]
    domains = list(dict.fromkeys(domains))  # deduplicate

    logger.info(f"Apollo returned {len(domains)} lookalike domains")
    return domains[:limit]


def _get_company_info(session, domain: str, api_key: str, delay: float) -> dict | None:
    payload = {
        "api_key": api_key,
        "domain": domain,
    }
    data = safe_post(session, f"{APOLLO_BASE}/organizations/enrich", json=payload, rate_delay=delay)
    if not data:
        return None

    org = data.get("organization") or {}
    return {
        "industries":      org.get("industries", []),
        "employee_ranges": _map_size(org.get("estimated_num_employees")),
        "name":            org.get("name", domain),
    }


def _search_similar(session, api_key, industries, employee_ranges, limit, delay) -> list[str]:
    payload = {
        "page": 1,
        "per_page": limit + 5,
        "organization_num_employees_ranges": employee_ranges or ["1,500"],
    }
    if industries:
        payload["q_organization_industry_tag_ids"] = industries[:3]

    data = safe_post(
        session,
        f"{APOLLO_BASE}/organizations/search",
        json=payload,
        rate_delay=delay
    )
    if not data:
        return []

    domains = []
    for org in data.get("organizations", []):
        domain = org.get("primary_domain") or org.get("website_url") or ""
        domain = _clean_domain(domain)
        if domain:
            domains.append(domain)

    return domains


def _map_size(num_employees) -> list[str]:
    if not num_employees:
        return []
    n = int(num_employees)
    if n < 10:      return ["1,10"]
    if n < 50:      return ["10,50"]
    if n < 200:     return ["50,200"]
    if n < 1000:    return ["200,1000"]
    return ["1000,10000"]


def _clean_domain(url: str) -> str:
    url = url.strip().lower()
    for prefix in ("https://", "http://", "www."):
        if url.startswith(prefix):
            url = url[len(prefix):]
    return url.split("/")[0]