# Made in Rwanda Content Recommender

**AIMS KTT Hackathon · Challenge S2.T1.3**  
**Author:** Youssouf Bouzir  
**Email:** bouzir.youssouf@students.jkuat.ac.ke  
**Date:** 2026-04-22

---

## Overview

A CPU-friendly content-based recommender for Made-in-Rwanda products. The system uses TF-IDF over product metadata, cosine similarity for retrieval, a local-boost rule that prioritises Rwandan-made items, and a curated fallback when no strong local match is found.

**Final metrics on the provided query set:**
- NDCG@5: _(0.0808 0.0808  (expected 0.0808))_
- Local-presence rate (top-3): _(1.0000  (expected 1.0000 = 100.0%))_
- Curated-fallback rate : 0.0000  (expected 0.0000)
  
**4-minute demo video:** _(............................)_

---

## Repository structure

```
made-in-rwanda-recommender/
├── recommender.py             # main retrieval pipeline + CLI
├── eval.ipynb                 # evaluation notebook (NDCG@5 + local-presence rate)
├── dispatcher.md              # product & business adaptation artifact
├── process_log.md             # timeline + declared LLM/tool use
├── SIGNED.md                  # signed honor code
├── README.md                  # this file
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT
├── data/
│   ├── catalog.csv            # product catalog (400 SKUs)
│   ├── queries.csv            # evaluation queries
│   └── click_log.csv          # user click events
└── generator/
    └── synthetic_generator.py # script to regenerate synthetic data
```

---

## Quick start (local)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run a query
python recommender.py --q "leather boots"

# 3. French / code-switched query (required demo)
python recommender.py --q "cadeau en cuir pour femme" --top_k 5
```

## Quick start (Google Colab)

Open a new Colab notebook and run:

```python
# Cell 1
!git clone https://github.com/YossoufBouzir/made-in-rwanda-recommender.git
%cd made-in-rwanda-recommender
!pip install -r requirements.txt

# Cell 2
!python recommender.py --q "cadeau en cuir pour femme" --top_k 5
```

---

## Data

Sample CSV files are included in `data/`. To regenerate a full synthetic dataset:

```bash
python generator/synthetic_generator.py --n_products 400 --n_queries 120 --n_clicks 600
```

Expected columns in `data/catalog.csv`:

| Column | Description |
|--------|-------------|
| sku | Unique product ID |
| title | Product name |
| description | Short product description |
| category | Product category (e.g. leather_goods, basketry) |
| material | Primary material |
| origin_district | Rwandan district of origin |
| price_rwf | Price in Rwandan Francs |
| artisan_id | Artisan identifier |

---

## Method summary

1. Build a TF-IDF representation from concatenated product fields (title, description, category, material, origin_district).
2. For each query, compute cosine similarity against all product vectors.
3. Apply a **local boost** (multiplicative factor) to products whose `origin_district` is in Rwanda.
4. Add a small **popularity prior** from click counts.
5. If the top global match is non-local and no local item passes the similarity threshold, trigger a **curated fallback** that filters local products by category/material keywords.

---

## Evaluation

Open and run `eval.ipynb` end-to-end. It will print and save:
- `evaluation_results.csv` — per-query metrics
- `evaluation_summary.csv` — aggregate NDCG@5 and local-presence rate

---

## License

MIT — see `LICENSE`.
