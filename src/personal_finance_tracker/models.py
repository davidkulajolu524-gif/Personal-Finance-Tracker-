from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, Integer, String

from .database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    amount = Column(
        Float,
        nullable=False
    )

    transaction_type = Column(
        String(20),
        nullable=False
    )

    category = Column(
        String(50),
        nullable=False
    )

    description = Column(
        String(255),
        nullable=True
    )

    transaction_date = Column(
        Date,
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    category = Column(
        String(50),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    month = Column(
        Integer,
        nullable=False
    )

    year = Column(
        Integer,
        nullable=False
    )