import os
import tempfile
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from personal_finance_tracker.main import app
from personal_finance_tracker.database import Base
from personal_finance_tracker.routes.transactions import get_db


# Create a temporary database specifically for tests.
fd, test_database_path = tempfile.mkstemp(
    suffix=".db"
)
os.close(fd)

TEST_DATABASE_URL = f"sqlite:///{test_database_path}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


# Use the test database instead of the real finance.db.
app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=test_engine)

client = TestClient(app)


def test_create_transaction():
    response = client.post(
        "/transactions/",
        json={
            "amount": 5000,
            "transaction_type": "income",
            "category": "Salary",
            "description": "Monthly salary",
            "transaction_date": str(date.today()),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == 5000
    assert data["transaction_type"] == "income"
    assert data["category"] == "Salary"


def test_get_transactions():
    response = client.get("/transactions/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
def test_get_single_transaction():
    create_response = client.post(
        "/transactions/",
        json={
            "amount": 2500,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Lunch",
            "transaction_date": str(date.today()),
        },
    )

    assert create_response.status_code == 200

    transaction_id = create_response.json()["id"]

    response = client.get(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == transaction_id
    assert data["amount"] == 2500
    assert data["transaction_type"] == "expense"
    assert data["category"] == "Food"


def test_update_transaction():
    create_response = client.post(
        "/transactions/",
        json={
            "amount": 1000,
            "transaction_type": "expense",
            "category": "Transport",
            "description": "Bus fare",
            "transaction_date": str(date.today()),
        },
    )

    assert create_response.status_code == 200

    transaction_id = create_response.json()["id"]

    update_response = client.put(
        f"/transactions/{transaction_id}",
        json={
            "amount": 1500,
            "category": "Transportation",
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["id"] == transaction_id
    assert data["amount"] == 1500
    assert data["category"] == "Transportation"


def test_delete_transaction():
    create_response = client.post(
        "/transactions/",
        json={
            "amount": 750,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Snack",
            "transaction_date": str(date.today()),
        },
    )

    assert create_response.status_code == 200

    transaction_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/transactions/{transaction_id}"
    )

    assert delete_response.status_code == 200

    data = delete_response.json()

    assert data["message"] == "Transaction deleted successfully"

    get_response = client.get(
        f"/transactions/{transaction_id}"
    )

    assert get_response.status_code == 404


def test_get_nonexistent_transaction():
    response = client.get(
        "/transactions/999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Transaction not found"
