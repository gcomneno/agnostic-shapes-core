#!/usr/bin/env bash
#
# scripts/release.sh — Release flow for Agnostic SHAPES Core.
#
# Usage:
#   scripts/release.sh --dry-run <version>
#   scripts/release.sh <version>
#
# The release metadata must already be reviewed and committed before this
# script is run. The script validates that state; it does not manufacture
# release metadata immediately before tagging.
#
set -euo pipefail

CONCEPT_DOI="10.5281/zenodo.22741778"
CONCEPT_RECORD_URL="https://zenodo.org/records/22741778"

REPO_DIR="$(git rev-parse --show-toplevel)"
PARENT_DIR="$(dirname "${REPO_DIR}")"

if [[ -x "${REPO_DIR}/.venv/bin/python" ]]; then
    PYTHON="${REPO_DIR}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
else
    printf 'ERROR: no usable Python interpreter found\n' >&2
    return 127 2>/dev/null || false
fi

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=1
    shift
fi

VERSION="${1:-}"

if [[ -z "${VERSION}" ]]; then
    printf 'ERROR: usage: %s [--dry-run] <version>\n' "$0" >&2
    return 2 2>/dev/null || false
fi

if [[ ! "${VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    printf 'ERROR: invalid version: %s\n' "${VERSION}" >&2
    return 2 2>/dev/null || false
fi

TAG="v${VERSION}"
TODAY="$(date +%F)"

ARCHIVE="${PARENT_DIR}/agnostic-shapes-core-${VERSION}.zip"
CHECKSUM="${PARENT_DIR}/agnostic-shapes-core-${VERSION}.sha256"
NOTES="${REPO_DIR}/RELEASE_NOTES_v${VERSION}.md"

fail() {
    printf 'RELEASE_GATE=FAIL: %s\n' "$*" >&2
    return 1
}

read_pyproject_version() {
    "${PYTHON}" - <<'PY'
from pathlib import Path
import re

text = Path("pyproject.toml").read_text()
match = re.search(r'(?m)^version = "([^"]+)"$', text)
if match is None:
    raise SystemExit("missing pyproject version")
print(match.group(1))
PY
}

read_citation_field() {
    local field="$1"

    "${PYTHON}" - "${field}" <<'PY'
from pathlib import Path
import re
import sys

field = sys.argv[1]
text = Path("CITATION.cff").read_text()
match = re.search(rf'(?m)^{re.escape(field)}:\s*"?([^"\n]+)"?\s*$', text)
if match is None:
    raise SystemExit(f"missing CITATION field: {field}")
print(match.group(1))
PY
}

printf '===== ASHES RELEASE %s =====\n' "${TAG}"
printf 'MODE=%s\n' "$([[ "${DRY_RUN}" == "1" ]] && printf DRY_RUN || printf PUBLISH)"

cd "${REPO_DIR}"

printf '\n===== RELEASE STATE =====\n'

[[ -z "$(git status --porcelain)" ]] || fail "working tree is not clean"

PYPROJECT_VERSION="$(read_pyproject_version)"
CITATION_VERSION="$(read_citation_field version)"
CITATION_DATE="$(read_citation_field date-released)"

[[ "${PYPROJECT_VERSION}" == "${VERSION}" ]] \
    || fail "pyproject version=${PYPROJECT_VERSION}, expected=${VERSION}"

[[ "${CITATION_VERSION}" == "${VERSION}" ]] \
    || fail "CITATION version=${CITATION_VERSION}, expected=${VERSION}"

[[ "${CITATION_DATE}" == "${TODAY}" ]] \
    || fail "CITATION date=${CITATION_DATE}, release date=${TODAY}"

if grep -q '^doi:' CITATION.cff; then
    fail "CITATION.cff contains a version DOI before Zenodo publication"
fi

grep -q "^## \[${VERSION}\] — ${TODAY}$" CHANGELOG.md \
    || fail "CHANGELOG release heading missing or date mismatch"

[[ -f "${NOTES}" ]] || fail "release notes missing: ${NOTES}"

if git rev-parse "${TAG}" >/dev/null 2>&1; then
    fail "tag already exists: ${TAG}"
fi

if [[ "${DRY_RUN}" != "1" ]]; then
    [[ "$(git branch --show-current)" == "main" ]] \
        || fail "publishing is allowed only from main"

    git fetch origin --prune

    [[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] \
        || fail "local main is not aligned with origin/main"
fi

printf 'RELEASE_METADATA_GATE=PASS\n'

printf '\n===== QUALITY GATES =====\n'

if [[ -d ".venv" ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

"${PYTHON}" -m pip install -e '.[dev]' -q
"${PYTHON}" -m pip install -e './resolver[test]' -q

"${PYTHON}" -m pytest -q -m "not slow"
"${PYTHON}" -m ruff check src tests resolver/src resolver/tests
"${PYTHON}" -m mypy src/shapes src/petra
"${PYTHON}" -m mypy --config-file resolver/pyproject.toml resolver/src/resolver
make docs-check
git diff --check

printf 'QUALITY_GATE=PASS\n'

printf '\n===== RELEASE ARTIFACT =====\n'

rm -f "${ARCHIVE}" "${CHECKSUM}"

if [[ "${DRY_RUN}" == "1" ]]; then
    ARCHIVE_REF="HEAD"
else
    git tag -a "${TAG}" -m "Agnostic SHAPES Core ${TAG}"
    ARCHIVE_REF="${TAG}"
fi

git archive \
    --format=zip \
    --prefix="agnostic-shapes-core-${VERSION}/" \
    -o "${ARCHIVE}" \
    "${ARCHIVE_REF}"

(
    cd "${PARENT_DIR}"
    sha256sum "$(basename "${ARCHIVE}")" > "$(basename "${CHECKSUM}")"
    sha256sum -c "$(basename "${CHECKSUM}")"
)

printf 'ARCHIVE=%s\n' "${ARCHIVE}"
printf 'CHECKSUM=%s\n' "${CHECKSUM}"
printf 'ARTIFACT_GATE=PASS\n'

if [[ "${DRY_RUN}" == "1" ]]; then
    printf '\nDRY_RUN_GATE=PASS\n'
    printf 'NO_TAG_CREATED=PASS\n'
    printf 'NO_PUSH_PERFORMED=PASS\n'
    printf 'NO_GITHUB_RELEASE_CREATED=PASS\n'
else
    printf '\n===== PUBLISH GITHUB RELEASE =====\n'

    git push origin "${TAG}"

    gh release create "${TAG}" \
        --repo gcomneno/agnostic-shapes-core \
        --title "Agnostic SHAPES Core ${TAG}" \
        --notes-file "${NOTES}" \
        --latest \
        "${ARCHIVE}" \
        "${CHECKSUM}"

    printf 'GITHUB_RELEASE_GATE=PASS\n'

    cat <<REMINDER

===== ZENODO FOLLOW-UP =====

GitHub release ${TAG} is published.

Zenodo repository integration is enabled for:

    gcomneno/agnostic-shapes-core

Concept DOI:

    ${CONCEPT_DOI}

Concept record:

    ${CONCEPT_RECORD_URL}

Verify that Zenodo automatically creates the ${TAG} record.

Do not reuse a historical PETRA Version DOI.

After Zenodo assigns the new Version DOI:

1. add that DOI to CITATION.cff;
2. add it under CHANGELOG.md -> ${VERSION} -> Published;
3. commit the metadata annotation separately.

ZENODO_VERSION_DOI=PENDING
REMINDER
fi
