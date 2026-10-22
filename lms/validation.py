def require(**fields) -> None:
    missing = [name for name, value in fields.items() if not str(value).strip()]
    if missing:
        raise ValueError(f"Required: {', '.join(missing)}")
