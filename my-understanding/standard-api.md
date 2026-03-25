# API Documentation Standard

## Folder Structure

The industry-standard convention is to place all documentation under a `docs/` folder at the project root.

```
docs/
├── api/                    ← all endpoint documentation lives here
│   ├── README.md           ← index/overview of all API services
│   ├── auth/               ← one folder per feature/service
│   │   ├── README.md       ← overview table + shared notes for this service
│   │   ├── signin.md       ← one file per endpoint
│   │   ├── signup.md
│   │   └── ...
│   ├── community/
│   ├── dining-halls/
│   └── ...
├── architecture.md         ← system design, infrastructure decisions
├── db-doc.md               ← database schema documentation
└── ...                     ← other project-level docs
```

## Key Principles

### 1. One File Per Endpoint

Each API endpoint gets its own markdown file. This gives you:

- **Discoverability** — devs find exactly what they need without scrolling through a monolith
- **Git-friendly** — PRs only touch the file for the endpoint that changed (cleaner diffs, blame, reviews)
- **Ownership** — easy to assign reviewers per endpoint
- **Scalability** — adding a new endpoint = adding a new file, no merge conflicts on a shared doc

### 2. README.md as the Index

Each feature folder has a `README.md` that acts as the overview/index:

- Service description (one-liner about what this service handles)
- Shared notes (e.g. authentication header requirements)
- Endpoints overview table (method, endpoint, description, auth required)
- Links to individual endpoint files

### 3. Individual Endpoint File Structure

Each endpoint file (e.g. `signin.md`) should contain:

```markdown
# POST /auth/signin

Short description of what this endpoint does.

## Request

### Headers
(if applicable, e.g. Authorization)

### Body
(JSON example with field descriptions)

## Response

### Success (200 OK)
(JSON example)

### Errors
- `400 Bad Request` — reason
- `401 Unauthorized` — reason
```

### 4. Language

All documentation should be written in **English** for consistency and accessibility across the team.

### 5. Source of Truth

- Hand-written docs in `docs/api/` are fine for planning and design phase
- Once the backend is built, FastAPI auto-generates OpenAPI/Swagger docs from code docstrings
- The rendered interactive docs live at `/docs` (Swagger UI) and `/redoc` (ReDoc) when the server runs
- Eventually, code annotations become the single source of truth and `docs/api/` serves as the human-readable supplement
