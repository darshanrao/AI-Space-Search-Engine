from __future__ import annotations

import click
import os
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models


@click.command()
@click.option("--collection", default="nasa_corpus_v1", type=str)
@click.option("--query", required=True, type=str)
@click.option("--top-k", default=10, type=int)
@click.option("--dense-model", default="sentence-transformers/all-MiniLM-L6-v2", type=str)
@click.option("--sparse-model", default="prithivida/Splade_PP_en_v1", type=str)
def main(collection: str, query: str, top_k: int, dense_model: str, sparse_model: str) -> None:
    # Load .env from repo root and connect to Qdrant Cloud
    root = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=root / ".env", override=True)
    url = os.environ.get("QDRANT_URL")
    api_key = os.environ.get("QDRANT_API_KEY")
    client = QdrantClient(url=url, api_key=api_key, timeout=90.0)
    # Hybrid query with RRF using built-in Document wrappers per Qdrant docs
    resp = client.query_points(
        collection_name=collection,
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        prefetch=[
            models.Prefetch(
                query=models.Document(text=query, model=dense_model),
                using="dense",
            ),
            models.Prefetch(
                query=models.Document(text=query, model=sparse_model),
                using="sparse",
            ),
        ],
        limit=top_k,
        with_payload=True,
    )

    for i, pt in enumerate(resp.points, start=1):
        pl = pt.payload or {}
        text = (pl.get("text") or "").split("\n", 2)[-1]
        print(f"[{i}] score={pt.score:.4f} id={pt.id} section={pl.get('section')}\n{text[:240]}\n")


if __name__ == "__main__":
    main()


