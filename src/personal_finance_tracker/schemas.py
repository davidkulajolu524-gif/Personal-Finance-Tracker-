from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# =========================
# TRANSACTION TYPES
# =========================

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# =========================
# TRANSACTION SCHEMAS
# =========================

class TransactionCreate(BaseModel):
    amount: float = Field(gt=0)
    transaction_type: TransactionType
    category: str = Field(min_length=1)
    description: str | None = None
    transaction_date: date


class TransactionUpdate(BaseModel):
    amount: float | None = Field(
        default=None,
        gt=0
    )

    transaction_type: TransactionType | None = None

    category: str | None = Field(
        default=None,
        min_length=1
    )

    description: str | None = None

    transaction_date: date | None = None


# =========================
# BUDGET SCHEMAS
# =========================

class BudgetCreate(BaseModel):
    category: str
    amount: float
    month: int
    year: int


class BudgetResponse(BaseModel):
    id: int
    category: str
    amount: float
    month: int
    year: int

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================
# BUDGET STATUS
# =========================

class BudgetStatusResponse(BaseModel):
    id: int
    category: str

    budget_amount: float
    spent_amount: float
    remaining_amount: float
    percentage_used: float

    month: int
    year: int

