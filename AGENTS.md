# AGENTS.md — Development Guidelines for DCP

Data Collection Platform (DCP) — Python FastAPI backend, Next.js 15/React 19 frontend, PostgreSQL.

## Git Workflow

- All work must be done in feature branches off `main`
- **No commits directly to `main`** under any circumstances
- All merges to `main` require human code review via pull request
- Branch naming: `feature/description`, `fix/description`
- Keep commits focused and rebase before opening a PR

## Project Structure

- **Backend**: `/back` — FastAPI
- **Frontend**: `/front` — Next.js 15 with Turbopack
- **Database**: PostgreSQL via Docker Compose
- **Data files**: `/new_data` — JSONL and CSV sources

---

## Commands

### Backend (Python)

```bash
cd /home/user/dcp/back
pytest                                    # All tests
pytest tests/test_tasks.py                # Single file
pytest tests/test_tasks.py::TestTaskCreation::test_add_task_creates_task  # Single test
pytest tests/test_error_handling.py::TestFindExceptions -v  # Test class
pytest --cov=back/app --cov-report=term-missing  # Coverage
uvicorn app.main:app --reload --port 8000 # Dev server
pip install -r requirements.txt           # Install deps
```

### Frontend (Next.js)

```bash
cd /home/user/dcp/front
npm run dev      # Dev server with Turbopack
npm run build    # Production build
npm run lint     # ESLint
npx tsc --noEmit # Type check
npm test         # Math preprocessing tests (zero-dependency, runs with node)
```

### Full Stack (Docker)

```bash
docker compose up --build -d     # Build and start all services
docker compose logs -f backend   # Tail backend logs
docker compose build             # Build images without starting
```

---

## Backend Guidelines (Python/FastAPI)

### Imports
```python
import json
from sqlalchemy import select, func
from fastapi import FastAPI, Depends, HTTPException, status
from .models import Task
from .database import Base
```

### Naming & Types
- Functions/methods: `snake_case`
- Private methods: `__private_method`
- Always use type hints: `def add_task(db, name: str) -> UUID:`

### Database Operations
```python
stmt = select(Task).where(Task.id == task_id)
result = db.execute(stmt).scalars().first()
db.add(db_task)
db.commit()
db.refresh(db_task)
```

### Error Handling
```python
# Business logic — raise Exception
if len(lst) > 1:
    raise Exception(f'Too much ({len(lst)}) prompts for task_id=={task_id}.')

# API errors — use HTTPException
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
```

### Testing
- Tests in `back/tests/` with `test_*.py` naming
- Fixtures: `db_session`, `platform`, `seeded_task`, `authenticated_client`
- Assertion pattern: `pytest.raises(Exception, match="pattern")`

---

## Frontend Guidelines (TypeScript/React)

### Structure
```
front/
├── app/          # Next.js pages
├── lib/
│   ├── api.ts    # User-facing API client functions
│   ├── adminApi.ts  # Admin API client (HTTP Basic Auth)
│   ├── math.ts   # Shared LaTeX preprocessing (3 functions)
│   ├── components/
│   ├── contexts/ # React Context providers
│   ├── types/    # TypeScript interfaces
│   └── __tests__/ # Unit tests
```

### Components
```typescript
"use client";

import { useContext } from "react";
import { TasksContext } from "@/lib/contexts/TasksProvider";

interface Props {
    isEnabled: boolean;
    tasks: Task[];
}

export default function Tasks({ isEnabled, tasks }: Props) {
    return <div>...</div>;
}
```

### Types
```typescript
export interface Task {
    id: string;
    name: string;
    done: number;
    total: number;
}
```

### API Calls
```typescript
import { getTasks, updateVote } from "@/lib/api";
const tasks = await getTasks();
await updateVote({ task_instance_id, ... });
```

---

## Math Rendering Pipeline

All LaTeX goes through this pipeline before `marked()` renders it to HTML:

```
preprocessLatexDelimiters  →  normalizeMathBlockSpacing  →  preprocessLatexNewlines  →  marked + KaTeX
```

---

## Admin Auth

The admin UI at `/admin` uses HTTP Basic Auth. Credentials come from environment variables:

- `ADMIN_USERNAME` — default `admin`
- `ADMIN_PASSWORD` — default `changeme`

**Endpoints**:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/admin/stats` | Task/prompt/generation counts |
| `GET` | `/admin/tasks` | All tasks with prompt counts |
| `GET` | `/admin/tasks/{id}/prompts?page=&per_page=` | Paginated prompts for a task |
| `GET` | `/admin/prompts/{id}` | Full prompt text + all generations |
| `GET` | `/admin/generations/{id}` | Single generation detail |
| `PUT` | `/admin/prompts/{id}/text` | Update prompt text (logged) |
| `PUT` | `/admin/generations/{id}/text` | Update generation text (logged) |
| `GET` | `/admin/audit-logs` | View edit history for an entity |

All changes to prompt/generation text are recorded in `admin_audit_logs` with before/after text, admin username, and timestamp.

---

## Key Conventions

| Element   | Backend        | Frontend        |
|-----------|---------------|-----------------|
| Classes   | PascalCase    | PascalCase      |
| Functions | snake_case    | camelCase       |
| Variables | snake_case    | camelCase       |
| Constants | UPPER_CASE    | UPPER_CASE      |
| Files     | snake_case.py | camelCase.ts    |

### Database Schema
- **Users**: Integer PK, UUID sessions
- **Tasks**: UUID PK, linked to Instructions
- **Generations**: UUID PK, linked to Prompts
- **Bots**: One bot per user (enforced)
- **AdminAuditLog**: Tracks text edits with before/after

### API Patterns
- **User auth**: Cookie-based (`session_id`), uses `_get_user_id` dependency
- **Admin auth**: HTTP Basic Auth via `_require_admin` dependency
- Pydantic models define schemas
- FastAPI dependency injection for DB

### State Management
- React Context for global state
- Tailwind CSS v4 with typography plugin

---

## Adding a New API Endpoint

### Regular (user-facing) endpoint
1. Define Pydantic models in `main.py`
2. Create endpoint with `Depends(get_db)`
3. Add `_get_user_id` if authenticated
4. Write tests using `api_client` fixture
5. Add TypeScript types in `front/lib/types/`
6. Add API function in `front/lib/api.ts`

### Admin endpoint
1. Same as above, but use `_=Depends(_require_admin)` instead of `_get_user_id`
2. Add admin types in `front/lib/types/admin.ts`
3. Add API function in `front/lib/adminApi.ts` (uses `put()` or `get()` helpers with Basic Auth)
