# 'Made in Rwanda' Content Recommender — Dispatcher & Pilot Plan

**Challenge:** AIMS KTT Hackathon · S2.T1.3 · "Made in Rwanda" Content Recommender
**Focus:** Low-tech distribution of recommendation leads to offline artisans in Rwanda.

---

## 1. Weekly leads workflow for a Nyamirambo leather artisan (no smartphone)

### 1.1 Actors

- **Buyer-facing marketplace (platform operator)**
  Runs the search/recommender engine, stores query logs, and aggregates leads.

- **Sector cooperative / local agent in Nyamirambo**
  A field officer or cooperative staff member who has a basic smartphone and can receive SMS / WhatsApp and make calls. This person is the bridge between the platform and offline artisans.

- **Artisan**
  A leatherworker based in Nyamirambo, Kigali. No smartphone, typically reachable via a feature phone (basic calls/SMS) or in-person visits coordinated through the cooperative.

### 1.2 Data pipeline from queries to leads

1. **Daily query logging**
   Every search on the platform is logged with: `timestamp`, `query_text`, `top_5_skus`, `clicked_sku` and position (if any).

2. **Local candidate detection (same day)**
   For each query, the TF-IDF recommender produces top-5 candidates with `is_local` flags and a reason code (`content_match`, `local_boosted_or_relevant`, or `curated_fallback`).
   If at least one local product appears in the top-3, that query is marked as **local-present**.

3. **Lead scoring and filtering (end of each day)**
   For each artisan, aggregate:
   - # of queries where their products appeared in top-3.
   - # of clicks on their SKUs.
   A query → product → artisan is a **lead** if the product appeared in top-3 AND was clicked OR similarity score ≥ 0.25.

4. **Weekly consolidation**
   At end of each week, the system aggregates per artisan: total queries shown, high-intent leads, approximate GMV potential.

### 1.3 Weekly communication to the artisan

**Step 1: Platform → Cooperative (SMS + dashboard)**

Every Monday at 09:00 the platform sends an SMS summary to the cooperative agent:

> *"AIMS Market — Weekly Leads for Nyamirambo Leather Artisans:
>  • 47 buyers searched for leather items related to Nyamirambo.
>  • 19 high-intent leads matched your cooperative's products.
>  • Estimated sales value: 380,000 RWF.
>  Log in to the dashboard for details."*

**Step 2: Cooperative → Artisan (SMS or voice call)**

- **If artisan has a feature phone:**
  SMS digest in Kinyarwanda / simple English:
  > *"AIMS Market: This week 5 buyers looked for women's leather bags like yours.
  >  2 buyers preferred black (30–40k RWF), 3 preferred brown (40–50k).
  >  Please prepare 3 sample bags for next market visit on Friday."*

- **If artisan has no phone:**
  In-person visit (e.g. weekly Thursday visits to Nyamirambo workshop cluster) with printed or handwritten summaries with simple icons/colors per product type.

### 1.4 Key weekly numbers tracked

Per artisan:
- `queries_exposed`: queries where their products appeared in top-3.
- `high_intent_leads`: subset where the product was clicked or had high similarity.
- `contacts_attempted`: leads the artisan tried to respond to.
- `sales_closed`: confirmed sales.
- `realized_gmv_rwf`: total value of sales linked to recommendation leads.

---

## 2. Three-month pilot with 20 artisans

### 2.1 Pilot structure

- **Duration:** 3 months (12 weeks).
- **Participants:** 20 artisans from Kigali and nearby districts:
  - 8 leather artisans (including Nyamirambo leatherworker)
  - 5 basketry cooperatives
  - 4 jewellery makers
  - 3 home-decor artisans
- **Channel mix:** 60% feature phones (SMS + calls), 40% in-person cooperative visits.

### 2.2 Volume assumptions (per artisan)

- Average relevant queries per artisan per week: **50 queries**
- High-intent leads: **15 leads/week**
- Conversion rate: **15–20%** (assume 18%)
- Average basket size: **35,000 RWF**

Per artisan per week:
- `15 leads × 0.18 ≈ 2.7 sales/week`
- `2.7 × 35,000 RWF ≈ 94,500 RWF GMV/week`

Per artisan over 12 weeks:
- ~32 sales, ~1,134,000 RWF GMV

For **20 artisans** over the pilot:
- ~640 sales, ~22.7M RWF GMV

### 2.3 Cost model

| Cost item | Weekly | 12-week total |
|-----------|--------|---------------|
| Agent time (20 artisans × 10 min @ 3,000 RWF/hr) | ~10,000 RWF | ~120,000 RWF |
| Telecom (20 artisans × 300 RWF/week) | ~6,000 RWF | ~72,000 RWF |
| **Total variable cost** | **~16,000 RWF** | **~192,000 RWF** |

### 2.4 Unit economics

- **Cost per artisan (3 months):** 192,000 / 20 ≈ **9,600 RWF**
- **Cost per lead:** 192,000 / 3,600 ≈ **53 RWF**
- **GMV per artisan:** ~1,134,000 RWF
- **Variable cost as % of GMV:** < 1%

### 2.5 Break-even GMV

Assuming 15% platform commission:
- Commission needed to break even per artisan = 9,600 RWF
- `0.15 × GMV = 9,600` → **Break-even GMV ≈ 64,000 RWF per artisan**

Our conservative estimate (~1.13M RWF) is far above this threshold.

### 2.6 Success criteria

**Technical / model metrics**
- NDCG@5 above keyword-search baseline on 120-query set.
- Local-presence rate in top-3 ≥ 70% for relevant queries.

**Business / adoption metrics**
- ≥ 80% of artisans report weekly digests are understandable and useful.
- ≥ 50% of GMV for participating artisans attributed to recommendation-driven leads.
- Variable cost per lead stays under 100 RWF as traffic scales.
