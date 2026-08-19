from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Budget, Transaction
from ..schemas import (
    BudgetCreate,
    BudgetResponse,
    BudgetStatusResponse,
)


router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"],
)


# =========================
# DATABASE DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================
# CREATE BUDGET
# =========================

@router.post(
    "/",
    response_model=BudgetResponse,
)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
):
    new_budget = Budget(
        category=budget.category,
        amount=budget.amount,
        month=budget.month,
        year=budget.year,
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget


# =========================
# GET ALL BUDGETS
# =========================

@router.get(
    "/",
    response_model=list[BudgetResponse],
)
def get_budgets(
    month: int | None = None,
    year: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Budget)

    if month is not None:
        query = query.filter(
            Budget.month == month
        )

    if year is not None:
        query = query.filter(
            Budget.year == year
        )

    return query.all()


# =========================
# GET ONE BUDGET
# =========================

@router.get(
    "/{budget_id}",
    response_model=BudgetResponse,
)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
):
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id)
        .first()
    )

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found",
        )

    return budget


# =========================
# GET BUDGET STATUS
# =========================

@router.get(
    "/{budget_id}/status",
    response_model=BudgetStatusResponse,
)
def get_budget_status(
    budget_id: int,
    db: Session = Depends(get_db),
):
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id)
        .first()
    )

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found",
        )

    expenses = (
        db.query(Transaction)
        .filter(
            Transaction.category == budget.category,
            Transaction.transaction_type == "expense",
        )
        .all()
    )

    spent_amount = sum(
        transaction.amount
        for transaction in expenses
        if transaction.transaction_date.month == budget.month
        and transaction.transaction_date.year == budget.year
    )

    remaining_amount = (
        budget.amount - spent_amount
    )

    if budget.amount > 0:
        percentage_used = (
            spent_amount / budget.amount
        ) * 100
    else:
        percentage_used = 0

    return {
        "id": budget.id,
        "category": budget.category,
        "budget_amount": budget.amount,
        "spent_amount": spent_amount,
        "remaining_amount": remaining_amount,
        "percentage_used": round(
            percentage_used,
            2,
        ),
        "month": budget.month,
        "year": budget.year,
    }


# =========================
# UPDATE BUDGET
# =========================

@router.put(
    "/{budget_id}",
    response_model=BudgetResponse,
)
def update_budget(
    budget_id: int,
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
):
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id)
        .first()
    )

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found",
        )

    budget.category = budget_data.category
    budget.amount = budget_data.amount
    budget.month = budget_data.month
    budget.year = budget_data.year

    db.commit()
    db.refresh(budget)

    return budget


# =========================
# DELETE BUDGET
# =========================

@router.delete(
    "/{budget_id}"
)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
):
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id)
        .first()
    )

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Budget not found",
        )

    db.delete(budget)
    db.commit()

    return {
        "message": "Budget deleted successfully"
    }