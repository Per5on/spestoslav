# Preview007 API rollout

Scope: bring the connected preview service from0.5.0 to0.6.0 using the backend/data/importer code verified in PR16 at48c7442, without changing mobile source or publishing an APK. The owner explicitly requires working live connections for the authorized test build. Preserve existing clients and every numbered release. This branch does not merge the inventory seed work from PR15.

Evidence:87local PostgreSQL16/Bulgarian OCR tests passed. Current app exact-head CI passed and Android10 run44105274182 succeeded (navigation, real locality selection, camera denial/preview, native image barcode decode, language/version settings). Isolated Neon branch br-polished-unit-bafzpcnc validated0008+1000source-backed technology identities, full repeated-upsert hash stability and unchanged grocery/store hashes versus preview. New group index4-row predicate uses3shared-buffer hits versus47for sequential scan; tiny timings are noisy. No prices/GTINs invented.

Controlled sequence:
1. Retain a no-compute recovery copy of existing preview before writes. Confirm baseline1000groceries/0technology/139stores/1inactive/0current prices, canonical links and hashes.
2. Apply only checked0008additive tables/index and verified technology identities transactionally. Compile/import with explicit aliases defaults and original UUID5 identities; preserve barcode/active fields. No other migration chain, Home/postal retirement, purge or store import.
3. Repeat import and compare counts/hashes; retain every existing grocery/store row. Expected1000groceries+1000technology,139stores/1inactive,0current prices; observed metadata is not live-price evidence.
4. Require exact-head backend CI on this backend-only branch, then roll out to the existing preview API service in the owner-selected MyWorkspace. Service follows main with auto-deploy; do not trigger a deployment of old main expecting candidate code. Check the specific resulting deploy to live and then verify0.6.0/ready, both1000-item catalogue snapshots, real location filtering, optional sample images/credits and auth/private-storage availability.
5. Feedback remains unavailable until a supported delivery provider is chosen/configured and actual delivery verified. Render Free explicitly blocks SMTP465/587 (https://render.com/docs/free.md); existing non-password Yahoo settings do not solve this. No billing upgrade and no email send without approved configuration. Credentials stay server-side.
6. Keep known gaps visible: verified offer/barcode coverage, final live account/receipt tests, provider delivery and three full final-source passes still gate the fully live release. Do not claim those from mocked evidence or metadata count alone. GooglePlay test distribution is a subsequent separate stage.

Schema check: all runtime API model columns exist in the validation clone. The unused legacy user_submissions.locality_id column is absent; no actual route uses it, so retain the legacy table unchanged rather than adding or dropping speculative compatibility fields.

Roll back application code only if necessary, respecting additive schema compatibility. Never delete recovery branches or existing user/receipt/store data as part of rollout. Record actual deploy/CI results separately so the tested source stays immutable.
