"""GS1 identities only. Keep zeroes and reject retailer PLUs / arbitrary QR text."""

import re


def validate_gtin(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"(?:[0-9]{8}|[0-9]{12}|[0-9]{13}|[0-9]{14})", value
    ):
        raise ValueError("Invalid GTIN length or digits")
    total = sum(
        int(n) * (3 if i % 2 == 0 else 1) for i, n in enumerate(reversed(value[:-1]))
    ) + int(value[-1])
    if total % 10:
        raise ValueError("Invalid GTIN check digit")
    return value


def gtin_aliases(value):
    canonical = validate_gtin(value).zfill(14)
    return {
        canonical[-length:]
        for length in (8, 12, 13, 14)
        if canonical[:-length].strip("0") == ""
    }
