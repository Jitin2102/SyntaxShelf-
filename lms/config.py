import os
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "library.db"
DB_PATH = Path(os.environ.get("LMS_DB_PATH", DEFAULT_DB))
