"""
Tests for Phase 3: Knowledge Library — Intent Parser.

These tests verify src.core.intent_parser:
- parse_intent(text) -> {"intent": str, "params": dict, "confidence": float}

All tests run offline (mocked LLM calls).
"""

from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from dotenv import load_dotenv

load_dotenv()

from src.core.intent_parser import parse_intent


class IntentParserTests(unittest.TestCase):
    """Contract tests for src.core.intent_parser."""

    def test_parse_intent_returns_structured_dict(self) -> None:
        """parse_intent returns a dict with intent, params, and confidence keys."""
        mock_response = json.dumps({
            "intent": "library_search",
            "params": {"query": "ai"},
            "confidence": 0.95,
        })

        with patch("src.core.intent_parser.run_agent", return_value=mock_response):
            result = parse_intent("search for ai topics")

        self.assertIsInstance(result, dict)
        self.assertIn("intent", result)
        self.assertIn("params", result)
        self.assertIn("confidence", result)

    def test_parse_intent_library_search(self) -> None:
        """parse_intent correctly extracts library_search intent."""
        mock_response = json.dumps({
            "intent": "library_search",
            "params": {"query": "machine learning"},
            "confidence": 0.92,
        })

        with patch("src.core.intent_parser.run_agent", return_value=mock_response):
            result = parse_intent("find machine learning in my library")

        self.assertEqual(result["intent"], "library_search")
        self.assertEqual(result["params"]["query"], "machine learning")

    def test_parse_intent_park_distraction(self) -> None:
        """parse_intent correctly extracts park_distraction intent."""
        mock_response = json.dumps({
            "intent": "park_distraction",
            "params": {"text": "remember to buy milk"},
            "confidence": 0.88,
        })

        with patch("src.core.intent_parser.run_agent", return_value=mock_response):
            result = parse_intent("park this thought: remember to buy milk")

        self.assertEqual(result["intent"], "park_distraction")

    def test_parse_intent_malformed_json_fallback(self) -> None:
        """Malformed JSON from run_agent falls back to keyword _detect_intent."""
        with patch("src.core.intent_parser.run_agent", return_value="not valid json"):
            with patch("src.core.router._detect_intent", return_value="unknown"):
                result = parse_intent("some random text")

        self.assertEqual(result["intent"], "unknown")
        self.assertIn("params", result)
        self.assertEqual(result["confidence"], 0.3)

    def test_parse_intent_run_agent_failure_fallback(self) -> None:
        """Exception from run_agent falls back to keyword detection."""
        with patch("src.core.intent_parser.run_agent", side_effect=RuntimeError("LLM unavailable")):
            with patch("src.core.router._detect_intent", return_value="ask_ai"):
                result = parse_intent("what is the weather")

        self.assertEqual(result["intent"], "ask_ai")
        self.assertIn("params", result)
        self.assertIsInstance(result["params"], dict)

    def test_parse_intent_preserves_original_text_in_params(self) -> None:
        """Fallback includes the original text in params."""
        original_text = "this is my important thought"

        with patch("src.core.intent_parser.run_agent", side_effect=Exception("boom")):
            with patch("src.core.router._detect_intent", return_value="unknown"):
                result = parse_intent(original_text)

        self.assertIn("text", result["params"])
        self.assertEqual(result["params"]["text"], original_text)

    def test_parse_intent_validates_intent(self) -> None:
        """Invalid intent from LLM is coerced to 'unknown'."""
        mock_response = json.dumps({
            "intent": "hax",
            "params": {"query": "something"},
            "confidence": 0.99,
        })

        with patch("src.core.intent_parser.run_agent", return_value=mock_response):
            result = parse_intent("some random text")

        self.assertEqual(result["intent"], "unknown")

    def test_parse_intent_confidence_default(self) -> None:
        """Missing confidence defaults to 0.5."""
        mock_response = json.dumps({
            "intent": "library_search",
            "params": {"query": "test"},
        })

        with patch("src.core.intent_parser.run_agent", return_value=mock_response):
            result = parse_intent("search test")

        self.assertEqual(result["confidence"], 0.5)

    def test_parse_intent_strips_code_fences(self) -> None:
        """LLM response wrapped in markdown code fences is handled."""
        mock_response = "```json\n" + json.dumps({
            "intent": "library_search",
            "params": {"query": "code fences"},
            "confidence": 0.90,
        }) + "\n```"

        with patch("src.core.intent_parser.run_agent", return_value=mock_response):
            result = parse_intent("search code fences")

        self.assertEqual(result["intent"], "library_search")
        self.assertEqual(result["params"]["query"], "code fences")


if __name__ == "__main__":
    unittest.main()
