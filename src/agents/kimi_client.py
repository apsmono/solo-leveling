"""
Kimi API client via LiteLLM.

Uses the existing litellm_config.yaml at the project root.
Exposes the same interface as the Gemini dispatcher so the autopilot
can swap providers without changing call sites.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "litellm_config.yaml"


def _load_config() -> dict[str, Any]:
    """Load litellm_config.yaml and return the first model entry."""
    try:
        import yaml
    except ImportError:
        logger.warning("PyYAML not installed; cannot parse litellm_config.yaml")
        return {}

    if not _CONFIG_PATH.exists():
        logger.warning("litellm_config.yaml not found at %s", _CONFIG_PATH)
        return {}

    try:
        raw = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8"))
        model_list = raw.get("model_list", [])
        if not model_list:
            return {}
        return model_list[0]
    except Exception:
        logger.exception("Failed to parse litellm_config.yaml")
        return {}


def run_agent(task: str, context: str = "", system: str = "", tools: list[dict[str, Any]] | None = None) -> str:
    """
    Run a task through the Kimi API via LiteLLM.

    Args:
        task:    The instruction or question for the agent.
        context: Background text to reason over.
        system:  Custom system prompt.
        tools:   Optional list of tool schemas for function calling.

    Returns:
        The agent's response as a plain string.
    """
    try:
        import litellm
    except ImportError:
        raise EnvironmentError("litellm is not installed. Run: pip install litellm")

    config = _load_config()
    litellm_params = config.get("litellm_params", {})

    model = litellm_params.get("model", "moonshot/kimi-k2.6")
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        raise EnvironmentError("KIMI_API_KEY is not set.")

    api_base = litellm_params.get("api_base", "https://api.moonshot.ai/v1")
    temperature = litellm_params.get("temperature", 0.1)
    max_tokens = litellm_params.get("max_tokens", 8192)
    extra_headers = litellm_params.get("extra_headers", {})

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    if context:
        messages.append({"role": "user", "content": f"Context:\n{context}\n\nTask:\n{task}"})
    else:
        messages.append({"role": "user", "content": task})

    try:
        response = litellm.completion(
            model=model,
            messages=messages,
            api_key=api_key,
            api_base=api_base,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers=extra_headers,
            tools=tools,
            drop_params=True,
        )
        content = response.choices[0].message.content or ""
        logger.info("Kimi agent responded (%d chars).", len(content))
        return content.strip()
    except Exception:
        logger.exception("Kimi API call failed")
        raise
