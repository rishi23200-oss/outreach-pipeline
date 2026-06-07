"""
Pretty CLI display helpers.
"""

CYAN  = "\033[96m"
GREEN = "\033[92m"
YELLOW= "\033[93m"
RED   = "\033[91m"
BOLD  = "\033[1m"
RESET = "\033[0m"
DIM   = "\033[2m"


def print_banner():
    print(f"""
{BOLD}{CYAN}
╔══════════════════════════════════════════════════════════════╗
║         AUTOMATED COLD-OUTREACH PIPELINE  v1.0              ║
║   Ocean.io → Prospeo → Eazyreach → Brevo                   ║
╚══════════════════════════════════════════════════════════════╝
{RESET}""")


def print_stage(number: int, tool: str, description: str):
    print(f"\n{BOLD}{CYAN}── Stage {number}: {tool}{RESET}  {DIM}{description}{RESET}")
    print(f"   {'─' * 54}")


def print_checkpoint(prospects: list):
    print(f"""
{BOLD}{YELLOW}╔══════════════════════════════════════════════════════════════╗
║                  ⚠  SAFETY CHECKPOINT                       ║
╚══════════════════════════════════════════════════════════════╝{RESET}

  You are about to send {len(prospects)} outreach email(s):
""")
    for p in prospects:
        name  = p.get("full_name", "Unknown")
        email = p.get("email", "—")
        title = p.get("job_title", "")
        company = p.get("company_domain", "")
        print(f"    • {name} <{email}>  –  {title} @ {company}")


def print_summary(results: dict):
    stages = results.get("stages", {})
    ocean   = stages.get("ocean",    {}).get("companies_found", 0)
    pros    = stages.get("prospeo",  {}).get("prospects_found", 0)
    emails  = stages.get("eazyreach",{}).get("emails_resolved",  0)
    sent    = stages.get("brevo",    {}).get("emails_sent",       0)
    aborted = stages.get("brevo",    {}).get("aborted", False)

    status = f"{RED}Aborted{RESET}" if aborted else f"{GREEN}Complete{RESET}"

    print(f"""
{BOLD}── Pipeline Summary ─────────────────────────────────────────{RESET}

   Seed domain      : {results.get('seed_domain')}
   Status           : {status}

   Stage 1 – Ocean    : {ocean:>4}  lookalike companies
   Stage 2 – Prospeo  : {pros:>4}  decision-makers found
   Stage 3 – Eazyreach: {emails:>4}  emails resolved
   Stage 4 – Brevo    : {sent:>4}  outreach emails sent

{BOLD}─────────────────────────────────────────────────────────────{RESET}
""")
