from contextlib import closing
from datetime import datetime
from pathlib import Path
import sqlite3

from flask import current_app

from .extensions import db


class DatabaseBackupError(Exception):
    """Raised when a consistent SQLite backup cannot be created."""


def _remove_partial_backup(path):
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def create_sqlite_backup():
    if db.engine.dialect.name != "sqlite":
        raise DatabaseBackupError("Chỉ hỗ trợ sao lưu SQLite.")

    database_name = db.engine.url.database
    if not database_name or database_name == ":memory:":
        raise DatabaseBackupError("Không tìm thấy file SQLite để sao lưu.")

    database_path = Path(database_name)
    if not database_path.is_absolute():
        database_path = Path(current_app.instance_path) / database_path
    database_path = database_path.resolve()
    if not database_path.is_file():
        raise DatabaseBackupError(f"Không tìm thấy database: {database_path}")

    backup_dir = Path(current_app.instance_path) / "backups"
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup_path = backup_dir / f"family_expenses-{timestamp}.sqlite3"
        source_uri = f"{database_path.as_uri()}?mode=ro"

        with closing(sqlite3.connect(source_uri, uri=True)) as source, closing(
            sqlite3.connect(str(backup_path))
        ) as destination:
            source.backup(destination)
            integrity = destination.execute("PRAGMA integrity_check").fetchone()
            if not integrity or integrity[0] != "ok":
                raise DatabaseBackupError("Kiểm tra tính toàn vẹn của bản sao lưu thất bại.")
    except DatabaseBackupError:
        if "backup_path" in locals():
            _remove_partial_backup(backup_path)
        raise
    except (OSError, sqlite3.Error) as error:
        if "backup_path" in locals():
            _remove_partial_backup(backup_path)
        raise DatabaseBackupError(f"Không thể sao lưu database: {error}") from error

    return backup_path
