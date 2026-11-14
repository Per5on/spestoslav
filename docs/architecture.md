# Architecture decisions

- Android-first mobile app using React Native + TypeScript.
- FastAPI backend; Neon PostgreSQL; Render hosting.
- Bulgarian default, English first additional language; localization from the beginning.
- Four top-level categories: food, fuel, home and technology.
- Settlement selection is shared across all categories.
- Prefer settlement/postal-code selection; GPS/radius is not mandatory.
- Price observations retain source, timestamp, verification state and physical branch.
- Demo values must never be presented as verified live prices.
- Legacy `Per5on/testing` remains unchanged during migration.

This file records the initial direction only. Production architecture and data migration remain subject to the source and schema audit.
