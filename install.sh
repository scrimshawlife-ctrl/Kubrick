#!/usr/bin/env bash
# Install Kubrick as an OpenClaw skill. Hermes remains available as an option.

set -euo pipefail

PLATFORM="openclaw"
DEST=""

usage() {
  cat <<'EOF'
Usage: ./install.sh [--openclaw|--hermes] [--dest PATH]

Defaults:
  platform: OpenClaw
  path:     ~/.openclaw/skills/kubrick

Examples:
  ./install.sh
  ./install.sh --hermes
  ./install.sh --dest /custom/skills/kubrick
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --openclaw)
      PLATFORM="openclaw"
      ;;
    --hermes)
      PLATFORM="hermes"
      ;;
    --dest)
      shift
      [ "$#" -gt 0 ] || { echo "--dest requires a path" >&2; exit 2; }
      DEST="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

SOURCE="$(cd "$(dirname "$0")" && pwd)"
if [ -z "$DEST" ]; then
  if [ "$PLATFORM" = "openclaw" ]; then
    DEST="${HOME}/.openclaw/skills/kubrick"
  else
    DEST="${HOME}/.hermes/skills/kubrick"
  fi
fi

DEST_PARENT="$(dirname "$DEST")"
mkdir -p "$DEST_PARENT"

if [ -d "$DEST" ] && [ "$(cd "$DEST" && pwd -P)" = "$SOURCE" ]; then
  echo "Kubrick is already located at the requested destination: ${DEST}"
  exit 0
fi

if [ -e "$DEST" ] || [ -L "$DEST" ]; then
  STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
  BACKUP="${DEST}.backup-${STAMP}"
  echo "Existing installation moved to: ${BACKUP}"
  mv "$DEST" "$BACKUP"
fi

mkdir -p "$DEST"
(
  cd "$SOURCE"
  tar \
    --exclude='./.git' \
    --exclude='./.DS_Store' \
    --exclude='./__pycache__' \
    --exclude='./references/usage/receipts' \
    --exclude='./references/usage/evolution' \
    -cf - .
) | tar -xf - -C "$DEST"

chmod +x "$DEST"/scripts/*.py 2>/dev/null || true

echo "Kubrick installed for ${PLATFORM}: ${DEST}"
echo "Run: python3 ${DEST}/scripts/doctor.py"
if ! python3 -c 'import yaml' >/dev/null 2>&1; then
  echo "PyYAML is not installed. JSON briefs work now; for YAML run:"
  echo "  python3 -m pip install -r ${DEST}/requirements.txt"
fi
