# CLAUDE.md — unitysvc-py

Customer-facing Python SDK + CLI for the UnitySVC platform. Lets
customers manage secrets, aliases, and recurrent requests via
`unitysvc.Client` (sync) / `AsyncClient` (async) or the `usvc` CLI.

## Key directories

| Path | Purpose |
|------|---------|
| `src/unitysvc/` | Package root — client, resource facades, CLI, utilities |
| `src/unitysvc/_generated/` | Auto-generated HTTP client from OpenAPI spec. **Do not edit by hand.** |
| `src/unitysvc/commands/` | CLI command implementations (typer) |
| `scripts/` | Code-generation and doc-generation scripts |
| `docs/` | mkdocs site — tutorials (guides) and references |
| `openapi.json` | Committed snapshot of the customer OpenAPI spec (input for code gen) |

## Commands

```bash
# Tests
uv run --extra test pytest tests/

# Linting
uv run --extra test ruff check src/ tests/

# Type checking
uv run --extra test mypy src/unitysvc/ --exclude _generated

# Build docs site
uv run --extra docs mkdocs build

# Serve docs locally
uv run --extra docs mkdocs serve
```

## Regeneration workflows

When the backend API changes, two things need updating:

### 1. Regenerate the HTTP client (from OpenAPI spec)

```bash
./scripts/generate_client.sh [path/to/customer_api.json]
```

- Copies the spec to `openapi.json`
- Runs `openapi-python-client generate` → `src/unitysvc/_generated/`
- Default spec path: `../unitysvc/backend/generated/customer_api.json`

### 2. Regenerate the CLI reference

```bash
./scripts/generate_cli_reference.sh
```

- Uses `typer utils docs` to produce `docs/cli-reference.md`
- Must be re-run whenever CLI commands or options change

### 3. Update the SDK reference

`docs/sdk-reference.md` uses mkdocstrings directives — it auto-generates
from Python docstrings at `mkdocs build` time. When you add a new resource
class, add a `:::` block for it in `docs/sdk-reference.md`.

### After any API change, the full sequence is:

```bash
./scripts/generate_client.sh          # 1. regen HTTP client
# edit resources/ if the facade needs changes
./scripts/generate_cli_reference.sh   # 2. regen CLI reference
# add mkdocstrings entry in docs/sdk-reference.md if new resource
uv run --extra docs mkdocs build      # 3. verify docs build
uv run --extra test pytest tests/     # 4. verify tests pass
```

## Conventions

- `ruff` excludes `src/unitysvc/_generated/` (byte-stable codegen output)
- Docstring style: Google
- Python >= 3.11
- Package manager: uv
- CLI entry point: `usvc` (typer app at `unitysvc.cli:app`)

## Docs structure

- **`*-reference.md`** files are auto-generated or mkdocstrings-powered. They must match the implementation exactly.
- **`*-guide.md`** files are hand-written tutorials. They don't need updating with every API change.
