from datetime import date


def today_iso() -> str:
    """Return today's date in ISO format (YYYY-MM-DD)."""
    return date.today().isoformat()


def greet(name: str) -> str:
    """Return a friendly greeting for a provided name."""
    cleaned = name.strip() or "friend"
    return f"Hello, {cleaned}!"
