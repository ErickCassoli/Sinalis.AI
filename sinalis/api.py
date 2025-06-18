"""Utility for sending signals to an external HTTP API."""

from typing import Mapping

import requests

from .config import API_ENDPOINT


def send_signal(payload: Mapping[str, object]) -> None:
    """Send signal data to configured API endpoint if available."""
    if not API_ENDPOINT:
        return
    try:
        response = requests.post(API_ENDPOINT, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as exc:  # network or HTTP error
        print("Failed to send signal:", exc)
