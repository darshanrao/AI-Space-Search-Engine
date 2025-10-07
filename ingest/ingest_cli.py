from __future__ import annotations

import glob
import json
from pathlib import Path
from typing import Dict, Iterable, List

import click
import numpy as np
from tqdm import tqdm

from .encoders import DenseEncoder, DenseEncoderConfig, SpladeEncoder, SpladeEncoderConfig
from .qdrant_utils import QdrantConfig, connect, ensure_collection, upsert_batch


def iter_jsonl_records(path: Path) -> Iterable[Dict[str, object]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


@click.command()
@click.option("--input-dir", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--collection", type=str, required=True)
@click.option("--batch-size", type=int, default=16)
@click.option("--sparse-top-k", type=int, default=200)
@click.option("--dense-model", type=str, default="BAAI/bge-small-en-v1.5")
@click.option("--sparse-model", type=str, default="prithivida/Splade_PP_en_v1")
@click.option("--start-index", type=int, default=0, help="Start from this file index (sorted by name)")
def main(input_dir: Path, collection: str, batch_size: int, sparse_top_k: int, dense_model: str, sparse_model: str, start_index: int) -> None:
    client = connect(QdrantConfig(collection=collection))
    ensure_collection(client, QdrantConfig(collection=collection))

    dense = DenseEncoder(DenseEncoderConfig(model_name=dense_model))
    splade = SpladeEncoder(SpladeEncoderConfig(model_name=sparse_model, top_k=sparse_top_k))

    files = sorted(Path(input_dir).glob("*.jsonl"))
    click.echo(f"Found {len(files)} jsonl files in {input_dir}")
    if start_index > 0:
        files = files[start_index:]
        click.echo(f"Resuming from index {start_index} -> {len(files)} files remaining")

    buffer_records: List[Dict[str, object]] = []
    buffer_texts: List[str] = []

    def flush() -> None:
        if not buffer_records:
            return
        dvecs = dense.encode(buffer_texts, batch_size=batch_size)
        svecs = splade.encode(buffer_texts, batch_size=max(1, batch_size // 2))
        upsert_batch(
            client,
            QdrantConfig(collection=collection),
            buffer_records,
            dvecs,
            svecs,
            upload_batch_size=max(16, batch_size),
        )
        buffer_records.clear()
        buffer_texts.clear()

    for fpath in tqdm(files, desc="files"):
        for rec in iter_jsonl_records(fpath):
            text = str(rec.get("text") or "")
            if not text:
                continue
            buffer_records.append(rec)
            buffer_texts.append(text)
            if len(buffer_records) >= batch_size:
                flush()
        flush()

    click.echo("Done.")


if __name__ == "__main__":
    main()


