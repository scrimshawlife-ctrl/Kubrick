#!/usr/bin/env bash
# Kubrick — Hermes Skill Installer
# Usage:
#   ./install.sh                 # installs to ~/.hermes/skills/kubrick  (recommended)
#   ./install.sh creative        # installs to ~/.hermes/skills/creative/kubrick
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_BASE="${HERMES_HOME:-$HOME/.hermes}/skills"
SUBDIR=""

if [[ "${1:-}" == "creative" || "${1:-}" == "categorized" ]]; then
  SUBDIR="creative/"
fi

DEST="${TARGET_BASE}/${SUBDIR}kubrick"

echo "Installing Kubrick to: ${DEST}"
mkdir -p "$(dirname "${DEST}")"

if [[ -d "${DEST}" ]]; then
  echo "Existing installation found. Backing up to ${DEST}.bak"
  rm -rf "${DEST}.bak"
  mv "${DEST}" "${DEST}.bak"
fi

mkdir -p "${DEST}"
if command -v rsync >/dev/null 2>&1; then
  rsync -a \
    --exclude '.git/' \
    --exclude '.github/' \
    --exclude 'out/' \
    --exclude 'dist/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache/' \
    "${ROOT}/" "${DEST}/"
else
  # Fallback: copy then strip heavy/meta dirs
  cp -R "${ROOT}/." "${DEST}/"
  rm -rf "${DEST}/.git" "${DEST}/.github" "${DEST}/out" "${DEST}/dist" 2>/dev/null || true
fi

chmod +x "${DEST}/scripts/"*.py 2>/dev/null || true
chmod +x "${DEST}/scripts/"*.sh 2>/dev/null || true
chmod +x "${DEST}/install.sh" 2>/dev/null || true

echo ""
echo "Kubrick installed successfully."
echo "Location: ${DEST}"
echo ""
echo "Validate:"
echo "  python3 ${DEST}/scripts/kubrick.py do check --action smoke"
echo ""
echo "Try prompts like:"
echo "  develop a screenplay visual system"
echo "  storyboard continuity for a sci-fi short"
echo "  single-frame image prompt with motif continuity"
echo ""
echo "Standalone Hermes skill — Continuity Forge optional."
