# Architecture decisions

- Android-first mobile app using React Native + TypeScript.
- FastAPI backend; Neon PostgreSQL; Render hosting.
- Bulgarian default, English first additional language; localization from the beginning.
- Three backend categories: groceries, technology and fuel. Four UI tabs: Food, Technology, Fuel, My list.
- Settlement selection is shared across all categories.
- Use shared settlement-name selection. GPS, radius and OSM features are excluded.
- Price observations retain source, timestamp, verification state and physical branch.
- Demo values must never be presented as verified live prices.
- Legacy `Per5on/testing` remains unchanged during migration.

This file records the initial direction only. Production architecture and data migration remain subject to the source and schema audit.
