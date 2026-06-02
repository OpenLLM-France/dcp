# DCP — Data Collection Platform

Platform for collecting human evaluations of LLM-generated completions.

---

## Architecture

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | FastAPI (Python 3.13) | REST API, session-based user auth, HTTP Basic admin auth |
| Frontend | Next.js 15 / React 19 | Static export (`output: 'export'`), Tailwind CSS v4 |
| Database | PostgreSQL 15 | Docker Compose, data persisted via volume |
| Admin UI | `/admin` | Same frontend bundle, HTTP Basic Auth |
| Reverse proxy | nginx | Serves frontend static files, proxies API to backend |

### Directory structure

```
.
├── back/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py        # API endpoints (user + admin)
│   │   ├── models.py      # SQLAlchemy ORM models
│   │   ├── service.py     # Business logic / DB queries
│   │   └── database.py    # Engine, session, Base
│   ├── scripts/
│   │   ├── add_task.py    # CLI — add a new task
│   │   └── add_prompts_and_generations.py  # CLI — import data
│   └── tests/
├── front/                 # Next.js frontend
│   ├── app/
│   │   ├── page.tsx       # Home — task list
│   │   ├── task/page.tsx  # Task — prompt, generations, voting
│   │   ├── admin/page.tsx # Admin dashboard (protected)
│   │   └── leaderboard/
│   └── lib/
│       ├── api.ts         # User-facing API client (cookie auth)
│       ├── adminApi.ts    # Admin API client (Basic Auth)
│       ├── math.ts        # LaTeX preprocessing pipeline
│       ├── types/         # TypeScript interfaces
│       └── __tests__/     # Unit tests (run with `npm test`)
├── new_data/              # Source data files (JSONL, CSV)
├── docker-compose.yml     # All services
└── AGENTS.md              # Developer guidelines
```

---

## Quick Start

```bash
# Build and start all services
docker compose up --build -d

# The app is served at http://localhost:8000
```

---

## Source Data Format

Each line is a JSON object with one prompt and its associated AI generations:

```jsonl
{"prompt": "Full prompt text", "generations": [
  {"text": "First model's answer...", "params": {"Model": "model-8b"}},
  {"text": "Second model's answer...", "params": {"Model": "model-1b"}}
]}
```

Fields:
- **`prompt`** (string, required): The prompt shown to annotators.
- **`generations`** (array, required): One or more LLM-generated completions.
  - **`text`** (string, required): The full generation text.
  - **`params`** (object, required): Generation parameters. At minimum must include a `Model` key with the model name. Other keys are stored as-is in `generationparams` table.

---

## Adding a New Task

### 1. Add an Instruction

Instructions are task-level guidance text. Add one via:

```bash
python back/scripts/add_instruction.py --text "Compare the following fractions and explain your reasoning."
```

The script outputs the new instruction ID. Save it — you'll need it for the next step.

### 2. Add the task

```bash
# From the project root
python back/scripts/add_task.py \
    --name "mon-super-exercice" \
    --meta data/meta.json \
    --public \
    --instruction-id 1
```

The script outputs the new task UUID. Save this — you'll need it to associate prompts.

---

## Adding Prompts and Generations

### 1. Prepare data in JSONL format

Each line is one prompt + its generations (see format above).

### 2. Run the import script

```bash
python back/scripts/add_prompts_and_generations.py \
    --task-id <task-uuid> \
    --data new_data/my_dataset.jsonl \
    --verbose
```

The script is idempotent:
- Prompts are deduplicated by `task_id + text`
- Generation params are deduplicated by their JSON content
- Generations are deduplicated by `text + params_id + prompt_id`

Re-running the same file will skip already-existing entries and only insert new ones.

Compressed files (`.jsonl.xz`) are auto-detected and transparently decompressed.

---

## Admin

The admin UI is served at `/admin` on the same static frontend. It is **not** a separate app — it's part of the Next.js build.

### Access

- Default: username `admin`, password `changeme`
- Override via `ADMIN_USERNAME` / `ADMIN_PASSWORD` environment variables on the backend service

### Features

1. **Dashboard** — Stats cards (total tasks, prompts, generations)
2. **Task browser** — Expandable tree: task → prompts (paginated) → generations
3. **Raw / Rendered toggle** — Every prompt and generation has a toggle between KaTeX-rendered HTML and raw LaTeX source
4. **Text editing** — Click "Edit" on any prompt or generation, modify the text in a textarea, save
5. **Audit trail** — All edits are logged with before/after text, admin username, and timestamp. View history via the "History" button on any prompt/generation, showing word-level diffs.

### API auditing

Every `PUT /admin/prompts/{id}/text` and `PUT /admin/generations/{id}/text` creates an `admin_audit_logs` row recording:
- The entity type and ID
- The full text before and after
- The admin username (from HTTP Basic Auth)
- A timestamp

---

## Environment Variables

| Variable | Default | Used by | Purpose |
|----------|---------|---------|---------|
| `DATABASE_URL` | `postgresql://postgres:postgres@db:5432/postgres` | Backend | PostgreSQL connection |
| `ADMIN_USERNAME` | `admin` | Backend | Admin HTTP Basic Auth |
| `ADMIN_PASSWORD` | `changeme` | Backend | Admin HTTP Basic Auth |
| `NEXT_PUBLIC_API_URL` | `""` (same-origin) | Frontend | Backend API base URL |

