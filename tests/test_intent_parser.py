"""
Test stubs for Phase 3: Knowledge Library — Intent Parser (Wave 0).

These tests define the contract for src.core.intent_parser:
- parse_intent(text) -> {"intent": str, "params": dict, "confidence": float}

All tests run offline (mocked LLM calls).
"""

from __future__ import annotations

import asyncio
import json
import os
import unittest
from unittest.mock import patch

from dotenv import load_dotenv

load_dotenv()

# Conditional import — module does not exist yet in Wave 0
_try_imported = False
_intent_parser = None

try:
    from src.core import intent_parser as _intent_parser

    _try_imported = True
except ImportError:
    pass


@unittest.skipUnless(_try_imported, "src.core.intent_parser not yet implemented — skipping")
class IntentParserTests(unittest.TestCase):
    """Contract tests for src.core.intent_parser."""

    def test_parse_intent_returns_structured_dict(self) -> None:
        """parse_intent returns a dict with intent, params, and confidence keys."""
        from src.core.intent_parser import parse_intent

        async def _run() -> None:
            mock_response = json.dumps({
                "intent": "library_search",
                "params": {"query": "ai"},
                "confidence": 0.95,
            })

            with patch("src.core.intent_parser.run_agent", return_value=mock_response):
                result = await parse_intent("search for ai topics")

            self.assertIsInstance(result, dict)
            self.assertIn("intent", result)
            self.assertIn("params", result)
            self.assertIn("confidence", result)

        asyncio.run(_run())

    def test_parse_intent_library_search(self) -> None:
        """parse_intent correctly extracts library_search intent."""
        from src.core.intent_parser import parse_intent

        async def _run() -> None:
            mock_response = json.dumps({
                "intent": "library_search",
                "params": {"query": "machine learning"},
                "confidence": 0.92,
            })

            with patch("src.core.intent_parser.run_agent", return_value=mock_response):
                result = await parse_intent("find machine learning in my library")

            self.assertEqual(result["intent"], "library_search")
            self.assertEqual(result["params"]["query"], "machine learning")

        asyncio.run(_run())

    def test_parse_intent_park_distraction(self) -> None:
        """parse_intent correctly extracts park_distraction intent."""
        from src.core.intent_parser import parse_intent

        async def _run() -> None:
            mock_response = json.dumps({
                "intent": "park_distraction",
                "params": {"text": "remember to buy milk"},
                "confidence": 0.88,
            })

            with patch("src.core.intent_parser.run_agent", return_value=mock_response):
                result = await parse_intent("park this thought: remember to buy milk")

            self.assertEqual(result["intent"], "park_distraction")

        asyncio.run(_run())

    def test_parse_intent_malformed_json_fallback(self) -> None:
        """Malformed JSON from run_agent falls back to keyword _detect_intent."""
        from src.core.intent_parser import parse_intent

        async def _run() -> None:
            with patch("src.core.intent_parser.run_agent", return_value="not valid json"):
                with patch("src.core.intent_parser._detect_intent", return_value="unknown"):
                    result = await parse_intent("some random text")

            self.assertEqual(result["intent"], "unknown")
            self.assertIn("params", result)
            self.assertEqual(result["confidence"], 0.3)

        asyncio.run(_run())

    def test_parse_intent_run_agent_failure_fallback(self) -> None:
        """Exception from run_agent falls back to keyword detection."""
        from src.core.intent_parser import parse_intent

        async def _run() -> None:
            with patch("src.core.intent_parser.run_agent", side_effect=RuntimeError("LLM unavailable")):
                with patch("src.core.intent_parser._detect_intent", return_value="ask_ai"):
                    result = await parse_intent("what is the weather")

            self.assertEqual(result["intent"], "ask_ai")
            self.assertIn("params", result)
            self.assertIsInstance(result["params"], dict)

        asyncio.run(_run())

    def test_parse_intent_preserves_original_text_in_params(self) -> None:
        """Fallback includes the original text in params."""
        from src.core.intent_parser import parse_intent

        async def _run() -> None:
            original_text = "this is my important thought"

            with patch("src.core.intent_parser.run_agent", side_effect=Exception("boom")):
                with patch("src.core.intent_parser._detect_intent", return_value="unknown"):
                    result = await parse_intent(original_text)

            self.assertIn("text", result["params"])
            self.assertEqual(result["params"]["text"], original_text)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
