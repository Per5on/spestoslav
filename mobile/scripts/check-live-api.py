"""Record public endpoint status only; never log tokens or response payloads."""

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
base = os.environ.get(
    "EXPO_PUBLIC_API_URL", "https://spestoslav-api.onrender.com"
).rstrip("/")


def check(path):
    start = time.monotonic()
    result = {"endpoint": path}
    try:
        with urlopen(base + path, timeout=15) as response:
            result["status"] = response.status
            response.read(1024)
    except HTTPError as error:
        result["status"] = error.code
    except (OSError, ValueError, HTTPException) as error:
        result["error_type"] = type(error).__name__
    result["seconds"] = round(time.monotonic() - start, 2)
    return result


paths = [
    "/health",
    "/api/v1/localities?q=Sofia",
    "/api/v1/catalog/groceries",
    "/api/v1/catalog/technology",
    "/api/v1/feedback/availability",
    "/ready",
]
with ThreadPoolExecutor(max_workers=6) as pool:
    results = list(pool.map(check, paths))
args.output.write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results))
