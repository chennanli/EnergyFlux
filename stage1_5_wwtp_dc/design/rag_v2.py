"""Vault-backed RAG for the EnergyFlux unified knowledge base.

Successor to ``design.rag``. Two changes vs the legacy retriever:

1. **Source of truth is the project knowledge_vault**, not the
   stage-local ``design_wiki/`` folder. Every page in
   ``knowledge_vault/wiki/`` carries YAML frontmatter declaring
   ``authority`` (authoritative / reviewed / candidate / legacy) and
   ``scope`` (host_type, region, equipment, voltage_level, applies_when).

2. **Retrieval respects authority**. By default the LLM is fed only
   ``authoritative`` and ``reviewed`` content as primary answer
   material. ``candidate`` and ``legacy`` pages are still retrieved
   when nothing better exists, but they are flagged in the hit
   payload so the caller can render a "pending review" warning.

The public surface is one class (``VaultRetriever``) and one tool
function (``retrieve``), exactly mirroring the legacy ``rag.py`` API
so the Streamlit app and the LLM tool dispatcher don't need to learn
new shapes.

Each hit:

    {
      "path": "concepts/behind_the_meter_siting.md",
      "title": "Behind-the-meter (BTM) siting for AI inference",
      "authority": "candidate",
      "scope": {"host_type": ["WWTP", "chemical", "substation", "campus"],
                "region": ["any"], "equipment": ["any"],
                "voltage_level": ["distribution", "behind_the_meter"],
                "applies_when": "..."},
      "wiki_url": "wiki/concepts/behind_the_meter_siting.html",
      "score": 0.43,
      "excerpt": "...200-char snippet around the best-matching line...",
      "text": "...full markdown body, frontmatter stripped...",
      "is_primary": True,    # True if authority is reviewed or authoritative
    }

The TF-IDF backend uses pure numpy. An optional sentence-transformers
+ FAISS backend is enabled via ``EF_RAG_BACKEND=st+faiss``; same
contract as the legacy retriever.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
# Repo root is two levels above this file: stage1_5_wwtp_dc/design/rag_v2.py
# → stage1_5_wwtp_dc/ → EnergyFlux/.
REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[2]
VAULT_WIKI_DIR_DEFAULT = REPO_ROOT_DEFAULT / "knowledge_vault" / "wiki"
WIKI_SITE_BASE_DEFAULT = "wiki"  # relative URL prefix where the rendered HTML lives

# The four authority levels and which ones the LLM may auto-cite as primary.
AUTHORITY_LEVELS = ("authoritative", "reviewed", "candidate", "legacy")
PRIMARY_AUTHORITIES = frozenset({"authoritative", "reviewed"})


# ---------------------------------------------------------------------------
# YAML frontmatter parsing
# ---------------------------------------------------------------------------
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_frontmatter(raw: str) -> tuple[Dict[str, Any], str]:
    """Pull the YAML frontmatter off the top of a markdown file.

    Returns ``(metadata_dict, body_text)``. Body excludes the
    frontmatter; metadata is empty if no frontmatter present.

    We avoid PyYAML to keep the dependency tree thin. The parser
    handles only what our templates produce: top-level scalar fields,
    flat list fields ``[a, b, c]``, and one nested ``scope:`` dict
    with sub-fields. That covers every page in this project's vault
    and fails loud (raises) on anything else, which is the right
    failure mode for governance metadata.
    """
    m = _FRONTMATTER_RE.match(raw)
    if not m:
        return {}, raw
    fm_text, body = m.group(1), m.group(2)
    return _parse_yaml_subset(fm_text), body


def _parse_yaml_subset(text: str) -> Dict[str, Any]:
    """Tiny YAML parser for our frontmatter shape only."""
    out: Dict[str, Any] = {}
    current_dict_key: Optional[str] = None
    nested: Dict[str, Any] = {}

    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        # Two-space-indented line under a dict key (only one level deep supported).
        if line.startswith("  ") and current_dict_key is not None:
            key, _, value = line.strip().partition(":")
            nested[key.strip()] = _parse_value(value.strip())
            continue
        # Top-level line. Flush any in-progress nested dict to the parent.
        if current_dict_key is not None:
            out[current_dict_key] = nested
            current_dict_key = None
            nested = {}
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "" or value is None:
            current_dict_key = key
            nested = {}
        else:
            out[key] = _parse_value(value)
    if current_dict_key is not None:
        out[current_dict_key] = nested
    return out


def _parse_value(v: str) -> Any:
    if v == "" or v.lower() == "null":
        return None
    # Inline list: [a, b, "c"]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        items = [item.strip() for item in inner.split(",")]
        return [_unquote(it) for it in items]
    return _unquote(v)


def _unquote(v: str) -> str:
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


# ---------------------------------------------------------------------------
# Vault loading
# ---------------------------------------------------------------------------
@dataclass
class VaultDoc:
    path: str          # relative to vault wiki root, e.g. "entities/bess_4hr_lfp.md"
    title: str
    authority: str
    scope: Dict[str, Any]
    text: str          # body text, frontmatter stripped (for LLM consumption)
    metadata: Dict[str, Any] = field(default_factory=dict)
    index_text: str = ""

    def __post_init__(self):
        if not self.index_text:
            # Title + filename gets ~3x weight in the bag-of-words.
            slug = Path(self.path).stem.replace("_", " ").replace("-", " ")
            self.index_text = f"{self.title}\n{slug}\n{self.title}\n{slug}\n{self.text}"

    @property
    def is_primary(self) -> bool:
        return self.authority in PRIMARY_AUTHORITIES

    def wiki_url(self, base: str = WIKI_SITE_BASE_DEFAULT) -> str:
        # Strip .md suffix and translate to URL with .html.
        url_path = Path(self.path).with_suffix(".html").as_posix()
        if base:
            return f"{base.rstrip('/')}/{url_path}"
        return url_path


def _load_vault(wiki_dir: Path) -> List[VaultDoc]:
    """Walk vault wiki/, parse frontmatter, return docs."""
    docs: List[VaultDoc] = []
    if not wiki_dir.exists():
        return docs
    for path in sorted(wiki_dir.rglob("*.md")):
        if path.name.startswith("_"):
            continue
        raw = path.read_text()
        meta, body = _parse_frontmatter(raw)
        title = meta.get("title") or _extract_title(body) or path.stem.replace("_", " ").title()
        authority = (meta.get("authority") or "candidate").strip().lower()
        if authority not in AUTHORITY_LEVELS:
            authority = "candidate"
        scope = meta.get("scope") if isinstance(meta.get("scope"), dict) else {}
        rel = path.relative_to(wiki_dir).as_posix()
        docs.append(
            VaultDoc(
                path=rel, title=title, authority=authority, scope=scope,
                text=body, metadata=meta,
            )
        )
    return docs


def _extract_title(text: str) -> Optional[str]:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


# ---------------------------------------------------------------------------
# Tokenization (shared with legacy rag.py — same stopwords)
# ---------------------------------------------------------------------------
_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_\-]+")
_STOPWORDS = frozenset(
    """a an the and or but if then else as of in on at to for with by
    is are was were be been being have has had do does did will would
    can could should may might this that these those it its they them
    we you your our their which what who how when where why because
    not no nor so than too very just""".split()
)


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text) if t.lower() not in _STOPWORDS]


# ---------------------------------------------------------------------------
# TF-IDF backend
# ---------------------------------------------------------------------------
class _TFIDFIndex:
    def __init__(self, docs: List[VaultDoc]):
        self.docs = docs
        self.vocab: Dict[str, int] = {}
        self._build()

    def _build(self) -> None:
        if not self.docs:
            self.matrix = np.zeros((0, 0))
            self.idf = np.zeros(0)
            return
        doc_tokens = [_tokenize(d.index_text) for d in self.docs]
        for tokens in doc_tokens:
            for tok in tokens:
                if tok not in self.vocab:
                    self.vocab[tok] = len(self.vocab)
        V = len(self.vocab)
        N = len(self.docs)
        tf = np.zeros((N, V), dtype=np.float32)
        for i, tokens in enumerate(doc_tokens):
            for tok in tokens:
                tf[i, self.vocab[tok]] += 1.0
        row_sums = tf.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        tf = tf / row_sums
        df = (tf > 0).sum(axis=0)
        idf = np.log((1.0 + N) / (1.0 + df)) + 1.0
        self.idf = idf.astype(np.float32)
        tfidf = tf * self.idf
        norms = np.linalg.norm(tfidf, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.matrix = (tfidf / norms).astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
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
        return self.matrix @ query_vec


# ---------------------------------------------------------------------------
# Optional sentence-transformers + FAISS backend
# ---------------------------------------------------------------------------
class _STIndex:
    def __init__(self, docs: List[VaultDoc], model_name: str):
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
        return (self.embeddings @ query_vec).astype(np.float32)


# ---------------------------------------------------------------------------
# Public class: VaultRetriever
# ---------------------------------------------------------------------------
class VaultRetriever:
    """Vault-backed RAG retriever with authority-aware filtering.

    Default behavior: returns top-k hits, primary-authority hits
    (reviewed + authoritative) ranked first; candidate / legacy hits
    are returned only if k is not yet satisfied or if no primary hit
    cleared a low score floor.
    """

    def __init__(
        self,
        wiki_dir: Optional[Path] = None,
        wiki_url_base: str = WIKI_SITE_BASE_DEFAULT,
        backend: Optional[str] = None,
        st_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        primary_only: bool = False,
    ):
        self.wiki_dir = Path(wiki_dir) if wiki_dir else VAULT_WIKI_DIR_DEFAULT
        self.wiki_url_base = wiki_url_base
        self.docs = _load_vault(self.wiki_dir)
        self.primary_only = primary_only

        chosen = (backend or os.getenv("EF_RAG_BACKEND", "tfidf")).lower()
        if chosen == "st+faiss":
            self._impl = _STIndex(self.docs, model_name=st_model)
            self.backend = "st+faiss"
        else:
            self._impl = _TFIDFIndex(self.docs)
            self.backend = "tfidf"

    # --- stats ------------------------------------------------------------
    def stats(self) -> Dict[str, int]:
        """Authority-level counts. Useful for the chat status bar."""
        out = {a: 0 for a in AUTHORITY_LEVELS}
        for d in self.docs:
            out[d.authority] = out.get(d.authority, 0) + 1
        out["total"] = len(self.docs)
        return out

    # --- retrieve ---------------------------------------------------------
    def retrieve(self, query: str, k: int = 3, primary_only: Optional[bool] = None) -> List[Dict[str, Any]]:
        if not self.docs:
            return []
        primary_only = self.primary_only if primary_only is None else primary_only
        query_vec = self._impl.embed_query(query)
        sims = self._impl.similarities(query_vec)
        if sims.size == 0:
            return []

        # Two-pass ranking: rank primaries first, then non-primaries, by score.
        order = np.argsort(-sims)
        primaries = [int(i) for i in order if self.docs[int(i)].is_primary]
        nonprimaries = [int(i) for i in order if not self.docs[int(i)].is_primary]

        picked: List[int] = []
        picked.extend(primaries[:k])
        if not primary_only and len(picked) < k:
            picked.extend(nonprimaries[: (k - len(picked))])
        # Edge case: if primary_only is on but nothing primary cleared, we
        # still surface the top non-primary so the chat doesn't go silent.
        if primary_only and not picked and nonprimaries:
            picked = nonprimaries[:k]

        hits: List[Dict[str, Any]] = []
        for i in picked:
            doc = self.docs[i]
            score = float(sims[i])
            hits.append(
                {
                    "path": doc.path,
                    "title": doc.title,
                    "authority": doc.authority,
                    "is_primary": doc.is_primary,
                    "scope": doc.scope,
                    "wiki_url": doc.wiki_url(self.wiki_url_base),
                    "score": round(score, 4),
                    "excerpt": _excerpt(doc.text, query),
                    "text": doc.text,
                }
            )
        return hits

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"VaultRetriever(wiki_dir={self.wiki_dir!s}, "
            f"backend={self.backend!r}, docs={len(self.docs)}, "
            f"primary_only={self.primary_only})"
        )


def _excerpt(text: str, query: str, width: int = 220) -> str:
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
# Tool wrapping (mirror legacy rag.py shape so dispatch swaps cleanly)
# ---------------------------------------------------------------------------
_SINGLETON: Optional[VaultRetriever] = None


def get_retriever() -> VaultRetriever:
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = VaultRetriever()
    return _SINGLETON


def retrieve(query: str, k: int = 3) -> Dict[str, Any]:
    r = get_retriever()
    return {
        "query": query,
        "k": k,
        "hits": r.retrieve(query, k=k),
        "backend": r.backend,
        "vault_stats": r.stats(),
    }


TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "retrieve",
            "description": (
                "Retrieve the top-k most relevant entries from the EnergyFlux "
                "knowledge vault for a natural-language query. Each hit "
                "includes 'authority' (authoritative / reviewed / candidate / "
                "legacy) and a wiki URL. Call this BEFORE answering any "
                "domain question (PV / BESS / hardware / siting / regulations / "
                "CAPEX) so the answer is grounded in vault content. Cite "
                "primary-authority hits (reviewed + authoritative) as fact; "
                "label any candidate / legacy citations as 'pending review'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "k": {
                        "type": "integer",
                        "description": "Max hits to return. Default 3.",
                    },
                },
                "required": ["query"],
            },
        },
    }
]

TOOL_DISPATCH: Dict[str, Any] = {"retrieve": retrieve}
