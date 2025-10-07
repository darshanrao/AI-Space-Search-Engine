from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
import uuid
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from dotenv import load_dotenv


DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"


@dataclass
class QdrantConfig:
    url: str = "http://localhost:6333"
    api_key: Optional[str] = None
    collection: str = "nasa_corpus_v1"
    dense_dim: int = 384  # bge-small-en-v1.5 output dim


def connect(cfg: QdrantConfig) -> QdrantClient:
    # Load .env at runtime so env vars are picked up without restarting
    load_dotenv()
    url = os.environ.get("QDRANT_URL", cfg.url)
    api_key = os.environ.get("QDRANT_API_KEY", cfg.api_key)
    # Increase timeout to reduce ReadTimeouts on larger uploads
    return QdrantClient(url=url, api_key=api_key, timeout=120.0)


def ensure_collection(client: QdrantClient, cfg: QdrantConfig) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if cfg.collection in existing:
        return
    client.create_collection(
        collection_name=cfg.collection,
        vectors_config={
            DENSE_VECTOR_NAME: rest.VectorParams(size=cfg.dense_dim, distance=rest.Distance.COSINE)
        },
        # Enable named sparse vector per docs
        sparse_vectors_config={SPARSE_VECTOR_NAME: rest.SparseVectorParams()},
        optimizers_config=rest.OptimizersConfigDiff(memmap_threshold=20000),
    )


def make_point_id(record: Dict[str, object]) -> str:
    """Return a Qdrant-compatible ID (UUID string). Deterministic from record content."""
    basis = None
    rid = record.get("id")
    if isinstance(rid, str) and rid:
        basis = rid
    else:
        # fallback: text
        basis = str(record.get("text") or "")
    # Deterministic UUID5 from basis
    return str(uuid.uuid5(uuid.NAMESPACE_URL, basis))


def to_sparse_vector(term_to_weight: Dict[int, float]) -> rest.SparseVector:
    if not term_to_weight:
        return rest.SparseVector(indices=[], values=[])
    # ensure sorted indices for reproducibility
    items = sorted(term_to_weight.items())
    indices = [i for i, _ in items]
    values = [float(v) for _, v in items]
    return rest.SparseVector(indices=indices, values=values)


def upsert_batch(
    client: QdrantClient,
    cfg: QdrantConfig,
    records: List[Dict[str, object]],
    dense: np.ndarray,
    sparse: List[Dict[int, float]],
    upload_batch_size: int = 64,
    max_retries: int = 5,
    retry_backoff_sec: float = 2.0,
) -> None:
    assert len(records) == len(dense) == len(sparse)
    # chunked upload via upload_collection to reduce request size
    import time
    n = len(records)
    for start in range(0, n, upload_batch_size):
        end = min(start + upload_batch_size, n)
        vectors_named = []
        payloads: List[Dict[str, object]] = []
        ids: List[str] = []
        for rec, dvec, sdict in zip(records[start:end], dense[start:end], sparse[start:end]):
            vectors_named.append({
                DENSE_VECTOR_NAME: dvec.tolist(),
                SPARSE_VECTOR_NAME: to_sparse_vector(sdict),
            })
            payloads.append(dict(rec))
            ids.append(make_point_id(rec))

        attempt = 0
        while True:
            try:
                client.upload_collection(
                    collection_name=cfg.collection,
                    vectors=vectors_named,
                    payload=payloads,
                    ids=ids,
                    batch_size=max(1, min(32, upload_batch_size)),
                )
                break
            except Exception:
                attempt += 1
                if attempt >= max_retries:
                    raise
                time.sleep(retry_backoff_sec * attempt)


