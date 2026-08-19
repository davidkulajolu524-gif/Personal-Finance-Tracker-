import os
import tempfile
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from personal_finance_tracker.database import Base
from personal_finance_tracker.main import app
from personal_finance_tracker.routes.budgets import get_db
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

    app.dependency_overrides[
        get_db
    ] = override_get_db

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
# CREATE BUDGET
# =========================

def test_create_budget(client):
    response = client.post(
        "/budgets/",
        json={
            "category": "Food",
            "amount": 10000,
            "month": date.today().month,
            "year": date.today().year,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "Food"
    assert data["amount"] == 10000
    assert data["month"] == date.today().month
    assert data["year"] == date.today().year


# =========================
# GET ALL BUDGETS
# =========================

def test_get_budgets(client):
    response = client.get(
        "/budgets/"
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


# =========================
# GET ONE BUDGET
# =========================

def test_get_single_budget(client):
    create_response = client.post(
        "/budgets/",
        json={
            "category": "Transport",
            "amount": 15000,
            "month": date.today().month,
            "year": date.today().year,
        },
    )

    assert create_response.status_code == 200

    budget_id = (
        create_response.json()["id"]
    )

    response = client.get(
        f"/budgets/{budget_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == budget_id
    assert data["category"] == "Transport"
    assert data["amount"] == 15000


# =========================
# UPDATE BUDGET
# =========================

def test_update_budget(client):
    create_response = client.post(
        "/budgets/",
        json={
            "category": "Food",
            "amount": 10000,
            "month": date.today().month,
            "year": date.today().year,
        },
    )

    assert create_response.status_code == 200

    budget_id = (
        create_response.json()["id"]
    )

    update_response = client.put(
        f"/budgets/{budget_id}",
        json={
            "category": "Groceries",
            "amount": 20000,
            "month": date.today().month,
            "year": date.today().year,
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["id"] == budget_id
    assert data["category"] == "Groceries"
    assert data["amount"] == 20000


# =========================
# DELETE BUDGET
# =========================

def test_delete_budget(client):
    create_response = client.post(
        "/budgets/",
        json={
            "category": "Entertainment",
            "amount": 5000,
            "month": date.today().month,
            "year": date.today().year,
        },
    )

    assert create_response.status_code == 200

    budget_id = (
        create_response.json()["id"]
    )

    delete_response = client.delete(
        f"/budgets/{budget_id}"
    )

    assert delete_response.status_code == 200

    data = delete_response.json()

    assert (
        data["message"]
        == "Budget deleted successfully"
    )

    get_response = client.get(
        f"/budgets/{budget_id}"
    )

    assert get_response.status_code == 404


# =========================
# BUDGET STATUS
# =========================

def test_budget_status(client):
    budget_response = client.post(
        "/budgets/",
        json={
            "category": "Food",
            "amount": 10000,
            "month": date.today().month,
            "year": date.today().year,
        },
    )

    assert budget_response.status_code == 200

    budget_id = (
        budget_response.json()["id"]
    )

    transaction_response = client.post(
        "/transactions/",
        json={
            "amount": 2500,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Lunch",
            "transaction_date": str(
                date.today()
            ),
        },
    )

    assert transaction_response.status_code == 200

    response = client.get(
        f"/budgets/{budget_id}/status"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["budget_amount"] == 10000
    assert data["spent_amount"] == 2500
    assert data["remaining_amount"] == 7500
    assert data["percentage_used"] == 25.0


# =========================
# NONEXISTENT BUDGET
# =========================

def test_get_nonexistent_budget(client):
    response = client.get(
        "/budgets/999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert (
        data["detail"]
        == "Budget not found"
    )
