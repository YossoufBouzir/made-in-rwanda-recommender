# process_log.md — AIMS KTT Hackathon · S2.T1.3

**Candidate:** Youssouf Bouzir
**Challenge:** S2.T1.3 · "Made in Rwanda" Content Recommender
**Date:** 2026-04-22

---

## 1. Hour-by-hour timeline

**0:00–0:20** — Read challenge brief and candidate briefing
- Carefully read the S2.T1.3 brief and the general hackathon briefing.
- Sketched rough plan: TF-IDF baseline, local boost, popularity prior, evaluation notebook, and offline-artisan workflow.

**0:20–1:20** — Implement baseline recommender (`recommender.py`)
- Defined data loading for `catalog.csv` and `click_log.csv`.
- Built TF-IDF vectorizer (bigrams) over combined text fields and cosine similarity retrieval.
- Added `is_local` inference from `origin_district` and a multiplicative local-boost factor.
- Implemented curated fallback when the top global match is non-local and no local item passes the similarity threshold.

**1:20–1:50** — Implement evaluation notebook (`eval.ipynb`)
- Loaded `catalog.csv`, `queries.csv`, and `click_log.csv`.
- Built graded relevance from click logs.
- Computed NDCG@5 and local-presence rate across all queries.
- Saved `evaluation_results.csv` and `evaluation_summary.csv`.

**1:50–2:20** — README and repo wiring
- Drafted `README.md` with instructions to run in ≤2 commands on a free Colab CPU.
- Documented expected columns in `catalog.csv` and example CLI usage.
- Included required demo query `cadeau en cuir pour femme`.

**2:20–3:00** — Product & business artifact (`dispatcher.md`)
- Designed weekly lead workflow for a Nyamirambo leather artisan without a smartphone.
- Defined roles for platform operator, cooperative agent, and artisans.
- Estimated 3-month pilot unit economics: cost per artisan, cost per lead, break-even GMV.

**3:00–3:30** — Data samples and generator
- Created synthetic sample CSVs: `data/catalog.csv`, `data/queries.csv`, `data/click_log.csv`.
- Created `generator/synthetic_generator.py` for reproducible data generation.

**3:30–4:00** — Documentation artifacts
- Wrote `process_log.md` (this file) and `SIGNED.md`.
- Prepared talking points for the 4-minute video.

---

## 2. LLMs and assistant tools used

1. **Perplexity (Comet / GPT-based assistant)**
   - **Purpose:** Help structure the overall solution, generate baseline implementation of `recommender.py`, draft `eval.ipynb`, `README.md`, `dispatcher.md`, `process_log.md`, and `SIGNED.md`.
   - **How I used it:** Treated as a coding and writing assistant. I checked and adjusted all code and text locally to ensure I can defend every line in the live defence. Judgment calls (thresholds, metric interpretation, economic assumptions) were made by me.

---

## 3. Three representative prompts I used

### Prompt 1 — Specification understanding and plan
> *"Here is the S2.T1.3 Made in Rwanda Content Recommender brief. Help me extract the exact technical and product deliverables and propose a simple Python-based TF-IDF recommender design that fits CPU-only and low-tech constraints."*

### Prompt 2 — Baseline code scaffolding
> *"Python is OK. I will create catalog.csv, queries.csv, and click_log.csv under data/. Please write a recommender.py with TF-IDF + cosine similarity + local boost + curated fallback, and a CLI: python recommender.py --q 'leather boots'."*

### Prompt 3 — Business adaptation
> *"Draft dispatcher.md describing a weekly SMS/voice lead flow for a Nyamirambo leather artisan with no smartphone, and a 3-month pilot with 20 artisans including unit economics and break-even GMV."*

---

## 4. One prompt I considered but discarded

> *"Generate a multilingual sentence embedding recommender with transformers and GPU acceleration."*

**Why I discarded it:** This would violate the CPU-only, no-paid-API constraints of the challenge. A transformer-based approach would add complexity and latency without clear benefit for a 400-product catalog, and would be harder to defend in the live defence. I chose TF-IDF with clear trade-offs instead.

---

## 5. Hardest decision and how I resolved it

The hardest decision was **choosing TF-IDF + cosine similarity over multilingual sentence embeddings**.

- **Arguments for sentence embeddings:** Better handling of French/English/code-switched queries; more robust to spelling variants.
- **Arguments for TF-IDF:** Fits CPU-only constraints perfectly; very fast on 400 items; easy to explain; no paid APIs needed.

I chose **TF-IDF with bigrams + local-boost rule + popularity prior** as a baseline that is transparent, reproducible, and aligned with the challenge constraints. If I had more time, I would consider adding a sentence embedding model as a secondary candidate generator.
