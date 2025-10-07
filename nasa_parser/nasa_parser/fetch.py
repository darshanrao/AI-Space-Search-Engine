from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Optional

import requests


PMC_ID_RE = re.compile(r"PMC(\d+)")


@dataclass
class FetchResult:
    pmc_id: str
    jats_xml: Optional[str]
    html: Optional[str]
    source: str  # "jats" | "html" | "none"
    url: Optional[str] = None
    pmid: Optional[str] = None
    doi: Optional[str] = None


def extract_pmc_id(url: str) -> Optional[str]:
    match = PMC_ID_RE.search(url)
    if not match:
        return None
    return match.group(1)


def _requests_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "nasa-parser/0.1 (+https://nasa.gov; contact: noreply@example.com)",
            "Accept": "*/*",
        }
    )
    return session


def fetch_pmc_jats(pmc_numeric_id: str, session: Optional[requests.Session] = None) -> Optional[str]:
    sess = session or _requests_session()
    params = {
        "db": "pmc",
        "id": f"PMC{pmc_numeric_id}",
        "retmode": "xml",
        "tool": "nasa-parser",
        "email": "noreply@example.com",
    }
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    resp = sess.get(url, params=params, timeout=30)
    if resp.status_code == 200 and resp.text and "<article" in resp.text:
        return resp.text

    # Fallback without PMC prefix
    params["id"] = pmc_numeric_id
    resp = sess.get(url, params=params, timeout=30)
    if resp.status_code == 200 and resp.text and "<article" in resp.text:
        return resp.text

    return None


def fetch_pmc_html(article_url: str, session: Optional[requests.Session] = None) -> Optional[str]:
    sess = session or _requests_session()
    # Prefer full article HTML (contains figures) and fallback to printable if needed
    resp = sess.get(article_url, timeout=30)
    if resp.status_code == 200 and "<html" in resp.text.lower():
        return resp.text
    printable_url = article_url.rstrip("/") + "/?page=1"
    resp = sess.get(printable_url, timeout=30)
    if resp.status_code == 200 and "<html" in resp.text.lower():
        return resp.text
    return None


def get_article(article_url: str, session: Optional[requests.Session] = None) -> FetchResult:
    sess = session or _requests_session()
    pmc_id = extract_pmc_id(article_url)
    if not pmc_id:
        raise ValueError(f"Could not extract PMC id from URL: {article_url}")

    time.sleep(0.34)
    jats = fetch_pmc_jats(pmc_id, session=sess)
    if jats:
        # Also fetch HTML for assets like figure CDN links
        time.sleep(0.2)
        html_page = fetch_pmc_html(article_url, session=sess)
        return FetchResult(pmc_id=pmc_id, jats_xml=jats, html=html_page, source="jats", url=article_url)

    time.sleep(0.34)
    html = fetch_pmc_html(article_url, session=sess)
    if html:
        return FetchResult(pmc_id=pmc_id, jats_xml=None, html=html, source="html", url=article_url)

    return FetchResult(pmc_id=pmc_id, jats_xml=None, html=None, source="none", url=article_url)


