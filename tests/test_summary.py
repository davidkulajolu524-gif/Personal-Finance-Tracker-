import os
import tempfile
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from personal_finance_tracker.database import Base
from personal_finance_tracker.main import app
from personal_finance_tracker.routes.summary import get_db
from personal_finance_tracker.routes.transactions import (
    get_db as transaction_get_db,
)


# =========================
# TEST DATABASE FIXTURE
# =========================

@pytest.fixture
def client():
    fd, test_database_path = tempfile.mkstemp(
        suffix=".db"
    )

    os.close(fd)

    test_database_url = (
        f"sqlite:///{test_database_path}"
    )

    test_engine = create_engine(
        test_database_url,
        connect_args={
            "check_same_thread": False
        },
    )

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db

        finally:
            db.close()

    # Summary endpoints use this database.
    app.dependency_overrides[
        get_db
    ] = override_get_db

    # Transactions created during the tests
    # must use the SAME database.
    app.dependency_overrides[
        transaction_get_db
    ] = override_get_db

    test_client = TestClient(app)

    try:
        yield test_client

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        app.dependency_overrides.pop(
            transaction_get_db,
            None,
        )

        test_engine.dispose()

        try:
            os.remove(
                test_database_path
            )
        except FileNotFoundError:
            pass


# =========================
# OVERALL SUMMARY
# =========================

def test_get_summary(client):
    income_response = client.post(
        "/transactions/",
        json={
            "amount": 10000,
            "transaction_type": "income",
            "category": "Salary",
            "description": "Monthly salary",
            "transaction_date": str(
                date.today()
            ),
        },
    )

    assert income_response.status_code == 200

    expense_response = client.post(
        "/transactions/",
        json={
            "amount": 2500,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Groceries",
            "transaction_date": str(
                date.today()
            ),
        },
    )

    assert expense_response.status_code == 200

    response = client.get(
        "/summary/"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_income"] == 10000
    assert data["total_expenses"] == 2500
    assert data["balance"] == 7500


# =========================
# CATEGORY SPENDING
# =========================

def test_category_spending(client):
    food_one = client.post(
        "/transactions/",
        json={
            "amount": 3000,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Groceries",
            "transaction_date": str(
                date.today()
            ),
        },
    )

    assert food_one.status_code == 200

    food_two = client.post(
        "/transactions/",
        json={
            "amount": 2000,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Restaurant",
            "transaction_date": str(
                date.today()
            ),
        },
    )

    assert food_two.status_code == 200

    transport = client.post(
        "/transactions/",
        json={
            "amount": 5000,
            "transaction_type": "expense",
            "category": "Transport",
            "description": "Fuel",
            "transaction_date": str(
                date.today()
            ),
        },
    )

    assert transport.status_code == 200

    response = client.get(
        "/summary/categories"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["Food"] == 5000
    assert data["Transport"] == 5000


# =========================
# MONTHLY SUMMARY
# =========================

def test_monthly_summary(client):
    today = date.today()

    income_response = client.post(
        "/transactions/",
        json={
            "amount": 15000,
            "transaction_type": "income",
            "category": "Salary",
            "description": "Salary",
            "transaction_date": str(
                today
            ),
        },
    )

    assert income_response.status_code == 200

    expense_response = client.post(
        "/transactions/",
        json={
            "amount": 4000,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Food",
            "transaction_date": str(
                today
            ),
        },
    )

    assert expense_response.status_code == 200

    response = client.get(
        f"/summary/monthly/"
        f"{today.year}/{today.month}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["year"] == today.year
    assert data["month"] == today.month
    assert data["total_income"] == 15000
    assert data["total_expenses"] == 4000
    assert data["balance"] == 11000


# =========================
# MONTHLY SUMMARY EXCLUDES
# OTHER MONTHS
# =========================

def test_monthly_summary_excludes_other_months(client):
    today = date.today()

    if today.month == 1:
        previous_year = today.year - 1
        previous_month = 12
    else:
        previous_year = today.year
        previous_month = today.month - 1

    previous_month_date = date(
        previous_year,
        previous_month,
        15,
    )

    previous_response = client.post(
        "/transactions/",
        json={
            "amount": 20000,
            "transaction_type": "income",
            "category": "Salary",
            "description": "Previous month salary",
            "transaction_date": str(
                previous_month_date
            ),
        },
    )

    assert previous_response.status_code == 200

    current_response = client.post(
        "/transactions/",
        json={
            "amount": 5000,
            "transaction_type": "income",
            "category": "Salary",
            "description": "Current month salary",
            "transaction_date": str(
                today
            ),
        },
    )

    assert current_response.status_code == 200

    response = client.get(
        f"/summary/monthly/"
        f"{today.year}/{today.month}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_income"] == 5000

