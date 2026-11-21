#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

is_python311() {
    "$1" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 11) else 1)' >/dev/null 2>&1
}

find_python311() {
    for candidate in \
        "$SCRIPT_DIR/.venv/bin/python" \
        "$SCRIPT_DIR/.venv/bin/python3"
    do
        if [ -x "$candidate" ] && is_python311 "$candidate"; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done

    for candidate_name in python3.11 python3 python; do
        if command -v "$candidate_name" >/dev/null 2>&1; then
            candidate=$(command -v "$candidate_name")
            if [ -x "$candidate" ] && is_python311 "$candidate"; then
                printf '%s\n' "$candidate"
                return 0
            fi
        fi
    done

    return 1
}

PYTHON=$(find_python311 || true)
if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.11 was not found."
    echo "Install Python 3.11 and create the virtual environment with it:"
    echo "  python3.11 -m venv .venv"
    echo "  .venv/bin/python -m pip install -r requirements.txt"
    echo "See docs/python311-trixie.md for full instructions."
    exit 1
fi

export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export FLASK_DEBUG=0

echo
echo "Initializing admin account only if the database is empty..."
"$PYTHON" "$SCRIPT_DIR/init_admin.py" --skip-existing
echo
echo "Starting application at http://0.0.0.0:5000"
"$PYTHON" "$SCRIPT_DIR/run.py"
