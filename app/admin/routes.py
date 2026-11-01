from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, session, url_for
from flask_login import current_user
from openpyxl.utils.exceptions import InvalidFileException
from sqlalchemy.exc import SQLAlchemyError
from zipfile import BadZipFile
from ..backups import DatabaseBackupError, create_sqlite_backup
from ..extensions import db
from ..importer import apply_staged_import, parse_expense_workbook, read_staged_import
from ..models import AuditLog, Category, Expense, Role, User
from ..utils import add_audit_log, admin_required, create_audit_free_user


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/database-backup", methods=["GET", "POST"])
@admin_required
def database_backup():
    if request.method == "POST":
        try:
            backup_path = create_sqlite_backup()
        except DatabaseBackupError as error:
            flash(str(error), "danger")
            return redirect(url_for("admin.database_backup"))
        add_audit_log("backup", "database", details={"filename": backup_path.name})
        db.session.commit()
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=backup_path.name,
            mimetype="application/vnd.sqlite3",
        )
    return render_template("admin/backup.html")


@admin_bp.route("/audit-log")
@admin_required
def audit_log():
    pagination = AuditLog.query.order_by(AuditLog.created_at.desc(), AuditLog.idAuditLog.desc()).paginate(
        page=max(request.args.get("page", 1, type=int), 1), per_page=50, error_out=False
    )
    return render_template("admin/audit_log.html", pagination=pagination)


@admin_bp.route("/import-transactions", methods=["GET", "POST"])
@admin_required
def import_transactions():
    if request.method == "POST":
        uploaded = request.files.get("file")
        if not uploaded or not uploaded.filename:
            flash("Vui lòng chọn tệp Excel .xlsx.", "danger")
            return redirect(url_for("admin.import_transactions"))
        if not uploaded.filename.lower().endswith(".xlsx"):
            flash("Chỉ hỗ trợ tệp .xlsx theo mẫu cấu trúc dữ liệu.", "danger")
            return redirect(url_for("admin.import_transactions"))
        try:
            token, records = parse_expense_workbook(uploaded.stream, current_app.instance_path, current_user.idUser)
        except (ValueError, OSError, KeyError, TypeError, InvalidFileException, BadZipFile) as error:
            flash(f"Không thể đọc tệp Excel: {error}", "danger")
            return redirect(url_for("admin.import_transactions"))
        session["expense_import_token"] = token
        return render_template("admin/import_preview.html", records=records, token=token)
    return render_template("admin/import_transactions.html")


@admin_bp.post("/import-transactions/confirm")
@admin_required
def confirm_import_transactions():
    token = session.get("expense_import_token")
    staged_path, records = read_staged_import(current_app.instance_path, token)
    if not records:
        session.pop("expense_import_token", None)
        flash("Bản xem trước đã hết hạn hoặc không còn tồn tại. Hãy chọn lại tệp.", "warning")
        return redirect(url_for("admin.import_transactions"))
    try:
        imported, duplicates, invalid = apply_staged_import(records)
        add_audit_log("import", "expense_batch", details={"imported": imported, "duplicates_skipped": duplicates, "invalid_skipped": invalid})
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash("Không thể nhập dữ liệu; bản xem trước vẫn được giữ để thử lại.", "danger")
        return redirect(url_for("admin.import_transactions"))
    session.pop("expense_import_token", None)
    staged_path.unlink(missing_ok=True)
    flash(f"Đã nhập {imported} giao dịch; bỏ qua {duplicates} dòng trùng và {invalid} dòng lỗi.", "success")
    return redirect(url_for("transactions.index"))


@admin_bp.post("/import-transactions/cancel")
@admin_required
def cancel_import_transactions():
    staged_path, _records = read_staged_import(current_app.instance_path, session.pop("expense_import_token", None))
    if staged_path:
        staged_path.unlink(missing_ok=True)
    return redirect(url_for("admin.import_transactions"))


@admin_bp.route("/users")
@admin_required
def users():
    users_list = User.query.join(Role).order_by(User.idUser.asc()).all()
    return render_template("admin/users.html", users=users_list)


@admin_bp.route("/users/new", methods=["GET", "POST"])
@admin_required
def create_user():
    roles = Role.query.order_by(Role.roleName.asc()).all()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("hoten", "").strip()
        password = request.form.get("password", "")
        role_id = request.form.get("idRole", "")
        role = db.session.get(Role, int(role_id)) if role_id.isdigit() else None
        errors = []
        if not username or len(username) > 80:
            errors.append("Tên đăng nhập là bắt buộc và tối đa 80 ký tự.")
        if any(ch.isspace() for ch in username):
            errors.append("Tên đăng nhập không được chứa khoảng trắng.")
        if User.query.filter_by(username=username).first():
            errors.append("Tên đăng nhập đã tồn tại.")
        if not full_name or len(full_name) > 120:
            errors.append("Họ và tên là bắt buộc và tối đa 120 ký tự.")
        if len(password) < 8:
            errors.append("Mật khẩu phải có ít nhất 8 ký tự.")
        if not role:
            errors.append("Vai trò không hợp lệ.")
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            user = create_audit_free_user(username, full_name, password, role)
            db.session.add(user)
            db.session.flush()
            add_audit_log("create", "user", user.idUser, {"username": username, "full_name": full_name, "role": role.roleName})
            db.session.commit()
            flash("Đã tạo tài khoản thành viên.", "success")
            return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", user=None, roles=roles)


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.order_by(Role.roleName.asc()).all()
    if request.method == "POST":
        full_name = request.form.get("hoten", "").strip()
        password = request.form.get("password", "")
        role_id = request.form.get("idRole", "")
        role = db.session.get(Role, int(role_id)) if role_id.isdigit() else None
        errors = []
        if not full_name or len(full_name) > 120:
            errors.append("Họ và tên là bắt buộc và tối đa 120 ký tự.")
        if password and len(password) < 8:
            errors.append("Mật khẩu mới phải có ít nhất 8 ký tự.")
        if not role:
            errors.append("Vai trò không hợp lệ.")
        if user.idUser == current_user.idUser and role and role.roleName != "admin":
            errors.append("Bạn không thể tự hạ quyền quản trị của chính mình.")
        active_admins = User.query.join(Role).filter(Role.roleName == "admin", User.is_active_account.is_(True)).count()
        if user.is_active_account and user.is_admin and role and role.roleName != "admin" and active_admins <= 1:
            errors.append("Không thể hạ quyền quản trị của quản trị viên đang hoạt động cuối cùng.")
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            before = {"full_name": user.hoten, "role": user.role.roleName, "active": user.is_active_account}
            user.hoten = full_name
            user.idRole = role.idRole
            if password:
                user.set_password(password)
            add_audit_log("update", "user", user.idUser, {"username": user.username, "before": before, "after": {"full_name": full_name, "role": role.roleName, "password_changed": bool(password)}})
            db.session.commit()
            flash("Đã cập nhật tài khoản.", "success")
            return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", user=user, roles=roles)


