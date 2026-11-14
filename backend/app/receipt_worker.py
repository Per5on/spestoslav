"""Run `python -m app.receipt_worker --once` or omit --once for a worker loop.

Tesseract must be installed with Bulgarian language data. OCR is untrusted;
extracted receipt lines never publish a current price without human review.
"""

import argparse
import logging
import os
import subprocess
import shutil
import tempfile
import time
from pathlib import Path

from .db import SessionLocal
from .receipts import ReceiptStorage
from .receipt_processing import claim_job, finish_job

logger = logging.getLogger(__name__)


def extract_text(data):
    with tempfile.TemporaryDirectory(prefix="receipt-") as directory:
        path = Path(directory) / "receipt.img"
        path.write_bytes(data)
        result = subprocess.run(
            [
                "tesseract",
                str(path),
                "stdout",
                "-l",
                os.getenv("OCR_LANGUAGES", "bul+eng"),
            ],
            capture_output=True,
            timeout=60,
            check=True,
        )
        return result.stdout.decode("utf-8")[:100000]


def process_one(session_factory=None, ocr=None, storage=None):
    factory = session_factory or SessionLocal
    if factory is None:
        raise RuntimeError("DATABASE_URL is not configured")
    # Preflight dependencies before claiming jobs. A configuration failure must
    # not consume every queued receipt's retry budget.
    storage = storage or ReceiptStorage()
    if ocr is None and not shutil.which("tesseract"):
        raise RuntimeError("Install Tesseract and the configured OCR language data")
    with factory() as db:
        with db.begin():
            row = claim_job(db)
            if not row:
                return False
            job, scan = row
            job_id, attempt, key = job.id, job.attempts, scan.image_storage_key
    try:
        text = (ocr or extract_text)(storage.get(key))
        with factory() as db:
            with db.begin():
                finish_job(db, job_id, attempt, text)
    except Exception:
        logger.warning("Receipt OCR failed for job %s", job_id)
        with factory() as db:
            with db.begin():
                finish_job(db, job_id, attempt)

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--max-jobs", type=int, default=1)
    args = parser.parse_args()
    if not 1 <= args.max_jobs <= 100:
        parser.error("--max-jobs must be between 1 and 100")
    processed = 0
    while True:
        worked = process_one()
        if worked:
            processed += 1
        if args.once and (not worked or processed >= args.max_jobs):
            break
        if not worked:
            time.sleep(5)
