#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFIX="${PREFIX:-$HOME/.local}"

# Python 3.11+ is required.
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "error: python3 not found (Python 3.11+ required)" >&2
  exit 1
fi
if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
  echo "error: Python 3.11+ required" >&2
  exit 1
fi

echo "Installing ForgeStack CLI into $PREFIX/bin"
mkdir -p "$PREFIX/bin"

"$PYTHON" -m pip install --quiet --upgrade "$REPO_ROOT"

ln -sf "$PREFIX/bin/forgestack" "$PREFIX/bin/forgestack" >/dev/null 2>&1 || true

if ! "$PREFIX/bin/forgestack" --help >/dev/null 2>&1; then
  echo "error: install failed; is $PREFIX/bin on PATH?" >&2
  exit 1
fi

cat <<'EOF'

ForgeStack installed.

Next steps:
  1. Ensure $PREFIX/bin is on your PATH.
  2. Run: forgestack setup
EOF