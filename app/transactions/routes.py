from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from ..extensions import db
from ..models import Category, Expense, User
from ..utils import (
    VALID_SOURCES,
    active_categories,
    can_manage_expense,
    notify_budget_overruns,
    parse_amount,
    parse_iso_date,
    visible_expense_query,
)


transactions_bp = Blueprint("transactions", __name__)


def _transaction_form_data(expense=None):
    categories = active_categories()
    if expense and expense.category and expense.category not in categories:
        categories.append(expense.category)
    return categories


def _apply_transaction_form(expense=None):
    raw_date = request.form.get("date", "").strip()
    transaction_date = parse_iso_date(raw_date)
    amount = parse_amount(request.form.get("amount", ""))
    try:
        category_id = int(request.form.get("idCategory", ""))
    except (TypeError, ValueError):
        category_id = None
    category = db.session.get(Category, category_id) if category_id else None
    source = request.form.get("source", "personal")
    purpose = request.form.get("purpose", "").strip()
    errors = []
    if not transaction_date:
        errors.append("Ngày giao dịch không hợp lệ.")
    if amount is None:
        errors.append("Số tiền phải lớn hơn 0 và nằm trong giới hạn cho phép.")
    if not category or (not category.is_active and (not expense or expense.idCategory != category.idCategory)):
        errors.append("Vui lòng chọn danh mục hợp lệ.")
    if source not in VALID_SOURCES:
        errors.append("Nguồn tiền không hợp lệ.")
    if len(purpose) > 500:
        errors.append("Ghi chú không được vượt quá 500 ký tự.")
    if errors:
        for error in errors:
            flash(error, "danger")
        return False

    if expense is None:
        expense = Expense(idUser=current_user.idUser)
        db.session.add(expense)
    expense.date = transaction_date
    expense.amount = amount
    expense.idCategory = category.idCategory
    expense.source = source
    expense.purpose = purpose
    db.session.commit()
    notify_budget_overruns(expense)
    return expense


@transactions_bp.route("/")
@login_required
def index():
    query = visible_expense_query()
    start_value = request.args.get("start", "").strip()
    end_value = request.args.get("end", "").strip()
    start = parse_iso_date(start_value)
    end = parse_iso_date(end_value)
    source = request.args.get("source", "")
    transaction_type = request.args.get("type", "")
    category_value = request.args.get("category", "")
    member_value = request.args.get("member", "")

    if start_value and not start:
        flash("Ngày bắt đầu không hợp lệ; bộ lọc ngày bắt đầu đã được bỏ qua.", "warning")
    if end_value and not end:
        flash("Ngày kết thúc không hợp lệ; bộ lọc ngày kết thúc đã được bỏ qua.", "warning")
    if start:
        query = query.filter(Expense.date >= start)
    if end:
        query = query.filter(Expense.date <= end)
    if source in VALID_SOURCES:
        query = query.filter(Expense.source == source)
    if transaction_type in {"expense", "income"}:
        query = query.filter(Category.type == transaction_type)
    if category_value.isdigit():
        query = query.filter(Expense.idCategory == int(category_value))
    if current_user.is_admin and member_value.isdigit():
        query = query.filter(Expense.idUser == int(member_value))

    items = query.order_by(Expense.date.desc(), Expense.idExpense.desc()).all()
    categories = Category.query.order_by(Category.nameCategory.asc()).all()
    members = User.query.order_by(User.hoten.asc()).all() if current_user.is_admin else []
    return render_template(
        "transactions/index.html",
        items=items,
        categories=categories,
        members=members,
        filters={"start": start_value, "end": end_value, "source": source, "type": transaction_type, "category": category_value, "member": member_value},
    )


@transactions_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        result = _apply_transaction_form()
        if result:
            flash("Đã thêm giao dịch.", "success")
            return redirect(url_for("transactions.index"))
    return render_template("transactions/form.html", expense=None, categories=_transaction_form_data())


@transactions_bp.route("/<int:expense_id>/edit", methods=["GET", "POST"])
@login_required
def edit(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if not can_manage_expense(expense):
        flash("Bạn chỉ có thể chỉnh sửa giao dịch do mình tạo.", "danger")
        return redirect(url_for("transactions.index"))
    if request.method == "POST":
        result = _apply_transaction_form(expense)
        if result:
            flash("Đã cập nhật giao dịch.", "success")
            return redirect(url_for("transactions.index"))
    return render_template("transactions/form.html", expense=expense, categories=_transaction_form_data(expense))


@transactions_bp.post("/<int:expense_id>/delete")
@login_required
def delete(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if not can_manage_expense(expense):
        flash("Bạn chỉ có thể xóa giao dịch do mình tạo.", "danger")
        return redirect(url_for("transactions.index"))
    db.session.delete(expense)
    db.session.commit()
    flash("Đã xóa giao dịch.", "success")
    return redirect(url_for("transactions.index"))
