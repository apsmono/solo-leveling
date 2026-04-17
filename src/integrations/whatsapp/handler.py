"""
WhatsApp webhook handler.

Receives inbound messages from Meta WhatsApp Cloud API or Twilio.
Validates the sender, passes the message to the router, and sends the reply.

Usage:
    Run with any WSGI server, e.g.:
        uvicorn handler:app --port 8000

Environment variables required:
    See src/integrations/whatsapp/README.md
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Any

# FastAPI is used as the webhook server. Install with: pip install fastapi uvicorn httpx
from fastapi import FastAPI, Request, Response, HTTPException

from src.core.router import route_command
from src.core.scheduler import shutdown_scheduler, start_scheduler
from src.integrations.whatsapp.client import send_message

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(lifespan=lifespan)

OWNER_NUMBER = os.environ.get("WHATSAPP_OWNER_NUMBER", "")
PROVIDER = os.environ.get("WHATSAPP_PROVIDER", "meta").lower()
META_VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN", "")


# ---------------------------------------------------------------------------
# Meta webhook verification (GET)
# ---------------------------------------------------------------------------

@app.get("/webhook/whatsapp")
async def verify_webhook(request: Request) -> Response:
    """Meta sends a GET request to verify the webhook on initial setup."""
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == META_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified.")
        return Response(content=challenge, media_type="text/plain")

    raise HTTPException(status_code=403, detail="Webhook verification failed.")


# ---------------------------------------------------------------------------
# Inbound message (POST)
# ---------------------------------------------------------------------------

@app.post("/webhook/whatsapp")
async def receive_message(request: Request) -> dict[str, Any]:
    """Process an inbound WhatsApp message."""
    payload = await request.json()

    sender, text = _extract_message(payload)

    if not sender or not text:
        # Not a user-text message (could be a status update etc.) — ignore silently.
        return {"status": "ignored"}

    if sender != OWNER_NUMBER:
        # Security: discard messages from any number that is not the owner.
        logger.warning("Message from unknown number %s ignored.", sender)
        return {"status": "unauthorized"}

    logger.info("Command received from owner: %s", text)

    reply = route_command(text)
    send_message(to=sender, body=reply)

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_message(payload: dict) -> tuple[str, str]:
    """
    Extract sender phone number and message text from a Meta Cloud API payload.
    Returns ("", "") when the payload does not contain a user text message.
    """
    try:
        entry = payload["entry"][0]
        change = entry["changes"][0]
        value = change["value"]
        message = value["messages"][0]
        sender = message["from"]
        text = message["text"]["body"]
        return sender, text
    except (KeyError, IndexError):
        return "", ""
