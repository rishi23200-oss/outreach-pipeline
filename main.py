#!/usr/bin/env python3
"""
Automated Cold-Outreach Pipeline
One domain in → lookalike companies → decision-makers → verified emails → outreach sent
"""

import sys
import json
import time
import logging
from datetime import datetime

from stages.stage1_apollo import find_lookalike_companies
from stages.stage2_prospeo import find_decision_makers
from stages.stage3_eazyreach import resolve_emails
from stages.stage4_brevo import send_outreach_emails
from utils.config import load_config
from utils.display import print_banner, print_stage, print_summary, print_checkpoint

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline(seed_domain: str, config: dict) -> dict:
    results = {
        "seed_domain": seed_domain,
        "timestamp": datetime.now().isoformat(),
        "stages": {}
    }

    # ── Stage 1: Ocean.io → lookalike companies ──────────────────────────────
    print_stage(1, "Ocean.io", "Finding lookalike companies")
    companies = find_lookalike_companies(seed_domain, config)
    results["stages"]["ocean"] = {"companies_found": len(companies), "domains": companies}
    logger.info(f"Stage 1 complete: {len(companies)} companies found")
    print(f"\n  ✓ Found {len(companies)} lookalike companies\n")
    for d in companies[:5]:
        print(f"    • {d}")
    if len(companies) > 5:
        print(f"    … and {len(companies) - 5} more")

    # ── Stage 2: Prospeo → decision-makers ───────────────────────────────────
    print_stage(2, "Prospeo", "Finding decision-makers (C-suite / VP)")
    prospects = find_decision_makers(companies, config)
    results["stages"]["prospeo"] = {"prospects_found": len(prospects), "prospects": prospects}
    logger.info(f"Stage 2 complete: {len(prospects)} prospects found")
    print(f"\n  ✓ Found {len(prospects)} decision-makers\n")
    for p in prospects[:3]:
        print(f"    • {p.get('full_name','?')} – {p.get('job_title','?')} @ {p.get('company_domain','?')}")

    # ── Stage 3: Eazyreach → verified work emails ────────────────────────────
    print_stage(3, "Eazyreach", "Resolving verified work emails from LinkedIn")
    prospects_with_emails = resolve_emails(prospects, config)
    emailed = [p for p in prospects_with_emails if p.get("email")]
    results["stages"]["eazyreach"] = {"emails_resolved": len(emailed), "prospects": prospects_with_emails}
    logger.info(f"Stage 3 complete: {len(emailed)} emails resolved")
    print(f"\n  ✓ Resolved {len(emailed)} verified emails\n")
    for p in emailed[:3]:
        print(f"    • {p.get('full_name','?')} → {p.get('email','?')}")

    if not emailed:
        print("\n  ⚠  No verified emails resolved. Exiting before send stage.\n")
        results["stages"]["brevo"] = {"emails_sent": 0}
        return results

    # ── Safety checkpoint ─────────────────────────────────────────────────────
    print_checkpoint(emailed)
    confirm = input("\n  Proceed and send outreach emails? [y/N] ").strip().lower()
    if confirm != "y":
        print("\n  ✗ Aborted by user. No emails sent.\n")
        results["stages"]["brevo"] = {"emails_sent": 0, "aborted": True}
        return results

    # ── Stage 4: Brevo → send personalised outreach ──────────────────────────
    print_stage(4, "Brevo", "Sending personalized outreach emails")
    sent_count = send_outreach_emails(emailed, config)
    results["stages"]["brevo"] = {"emails_sent": sent_count}
    logger.info(f"Stage 4 complete: {sent_count} emails sent")
    print(f"\n  ✓ Sent {sent_count} outreach emails\n")

    return results


def main():
    print_banner()
    config = load_config()

    if len(sys.argv) > 1:
        seed_domain = sys.argv[1].strip().lower()
    else:
        seed_domain = input("  Enter seed company domain (e.g. stripe.com): ").strip().lower()

    if not seed_domain:
        print("  ✗ No domain provided. Exiting.")
        sys.exit(1)

    print(f"\n  Seed domain: {seed_domain}\n")

    try:
        results = run_pipeline(seed_domain, config)
        print_summary(results)

        # Save run results
        out_file = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(out_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n  Results saved to {out_file}\n")

    except KeyboardInterrupt:
        print("\n\n  Pipeline interrupted by user.\n")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        print(f"\n  ✗ Pipeline error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
