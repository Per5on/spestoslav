"""Rolling 24-hour per-person quotas stored in the database.

Unlike the in-process request limiter these survive restarts and are shared by every
API instance. A limit of 0 disables a quota; an unparsable value falls back to the default.
"""

import os
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import func, select


def env_limit(name, default):
    try:
        return max(0, int(os.getenv(name, str(default))))
    except ValueError:
        return default


def enforce_daily_quota(db, model, subject, env_name, default, message):
    """Raise 429 when `subject` already created `limit` rows of `model` in 24 hours.

    `model` needs `owner_subject` and `created_at` columns. Call it only for work that
    would create a new row, never for an idempotent replay of an earlier request.
    """
    limit = env_limit(env_name, default)
    if not limit:
        return
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    used = db.scalar(
        select(func.count())
        .select_from(model)
        .where(model.owner_subject == subject, model.created_at >= since)
    )
    if used >= limit:
        raise HTTPException(429, message, headers={"Retry-After": "3600"})
