from datetime import date
from decimal import Decimal

import pytest
from app import create_app
from app.extensions import db
from app.models import Category, Expense, Role, User
from app.utils import parse_amount


@pytest.fixture()
def app_instance():
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "test-key",
    })
    with app.app_context():
        db.create_all()
        admin_role = Role(roleName="admin", description="Admin")
        member_role = Role(roleName="user", description="Member")
        db.session.add_all([admin_role, member_role])
        db.session.flush()
        admin = User(username="admin", hoten="Admin User", role=admin_role)
        admin.set_password("password123")
        member = User(username="member", hoten="Member User", role=member_role)
        member.set_password("password123")
        db.session.add_all([admin, member, Category(nameCategory="Ăn uống", type="expense")])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app_instance):
    return app_instance.test_client()


def login(client, username, password="password123"):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


def test_login_and_dashboard(client):
    response = login(client, "member")
    assert response.status_code == 200
    assert "Tổng quan" in response.get_data(as_text=True)


def test_member_cannot_open_admin_user_management(client):
    login(client, "member")
    response = client.get("/admin/users")
    assert response.status_code == 403


def test_login_rejects_invalid_password(client):
    response = login(client, "member", "wrong-password")
    assert "không chính xác" in response.get_data(as_text=True)


def test_member_sees_own_and_common_transactions_only(client, app_instance):
    with app_instance.app_context():
        admin = User.query.filter_by(username="admin").one()
        member = User.query.filter_by(username="member").one()
        category = Category.query.filter_by(nameCategory="Ăn uống").one()
        db.session.add_all([
            Expense(idUser=admin.idUser, idCategory=category.idCategory, date=date(2026, 1, 1), amount=Decimal("100"), purpose="admin private", source="personal"),
            Expense(idUser=member.idUser, idCategory=category.idCategory, date=date(2026, 1, 2), amount=Decimal("200"), purpose="member private", source="personal"),
            Expense(idUser=admin.idUser, idCategory=category.idCategory, date=date(2026, 1, 3), amount=Decimal("300"), purpose="common transaction", source="common"),
        ])
        db.session.commit()

    login(client, "member")
    response = client.get("/transactions/")
    body = response.get_data(as_text=True)
    assert "member private" in body
    assert "common transaction" in body
    assert "admin private" not in body


def test_member_cannot_edit_another_users_transaction(client, app_instance):
    with app_instance.app_context():
        admin = User.query.filter_by(username="admin").one()
        category = Category.query.filter_by(nameCategory="Ăn uống").one()
        expense = Expense(
            idUser=admin.idUser,
            idCategory=category.idCategory,
            date=date(2026, 1, 1),
            amount=Decimal("100"),
            purpose="private transaction",
            source="personal",
        )
        db.session.add(expense)
        db.session.commit()
        expense_id = expense.idExpense

    login(client, "member")
    response = client.get(f"/transactions/{expense_id}/edit")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/transactions/")


def test_parse_amount_rejects_non_positive_and_accepts_valid_amounts():
    assert parse_amount("0") is None
    assert parse_amount("-10") is None
    assert parse_amount("1250.50") == Decimal("1250.50")
