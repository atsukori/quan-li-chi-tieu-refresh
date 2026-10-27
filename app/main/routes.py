from datetime import date
from decimal import Decimal
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from ..extensions import db
from ..models import Expense, User
from ..utils import budget_progress, period_contains_today, total_amount, visible_budgets, visible_expense_query


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    today = date.today()
    month_start = date(today.year, today.month, 1)
    month_end = date(today.year + (today.month == 12), 1 if today.month == 12 else today.month + 1, 1)
    month_expenses_query = visible_expense_query().filter(Expense.date >= month_start, Expense.date < month_end)
    month_items = month_expenses_query.order_by(Expense.date.desc()).all()
    income_total = total_amount(month_items, "income")
    expense_total = total_amount(month_items, "expense")

    recent_items = visible_expense_query().order_by(Expense.date.desc(), Expense.idExpense.desc()).limit(8).all()
    budgets = [budget for budget in visible_budgets() if period_contains_today(budget, today)]
    budget_cards = []
    for budget in budgets[:6]:
        spent, percent, exceeded = budget_progress(budget)
        budget_cards.append({"budget": budget, "spent": spent, "percent": percent, "exceeded": exceeded})

    daily_totals = {}
    for item in month_items:
        if item.category and item.category.type == "expense":
            key = item.date.isoformat()
            daily_totals[key] = daily_totals.get(key, Decimal("0")) + Decimal(str(item.amount))
    chart_labels = sorted(daily_totals.keys())
    chart_values = [float(daily_totals[label]) for label in chart_labels]

    if current_user.is_admin:
        member_count = User.query.count()
        transaction_count = Expense.query.count()
    else:
        member_count = None
        transaction_count = visible_expense_query().count()

    return render_template(
        "main/dashboard.html",
        income_total=income_total,
        expense_total=expense_total,
        balance=income_total - expense_total,
        recent_items=recent_items,
        budget_cards=budget_cards,
        chart_labels=chart_labels,
        chart_values=chart_values,
        member_count=member_count,
        transaction_count=transaction_count,
    )
