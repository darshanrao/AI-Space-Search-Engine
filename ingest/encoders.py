from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForMaskedLM, AutoTokenizer


@dataclass
class DenseEncoderConfig:
    model_name: str = "BAAI/bge-small-en-v1.5"
    device: str | None = None  # "cuda", "mps", "cpu"


class DenseEncoder:
    def __init__(self, cfg: DenseEncoderConfig) -> None:
        self.model = SentenceTransformer(cfg.model_name, device=cfg.device or self._auto_device())

    @staticmethod
    def _auto_device() -> str:
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        return self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True, normalize_embeddings=True)


@dataclass
class SpladeEncoderConfig:
    model_name: str = "prithivida/Splade_PP_en_v1"
    device: str | None = None
    top_k: int = 200  # keep top-k terms per doc


class SpladeEncoder:
    """Minimal SPLADE scorer that returns CSR-like sparse dicts {term_id: weight}."""

    def __init__(self, cfg: SpladeEncoderConfig) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(cfg.model_name)
        self.model.eval()
        self.device = cfg.device or self._auto_device()
        self.model.to(self.device)
        self.top_k = cfg.top_k

    @staticmethod
    def _auto_device() -> str:
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    @torch.no_grad()
    def encode(self, texts: List[str], batch_size: int = 8) -> List[Dict[int, float]]:
        results: List[Dict[int, float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            toks = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=256,
                return_tensors="pt",
            ).to(self.device)
            logits = self.model(**toks).logits  # [B, L, V]
            # log1p(ReLU) per SPLADE; then max-pool over tokens
            relu = torch.relu(logits)
            scores = torch.log1p(relu)  # [B, L, V]
            pooled, _ = torch.max(scores, dim=1)  # [B, V]
            pooled = pooled.cpu()
            for row in pooled:
                values, indices = torch.topk(row, k=min(self.top_k, row.numel()))
                sparse: Dict[int, float] = {}
                for v, idx in zip(values.tolist(), indices.tolist()):
                    if v > 0:
                        sparse[int(idx)] = float(v)
                results.append(sparse)
        return results

    def vocab(self) -> List[str]:
        # id -> token string
        vocab_size = self.tokenizer.vocab_size
        id_to_token = [""] * vocab_size
        for tok, idx in self.tokenizer.get_vocab().items():
            if idx < vocab_size:
                id_to_token[idx] = tok
        return id_to_token


