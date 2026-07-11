# My Operations

FastAPI app with a sidebar UI for quick calculations and related tasks. HTML and JSON APIs run on the same port.

## Setup

```bash
cd my_operations
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Or from Cursor: **Run and Debug** → **My Operations** (installs dependencies first).

Open http://127.0.0.1:8000

## Tasks

| Task | Description |
|------|-------------|
| TPS Calculator | Sustain TPS + Fixed Dataset Duration side by side |
| App Dashboard | App1–3 version matrix across envs/regions (east/west) with conflict coloring |

Click the **(i)** icon on calculator results to see the formula and worked example.

### App Dashboard local test

```bash
cd ../mock_actuators && uvicorn mock:app --reload --port 9001
```

Then run My Operations and open **App Dashboard**.

## Docs for agents

See [CLAUDE.md](CLAUDE.md) for architecture and how to add new tasks.
