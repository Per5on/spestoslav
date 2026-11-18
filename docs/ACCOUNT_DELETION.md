# Account deletion (review patch, 18 November 2026)

Status: **implemented and unit-tested with mocks; not verified against PostgreSQL CI or real Neon Auth.** Do not claim working account deletion, or GDPR compliance, from this document.

## Contract

`DELETE /api/v1/account` — headers `Authorization: Bearer <access token>` and `X-Auth-Session: <provider session>`.

| Result | Meaning |
|---|---|
| 204 | Private data erased and the provider accepted `/delete-user`. |
| 401 | Missing/invalid token. |
| 403 | Session does not belong to the token's subject, or a service/admin identity called it. |
| 409 | A receipt is being OCR-processed; retry shortly. Nothing was erased. |
| 502 | Private data **is erased**, the provider step failed. Retrying is safe. |
| 503 | Receipt storage or the provider was unavailable. Retrying is safe. |

## Order of operations (each step retry-safe)

1. Confirm the provider session's user id equals the token subject.
2. Refuse while any receipt is `PROCESSING`.
3. Mark receipts `DELETING`, delete stored images, then OCR items, jobs and scans.
4. Delete the caller's `PENDING` price submissions (and their cache rows) and `PENDING` identification requests; for reviewed ones replace `owner_subject` with a random `deleted:<uuid>` so the catalogue keeps anonymous provenance.
5. Call the provider's `/delete-user` with the session cookie.

## Owner decisions and checks still needed

- **Policy:** reviewed (verified/rejected/expired) contributions are kept anonymously. Confirm this, then state it in `mobile/src/legal/policies.json` (the Terms/Privacy source) and re-render with `scripts/render_legal_documents.py`. This patch deliberately does not edit the legal text.
- **Provider:** `/delete-user` is the Better-Auth-style path and is **assumed** to be exposed by Neon Auth for this project. Test with a throwaway real account. If it is unsupported or needs a fresh sign-in/password, the route returns 502 and the data erasure still works; adjust `app/account.py` accordingly.
- **Identity match:** step 1 assumes the provider user id equals the JWT `sub`. If the first real test returns 403, check that assumption.
- **Not covered:** server logs/backups (retention periods are an operator decision) and a receipt uploaded concurrently while deletion runs (it would be left for a retry).
- **App:** Account screen offers "Delete account" with a confirmation; after a 502 the user stays signed in so they can retry.
