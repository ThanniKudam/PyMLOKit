from __future__ import annotations

from typing import Iterable, Sequence, Any


def format_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    rows_list = [[("" if c is None else str(c)) for c in row] for row in rows]
    cols = len(headers)
    widths = [len(h) for h in headers]
    for idx, row in enumerate(rows_list):
        if len(row) != cols:
            if len(row) < cols:
                row.extend([""] * (cols - len(row)))
            elif len(row) > cols:
                rows_list[idx] = row[:cols]
                row = rows_list[idx]
        
        for i, c in enumerate(row):
            widths[i] = max(widths[i], len(c))

    header_line = " | ".join(h.rjust(widths[i]) for i, h in enumerate(headers))
    sep_line = "-" * len(header_line)
    body_lines = [" | ".join(row[i].rjust(widths[i]) for i in range(cols)) for row in rows_list]
    return "\n".join([header_line, sep_line, *body_lines])


def print_table(
    headers_or_data: Sequence[str] | Sequence[dict[str, Any]], 
    rows: Iterable[Sequence[object]] | None = None
) -> None:
    """
    Prints a table. 
    Usage 1: print_table(["Header1", "Header2"], [["Row1Col1", "Row1Col2"], ...])
    Usage 2: print_table([{"Header1": "Val1", "Header2": "Val2"}, ...])
    """
    if rows is None:
        # Assume usage 2: list of dicts
        data = headers_or_data
        if not data:
            return
            
        # Check if it's actually a list of dicts
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            # Infer headers from first item keys
            headers = list(data[0].keys())
            # Extract rows
            extracted_rows = [[d.get(h, "") for h in headers] for d in data]
            print(format_table(headers, extracted_rows))
            return
        else:
            # Empty list or not list of dicts?
            # If it was intended as headers but rows is None, that's invalid usage 1
            pass
            
    # Usage 1
    if rows is not None:
        print(format_table(headers_or_data, rows))
