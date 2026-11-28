"""Least-privilege GitHub workload identity for OCR, with no repository secrets."""

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import bearer, jwks_client
from .db import get_db
from .marketplace import ReceiptScan
from .receipts import ReceiptStorage
from .receipt_processing import claim_job, finish_job
from .workflows import ReceiptJob

router = APIRouter(prefix="/internal/receipt-worker")
ISSUER = "https://token.actions.githubusercontent.com"


def github_worker(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if os.getenv("RECEIPT_WORKER_OIDC_ENABLED") != "true":
        raise HTTPException(503, "Receipt worker is not enabled")
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "GitHub workload identity required")
    audience = os.getenv("RECEIPT_WORKER_AUDIENCE")
    if not audience:
        raise HTTPException(503, "Receipt worker audience is not configured")
    try:
        key = jwks_client(ISSUER + "/.well-known/jwks").get_signing_key_from_jwt(
            credentials.credentials
        )
        claims = jwt.decode(
            credentials.credentials,
            key.key,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=audience,
            options={
                "require": [
                    "sub",
                    "exp",
                    "iat",
                    "nbf",
                    "repository_id",
                    "repository_owner_id",
                    "ref",
                    "workflow_ref",
                    "event_name",
                    "run_id",
                    "run_attempt",
                ]
            },
        )
    except jwt.PyJWKClientConnectionError:
        raise HTTPException(503, "GitHub identity provider unavailable") from None
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid GitHub workload identity") from None
    # Immutable IDs prevent namespace/repository takeover. Both documented
    # subject formats are accepted only with the same immutable IDs and ref.
    worker_repository = {
        "Per5on/spestoslav/.github/workflows/backend-workers.yml@refs/heads/main": "spestoslav",
        "Per5on/spestovnik/.github/workflows/backend-workers.yml@refs/heads/main": "spestovnik",
    }.get(str(claims["workflow_ref"]))
    subjects = {
        f"repo:Per5on@162897472/{worker_repository}@1457549969:ref:refs/heads/main",
        f"repo:Per5on/{worker_repository}:ref:refs/heads/main",
    }
    if (
        str(claims["repository_id"]) != "1457549969"
        or str(claims["repository_owner_id"]) != "162897472"
        or claims["sub"] not in subjects
        or claims["ref"] != "refs/heads/main"
        or worker_repository is None
        or claims["event_name"] not in ("schedule", "workflow_dispatch")
        or claims.get("runner_environment") != "github-hosted"
    ):
        raise HTTPException(
            403, "This workflow is not authorized for receipt processing"
        )
    return str(claims["run_id"]) + ":" + str(claims["run_attempt"])


def lease(job, worker):
    key = os.getenv("ADMIN_API_KEY", "")
    if len(key) < 32:
        raise HTTPException(503, "Receipt lease signing is not configured")
    message = f"receipt-lease-v1:{job.id}:{job.attempts}:{worker}".encode()
    return hmac.new(key.encode(), message, hashlib.sha256).hexdigest()


def leased_job(db, job_id, worker, supplied):
    job = db.scalar(select(ReceiptJob).where(ReceiptJob.id == job_id).with_for_update())
    if not job or not supplied or not hmac.compare_digest(lease(job, worker), supplied):
        raise HTTPException(403, "Invalid receipt job lease")
    claimed = job.claimed_at
    if claimed and claimed.tzinfo is None:
        claimed = claimed.replace(tzinfo=timezone.utc)
    scan = db.get(ReceiptScan, job.scan_id)
    if (
        not claimed
        or claimed < datetime.now(timezone.utc) - timedelta(minutes=5)
        or scan.status != "PROCESSING"
    ):
        raise HTTPException(409, "Receipt lease expired or job already finished")
    return job, scan


class Completion(BaseModel):
    text: str | None = Field(default=None, max_length=100000)


@router.post("/claim")
def claim(worker=Depends(github_worker), db: Session = Depends(get_db)):
    row = claim_job(db)
    if not row:
        db.commit()
        return {"job": None}
    job, scan = row
    token = lease(job, worker)
    db.commit()
    return {"job": {"id": str(job.id), "lease": token}}


@router.get("/jobs/{job_id}/image")
def image(
    job_id: UUID,
    worker=Depends(github_worker),
    x_receipt_lease: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    job, scan = leased_job(db, job_id, worker, x_receipt_lease)
    data = ReceiptStorage().get(scan.image_storage_key)
    db.rollback()  # Release the row lock before streaming to the runner.
    return Response(
        data,
        media_type="application/octet-stream",
        headers={"Cache-Control": "no-store"},
    )


@router.post("/jobs/{job_id}/complete")
def complete(
    job_id: UUID,
    payload: Completion,
    worker=Depends(github_worker),
    x_receipt_lease: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    job, scan = leased_job(db, job_id, worker, x_receipt_lease)
    finish_job(db, job.id, job.attempts, payload.text)
    db.commit()
    return {"status": scan.status}
