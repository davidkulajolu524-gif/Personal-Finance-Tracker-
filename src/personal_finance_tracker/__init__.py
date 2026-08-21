import uvicorn


def main() -> None:
    uvicorn.run(
        "personal_finance_tracker.main:app",
        host="127.0.0.1",
        port=8000,
    )