@admin_bp.post("/users/<int:user_id>/toggle")
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.idUser == current_user.idUser:
        flash("Bạn không thể khóa tài khoản đang đăng nhập.", "danger")
        return redirect(url_for("admin.users"))
    if user.is_active_account and user.is_admin:
        active_admins = User.query.join(Role).filter(Role.roleName == "admin", User.is_active_account.is_(True)).count()
        if active_admins <= 1:
            flash("Không thể khóa quản trị viên đang hoạt động cuối cùng.", "danger")
            return redirect(url_for("admin.users"))
    user.is_active_account = not user.is_active_account
    add_audit_log("activate" if user.is_active_account else "deactivate", "user", user.idUser, {"username": user.username})
    db.session.commit()
    flash("Đã mở khóa tài khoản." if user.is_active_account else "Đã khóa tài khoản.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/categories", methods=["GET", "POST"])
@admin_required
def categories():
    if request.method == "POST":
        name = request.form.get("nameCategory", "").strip()
        category_type = request.form.get("type", "")
        errors = []
        if not name or len(name) > 100:
            errors.append("Tên danh mục là bắt buộc và tối đa 100 ký tự.")
        if category_type not in {"expense", "income"}:
            errors.append("Loại danh mục không hợp lệ.")
        if Category.query.filter_by(nameCategory=name, type=category_type).first():
            errors.append("Danh mục cùng tên và loại đã tồn tại.")
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            category = Category(nameCategory=name, type=category_type, is_active=True)
            db.session.add(category)
            db.session.flush()
            add_audit_log("create", "category", category.idCategory, {"name": name, "type": category_type})
            db.session.commit()
            flash("Đã thêm danh mục.", "success")
            return redirect(url_for("admin.categories"))
    categories_list = Category.query.order_by(Category.type.asc(), Category.nameCategory.asc()).all()
    usage_rows = db.session.query(Expense.idCategory, db.func.count(Expense.idExpense)).group_by(Expense.idCategory).all()
    category_usage = dict(usage_rows)
    return render_template("admin/categories.html", categories=categories_list, category_usage=category_usage)


@admin_bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    usage_count = Expense.query.filter_by(idCategory=category.idCategory).count()
    if request.method == "POST":
        name = request.form.get("nameCategory", "").strip()
        category_type = request.form.get("type", "")
        errors = []
        if not name or len(name) > 100:
            errors.append("Tên danh mục là bắt buộc và tối đa 100 ký tự.")
        if category_type not in {"expense", "income"}:
            errors.append("Loại danh mục không hợp lệ.")
        duplicate = Category.query.filter_by(nameCategory=name, type=category_type).filter(
            Category.idCategory != category.idCategory
        ).first()
        if duplicate:
            errors.append("Danh mục cùng tên và loại đã tồn tại.")
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            before = {"name": category.nameCategory, "type": category.type}
            category.nameCategory = name
            category.type = category_type
            add_audit_log("update", "category", category.idCategory, {
                "before": before,
                "after": {"name": name, "type": category_type},
                "linked_transactions": usage_count,
            })
            db.session.commit()
            flash("Đã cập nhật danh mục.", "success")
            return redirect(url_for("admin.categories"))
    return render_template("admin/category_form.html", category=category, usage_count=usage_count)


@admin_bp.post("/categories/<int:category_id>/delete")
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    usage_count = Expense.query.filter_by(idCategory=category.idCategory).count()
    if usage_count:
        flash(f"Không thể xóa danh mục đang được dùng trong {usage_count} giao dịch. Hãy sửa tên hoặc ẩn danh mục để giữ nguyên lịch sử.", "warning")
        return redirect(url_for("admin.categories"))
    details = {"name": category.nameCategory, "type": category.type}
    add_audit_log("delete", "category", category.idCategory, details)
    db.session.delete(category)
    db.session.commit()
    flash("Đã xóa danh mục.", "success")
    return redirect(url_for("admin.categories"))


@admin_bp.post("/categories/<int:category_id>/toggle")
@admin_required
def toggle_category(category_id):
    category = Category.query.get_or_404(category_id)
    category.is_active = not category.is_active
    add_audit_log("activate" if category.is_active else "deactivate", "category", category.idCategory, {"name": category.nameCategory, "type": category.type})
    db.session.commit()
    flash("Đã kích hoạt danh mục." if category.is_active else "Đã ẩn danh mục.", "success")
    return redirect(url_for("admin.categories"))
