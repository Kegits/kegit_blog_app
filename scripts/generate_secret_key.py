#!/usr/bin/env python3
"""Print a Django-compatible SECRET_KEY to stdout.

Usage:
  python scripts/generate_secret_key.py

Copy the printed key into your `.env` as SECRET_KEY=the_value
"""
import secrets
try:
    from django.core.management.utils import get_random_secret_key
except Exception:
    get_random_secret_key = None


def main() -> None:
    if get_random_secret_key:
        print(get_random_secret_key())
    else:
        # fallback
        print(secrets.token_urlsafe(50))


if __name__ == "__main__":
    main()
