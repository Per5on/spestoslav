"""Account erasure for people who registered through the mobile sign-in bridge.

Order matters and every step is safe to retry:
1. confirm the provider session belongs to the authenticated principal;
2. refuse while an OCR job is running (same rule as single-receipt deletion);
3. erase private receipts, their stored images and OCR text;
4. delete unreviewed contributions and unlink reviewed ones from the person;
5. ask the identity provider to delete the sign-in account.

Reviewed price/identification outcomes stay as anonymous catalogue provenance;
only the link to the person is removed.
"""

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from botocore.exceptions import BotoCoreError, ClientError

from .auth import Principal, current_user
from .db import get_db
from .marketplace import PriceCache, ReceiptScan
from .mobile_auth import upstream
from .receipts import ReceiptStorage, delete_receipt_rows
from .workflows import ProductIdentificationRequest, ReceiptJob, ReviewSubmission

router = APIRouter(prefix="/api/v1/account")


def _erase_receipts(db: Session, subject: str) -> None:
    rows = db.execute(
        select(ReceiptJob, ReceiptScan)
        .join(ReceiptScan, ReceiptScan.id == ReceiptJob.scan_id)
        .where(ReceiptJob.owner_subject == subject)
        .with_for_update()
    ).all()
    if not rows:
        return
    if any(scan.status == "PROCESSING" for _, scan in rows):
        raise HTTPException(409, "Wait for receipt processing to finish")
    # Tombstone first so an interrupted run never re-queues OCR or serves a broken image.
    scans = [(scan.id, scan.image_storage_key) for _, scan in rows]
    for _, scan in rows:
        scan.status = "DELETING"
    db.commit()
    try:
        storage = ReceiptStorage()
        for _, key in scans:
            storage.delete(key)
    except (BotoCoreError, ClientError, OSError):
        raise HTTPException(503, "Receipt storage unavailable") from None
    delete_receipt_rows(db, [scan_id for scan_id, _ in scans])
    db.commit()


def _erase_contributions(db: Session, subject: str) -> None:
    pseudonym = "deleted:" + uuid.uuid4().hex
    submissions = db.execute(
        select(ReviewSubmission, PriceCache)
        .join(PriceCache, PriceCache.id == ReviewSubmission.cache_id)
        .where(ReviewSubmission.owner_subject == subject)
    ).all()
    for submission, cache in submissions:
        if cache.status == "PENDING":
            db.delete(submission)
            db.flush()
            db.delete(cache)
        else:
            submission.owner_subject = pseudonym
    requests = db.scalars(
        select(ProductIdentificationRequest).where(
            ProductIdentificationRequest.owner_subject == subject
        )
    ).all()
    for request in requests:
        if request.status == "PENDING":
            db.delete(request)
        else:
            request.owner_subject = pseudonym
    db.commit()


@router.delete("", status_code=204)
def delete_account(
    principal: Principal = Depends(current_user),
    db: Session = Depends(get_db),
    x_auth_session: str = Header(min_length=1, max_length=2048),
):
    if principal.role != "user":
        raise HTTPException(403, "Service and administrator identities cannot use this route")
    data, _ = upstream("/get-session", session=x_auth_session)
    user = (data or {}).get("user") or {}
    if user.get("id") != principal.subject:
        raise HTTPException(403, "Session does not belong to this account")
    _erase_receipts(db, principal.subject)
    _erase_contributions(db, principal.subject)
    try:
        result, _ = upstream("/delete-user", "POST", session=x_auth_session, payload={})
        if not isinstance(result, dict) or (
            result.get("success") is not True or result.get("message") != "User deleted"
        ):
            raise HTTPException(502, "Identity provider did not confirm deletion")
    except HTTPException:
        # Private data is already erased and a retry is safe; never imply the account is gone.
        raise HTTPException(
            502,
            "Your data was erased but the sign-in account could not be removed. Try again later.",
        ) from None
    return Response(status_code=204, headers={"Cache-Control": "no-store"})
