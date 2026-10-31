from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from functools import wraps
from flask import abort, flash
from flask_login import current_user, login_required
from .extensions import db
from .models import Budget, Category, Expense, User


VALID_SOURCES = {"personal", "common"}
VALID_TYPES = {"expense", "income"}
VALID_PERIODS = {"weekly", "monthly", "quarterly"}


def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


def parse_iso_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def parse_amount(value):
    try:
        amount = Decimal(str(value).strip().replace(",", ""))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not amount.is_finite() or amount <= 0:
        return None
    if amount > Decimal("999999999999.99"):
        return None
    return amount.quantize(Decimal("0.01"))


def visible_expense_query(user=None):
    user = user or current_user
    query = Expense.query.join(Category, Expense.idCategory == Category.idCategory)
    if not user.is_admin:
        query = query.filter(db.or_(Expense.idUser == user.idUser, Expense.source == "common"))
    return query


def can_manage_expense(expense, user=None):
    user = user or current_user
    return user.is_admin or expense.idUser == user.idUser


def get_budget_period(budget):
    if budget.period_type == "weekly":
        try:
            start = date.fromisocalendar(budget.year, budget.period_number, 1)
        except ValueError:
            return None, None
        return start, start + timedelta(days=6)
    if budget.period_type == "quarterly":
        first_month = (budget.period_number - 1) * 3 + 1
        if first_month < 1 or first_month > 10:
            return None, None
        start = date(budget.year, first_month, 1)
        if first_month == 10:
            end = date(budget.year, 12, 31)
        else:
            next_quarter = date(budget.year, first_month + 3, 1)
            end = next_quarter - timedelta(days=1)
        return start, end
    if budget.month is None or budget.month < 1 or budget.month > 12:
        return None, None
    start = date(budget.year, budget.month, 1)
    if budget.month == 12:
        end = date(budget.year, 12, 31)
    else:
        end = date(budget.year, budget.month + 1, 1) - timedelta(days=1)
    return start, end


def budget_period_label(budget):
    if budget.period_type == "weekly":
        return f"Tuần {budget.period_number}, {budget.year}"
    if budget.period_type == "quarterly":
        return f"Quý {budget.period_number}/{budget.year}"
    return f"Tháng {budget.month:02d}/{budget.year}"


def budget_spent(budget):
    start, end = get_budget_period(budget)
    if not start or not end:
        return Decimal("0")
    result = db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).select_from(Expense).join(Category).filter(
        Expense.date >= start,
        Expense.date <= end,
        Expense.source == budget.source,
        Category.type == "expense",
    )
    if budget.source == "personal":
        result = result.filter(Expense.idUser == budget.idUser)
    total = result.scalar()
    return Decimal(str(total or 0))


def budget_progress(budget):
    spent = budget_spent(budget)
    limit = Decimal(str(budget.amountLimit))
    percent = float((spent / limit) * 100) if limit > 0 else 0
    return spent, min(percent, 100), percent >= 100


def visible_budgets(user=None):
    user = user or current_user
    if user.is_admin:
        return Budget.query.order_by(Budget.year.desc(), Budget.idBudget.desc()).all()
    return Budget.query.filter(
        db.or_(Budget.idUser == user.idUser, db.and_(Budget.source == "common", Budget.idUser.is_(None)))
    ).order_by(Budget.year.desc(), Budget.idBudget.desc()).all()


def period_contains_today(budget, target_date=None):
    target_date = target_date or date.today()
    start, end = get_budget_period(budget)
    return bool(start and end and start <= target_date <= end)


def applicable_budgets_for_expense(expense):
    query = Budget.query.filter(Budget.source == expense.source)
    if expense.source == "personal":
        query = query.filter(Budget.idUser == expense.idUser)
    else:
        query = query.filter(Budget.idUser.is_(None))
    return [budget for budget in query.all() if (get_budget_period(budget)[0] and get_budget_period(budget)[0] <= expense.date <= get_budget_period(budget)[1])]


def notify_budget_overruns(expense):
    warnings = []
    for budget in applicable_budgets_for_expense(expense):
        spent, _, exceeded = budget_progress(budget)
        if exceeded:
            warnings.append(f"Đã vượt hạn mức {budget_period_label(budget)} ({budget.source == 'common' and 'quỹ chung tập thể' or 'thành viên'}): {spent:,.0f} / {Decimal(str(budget.amountLimit)):,.0f} VNĐ.")
    for warning in warnings:
        flash(warning, "warning")


def active_categories(transaction_type=None):
    query = Category.query.filter_by(is_active=True)
    if transaction_type in VALID_TYPES:
        query = query.filter_by(type=transaction_type)
    return query.order_by(Category.nameCategory.asc()).all()


def period_range(mode, custom_start=None, custom_end=None, today=None):
    today = today or date.today()
    if mode == "day":
        return today, today
    if mode == "week":
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=6)
    if mode == "year":
        return date(today.year, 1, 1), date(today.year, 12, 31)
    if mode == "custom" and custom_start and custom_end and custom_start <= custom_end:
        return custom_start, custom_end
    start = date(today.year, today.month, 1)
    end = date(today.year, 12, 31) if today.month == 12 else date(today.year, today.month + 1, 1) - timedelta(days=1)
    return start, end


def total_amount(expenses, transaction_type):
    return sum((Decimal(str(item.amount)) for item in expenses if item.category and item.category.type == transaction_type), Decimal("0"))


def create_audit_free_user(username, full_name, password, role):
    user = User(username=username, hoten=full_name, role=role)
    user.set_password(password)
    return user
