import csv
from datetime import date
from decimal import Decimal
from io import BytesIO, StringIO
from flask import Blueprint, Response, flash, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from ..models import Category, Expense, User
from ..utils import parse_iso_date, period_range, total_amount, visible_expense_query


reports_bp = Blueprint("reports", __name__)


def _report_data():
    mode = request.args.get("mode", "month")
    if mode not in {"day", "week", "month", "year", "custom"}:
        mode = "month"
    start_arg = parse_iso_date(request.args.get("start", ""))
    end_arg = parse_iso_date(request.args.get("end", ""))
    if mode == "custom" and request.args.get("start") and not start_arg:
        flash("Ngày bắt đầu không hợp lệ.", "warning")
    if mode == "custom" and request.args.get("end") and not end_arg:
        flash("Ngày kết thúc không hợp lệ.", "warning")
    start, end = period_range(mode, start_arg, end_arg)
    if start > end:
        start, end = end, start
    query = visible_expense_query().filter(Expense.date >= start, Expense.date <= end)
    member_value = request.args.get("member", "")
    if current_user.is_admin and member_value.isdigit():
        query = query.filter(Expense.idUser == int(member_value))
    source = request.args.get("source", "")
    if source in {"personal", "common"}:
        query = query.filter(Expense.source == source)
    items = query.order_by(Expense.date.asc(), Expense.idExpense.asc()).all()
    income_total = total_amount(items, "income")
    expense_total = total_amount(items, "expense")

    category_totals = {}
    daily_totals = {}
    for item in items:
        key = (item.category.nameCategory, item.category.type)
        category_totals[key] = category_totals.get(key, Decimal("0")) + Decimal(str(item.amount))
        if item.category.type == "expense":
            daily_key = item.date.isoformat()
            daily_totals[daily_key] = daily_totals.get(daily_key, Decimal("0")) + Decimal(str(item.amount))
    category_rows = [{"name": name, "type": category_type, "amount": amount} for (name, category_type), amount in sorted(category_totals.items(), key=lambda pair: pair[1], reverse=True)]
    chart_labels = sorted(daily_totals.keys())
    chart_values = [float(daily_totals[label]) for label in chart_labels]
    members = User.query.order_by(User.hoten.asc()).all() if current_user.is_admin else []
    return {
        "mode": mode,
        "start": start,
        "end": end,
        "items": items,
        "income_total": income_total,
        "expense_total": expense_total,
        "balance": income_total - expense_total,
        "category_rows": category_rows,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
        "members": members,
        "selected_member": member_value,
        "source": source,
    }


@reports_bp.route("/")
@login_required
def index():
    return render_template("reports/index.html", report=_report_data())


@reports_bp.route("/export.xlsx")
@login_required
def export_xlsx():
    report = _report_data()
    workbook = Workbook()
    summary = workbook.active
    summary.title = "Tong quan"
    summary.append(["BÁO CÁO QUẢN LÝ CHI TIÊU TẬP THỂ / TỔ CHỨC"])
    summary.append(["Từ ngày", report["start"].strftime("%d/%m/%Y")])
    summary.append(["Đến ngày", report["end"].strftime("%d/%m/%Y")])
    summary.append(["Tổng thu (VNĐ)", float(report["income_total"])])
    summary.append(["Tổng chi (VNĐ)", float(report["expense_total"])])
    summary.append(["Chênh lệch thu - chi (VNĐ)", float(report["balance"])])
    summary["A1"].font = Font(bold=True, size=14, color="FFFFFF")
    summary["A1"].fill = PatternFill("solid", fgColor="173F5F")
    summary.merge_cells("A1:B1")
    for row in range(4, 7):
        summary.cell(row=row, column=2).number_format = '#,##0.00'
    summary.column_dimensions["A"].width = 32
    summary.column_dimensions["B"].width = 24

    sheet = workbook.create_sheet("Giao dich")
    headers = ["Mã giao dịch", "Ngày", "Thành viên", "Loại", "Danh mục", "Nguồn tiền", "Số tiền (VNĐ)", "Ghi chú"]
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="173F5F")
        cell.alignment = Alignment(horizontal="center")
    for item in report["items"]:
        sheet.append([
            item.idExpense,
            item.date.strftime("%d/%m/%Y"),
            item.user.hoten,
            "Thu nhập" if item.category.type == "income" else "Chi tiêu",
            item.category.nameCategory,
            "Quỹ chung" if item.source == "common" else "Cá nhân",
            float(item.amount),
            item.purpose,
        ])
        sheet.cell(row=sheet.max_row, column=7).number_format = '#,##0.00'
    widths = [16, 14, 24, 15, 22, 16, 20, 42]
    for index, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f"bao_cao_chi_tieu_{report['start'].isoformat()}_{report['end'].isoformat()}.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@reports_bp.route("/export.csv")
@login_required
def export_csv():
    report = _report_data()
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Mã giao dịch", "Ngày", "Thành viên", "Loại", "Danh mục", "Nguồn tiền", "Số tiền (VNĐ)", "Ghi chú"])
    for item in report["items"]:
        writer.writerow([
            item.idExpense,
            item.date.strftime("%d/%m/%Y"),
            item.user.hoten,
            "Thu nhập" if item.category.type == "income" else "Chi tiêu",
            item.category.nameCategory,
            "Quỹ chung" if item.source == "common" else "Cá nhân",
            str(item.amount),
            item.purpose,
        ])
    return Response("\ufeff" + output.getvalue(), mimetype="text/csv; charset=utf-8", headers={"Content-Disposition": f"attachment; filename=bao_cao_chi_tieu_{report['start'].isoformat()}_{report['end'].isoformat()}.csv"})
