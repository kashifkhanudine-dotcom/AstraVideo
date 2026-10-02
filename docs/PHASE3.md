# AstraVideo — Phase 3

This branch introduces the new cross-platform architecture while preserving the existing Android/Desktop prototype on `main`.

## New architecture

- `mobile/`: Flutter app for Android + iOS
- `backend/`: FastAPI API for AI video generation jobs
- Firebase Auth-ready
- Supabase/PostgreSQL-ready
- RevenueCat-ready subscriptions
- Pluggable AI providers

## Local development

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

### Flutter

Install Flutter, then:

```bash
cd mobile
flutter pub get
flutter run
```

For Android emulator the default API URL is `http://10.0.2.2:8000`; for iOS Simulator use `http://127.0.0.1:8000`.

## Security

Never commit API keys, Firebase service-account files, RevenueCat secrets, or provider tokens. Keep them in environment variables / secret managers.
