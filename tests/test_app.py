from datetime import date
from decimal import Decimal

import pytest
from app import create_app
from app.extensions import db
from app.models import Category, Role, User


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
