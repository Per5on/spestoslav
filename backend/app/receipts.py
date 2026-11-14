"""Private receipt upload and owner-scoped retrieval; OCR runs in a worker."""

from datetime import datetime
import hashlib
from io import BytesIO
import os
from pathlib import Path
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from botocore.config import Config
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form
from PIL import Image, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import current_user, admin_user
from .db import get_db
from .models import StoreBranch
from .marketplace import ReceiptScan, ReceiptItem
from .workflows import ReceiptJob

router = APIRouter(prefix="/api/v1/receipts")
MAX_BYTES = 8 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 20_000_000


class ReceiptStorage:
    def __init__(self):
        self.directory = os.getenv("RECEIPT_STORAGE_DIR", "")
        self.bucket = os.getenv("RECEIPT_S3_BUCKET", "")
        if self.directory:
            # Explicit local development/persistent-disk mode only.
            self.root = Path(self.directory).resolve()
            self.root.mkdir(parents=True, exist_ok=True)
            self.client = None
        elif self.bucket:
            self.client = boto3.client(
                "s3",
                endpoint_url=os.getenv("RECEIPT_S3_ENDPOINT")
                or os.getenv("AWS_ENDPOINT_URL_S3")
                or None,
                config=Config(
                    signature_version="s3v4",
                    s3={"addressing_style": "path"},
                    connect_timeout=5,
                    read_timeout=15,
                    retries={"max_attempts": 2},
                ),
            )
        else:
            raise HTTPException(503, "Receipt object storage is not configured")

    def path(self, key):
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("Invalid object key")
        return path

    def put(self, key, data, content_type):
        if self.client:
            self.client.put_object(
                Bucket=self.bucket, Key=key, Body=data, ContentType=content_type
            )
        else:
            path = self.path(key)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                handle.write(data)

    def get(self, key):
        if self.client:
            stream = self.client.get_object(Bucket=self.bucket, Key=key)["Body"]
            try:
                data = stream.read(MAX_BYTES + 1)
            finally:
                stream.close()
        else:
            with self.path(key).open("rb") as handle:
                data = handle.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("Receipt is too large")
        return data

    def delete(self, key):
        if self.client:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        else:
            self.path(key).unlink(missing_ok=True)


@router.post("", status_code=202)
async def upload_receipt(
    file: UploadFile = File(),
    branch_id: uuid.UUID | None = Form(default=None),
    principal=Depends(current_user),
    db: Session = Depends(get_db),
):
    if branch_id:
        branch = db.get(StoreBranch, branch_id)
        if not branch or not branch.active:
            raise HTTPException(422, "Unknown or inactive branch")
    data = await file.read(MAX_BYTES + 1)
    await file.close()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "Receipt exceeds 8 MiB")
    try:
        with Image.open(BytesIO(data)) as image:
            if image.width * image.height > Image.MAX_IMAGE_PIXELS:
                raise ValueError()
            image.verify()
            format = image.format
        if format not in ("JPEG", "PNG", "WEBP"):
            raise ValueError()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise HTTPException(422, "Upload a valid JPEG, PNG or WebP image") from None
    key = (
        "receipts/"
        + hashlib.sha256(principal.subject.encode()).hexdigest()
        + "/"
        + uuid.uuid4().hex
        + "."
        + format.lower()
    )
    storage = ReceiptStorage()
    try:
        storage.put(
            key, data, "image/" + ("jpeg" if format == "JPEG" else format.lower())
        )
    except (BotoCoreError, ClientError, OSError):
        raise HTTPException(503, "Receipt storage is unavailable") from None
    scan = ReceiptScan(image_storage_key=key, branch_id=branch_id, status="UPLOADED")
    try:
        db.add(scan)
        db.flush()
        db.add(ReceiptJob(scan_id=scan.id, owner_subject=principal.subject))
        db.commit()
    except Exception:
        db.rollback()
        storage.delete(key)
        raise
    return {"id": str(scan.id), "status": scan.status}


@router.get("/{scan_id}")
def receipt(
    scan_id: uuid.UUID, principal=Depends(current_user), db: Session = Depends(get_db)
):
    row = db.execute(
        select(ReceiptJob, ReceiptScan)
        .join(ReceiptScan, ReceiptScan.id == ReceiptJob.scan_id)
        .where(
            ReceiptJob.scan_id == scan_id, ReceiptJob.owner_subject == principal.subject
        )
    ).first()
    if not row:
        raise HTTPException(404, "Receipt not found")
    job, scan = row
    items = db.scalars(
        select(ReceiptItem)
        .where(ReceiptItem.receipt_scan_id == scan.id)
        .order_by(ReceiptItem.id)
    ).all()
    return {
        "id": str(scan.id),
        "status": scan.status,
        "error": job.error,
        "extracted_text": scan.extracted_text,
        "items": [
            {
                "id": str(i.id),
                "description": i.raw_description,
                "line_total_eur": str(i.line_total_eur)
                if i.line_total_eur is not None
                else None,
                "status": i.status,
            }
            for i in items
        ],
    }


@router.post("/{scan_id}/items/{item_id}/submit-price", status_code=201)
def submit_receipt_price(
    scan_id: uuid.UUID,
    item_id: uuid.UUID,
    payload: dict,
    principal=Depends(current_user),
    db: Session = Depends(get_db),
):
    from .write_api import PriceInput, enqueue, submission_view
    from pydantic import ValidationError

    job = db.scalar(
        select(ReceiptJob).where(
            ReceiptJob.scan_id == scan_id, ReceiptJob.owner_subject == principal.subject
        )
    )
    scan = db.get(ReceiptScan, scan_id) if job else None
    item = (
        db.scalar(
            select(ReceiptItem).where(
                ReceiptItem.id == item_id, ReceiptItem.receipt_scan_id == scan_id
            )
        )
        if job
        else None
    )
    if not job or not scan or not item:
        raise HTTPException(404, "Receipt item not found")
    if scan.status != "NEEDS_REVIEW":
        raise HTTPException(409, "Receipt extraction is not ready for review")
    try:
        data = PriceInput.model_validate(
            dict(payload, source_reference=f"receipt:{scan_id}:item:{item_id}")
        )
    except ValidationError:
        raise HTTPException(
            422, "Provide a product, branch, positive unit price and a future expiry"
        ) from None
    if scan.branch_id and scan.branch_id != data.branch_id:
        raise HTTPException(422, "Branch does not match receipt")
    row, cache = enqueue(db, data, principal, "receipt-item:" + str(item_id), "RECEIPT")
    item.product_id = data.product_id
    item.status = "PENDING_REVIEW"
    db.commit()
    return submission_view(row, cache)
