import unittest

from app.main import GenerateRequest, parse_result


class BackendContractTests(unittest.TestCase):
    def test_prompt_or_lyrics_is_validated_by_endpoint_contract(self):
        request = GenerateRequest(prompt="Cumbia romántica", lyrics="", duration=180)
        self.assertEqual(request.duration, 180)
        self.assertEqual(request.vocal_language, "es")

    def test_parse_provider_result_json_string(self):
        raw = '[{"file":"/v1/audio?path=demo.mp3","status":1,"metas":{"bpm":120}}]'
        parsed = parse_result(raw)
        self.assertEqual(parsed[0]["status"], 1)
        self.assertEqual(parsed[0]["metas"]["bpm"], 120)

    def test_parse_provider_result_invalid_string(self):
        self.assertEqual(parse_result("not-json"), [])

    def test_parse_provider_result_dict(self):
        self.assertEqual(parse_result({"file":"demo.mp3"}), [{"file":"demo.mp3"}])


if __name__ == "__main__":
    unittest.main()
