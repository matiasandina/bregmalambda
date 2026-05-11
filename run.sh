#!/usr/bin/env bash
# Launch the planner in a local browser. Atlas must be built first:
#   source .venv/bin/activate && python slicer/build_atlas.py
set -e
cd "$(dirname "$0")"
PORT="${PORT:-8765}"
echo "open http://localhost:${PORT}/  (Ctrl-C to stop)"
exec python3 -m http.server "$PORT"
