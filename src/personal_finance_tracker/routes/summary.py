from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Transaction


router = APIRouter(
    prefix="/summary",
    tags=["summary"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_summary(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()

    total_income = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "income"
    )

    total_expenses = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "expense"
    )

    balance = total_income - total_expenses

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
    }


@router.get("/categories")
def get_category_spending(db: Session = Depends(get_db)):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.transaction_type == "expense")
        .all()
    )

    spending = {}

    for transaction in transactions:
        category = transaction.category

        if category not in spending:
            spending[category] = 0

        spending[category] += transaction.amount

    return spending


@router.get("/monthly/{year}/{month}")
def get_monthly_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.transaction_date >= date(year, month, 1)
        )
        .filter(
            Transaction.transaction_date < (
                date(year + (month == 12), (month % 12) + 1, 1)
            )
        )
        .all()
    )

    total_income = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "income"
    )

    total_expenses = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "expense"
    )

    balance = total_income - total_expenses

    return {
        "year": year,
        "month": month,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
    }