import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("async_video", ROOT / "examples/async_video.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
VideoAPI = module.VideoAPI
submit_poll_download = module.submit_poll_download


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
    def read(self):
        return self.payload
    def close(self):
        pass


class Recorder:
    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.requests = []
    def __call__(self, request, timeout):
        self.requests.append(request)
        return FakeResponse(self.payloads.pop(0))


class CatalogTests(unittest.TestCase):
    def test_every_row_has_primary_source_and_pricing_shape(self):
        data = json.loads((ROOT / "catalog/models.json").read_text())
        self.assertEqual(data["checked"], "2026-10-07")
        self.assertTrue(data["models"])
        for row in data["models"]:
            self.assertTrue(row["source"].startswith("https://argolink.io/en/models/"))
            self.assertIn("effective_usd_per_unit", row)
            self.assertIn("official_usd_per_unit", row)

    def test_full_async_lifecycle_has_auth_and_user_agent(self):
        recorder = Recorder([b'{"request_id":"job-1"}', b'{"status":"done"}', b'mp4'])
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "out.mp4"
            api = VideoAPI("https://api.test/v1", "secret", recorder)
            result = submit_poll_download("x", api=api, output=output, interval=1, timeout=2)
            self.assertEqual(result["status"], "done")
            self.assertEqual(output.read_bytes(), b"mp4")
            self.assertEqual(recorder.requests[0].get_header("User-agent"), "ai-media-model-workflows/1.0")
            self.assertEqual(recorder.requests[0].get_header("Authorization"), "Bearer secret")
            self.assertEqual(recorder.requests[2].get_header("User-agent"), "ai-media-model-workflows/1.0")

    def test_unknown_status_stops(self):
        recorder = Recorder([b'{"request_id":"job-1"}', b'{"status":"running"}'])
        api = VideoAPI("https://api.test/v1", "secret", recorder)
        with self.assertRaises(module.VideoError):
            api.status("job-1")


if __name__ == "__main__":
    unittest.main()
