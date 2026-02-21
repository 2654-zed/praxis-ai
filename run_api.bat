@echo off
:: Run the FastAPI app using uvicorn on Windows
python -m uvicorn praxis.api:app --reload --port 8000
