"""Atomic receipt claims and completion shared by local and remote OCR workers."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import re

from sqlalchemy import and_, or_, select
from .marketplace import ReceiptScan, ReceiptItem
from .workflows import ReceiptJob


def claim_job(db):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=5)
    exhausted = db.scalars(
        select(ReceiptJob)
        .join(ReceiptScan, ReceiptScan.id == ReceiptJob.scan_id)
        .where(
            ReceiptJob.attempts >= 3,
            ReceiptScan.status == "PROCESSING",
            ReceiptJob.claimed_at < cutoff,
        )
        .limit(100)
        .with_for_update(skip_locked=True)
    ).all()
    for job in exhausted:
        db.get(ReceiptScan, job.scan_id).status = "FAILED"
        job.error = "Receipt processing exhausted its retry budget"
    row = db.execute(
        select(ReceiptJob, ReceiptScan)
        .join(ReceiptScan, ReceiptScan.id == ReceiptJob.scan_id)
        .where(
            ReceiptJob.attempts < 3,
            or_(
                ReceiptScan.status == "UPLOADED",
                and_(
                    ReceiptScan.status == "PROCESSING", ReceiptJob.claimed_at < cutoff
                ),
            ),
        )
        .order_by(ReceiptScan.created_at, ReceiptScan.id)
        .limit(1)
        .with_for_update(skip_locked=True)
    ).first()
    if row:
        job, scan = row
        job.attempts += 1
        job.claimed_at = now
        scan.status = "PROCESSING"
    return row


def finish_job(db, job_id, attempt, text=None):
    job = db.scalar(select(ReceiptJob).where(ReceiptJob.id == job_id).with_for_update())
    if not job or job.attempts != attempt:
        return False
    scan = db.get(ReceiptScan, job.scan_id)
    if scan.status != "PROCESSING":
        return False
    if text is None:
        scan.status = "FAILED" if job.attempts >= 3 else "UPLOADED"
        job.error = "Receipt processing failed; verify storage and OCR configuration"
    else:
        scan.extracted_text = text[:100000]
        scan.status = "NEEDS_REVIEW"
        job.error = None
        has_eur = bool(re.search(r"EUR|€|ЕВРО", text, re.I))
        has_bgn = bool(re.search(r"BGN|лв\.?", text, re.I))
        for line in text.splitlines()[:500]:
            # Bulgarian OCR sometimes emits Latin lookalikes (PECTO for РЕСТО).
            heading = line.upper().translate(
                str.maketrans("ABCEHKMOPTXY", "АВСЕНКМОРТХУ")
            )
            if re.search(
                r"^\s*(?:TOTAL|SUBTOTAL|VAT|CHANGE|CASH)\b", line, re.I
            ) or re.search(
                r"^\s*(?:ОБЩО|СУМА|ДДС|РЕСТО|КАРТА|В БРОЙ|ПЛАЩАНЕ)(?:\b|(?=\d))",
                heading,
            ):
                continue
            if re.search(
                r"\b\d+(?:[,.]\d+)?\s*[xх×*]\s*\d+[,.]\d{2}\s*(?:EUR|€|ЕВРО|лв\.?|BGN)?\s*$",
                line,
                re.I,
            ):
                # A separate quantity × unit-price row is not a product line total.
                continue
            match = re.search(
                r"(?<!\d)(\d{1,7}[,.]\d{2})\s*(?:EUR|€|ЕВРО|лв\.?|BGN)?\s*$", line, re.I
            )
            if match and not re.search(r"-\s*\d+[,.]\d{2}", line):
                explicit_eur = bool(re.search(r"(?:EUR|€|ЕВРО)\s*$", line, re.I))
                amount = Decimal(match.group(1).replace(",", "."))
                if amount <= 0:
                    continue
                db.add(
                    ReceiptItem(
                        receipt_scan_id=scan.id,
                        raw_description=line[:400],
                        line_total_eur=amount
                        if explicit_eur or (has_eur and not has_bgn)
                        else None,
                        match_confidence=Decimal("0.2"),
                        status="UNMATCHED",
                    )
                )
    return True
