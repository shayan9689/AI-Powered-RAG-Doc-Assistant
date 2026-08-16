# Deployment

## Local

1. Copy `.env.example` to `backend/.env`.
2. Copy `frontend/.env.example` to `frontend/.env`.
3. Fill in the keys listed in the root README.
4. Start backend: `cd backend` then `uvicorn app.main:app --reload`
5. Start frontend: `cd frontend` then `npm run dev`

Health check: `GET http://localhost:8000/health`

## Recommended hosts

| Piece | Host | Why |
| --- | --- | --- |
| Frontend (`frontend/`) | **Vercel** | Static Vite build |
| Backend (`backend/`) | **Railway** | Always-on Python process + optional disk |

Do not put FastAPI on Vercel.

---

## 1. Backend on Railway

1. Push this repo to GitHub.
2. In Railway: **New project → Deploy from GitHub repo**.
3. Railway should pick up `Dockerfile` and `railway.toml` at the repo root.
4. Attach a **volume** mounted at `/data` so Chroma and PDFs survive redeploys.
5. Generate a public URL (Railway Settings → Networking → Generate domain).

### Backend variables

| Variable | Example |
| --- | --- |
| `ENVIRONMENT` | `production` |
| `AUTH_REQUIRED` | `true` |
| `CORS_ORIGINS` | `https://your-app.vercel.app` |
| `DATA_DIR` | `/data` |
| `CHROMA_PERSIST_DIR` | `/data/chroma` |
| `LLM_PROVIDER` | `openai` |
| `LLM_MODEL` | `gpt-4o-mini` |
| `OPENAI_API_KEY` | your key |
| `SUPABASE_URL` | `https://xxxx.supabase.co` |
| `SUPABASE_ANON_KEY` | anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | service role key |

You can leave `CORS_ORIGINS` as `http://localhost:5173` until Vercel is live, then add the Vercel URL (comma-separated is fine):

```text
https://your-app.vercel.app,http://localhost:5173
```

Confirm: `GET https://your-service.up.railway.app/health` → `{"status":"ok"}`.

First deploy may take a few minutes while the embedding model downloads.

---

## 2. Frontend on Vercel

1. Import the same GitHub repo in Vercel.
2. Set **Root Directory** to `frontend`.
3. Framework: Vite.
4. Add environment variables, then deploy.

| Variable | Example |
| --- | --- |
| `VITE_API_BASE_URL` | `https://your-service.up.railway.app` (no trailing slash) |
| `VITE_SUPABASE_URL` | `https://xxxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | anon key only |

Never put `SUPABASE_SERVICE_ROLE_KEY` or LLM keys in Vercel.

After the Vercel URL exists, go back to Railway and set `CORS_ORIGINS` to that URL, then redeploy the backend.

---

## Production checklist

- [ ] Railway `/health` returns ok
- [ ] Volume mounted at `/data`
- [ ] `AUTH_REQUIRED=true`
- [ ] `CORS_ORIGINS` matches the Vercel origin
- [ ] Vercel `VITE_API_BASE_URL` points at Railway
- [ ] Upload a PDF, select it, ask a question, open a page preview

## Docker (optional, local or a VM)

```bash
docker compose up --build
```

Chroma, app data, and uploaded PDFs persist in `./data`.
