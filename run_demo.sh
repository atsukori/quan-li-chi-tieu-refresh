#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

if [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python"
elif [ -x "$SCRIPT_DIR/.venv/bin/python3" ]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
else
    PYTHON="$(command -v python)"
fi

if [ ! -x "$PYTHON" ] && [ ! -f "$PYTHON" ]; then
    echo "ERROR: Cannot find a usable Python interpreter."
    echo "Create the virtual environment first:"
    echo "  python3 -m venv .venv"
    echo "  .venv/bin/python -m pip install -r requirements.txt"
    exit 1
fi

printf '
WARNING: Demo mode will DELETE the current database data and recreate demo data.
'
printf 'This removes existing accounts, categories, transactions, and budgets.

'
printf 'Continue? Press Y to reset to demo data or N to cancel: '
read ans || exit 1
case "$ans" in
    Y|y)
        ;;
    *)
        printf '
Cancelled. No database changes were made.
'
        exit 0
        ;;
esac

export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000

echo
echo "Creating demo database..."
"$PYTHON" "$SCRIPT_DIR/seed.py" --reset
echo
echo "Starting Flask at http://0.0.0.0:5000"
"$PYTHON" "$SCRIPT_DIR/run.py"
