from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from ..extensions import db
from ..models import Category, Role, User
from ..utils import admin_required, create_audit_free_user


admin_bp = Blueprint("admin", __name__)


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
            user.hoten = full_name
            user.idRole = role.idRole
            if password:
                user.set_password(password)
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
            db.session.add(Category(nameCategory=name, type=category_type, is_active=True))
            db.session.commit()
            flash("Đã thêm danh mục.", "success")
            return redirect(url_for("admin.categories"))
    categories_list = Category.query.order_by(Category.type.asc(), Category.nameCategory.asc()).all()
    return render_template("admin/categories.html", categories=categories_list)


@admin_bp.post("/categories/<int:category_id>/toggle")
@admin_required
def toggle_category(category_id):
    category = Category.query.get_or_404(category_id)
    category.is_active = not category.is_active
    db.session.commit()
    flash("Đã kích hoạt danh mục." if category.is_active else "Đã ẩn danh mục.", "success")
    return redirect(url_for("admin.categories"))
