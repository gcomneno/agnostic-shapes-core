#!/usr/bin/env bash
#
# scripts/release.sh — Flusso di release per Agnostic SHAPES Core.
#
# Uso:
#   scripts/release.sh <versione>              # release vera
#   scripts/release.sh --dry-run <versione>    # simulazione, nessun effetto
#
set -euo pipefail

# ---------- Configurazione ----------
CONCEPT_DOI="10.5281/zenodo.22741778"
CONCEPT_RECORD_URL="https://zenodo.org/records/22741778"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PARENT_DIR="$(dirname "${REPO_DIR}")"

# ---------- Colori ----------
C_RESET=$'\033[0m'
C_BOLD=$'\033[1m'
C_GREEN=$'\033[0;32m'
C_YELLOW=$'\033[0;33m'
C_RED=$'\033[0;31m'
C_BLUE=$'\033[0;34m'
C_DIM=$'\033[2m'

say()  { printf "${C_BLUE}==>${C_RESET} %s\n" "$*"; }
ok()   { printf "${C_GREEN}✅${C_RESET} %s\n" "$*"; }
warn() { printf "${C_YELLOW}⚠️ ${C_RESET}%s\n" "$*"; }
die()  { printf "${C_RED}❌${C_RESET} %s\n" "$*" >&2; exit 1; }
run()  {
  if [[ "${DRY_RUN}" == "1" ]]; then
    printf "${C_DIM}  [dry-run] %s${C_RESET}\n" "$*"
  else
    eval "$@"
  fi
}

# ---------- Argomenti ----------
DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  shift
fi

VERSION="${1:-}"
if [[ -z "${VERSION}" ]]; then
  die "Uso: $0 [--dry-run] <versione>   (es. 2.1.0)"
