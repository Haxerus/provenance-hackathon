import os

ROOT = os.environ.get(
    "PROVENANCE_ROOT",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

PUBLIC_KEYS_PATH = os.environ.get(
    "PUBLIC_KEYS_PATH",
    os.path.join(ROOT, "registry", "supplier_public_keys.json"),
)
PRIVATE_KEYS_PATH = os.environ.get(
    "PRIVATE_KEYS_PATH",
    os.path.join(ROOT, "private_keys", "supplier_private_keys.json"),
)
ANCHOR_PATH = os.environ.get(
    "ANCHOR_PATH",
    os.path.join(ROOT, "registry", "anchor_registry.json"),
)
TRAINING_CORPUS_PATH = os.environ.get(
    "TRAINING_CORPUS_PATH",
    os.path.join(ROOT, "training_corpus.jsonl"),
)
MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "model", "baseline_stats.json"),
)
STORE_BACKEND = os.environ.get("STORE_BACKEND", "memory")
SQLITE_PATH = os.environ.get("SQLITE_PATH", os.path.join(ROOT, "provenance.db"))
SEED = os.environ.get("SEED", "none")
