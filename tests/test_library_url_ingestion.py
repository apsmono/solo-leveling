"""Tests for URL-based library entry ingestion and metadata enrichment."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from src.core import libraries
from src.integrations.web_fetch import detect_platform, fetch_url_metadata
from src.integrations.youtube import extract_video_id, fetch_transcript


class PlatformDetectionTests(unittest.TestCase):
    def test_youtube_watch_url(self) -> None:
        self.assertEqual(detect_platform("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "youtube")

    def test_youtube_short_url(self) -> None:
        self.assertEqual(detect_platform("https://youtu.be/dQw4w9WgXcQ"), "youtube")

    def test_youtube_shorts_url(self) -> None:
        self.assertEqual(detect_platform("https://youtube.com/shorts/abc123def45"), "youtube")

    def test_youtube_mobile_url(self) -> None:
        self.assertEqual(detect_platform("https://m.youtube.com/watch?v=dQw4w9WgXcQ"), "youtube")

    def test_github_repo_url(self) -> None:
        self.assertEqual(detect_platform("https://github.com/apsmono/solo-leveling"), "github")

    def test_github_www_url(self) -> None:
        self.assertEqual(detect_platform("https://www.github.com/torvalds/linux"), "github")

    def test_generic_blog_url(self) -> None:
        self.assertEqual(detect_platform("https://example.com/blog/post"), "generic")

    def test_generic_localhost(self) -> None:
        self.assertEqual(detect_platform("http://localhost:8000/docs"), "generic")


class FetchUrlMetadataTests(unittest.TestCase):
    def test_fetch_youtube_metadata(self) -> None:
        oembed_response = {
            "title": "Test Video Title",
            "author_name": "Test Channel",
            "thumbnail_url": "https://i.ytimg.com/vi/123/hqdefault.jpg",
            "thumbnail_width": 480,
            "thumbnail_height": 360,
            "provider_name": "YouTube",
            "type": "video",
        }
        mock_response = MagicMock()
        mock_response.json.return_value = oembed_response
        mock_response.raise_for_status.return_value = None

        with patch("src.integrations.web_fetch.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            result = fetch_url_metadata("https://www.youtube.com/watch?v=123")

        self.assertEqual(result["platform"], "youtube")
        self.assertEqual(result["title"], "Test Video Title")
        self.assertEqual(result["author"], "Test Channel")
        self.assertEqual(result["source_url"], "https://www.youtube.com/watch?v=123")
        self.assertIn("thumbnail_url", result["extra"])

    def test_fetch_generic_metadata(self) -> None:
        html = (
            '<html><head><title>  My Blog Post  </title>'
            '<meta property="og:description" content="A great article about AI.">'
            '</head><body></body></html>'
        )
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"content-type": "text/html; charset=utf-8"}

        with patch("src.integrations.web_fetch.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            result = fetch_url_metadata("https://example.com/blog/ai-post")

        self.assertEqual(result["platform"], "generic")
        self.assertEqual(result["title"], "My Blog Post")
        self.assertEqual(result["description"], "A great article about AI.")
        self.assertEqual(result["source_url"], "https://example.com/blog/ai-post")

    def test_fetch_generic_metadata_fallback_title(self) -> None:
        html = "<html><head></head><body></body></html>"
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"content-type": "text/html"}

        with patch("src.integrations.web_fetch.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.get.return_value = mock_response

            result = fetch_url_metadata("https://example.com/blog/ai-post")

        self.assertEqual(result["title"], "Ai Post")

    def test_fetch_url_metadata_fallback_on_error(self) -> None:
        with patch("src.integrations.web_fetch.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__enter__.return_value = mock_client
            mock_client.get.side_effect = Exception("Network error")

            result = fetch_url_metadata("https://example.com/fail")

        self.assertEqual(result["platform"], "generic")
        self.assertEqual(result["source_url"], "https://example.com/fail")
        self.assertEqual(result["title"], "https://example.com/fail")


class YouTubeTranscriptTests(unittest.TestCase):
    def test_extract_video_id_watch(self) -> None:
        self.assertEqual(extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_extract_video_id_short(self) -> None:
        self.assertEqual(extract_video_id("https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_extract_video_id_shorts(self) -> None:
        self.assertEqual(extract_video_id("https://youtube.com/shorts/dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_extract_video_id_embed(self) -> None:
        self.assertEqual(extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_extract_video_id_invalid(self) -> None:
        self.assertIsNone(extract_video_id("https://youtube.com/playlist?list=PL123"))

    @patch("youtube_transcript_api.YouTubeTranscriptApi")
    def test_fetch_transcript_success(self, mock_api_class: MagicMock) -> None:
        mock_snippet1 = MagicMock(text="Hello world")
        mock_snippet2 = MagicMock(text="This is a test")
        mock_api = MagicMock()
        mock_api.fetch.return_value = [mock_snippet1, mock_snippet2]
        mock_api_class.return_value = mock_api

        result = fetch_transcript("dQw4w9WgXcQ")
        self.assertEqual(result, "Hello world\nThis is a test")

    @patch("youtube_transcript_api.YouTubeTranscriptApi")
    def test_fetch_transcript_failure_returns_none(self, mock_api_class: MagicMock) -> None:
        mock_api = MagicMock()
        mock_api.fetch.side_effect = Exception("blocked")
        mock_api_class.return_value = mock_api

        result = fetch_transcript("dQw4w9WgXcQ")
        self.assertIsNone(result)


class LibraryUrlCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.original_project_root = libraries._PROJECT_ROOT
        self.original_library_root = libraries._LIBRARY_ROOT
        self.original_index_path = libraries._INDEX_PATH

        temp_root = Path(self.temp_dir.name)
        libraries._PROJECT_ROOT = temp_root
        libraries._LIBRARY_ROOT = temp_root / "library"
        libraries._INDEX_PATH = libraries._LIBRARY_ROOT / "index.json"
        libraries._ensure_library_dirs()

        self.addCleanup(self._restore_globals)

    def _restore_globals(self) -> None:
        libraries._PROJECT_ROOT = self.original_project_root
        libraries._LIBRARY_ROOT = self.original_library_root
        libraries._INDEX_PATH = self.original_index_path

    @patch("src.core.libraries.fetch_url_metadata")
    def test_capture_entry_includes_source_url_in_frontmatter(self, mock_fetch: MagicMock) -> None:
        mock_fetch.return_value = {
            "title": "Test Article",
            "description": "Desc",
            "author": "Author",
            "platform": "generic",
            "source_url": "https://example.com/article",
            "extra": {},
        }

        path = libraries._capture_entry(
            "article",
            "Test Article",
            "Body text here.",
            source_url="https://example.com/article",
        )

        file_path = libraries._PROJECT_ROOT / path
        self.assertTrue(file_path.exists())
        content = file_path.read_text(encoding="utf-8")
        self.assertIn("source_url: https://example.com/article", content)

    @patch("src.core.libraries.fetch_url_metadata")
    def test_build_library_index_includes_source_url(self, mock_fetch: MagicMock) -> None:
        mock_fetch.return_value = {
            "title": "Test Article",
            "description": "Desc",
            "author": "Author",
            "platform": "generic",
            "source_url": "https://example.com/article",
            "extra": {},
        }

        libraries._capture_entry(
            "article",
            "Test Article",
            "Body text here.",
            source_url="https://example.com/article",
        )

        index = libraries._build_library_index()
        entries = index.get("entries", [])
        self.assertTrue(any(e.get("source_url") == "https://example.com/article" for e in entries))

    @patch("src.core.libraries.fetch_url_metadata")
    def test_default_capture_analysis_with_url_enriches_output(self, mock_fetch: MagicMock) -> None:
        mock_fetch.return_value = {
            "title": "YouTube Video",
            "description": "A great video",
            "author": "Creator",
            "platform": "youtube",
            "source_url": "https://youtube.com/watch?v=abc",
            "extra": {"duration": "10:00"},
        }

        result = libraries._default_capture_analysis("https://youtube.com/watch?v=abc", [])

        self.assertEqual(result["title"], "YouTube Video")
        self.assertEqual(result["category"], "article")
        self.assertEqual(result["item_type"], "youtube-research")
        self.assertIn("video-transcript", result["information_to_track"])
        self.assertIn("channel", result["information_to_track"])
        self.assertIn("Source: https://youtube.com/watch?v=abc", result["key_facts"])
        self.assertEqual(result["source_url"], "https://youtube.com/watch?v=abc")

    @patch("src.core.libraries.fetch_url_metadata")
    def test_default_capture_analysis_github_platform(self, mock_fetch: MagicMock) -> None:
        mock_fetch.return_value = {
            "title": "apsmono/solo-leveling",
            "description": "Backend brain",
            "author": "apsmono",
            "platform": "github",
            "source_url": "https://github.com/apsmono/solo-leveling",
            "extra": {"stars": 42, "language": "Python"},
        }

        result = libraries._default_capture_analysis("https://github.com/apsmono/solo-leveling", [])

        self.assertEqual(result["item_type"], "github-research")
        self.assertIn("repo-language", result["information_to_track"])
        self.assertIn("stars", result["information_to_track"])
        self.assertIn("use-case", result["information_to_track"])

    @patch("src.core.libraries.fetch_url_metadata")
    def test_handle_article_with_url_saves_enriched_entry(self, mock_fetch: MagicMock) -> None:
        mock_fetch.return_value = {
            "title": "My Article",
            "description": "Article description",
            "author": "Writer",
            "platform": "generic",
            "source_url": "https://example.com/my-article",
            "extra": {"site_name": "Example Blog"},
        }

        result = libraries._handle_article("article: https://example.com/my-article")

        self.assertIn("Article saved to local library.", result)
        self.assertIn("Platform: generic", result)

        # Verify file was written with source_url
        articles_dir = libraries._LIBRARY_ROOT / "articles"
        files = list(articles_dir.glob("*.md"))
        self.assertEqual(len(files), 1)
        content = files[0].read_text(encoding="utf-8")
        self.assertIn("source_url: https://example.com/my-article", content)
        self.assertIn("My Article", content)

    @patch("src.core.libraries.fetch_url_metadata")
    @patch("src.core.libraries.fetch_transcript")
    def test_capture_research_bundle_with_youtube_includes_transcript(self, mock_transcript: MagicMock, mock_fetch: MagicMock) -> None:
        mock_fetch.return_value = {
            "title": "YouTube Video",
            "description": "A great video",
            "author": "Creator",
            "platform": "youtube",
            "source_url": "https://youtube.com/watch?v=abc123def45",
            "extra": {},
        }
        mock_transcript.return_value = "This is the transcript."

        with patch("src.core.libraries.run_agent", side_effect=RuntimeError("ai unavailable")):
            result = libraries.handle_library_command(
                "add to library: https://youtube.com/watch?v=abc123def45",
                "library_capture",
            )

        self.assertIn("Knowledge capture saved to local library.", result)

        # URL captures are stored in articles/ (not research/)
        bundles = [path for path in (libraries._LIBRARY_ROOT / "articles").iterdir() if path.is_dir()]
        self.assertEqual(len(bundles), 1)
        bundle = bundles[0]

        # Check if transcript file exists
        transcript_path = bundle / "08-transcript.md"
        self.assertTrue(transcript_path.exists())
        self.assertIn("This is the transcript.", transcript_path.read_text(encoding="utf-8"))


class LibraryApiSourceUrlFilterTests(unittest.TestCase):
    def setUp(self) -> None:
        from fastapi.testclient import TestClient
        from src.app import app

        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

    @patch("src.api.deps.verify_id_token")
    def test_list_entries_filter_by_source_url(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get(
            "/api/v1/library/entries?source_url=https://nonexistent-url-12345.com",
            headers={"Authorization": "Bearer valid-token"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["entries"]), 0)


if __name__ == "__main__":
    unittest.main()


class ArticleCommandParsingTests(unittest.TestCase):
    def test_article_command_parses_tags_and_status(self) -> None:
        text = (
            "article: https://example.com/blog-post\n"
            "tags: ai, ml, research\n"
            "status: reading"
        )
        with patch("src.core.libraries.fetch_url_metadata") as mock_fetch:
            mock_fetch.return_value = {
                "title": "Example Blog",
                "description": "A blog post",
                "author": "Writer",
                "platform": "generic",
                "source_url": "https://example.com/blog-post",
                "extra": {},
            }
            result = libraries._handle_article(text)
        self.assertIn("Article saved to local library.", result)
