#!/usr/bin/env bash
# Regenerate the low-level customer API client from the committed customer spec.
#
# Usage:
#     ./scripts/generate_client.sh [path/to/customer_api.json]
#
# With no argument, reads the spec from the sibling unitysvc checkout:
#
#     ../unitysvc/backend/generated/customer_api.json
#
# That file is produced by `inv generate-client` in the unitysvc repo,
# which dumps the OpenAPI spec of a customer-only FastAPI sub-app — no
# filtering or sanitization is needed on this side, the upstream
# sub-app already emits a spec containing only customer-tagged
# operations and their reachable schemas.
#
# Requirements:
#   - openapi-python-client installed. If not on PATH, this script
#     bootstraps it in .tool-venv/.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEFAULT_SPEC="${REPO_ROOT}/../unitysvc/backend/generated/customer_api.json"
SPEC_PATH="${1:-${DEFAULT_SPEC}}"

if [ ! -f "${SPEC_PATH}" ]; then
    cat >&2 <<ERR
error: spec file not found: ${SPEC_PATH}

The unitysvc-py SDK is generated from a customer-filtered OpenAPI spec
produced by the sibling unitysvc repo. Options:

  1. Check out unitysvc alongside this repo and run 'inv generate-client'
     there. That writes backend/generated/customer_api.json, which this
     script reads by default.

  2. Pass an explicit spec path as the first argument:

         ./scripts/generate_client.sh /path/to/customer_api.json

ERR
    exit 1
fi

# ---------------------------------------------------------------------------
# Tool bootstrap
# ---------------------------------------------------------------------------
if ! command -v openapi-python-client >/dev/null 2>&1; then
    if [ ! -x "${REPO_ROOT}/.tool-venv/bin/openapi-python-client" ]; then
        echo "==> Bootstrapping openapi-python-client into .tool-venv"
        # Requires Python 3.10+; prefer a recent version if available.
        PYTHON=$(command -v python3.13 || command -v python3.12 || command -v python3.11 || command -v python3.10 || command -v python3)
        "${PYTHON}" -m venv "${REPO_ROOT}/.tool-venv"
        "${REPO_ROOT}/.tool-venv/bin/pip" install --quiet "openapi-python-client @ git+https://github.com/openapi-generators/openapi-python-client@v0.28.3"
    fi
    OAPI_CLIENT="${REPO_ROOT}/.tool-venv/bin/openapi-python-client"
else
    OAPI_CLIENT="$(command -v openapi-python-client)"
fi

# ---------------------------------------------------------------------------
# Mirror the spec into the repo so the committed copy is always in sync
# with what the generated client was last produced from.
# ---------------------------------------------------------------------------
cp "${SPEC_PATH}" "${REPO_ROOT}/openapi.json"
echo "==> Using spec: ${SPEC_PATH}"
echo "    Copied to:  openapi.json (tracked)"

# ---------------------------------------------------------------------------
# Regenerate client
# ---------------------------------------------------------------------------
echo "==> Regenerating src/unitysvc/_generated/"
cd "${REPO_ROOT}"
rm -rf src/unitysvc/_generated
"${OAPI_CLIENT}" generate \
    --path openapi.json \
    --config scripts/openapi-python-client.yml \
    --meta none \
    --output-path src/unitysvc/_generated \
    --overwrite

echo
echo "==> Done. Review the diff, run tests, and commit:"
echo "      python -m pytest tests/"
