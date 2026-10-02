# AstraVideo

ASTRA VIDEO AI now contains three separate delivery targets:

- `web/` — Next.js SaaS/PWA frontend and server API base for Vercel.
- `app/` — native Android prototype and APK build.
- `desktop/` — Windows desktop prototype and EXE build.

## Vercel

Create/import the GitHub project in Vercel and set **Root Directory** to `web`.
Vercel will detect Next.js automatically. The health endpoint is `/api/health`.

The web application intentionally does **not** fabricate AI generations. Until a real provider adapter is connected, `/api/generate` returns `AI_PROVIDER_NOT_CONNECTED`.

Copy `web/.env.example` into your local environment and configure secrets only in Vercel Environment Variables; never commit provider API keys.

## Local web development

```bash
cd web
npm install
npm run dev
```

## Android / Windows

Existing GitHub Actions continue to build the Android APK and Windows EXE independently from the Vercel web app.
