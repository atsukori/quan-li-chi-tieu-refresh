import os
from app import create_app

app = create_app()


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "1").strip().lower() in {"1", "true", "yes"}
    host = os.getenv("FLASK_HOST", "127.0.0.1").strip() or "127.0.0.1"
    try:
        port = int(os.getenv("FLASK_PORT", "5000"))
    except ValueError:
        port = 5000
    app.run(host=host, port=port, debug=debug_mode)
