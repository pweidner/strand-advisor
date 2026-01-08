set -euo pipefail

die() { echo "[ERROR] $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "Missing dependency in PATH: $1"; }
