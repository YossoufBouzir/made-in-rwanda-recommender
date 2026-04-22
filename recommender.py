"""
recommender.py
Made in Rwanda Content Recommender
AIMS KTT Hackathon - Challenge S2.T1.3
Author: Youssouf Bouzir
Date: 2026-04-22

Usage:
    python recommender.py --q "leather boots"
    python recommender.py --q "cadeau en cuir pour femme" --top_k 5
"""

import argparse
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CATALOG_PATH = os.path.join(DATA_DIR, "catalog.csv")
CLICK_LOG_PATH = os.path.join(DATA_DIR, "click_log.csv")

# Districts that are considered "local" (Rwanda)
RWANDAN_DISTRICTS = {
    "kigali", "gasabo", "kicukiro", "nyarugenge", "nyamirambo",
    "huye", "musanze", "rubavu", "rusizi", "nyagatare",
    "rwamagana", "kayonza", "kirehe", "ngoma", "bugesera",
    "kamonyi", "muhanga", "ruhango", "nyanza", "gisagara",
    "nyaruguru", "nyamagabe", "karongi", "rutsiro", "ngororero",
    "nyabihu", "gakenke", "rulindo", "gicumbi", "burera",
    "gatsibo", "rwamagana"
}

DEFAULT_LOCAL_BOOST = 0.25   # multiply local item scores by (1 + boost)
DEFAULT_POPULARITY_WEIGHT = 0.05
DEFAULT_SIMILARITY_THRESHOLD = 0.10
DEFAULT_TOP_K = 5


# ---------------------------------------------------------------------------
# Helper: build product text
# ---------------------------------------------------------------------------

def build_product_text(row: pd.Series) -> str:
    """Concatenate relevant fields into a single text string for TF-IDF."""
    parts = [
        str(row.get("title", "")),
        str(row.get("description", "")),
        str(row.get("category", "")),
        str(row.get("material", "")),
        str(row.get("origin_district", "")),
    ]
    return " ".join(p for p in parts if p and p.lower() != "nan")


# ---------------------------------------------------------------------------
# Main recommender class
# ---------------------------------------------------------------------------

