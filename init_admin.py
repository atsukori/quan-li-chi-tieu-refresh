import argparse
import os
import sys

from app import create_app
from app.extensions import db
from app.models import Budget, Category, Expense, Role, User


def parse_args():
    parser = argparse.ArgumentParser(
        description="Khởi tạo CSDL sạch với duy nhất một tài khoản quản trị viên."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="XÓA toàn bộ dữ liệu hiện có rồi tạo lại CSDL chỉ có tài khoản admin.",
    )
    parser.add_argument(
        "--username",
        default=os.getenv("INITIAL_ADMIN_USERNAME", "admin"),
        help="Tên đăng nhập admin (mặc định: admin).",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("INITIAL_ADMIN_PASSWORD", "admin12345"),
        help="Mật khẩu admin (mặc định dùng cho test: admin12345).",
    )
    parser.add_argument(
        "--name",
        default=os.getenv("INITIAL_ADMIN_NAME", "Quản trị viên"),
        help="Họ tên admin (mặc định: Quản trị viên).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    username = args.username.strip()
    full_name = args.name.strip()
    password = args.password

    if not username or len(username) > 80 or any(ch.isspace() for ch in username):
        raise SystemExit("Tên đăng nhập không hợp lệ: không được rỗng, tối đa 80 ký tự và không chứa khoảng trắng.")
    if not full_name or len(full_name) > 120:
        raise SystemExit("Họ tên không hợp lệ: không được rỗng và tối đa 120 ký tự.")
    if len(password) < 8:
        raise SystemExit("Mật khẩu phải có ít nhất 8 ký tự.")

    app = create_app()
    with app.app_context():
        if args.reset:
            print("CẢNH BÁO: Đang xóa toàn bộ bảng và dữ liệu trong cơ sở dữ liệu hiện tại...")
            db.drop_all()

        db.create_all()

        existing_users = User.query.count()
        existing_categories = Category.query.count()
        existing_expenses = Expense.query.count()
        existing_budgets = Budget.query.count()

        if not args.reset and any(
            (existing_users, existing_categories, existing_expenses, existing_budgets)
        ):
            admin = User.query.filter_by(username=username).first()
            is_already_initialized = (
                existing_users == 1
                and existing_categories == 0
                and existing_expenses == 0
                and existing_budgets == 0
                and admin is not None
                and admin.is_admin
            )
            if is_already_initialized:
                print("CSDL đã được khởi tạo ở chế độ admin-only; không thay đổi dữ liệu.")
                print(f"Tài khoản quản trị: {admin.username}")
                print("Danh mục: 0 | Giao dịch: 0 | Hạn mức: 0")
                return

            print("Không thực hiện thay đổi vì CSDL hiện tại đã có dữ liệu.", file=sys.stderr)
            print("Để giữ nguyên dữ liệu, hãy dừng tại đây.", file=sys.stderr)
            print("Nếu bạn thật sự muốn xóa toàn bộ dữ liệu và khởi tạo lại, chạy:", file=sys.stderr)
            print("  python init_admin.py --reset", file=sys.stderr)
            raise SystemExit(1)

        admin_role = Role.query.filter_by(roleName="admin").first()
        if admin_role is None:
            admin_role = Role(
                roleName="admin",
                description="Quản trị tài khoản, danh mục, hạn mức và báo cáo toàn gia đình.",
            )
            db.session.add(admin_role)

        member_role = Role.query.filter_by(roleName="user").first()
        if member_role is None:
            member_role = Role(
                roleName="user",
                description="Ghi nhận và theo dõi giao dịch cá nhân, giao dịch quỹ chung.",
            )
            db.session.add(member_role)

        db.session.flush()

        admin = User(
            username=username,
            hoten=full_name,
            role=admin_role,
            is_active_account=True,
        )
        admin.set_password(password)
        db.session.add(admin)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        print("Đã khởi tạo CSDL sạch thành công.")
        print(f"Tên đăng nhập: {username}")
        print(f"Mật khẩu: {password}")
        print("Vai trò: admin")
        print("Tài khoản người dùng: 1 (chỉ admin)")
        print("Danh mục: 0 | Giao dịch: 0 | Hạn mức: 0")
        if password == "admin12345":
            print("Lưu ý: admin12345 là mật khẩu dùng để test; hãy đổi mật khẩu trước khi dùng dữ liệu thật.")


if __name__ == "__main__":
    main()
