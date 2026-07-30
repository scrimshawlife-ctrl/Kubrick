#!/usr/bin/env bash
# Package Kubrick for NousResearch/hermes-agent optional-skills/creative/kubrick.
# Usage:
#   ./scripts/package_optional_skill.sh /path/to/hermes-agent
#   ./scripts/package_optional_skill.sh ./dist/hermes-agent-package
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_ROOT="${1:-}"

if [[ -z "${DEST_ROOT}" ]]; then
  echo "Usage: $0 <hermes-agent-repo-or-output-dir>" >&2
  exit 2
fi

TARGET="${DEST_ROOT%/}/optional-skills/creative/kubrick"
mkdir -p "${TARGET}"

# Core skill payload only — exclude git metadata, CI, historical planning docs,
# and packaging helpers that are not needed inside hermes-agent.
rsync -a --delete \
  --exclude '.git/' \
  --exclude '.github/' \
  --exclude 'dist/' \
  --exclude 'out/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.pytest_cache/' \
  --exclude 'docs/superpowers/' \
  --exclude 'docs/ROADMAP-v0.11.md' \
  --exclude 'docs/ROADMAP-v0.12.md' \
  --exclude 'docs/RELEASE-CHECKLIST-v0.12.md' \
  --exclude 'docs/RELEASE-NOTES-v0.12.md' \
  --exclude 'PR_BODY.md' \
  --exclude 'scripts/package_optional_skill.sh' \
  --exclude 'skills.sh.json' \
  "${ROOT}/" "${TARGET}/"

echo "Packaged → ${TARGET}"
echo
echo "File inventory (depth ≤3):"
find "${TARGET}" -maxdepth 3 -type f | sort | head -200
echo "…"
echo "Total files: $(find "${TARGET}" -type f | wc -l)"
echo
echo "Sanity checks:"
test -f "${TARGET}/SKILL.md"
test -f "${TARGET}/LICENSE"
! rg -n '/home/|/Users/[A-Za-z]' "${TARGET}/SKILL.md" "${TARGET}/README.md" "${TARGET}/QUICKSTART.md" || true
rg -n 'license:|author:|name: kubrick' "${TARGET}/SKILL.md" | head -10
echo
echo "Next:"
echo "  cd ${DEST_ROOT}"
echo "  git checkout -b feat/add-kubrick-skill   # if this is a hermes-agent checkout"
echo "  git add optional-skills/creative/kubrick"
echo "  git commit -m 'feat(skills): add Kubrick cinematic design skill'"
