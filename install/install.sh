#!/usr/bin/env bash
# TEFLoN2 installation helper: checks the dependencies and downloads the latest Dfam TE library.
# Usage: bash install/install.sh [--taxon NAME] [--skip-library] [--outdir DIR]
set -euo pipefail
cd "$(dirname "$0")/.."

TAXON=""; SKIP_LIB=0; OUTDIR="data_input/library"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --taxon) TAXON="$2"; shift 2;;
    --skip-library) SKIP_LIB=1; shift;;
    --outdir) OUTDIR="$2"; shift 2;;
    -h|--help) sed -n '2,3p' "$0"; exit 0;;
    *) echo "Unknown option: $1" >&2; exit 1;;
  esac
done

echo "== Checking dependencies"
missing=0
for tool in python3 bwa samtools awk snakemake; do
  if command -v "$tool" >/dev/null 2>&1; then printf '  [ok]      %s (%s)\n' "$tool" "$(command -v "$tool")"
  else printf '  [MISSING] %s\n' "$tool"; missing=1; fi
done
for tool in RepeatMasker fastp singularity bgzip tabix; do
  command -v "$tool" >/dev/null 2>&1 && printf '  [ok]      %s (optional)\n' "$tool" || printf '  [absent]  %s (optional)\n' "$tool"
done
python3 -c "import numpy" 2>/dev/null && echo "  [ok]      numpy (HTML report)" || echo "  [absent]  numpy (needed for the population part of the HTML report: pip install numpy)"
[[ $missing -eq 1 ]] && echo "  -> install the missing tools (see docs: Installation) before running the pipeline."

if [[ $SKIP_LIB -eq 0 ]]; then
  echo "== Downloading the latest Dfam library into $OUTDIR"
  args=(-o "$OUTDIR")
  if [[ -n "$TAXON" ]]; then
    python3 -c "import h5py" 2>/dev/null || python3 -m pip install --user h5py
    args+=(--taxon "$TAXON")
  fi
  python3 install/download_dfam.py "${args[@]}"
fi
echo "== Next step: python3 teflon2_configure.py"
