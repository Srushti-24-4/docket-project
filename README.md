# Docket — Document Intelligence Pipeline

Upload any mix of documents — clean PDFs, scanned images, table-heavy reports,
standalone images, Word docs, plain text — and Docket routes each one to the
right extractor, indexes it, and answers questions with the exact source file
and page number attached. Accounts are required: sign up, verify your email,
and every document and answer is scoped to you alone.

```
Register / Log in (Supabase Auth, email verification required)
       │
Upload → Router → [PyMuPDF | OpenCV+OCR | pdfplumber/Camelot | python-docx | plain text]
       → Chunk → Gemini Embeddings → Qdrant (scoped to your user id)
       → (on question) Search → Rerank → Gemini answer → Evidence verification
       → Answer + citations
```

## Pages

| Route | What it does |
|---|---|
| `/` | Landing page |
| `/register` | Create an account (Supabase sends a verification email) |
| `/login` | Log in |
| `/forgot-password` | Request a password reset email |
| `/reset-password` | Set a new password (reached via the email link) |
| `/ask` | Protected dashboard — upload documents, ask cited questions |
| `/documents/:id` | Protected detail page for a single document |

## Project layout

```
docket-project/
├── backend/            FastAPI service (extraction, embeddings, search, chat)
│   ├── app/
│   │   ├── routers/     upload.py, chat.py
│   │   ├── services/    router, pdf_extractor, ocr, table_extractor,
│   │   │                image_extractor, docx_extractor, text_extractor,
│   │   │                chunker, embeddings, vector_store, reranker,
│   │   │                llm, verification, storage
│   │   ├── models/      pydantic schemas
│   │   └── core/        settings, security (JWT verification)
│   ├── supabase_schema.sql
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            Next.js + Tailwind + shadcn-style components
│   ├── app/              /, /login, /register, /forgot-password,
│   │                     /reset-password, /ask, /documents/[id]
│   ├── components/        Nav, RequireAuth, UploadDropzone, CitationChip
│   └── lib/                supabaseClient, auth-context, api client, types
└── docker-compose.yml    backend + local Qdrant
```

## How auth works here

The **frontend talks to Supabase Auth directly** (via `supabase-js`) for
sign-up, login, password reset, and email verification — that's the standard,
secure pattern and it's what Supabase is built for. The **backend never
handles passwords**; it only verifies the access token Supabase issues,
on every request to `/documents` and `/chat` (see `app/core/security.py`).
Every document and chunk is tagged with the uploader's `user_id`, and both
Supabase queries and Qdrant searches are scoped to it — one user can never
see another's documents or answers.

## Setup

### 1. Supabase — auth settings (do this first, in the dashboard)

- **Authentication → Providers → Email**: turn on **"Confirm email"** so new
  signups must verify their address before logging in.
- **Authentication → URL Configuration**:
  - Set **Site URL** to your frontend's URL (`http://localhost:3000` locally).
  - Add `http://localhost:3000/reset-password` to **Redirect URLs** — without
    this, the password-reset email link won't work.
- **Settings → API**: copy the **Project URL**, the **anon public key**
  (goes in the frontend), and the **service_role key** (goes in the backend —
  keep it secret, never ship it to the browser).
- Run `backend/supabase_schema.sql` in the SQL editor.
- **Storage**: create a bucket named `documents` (or whatever you set
  `SUPABASE_STORAGE_BUCKET` to).

### 2. Backend

```bash
cd backend
cp .env.example .env      # fill in GEMINI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Run Qdrant locally (or use Qdrant Cloud and set `QDRANT_URL`/`QDRANT_API_KEY`):

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Start the API:

```bash
uvicorn app.main:app --reload
```

### 3. Frontend

```bash
cd frontend
cp .env.local.example .env.local   # fill in NEXT_PUBLIC_SUPABASE_URL / ANON_KEY
npm install
npm run dev
```

Visit `http://localhost:3000`, register an account, check your email for the
verification link, log in, and go to `/ask`.

### 4. Or run everything with Docker Compose

```bash
docker compose up --build
```

(This brings up the backend + Qdrant. Run the frontend separately with `npm run dev`,
or add a frontend service to `docker-compose.yml` once you're ready to containerize it too.)

## Deployment

Matches the intended stack:

| Component | Where |
|---|---|
| Frontend | Vercel (`vercel deploy` from `frontend/`) |
| Backend | Render (Docker deploy from `backend/`) |
| Vector DB | Qdrant Cloud, or self-hosted alongside the backend |
| Database / Auth / Storage | Supabase |

When you deploy, remember to add your production frontend URL to Supabase's
**Site URL** and **Redirect URLs** too — the local `http://localhost:3000`
entries won't work once the app is live.

You don't need to train Gemini — it's used purely for embeddings and the final
grounded-answer generation step.

## Supported file types

| Type | Route | Extractor |
|---|---|---|
| PDF with a text layer | `normal_pdf` | PyMuPDF |
| Scanned / image-only PDF | `scanned_pdf` | OpenCV + PaddleOCR |
| Table-heavy PDF | `table_heavy` | pdfplumber / Camelot |
| Standalone image (jpg, png, webp, bmp, tiff) | `image` | OpenCV + PaddleOCR |
| Word document (.docx) | `docx` | python-docx |
| Plain text (.txt, .md) | `plain_text` | direct decode |

## Notes on the extraction routing

`app/services/router.py` first looks at the file extension, then — for PDFs
specifically — samples the first few pages and decides between the three PDF
paths using cheap heuristics (extractable text density, and the proportion of
numeric/tabular-looking lines). It's deliberately simple — swap in a small
classifier if you outgrow it.

## Extending this

- **Reranker**: currently a lexical overlap blend on top of vector score.
  Swap in a cross-encoder (e.g. Cohere Rerank or a local model) for higher precision.
- **Streaming answers**: `llm.py` currently returns the full answer at once;
  switch to `generate_content(..., stream=True)` and a Server-Sent Events
  response if you want token-by-token streaming in the UI.
- **Sharing documents between users**: right now everything is strictly
  per-user. If you need shared workspaces, add an `organization_id` alongside
  `user_id` in both the Supabase schema and the Qdrant payload, and adjust the
  filters in `storage.py` and `vector_store.py` accordingly.
