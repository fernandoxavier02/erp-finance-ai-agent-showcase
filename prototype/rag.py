"""RAG - toy retrieval over a synthetic finance policy manual.

A deterministic bag-of-words embedding (5-char prefix "stemming" + term
counts over a fixed vocabulary) plus brute-force cosine similarity. No
external model, no network, no vector database - pure standard library.

# PRODUCTION: replace toy embedding with sentence-transformers (MiniLM) + FAISS
"""

import math
import re
from typing import Dict, List

from models import PolicyChunk

_POLICY_DOC = "Finance Operations Policy Manual (synthetic)"

# Each tuple becomes one retrievable PolicyChunk.
_POLICY_SECTIONS = [
    (
        "AP Invoice Approval Thresholds",
        "Accounts payable invoices up to USD 5,000 that carry a matching purchase "
        "order may be auto-approved by the system. Invoices above USD 5,000, or any "
        "invoice without a purchase order, require manual approval by a finance manager.",
    ),
    (
        "Bank Reconciliation",
        "Bank statements are reconciled against the general ledger every business day. "
        "Any unmatched item above USD 1,000 must be investigated within 48 hours.",
    ),
    (
        "Journal Entry Controls",
        "Every journal entry posting to the general ledger requires review and explicit "
        "approval by an authorized human before it is committed. Automated agents may "
        "draft entries but must never post them without human sign-off.",
    ),
    (
        "Vendor Master Data",
        "New vendors must be validated against the registered tax id and approved by "
        "procurement before any invoice can be paid.",
    ),
    (
        "Budget Variance",
        "Cost center owners must explain any monthly budget variance greater than 10 "
        "percent or USD 25,000, whichever is lower, in the monthly close commentary.",
    ),
]

CHUNKS: List[PolicyChunk] = [
    PolicyChunk(doc=_POLICY_DOC, section=section, text=text)
    for section, text in _POLICY_SECTIONS
]


def _tokens(text: str) -> List[str]:
    """Lowercase word tokens, light 5-char prefix stemmer (toy)."""
    return [w[:5] for w in re.findall(r"[a-z0-9]+", text.lower())]


# Fixed vocabulary built once from the policy corpus.
_VOCAB: Dict[str, int] = {}
for _chunk in CHUNKS:
    for _tok in _tokens(_chunk.text):
        _VOCAB.setdefault(_tok, len(_VOCAB))


def _embed(text: str) -> List[float]:
    """Deterministic term-count vector over the fixed vocabulary."""
    vec = [0.0] * len(_VOCAB)
    for tok in _tokens(text):
        idx = _VOCAB.get(tok)
        if idx is not None:
            vec[idx] += 1.0
    return vec


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# Pre-embed the corpus once (brute-force index).
_CHUNK_VECTORS = [(_chunk, _embed(_chunk.text)) for _chunk in CHUNKS]


def retrieve(query: str, k: int = 1) -> List[Dict[str, object]]:
    """Return the top-k most similar policy chunks for the query."""
    q = _embed(query)
    scored = [
        {"section": chunk.section, "text": chunk.text, "score": round(_cosine(q, vec), 4)}
        for chunk, vec in _CHUNK_VECTORS
    ]
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:k]
