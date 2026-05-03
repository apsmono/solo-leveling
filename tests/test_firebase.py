"""Unit tests for Firebase auth and Firestore integrations."""

from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

# Inject mock firebase modules before importing our code
_mock_firebase_admin = MagicMock()
_mock_firebase_admin.credentials.Certificate.from_json = MagicMock(return_value=MagicMock())
_mock_firebase_admin.initialize_app = MagicMock(return_value=MagicMock())

_mock_google_cloud = MagicMock()

sys.modules["firebase_admin"] = _mock_firebase_admin
sys.modules["firebase_admin.credentials"] = _mock_firebase_admin.credentials
sys.modules["firebase_admin.auth"] = _mock_firebase_admin.auth
sys.modules["google.cloud"] = _mock_google_cloud
sys.modules["google.cloud.firestore"] = _mock_google_cloud.firestore

from src.integrations.firebase import auth as fb_auth
from src.integrations.firebase import firestore as fb_firestore


class FirebaseAuthTests(unittest.TestCase):
    def setUp(self) -> None:
        fb_auth._FIREBASE_APP = None
        _mock_firebase_admin.initialize_app.reset_mock()
        _mock_firebase_admin.auth.verify_id_token.reset_mock(side_effect=True)

    @patch("src.integrations.firebase.auth.FIREBASE_CREDENTIALS_JSON", '{"type": "service_account"}')
    def test_verify_id_token_success(self) -> None:
        _mock_firebase_admin.auth.verify_id_token.return_value = {"email": "owner@example.com"}
        result = fb_auth.verify_id_token("valid-token")
        self.assertEqual(result["email"], "owner@example.com")

    @patch("src.integrations.firebase.auth.FIREBASE_CREDENTIALS_JSON", '{"type": "service_account"}')
    def test_verify_id_token_invalid_raises_401(self) -> None:
        from fastapi import HTTPException
        _mock_firebase_admin.auth.verify_id_token.side_effect = Exception("bad token")
        with self.assertRaises(HTTPException) as ctx:
            fb_auth.verify_id_token("bad-token")
        self.assertEqual(ctx.exception.status_code, 401)

    @patch("src.integrations.firebase.auth.FIREBASE_CREDENTIALS_JSON", '{"type": "service_account"}')
    @patch("src.integrations.firebase.auth.ALLOWED_USER_EMAIL", "owner@example.com")
    def test_verify_id_token_wrong_email_raises_403(self) -> None:
        from fastapi import HTTPException
        _mock_firebase_admin.auth.verify_id_token.return_value = {"email": "intruder@example.com"}
        with self.assertRaises(HTTPException) as ctx:
            fb_auth.verify_id_token("valid-token")
        self.assertEqual(ctx.exception.status_code, 403)

    @patch("src.integrations.firebase.auth.FIREBASE_CREDENTIALS_JSON", "")
    @patch("src.integrations.firebase.auth.FIREBASE_CREDENTIALS_PATH", "")
    def test_init_firebase_missing_credentials_raises(self) -> None:
        with self.assertRaises(EnvironmentError):
            fb_auth._init_firebase()


class FirebaseFirestoreTests(unittest.TestCase):
    def setUp(self) -> None:
        fb_auth._FIREBASE_APP = None
        fb_firestore._firestore_client = None
        self.mock_client = MagicMock()
        _mock_google_cloud.firestore.client.return_value = self.mock_client

    @patch("src.integrations.firebase.auth.FIREBASE_CREDENTIALS_JSON", '{"type": "service_account"}')
    def test_create_reminder_doc(self) -> None:
        from datetime import datetime
        doc_ref = MagicMock()
        self.mock_client.collection.return_value.document.return_value = doc_ref
        doc_id = fb_firestore.create_reminder_doc("test", datetime.now())
        self.mock_client.collection.assert_called_once_with("reminders")
        doc_ref.set.assert_called_once()
        self.assertEqual(doc_id, doc_ref.id)

    @patch("src.integrations.firebase.auth.FIREBASE_CREDENTIALS_JSON", '{"type": "service_account"}')
    def test_list_pending_reminders(self) -> None:
        mock_doc = MagicMock()
        mock_doc.id = "abc"
        mock_doc.to_dict.return_value = {"message": "hi", "run_at": None}
        self.mock_client.collection.return_value.where.return_value.order_by.return_value.stream.return_value = [mock_doc]
        results = fb_firestore.list_pending_reminders()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "abc")

    @patch("src.integrations.firebase.auth.FIREBASE_CREDENTIALS_JSON", '{"type": "service_account"}')
    def test_mark_reminder_sent(self) -> None:
        fb_firestore.mark_reminder_sent("abc")
        self.mock_client.collection.return_value.document.assert_called_once_with("abc")

    @patch("src.integrations.firebase.auth.FIREBASE_CREDENTIALS_JSON", '{"type": "service_account"}')
    def test_log_command(self) -> None:
        fb_firestore.log_command("hello", "status", "ok")
        self.mock_client.collection.assert_called_with("commands")
        self.mock_client.collection.return_value.add.assert_called_once()

    @patch("src.integrations.firebase.auth.FIREBASE_CREDENTIALS_JSON", '{"type": "service_account"}')
    def test_list_recent_commands(self) -> None:
        mock_doc = MagicMock()
        mock_doc.id = "cmd1"
        mock_doc.to_dict.return_value = {"text": "hello"}
        self.mock_client.collection.return_value.order_by.return_value.limit.return_value.stream.return_value = [mock_doc]
        results = fb_firestore.list_recent_commands(limit=10)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "cmd1")


if __name__ == "__main__":
    unittest.main()
