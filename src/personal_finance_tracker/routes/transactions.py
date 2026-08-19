from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Transaction
from ..schemas import TransactionCreate, TransactionUpdate


router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
):
    new_transaction = Transaction(
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        category=transaction.category,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@router.get("/")
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()

    return transactions


@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    return transaction


@router.put("/{transaction_id}")
def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db),
):
    existing_transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    if existing_transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    update_data = transaction.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(existing_transaction, field, value)

    db.commit()
    db.refresh(existing_transaction)

    return existing_transaction


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully"
    }