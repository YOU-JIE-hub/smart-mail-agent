from __future__ import annotations

import re
from typing import Iterable, Tuple

try:
    from email_validator import EmailNotValidError, validate_email  # provided by email-validator
except Exception:
    validate_email = None
    EmailNotValidError = Exception

MAX_SUBJECT = 200
MAX_CONTENT = 20000
ATTACH_BAD_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]')


def check_sender(sender: str) -> Tuple[bool, str]:
    if not sender or "@" not in sender:
        return False, "sender_missing_or_invalid"
    if validate_email:
        try:
            validate_email(sender, check_deliverability=False)
        except EmailNotValidError:
            return False, "sender_invalid_format"
    return True, "OK"


def check_subject(subject: str) -> Tuple[bool, str]:
    if not subject:
        return False, "subject_missing"
    if len(subject) > MAX_SUBJECT:
        return False, "subject_too_long"
    return True, "OK"


def check_content(content: str) -> Tuple[bool, str]:
    if not content or not content.strip():
        return False, "content_empty"
    if len(content) > MAX_CONTENT:
        return False, "content_too_long"
    return True, "OK"


def check_attachments(names: Iterable[str]) -> Tuple[bool, str]:
    for n in names or []:
        if ATTACH_BAD_CHARS.search(n):
            return False, "attachment_name_illegal_chars"
    return True, "OK"
