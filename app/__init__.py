import os
from datetime import date
from dotenv import load_dotenv
from flask import Flask, render_template
from sqlalchemy import event

load_dotenv()

from .config import Config
from .extensions import csrf, db, login_manager
from .utils import budget_period_label, budget_progress, source_label


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    with app.app_context():
        engine = db.engine
        if engine.dialect.name == "sqlite":
            def enable_sqlite_foreign_keys(connection, _record):
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
            event.listen(engine, "connect", enable_sqlite_foreign_keys)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Vui lòng đăng nhập để tiếp tục."
    login_manager.login_message_category = "info"

    from . import models
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .transactions.routes import transactions_bp
    from .admin.routes import admin_bp
    from .budgets.routes import budgets_bp
    from .reports.routes import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(transactions_bp, url_prefix="/transactions")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(budgets_bp, url_prefix="/budgets")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    # Add the audit table for existing installations without altering existing tables.
    with app.app_context():
        models.AuditLog.__table__.create(db.engine, checkfirst=True)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            user = db.session.get(models.User, int(user_id))
        except (TypeError, ValueError):
            return None
        if user is None or not user.is_active_account:
            return None
        return user

    @app.template_filter("vnd")
    def format_vnd(value):
        try:
            rendered = f"{float(value):,.0f}".replace(",", ".")
        except (TypeError, ValueError):
            rendered = "0"
        return f"{rendered} ₫"

    @app.template_filter("date_vn")
    def format_date_vn(value):
        return value.strftime("%d/%m/%Y") if value else "—"

    @app.context_processor
    def inject_template_helpers():
        today = date.today()
        return {"budget_period_label": budget_period_label, "budget_progress": budget_progress, "source_label": source_label, "current_year": today.year, "current_month": today.month}

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Đã tạo các bảng SQLite.")

    return app
