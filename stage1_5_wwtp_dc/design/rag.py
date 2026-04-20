"""Static RAG over the design_wiki/ knowledge base.

Two implementations:

* **default** — pure-numpy TF-IDF. No external deps (`numpy` only). Good
  enough for our 15-file corpus and fast to initialize. This is what the
  MVP ships with.

* **upgraded** — sentence-transformers + FAISS. Enabled by setting
  ``EF_RAG_BACKEND=st+faiss`` in the environment **and** having both
  packages installed. Gives semantic search (better recall on paraphrased
  queries) at the cost of ~90 MB model download on first run.

The public surface is one class: ``Retriever``. Construct it with a wiki
path, call ``.retrieve(query, k=3)``, get back a list of hits. That's it.

Each hit is a dict:

    {"path": "pv/single_axis_tracker.md",
     "title": "Single-axis tracking",
     "score": 0.43,
     "text": "...the full file body...",
     "excerpt": "...200-char snippet around the best-matching line..."}

Contract for callers
--------------------
* ``retrieve`` is deterministic given the same corpus + query.
* If the corpus is empty, returns an empty list (never raises).
* Scores are cosine similarities in [0, 1].
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import numpy as np


WIKI_DIR_DEFAULT = (
    Path(__file__).resolve().parent.parent / "design_wiki"
)

# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------
@dataclass
class WikiDoc:
    path: str          # relative to wiki root, e.g. "pv/single_axis_tracker.md"
    title: str
    text: str          # the original, clean markdown body (what we return to the LLM)
    index_text: str = ""  # the title+filename-boosted body (what the index sees)

    def __post_init__(self):
        if not self.index_text:
            self.index_text = self.text


def _load_wiki(wiki_dir: Path) -> List[WikiDoc]:
    """Walk wiki_dir, load every .md file (except _index.md), parse title.

    Note on TF-IDF indexing: we prepend the title + filename 3 times at the
    start of each doc. This gives title/filename tokens ~3x weight in the
    bag-of-words representation without needing a separate boost factor.
    Empirically this fixes confusable queries like "dual axis tracker cost"
    that would otherwise match `single_axis_tracker.md` because the latter
    cross-references dual-axis.
    """
    docs: List[WikiDoc] = []
    if not wiki_dir.exists():
        return docs
    for path in sorted(wiki_dir.rglob("*.md")):
        if path.name.startswith("_"):
            continue  # skip _index.md and any other underscore-prefixed meta files
        raw = path.read_text()
        title = _extract_title(raw) or path.stem.replace("_", " ").title()
        rel = path.relative_to(wiki_dir).as_posix()
        # Filename-as-keyword boost (e.g. "dual_axis" -> tokens "dual", "axis").
        fname_keyword = path.stem.replace("_", " ").replace("-", " ")
        indexed = f"{title}\n{fname_keyword}\n{title}\n{fname_keyword}\n{raw}"
        docs.append(WikiDoc(path=rel, title=title, text=raw, index_text=indexed))
    return docs


def _extract_title(text: str) -> Optional[str]:
    """Return the first H1 (`# ...`) header in a markdown body, or None."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


# ---------------------------------------------------------------------------
# Tokenization — shared between backends
# ---------------------------------------------------------------------------
_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_\-]+")

# Light English stopword list. We intentionally keep technical terms like
# "tier", "rate", "peak" — they're semantically meaningful in our corpus.
_STOPWORDS = frozenset(
    """a an the and or but if then else as of in on at to for with by
    is are was were be been being have has had do does did will would
    can could should may might this that these those it its they them
    we you your our their which what who how when where why because
    not no nor so than too very just""".split()
)


def _tokenize(text: str) -> List[str]:
    return [
        t.lower() for t in _TOKEN_RE.findall(text) if t.lower() not in _STOPWORDS
    ]


