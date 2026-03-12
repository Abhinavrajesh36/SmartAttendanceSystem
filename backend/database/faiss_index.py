"""
FAISS Index Manager - Thread-Safe Version
==========================================

Key fixes vs original:
1. Thread safety: a threading.Lock guards all mutations (clear, add, remove).
   Without this, concurrent register + mark-attendance requests can produce
   a search() call on a half-cleared index, returning stale/wrong user_ids.

2. No auto-load in __init__: the constructor no longer loads from disk.
   Startup explicitly calls rebuild_faiss_from_db() which is the single
   source of truth (PostgreSQL). This eliminates the stale-disk-index bug
   where a .bin file from a previous run (or the shipped placeholder with
   mapping=[18]) could poison the in-memory index if the DB rebuild failed.

3. search_top_k: returns top-k candidates instead of just top-1.
   main.py uses this to pick the best match AMONG the top-k results,
   which is more robust than blindly trusting the single nearest neighbour.
"""

import threading
import faiss
import numpy as np
import pickle
import os
from typing import Tuple, List, Optional


class FAISSIndexManager:

    def __init__(
        self,
        embedding_dim: int = 512,
        index_path: str = "data/faiss_index.bin",
        metric: str = "cosine",
    ):
        self.embedding_dim = embedding_dim
        self.index_path    = index_path
        self.metric        = metric

        # id_mapping[i] = user_id for the i-th vector in the FAISS index
        self.id_mapping: List[int] = []

        # Thread lock - guards all mutations and search operations
        self._lock = threading.Lock()

        # Always start with an empty in-memory index.
        # main.py calls rebuild_faiss_from_db() at startup to populate from DB.
        # This avoids the stale-disk-index bug.
        self._reset_index()

        print("FAISSIndexManager initialised (empty). Call rebuild_faiss_from_db() to populate.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset_index(self):
        """Create a fresh empty FAISS index (does not acquire lock)."""
        if self.metric == "cosine":
            self.index = faiss.IndexFlatIP(self.embedding_dim)
        else:
            self.index = faiss.IndexFlatL2(self.embedding_dim)

    @staticmethod
    def _normalize(embedding: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(embedding)
        if norm < 1e-10:
            return embedding
        return embedding / norm

    # ------------------------------------------------------------------
    # Write operations (all hold the lock)
    # ------------------------------------------------------------------

    def clear(self):
        """Wipe the in-memory index and id_mapping."""
        with self._lock:
            self._reset_index()
            self.id_mapping = []
        print("FAISS index cleared.")

    def add_embedding(self, user_id: int, embedding: np.ndarray):
        """
        Add a single embedding to the index.

        The embedding is L2-normalised before insertion so that
        IndexFlatIP computes cosine similarity correctly.
        """
        emb = self._normalize(embedding.astype("float32"))
        emb = emb.reshape(1, -1)

        with self._lock:
            self.index.add(emb)
            self.id_mapping.append(user_id)

        print(f"[FAISS] Added user_id={user_id}. Total vectors: {self.index.ntotal}")

    def add_embeddings_batch(self, user_ids: List[int], embeddings: np.ndarray):
        """Add multiple embeddings atomically."""
        embs = embeddings.astype("float32")
        # Normalise row-wise
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        norms = np.where(norms < 1e-10, 1.0, norms)
        embs = embs / norms

        with self._lock:
            self.index.add(embs)
            self.id_mapping.extend(user_ids)

        print(f"[FAISS] Batch added {len(user_ids)} vectors. Total: {self.index.ntotal}")

    def remove_embedding(self, user_id: int) -> bool:
        """
        Remove all embeddings for user_id by rebuilding the index.
        Returns True if any entry was removed.
        """
        with self._lock:
            if user_id not in self.id_mapping:
                return False

            keep_indices = [i for i, uid in enumerate(self.id_mapping) if uid != user_id]
            if len(keep_indices) == self.index.ntotal:
                return False  # Nothing to remove

            kept_vecs = []
            kept_ids  = []
            for i in keep_indices:
                vec = self.index.reconstruct(i)
                kept_vecs.append(vec)
                kept_ids.append(self.id_mapping[i])

            self._reset_index()
            self.id_mapping = []

            if kept_vecs:
                arr = np.array(kept_vecs, dtype="float32")
                self.index.add(arr)
                self.id_mapping = kept_ids

        print(f"[FAISS] Removed user_id={user_id}. Total vectors: {self.index.ntotal}")
        return True

    # ------------------------------------------------------------------
    # Search (holds lock for the duration of the FAISS call)
    # ------------------------------------------------------------------

    def search(self, query_embedding: np.ndarray, k: int = 1) -> Tuple[int, float]:
        """
        Find the closest registered embedding.

        Returns:
            (user_id, cosine_distance) where distance = 1 - cosine_similarity.
            Raises ValueError if the index is empty.
        """
        with self._lock:
            if self.index.ntotal == 0:
                raise ValueError("FAISS index is empty. No users registered.")

            emb = self._normalize(query_embedding.astype("float32")).reshape(1, -1)
            k_clamped = min(k, self.index.ntotal)
            distances, indices = self.index.search(emb, k_clamped)

        # Convert inner-product scores to cosine distances
        best_idx  = indices[0][0]
        best_ip   = float(distances[0][0])  # inner product = cosine similarity (normalised)

        if best_idx < 0 or best_idx >= len(self.id_mapping):
            raise ValueError(f"FAISS returned invalid index {best_idx}. Index may be corrupt.")

        user_id  = self.id_mapping[best_idx]
        distance = float(1.0 - best_ip)    # cosine distance: 0=identical, 2=opposite
        return user_id, distance

    def search_top_k(
        self, query_embedding: np.ndarray, k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Return top-k (user_id, cosine_distance) candidates sorted by distance.

        Use this in mark-attendance for more robust matching: pick the
        candidate with the smallest distance below the threshold, rather than
        blindly trusting the single nearest neighbour.
        """
        with self._lock:
            if self.index.ntotal == 0:
                raise ValueError("FAISS index is empty. No users registered.")

            emb = self._normalize(query_embedding.astype("float32")).reshape(1, -1)
            k_clamped = min(k, self.index.ntotal)
            distances, indices = self.index.search(emb, k_clamped)

        results = []
        for idx, ip in zip(indices[0], distances[0]):
            if 0 <= idx < len(self.id_mapping):
                results.append((self.id_mapping[idx], float(1.0 - ip)))

        results.sort(key=lambda x: x[1])  # sort by ascending distance
        return results

    # ------------------------------------------------------------------
    # Persistence (save / load)
    # ------------------------------------------------------------------

    def save_index(self):
        """Persist the current in-memory index and id_mapping to disk."""
        os.makedirs(os.path.dirname(os.path.abspath(self.index_path)), exist_ok=True)

        with self._lock:
            faiss.write_index(self.index, self.index_path)
            mapping_path = self.index_path.replace(".bin", "_mapping.pkl")
            with open(mapping_path, "wb") as f:
                pickle.dump(self.id_mapping, f)

        print(f"[FAISS] Saved index ({self.index.ntotal} vectors) to {self.index_path}")

    def load_index(self):
        """
        Load a previously saved index from disk into the in-memory state.

        Called ONLY by rebuild_faiss_from_db after a successful full rebuild,
        or during explicit admin operations. Never called in __init__.
        """
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"FAISS index file not found: {self.index_path}")

        loaded_index   = faiss.read_index(self.index_path)
        mapping_path   = self.index_path.replace(".bin", "_mapping.pkl")
        loaded_mapping = []
        if os.path.exists(mapping_path):
            with open(mapping_path, "rb") as f:
                loaded_mapping = pickle.load(f)

        with self._lock:
            self.index      = loaded_index
            self.id_mapping = loaded_mapping

        print(f"[FAISS] Loaded index from disk: {self.index.ntotal} vectors, {len(self.id_mapping)} mapped IDs")

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_stats(self) -> dict:
        with self._lock:
            ntotal   = self.index.ntotal
            n_unique = len(set(self.id_mapping))
            mapping  = list(self.id_mapping)
        return {
            "total_vectors":  ntotal,
            "unique_users":   n_unique,
            "embedding_dim":  self.embedding_dim,
            "metric":         self.metric,
            "index_type":     type(self.index).__name__,
            "id_mapping":     mapping,
        }
