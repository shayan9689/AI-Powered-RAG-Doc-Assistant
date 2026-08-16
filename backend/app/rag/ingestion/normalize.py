import re

_HYPHEN_LINE_BREAK = re.compile(r"(\w)-\n(\w)")
_SINGLE_NEWLINE = re.compile(r"(?<!\n)\n(?!\n)")
_MULTI_SPACE = re.compile(r"[ \t]+")
_MULTI_BLANK = re.compile(r"\n{3,}")


def normalize_text(text: str) -> str:
    cleaned = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    cleaned = _HYPHEN_LINE_BREAK.sub(r"\1\2", cleaned)
    cleaned = _SINGLE_NEWLINE.sub(" ", cleaned)
    cleaned = _MULTI_SPACE.sub(" ", cleaned)
    cleaned = _MULTI_BLANK.sub("\n\n", cleaned)
    return cleaned.strip()
