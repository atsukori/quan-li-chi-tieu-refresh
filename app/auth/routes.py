from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from ..models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.is_active_account and user.check_password(password):
            login_user(user, remember=request.form.get("remember") == "on")
            next_url = request.args.get("next", "")
            if not next_url.startswith("/") or next_url.startswith("//"):
                next_url = url_for("main.dashboard")
            return redirect(next_url)
        if user and not user.is_active_account:
            flash("Tài khoản đã bị khóa. Hãy liên hệ quản trị viên.", "danger")
        else:
            flash("Tên đăng nhập hoặc mật khẩu không chính xác.", "danger")
    return render_template("auth/login.html")


@auth_bp.post("/logout")
def logout():
    logout_user()
    flash("Bạn đã đăng xuất.", "success")
    return redirect(url_for("auth.login"))
