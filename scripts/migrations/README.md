# Shared-preview SQL history

The active preview still has Flyway-origin schema history. Do not replay an independent Alembic baseline or an old bootstrap script over it.

- `legacy_preview_marketplace.sql`: historical non-idempotent 0003-equivalent bootstrap, retained for provenance/recovery. Not a current import/deploy instruction.
- `preview_backend_workflows.sql`: earlier additive compatibility/workflow preparation, already applied to shared preview. Do not use it to recreate retired postal storage.
- Later explicit SQL lives in `backend/migrations/sql/`: 0006 Home/postal retirement is already applied; 0007 grocery/receipt additions are tested in isolation and await rollout authorization.

Current path/state: `docs/decisions/migration-strategy.md` and `docs/PROJECT_STATUS.md`.
