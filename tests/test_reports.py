import os
import tempfile
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from personal_finance_tracker.database import Base
from personal_finance_tracker.main import app
from personal_finance_tracker.routes.reports import get_db
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

    # Reports use the test database.
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
# YEARLY REPORT
# =========================

def test_yearly_report(client):
    today = date.today()

    income_response = client.post(
        "/transactions/",
        json={
            "amount": 30000,
            "transaction_type": "income",
            "category": "Salary",
            "description": "Monthly salary",
            "transaction_date": str(
                today
            ),
        },
    )

    assert income_response.status_code == 200

    expense_response = client.post(
        "/transactions/",
        json={
            "amount": 8000,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Food expenses",
            "transaction_date": str(
                today
            ),
        },
    )

    assert expense_response.status_code == 200

    response = client.get(
        f"/reports/?year={today.year}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["year"] == today.year
    assert data["month"] is None
    assert data["total_income"] == 30000
    assert data["total_expenses"] == 8000
    assert data["balance"] == 22000


# =========================
# MONTHLY REPORT
# =========================

def test_monthly_report(client):
    today = date.today()

    income_response = client.post(
        "/transactions/",
        json={
            "amount": 20000,
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
            "amount": 5000,
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
        f"/reports/?year={today.year}"
        f"&month={today.month}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["year"] == today.year
    assert data["month"] == today.month
    assert data["total_income"] == 20000
    assert data["total_expenses"] == 5000
    assert data["balance"] == 15000


# =========================
# REPORT OVERVIEW
# =========================

def test_report_overview(client):
    today = date.today()

    income_response = client.post(
        "/transactions/",
        json={
            "amount": 25000,
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
            "amount": 7000,
            "transaction_type": "expense",
            "category": "Transport",
            "description": "Fuel",
            "transaction_date": str(
                today
            ),
        },
    )

    assert expense_response.status_code == 200

    response = client.get(
        f"/reports/overview?"
        f"month={today.month}"
        f"&year={today.year}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["month"] == today.month
    assert data["year"] == today.year
    assert data["total_income"] == 25000
    assert data["total_expenses"] == 7000
    assert data["balance"] == 18000


# =========================
# CATEGORY REPORT
# =========================

def test_category_report(client):
    today = date.today()

    food_response = client.post(
        "/transactions/",
        json={
            "amount": 3000,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Groceries",
            "transaction_date": str(
                today
            ),
        },
    )

    assert food_response.status_code == 200

    transport_response = client.post(
        "/transactions/",
        json={
            "amount": 7000,
            "transaction_type": "expense",
            "category": "Transport",
            "description": "Fuel",
            "transaction_date": str(
                today
            ),
        },
    )

    assert transport_response.status_code == 200

    second_food_response = client.post(
        "/transactions/",
        json={
            "amount": 2000,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Restaurant",
            "transaction_date": str(
                today
            ),
        },
    )

    assert second_food_response.status_code == 200

    response = client.get(
        f"/reports/categories?"
        f"month={today.month}"
        f"&year={today.year}"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert data[0]["category"] == "Transport"
    assert data[0]["amount"] == 7000

    assert data[1]["category"] == "Food"
    assert data[1]["amount"] == 5000

