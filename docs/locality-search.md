# Locality search API and mobile configuration

The mobile app uses the shared `GET /api/v1/localities?q=...` endpoint for all four category tabs. It searches Bulgarian names, Latin names (including the common `Sofia` → `Sofija` spelling variation), and postal-code prefixes. Results include municipality, region and all known postal codes.

Set `EXPO_PUBLIC_API_URL` in `mobile/.env` to the API base URL. For the Android emulator during local development, use `http://10.0.2.2:8000`. On a physical Android device, use the development computer's LAN IP address. For a published build, use the deployed HTTPS API URL.

No GPS permission or device-location lookup is used.

## API tests

From `backend/`:

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
PYTHONPATH=. pytest
```

The locality API tests use an isolated SQLite test database and do not modify Neon.