# ---------------------------------------------------------------------------
# TF-IDF backend (default, pure numpy)
# ---------------------------------------------------------------------------
class _TFIDFIndex:
    """Tiny TF-IDF + cosine-similarity retrieval. Enough for 10–100 docs."""

    def __init__(self, docs: List[WikiDoc]):
        self.docs = docs
        self.vocab: Dict[str, int] = {}
        self._build()

    def _build(self) -> None:
        if not self.docs:
            self.matrix = np.zeros((0, 0))
            self.idf = np.zeros(0)
            return

        # Pass 1: build vocab. We use index_text (title+filename-boosted) so
        # title keywords carry ~3x weight; the original text is what callers
        # get back in the hit payload.
        doc_tokens = [_tokenize(d.index_text) for d in self.docs]
        for tokens in doc_tokens:
            for tok in tokens:
                if tok not in self.vocab:
                    self.vocab[tok] = len(self.vocab)

        V = len(self.vocab)
        N = len(self.docs)

        # Pass 2: term frequency matrix (docs × vocab).
        tf = np.zeros((N, V), dtype=np.float32)
        for i, tokens in enumerate(doc_tokens):
            for tok in tokens:
                tf[i, self.vocab[tok]] += 1.0
        # L1-normalize (relative frequency within each doc).
        row_sums = tf.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        tf = tf / row_sums

        # Document frequency + smoothed IDF.
        df = (tf > 0).sum(axis=0)
        idf = np.log((1.0 + N) / (1.0 + df)) + 1.0
        self.idf = idf.astype(np.float32)

        # TF-IDF matrix, then L2-normalize for cosine similarity.
        tfidf = tf * self.idf
        norms = np.linalg.norm(tfidf, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.matrix = (tfidf / norms).astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Map a query to the same TF-IDF space."""
        V = len(self.vocab)
        if V == 0:
            return np.zeros(0, dtype=np.float32)
        vec = np.zeros(V, dtype=np.float32)
        for tok in _tokenize(query):
            idx = self.vocab.get(tok)
            if idx is not None:
                vec[idx] += 1.0
        s = vec.sum()
        if s == 0:
            return vec
        vec = vec / s * self.idf
        n = np.linalg.norm(vec)
        return vec if n == 0 else vec / n

    def similarities(self, query_vec: np.ndarray) -> np.ndarray:
        if self.matrix.size == 0 or query_vec.size == 0:
            return np.zeros(len(self.docs))
        # Cosine sim = dot product since both matrix and query are L2-normalized.
        return self.matrix @ query_vec


# ---------------------------------------------------------------------------
# Optional sentence-transformers + FAISS backend
# ---------------------------------------------------------------------------
class _STIndex:
    """Sentence-transformers embeddings + FAISS inner-product search.

    Lazily imports its dependencies so we don't pay the cost if the user
    sticks with the TF-IDF default.
    """

    def __init__(self, docs: List[WikiDoc], model_name: str):
        try:
            from sentence_transformers import SentenceTransformer  # noqa: F401
            import faiss  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "EF_RAG_BACKEND=st+faiss requires sentence-transformers and faiss-cpu installed"
            ) from exc

        from sentence_transformers import SentenceTransformer
        import faiss

        self.docs = docs
        self.model = SentenceTransformer(model_name)
        if not docs:
            self.index = None
            self.embeddings = np.zeros((0, 0))
            return

        texts = [d.text for d in docs]
        embeds = self.model.encode(texts, normalize_embeddings=True)
        self.embeddings = np.asarray(embeds, dtype=np.float32)
        self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
        self.index.add(self.embeddings)

    def embed_query(self, query: str) -> np.ndarray:
        vec = self.model.encode([query], normalize_embeddings=True)
        return np.asarray(vec, dtype=np.float32)[0]

    def similarities(self, query_vec: np.ndarray) -> np.ndarray:
        if self.index is None or query_vec.size == 0:
            return np.zeros(len(self.docs))
        D, _ = self.index.search(query_vec[None, :], len(self.docs))
        # D is ordered; re-scatter to match docs[] order.
        # For a simple corpus (<100 docs) it's fine to just compute directly:
        return (self.embeddings @ query_vec).astype(np.float32)


# ---------------------------------------------------------------------------
# Public class: Retriever
# ---------------------------------------------------------------------------
class Retriever:
    """Static RAG retriever over the wiki. Instantiate once, reuse."""

    def __init__(
        self,
        wiki_dir: Optional[Path] = None,
        backend: Optional[str] = None,
        st_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.wiki_dir = wiki_dir or WIKI_DIR_DEFAULT
        self.docs = _load_wiki(self.wiki_dir)

        chosen = (backend or os.getenv("EF_RAG_BACKEND", "tfidf")).lower()
        if chosen == "st+faiss":
            self._impl = _STIndex(self.docs, model_name=st_model)
            self.backend = "st+faiss"
        else:
            self._impl = _TFIDFIndex(self.docs)
            self.backend = "tfidf"

    def retrieve(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Top-k most relevant wiki docs for the query."""
        if not self.docs:
            return []

        query_vec = self._impl.embed_query(query)
        sims = self._impl.similarities(query_vec)
        if sims.size == 0:
            return []

        k = max(1, min(k, len(self.docs)))
        top_idx = np.argsort(-sims)[:k]
        hits: List[Dict[str, Any]] = []
        for i in top_idx:
            doc = self.docs[int(i)]
            score = float(sims[int(i)])
            hits.append(
                {
                    "path": doc.path,
                    "title": doc.title,
                    "score": round(score, 4),
                    "excerpt": _excerpt(doc.text, query),
                    "text": doc.text,
                }
            )
        return hits

    def __repr__(self) -> str:  # pragma: no cover — debug convenience
        return (
            f"Retriever(wiki_dir={self.wiki_dir!s}, "
            f"backend={self.backend!r}, docs={len(self.docs)})"
        )


def _excerpt(text: str, query: str, width: int = 220) -> str:
    """Return ~width chars of text centered on the best-matching line."""
    q_tokens = set(_tokenize(query))
    if not q_tokens:
        return text[:width].strip()

    best_line, best_score = "", -1
    for line in text.splitlines():
        score = sum(1 for t in _tokenize(line) if t in q_tokens)
        if score > best_score:
            best_score, best_line = score, line.strip()

    if not best_line:
        return text[:width].strip()

    idx = text.find(best_line)
    if idx < 0:
        return best_line[:width]
    half = width // 2
    lo = max(0, idx - half)
    hi = min(len(text), idx + len(best_line) + half)
    snippet = text[lo:hi].strip().replace("\n", " ")
    if lo > 0:
        snippet = "… " + snippet
    if hi < len(text):
        snippet = snippet + " …"
    return snippet


# ---------------------------------------------------------------------------
# Tool wrapping (callable as an LLM tool)
# ---------------------------------------------------------------------------
_SINGLETON: Optional[Retriever] = None


def get_retriever() -> Retriever:
    """Module-level cached retriever, so Streamlit reruns don't rebuild the index."""
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = Retriever()
    return _SINGLETON


def retrieve(query: str, k: int = 3) -> Dict[str, Any]:
    """LLM-friendly wrapper. Returns ``{query, k, hits}``."""
    r = get_retriever()
    return {
        "query": query,
        "k": k,
        "hits": r.retrieve(query, k=k),
        "backend": r.backend,
    }


TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "retrieve",
            "description": (
                "Retrieve the top-k most relevant design-wiki entries for a "
                "natural-language query. Call this BEFORE answering any "
                "question about hardware, PV, BESS, regulations, or CAPEX "
                "so the answer is grounded in the wiki."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "k": {"type": "integer",
                          "description": "Max hits to return. Default 3."},
                },
                "required": ["query"],
            },
        },
    }
]


TOOL_DISPATCH: Dict[str, Any] = {"retrieve": retrieve}
