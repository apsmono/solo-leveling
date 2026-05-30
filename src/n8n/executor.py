"""
Intent → n8n execution orchestrator (Phase 2).

Ties the n8n modules together per the locked decisions:
- D-01: hybrid — keyword match selects a vetted skeleton, the LLM dispatcher
  fills its parameters.
- D-02: no template match → soft decline + log the unmet intent (never a silent
  fallback to fully LLM-authored workflow JSON).
- D-04/D-05/N8N-02: the owner's credentials are synced into n8n before a run.
- D-07: side-effecting workflows pass the RL approval gate at the OWNER'S real
  RL (config), not a hardcoded level.
- D-09/D-10/D-11: silent on success, one automatic retry, then a soft message.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.agents.dispatcher import run_agent
from src.autopilot.governor import Governor, ResponsibilityLevel
from src.core.config import AUTOPILOT_RL_LEVEL, SIGNAL_OWNER_ID
from src.n8n import client as n8n_client
from src.n8n import credentials as n8n_creds
from src.n8n import templates as n8n_templates
from src.n8n.errors import classify_error, soft_error_message

logger = logging.getLogger(__name__)

_MAX_RETRIES = 1  # D-10: one automatic retry before bothering the owner.
_UNMET_INTENTS_PATH = Path("data/unmet_intents.json")
_MAX_UNMET = 100
_TERMINAL_STATUSES = {"success", "error", "crashed", "failed", "canceled"}


async def execute_intent(
    intent: str, params: dict[str, Any], owner_id: str = SIGNAL_OWNER_ID
) -> dict[str, Any]:
    """Resolve an owner intent to an n8n workflow run and return a result dict."""
    skeleton = n8n_templates.match_template(intent)
    if skeleton is None:
        _log_unmet_intent(intent, params)
        return {
            "status": "declined",
            "message": "I can't do that yet — but I've noted it for a future update.",
        }

    # D-01: LLM fills the matched skeleton's parameters.
    workflow_json = _fill_with_llm(intent, skeleton, params)

    # D-07: gate side-effecting workflows FIRST, at the owner's real RL.
    if skeleton.get("side_effecting", False):
        governor = Governor(ResponsibilityLevel(AUTOPILOT_RL_LEVEL))
        allowed, _reason = governor.can_execute(
            "n8n_workflow", {"workflow": skeleton["name"], "intent": intent}
        )
        if not allowed:
            return {
                "status": "needs_approval",
                "message": f"This action needs your approval: {skeleton.get('description', intent)}",
                "approval_context": {"intent": intent, "skeleton": skeleton["id"]},
            }

    # N8N-02 / D-04 / D-05: ensure n8n holds a valid credential before the run.
    integration = skeleton.get("integration")
    if integration:
        try:
            token = _load_integration_token(integration) or {}
            n8n_creds.sync_credential(integration, token, owner_id=owner_id)
        except Exception as e:  # noqa: BLE001 — soften any sync failure for the owner
            logger.warning("Credential sync failed for %s: %s", integration, e)
            error_class = classify_error({"error": str(e)})
            return {
                "status": "error",
                "message": soft_error_message(
                    error_class, intent=intent, integration=integration
                ),
            }

    workflow_id = skeleton.get("n8n_workflow_id")
    try:
        result = n8n_client.trigger_workflow(workflow_id, data=workflow_json)
        execution_id = _extract_execution_id(result)
        logger.info("n8n workflow triggered: id=%s execution=%s", workflow_id, execution_id)
        if execution_id is not None:
            exec_result = await _poll_execution(execution_id)
            if _is_success(exec_result):
                return {"status": "ok", "result": exec_result}
            return await _retry_and_report(workflow_id, workflow_json, exec_result, intent)
        return {"status": "ok", "result": result}
    except Exception as e:  # noqa: BLE001
        return await _retry_and_report(workflow_id, workflow_json, {"error": str(e)}, intent)


def _fill_with_llm(
    intent: str, skeleton: dict[str, Any], params: dict[str, Any]
) -> dict[str, Any]:
    """Use the dispatcher to fill the skeleton's parameters (D-01).

    Falls back to schema defaults on any LLM/parse failure. Explicit caller
    params always win on conflict.
    """
    schema = skeleton.get("parameter_schema", {})
    explicit = dict(params or {})
    if not schema:
        return explicit

    system = (
        "You translate a user request into JSON parameters for an automation. "
        "Return ONLY a JSON object whose keys match the provided parameter schema. "
        "Do not include any prose, comments, or code fences."
    )
    try:
        raw = run_agent(task=intent, context=json.dumps(schema), system=system)
        parsed = _extract_json(raw)
        merged = parsed if isinstance(parsed, dict) else n8n_templates.fill_parameters(
            skeleton, explicit
        )
    except Exception:  # noqa: BLE001
        logger.warning("LLM parameter fill failed; using schema defaults", exc_info=True)
        merged = n8n_templates.fill_parameters(skeleton, explicit)

    merged.update(explicit)
    return merged


def _extract_json(text: str) -> dict[str, Any] | None:
    """Best-effort parse of a JSON object from an LLM response."""
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned)
    except Exception:  # noqa: BLE001
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:  # noqa: BLE001
                return None
    return None


def _extract_execution_id(result: dict[str, Any]) -> Any:
    if not isinstance(result, dict):
        return None
    if result.get("executionId") is not None:
        return result["executionId"]
    if result.get("id") is not None:
        return result["id"]
    data = result.get("data")
    if isinstance(data, dict):
        return data.get("executionId") or data.get("id")
    return None


def _is_success(exec_result: dict[str, Any]) -> bool:
    if not isinstance(exec_result, dict):
        return False
    status = str(exec_result.get("status", "")).lower()
    if status == "success":
        return True
    if exec_result.get("finished") and not exec_result.get("error") and status not in {
        "error",
        "crashed",
        "failed",
    }:
        return True
    return False


async def _poll_execution(execution_id: Any, max_wait: int = 30) -> dict[str, Any]:
    """Poll get_execution until the run reaches a terminal state or times out."""
    last: dict[str, Any] = {}
    for _ in range(max_wait):
        try:
            last = n8n_client.get_execution(execution_id)
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}
        status = str(last.get("status", "")).lower()
        if status in _TERMINAL_STATUSES or last.get("finished"):
            return last
        await asyncio.sleep(1)
    return last


async def _retry_and_report(
    workflow_id: Any,
    workflow_json: dict[str, Any],
    first_result: dict[str, Any],
    intent: str,
) -> dict[str, Any]:
    """Retry once (D-10); if it still fails, return a soft error (D-11)."""
    try:
        result = n8n_client.trigger_workflow(workflow_id, data=workflow_json)
        execution_id = _extract_execution_id(result)
        if execution_id is not None:
            exec_result = await _poll_execution(execution_id)
            if _is_success(exec_result):
                return {"status": "ok", "result": exec_result}
            first_result = exec_result
    except Exception as e:  # noqa: BLE001
        first_result = {"error": str(e)}

    error_class = classify_error(first_result)
    return {"status": "error", "message": soft_error_message(error_class, intent=intent)}


def _load_integration_token(integration: str) -> dict[str, Any] | None:
    """Best-effort read of the owner's token for an integration (D-06)."""
    try:
        if integration in ("gmail", "gdrive"):
            path = Path(os.environ.get("GMAIL_TOKEN_PATH", ".gmail_token.json"))
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
            return None
        if integration == "github":
            from src.core.config import GITHUB_PAT

            return {"access_token": GITHUB_PAT} if GITHUB_PAT else None
        if integration == "notion":
            token = os.environ.get("NOTION_API_TOKEN", "")
            return {"api_key": token} if token else None
        if integration == "telegram":
            from src.core.config import TELEGRAM_BOT_TOKEN

            return {"access_token": TELEGRAM_BOT_TOKEN} if TELEGRAM_BOT_TOKEN else None
        if integration == "discord":
            from src.core.config import DISCORD_BOT_TOKEN

            return {"token": DISCORD_BOT_TOKEN} if DISCORD_BOT_TOKEN else None
    except Exception:  # noqa: BLE001
        logger.warning("Failed to load token for %s", integration, exc_info=True)
    return None


def _log_unmet_intent(intent: str, params: dict[str, Any]) -> None:
    """Append an unmet intent for future template development (D-02)."""
    entries: list[dict[str, Any]] = []
    if _UNMET_INTENTS_PATH.exists():
        try:
            entries = json.loads(_UNMET_INTENTS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            entries = []
    entries.append(
        {
            "intent": intent,
            "params": params,
            "logged_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    _UNMET_INTENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _UNMET_INTENTS_PATH.write_text(
        json.dumps(entries[-_MAX_UNMET:], indent=2), encoding="utf-8"
    )
