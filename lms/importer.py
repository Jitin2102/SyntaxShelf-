from io import BytesIO

import pandas as pd

COLUMNS = ["Title", "Author", "ISBN", "Copies"]
REQUIRED = ["title", "author", "isbn"]


def template() -> bytes:
    sample = pd.DataFrame(
        [["Dune", "Frank Herbert", "9780441013593", 2]], columns=COLUMNS
    )
    buffer = BytesIO()
    sample.to_excel(buffer, index=False)
    return buffer.getvalue()


def _copies(value: str) -> int:
    try:
        return max(1, int(float(value)))
    except ValueError:
        return 1


def read_books(file) -> tuple[list[dict], int]:
    frame = pd.read_excel(file, dtype=str).fillna("")
    frame.columns = [str(name).strip().lower() for name in frame.columns]
    missing = [name for name in REQUIRED if name not in frame.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    rows, invalid = [], 0
    for record in frame.to_dict("records"):
        title, author, isbn = (record[name].strip() for name in REQUIRED)
        if not (title and author and isbn):
            invalid += 1
            continue
        rows.append(
            {
                "title": title,
                "author": author,
                "isbn": isbn,
                "copies": _copies(record.get("copies", "")),
            }
        )
    return rows, invalid
