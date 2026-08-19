from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes.reports import router as reports_router

import os

from .database import create_tables

from .routes.transactions import (
    router as transaction_router
)

from .routes.summary import (
    router as summary_router
)

from .routes.budgets import (
    router as budget_router
)


# =========================
# CREATE APPLICATION
# =========================

app = FastAPI(
    title="Personal Finance Tracker"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================
# CREATE DATABASE TABLES
# =========================

create_tables()


# =========================
# API ROUTES
# =========================

app.include_router(
    transaction_router
)

app.include_router(
    summary_router
)

app.include_router(
    budget_router
)

app.include_router(
    reports_router
)


# =========================
# FRONTEND
# =========================

frontend_path = os.path.join(
    os.path.dirname(__file__),
    "../../frontend"
)


if os.path.exists(frontend_path):

    app.mount(
        "/",
        StaticFiles(
            directory=frontend_path,
            html=True
        ),
        name="frontend"
    )


# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {
        "message":
            "Personal Finance Tracker API is running"
    }