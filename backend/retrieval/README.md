## Retrieval (Hybrid: dense + sparse)

Query Qdrant Cloud with both dense and sparse signals, fused with Reciprocal Rank Fusion (RRF).

### Requirements

Use the same venv as the project. Ensure (fastembed-enabled client so Document encoding works server-side):
```bash
pip install "qdrant-client[fastembed]>=1.14.2" python-dotenv
```

### Qdrant credentials

Use `.env` at repo root:
```
QDRANT_URL=https://<your-cluster>.cloud.qdrant.io
QDRANT_API_KEY=<your-api-key>
```

### Run

Basic hybrid query:
```bash
source .venv/bin/activate
PYTHONPATH=$PWD python -m retrieval.query_cli \
  --collection nasa_corpus_v1 \
  --query "What are microgravity effects on stem cells?" \
  --top-k 10
```

Options:
- `--dense-model` (default `sentence-transformers/all-MiniLM-L6-v2`)
- `--sparse-model` (default `prithivida/Splade_PP_en_v1`)
- `--top-k` (default 10)


