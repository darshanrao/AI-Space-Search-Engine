## Ingest: Dense + Sparse embeddings to Qdrant

This module reads parser JSONL chunks and stores both dense and sparse vectors in a single Qdrant collection.

What it does:
- Dense: `BAAI/bge-small-en-v1.5` via SentenceTransformers
- Sparse: SPLADE `prithivida/Splade_PP_en_v1` (MaskedLM, log1p(ReLU) + max-pooling), top-k pruning
- Payload: preserves the original fields from the JSONL records

### Requirements

- Python 3.11+
- Qdrant running locally or remotely
- Packages (install into your active venv):
```bash
pip install qdrant-client sentence-transformers transformers torch scipy numpy tqdm ujson
```

If you run Apple Silicon, consider installing torch from the official instructions.

### Qdrant

- Cloud: put credentials in a `.env` at repo root (auto-loaded at runtime):
  - `QDRANT_URL=https://<your-cluster>.cloud.qdrant.io`
  - `QDRANT_API_KEY=<your-api-key>`
- Local: if no `.env` is present, defaults to `http://localhost:6333` without an API key.

### Run

Compute embeddings for a directory of JSONL files (e.g., `outputs_sentence_robust`) and upsert to Qdrant:
```bash
source .venv/bin/activate
PYTHONPATH=$PWD python -m ingest.ingest_cli \
  --input-dir outputs_sentence_robust \
  --collection nasa_corpus_v1 \
  --batch-size 8 \
  --sparse-top-k 200
```

Resume from a specific file index (sorted by filename) if a long run was interrupted:
```bash
PYTHONPATH=$PWD python -m ingest.ingest_cli \
  --input-dir outputs_sentence_robust \
  --collection nasa_corpus_v1 \
  --batch-size 8 \
  --sparse-top-k 200 \
  --start-index 349
```

Flags:
- `--input-dir`: directory containing `article_*.jsonl`
- `--collection`: Qdrant collection name (created if missing)
- `--batch-size`: texts per inference batch
- `--sparse-top-k`: keep top-k SPLADE terms per text
- `--dense-model`: override dense model (default `BAAI/bge-small-en-v1.5`)
- `--sparse-model`: override SPLADE model (default `prithivida/Splade_PP_en_v1`)
- `--start-index`: skip the first N files (for resuming)

### Notes

- Collection is created with named dense vector `dense` (COSINE) and named sparse vector `sparse` (per Qdrant docs).
- Point IDs are deterministic UUIDs derived from each record’s `id`/text, so re-runs upsert (overwrite) instead of duplicating.
- The client uses an increased timeout and chunked uploads with retries to reduce `ReadTimeout` errors on large batches.

### Background run (optional)

You can run long ingestions in the background and log output for monitoring:
```bash
PYTHONPATH=$PWD nohup python -m ingest.ingest_cli \
  --input-dir outputs_sentence_robust \
  --collection nasa_corpus_v1 \
  --batch-size 8 \
  --sparse-top-k 200 \
  > ingest_all.log 2>&1 & echo $! > ingest_all.pid
```
Resume after a failure from a known index:
```bash
kill $(cat ingest_all.pid) 2>/dev/null || true
PYTHONPATH=$PWD nohup python -m ingest.ingest_cli \
  --input-dir outputs_sentence_robust \
  --collection nasa_corpus_v1 \
  --batch-size 8 \
  --sparse-top-k 200 \
  --start-index 349 \
  > ingest_resume.log 2>&1 & echo $! > ingest_resume.pid
```


