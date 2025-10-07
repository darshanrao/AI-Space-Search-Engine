from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

import click
import json
import hashlib

from .fetch import get_article
from .parse import (
    parse_jats_sections,
    parse_html_main_text,
    parse_jats_metadata,
    parse_html_metadata,
    parse_jats_figures,
    parse_html_figures,
    parse_jats_tables,
    parse_html_tables,
    parse_html_main_text_loose,
    parse_html_main_text_robust,
)
from .clean import clean_blocks, clean_text, should_exclude_path


@click.group()
def cli() -> None:
    """CLI for parsing PMC articles according to dense-friendly rules."""


@cli.command()
@click.argument("url", type=str)
@click.option("--out", "out_path", type=click.Path(path_type=Path), required=True, help="Output txt file")
def parse(url: str, out_path: Path) -> None:
    art = get_article(url)
    if art.source == "none":
        click.echo("Failed to fetch article", err=True)
        raise SystemExit(2)
    if art.jats_xml:
        blocks = parse_jats_sections(art.jats_xml)
    else:
        blocks = parse_html_main_text(art.html or "")
    cleaned = clean_blocks(blocks)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(cleaned), encoding="utf-8")
    click.echo(f"Wrote {len(cleaned)} blocks to {out_path}")


@cli.command()
@click.argument("csv_path", type=click.Path(exists=True, path_type=Path))
@click.option("--limit", type=int, default=1, help="Number of rows to process")
@click.option("--outdir", type=click.Path(path_type=Path), default=Path("outputs"))
def parse_csv(csv_path: Path, limit: int, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            url = row.get("Link") or row.get("url") or row.get("URL")
            title = row.get("Title") or f"article_{i}"
            if not url:
                continue
            safe_title = "".join(c for c in title if c.isalnum() or c in ("_", "-", " ")).strip().replace(" ", "_")
            out_path = outdir / f"{safe_title}.txt"
            art = get_article(url)
            if art.source == "none":
                click.echo(f"Failed to fetch: {url}", err=True)
                continue
            blocks = parse_jats_sections(art.jats_xml) if art.jats_xml else parse_html_main_text(art.html or "")
            cleaned = clean_blocks(blocks)
            out_path.write_text("\n".join(cleaned), encoding="utf-8")
            click.echo(f"[{i+1}] {title} -> {out_path} ({len(cleaned)} blocks)")


@cli.command("parse-csv-sentences")
@click.argument("csv_path", type=click.Path(exists=True, path_type=Path))
@click.option("--limit", type=int, default=1, help="Number of rows to process")
@click.option("--outdir", type=click.Path(path_type=Path), default=Path("outputs_sentence"))
@click.option("--loose", is_flag=True, default=False, help="Looser HTML parsing and shorter min length")
@click.option("--robust", is_flag=True, default=False, help="Robust parsing for irregular pages")
def parse_csv_sentences(csv_path: Path, limit: int, outdir: Path, loose: bool, robust: bool) -> None:
    try:
        from chonkie import SentenceChunker  # Lazy import to respect active environment
    except ImportError as exc:
        click.echo("Missing dependency 'chonkie'. Please install it in the active environment.", err=True)
        raise SystemExit(3) from exc
    outdir.mkdir(parents=True, exist_ok=True)
    chunker = SentenceChunker(
        tokenizer_or_token_counter="character",
        chunk_size=1058,
        chunk_overlap=128,
        min_sentences_per_chunk=1,
    )
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            url = row.get("Link") or row.get("url") or row.get("URL")
            title = row.get("Title") or f"article_{i}"
            if not url:
                continue
            safe_title = "".join(c for c in title if c.isalnum() or c in ("_", "-", " ")).strip().replace(" ", "_")
            art = get_article(url)
            if art.source == "none":
                click.echo(f"Failed to fetch: {url}", err=True)
                continue
            # Sections
            if art.jats_xml:
                sections = parse_jats_sections(art.jats_xml)
                # Auto-robust if few/none
                if len(sections) < 2 and art.html:
                    sections = parse_html_main_text_robust(art.html)
            else:
                # Choose best HTML mode
                sections = parse_html_main_text(art.html or "")
                if len(sections) < 2:
                    sections = parse_html_main_text_loose(art.html or "")
                if len(sections) < 2:
                    sections = parse_html_main_text_robust(art.html or "")
            # Metadata
            meta = parse_jats_metadata(art.jats_xml) if art.jats_xml else parse_html_metadata(art.html or "")
            pmcid = f"PMC{art.pmc_id}" if art.pmc_id else ""
            pmid = meta.get("pmid") or ""
            doi = meta.get("doi") or ""

            # Helpers for IDs and fields
            def make_section(header: str) -> str:
                return header.split(" — ", 1)[1] if " — " in header else header

            def make_id(section_path: str, pmcid_val: str, text_val: str) -> str:
                basis = f"{pmcid_val}\n{section_path}\n{text_val}".encode("utf-8")
                h = hashlib.sha1(basis).hexdigest()[:8]
                # compact section slug
                sec = make_section(section_path)
                sec_slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in sec).strip("-")
                return f"{pmcid_val}:{sec_slug}:{h}"

            def provenance(url_val: str, pmcid_val: str, pmid_val: str, doi_val: str, image: str | None = None) -> str:
                base = f"{url_val} | {pmcid_val} | PMID:{pmid_val} | DOI:{doi_val}"
                return base + (f" | {image}" if image else "")

            # Build chunks per section, then sentence-chunk inside
            chunks_written = 0
            out_base = outdir / f"{safe_title}"
            out_jsonl = out_base.with_suffix(".jsonl")
            out_jsonl.parent.mkdir(parents=True, exist_ok=True)
            # truncate existing file
            out_jsonl.write_text("", encoding="utf-8")
            for path, section_text in sections:
                if should_exclude_path(path):
                    continue
                cleaned = clean_text(section_text, min_len=5 if (loose or robust) else 20)
                if not cleaned:
                    continue
                # Sentence-level chunks
                sentence_chunks = chunker.chunk(cleaned)
                if not sentence_chunks:
                    continue
                for idx, sc in enumerate(sentence_chunks, start=1):
                    body = sc.text
                    if len(body) < 20 and not body.startswith("[FIGURE CAPTION"):
                        continue
                    section_field = make_section(path)
                    prov = provenance(url, pmcid, pmid, doi)
                    text_field = f"{path}\n{prov}\n{body}"
                    record = {
                        "id": make_id(path, pmcid, body),
                        "kind": "paragraph",
                        "section": section_field,
                        "section_path": path,
                        "text": text_field,
                        "url": url,
                        "pmcid": pmcid,
                        "pmid": pmid,
                        "doi": doi,
                    }
                    with out_jsonl.open("a", encoding="utf-8") as of:
                        of.write(json.dumps(record, ensure_ascii=False) + "\n")
                    chunks_written += 1

            # Fallback: catchall when very low yield in robust mode
            if chunks_written < 10 and (art.html or ""):
                from bs4 import BeautifulSoup as _BS
                soup = _BS(art.html or "", "lxml")
                main = soup.find("div", id="maincontent") or soup
                catchall = main.get_text(" ", strip=True)
                cleaned_catchall = clean_text(catchall, min_len=50)
                if cleaned_catchall:
                    # chunk catchall as additional paragraphs
                    sentence_chunks = chunker.chunk(cleaned_catchall)
                    header = f"{title} — Body (Catchall)"
                    for sc in sentence_chunks:
                        body = sc.text
                        if len(body) < 20:
                            continue
                        section_field = make_section(header)
                        prov = provenance(url, pmcid, pmid, doi)
                        text_field = f"{header}\n{prov}\n{body}"
                        record = {
                            "id": make_id(header, pmcid, body),
                            "kind": "paragraph",
                            "section": section_field,
                            "section_path": header,
                            "text": text_field,
                            "url": url,
                            "pmcid": pmcid,
                            "pmid": pmid,
                            "doi": doi,
                        }
                        with out_jsonl.open("a", encoding="utf-8") as of:
                            of.write(json.dumps(record, ensure_ascii=False) + "\n")
                        chunks_written += 1

            # Figure chunks (no chonkie). Always append after text chunks
            figs = []
            if art.jats_xml:
                figs = parse_jats_figures(art.jats_xml, art.url, art.pmc_id, html_for_cdn=art.html)
                if not figs and art.html:
                    figs = parse_html_figures(art.html or "", art.url, art.pmc_id)
            else:
                figs = parse_html_figures(art.html or "", art.url, art.pmc_id)
            for fig in figs:
                header = fig["path"]
                fig_pmcid = fig["pmcid"]
                fig_doi = fig["doi"]
                fig_url = fig["url"]
                img = fig["img"]
                fig_id = fig["fig_id"]
                caption = fig["caption"]
                section_field = make_section(header)
                prov = provenance(fig_url, fig_pmcid, pmid, fig_doi, image=img if img else None)
                text_field = f"{header}\n{prov}\n{caption}"
                record = {
                    "id": make_id(header, fig_pmcid, caption or ""),
                    "kind": "caption",
                    "section": section_field,
                    "section_path": header,
                    "text": text_field,
                    "url": fig_url,
                    "pmcid": fig_pmcid,
                    "pmid": pmid,
                    "doi": fig_doi,
                    "image_hrefs": [img] if img else [],
                }
                with out_jsonl.open("a", encoding="utf-8") as of:
                    of.write(json.dumps(record, ensure_ascii=False) + "\n")
                chunks_written += 1

            # Table chunks (no chonkie)
            tables = []
            if art.jats_xml:
                tables = parse_jats_tables(art.jats_xml, art.url, art.pmc_id)
                if not tables and art.html:
                    tables = parse_html_tables(art.html or "", art.url, art.pmc_id)
            else:
                tables = parse_html_tables(art.html or "", art.url, art.pmc_id)
            for tbl in tables:
                header = tbl["path"]
                tbl_pmcid = tbl["pmcid"]
                tbl_doi = tbl["doi"]
                tbl_url = tbl["url"]
                rows = tbl["rows"]
                section_field = make_section(header)
                prov = provenance(tbl_url, tbl_pmcid, pmid, tbl_doi)
                # render rows to text (tab-separated rows)
                rows_text = "\n".join("\t".join(r) for r in rows)
                text_field = f"{header}\n{prov}\n{rows_text}" if rows_text else f"{header}\n{prov}"
                record = {
                    "id": make_id(header, tbl_pmcid, rows_text),
                    "kind": "table",
                    "section": section_field,
                    "section_path": header,
                    "text": text_field,
                    "url": tbl_url,
                    "pmcid": tbl_pmcid,
                    "pmid": pmid,
                    "doi": tbl_doi,
                }
                with out_jsonl.open("a", encoding="utf-8") as of:
                    of.write(json.dumps(record, ensure_ascii=False) + "\n")
                chunks_written += 1

            click.echo(f"[{i+1}] {title} -> {outdir}/{safe_title}.txt ({chunks_written} chunks)")


if __name__ == "__main__":
    cli()


