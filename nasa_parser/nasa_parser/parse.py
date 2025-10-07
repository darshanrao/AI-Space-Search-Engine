from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup
from bs4 import element as bs4_element
import re
from urllib.parse import urljoin
import requests


def parse_jats_sections(jats_xml: str) -> List[Tuple[str, str]]:
    """
    Return list of (section_path, aggregated_text) from JATS.
    One chunk per top-level <sec>. Subsection content is merged into its parent section.
    """
    soup = BeautifulSoup(jats_xml, "lxml-xml")
    # Metadata
    pmid_el = soup.find("article-id", {"pub-id-type": "pmid"})
    doi_el = soup.find("article-id", {"pub-id-type": "doi"})
    meta = {
        "pmid": pmid_el.get_text(strip=True) if pmid_el else None,
        "doi": doi_el.get_text(strip=True) if doi_el else None,
    }

    def section_label(sec) -> str:
        title_el = sec.find(["title"], recursive=False)
        return title_el.get_text(strip=True) if title_el else ""

    results: List[Tuple[str, str]] = []

    # Title
    article_title = soup.find("article-title")
    title_text = article_title.get_text(" ", strip=True) if article_title else ""

    # Abstract (single chunk)
    abstract = soup.find("abstract")
    if abstract:
        abs_text = abstract.get_text(" ", strip=True)
        if abs_text:
            results.append((f"{title_text} — Abstract", abs_text))

    # Body sections
    body = soup.find("body")
    if body:
        for sec in body.find_all("sec", recursive=False):
            sec_title = section_label(sec)
            sec_path = f"{title_text} — {sec_title}" if sec_title else f"{title_text} — Section"

            # Aggregate all text within this section, including subsections, but excluding titles
            sec_text_parts: List[str] = []
            for el in sec.find_all(["p", "list-item"], recursive=True):
                txt = el.get_text(" ", strip=True)
                if txt:
                    sec_text_parts.append(txt)
            if sec_text_parts:
                results.append((sec_path, " ".join(sec_text_parts)))

    return results


