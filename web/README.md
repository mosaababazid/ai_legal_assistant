# AI Legal Assistant — Frontend

Next.js 15 (App Router, React 19, Tailwind) UI for the AI Legal Assistant. Upload documents, choose language (DE/AR), and get summaries or legal analysis.

## Prerequisites

- Node.js 18+
- Backend running at `http://127.0.0.1:8000` (see `../backend/README.md`)

## Setup

1. **From this directory (`web/`)**:

   ```bash
   cp .env.local.example .env.local
   npm install
   ```

2. (Optional) To use a different API URL, set `NEXT_PUBLIC_API_URL` in `.env.local`.

## Run

```bash
npm run dev
```

Open **http://localhost:3000/**

## Scripts

- `npm run dev` — Development with Turbopack
- `npm run build` — Production build
- `npm run start` — Run production server
- `npm run lint` — ESLint
