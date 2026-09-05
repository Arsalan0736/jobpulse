"""HTML/text sanitization helpers for scrapers."""
from bs4 import BeautifulSoup
import re


_WHITESPACE_RE = re.compile(r"[ \t]+")
_NEWLINE_RE = re.compile(r"\n{3,}")


def html_to_text(raw: str) -> str:
    """Convert HTML to clean plain text. Strips tags, decodes entities,
    collapses whitespace, preserves paragraph/list structure with newlines."""
    if not raw:
        return ""
    if "<" not in raw and "&" not in raw:
        # already plain text, just normalize whitespace
        return _normalize(raw)

    soup = BeautifulSoup(raw, "html.parser")

    # Drop script/style/svg entirely
    for tag in soup(["script", "style", "svg", "noscript", "iframe"]):
        tag.decompose()

    # Insert newlines around block-level tags so paragraphs/lists stay readable
    block_tags = [
        "p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3",
        "h4", "h5", "h6", "section", "article", "header", "footer",
    ]
    for tag in soup.find_all(block_tags):
        tag.insert_after("\n")
        if tag.name == "li":
            tag.insert_before("- ")

    text = soup.get_text(separator=" ")
    return _normalize(text)


def _normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WHITESPACE_RE.sub(" ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = _NEWLINE_RE.sub("\n\n", text)
    return text.strip()