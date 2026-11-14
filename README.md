# Спестослав

Android-first price comparison app for Bulgaria.

## Initial technology direction

- Mobile: React Native + TypeScript (Expo workflow)
- API: Python + FastAPI
- Database: PostgreSQL on Neon
- Hosting: Render
- Source control: this repository

Bulgarian is the default language; English is the first additional locale. The four top-level categories are Храни, Горива, Дом and Техника. Settlement selection is shared across categories.

## Local development

### API

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Android app

```bash
cd mobile
npm install
npx expo start
```

This is the initial scaffold, not a production-ready application. No credentials or production configuration are included. Do not treat sample UI content or future demo prices as verified live retailer prices.
