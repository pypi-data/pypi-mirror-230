from collective.bluesky import DEFAULT_HOST
from collective.bluesky import HANDLE_VALIDATOR

import re


INVALID_TLD = rb"\.(local|arpa|localhost|internal|onion)$"


def validate_handle(handle: str) -> bool:
    """Check if this is a valid handle."""
    is_valid = False
    handle = handle.encode("utf-8")
    if not re.search(INVALID_TLD, handle):
        is_valid = True if re.match(HANDLE_VALIDATOR, handle) else False
    return is_valid


def format_handle(handle: str) -> str:
    """Format handle."""
    return f"@{handle}" if validate_handle(handle) else f"@{handle}.{DEFAULT_HOST}"
