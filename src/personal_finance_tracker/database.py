import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./finance.db",
)


class Base(DeclarativeBase):
    pass


if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
        },
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def create_tables():
    Base.metadata.create_all(bind=engine)