import argparse
import random
from datetime import date, timedelta
from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models import Budget, Category, Expense, Role, User


CATEGORIES = [
    ("Ăn uống", "expense"),
    ("Điện nước", "expense"),
    ("Đi lại", "expense"),
    ("Học tập", "expense"),
    ("Giải trí", "expense"),
    ("Y tế", "expense"),
    ("Mua sắm", "expense"),
    ("Sinh hoạt gia đình", "expense"),
    ("Lương / trợ cấp", "income"),
    ("Thu nhập khác", "income"),
]

PURPOSES = {
    "Ăn uống": ["Đi chợ", "Ăn trưa", "Mua thực phẩm", "Đồ uống", "Bữa tối gia đình"],
    "Điện nước": ["Tiền điện", "Tiền nước", "Cước Internet", "Nạp điện thoại"],
    "Đi lại": ["Xăng xe", "Gửi xe", "Xe buýt", "Di chuyển"],
    "Học tập": ["Sách tham khảo", "Đồ dùng học tập", "Học phí", "Tài liệu học"],
    "Giải trí": ["Xem phim", "Trò chơi", "Đi chơi cuối tuần", "Đăng ký dịch vụ"],
    "Y tế": ["Thuốc", "Khám sức khỏe", "Vật dụng y tế"],
    "Mua sắm": ["Đồ dùng cá nhân", "Quần áo", "Đồ gia dụng"],
    "Sinh hoạt gia đình": ["Mua vật dụng gia đình", "Sửa chữa nhỏ", "Đóng góp quỹ chung"],
    "Lương / trợ cấp": ["Lương tháng", "Trợ cấp", "Tiền được cấp"],
    "Thu nhập khác": ["Bán đồ cũ", "Tiền thưởng", "Thu nhập làm thêm"],
}


def main():
    parser = argparse.ArgumentParser(description="Tạo dữ liệu mẫu cho Hệ thống Quản lý Chi tiêu Gia đình.")
    parser.add_argument("--reset", action="store_true", help="Xóa dữ liệu hiện tại và tạo lại toàn bộ dữ liệu mẫu.")
    parser.add_argument("--transactions", type=int, default=360, help="Số giao dịch mẫu cần tạo (mặc định: 360).")
    args = parser.parse_args()
    if args.transactions < 1 or args.transactions > 5000:
        raise SystemExit("Số giao dịch phải nằm trong khoảng 1 đến 5000.")

    app = create_app()
    with app.app_context():
        if args.reset:
            db.drop_all()
        db.create_all()
        if User.query.first() and not args.reset:
            print("Cơ sở dữ liệu đã có tài khoản. Không thay đổi dữ liệu hiện tại.")
            print("Nếu muốn xóa và tạo lại dữ liệu mẫu, chạy: python seed.py --reset")
            return

        admin_role = Role.query.filter_by(roleName="admin").first()
        member_role = Role.query.filter_by(roleName="user").first()
        if not admin_role:
            admin_role = Role(roleName="admin", description="Quản trị tài khoản, danh mục, hạn mức và báo cáo toàn gia đình.")
            db.session.add(admin_role)
        if not member_role:
            member_role = Role(roleName="user", description="Ghi nhận và theo dõi giao dịch cá nhân, giao dịch quỹ chung.")
            db.session.add(member_role)
        db.session.flush()

        accounts = [
            ("admin", "Quản trị viên", "admin12345", admin_role),
            ("member1", "Nguyễn Minh Anh", "member12345", member_role),
            ("member2", "Trần Gia Huy", "member12345", member_role),
            ("member3", "Lê Khánh Linh", "member12345", member_role),
            ("member4", "Phạm Đức Minh", "member12345", member_role),
        ]
        users = []
        for username, full_name, password, role in accounts:
            user = User(username=username, hoten=full_name, role=role, is_active_account=True)
            user.set_password(password)
            db.session.add(user)
            users.append(user)

        category_objects = {}
        for name, category_type in CATEGORIES:
            category = Category(nameCategory=name, type=category_type, is_active=True)
            db.session.add(category)
            category_objects[name] = category
        db.session.flush()

        random.seed(20261027)
        today = date.today()
        start_date = today - timedelta(days=89)
        expense_categories = [category_objects[name] for name, kind in CATEGORIES if kind == "expense"]
        income_categories = [category_objects[name] for name, kind in CATEGORIES if kind == "income"]
        for index in range(args.transactions):
            user = users[index % len(users)]
            transaction_date = start_date + timedelta(days=random.randint(0, 89))
            is_income = random.random() < 0.13
            category = random.choice(income_categories if is_income else expense_categories)
            if is_income:
                amount = random.choice([500000, 800000, 1200000, 2000000, 3500000, 5000000])
            else:
                category_name = category.nameCategory
                if category_name == "Điện nước":
                    amount = random.randint(80000, 850000)
                elif category_name in {"Học tập", "Y tế", "Mua sắm"}:
                    amount = random.randint(50000, 1600000)
                else:
                    amount = random.randint(15000, 650000)
            source = "common" if random.random() < 0.28 else "personal"
            purpose = random.choice(PURPOSES[category.nameCategory])
            db.session.add(Expense(
                user=user,
                category=category,
                date=transaction_date,
                amount=Decimal(amount).quantize(Decimal("0.01")),
                purpose=purpose,
                source=source,
            ))

        current_month = today.month
        current_year = today.year
        for user in users:
            db.session.add(Budget(
                user=user,
                amountLimit=Decimal("6500000"),
                month=current_month,
                year=current_year,
                source="personal",
                period_type="monthly",
                period_number=current_month,
            ))
        db.session.add(Budget(
            idUser=None,
            amountLimit=Decimal("12000000"),
            month=current_month,
            year=current_year,
            source="common",
            period_type="monthly",
            period_number=current_month,
        ))
        quarter = ((today.month - 1) // 3) + 1
        db.session.add(Budget(
            idUser=None,
            amountLimit=Decimal("35000000"),
            month=(quarter - 1) * 3 + 1,
            year=current_year,
            source="common",
            period_type="quarterly",
            period_number=quarter,
        ))
        iso_year, iso_week, _ = today.isocalendar()
        db.session.add(Budget(
            user=users[1],
            amountLimit=Decimal("1800000"),
            month=today.month,
            year=iso_year,
            source="personal",
            period_type="weekly",
            period_number=iso_week,
        ))
        db.session.commit()

        print("Đã khởi tạo cơ sở dữ liệu và dữ liệu mẫu thành công.")
        print(f"Số giao dịch mẫu: {args.transactions}")
        print("Tài khoản mẫu:")
        print("  Admin:   admin / admin12345")
        print("  Member:  member1 / member12345")
        print("  Member:  member2 / member12345")
        print("  Member:  member3 / member12345")
        print("  Member:  member4 / member12345")
        print("Đổi mật khẩu mẫu trước khi sử dụng với dữ liệu thật.")


if __name__ == "__main__":
    main()
