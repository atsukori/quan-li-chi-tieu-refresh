import sys

from app import create_app
from app.backups import DatabaseBackupError, create_sqlite_backup


def main():
    app = create_app()
    with app.app_context():
        try:
            backup_path = create_sqlite_backup()
        except DatabaseBackupError as error:
            print(error, file=sys.stderr)
            raise SystemExit(1) from error

        print(f"Đã sao lưu và kiểm tra SQLite thành công: {backup_path}")


if __name__ == "__main__":
    main()
