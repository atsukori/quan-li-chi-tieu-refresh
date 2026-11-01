from datetime import date
from decimal import Decimal
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from ..extensions import db
from ..models import Budget, User
from ..utils import VALID_PERIODS, VALID_SOURCES, add_audit_log, admin_required, budget_progress, get_budget_period, visible_budgets


budgets_bp = Blueprint("budgets", __name__)


@budgets_bp.route("/")
@login_required
def index():
    budgets = visible_budgets()
    rows = []
    for budget in budgets:
        spent, percent, exceeded = budget_progress(budget)
        rows.append({"budget": budget, "spent": spent, "percent": percent, "exceeded": exceeded, "period": get_budget_period(budget)})
    return render_template("budgets/index.html", rows=rows)


@budgets_bp.route("/new", methods=["GET", "POST"])
@admin_required
def create():
    members = User.query.order_by(User.hoten.asc()).all()
    if request.method == "POST":
        result = _save_budget(None)
        if result:
            flash("Đã tạo hạn mức.", "success")
            return redirect(url_for("budgets.index"))
    return render_template("budgets/form.html", budget=None, members=members)


@budgets_bp.route("/<int:budget_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    members = User.query.order_by(User.hoten.asc()).all()
    if request.method == "POST":
        result = _save_budget(budget)
        if result:
            flash("Đã cập nhật hạn mức.", "success")
            return redirect(url_for("budgets.index"))
    return render_template("budgets/form.html", budget=budget, members=members)


@budgets_bp.post("/<int:budget_id>/delete")
@admin_required
def delete(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    add_audit_log("delete", "budget", budget.idBudget, {"source": budget.source, "user_id": budget.idUser, "amount_limit": str(budget.amountLimit), "year": budget.year, "period_type": budget.period_type, "period_number": budget.period_number})
    db.session.delete(budget)
    db.session.commit()
    flash("Đã xóa hạn mức.", "success")
    return redirect(url_for("budgets.index"))


def _save_budget(budget):
    raw_amount = request.form.get("amountLimit", "").strip().replace(",", "")
    source = request.form.get("source", "personal")
    period_type = request.form.get("period_type", "monthly")
    year_raw = request.form.get("year", "")
    period_raw = request.form.get("period_number", "")
    user_raw = request.form.get("idUser", "")
    errors = []
    try:
        amount_limit = Decimal(raw_amount)
        if not amount_limit.is_finite() or amount_limit <= 0:
            raise ValueError
        amount_limit = amount_limit.quantize(Decimal("0.01"))
    except Exception:
        amount_limit = None
        errors.append("Hạn mức phải là số tiền lớn hơn 0.")
    try:
        year = int(year_raw)
        if year < 2000 or year > 2100:
            raise ValueError
    except (TypeError, ValueError):
        year = date.today().year
        errors.append("Năm áp dụng phải nằm trong khoảng 2000–2100.")
    try:
        period_number = int(period_raw)
    except (TypeError, ValueError):
        period_number = 0
        errors.append("Kỳ áp dụng không hợp lệ.")
    valid_number = (period_type == "monthly" and 1 <= period_number <= 12) or (period_type == "quarterly" and 1 <= period_number <= 4) or (period_type == "weekly" and 1 <= period_number <= 53)
    if period_type not in VALID_PERIODS or not valid_number:
        errors.append("Kỳ áp dụng không hợp lệ với loại tuần/tháng/quý đã chọn.")
    if source not in VALID_SOURCES:
        errors.append("Nguồn ngân sách không hợp lệ.")
    user = None
    if source == "personal":
        user = db.session.get(User, int(user_raw)) if user_raw.isdigit() else None
        if not user:
            errors.append("Hạn mức dành cho thành viên phải gắn với một tài khoản thành viên.")
    month = period_number if period_type == "monthly" else (period_number - 1) * 3 + 1 if period_type == "quarterly" else None
    if period_type == "weekly":
        try:
            week_start = date.fromisocalendar(year, period_number, 1)
            month = week_start.month
        except ValueError:
            errors.append("Tuần được chọn không tồn tại trong năm này.")
    if not errors:
        duplicate_query = Budget.query.filter_by(
            idUser=user.idUser if user else None,
            source=source,
            year=year,
            period_type=period_type,
            period_number=period_number,
        )
        if budget:
            duplicate_query = duplicate_query.filter(Budget.idBudget != budget.idBudget)
        if duplicate_query.first():
            errors.append("Đã có hạn mức cho nguồn tiền và kỳ này.")
    if errors:
        for error in errors:
            flash(error, "danger")
        return False
    if budget is None:
        budget = Budget()
        db.session.add(budget)
    action = "update" if budget.idBudget else "create"
    before = None if action == "create" else {
        "source": budget.source, "user_id": budget.idUser, "amount_limit": str(budget.amountLimit),
        "year": budget.year, "period_type": budget.period_type, "period_number": budget.period_number,
    }
    budget.idUser = user.idUser if user else None
    budget.amountLimit = amount_limit
    budget.month = month
    budget.year = year
    budget.source = source
    budget.period_type = period_type
    budget.period_number = period_number
    db.session.flush()
    add_audit_log(action, "budget", budget.idBudget, {
        "before": before,
        "after": {"source": source, "user_id": budget.idUser, "amount_limit": str(amount_limit), "year": year, "period_type": period_type, "period_number": period_number},
    })
    db.session.commit()
    return budget
