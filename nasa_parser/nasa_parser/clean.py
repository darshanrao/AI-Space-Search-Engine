from __future__ import annotations

import re
import unicodedata
from typing import Iterable

from bs4 import BeautifulSoup


_REF_CALLOUT_RE = re.compile(r"\[(?:\d+|[\d,\s\-]+)\]")
_INLINE_XREF_RE = re.compile(r"\((?:Fig\.|Figure|Table|Eq\.|Equation)\s?[\w\-\.]+\)", re.IGNORECASE)
_URL_NOISE_RE = re.compile(r"https?://\S+")


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = _REF_CALLOUT_RE.sub("", normalized)
    normalized = _INLINE_XREF_RE.sub("", normalized)
    normalized = _URL_NOISE_RE.sub("", normalized)
    normalized = normalized.replace("-\n", "")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def replace_equations_and_tables(html_fragment: str) -> str:
    soup = BeautifulSoup(html_fragment, "lxml")
    for eq in soup.find_all(["math", "mml:math", "equation"]):
        eq.replace_with("[MATH]")
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if len(rows) >= 10 or any(len(r.find_all(["td", "th"])) >= 6 for r in rows):
            table.replace_with("[TABLE OMITTED]")
        else:
            table.replace_with(table.get_text(" ", strip=True))
    for fig in soup.find_all(["fig", "figure"]):
        caption = fig.find(["caption", "figcaption"]) or fig.find(class_=re.compile("caption", re.I))
        cap_text = caption.get_text(" ", strip=True) if caption else ""
        placeholder = f"[FIGURE CAPTION: {cap_text}]" if cap_text else "[FIGURE CAPTION]"
        fig.replace_with(placeholder)
    return str(soup)


def clean_blocks(blocks: Iterable[tuple[str, str]]) -> list[str]:
    cleaned: list[str] = []
    exclude_keywords = (
        "references",
        "bibliography",
        "acknowledgments",
        "acknowledgements",
        "conflict of interest",
        "competing interests",
        "author contributions",
        "funding",
        "ethics",
        "data availability",
        "supplementary",
    )
    for path, text in blocks:
        lower_path = path.lower()
        if any(k in lower_path for k in exclude_keywords):
            continue
        fragment = f"<div>{text}</div>"
        fragment = replace_equations_and_tables(fragment)
        soup = BeautifulSoup(fragment, "lxml")
        raw_text = soup.get_text(" ", strip=True)
        norm = normalize_text(raw_text)
        if len(norm) < 20 and not norm.startswith("[FIGURE CAPTION"):
            continue
        cleaned.append(f"{path}: {norm}")
    return cleaned


def should_exclude_path(path: str) -> bool:
    lower_path = path.lower()
    exclude_keywords = (
        "references",
        "reference",
        "bibliography",
        "acknowledgments",
        "acknowledgements",
        "appendix",
        "footnotes",
        "publisher's disclaimer",
        "publisher s disclaimer",
        "disclaimer",
        "highlights",
        "actions",
        "cite",
        "add to collections",
        "abbreviations",
        "conflict of interest",
        "competing interests",
        "author contributions",
        "funding",
        "ethics",
        "data availability",
        "supplementary",
    )
    return any(k in lower_path for k in exclude_keywords)


def clean_text(text: str, min_len: int = 20) -> str:
    fragment = f"<div>{text}</div>"
    fragment = replace_equations_and_tables(fragment)
    soup = BeautifulSoup(fragment, "lxml")
    raw_text = soup.get_text(" ", strip=True)
    norm = normalize_text(raw_text)
    if len(norm) < min_len and not norm.startswith("[FIGURE CAPTION"):
        return ""
    return norm


