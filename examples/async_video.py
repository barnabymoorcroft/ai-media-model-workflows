"""A bounded submit -> status -> content example for the catalog."""
from __future__ import annotations

import json
import os
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, Optional

BASE = "https://argolink.io/v1"
USER_AGENT = "ai-media-model-workflows/1.0"
STATUSES = {"pending", "done", "failed", "expired"}


class VideoError(RuntimeError):
    pass


class VideoAPI:
    def __init__(self, base: str = BASE, key: Optional[str] = None, opener: Optional[Callable[..., Any]] = None):
        self.base = base.rstrip("/")
        self.key = key or os.environ.get("VIDEO_API_KEY")
        self._open = opener or urllib.request.urlopen

    def request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, *, binary: bool = False) -> Any:
        if not self.key:
            raise VideoError("set VIDEO_API_KEY in the environment")
        data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
        headers = {"Authorization": f"Bearer {self.key}", "User-Agent": USER_AGENT}
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            response = self._open(request, timeout=90)
            try:
                raw = response.read()
            finally:
                response.close()
        except urllib.error.HTTPError as error:
            detail = error.read(4096).decode("utf-8", errors="replace").replace(self.key, "[redacted]")
            raise VideoError(f"{method} {path} HTTP {error.code}: {detail[:300]}") from None
        if binary:
            return raw
        try:
            result = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise VideoError(f"{method} {path} returned invalid JSON") from error
        if not isinstance(result, dict):
            raise VideoError(f"{method} {path} returned a non-object")
        return result

    def submit(self, model: str, prompt: str, duration: int = 5, resolution: str = "720p") -> str:
        result = self.request("POST", "/videos/generations", {
            "model": model, "prompt": prompt, "duration": duration,
            "resolution": resolution, "aspect_ratio": "16:9", "generate_audio": True,
        })
        request_id = result.get("request_id")
        if not isinstance(request_id, str) or not request_id:
            raise VideoError("submit response has no request_id")
        return request_id

    def status(self, request_id: str) -> Dict[str, Any]:
        result = self.request("GET", f"/videos/{request_id}")
        if result.get("status") not in STATUSES:
            raise VideoError(f"unknown status {result.get('status')!r}")
        return result

    def download(self, request_id: str, destination: Path) -> None:
        if destination.exists():
            raise FileExistsError(str(destination))
        raw = self.request("GET", f"/videos/{request_id}/content", binary=True)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".video-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(raw)
            handle.flush()
        try:
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)


def submit_poll_download(
    prompt: str,
    *,
    model: str = "seedance-2.5",
    duration: int = 5,
    resolution: str = "720p",
    output: Path = Path("output.mp4"),
    interval: float = 10.0,
    timeout: float = 1800.0,
    api: Optional[VideoAPI] = None,
) -> Dict[str, Any]:
    """Submit once, poll explicitly, and download only after done."""
    if interval <= 0 or timeout <= 0:
        raise ValueError("interval and timeout must be positive")
    api = api or VideoAPI()
    request_id = api.submit(model, prompt, duration, resolution)
    deadline = time.monotonic() + timeout
    while True:
        state = api.status(request_id)
        if state["status"] == "done":
            api.download(request_id, output)
            return {"request_id": request_id, "status": "done", "output": str(output)}
        if state["status"] in {"failed", "expired"}:
            return {"request_id": request_id, "status": state["status"], "error": state.get("error")}
        if time.monotonic() + interval > deadline:
            return {"request_id": request_id, "status": "resume"}
        time.sleep(interval)


if __name__ == "__main__":
    print(submit_poll_download("A sunrise over a quiet harbor."))