def parse_jats_metadata(jats_xml: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(jats_xml, "lxml-xml")
    pmid = soup.find("article-id", {"pub-id-type": "pmid"})
    doi = soup.find("article-id", {"pub-id-type": "doi"})
    return {
        "pmid": pmid.get_text(strip=True) if pmid else None,
        "doi": doi.get_text(strip=True) if doi else None,
    }


def parse_html_main_text(html: str) -> List[Tuple[str, str]]:
    """
    Aggregate content by section: one chunk per <h2> block.
    All content under an <h2> until the next <h2> is merged (including <h3> subsections).
    Paragraphs before the first <h2> are grouped into Title — Body.
    """
    soup = BeautifulSoup(html, "lxml")
    title_el = soup.find("h1")
    title_text = title_el.get_text(" ", strip=True) if title_el else ""
    # PMC pages structure: sections within article content
    article = soup.find("div", id="maincontent") or soup

    results: List[Tuple[str, str]] = []

    current_h2_title: Optional[str] = None
    current_h2_parts: List[str] = []
    preface_parts: List[str] = []

    def flush_h2():
        nonlocal current_h2_title, current_h2_parts
        if current_h2_title and current_h2_parts:
            path = f"{title_text} — {current_h2_title}"
            results.append((path, " ".join(current_h2_parts)))
        current_h2_title = None
        current_h2_parts = []

    for el in article.find_all(["h2", "p", "li", "h3", "h4"], recursive=True):
        # Skip anything inside a figure container
        if el.find_parent(["figure"]) is not None:
            continue
        if el.name == "h2":
            title_candidate = el.get_text(" ", strip=True)
            # Avoid promoting bare figure labels as section headers
            if re.match(r"^\s*(Figure|Fig\.)\s*\d+[.:]?\s*$", title_candidate, re.I):
                continue
            flush_h2()
            current_h2_title = title_candidate
        else:
            text = el.get_text(" ", strip=True)
            if not text:
                continue
            if current_h2_title:
                current_h2_parts.append(text)
            else:
                preface_parts.append(text)

    flush_h2()
    if preface_parts:
        results.insert(0, (f"{title_text} — Body", " ".join(preface_parts)))

    return results


def parse_html_main_text_loose(html: str) -> List[Tuple[str, str]]:
    """
    Looser HTML parsing:
    - Recognize h1..h5 as section boundaries
    - If no headings found, aggregate all paragraphs under Body
    - Include list items and simple divs with text
    """
    soup = BeautifulSoup(html, "lxml")
    title_el = soup.find("h1")
    title_text = title_el.get_text(" ", strip=True) if title_el else ""
    article = soup.find("div", id="maincontent") or soup

    results: List[Tuple[str, str]] = []
    current_title: Optional[str] = None
    current_parts: List[str] = []

    def flush():
        nonlocal current_title, current_parts
        if current_title and current_parts:
            path = f"{title_text} — {current_title}"
            results.append((path, " ".join(current_parts)))
        current_title = None
        current_parts = []

    headings = {"h1", "h2", "h3", "h4", "h5"}
    any_heading = False
    for el in article.find_all(list(headings | {"p", "li", "div"}), recursive=True):
        # Skip anything inside a figure container
        if el.find_parent(["figure"]) is not None:
            continue
        if el.name in headings:
            title_candidate = el.get_text(" ", strip=True)
            # Avoid figure-only headers
            if re.match(r"^\s*(Figure|Fig\.)\s*\d+[.:]?\s*$", title_candidate, re.I):
                continue
            any_heading = True
            flush()
            current_title = title_candidate
        else:
            # only accept divs that look like text blocks (no nested sections)
            if el.name == "div" and (el.find(list(headings)) or not el.get_text(strip=True)):
                continue
            txt = el.get_text(" ", strip=True)
            if txt:
                if current_title:
                    current_parts.append(txt)
                else:
                    # buffer as Body
                    current_title = "Body"
                    current_parts.append(txt)
    flush()

    if not any_heading and not results:
        # Fallback: all text under Body
        body_txt = article.get_text(" ", strip=True)
        if body_txt:
            results.append((f"{title_text} — Body", body_txt))

    return results


def parse_html_main_text_robust(html: str) -> List[Tuple[str, str]]:
    """
    More robust HTML parsing for irregular pages:
    - Treat h1..h5, [role=heading], [aria-level] as headers
    - Promote paragraphs that start with bold/strong text + punctuation as headers
    - Aggregate text from p/li and simple divs
    - Fallback to Body if no headings found
    """
    soup = BeautifulSoup(html, "lxml")
    title_el = soup.find("h1")
    title_text = title_el.get_text(" ", strip=True) if title_el else ""
    article = soup.find("div", id="maincontent") or soup

    results: List[Tuple[str, str]] = []
    current_title: Optional[str] = None
    current_parts: List[str] = []

    def flush():
        nonlocal current_title, current_parts
        if current_title and current_parts:
            path = f"{title_text} — {current_title}"
            results.append((path, " ".join(current_parts)))
        current_title = None
        current_parts = []

    def is_header(el) -> bool:
        # Guard against Doctype and NavigableString
        if not isinstance(el, bs4_element.Tag):
            return False
        if getattr(el, "name", None) in {"h1", "h2", "h3", "h4", "h5"}:
            txt = el.get_text(" ", strip=True)
            if re.match(r"^\s*(Figure|Fig\.)\s*\d+\.?\s*$", txt, re.I):
                return False
            return True
        if el.has_attr("role") and isinstance(el.get("role"), str) and el["role"].lower() == "heading":
            return True
        if el.has_attr("aria-level"):
            return True
        return False

    # Promote leading bold/strong segments as header
    def promoted_header_from_p(p) -> Optional[str]:
        if p.name != "p":
            return None
        if not p.contents:
            return None
        first = p.contents[0]
        if getattr(first, "name", None) in ("strong", "b"):
            txt = first.get_text(" ", strip=True)
            # header-like if ends with ':' or '.' or is "Methods"/"Results" etc.
            if txt and (txt.endswith(":") or txt.endswith(".") or len(txt.split()) <= 3):
                if re.match(r"^\s*(Figure|Fig\.)\s*\d+\.?\s*$", txt, re.I):
                    return None
                return txt.rstrip(" :.")
        return None

    any_header = False
    for el in article.descendants:
        if not isinstance(el, bs4_element.Tag):
            continue
        if is_header(el):
            any_header = True
            flush()
            current_title = el.get_text(" ", strip=True)
            continue
        if el.name == "p":
            promoted = promoted_header_from_p(el)
            if promoted:
                flush()
                current_title = promoted
                # remove the promoted strong/b from text body
                body_txt = el.get_text(" ", strip=True)
                if body_txt:
                    # drop the promoted header substring if present at start
                    body_txt = body_txt[len(promoted):].lstrip(" .:-")
                if body_txt:
                    current_parts.append(body_txt)
                continue
        if el.name in {"p", "li", "div"}:
            # ignore divs that contain structural elements
            if el.name == "div" and (el.find(["h1", "h2", "h3", "h4", "h5"]) or not el.get_text(strip=True)):
                continue
            # Skip text inside figure containers
            if el.find_parent(["figure"]) is not None:
                continue
            txt = el.get_text(" ", strip=True)
            if txt:
                if current_title:
                    current_parts.append(txt)
                else:
                    current_title = "Body"
                    current_parts.append(txt)
    flush()

    if not any_header and not results:
        body_txt = article.get_text(" ", strip=True)
        if body_txt:
            results.append((f"{title_text} — Body", body_txt))

    return results


def _extract_article_title_from_jats(jats_xml: str) -> str:
    soup = BeautifulSoup(jats_xml, "lxml-xml")
    article_title = soup.find("article-title")
    return article_title.get_text(" ", strip=True) if article_title else ""


def _extract_article_title_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    title_el = soup.find("h1")
    return title_el.get_text(" ", strip=True) if title_el else ""


def _zero_pad_figure(num: Optional[str]) -> str:
    if not num:
        return ""
    try:
        return f"{int(re.sub(r'[^0-9]', '', num)):03d}"
    except Exception:
        return ""


def _resolve_cdn_url_from_html(html: Optional[str], filename: str, fig_num: Optional[str] = None) -> Optional[str]:
    if not html:
        return None
    soup = BeautifulSoup(html, "lxml")
    candidates: List[str] = []
    imgs = soup.find_all("img")
    # 1) Prefer images with class hints
    def score(img) -> int:
        s = 0
        classes = img.get("class") or []
        if any(c in ("graphic", "zoom-in") for c in classes):
            s += 2
        alt = (img.get("alt") or "").lower()
        if fig_num and f"figure {fig_num}" in alt:
            s += 3
        src = img.get("src") or img.get("data-src") or ""
        if fig_num and re.search(rf"\.g{int(fig_num):03d}\.\w+$", src):
            s += 2
        return s

    imgs = sorted(imgs, key=score, reverse=True)
    for img in imgs:
        # gather possible URL attrs
        for attr in ("src", "data-src"):
            v = img.get(attr)
            if not v:
                continue
            if fig_num and re.search(rf"\.g{int(fig_num):03d}\.\w+$", v):
                candidates.append(v)
            if filename and v.endswith(filename):
                candidates.append(v)
        for attr in ("srcset", "data-srcset"):
            v = img.get(attr)
            if v:
                for part in v.split(","):
                    url = part.strip().split(" ")[0]
                    if fig_num and re.search(rf"\.g{int(fig_num):03d}\.\w+$", url):
                        candidates.append(url)
                    if filename and url.endswith(filename):
                        candidates.append(url)
    # prefer CDN urls
    for url in candidates:
        if url.startswith("https://cdn.ncbi.nlm.nih.gov/"):
            return url
    return candidates[0] if candidates else None


def _resolve_cdn_via_head(bin_url: str) -> Optional[str]:
    try:
        with requests.Session() as s:
            s.headers.update({
                "User-Agent": "nasa-parser/0.1 (+https://nasa.gov; contact: noreply@example.com)",
                "Accept": "*/*",
            })
            resp = s.get(bin_url, timeout=20, allow_redirects=True)
            if resp.status_code == 200 and resp.url:
                return resp.url
    except Exception:
        return None
    return None


def parse_jats_figures(
    jats_xml: str,
    article_url: Optional[str],
    pmc_id: Optional[str],
    html_for_cdn: Optional[str] = None,
) -> List[Dict[str, str]]:
    soup = BeautifulSoup(jats_xml, "lxml-xml")
    title = _extract_article_title_from_jats(jats_xml)
    doi_el = soup.find("article-id", {"pub-id-type": "doi"})
    doi = doi_el.get_text(strip=True) if doi_el else ""
    results: List[Dict[str, str]] = []

    base_article_url = article_url or (f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmc_id}/" if pmc_id else None)

    def section_path_for(el) -> str:
        parent_sec = el.find_parent("sec")
        sec_title = ""
        if parent_sec:
            title_el = parent_sec.find(["title"], recursive=False)
            if title_el:
                sec_title = title_el.get_text(strip=True)
        return f"{title} — {sec_title}" if sec_title else f"{title} — Body"

    for fig in soup.find_all("fig"):
        label_el = fig.find("label")
        label_text = label_el.get_text(" ", strip=True) if label_el else ""
        # Extract figure number
        m = re.search(r"(\d+)", label_text)
        fig_num = m.group(1) if m else ""
        fig_num_padded = _zero_pad_figure(fig_num)
        # Caption
        caption_el = fig.find("caption")
        caption_text = caption_el.get_text(" ", strip=True) if caption_el else ""
        # Image href
        graphic = fig.find("graphic")
        img_href = ""
        if graphic:
            img_href = graphic.get("xlink:href") or graphic.get("href") or ""
        # Construct PMC 'bin' URL for figure assets if relative href is present
        img_url = ""
        if img_href:
            # Try resolve against HTML to get actual CDN blob link
            resolved = _resolve_cdn_url_from_html(html_for_cdn, img_href, fig_num=fig_num)
            if resolved:
                img_url = resolved
            else:
                if img_href.startswith("http://") or img_href.startswith("https://"):
                    img_url = img_href
                else:
                    if pmc_id:
                        candidate = f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmc_id}/bin/{img_href}"
                        redirected = _resolve_cdn_via_head(candidate)
                        img_url = redirected or candidate
                    elif base_article_url:
                        img_url = urljoin(base_article_url, img_href)

        sec_path = section_path_for(fig)
        path_header = f"{sec_path} > Figure {fig_num or ''}".rstrip()

        results.append(
            {
                "path": path_header,
                "pmcid": f"PMC{pmc_id}" if pmc_id else "",
                "doi": doi,
                "url": (article_url or (f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmc_id}/" if pmc_id else "")),
                "img": img_url,
                "fig_id": fig_num_padded or fig.get("id", ""),
                "caption": caption_text,
            }
        )

    return results


def parse_html_figures(html: str, article_url: Optional[str], pmc_id: Optional[str]) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    title = _extract_article_title_from_html(html)
    results: List[Dict[str, str]] = []
    base_article_url = article_url or (f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmc_id}/" if pmc_id else None)

    h2_titles: List[Tuple[object, str]] = []
    for h2 in soup.find_all("h2"):
        h2_titles.append((h2, h2.get_text(" ", strip=True)))

    def current_section_path(el) -> str:
        # Walk backwards to nearest h2
        prev = el
        while prev and prev.previous_element is not None:
            prev = prev.previous_element
            if getattr(prev, "name", None) == "h2":
                hdr = prev.get_text(" ", strip=True)
                return f"{title} — {hdr}"
        return f"{title} — Body"

    figures = []
    # Prefer article figures
    article_root = soup.find("div", id="maincontent") or soup
    figures.extend(article_root.find_all("figure"))
    figures.extend(article_root.find_all("div", class_=re.compile("fig", re.I)))

    for fig in figures:
        # Try to skip duplicates where a wrapper div and a nested figure both matched
        if fig.find_parent("figure") is not None and fig.name != "figure":
            continue
        # Caption
        caption_el = fig.find(["figcaption"]) or fig.find(class_=re.compile("caption", re.I))
        caption_text = caption_el.get_text(" ", strip=True) if caption_el else ""
        # Label / number
        label_text = ""
        label_el = fig.find(class_=re.compile("label", re.I)) or fig.find("span", class_=re.compile("fig-label", re.I))
        if label_el:
            label_text = label_el.get_text(" ", strip=True)
        if not label_text and caption_text:
            # Often caption starts with "Figure 2. ..."
            m = re.match(r"\s*(Figure|Fig\.)\s*(\d+)", caption_text, re.I)
            label_text = f"Figure {m.group(2)}" if m else ""
        m = re.search(r"(\d+)", label_text)
        fig_num = m.group(1) if m else ""
        fig_num_padded = _zero_pad_figure(fig_num)
        # Image URL
        img = fig.find("img")
        img_src = ""
        if img:
            img_src = img.get("src") or img.get("data-src") or ""
        img_url = ""
        if img_src:
            if img_src.startswith("http://") or img_src.startswith("https://"):
                img_url = img_src
            else:
                # Prefer pmc.ncbi.nlm.nih.gov as canonical domain
                if img_src.startswith("/"):
                    img_url = urljoin("https://pmc.ncbi.nlm.nih.gov", img_src)
                else:
                    img_url = urljoin(base_article_url or "https://pmc.ncbi.nlm.nih.gov", img_src)
        # Path
        sec_path = current_section_path(fig)
        path_header = f"{sec_path} > Figure {fig_num or ''}".rstrip()
        results.append(
            {
                "path": path_header,
                "pmcid": f"PMC{pmc_id}" if pmc_id else "",
                "doi": "",  # DOI is harder from HTML; leave blank if unknown
                "url": (article_url or (f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmc_id}/" if pmc_id else "")),
                "img": img_url,
                "fig_id": fig_num_padded or (fig.get("id") or ""),
                "caption": caption_text,
            }
        )

    # Robust fallback: if none found, scan generic img/anchor patterns and NIHMS blobs
    if not results:
        for img in soup.find_all("img"):
            classes = (img.get("class") or [])
            src = img.get("src") or img.get("data-src") or ""
            alt = (img.get("alt") or "").strip()
            if not src:
                continue
            # Heuristic for figure-like
            href_parent = (img.find_parent("a").get("href") if img.find_parent("a") and img.find_parent("a").has_attr("href") else "")
            is_blob = "pmc/blobs/" in src or src.endswith('.jpg') and 'nihms' in src.lower()
            is_tileshop = "tileshop_pmc" in href_parent
            gnum = re.search(r"\.g(\d{3})\.", src)
            looks_figure = (
                "graphic" in classes
                or alt.lower().startswith("figure")
                or bool(gnum)
                or is_blob
                or is_tileshop
            )
            if looks_figure:
                m = re.search(r"g(\d{3})\.", src)
                fig_num = None
                if m:
                    try:
                        fig_num = str(int(m.group(1)))
                    except Exception:
                        fig_num = None
                # Section path by nearest h2
                sec_path = current_section_path(img)
                path_header = f"{sec_path} > Figure {fig_num or ''}".rstrip()
                # Caption: try next sibling caption or enclosing anchor title
                caption_text = ""
                a = img.find_parent("a")
                if a and a.get("title"):
                    caption_text = a.get("title").strip()
                if not caption_text:
                    cap = img.find_next(["figcaption"]) or img.find_next(class_=re.compile("caption", re.I))
                    if cap:
                        caption_text = cap.get_text(" ", strip=True)
                # Resolve URL; prefer CDN as-is
                if src.startswith("/"):
                    img_url = urljoin("https://pmc.ncbi.nlm.nih.gov", src)
                else:
                    img_url = urljoin(article_url or "https://pmc.ncbi.nlm.nih.gov", src)
                results.append(
                    {
                        "path": path_header,
                        "pmcid": f"PMC{pmc_id}" if pmc_id else "",
                        "doi": "",
                        "url": (article_url or (f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmc_id}/" if pmc_id else "")),
                        "img": img_url,
                        "fig_id": _zero_pad_figure(fig_num) if fig_num else "",
                        "caption": caption_text,
                    }
                )
    return results


def _extract_table_rows_from_jats_table(table_tag) -> List[List[str]]:
    rows: List[List[str]] = []
    # headers
    thead = table_tag.find("thead")
    if thead:
        for tr in thead.find_all("tr", recursive=False):
            cells = [th.get_text(" ", strip=True) for th in tr.find_all(["th", "td"], recursive=False)]
            if any(cells):
                rows.append(cells)
    # body
    tbody = table_tag.find("tbody") or table_tag
    for tr in tbody.find_all("tr", recursive=False):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"], recursive=False)]
        if any(cells):
            rows.append(cells)
    return rows


def parse_jats_tables(jats_xml: str, article_url: Optional[str], pmc_id: Optional[str]) -> List[Dict[str, object]]:
    soup = BeautifulSoup(jats_xml, "lxml-xml")
    title = _extract_article_title_from_jats(jats_xml)
    doi_el = soup.find("article-id", {"pub-id-type": "doi"})
    doi = doi_el.get_text(strip=True) if doi_el else ""
    results: List[Dict[str, object]] = []

    for tw in soup.find_all("table-wrap"):
        label_el = tw.find("label")
        label_text = label_el.get_text(" ", strip=True) if label_el else ""
        m = re.search(r"(\d+)", label_text)
        tbl_num = m.group(1) if m else ""
        # caption/title as table name
        cap = tw.find("caption")
        cap_title = ""
        if cap:
            t = cap.find("title")
            cap_title = t.get_text(" ", strip=True) if t else cap.get_text(" ", strip=True)
        # section path
        parent_sec = tw.find_parent("sec")
        sec_title = ""
        if parent_sec:
            st = parent_sec.find("title", recursive=False)
            sec_title = st.get_text(strip=True) if st else ""
        # Use table name in header as requested
        header_path = f"{title} — {cap_title or sec_title} > Table {tbl_num or ''}".rstrip()
        # find the actual table
        table_tag = tw.find("table")
        rows = _extract_table_rows_from_jats_table(table_tag) if table_tag else []
        results.append(
            {
                "path": header_path,
                "pmcid": f"PMC{pmc_id}" if pmc_id else "",
                "doi": doi,
                "url": (article_url or (f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmc_id}/" if pmc_id else "")),
                "rows": rows,
            }
        )
    return results


def _extract_table_rows_from_html_table(table_tag) -> List[List[str]]:
    rows: List[List[str]] = []
    thead = table_tag.find("thead")
    if thead:
        for tr in thead.find_all("tr", recursive=False):
            cells = [th.get_text(" ", strip=True) for th in tr.find_all(["th", "td"], recursive=False)]
            if any(cells):
                rows.append(cells)
    tbody = table_tag.find("tbody") or table_tag
    for tr in tbody.find_all("tr", recursive=False):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"], recursive=False)]
        if any(cells):
            rows.append(cells)
    return rows


def parse_html_tables(html: str, article_url: Optional[str], pmc_id: Optional[str]) -> List[Dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    title = _extract_article_title_from_html(html)
    results: List[Dict[str, object]] = []

    for tbl in (soup.find("div", id="maincontent") or soup).find_all("table"):
        # caption and label/number
        cap_el = tbl.find("caption")
        cap_text = cap_el.get_text(" ", strip=True) if cap_el else ""
        # Try to parse "Table 1." at start
        tbl_num = ""
        m = re.match(r"\s*(Table|Tab\.)\s*(\d+)\.?\s*(.*)", cap_text, re.I)
        table_name = ""
        if m:
            tbl_num = m.group(2)
            table_name = m.group(3).strip()
        else:
            table_name = cap_text
        # fall back: search preceding text for Table N
        if not tbl_num:
            prev = cap_el or tbl
            while prev and prev.previous_element is not None and not tbl_num:
                prev = prev.previous_element
                if getattr(prev, "name", None) in ("p", "div"):
                    txt = prev.get_text(" ", strip=True)
                    m2 = re.search(r"(Table|Tab\.)\s*(\d+)", txt, re.I)
                    if m2:
                        tbl_num = m2.group(2)
                        break
        # section path: nearest h2
        sec_path = title + " — Body"
        prev = tbl
        while prev and prev.previous_element is not None:
            prev = prev.previous_element
            if getattr(prev, "name", None) == "h2":
                hdr = prev.get_text(" ", strip=True)
                sec_path = f"{title} — {hdr}"
                break
        header_path = f"{title} — {table_name or sec_path.split(' — ',1)[1]} > Table {tbl_num or ''}".rstrip()
        rows = _extract_table_rows_from_html_table(tbl)
        results.append(
            {
                "path": header_path,
                "pmcid": f"PMC{pmc_id}" if pmc_id else "",
                "doi": "",
                "url": (article_url or (f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmc_id}/" if pmc_id else "")),
                "rows": rows,
            }
        )
    # Robust fallback: scan for caption-like paragraphs and adjacent tables
    if not results:
        for cap_el in soup.find_all(["caption", "p", "div"]):
            txt = cap_el.get_text(" ", strip=True)
            if not txt:
                continue
            m = re.match(r"\s*(Table|Tab\.)\s*(\d+)\.?\s*(.*)", txt, re.I)
            if not m:
                continue
            tbl_num = m.group(2)
            table_name = m.group(3).strip()
            # find next table sibling/descendant
            table_tag = cap_el.find_next("table")
            if not table_tag:
                continue
            # section path by nearest h2
            sec_path = title + " — Body"
            prev = cap_el
            while prev and prev.previous_element is not None:
                prev = prev.previous_element
                if getattr(prev, "name", None) == "h2":
                    hdr = prev.get_text(" ", strip=True)
                    sec_path = f"{title} — {hdr}"
                    break
            header_path = f"{title} — {table_name or sec_path.split(' — ',1)[1]} > Table {tbl_num}".rstrip()
            rows = _extract_table_rows_from_html_table(table_tag)
            results.append(
                {
                    "path": header_path,
                    "pmcid": f"PMC{pmc_id}" if pmc_id else "",
                    "doi": "",
                    "url": (article_url or (f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmc_id}/" if pmc_id else "")),
                    "rows": rows,
                }
            )
    return results


def parse_html_metadata(html: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    pmid = None
    doi = None
    # Try common meta tags
    pmid_meta = soup.find("meta", attrs={"name": re.compile("pmid", re.I)})
    doi_meta = soup.find("meta", attrs={"name": re.compile("doi", re.I)})
    if pmid_meta and pmid_meta.get("content"):
        pmid = pmid_meta["content"].strip()
    if doi_meta and doi_meta.get("content"):
        doi = doi_meta["content"].strip()
    # Also try data- attributes on article container
    main = soup.find(id="maincontent")
    if main:
        if not pmid and main.has_attr("data-pmid"):
            pmid = main["data-pmid"].strip()
        if not doi and main.has_attr("data-doi"):
            doi = main["data-doi"].strip()
    return {"pmid": pmid, "doi": doi}


