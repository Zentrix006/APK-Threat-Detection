"""Null-safe helpers for analysis payloads."""

from typing import Any, Dict, List


def safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def safe_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def safe_str_list(value: Any) -> List[str]:
    return [clean_str(str(x)) for x in safe_list(value) if x is not None]


def clean_str(value: Any, max_len: int | None = None) -> str:
    """Remove NUL bytes PostgreSQL rejects in text/JSON string values."""
    if value is None:
        return ""
    text = str(value).replace("\x00", "")
    if max_len is not None:
        return text[:max_len]
    return text


def sanitize_for_db(value: Any) -> Any:
    """Recursively strip NUL characters from strings in nested structures."""
    if isinstance(value, str):
        return clean_str(value)
    if isinstance(value, dict):
        return {sanitize_for_db(k): sanitize_for_db(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_for_db(v) for v in value]
    return value