class MadeInRwandaRecommender:
    """
    Content-based recommender with:
    - TF-IDF representation over product metadata
    - Cosine similarity retrieval
    - Local boost for Made-in-Rwanda products
    - Popularity prior from click logs
    - Curated fallback when no strong local match is found
    """

    def __init__(
        self,
        catalog_path: str = CATALOG_PATH,
        click_log_path: str = CLICK_LOG_PATH,
        local_boost: float = DEFAULT_LOCAL_BOOST,
        popularity_weight: float = DEFAULT_POPULARITY_WEIGHT,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ):
        self.local_boost = local_boost
        self.popularity_weight = popularity_weight
        self.similarity_threshold = similarity_threshold

        self.catalog = self._load_catalog(catalog_path)
        self.click_counts = self._load_click_counts(click_log_path)
        self.vectorizer, self.doc_matrix = self._build_vectorizer()
        self.local_mask = self._build_local_mask()
        self.popularity = self._build_popularity_vector()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_catalog(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        required = ["sku", "title", "origin_district"]
        for col in required:
            if col not in df.columns:
                raise ValueError(f"catalog.csv is missing required column: '{col}'")
        df["product_text"] = df.apply(build_product_text, axis=1)
        df["origin_district"] = df["origin_district"].fillna("").str.lower().str.strip()
        return df.reset_index(drop=True)

    def _load_click_counts(self, path: str) -> pd.Series:
        if not os.path.exists(path):
            return pd.Series(dtype=float)
        df = pd.read_csv(path)
        if "sku" not in df.columns:
            return pd.Series(dtype=float)
        return df["sku"].value_counts()

    # ------------------------------------------------------------------
    # Model building
    # ------------------------------------------------------------------

    def _build_vectorizer(self):
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
        )
        doc_matrix = vectorizer.fit_transform(self.catalog["product_text"])
        return vectorizer, doc_matrix

    def _build_local_mask(self) -> np.ndarray:
        """Boolean array: True if product origin is a Rwandan district."""
        return self.catalog["origin_district"].apply(
            lambda d: any(rw in d for rw in RWANDAN_DISTRICTS)
        ).values

    def _build_popularity_vector(self) -> np.ndarray:
        """Normalised click counts vector aligned to catalog index."""
        counts = self.catalog["sku"].map(self.click_counts).fillna(0).values.astype(float)
        max_count = counts.max()
        if max_count > 0:
            counts = counts / max_count
        return counts

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def recommend(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> pd.DataFrame:
        """
        Main retrieval function.

        Parameters
        ----------
        query : str
            Free-text search query (English, French, or code-switched).
        top_k : int
            Number of recommendations to return.

        Returns
        -------
        pd.DataFrame with columns:
            rank, sku, title, origin_district, is_local,
            similarity, final_score, reason
        """
        q_vec = self.vectorizer.transform([query.lower()])
        sim = cosine_similarity(q_vec, self.doc_matrix).ravel()

        # Apply local boost
        adjusted = sim.copy()
        adjusted[self.local_mask] = adjusted[self.local_mask] * (1.0 + self.local_boost)

        # Add popularity prior
        final_score = adjusted + self.popularity_weight * self.popularity

        # Rank all products
        ranked_idx = np.argsort(final_score)[::-1]

        top_global = self.catalog.iloc[ranked_idx[:top_k]].copy()
        top_global["similarity"] = sim[ranked_idx[:top_k]]
        top_global["final_score"] = final_score[ranked_idx[:top_k]]

        # Check if the best result is local
        global_best_local = bool(self.local_mask[ranked_idx[0]])

        # Check if any local item passes the similarity threshold in top_k
        local_in_top = top_global[top_global["origin_district"].apply(
            lambda d: any(rw in d for rw in RWANDAN_DISTRICTS)
        )]
        strong_local = local_in_top[local_in_top["similarity"] >= self.similarity_threshold]

        # Trigger curated fallback if needed
        if (not global_best_local) and strong_local.empty:
            fallback = self._curated_fallback(query, top_k=top_k)
            if not fallback.empty:
                result = fallback
                reason_label = "curated_fallback"
            else:
                result = top_global
                reason_label = "content_match"
        else:
            result = top_global
            reason_label = None

        # Assign reason per row
        def assign_reason(row):
            if reason_label:
                return reason_label
            d = row["origin_district"]
            is_loc = any(rw in d for rw in RWANDAN_DISTRICTS)
            if is_loc and row["similarity"] >= self.similarity_threshold:
                return "local_boosted_or_relevant"
            return "content_match"

        result = result.head(top_k).copy()
        result["is_local"] = result["origin_district"].apply(
            lambda d: any(rw in d for rw in RWANDAN_DISTRICTS)
        )
        result["reason"] = result.apply(assign_reason, axis=1)
        result = result.reset_index(drop=True)
        result.index = result.index + 1
        result.index.name = "rank"

        cols = ["sku", "title", "origin_district", "is_local", "similarity", "final_score", "reason"]
        available_cols = [c for c in cols if c in result.columns]
        return result[available_cols]

    def _curated_fallback(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> pd.DataFrame:
        """
        When no local item has strong similarity, return a curated set of
        local products matched by category / material keywords extracted
        from the query.
        """
        local_catalog = self.catalog[self.local_mask].copy()
        if local_catalog.empty:
            return pd.DataFrame()

        query_lower = query.lower()
        # Score each local product: 1 point per keyword overlap
        def keyword_score(row):
            text = row["product_text"].lower()
            score = sum(1 for word in query_lower.split() if word in text)
            return score

        local_catalog["kw_score"] = local_catalog.apply(keyword_score, axis=1)
        local_catalog = local_catalog.sort_values(
            ["kw_score"], ascending=False
        ).head(top_k)

        local_catalog["similarity"] = 0.0
        local_catalog["final_score"] = local_catalog["kw_score"].astype(float)
        return local_catalog


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Made in Rwanda Content Recommender"
    )
    parser.add_argument(
        "--q", "--query", dest="query", required=True,
        help="Search query (English, French, or code-switched)"
    )
    parser.add_argument(
        "--top_k", type=int, default=DEFAULT_TOP_K,
        help=f"Number of results to return (default: {DEFAULT_TOP_K})"
    )
    parser.add_argument(
        "--local_boost", type=float, default=DEFAULT_LOCAL_BOOST,
        help=f"Local boost factor (default: {DEFAULT_LOCAL_BOOST})"
    )
    parser.add_argument(
        "--threshold", type=float, default=DEFAULT_SIMILARITY_THRESHOLD,
        help=f"Similarity threshold for local items (default: {DEFAULT_SIMILARITY_THRESHOLD})"
    )
    args = parser.parse_args()

    print(f"\nQuery: '{args.query}'")
    print("-" * 60)

    rec = MadeInRwandaRecommender(
        local_boost=args.local_boost,
        similarity_threshold=args.threshold,
    )
    results = rec.recommend(args.query, top_k=args.top_k)
    print(results.to_string())
    print("-" * 60)
    local_count = results["is_local"].sum()
    print(f"Local products in top-{args.top_k}: {local_count}/{args.top_k}")


if __name__ == "__main__":
    main()
