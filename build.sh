#!/usr/bin/env bash
set -euo pipefail
paper_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$paper_dir"
if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
elif command -v tectonic >/dev/null 2>&1; then
  tectonic main.tex --keep-logs --keep-intermediates
elif [[ -x ../tools/tectonic-0.17.0/tectonic ]]; then
  XDG_CACHE_HOME="$paper_dir/../tools/tectonic-cache" ../tools/tectonic-0.17.0/tectonic main.tex --keep-logs --keep-intermediates --only-cached
else
  echo 'Install TeX Live with latexmk, or Tectonic, then run bash build.sh.' >&2
  exit 1
fi
