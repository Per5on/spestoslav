# Database migration strategy

## Current decision — 16 November 2026

- **Fresh databases:** independent Alembic revisions 0001–0007. PostgreSQL16 online upgrade/downgrade/re-upgrade, offline SQL output and model-drift checks run in disposable schemas. Revision 0007 is current source work under a build/commit hold, not a deployed milestone.
- **Existing shared Neon preview:** `br-snowy-morning-baym8iw6` retains its legacy Flyway history. Do not execute the independent Alembic baseline there or invent missing V5/V6 Flyway source. Earlier compatibility/workflow changes used `scripts/migrations/preview_backend_workflows.sql`; 0006 retirement subsequently removed Home/postal data and storage after API0.5.0 deployment.
- **Current 0007 changes:** additive SQL in `backend/migrations/sql/0007_grocery_workflows.sql`, tested on local PostgreSQL and isolated branch `br-ancient-shadow-balr2n5l`. They have not been applied to shared preview. Keep schema changes in code; use the existing explicit migration path when rollout is authorized.
- **SQL-file execution:** 0006/0007 execute whole SQL files in the migration transaction, preserving quoted semicolons and PostgreSQL dollar-quoted bodies. Offline generation emits literal SQL without interpreting text as bind parameters. Retirement SQL itself is unchanged.
- **Recovery and provenance:** preserve canonical locality/branch identities and source evidence; no demo data or guessed prices. Retirement recovery branch `br-frosty-star-badgjcyw` remains separate. Downgrading 0006 restores structure, not deleted data.
- `scripts/migrations/legacy_preview_marketplace.sql` is retained as a historical, non-idempotent bootstrap reference for the still-existing Flyway-origin database. It is not a current rollout command. See `scripts/migrations/README.md` and [backend readiness](../BACKEND_READINESS.md).

## Historical context

Legacy Flyway source files stop at V4; the existing preview had a V5 baseline and V6 price-note history without corresponding source files. The project deliberately introduced an independent Alembic baseline rather than rewriting that history. Earlier statements that the current chain stopped at 0005 are superseded by the revision list above.
