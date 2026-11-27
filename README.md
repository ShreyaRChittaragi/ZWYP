# ZWYP: peer-to-peer barter marketplace (prototype)
React + Vite + Tailwind frontend, FastAPI + SQLAlchemy + SQLite backend. Items are swapped, not sold.

> **Status:** this project has been reviewed and fixed, but the full stack has **not yet been run end to end**
> (the build environment had no network to install FastAPI/SQLAlchemy/npm packages). See "Verification status" below.

## Requirements
Python 3.10+, Node 18+.

## Run the backend
    cd backend
    python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python seed.py                                          # creates/updates backend/zwyp.db with demo data
    uvicorn app.main:app --reload --port 8000
API docs (Swagger): http://localhost:8000/docs

## Run the frontend (second terminal)
    cd frontend
    npm install
    npm run dev                                             # http://localhost:5173
Vite proxies `/api`, `/uploads` and `/static` to port 8000, so keep the backend running on 8000.

## Seeding
`python seed.py` is safe to run repeatedly. It never drops tables or deletes user-created data. It creates only missing
demo users, listings and swaps, switches old picsum.photos demo images to local illustrations, and removes legacy demo swaps
that broke ownership rules (only rows where the requester did not own the offered item). To start from scratch, delete `backend/zwyp.db` yourself and re-run it.

## Demo logins (password `zwyp1234`)
aarav@zwyp.demo (Bengaluru), priya@zwyp.demo (Bengaluru), rohan@zwyp.demo (Mumbai), ishita@zwyp.demo (Hyderabad), karan@zwyp.demo (Delhi)

## Suggested demo walkthrough
1. Open Explore, search and filter. Open any item.
2. Log in as `aarav@zwyp.demo`. Priya's pending request for Aarav's guitar is under My Swaps > Incoming. Accept or reject it.
3. Open Matches to see mutual matches and the three-way chain: Aarav's jacket, Ishita's plant pots, Priya's sneakers, back to Aarav.
4. List a new item (try uploading a photo), then log in as another user and send a swap request. Chat from the Chat button.
5. Accept, then "Mark completed": both items become `swapped` and disappear from Explore.

## Swap rules
- You can only offer your own item and request someone else's. Duplicate active requests are rejected.
- Accepting a request automatically rejects/cancels every other pending request involving either item, and an item in an accepted swap cannot be requested or accepted again.
- Completing a swap marks both items `swapped`; a swapped item can never be part of another swap.
- Removing a listing cancels its pending requests, and is blocked while the item is in an accepted swap.

## Image uploads
Validated on the server by decoding the actual content (Pillow), not by filename: JPEG/PNG/WebP only, max 5 MB, max 25 megapixels, empty/corrupt/disguised files rejected. The stored extension comes from the detected format. Files are saved in `backend/uploads`. Demo listings use local SVG illustrations generated into `backend/static/seed/`.

## API (prefix `/api`)
- POST `/auth/register`, `/auth/login`; GET `/users/me`, `/users/me/dashboard`
- GET `/items` (q, category, location, condition, page, size), `/items/facets`, `/items/mine`, `/items/{id}`; POST `/items` (multipart); DELETE `/items/{id}`
- POST `/swaps`; GET `/swaps`; POST `/swaps/{id}/{accept|reject|cancel|complete}`
- GET `/matches`; GET `/messages`; GET/POST `/messages/{swap_id}`

## Verification status
Actually run in the build environment: image-validation logic (11 cases), seed-data ownership rules, validity of all 17 SVG files, Python byte-compilation, JSX syntax check.
**Not run:** the FastAPI server, SQLAlchemy queries, the seed script against a real DB, `npm install`/build, and any browser flow
(registration, login, create listing, swap request, accept/reject, messaging). Please run them locally and report any failure.

## Known limitations
No reviews feature. Messaging polls every 5 s (no WebSockets). Matching is keyword-based. Accept/complete checks are not wrapped in
database-level locks, so truly simultaneous requests on SQLite could race. Seed illustrations are simple vector drawings, not photos.
Tests are not automated yet.
## Deploying to Render
`render.yaml` defines two services: **zwyp-api** (Python web service, `backend/`) and **zwyp-web** (Static Site, `frontend/`).

**zwyp-api** (Build: `pip install -r requirements.txt` · Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`)

| Variable | Value | Notes |
|---|---|---|
| `FRONTEND_URL` | `https://<your-static-site>.onrender.com` | Required. Allowed CORS origin(s); comma-separate several. localhost:5173 is always allowed. |
| `DB_PATH` | `/var/data/zwyp.db` | Optional locally (defaults to `backend/zwyp.db`). Must be on a persistent disk in production. |
| `UPLOAD_DIR` | `/var/data/uploads` | Optional locally (defaults to `backend/uploads`). Must be on a persistent disk in production. |
| `ZWYP_SECRET` | long random string | Already read by the app; set it so JWTs aren't signed with the dev default. |
| `PYTHON_VERSION` | `3.12.7` | Pin the Python version. |

Attach a Render Disk mounted at `/var/data` (paid plan). Without one, SQLite data and uploads are wiped on every deploy/restart.

**zwyp-web** (Build: `npm install && npm run build` · Publish dir: `dist`)

| Variable | Value | Notes |
|---|---|---|
| `VITE_API_URL` | `https://<your-api>.onrender.com` | Required at build time. Backend origin only: no trailing slash, no `/api` (the app appends `/api`). Redeploy the static site after changing it. |

React Router: in Redirects/Rewrites add **Rewrite `/*` → `/index.html`** (already in `render.yaml` under `routes`; set it manually if you create the site by hand).

Deploy order: create the API, copy its URL into `VITE_API_URL`, deploy the static site, then copy the site URL into `FRONTEND_URL` on the API. Optionally run `python seed.py` from the API service's Shell for demo data.