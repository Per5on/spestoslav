# Account deletion (review patch, 18 November 2026)

Status: **verified locally with PostgreSQL and a mocked identity provider.** The live Neon Auth OpenAPI schema lists the deletion endpoint. An authenticated deletion against the live provider remains to be tested.

## Contract

`DELETE /api/v1/account` — headers `Authorization: Bearer <access token>` and `X-Auth-Session: <provider session>`.

| Result | Meaning |
|---|---|
| 204 | Private data erased and the provider returned an explicit user-deleted result. |
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
- **Provider:** The live schema lists `/delete-user`. Test the route with an authorized throwaway account to establish whether the branch requires fresh sign-in, password or email verification. The backend returns 502 after private data erasure if the provider does not confirm deletion.
- **Identity match:** step 1 assumes the provider user id equals the JWT `sub`. If the first real test returns 403, check that assumption.
- **Not covered:** server logs/backups (retention periods are an operator decision) and a receipt uploaded concurrently while deletion runs (it would be left for a retry).
- **App:** Account screen offers "Delete account" with a confirmation; after a 502 the user stays signed in so they can retry.

## Delete data in Pre-alpha 009

«Настройки → Изтрий данни» clears the app’s saved list, preferences, locality, SecureStore session and app-owned ImagePicker cache. It works offline for anonymous sessions. The app has no persistent guest account or collected device identifier to match to server records. Existing public catalogue caches and photos picked from the device gallery are outside the action.

With an active verified session, `DELETE /api/v1/account/data` calls the private receipt and contribution erase path. It expires local sign-in and the app requests server sign-out. Account identity remains available. The server erases private storage and data, unlinks approved catalogue contributions, and scrubs private descriptions and matching source references. A server failure still allows device reset and shows that server deletion was unconfirmed. This does not enumerate already-forwarded email, logs or backups. Feedback deletion requests go to the operator at ivo77@duck.com. Verify the live provider and storage with authorized test records. Concurrent writes from a different signed-in device remain an open check.
