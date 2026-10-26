"""``ledger load categories <csv>``: all-or-nothing load of a categories file."""

from __future__ import annotations

from cli.errors import Rejected
from cli.loader import read_csv_rows
from cli.registry import register
from cli.validate import validate_code, validate_description


def load_categories(db, args: list[str]) -> list[list[str]]:
    """Validate every row and rule first; write only once the whole file has passed."""
    checked: list[tuple[str, str]] = []
    seen: set[str] = set()
    for code_text, description_text in read_csv_rows(args[0], ("category", "description")):
        code = validate_code(code_text)
        description = validate_description(description_text)
        if code in seen:
            raise Rejected(f"category {code} appears more than once in the file")
        if db.categories.get(category=code) is not None:
            raise Rejected(f"category {code} already exists")
        seen.add(code)
        checked.append((code, description))
    for code, description in checked:
        db.categories.create(category=code, description=description)
    return [["table", "loaded"], ["categories", str(len(checked))]]


register(("load", "categories"), 1, 1, load_categories)
