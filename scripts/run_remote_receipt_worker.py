#!/usr/bin/env python3
"""Run on the approved GitHub workflow. No database or S3 credentials leave Render."""

import argparse
import os
from pathlib import Path
import sys
import time
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.receipt_worker import extract_text


def ensure_ready(client, base):
    # Warm the free API before acquiring a short-lived identity or claiming work.
    # Only this read-only request is retried; claims must not be duplicated.
    for attempt in range(2):
        try:
            response = client.get(base + "/ready", timeout=60)
            if response.status_code == 200:
                return
            if response.status_code not in (502, 503, 504):
                raise RuntimeError(f"API readiness failed: HTTP {response.status_code}")
        except httpx.RequestError:
            pass
        if attempt == 0:
            print("API is not ready yet; retrying the readiness check once")
            time.sleep(2)
    raise RuntimeError("API is unavailable after bounded readiness checks")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-jobs", type=int, default=10)
    args = parser.parse_args()
    if not 1 <= args.max_jobs <= 10:
        parser.error("--max-jobs must be 1..10")
    base = os.environ["API_BASE_URL"].rstrip("/")
    if base != "https://spestoslav-api.onrender.com":
        raise RuntimeError("Unexpected worker API destination")
    audience = base + "/receipt-worker"
    token_url = httpx.URL(os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"])
    if token_url.scheme != "https" or not token_url.host.endswith(
        ".actions.githubusercontent.com"
    ):
        raise RuntimeError("Unexpected GitHub identity endpoint")
    with httpx.Client(timeout=30, follow_redirects=False) as client:
        ensure_ready(client, base)
        processed = 0
        for _ in range(args.max_jobs):
            token_response = client.get(
                token_url.copy_merge_params({"audience": audience}),
                headers={
                    "Authorization": "Bearer "
                    + os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]
                },
            )
            if token_response.status_code != 200:
                raise RuntimeError("Could not obtain GitHub workload identity")
            token = token_response.json()["value"]
            print("::add-mask::" + token)
            headers = {"Authorization": "Bearer " + token}
            response = client.post(
                base + "/internal/receipt-worker/claim", headers=headers, timeout=60
            )
            if response.status_code != 200:
                raise RuntimeError(f"Receipt claim failed: HTTP {response.status_code}")
            job = response.json()["job"]
            if not job:
                break
            print("::add-mask::" + job["lease"])
            scoped = dict(headers, **{"X-Receipt-Lease": job["lease"]})
            text = None
            try:
                with client.stream(
                    "GET",
                    base + "/internal/receipt-worker/jobs/" + job["id"] + "/image",
                    headers=scoped,
                ) as image:
                    if image.status_code != 200:
                        raise RuntimeError("Receipt image unavailable")
                    data = bytearray()
                    for chunk in image.iter_bytes():
                        data.extend(chunk)
                        if len(data) > 8 * 1024 * 1024:
                            raise RuntimeError("Receipt image too large")
                text = extract_text(bytes(data))
            except Exception:
                print("OCR failed; returning the job to bounded retry handling")
            result = client.post(
                base + "/internal/receipt-worker/jobs/" + job["id"] + "/complete",
                headers=scoped,
                json={"text": text},
            )
            if result.status_code != 200:
                raise RuntimeError(
                    f"Receipt completion failed: HTTP {result.status_code}"
                )
            processed += 1
        print(
            f"Receipt worker authenticated; processed {processed} jobs. Extracted data requires review."
        )


if __name__ == "__main__":
    main()
