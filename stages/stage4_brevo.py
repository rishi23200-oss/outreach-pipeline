"""
Stage 4 — Brevo (Sendinblue)
Input : list of prospects with verified emails
Output: count of emails sent

Brevo Transactional Email API:
  POST https://api.brevo.com/v3/smtp/email
  Header: api-key: <BREVO_API_KEY>
"""

import logging
import time
from utils.http import make_session, safe_post

logger = logging.getLogger(__name__)

BREVO_BASE = "https://api.brevo.com/v3"


def send_outreach_emails(prospects: list[dict], config: dict) -> int:
    """
    Send a personalised cold-outreach email to each prospect via Brevo.
    Returns the number of emails successfully sent.
    """
    api_key      = config["brevo_api_key"]
    sender_email = config["sender_email"]
    sender_name  = config["sender_name"]
    delay        = config.get("rate_limit_delay", 1.0)

    session = make_session()
    session.headers.update({
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })

    sent = 0
    for prospect in prospects:
        email = prospect.get("email", "").strip()
        if not email:
            continue

        subject, html_body, text_body = _compose_email(prospect, sender_name)

        payload = {
            "sender": {"name": sender_name, "email": sender_email},
            "to": [{"email": email, "name": prospect.get("full_name", "")}],
            "subject": subject,
            "htmlContent": html_body,
            "textContent": text_body,
            "tags": ["outreach-pipeline"],
            "headers": {
                "X-Pipeline-Source": "automated-outreach-v1",
            },
        }

        logger.info(f"Brevo: sending to {prospect.get('full_name')} <{email}>")
        result = safe_post(session, f"{BREVO_BASE}/smtp/email", json=payload, rate_delay=delay)

        if result and (result.get("messageId") or result.get("message_id")):
            logger.info(f"  ✓ Sent — messageId: {result.get('messageId')}")
            sent += 1
        else:
            logger.warning(f"  ✗ Failed to send to {email}: {result}")

    return sent


def _compose_email(prospect: dict, sender_name: str) -> tuple[str, str, str]:
    """
    Build a personalised subject + HTML + plain-text email body.
    Personalization: first name, job title, company name.
    """
    first_name   = prospect.get("first_name") or prospect.get("full_name", "").split()[0] or "there"
    job_title    = prospect.get("job_title", "leader")
    company_name = prospect.get("company_name") or prospect.get("company_domain", "your company")

    subject = f"Quick question for {company_name}'s {job_title.split()[-1]}"

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; font-size: 15px; color: #222; max-width: 600px; margin: 0 auto; padding: 24px;">

<p>Hi {first_name},</p>

<p>
  I came across {company_name} while researching companies doing interesting work in your space,
  and I wanted to reach out directly.
</p>

<p>
  We help teams like yours automate the parts of the sales and growth process that eat up the most
  time — specifically the sourcing-to-outreach loop. Most of our customers cut their prospecting
  time by 60–70% in the first month.
</p>

<p>
  Given your role as <strong>{job_title}</strong> at {company_name}, I thought you'd be the right
  person to talk to — or at least point me in the right direction.
</p>

<p>
  Would it make sense to find 15 minutes to swap notes? Happy to show you exactly what the ROI
  looks like for a company your size.
</p>

<p>
  No pressure either way — even a quick "not the right time" is genuinely helpful.
</p>

<p>
  Best,<br/>
  <strong>{sender_name}</strong>
</p>

<p style="font-size: 12px; color: #888; margin-top: 32px;">
  You're receiving this because your profile was identified as a good match for our outreach.
  Reply with "unsubscribe" at any time and I'll remove you immediately.
</p>

</body>
</html>"""

    text_body = f"""Hi {first_name},

I came across {company_name} while researching companies doing interesting work in your space,
and I wanted to reach out directly.

We help teams like yours automate the parts of the sales and growth process that eat up the most
time — specifically the sourcing-to-outreach loop. Most of our customers cut their prospecting
time by 60-70% in the first month.

Given your role as {job_title} at {company_name}, I thought you'd be the right person to talk
to — or at least point me in the right direction.

Would it make sense to find 15 minutes to swap notes? Happy to show you exactly what the ROI
looks like for a company your size.

No pressure either way — even a quick "not the right time" is genuinely helpful.

Best,
{sender_name}

---
You're receiving this because your profile was identified as a good match for our outreach.
Reply with "unsubscribe" at any time and I'll remove you immediately.
"""

    return subject, html_body, text_body
