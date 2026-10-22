# Library Management System

Python + SQLite library system with a Streamlit frontend: book and member CRUD, issue/return with due dates, overdue tracking.

## Run locally
1. `pip install -r requirements.txt`
2. `python -m streamlit run app.py`

The `library.db` file and its tables are created automatically on first launch. Set `LMS_DB_PATH` to store the database elsewhere.

## Deploy (Streamlit Community Cloud)
Push to GitHub, then create the app on share.streamlit.io with `app.py` as the main file. The server's disk is ephemeral, so data resets whenever the app restarts; use a persistent host (VPS, Docker volume) if you need the data to last.
