from contextlib import closing
from datetime import datetime
from pathlib import Path
import sqlite3
import sys

from app import create_app
from app.extensions import db


def main():
    app = create_app()
    with app.app_context():
        if db.engine.dialect.name != "sqlite":
            raise SystemExit("Chỉ hỗ trợ sao lưu SQLite.")

        database_name = db.engine.url.database
        if not database_name or database_name == ":memory:":
            raise SystemExit("Không tìm thấy file SQLite để sao lưu.")

        database_path = Path(database_name)
        if not database_path.is_absolute():
            database_path = Path(app.instance_path) / database_path
        database_path = database_path.resolve()
        if not database_path.is_file():
            raise SystemExit(f"Không tìm thấy database: {database_path}")

        backup_dir = Path(app.instance_path) / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup_path = backup_dir / f"family_expenses-{timestamp}.sqlite3"
        source_uri = f"{database_path.as_uri()}?mode=ro"

        try:
            with closing(sqlite3.connect(source_uri, uri=True)) as source, closing(
                sqlite3.connect(str(backup_path))
            ) as destination:
                source.backup(destination)
                integrity = destination.execute("PRAGMA integrity_check").fetchone()
                if not integrity or integrity[0] != "ok":
                    raise RuntimeError(f"Kiểm tra bản sao lưu thất bại: {integrity}")
        except Exception as error:
            backup_path.unlink(missing_ok=True)
            print(f"Không thể sao lưu database: {error}", file=sys.stderr)
            raise SystemExit(1) from error

        print(f"Đã sao lưu và kiểm tra SQLite thành công: {backup_path}")


if __name__ == "__main__":
    main()
