# Спестовник

Android price comparison app for Bulgaria, using Expo/React Native + TypeScript, FastAPI, Neon PostgreSQL and Render. Bulgarian is the default language; four upper tabs (three categories and a saved list) share one searchable locality selection.

**Continue the ongoing project:** [current status](docs/PROJECT_STATUS.md), [activity log](docs/ACTIVITY_LOG.md), [confirmed frontend brief](docs/FRONTEND_BRIEF.md). Historical handoffs are linked from the status file. Keep numbered previews and APKs separate.

## Local development

API:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

Android:

```bash
cd mobile
npm ci
npm run typecheck
npm test
npx expo start
```

Use `npm ci` normally, including its reviewed dependency-patch postinstall hook. Patches preserve SDK 54 compatibility with fixed image parsing and protect config merging; they fail visibly if the locked dependency source changes. See [audit notes](docs/AUDIT_2026-11-15.md).

The Android APK workflow generates the native project and builds a standalone, test-signed Android 10+ preview. [Preview 001](docs/ANDROID_PREVIEW_001.md) is preserved; [preview 002](docs/ANDROID_PREVIEW_002.md) contains audit fixes.

## Verification

```bash
cd backend
PYTHONPATH=. pytest -q
cd ..
python scripts/validate_inventory.py
```

Set `TEST_DATABASE_URL` to a disposable PostgreSQL database to include migration, concurrency and transaction checks. CI runs PostgreSQL 16 with SQLAlchemy 2.0 and 2.1. Never point test setup at the shared preview database.

This is a preview app. Branch inventory and real price coverage remain incomplete. Demo photos are explicitly separate and have no asserted price. Camera scanning, sign-in and private receipt workflows exist in the Preview007 Android UI but are not yet verified against a live account and physical device. No server credentials belong in the app.

Release notes: [CHANGELOG](docs/CHANGELOG.md). Current candidate metadata: [mobile/preview.json](mobile/preview.json). Reproducible local scenarios: [MOCK_SCENARIOS_005](docs/MOCK_SCENARIOS_005.md).
