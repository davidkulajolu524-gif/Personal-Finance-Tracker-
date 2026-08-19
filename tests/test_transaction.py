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
