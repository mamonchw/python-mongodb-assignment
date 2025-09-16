# FastAPI + MongoDB Assessment

## Requirements
- Python 3.9+
- MongoDB running locally (default `mongodb://localhost:27017`)

## Install
1. Create venv:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # mac/linux
   ```

2. Install packages:
   ```bash
   pip install -r requirements.txt
   ```

## Run MongoDB (local)
- On mac/linux if using `brew`:
  ```bash
  brew services start mongodb-community@7.0
  ```

## Run app
```bash
uvicorn main:app --reload --port 8000
```

API docs:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
