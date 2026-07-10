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

| Task | Calculators |
|------|-------------|
| TPS Calculator | Sustain TPS (TPS + minutes → transactions); Fixed Dataset Duration (transactions + TPS → time) |

Click the **(i)** icon on any result to see the formula and worked example.

## Docs for agents

See [CLAUDE.md](CLAUDE.md) for architecture and how to add new tasks.
