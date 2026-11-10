import unittest
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import main
from app.main import GenerateRequest, app, parse_result, require_app_token, unwrap_provider


class BackendContractTests(unittest.TestCase):
    def test_prompt_or_lyrics_is_validated_by_request_model(self):
        request = GenerateRequest(prompt="Cumbia romántica", lyrics="", duration=180)
        self.assertEqual(request.duration, 180)
        self.assertEqual(request.vocal_language, "es")

    def test_generation_requires_prompt_or_lyrics_at_endpoint(self):
        with patch.object(main, "ACE_STEP_BASE_URL", "https://provider.invalid"):
            client = TestClient(app)
            response = client.post(
                "/api/music/generate",
                headers={"Authorization": "Bearer test-token"},
                json={"prompt": "", "lyrics": ""},
            )
        self.assertEqual(response.status_code, 422)

    def test_music_routes_fail_closed_when_backend_token_is_missing(self):
        with patch.object(main, "BACKEND_TOKEN", ""):
            response = TestClient(app).get("/api/music/models")
        self.assertEqual(response.status_code, 503)

    def test_music_routes_reject_wrong_token(self):
        with patch.object(main, "BACKEND_TOKEN", "expected-token"):
            response = TestClient(app).get(
                "/api/music/models",
                headers={"Authorization": "Bearer wrong-token"},
            )
        self.assertEqual(response.status_code, 401)

    def test_parse_provider_result_json_string(self):
        raw = '[{"file":"/v1/audio?path=demo.mp3","status":1,"metas":{"bpm":120}}]'
        parsed = parse_result(raw)
        self.assertEqual(parsed[0]["status"], 1)
        self.assertEqual(parsed[0]["metas"]["bpm"], 120)

    def test_parse_provider_result_invalid_string(self):
        self.assertEqual(parse_result("not-json"), [])

    def test_parse_provider_result_dict(self):
        self.assertEqual(parse_result({"file": "demo.mp3"}), [{"file": "demo.mp3"}])

    def test_provider_errors_are_not_returned_as_success(self):
        with self.assertRaises(HTTPException) as error:
            unwrap_provider({"error": "provider unavailable"})
        self.assertEqual(error.exception.status_code, 502)

    def test_generation_duration_is_bounded(self):
        with self.assertRaises(ValueError):
            GenerateRequest(prompt="song", duration=900)


if __name__ == "__main__":
    unittest.main()
