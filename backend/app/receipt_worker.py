"""Run `python -m app.receipt_worker --once` or omit --once for a worker loop.

Tesseract must be installed with Bulgarian language data. OCR is untrusted;
extracted receipt lines never publish a current price without human review.
"""

import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import logging
import os
import re
import subprocess
import shutil
import tempfile
import time
from pathlib import Path

from sqlalchemy import select, or_, and_
from .db import SessionLocal
from .marketplace import ReceiptScan, ReceiptItem
from .workflows import ReceiptJob
from .receipts import ReceiptStorage

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
    now = datetime.now(timezone.utc)
    with factory() as db:
        with db.begin():
            row = db.execute(
                select(ReceiptJob, ReceiptScan)
                .join(ReceiptScan, ReceiptScan.id == ReceiptJob.scan_id)
                .where(
                    ReceiptJob.attempts < 3,
                    or_(
                        ReceiptScan.status == "UPLOADED",
                        and_(
                            ReceiptScan.status == "PROCESSING",
                            ReceiptJob.claimed_at < now - timedelta(minutes=5),
                        ),
                    ),
                )
                .order_by(ReceiptScan.created_at, ReceiptScan.id)
                .with_for_update(skip_locked=True)
            ).first()
            if not row:
                return False
            job, scan = row
            job.attempts += 1
            job.claimed_at = now
            scan.status = "PROCESSING"
            scan_id = scan.id
            job_id = job.id
            key = scan.image_storage_key
            claimed_attempt = job.attempts
    try:
        text = (ocr or extract_text)(storage.get(key))
        with factory() as db:
            with db.begin():
                job = db.scalar(
                    select(ReceiptJob).where(ReceiptJob.id == job_id).with_for_update()
                )
                if job.attempts != claimed_attempt:
                    return True
                scan = db.get(ReceiptScan, scan_id)
                scan.extracted_text = text
                scan.status = "NEEDS_REVIEW"
                job.error = None
                # One whole candidate line, low confidence, no product match.
                # Ambiguous decimal values remain raw text for the reviewer.
                for line in text.splitlines()[:500]:
                    match = re.search(
                        r"(?<!\d)(\d{1,7}[,.]\d{2})\s*(?:EUR|€)?\s*$", line
                    )
                    if match:
                        value = Decimal(match.group(1).replace(",", "."))
                        db.add(
                            ReceiptItem(
                                receipt_scan_id=scan_id,
                                raw_description=line[:400],
                                line_total_eur=value,
                                match_confidence=Decimal("0.2"),
                                status="UNMATCHED",
                            )
                        )
    except Exception:
        logger.warning("Receipt OCR failed for job %s", job_id)
        with factory() as db:
            with db.begin():
                job = db.scalar(
                    select(ReceiptJob).where(ReceiptJob.id == job_id).with_for_update()
                )
                if job.attempts != claimed_attempt:
                    return True
                scan = db.get(ReceiptScan, scan_id)
                scan.status = "FAILED" if job.attempts >= 3 else "UPLOADED"
                job.error = (
                    "Receipt processing failed; verify storage and OCR configuration"
                )
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
