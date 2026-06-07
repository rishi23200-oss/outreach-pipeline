"""
Configuration loader — reads API keys from .env or environment variables.
"""

import os
import sys
from pathlib import Path


def load_config() -> dict:
    """Load configuration from .env file or environment variables."""
    env_path = Path(".env")
    if env_path.exists():
        _load_env_file(env_path)

    required = {
        "OCEAN_API_KEY": "Ocean.io API key",
        "PROSPEO_API_KEY": "Prospeo API key",
        "BREVO_API_KEY": "Brevo (Sendinblue) API key",
        "SENDER_EMAIL": "Your verified sender email address",
        "SENDER_NAME": "Your name / company name",
    }

    config = {}
    missing = []

    for key, description in required.items():
        value = os.environ.get(key, "").strip()
        if not value:
            missing.append(f"  {key}  ({description})")
        else:
            config[key.lower()] = value

    if missing:
        print("\n  ✗ Missing required environment variables:\n")
        for m in missing:
            print(m)
        print("\n  Copy .env.example → .env and fill in your keys.\n")
        sys.exit(1)

    # Optional settings with defaults
    config["ocean_limit"] = int(os.environ.get("OCEAN_LIMIT", "10"))
    config["prospeo_limit"] = int(os.environ.get("PROSPEO_LIMIT", "5"))
    config["rate_limit_delay"] = float(os.environ.get("RATE_LIMIT_DELAY", "1.0"))

    return config


def _load_env_file(path: Path):
    """Parse a .env file and set variables into os.environ."""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
