# Automated Cold-Outreach Pipeline

> One domain in. Four stages. A full outreach engine — zero humans in the loop.

```
company.domain
     │
     ▼
 Ocean.io       → lookalike company domains
     │
     ▼
 Prospeo        → C-suite / VP contacts + LinkedIn URLs
     │
     ▼
 Eazyreach      → verified work emails
     │
     ▼
 Brevo          → personalised outreach emails sent
```

---

## Quick Start

### 1. Prerequisites

- Python 3.10+
- A domain + company email (required for Ocean.io signup)
- API accounts for: Ocean.io, Prospeo, Eazyreach, Brevo

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API keys

```bash
cp .env.example .env
# Edit .env with your real API keys and sender email
```

### 4. Run the pipeline

```bash
# Interactive (prompts for domain)
python main.py

# Pass domain as argument
python main.py stripe.com
```

---

## Account Setup Order

The order matters — Ocean.io requires a company email to sign up.

```
1. Buy / claim domain (Namecheap or GitHub Student Pack)
2. Set up company email  (you@yourdomain.com)
3. Sign up Ocean.io      (requires company email)
4. Sign up Prospeo       (free tier, API included)
5. Sign up Eazyreach     (Vocallabs tops up your credits)
6. Sign up Brevo         (free tier, 300 emails/day)
```

**Reimbursement:** Submit payment screenshot + UPI ID at https://forms.gle/24Sui9bUX9yS3Qxx7

---

## What the Pipeline Does

| Stage | Tool       | Input                  | Output                        |
|-------|------------|------------------------|-------------------------------|
| 1     | Ocean.io   | Seed domain            | Lookalike company domains     |
| 2     | Prospeo    | Company domains        | C-suite contacts + LinkedIn   |
| 3     | Eazyreach  | LinkedIn URLs          | Verified work emails          |
| 4     | Brevo      | Contacts + emails      | Personalised outreach sent    |

---

## Safety Checkpoint

Before any emails are sent, the pipeline pauses and shows you exactly who will receive email and asks for confirmation. Type `y` to proceed, anything else to abort.

---

## Output Files

Each run saves two files:
- `run_YYYYMMDD_HHMMSS.json` — full structured results from all stages
- `pipeline_YYYYMMDD_HHMMSS.log` — detailed execution log

---

## Configuration Options

| Variable          | Default | Description                              |
|-------------------|---------|------------------------------------------|
| `OCEAN_LIMIT`     | 10      | Max lookalike companies from Ocean.io    |
| `PROSPEO_LIMIT`   | 5       | Max decision-makers per company          |
| `RATE_LIMIT_DELAY`| 1.0     | Seconds between API calls (rate safety)  |

---

## Edge Cases Handled

- **Rate limits (429):** Automatic retry with `Retry-After` header respect
- **Missing LinkedIn URLs:** Stage 3 skipped gracefully, prospect still tracked
- **Unresolved emails:** Removed before Stage 4 — no bounces
- **API failures:** Logged and skipped; pipeline continues with remaining data
- **Duplicates:** Deduplicated by LinkedIn URL across companies
- **No results:** Each stage warns and exits cleanly if nothing to process

---

## Project Structure

```
outreach-pipeline/
├── main.py                  # Entry point — orchestrates all stages
├── requirements.txt
├── .env.example             # Copy to .env and fill in keys
├── stages/
│   ├── stage1_ocean.py      # Ocean.io lookalike finder
│   ├── stage2_prospeo.py    # Prospeo decision-maker search
│   ├── stage3_eazyreach.py  # Eazyreach email resolver
│   └── stage4_brevo.py      # Brevo email sender + copy
└── utils/
    ├── config.py            # .env loader + validation
    ├── display.py           # CLI output helpers
    └── http.py              # Retry-aware HTTP session
```

---

## Demo Notes (Interview)

- Run: `python main.py <domain>` — entire pipeline executes live
- Checkpoint will pause before emails fire — type `y` to confirm
- Each stage's output is printed to terminal in real time
- Full JSON results saved automatically for inspection
- If an API key is missing, the pipeline tells you exactly which one
