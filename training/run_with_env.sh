#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LD_LIBRARY_PATH="/nix/store/06fzc209czv9cyp74p8x8ciza9456084-ld-library-path/share/nix-ld/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export MPLCONFIGDIR="${ROOT_DIR}/.mpl-cache"
mkdir -p "${MPLCONFIGDIR}"

exec "${ROOT_DIR}/.venv/bin/python" "$@"
