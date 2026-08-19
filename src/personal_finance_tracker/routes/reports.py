from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Transaction


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_report(
    year: int,
    month: int | None = None,
    db: Session = Depends(get_db),
):
    if month is None:
        start_date = date(year, 1, 1)
        end_date = date(year + 1, 1, 1)
    else:
        start_date = date(year, month, 1)

        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

    income = (
        db.query(
            func.coalesce(
                func.sum(Transaction.amount),
                0,
            )
        )
        .filter(
            Transaction.transaction_type == "income",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
        )
        .scalar()
    )

    expenses = (
        db.query(
            func.coalesce(
                func.sum(Transaction.amount),
                0,
            )
        )
        .filter(
            Transaction.transaction_type == "expense",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
        )
        .scalar()
    )

    return {
        "year": year,
        "month": month,
        "total_income": income,
        "total_expenses": expenses,
        "balance": income - expenses,
    }


@router.get("/overview")
def get_report_overview(
    month: int,
    year: int,
    db: Session = Depends(get_db),
):
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    income = (
        db.query(
            func.coalesce(
                func.sum(Transaction.amount),
                0,
            )
        )
        .filter(
            Transaction.transaction_type == "income",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
        )
        .scalar()
    )

    expenses = (
        db.query(
            func.coalesce(
                func.sum(Transaction.amount),
                0,
            )
        )
        .filter(
            Transaction.transaction_type == "expense",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
        )
        .scalar()
    )

    balance = income - expenses

    return {
        "month": month,
        "year": year,
        "total_income": income,
        "total_expenses": expenses,
        "balance": balance,
    }


@router.get("/categories")
def get_category_report(
    month: int,
    year: int,
    db: Session = Depends(get_db),
):
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    results = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("amount"),
        )
        .filter(
            Transaction.transaction_type == "expense",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
        )
        .group_by(Transaction.category)
        .order_by(
            func.sum(Transaction.amount).desc()
        )
        .all()
    )

    return [
        {
            "category": category,
            "amount": amount,
        }
        for category, amount in results
    ]