# Personal Finance Tracker

A full-stack personal finance tracking application built with **Python, FastAPI, SQLAlchemy, SQLite, HTML, CSS, and JavaScript**.

The application allows users to record income and expenses, monitor their financial summary, organize spending by category, create budgets, and view financial reports through a browser-based dashboard.

## Features

* Add financial transactions
* View transactions
* Edit existing transactions
* Delete transactions
* Separate income and expenses
* Categorize transactions
* Add transaction descriptions
* Track transaction dates
* View total income
* View total expenses
* View current balance
* View spending by category
* View recent transactions
* Create budgets
* Update budgets
* Delete budgets
* Monitor budget spending
* View remaining budget amounts
* View budget usage percentages
* View monthly financial summaries
* View yearly financial reports
* View category-based reports
* SQLite database for persistent storage
* Browser-based dashboard
* FastAPI REST API

## Technologies

### Backend

* Python 3.12+
* FastAPI
* Uvicorn
* SQLAlchemy
* SQLite
* Pydantic

### Frontend

* HTML5
* CSS3
* JavaScript
* Fetch API

### Development Tools

* Git
* GitHub
* uv
* pytest
* Visual Studio Code
* Ubuntu/WSL

## Project Structure

```text
personal-finance-tracker/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── src/
│   └── personal_finance_tracker/
│       ├── __init__.py
│       ├── database.py
│       ├── init_db.py
│       ├── main.py
│       ├── models.py
│       ├── schemas.py
│       │
│       └── routes/
│           ├── __init__.py
│           ├── budgets.py
│           ├── reports.py
│           ├── summary.py
│           └── transactions.py
│
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

## Database

The application uses SQLite for local data storage.

The database contains the application's financial information, including transactions and budgets.

Local database files are excluded from Git using `.gitignore` so personal financial data is not accidentally committed to the repository.

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd personal-finance-tracker
```

### 2. Install dependencies

This project uses `uv`.

```bash
uv sync
```

### 3. Start the application

```bash
uv run uvicorn personal_finance_tracker.main:app --reload
```

The application will start on:

```text
http://127.0.0.1:8000
```

### 4. Open the dashboard

Open the following address in your browser:

```text
http://127.0.0.1:8000/
```

Do not open `frontend/index.html` directly with `file://`.

The FastAPI application serves the frontend and provides the API used by the dashboard.

## API

The backend provides endpoints for several parts of the application.

### Transactions

Transactions support:

* Creating transactions
* Listing transactions
* Retrieving individual transactions
* Updating transactions
* Deleting transactions

Base endpoint:

```text
/transactions/
```

### Budgets

Budgets support:

* Creating budgets
* Listing budgets
* Updating budgets
* Deleting budgets
* Checking budget status

Base endpoint:

```text
/budgets/
```

### Summary

The summary API provides:

* Overall financial summary
* Spending by category
* Monthly financial summaries

### Reports

The reports API provides financial reporting functionality, including monthly, yearly, and category-based reports.

## Running Tests

The project uses pytest for testing.

Run the test suite with:

```bash
uv run pytest
```

For a shorter output:

```bash
uv run pytest -q
```

## Development

Start the development server with:

```bash
uv run uvicorn personal_finance_tracker.main:app --reload
```

The `--reload` option automatically restarts the development server when backend files change.

Press:

```text
Ctrl+C
```

to stop the server.

## Currency

The dashboard displays monetary values using the Nigerian Naira (NGN).

The frontend formats currency using the `en-NG` locale.

## Git

The project uses Git for version control.

Generated files and local development files such as virtual environments, Python cache files, pytest cache files, and local database files are excluded through `.gitignore`.

## Current Status

The application currently has a working frontend, FastAPI backend, SQLite database, transaction management, budget management, financial summaries, and reporting functionality.

## License

This project currently does not specify a license.
