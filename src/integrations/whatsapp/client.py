"""
WhatsApp API client.

Thin wrapper around the Meta WhatsApp Cloud API (and Twilio fallback).
Only send_message is implemented for now; extend as needed.

Environment variables required:
    WHATSAPP_PROVIDER        meta | twilio
    META_PHONE_NUMBER_ID
    META_ACCESS_TOKEN
    TWILIO_ACCOUNT_SID       (Twilio fallback)
    TWILIO_AUTH_TOKEN        (Twilio fallback)
    TWILIO_WHATSAPP_NUMBER   (Twilio fallback)
"""

import os
import logging

import httpx

logger = logging.getLogger(__name__)

PROVIDER = os.environ.get("WHATSAPP_PROVIDER", "meta").lower()


def send_message(to: str, body: str) -> None:
    """Send a WhatsApp text message to `to` using the configured provider."""
    if PROVIDER == "twilio":
        _send_twilio(to, body)
    else:
        _send_meta(to, body)


def _send_meta(to: str, body: str) -> None:
    phone_number_id = os.environ["META_PHONE_NUMBER_ID"]
    access_token = os.environ["META_ACCESS_TOKEN"]

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }

    response = httpx.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    logger.info("Message sent via Meta to %s.", to)


def _send_twilio(to: str, body: str) -> None:
    from twilio.rest import Client  # type: ignore

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    from_number = os.environ["TWILIO_WHATSAPP_NUMBER"]

    client = Client(account_sid, auth_token)
    client.messages.create(
        from_=f"whatsapp:{from_number}",
        to=f"whatsapp:{to}",
        body=body,
    )
    logger.info("Message sent via Twilio to %s.", to)