fi
if [[ ! "${VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  die "Formato versione non valido: '${VERSION}'. Atteso: X.Y.Z"
fi

TAG="v${VERSION}"
ARCHIVE="${PARENT_DIR}/agnostic-shapes-core-${VERSION}.zip"
CHECKSUM="${PARENT_DIR}/agnostic-shapes-core-${VERSION}.sha256"
NOTES="${PARENT_DIR}/RELEASE_NOTES_v${VERSION}.md"

# ---------- Controlli preliminari ----------
say "Release Agnostic SHAPES Core ${TAG} $( [[ ${DRY_RUN} == 1 ]] && echo '(DRY-RUN)' )"

[[ -f "pyproject.toml" ]] || die "pyproject.toml non trovato: esegui dalla root del repository."

if [[ -n "$(git status --porcelain)" ]]; then
  warn "Working tree non pulito:"
  git status --short
  if [[ "${DRY_RUN}" == "1" ]]; then
    warn "(dry-run: proseguo comunque)"
  else
    read -rp "Continuare comunque? [y/N] " ans
    [[ "${ans}" =~ ^[Yy]$ ]] || die "Interrotto dall'utente."
  fi
fi

if git rev-parse "${TAG}" >/dev/null 2>&1; then
  die "Il tag ${TAG} esiste già. Scegli un'altra versione o cancellalo."
fi

if [[ ! -f "${NOTES}" ]]; then
  warn "Release notes non trovate: ${NOTES}"
  if [[ "${DRY_RUN}" != "1" ]]; then
    read -rp "Continuare comunque? [y/N] " ans
    [[ "${ans}" =~ ^[Yy]$ ]] || die "Interrotto dall'utente."
  fi
fi

# ---------- 1. Bump versioni ----------
say "1/8 — Bump versioni: ${VERSION}"
run "sed -i.bak 's/^version = \".*\"/version = \"${VERSION}\"/' pyproject.toml"
run "rm -f pyproject.toml.bak"
if [[ "${DRY_RUN}" != "1" ]]; then
  grep -n '^version' pyproject.toml
  grep -n '^version' resolver/pyproject.toml
fi

# ---------- 2. Changelog ----------
say "2/8 — CHANGELOG.md"
if [[ "${DRY_RUN}" == "1" ]]; then
  warn "(dry-run: salto la pausa sul changelog)"
else
  warn "Aggiungi la voce [${VERSION}] in cima a CHANGELOG.md, poi premi INVIO."
  read -rp "Premi INVIO quando CHANGELOG.md è aggiornato..." _
  grep -q "^## \[${VERSION}\]" CHANGELOG.md || die "Voce [${VERSION}] non trovata nel CHANGELOG.md."
  ok "Voce [${VERSION}] presente."
fi

# ---------- 3. Test ----------
say "3/8 — Test"
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

run "python -m pip install -e '.[test]' -q"
run "python -m pytest tests/ -q"
run "ruff check src tests"
run "mypy src/shapes src/petra"

# ---------- 4. Commit + tag ----------
say "4/8 — Commit + tag"
run "git add CHANGELOG.md pyproject.toml README.md CITATION.cff docs/reports/STATUS.md scripts/release.sh"
run "git commit -m 'release: Agnostic SHAPES Core ${TAG}'"
run "git tag -a '${TAG}' -m 'Agnostic SHAPES Core ${TAG}'"

# ---------- 5. Archivio + checksum ----------
say "5/8 — Archivio + SHA256"
run "rm -f '${ARCHIVE}' '${CHECKSUM}'"
run "git -C '${REPO_DIR}' archive --format=zip --prefix='agnostic-shapes-core-${VERSION}/' -o '${ARCHIVE}' '${TAG}'"
run "cd '${PARENT_DIR}' && sha256sum \"\$(basename '${ARCHIVE}')\" > \"\$(basename '${CHECKSUM}')\""
if [[ "${DRY_RUN}" != "1" ]]; then
  ( cd "${PARENT_DIR}" && sha256sum -c "$(basename "${CHECKSUM}")" )
fi

# ---------- 6. Push ----------
say "6/8 — Push su origin"
run "git push origin main"
run "git push origin '${TAG}'"

# ---------- 7. GitHub Release ----------
say "7/8 — GitHub Release"
if [[ "${DRY_RUN}" == "1" ]]; then
  run "gh release create '${TAG}' --title 'Agnostic SHAPES Core ${TAG}' --notes-file '${NOTES}' --latest"
  run "gh release upload '${TAG}' '${ARCHIVE}' '${CHECKSUM}'"
else
  if gh release view "${TAG}" >/dev/null 2>&1; then
    warn "Release ${TAG} già esistente su GitHub. Salto."
  else
    if [[ -f "${NOTES}" ]]; then
      gh release create "${TAG}" \
        --title "Agnostic SHAPES Core ${TAG}" \
        --notes-file "${NOTES}" \
        --latest
    else
      gh release create "${TAG}" \
        --title "Agnostic SHAPES Core ${TAG}" \
        --generate-notes \
        --latest
    fi
    gh release upload "${TAG}" "${ARCHIVE}" "${CHECKSUM}"
    ok "GitHub Release ${TAG} pubblicata."
  fi
fi

# ---------- 8. Verifica Zenodo ----------
say "8/8 — Verifica archiviazione Zenodo"
cat <<REMINDER

${C_BOLD}============================================================${C_RESET}
${C_BOLD}  ✅ Release GitHub completata.${C_RESET}
${C_YELLOW}  ⚠️  Verifica l'archiviazione automatica Zenodo.${C_RESET}
${C_BOLD}============================================================${C_RESET}

  Repository Zenodo abilitato:
     gcomneno/agnostic-shapes-core

  Concept DOI storico:
     ${CONCEPT_DOI}

  Dopo la pubblicazione della GitHub Release:

  1. Apri la pagina GitHub integration di Zenodo.
  2. Verifica che la release ${TAG} venga acquisita senza errori.
  3. Apri il record Zenodo generato automaticamente.
  4. Verifica:
       Title:   Agnostic SHAPES Core ${TAG}
       Version: ${VERSION}
       Type:    Software
  5. Annota il nuovo Version DOI nel CHANGELOG/CITATION metadata
     con un commit separato, se necessario.

  Non creare manualmente una "New version" salvo fallimento esplicito
  dell'integrazione GitHub/Zenodo.

${C_BOLD}============================================================${C_RESET}
REMINDER

ok "Fatto."
