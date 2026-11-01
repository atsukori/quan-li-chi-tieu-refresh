import os
from app import create_app

app = create_app()


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0").strip().lower() in {"1", "true", "yes"}
    host = os.getenv("FLASK_HOST", "127.0.0.1").strip() or "127.0.0.1"
    try:
        port = int(os.getenv("FLASK_PORT", "5000"))
    except ValueError:
        port = 5000

    if debug_mode:
        app.run(host=host, port=port, debug=True)
    else:
        try:
            from waitress import serve
        except ImportError as error:
            raise SystemExit(
                "Waitress is missing. Install project dependencies with: "
                "python -m pip install -r requirements.txt"
            ) from error

        print(f"Starting Waitress on {host}:{port}. Press Ctrl+C to stop.", flush=True)
        if host == "0.0.0.0":
            print(f"Open http://<device-IP>:{port} from another device on the LAN.", flush=True)
        else:
            print(f"Open http://{host}:{port} in your browser.", flush=True)
        serve(app, host=host, port=port, threads=2)
