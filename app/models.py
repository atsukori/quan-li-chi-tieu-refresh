from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .extensions import db


class Role(db.Model):
    __tablename__ = "Role"

    idRole = db.Column(db.Integer, primary_key=True)
    roleName = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")

    users = db.relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role {self.roleName}>"


class User(UserMixin, db.Model):
    __tablename__ = "User"

    idUser = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    hoten = db.Column(db.String(120), nullable=False)
    idRole = db.Column(db.Integer, db.ForeignKey("Role.idRole"), nullable=False)
    is_active_account = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    role = db.relationship("Role", back_populates="users")
    expenses = db.relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    budgets = db.relationship("Budget", back_populates="user")

    def get_id(self):
        return str(self.idUser)

    @property
    def is_active(self):
        return self.is_active_account

    @property
    def is_admin(self):
        return bool(self.role and self.role.roleName == "admin")

    def set_password(self, plain_password):
        self.password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        return check_password_hash(self.password, plain_password)

    def __repr__(self):
        return f"<User {self.username}>"


class Category(db.Model):
    __tablename__ = "Category"
    __table_args__ = (db.UniqueConstraint("nameCategory", "type", name="uq_category_name_type"),)

    idCategory = db.Column(db.Integer, primary_key=True)
    nameCategory = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    expenses = db.relationship("Expense", back_populates="category")

    def __repr__(self):
        return f"<Category {self.nameCategory}>"


class Expense(db.Model):
    __tablename__ = "Expense"

    idExpense = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey("User.idUser"), nullable=False, index=True)
    idCategory = db.Column(db.Integer, db.ForeignKey("Category.idCategory"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    purpose = db.Column(db.String(500), nullable=False, default="")
    source = db.Column(db.String(20), nullable=False, default="personal")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="expenses")
    category = db.relationship("Category", back_populates="expenses")

    @property
    def transaction_type(self):
        return self.category.type if self.category else "expense"

    def __repr__(self):
        return f"<Expense {self.idExpense}: {self.amount}>"


class Budget(db.Model):
    __tablename__ = "Budget"

    idBudget = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey("User.idUser"), nullable=True, index=True)
    amountLimit = db.Column(db.Numeric(14, 2), nullable=False)
    month = db.Column(db.Integer, nullable=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    source = db.Column(db.String(20), nullable=False, default="personal")
    period_type = db.Column(db.String(20), nullable=False, default="monthly")
    period_number = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="budgets")

    def __repr__(self):
        return f"<Budget {self.idBudget}: {self.amountLimit}>"
