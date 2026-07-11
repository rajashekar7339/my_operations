# My Operations — CLAUDE.md

High-level map for agents and developers working in this folder. **Keep this file updated** whenever tasks, APIs, or structure change.

## Purpose

Small FastAPI web toolkit for calculations and related quick tasks. UI and JSON APIs run on the **same port** (default `:8000`).

## Run

```bash
cd my_operations
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Or from Cursor: **Run and Debug** → **My Operations** (installs `requirements.txt`, then starts uvicorn). For the App Dashboard mock: **Mock Actuators** (`:9001`) or **My Operations + Mock** (both).

Open http://127.0.0.1:8000

## Folder map

| Path | Role |
|------|------|
| `.vscode/launch.json` | Cursor/VS Code launch config for uvicorn |
| `.vscode/tasks.json` | Pre-launch task: `pip install -r requirements.txt` |
| `app/main.py` | FastAPI app: mounts static files, serves `index.html`, includes routers |
| `app/routers/calculators.py` | HTTP endpoints under `/api/*` |
| `app/routers/dashboard.py` | `GET /api/dashboard` — app version matrix |
| `app/services/calculators.py` | Sustain TPS and fixed dataset duration formulas |
| `app/services/dashboard.py` | YAML config load, parallel actuator GETs, version tones |
| `config/apps.yaml` | App × environment actuator URLs (local mock by default) |
| `config/apps.example.yaml` | Template for real environment URLs |
| `templates/index.html` | Shell: sidebar + task panels |
| `static/css/app.css` | UI styles |
| `static/js/app.js` | Sidebar nav, form submit, (i) info popovers |
| `CLAUDE.md` | This file — architecture and extension guide |
| `PLAN.md` | Original implementation plan and design spec |
| `.cursor/rules/my-operations-docs.mdc` | Cursor rule: read/update CLAUDE.md on changes |

## Architecture

```
Browser (:8000)
 → GET /              → Jinja template (HTML shell)
 → /static/*          → CSS, JS
 → POST /api/sustain   → app/services/calculators.py
 → POST /api/duration  → app/services/calculators.py
 → GET /api/dashboard  → app/services/dashboard.py → config/apps.yaml
```

## Current sidebar tasks

### 1. TPS Calculator (`id: tps`)

Single screen with two calculators side by side.

#### Sustain TPS

| Input | Field |
|-------|-------|
| TPS | `tps` |
| Duration | `minutes` |

**Formula:** `transactions = tps × 60 × minutes`

**API:** `POST /api/sustain`  
**Body:** `{ "tps": 300, "minutes": 20 }`  
**Response:** `{ "transactions", "formula", "explanation", "inputs" }`

**Logic:** `app/services/calculators.py` → `calculate_sustain_tps()`

#### Fixed Dataset Duration

| Input | Field |
|-------|-------|
| Total transactions | `transactions` |
| TPS | `tps` |

**Formula:** `seconds = transactions ÷ tps` (minutes = seconds ÷ 60)

**API:** `POST /api/duration`  
**Body:** `{ "transactions": 1000000, "tps": 300 }`  
**Response:** `{ "seconds", "minutes", "formula", "explanation", "inputs" }`

**Logic:** `app/services/calculators.py` → `calculate_duration()`

### 2. App Dashboard (`id: dashboard`)

Matrix of **App1 / App2 / App3** × **dev, uat, sit, perf, prod**. Simple GET to each actuator URL in [`config/apps.yaml`](config/apps.yaml); expects HTTP 200 and `{"version": "..."}`.

**API:** `GET /api/dashboard` (also `POST /api/dashboard/refresh`)

**Cell tones (per app row):**
- **Green** (`match`) — version matches the majority among healthy envs
- **Yellow** (`conflict`) — healthy but different version
- **Red** (`error`) — timeout, non-200, or missing version

**Logic:** `app/services/dashboard.py`

#### Local mock (outside repo)

Sibling folder `../mock_actuators/` on port **9001** — do not check in. See that folder's README.

```bash
# Terminal 1
cd ../mock_actuators && uvicorn mock:app --reload --port 9001

# Terminal 2 — My Operations
uvicorn app.main:app --reload --port 8000
```

Swap URLs in `config/apps.yaml` for real actuator endpoints when ready.

## API response contract

Every calculator returns:

- Primary result fields (e.g. `transactions`, `seconds`)
- `formula` — human-readable formula string (shown in (i) popover)
- `explanation` — worked example with input values
- `inputs` — echo of request inputs

## How to add a new task

1. **Logic** — Add a function in `app/services/` returning `{ result fields, formula, explanation, inputs }`.
2. **Router** — Add Pydantic request model + `POST /api/<task>` in `app/routers/` (or new router included in `app/main.py`).
3. **Sidebar** — Add entry to `tasks` list in `app/main.py` `index()` view.
4. **UI panel** — Add `<section class="task-panel">` in `templates/index.html` with form + result card + (i) popover.
5. **JS** — Add form handler in `static/js/app.js` calling the new endpoint.
6. **CLAUDE.md** — Document the new task in "Current sidebar tasks" and update folder map if needed.

## UI notes

- Left sidebar lists tasks; clicking switches panels client-side (no reload).
- Each result has an **(i)** icon; popover shows `formula` and `explanation` from API response.
- Do not duplicate formula logic in JavaScript — always use backend `formula` / `explanation`.

## Dependencies

- FastAPI, Uvicorn, Jinja2, Pydantic — see `requirements.txt`
