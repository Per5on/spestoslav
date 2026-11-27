"""Export and test the app against an isolated fixture API. No Android packaging."""

import argparse
from contextlib import ExitStack
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
MOBILE = ROOT / "mobile"
API_URL = "http://127.0.0.1:8774"
WEB_URL = "http://127.0.0.1:8775"


def wait_for_server(process, url):
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError(f"Fixture server exited: {url}")
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except URLError:
            time.sleep(0.15)
    raise RuntimeError(f"Fixture server did not become ready: {url}")


def stop(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def verify(output):
    with tempfile.TemporaryDirectory(prefix="spestovnik-fixture-") as temporary, ExitStack() as stack:
        scratch = Path(temporary)
        fixtures = scratch / "images"
        web = scratch / "web"
        subprocess.run(
            [sys.executable, "scripts/generate_mock_images.py", "--output", str(fixtures), "--video"],
            cwd=ROOT, check=True,
        )
        fixture_env = {
            **os.environ,
            "PYTHONPATH": os.pathsep.join([str(ROOT / "backend"), str(ROOT / "backend/tests")]),
            "SPESTOVNIK_SIMULATION": "local-only",
            "DATABASE_URL": "",
            "TEST_DATABASE_URL": "",
            "THUMBNAILS_DATABASE_URL": "",
            "RECEIPT_STORAGE_DIR": str(scratch / "receipts"),
        }
        receipt_settings = ("RECEIPT_S3_BUCKET", "RECEIPT_S3_ENDPOINT", "RECEIPT_WORKER_KEY")
        for setting in receipt_settings:
            fixture_env.pop(setting, None)
        api_log = stack.enter_context((output / "fixture-api.log").open("w"))
        api = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "scenario_api:app", "--host", "127.0.0.1",
             "--port", "8774", "--no-access-log"],
            cwd=ROOT, env=fixture_env, stdout=api_log, stderr=subprocess.STDOUT,
        )
        stack.callback(stop, api)
        wait_for_server(api, API_URL + "/api/v1/localities?q=Sofija")
        subprocess.run(
            ["npm", "exec", "--", "expo", "export", "--clear", "--platform", "web", "--output-dir", str(web)],
            cwd=MOBILE, check=True, env={
                **os.environ, "CI": "1", "EXPO_NO_DOTENV": "1", "EXPO_NO_TELEMETRY": "1",
                "EXPO_PUBLIC_API_URL": API_URL, "EXPO_PUBLIC_SIMULATION_MODE": "true",
            },
        )
        web_log = stack.enter_context((output / "fixture-web.log").open("w"))
        server = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8775", "--bind", "127.0.0.1", "--directory", str(web)],
            cwd=ROOT, stdout=web_log, stderr=subprocess.STDOUT,
        )
        stack.callback(stop, server)
        wait_for_server(server, WEB_URL + "/")
        suites = {
            "legal": [], "menu": ["--fixtures", str(fixtures)], "network": [], "preview007": [],
            "fuel": [], "toolbars": [], "workflows": ["--fixtures", str(fixtures)],
        }
        failures = []
        for suite, options in suites.items():
            result = subprocess.run(
                [sys.executable, f"scripts/test-browser-{suite}.py", "--output-dir", str(output / suite), *options],
                cwd=MOBILE, check=False,
            )
            if result.returncode:
                failures.append(suite)
        if failures:
            raise SystemExit("Failed browser suites: " + ", ".join(failures))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    directory = args.output_dir.resolve() if args.output_dir else Path(tempfile.mkdtemp(prefix="spestovnik-browser-"))
    directory.mkdir(parents=True, exist_ok=True)
    print(f"Browser evidence: {directory}", flush=True)
    verify(directory)
