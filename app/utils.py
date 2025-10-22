import os
import re
from typing import Tuple

def clean_text(raw_text: str) -> str:
    """Clean control characters and collapse whitespace.

    Returns an empty string for falsy input.
    """
    if not raw_text:
        return ""

    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", raw_text)
    text = text.replace("\r\n", " ").replace("\n", " ").replace("\t", " ")
    text = " ".join(text.split())
    return text

def check_file_size_bytes(content_bytes: bytes, max_mb: int) -> Tuple[bool, str]:
    """Return (ok, message) whether bytes length <= max_mb.

    Message is Vietnamese to match project style.
    """
    max_bytes = max_mb * 1024 * 1024
    if len(content_bytes) > max_bytes:
        return False, f"File quá lớn (> {max_mb}MB)."
    return True, "OK"

def safe_filename(filename: str) -> str:
    """Return basename to avoid directory traversal in uploaded filenames."""
    return os.path.basename(filename)
