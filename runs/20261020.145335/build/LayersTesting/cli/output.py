"""CSV and diagnostic text rendering. Field values are written exactly as given; nothing is quoted, escaped, or padded."""

from __future__ import annotations


def render_csv(header: list[str], rows: list[list[str]]) -> str:
    """Return the header line followed by one line per row, each terminated by ``\\n``."""
    lines = [header, *rows]
    return "".join(",".join(fields) + "\n" for fields in lines)


def render_diagnostic(message: str) -> str:
    """Return ``message`` followed by a single ``\\n``. The caller writes it to standard error."""
    return message + "\n"
