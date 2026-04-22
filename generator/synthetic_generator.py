"""
synthetic_generator.py
Generates synthetic data for the Made in Rwanda Content Recommender.
AIMS KTT Hackathon - Challenge S2.T1.3
Author: Youssouf Bouzir

Usage:
    python generator/synthetic_generator.py
    python generator/synthetic_generator.py --n_products 400 --n_queries 120 --n_clicks 600
"""

import argparse
import os
import random
import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# Data pools
# ---------------------------------------------------------------------------

RWANDAN_DISTRICTS = [
    "kigali", "gasabo", "kicukiro", "nyarugenge", "nyamirambo",
    "huye", "musanze", "rubavu", "rusizi", "nyagatare",
    "rwamagana", "kayonza", "kirehe", "ngoma", "bugesera",
    "kamonyi", "muhanga", "ruhango", "nyanza", "gisagara",
]

NON_LOCAL_DISTRICTS = [
    "nairobi_ke", "lagos_ng", "addis_ababa_et", "dakar_sn", "accra_gh"
]

CATEGORIES = [
    "leather_goods", "basketry", "jewellery", "home_decor",
    "footwear", "bags", "textiles", "ceramics"
]

MATERIALS = {
    "leather_goods": ["leather"],
    "basketry": ["sisal", "wicker", "banana_leaf", "raffia"],
    "jewellery": ["beads", "silver", "copper", "brass"],
    "home_decor": ["wood", "paint", "sisal", "ceramic"],
    "footwear": ["leather", "rubber", "canvas"],
    "bags": ["leather", "raffia", "fabric"],
    "textiles": ["cotton", "silk", "wool"],
    "ceramics": ["clay", "porcelain"]
}

TITLE_TEMPLATES = {
    "leather_goods": [
        "{color} Leather Handbag", "Leather Wallet", "Leather Belt",
        "Leather Passport Holder", "Leather Coin Purse", "Leather Laptop Bag"
    ],
    "basketry": [
        "Woven {material} Basket", "Agaseke Peace Basket", "Storage Basket",
        "Banana Leaf Basket", "Decorative Wicker Basket"
    ],
    "jewellery": [
        "Beaded Necklace", "Silver Earrings", "Copper Bracelet",
        "Beaded Bracelet", "Brass Anklet", "Wire Pendant"
    ],
    "home_decor": [
        "Imigongo Wall Art", "Wooden Serving Bowl", "Woven Wall Hanging",
        "Sisal Floor Mat", "Wooden Picture Frame", "Ceramic Vase"
    ],
    "footwear": [
        "Leather Sandals", "Handmade Leather Shoes", "Open-Toe Sandals"
    ],
    "bags": [
        "Raffia Handbag", "Fabric Tote Bag", "Leather Shoulder Bag"
    ],
    "textiles": [
        "Cotton Kikoi Wrap", "Woven Scarf", "Hand-Printed Fabric"
    ],
    "ceramics": [
        "Handmade Clay Pot", "Decorative Ceramic Bowl", "Clay Water Jug"
    ]
}

DESCRIPTION_TEMPLATES = [
    "Handcrafted {material} {category} made by skilled artisans in {district}.",
    "Traditional Rwandan {category} made from {material}, crafted in {district}.",
    "High-quality {material} product from {district}, Rwanda. Perfect gift.",
    "Authentic Made-in-Rwanda {category} from {district}. Durable {material}.",
    "Locally sourced {material} used by artisans in {district} to create this {category}."
]

QUERY_TEMPLATES = [
    "leather handbag for women",
    "cadeau en cuir pour femme",
    "woven basket Rwanda",
    "panier tresse traditionnel",
    "leather boots handmade",
    "silver jewellery necklace",
    "sac en cuir noir",
    "wooden home decor",
    "beaded bracelet colourful",
    "imigongo wall art traditional",
    "leather wallet slim",
    "sisal floor mat",
    "bijoux perles fait main",
    "leather sandals open toe",
    "corbeille sisal Rwanda",
    "copper bracelet handmade",
    "laptop bag leather",
    "sac ordinateur portable cuir",
    "banana leaf eco basket",
    "agaseke peace basket Rwanda",
    "wooden serving bowl handcrafted",
    "raffia tote bag colorful",
    "cotton scarf handmade",
    "clay pot traditional Rwanda",
    "brass earrings handcrafted",
]

COLORS = ["black", "brown", "red", "blue", "green", "natural", "tan"]


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def generate_catalog(n_products: int, local_fraction: float = 0.65) -> pd.DataFrame:
    records = []
    n_local = int(n_products * local_fraction)
    n_foreign = n_products - n_local

    for i in range(n_products):
        sku = f"SKU{i+1:04d}"
        category = random.choice(CATEGORIES)
        material = random.choice(MATERIALS[category])
        color = random.choice(COLORS)
        title_template = random.choice(TITLE_TEMPLATES[category])
        title = title_template.format(color=color, material=material)

        if i < n_local:
            district = random.choice(RWANDAN_DISTRICTS)
        else:
            district = random.choice(NON_LOCAL_DISTRICTS)

        desc_template = random.choice(DESCRIPTION_TEMPLATES)
        description = desc_template.format(
            material=material, category=category, district=district
        )

        price = random.randint(5000, 80000)
        artisan_id = f"A{random.randint(1, 50):03d}"

        records.append({
            "sku": sku,
            "title": title,
            "description": description,
            "category": category,
            "material": material,
            "origin_district": district,
            "price_rwf": price,
            "artisan_id": artisan_id,
        })

    return pd.DataFrame(records)


def generate_queries(n_queries: int) -> pd.DataFrame:
    records = []
    languages = ["en", "fr"]
    for i in range(n_queries):
        qid = f"Q{i+1:03d}"
        q_text = random.choice(QUERY_TEMPLATES)
        lang = "fr" if any(w in q_text for w in ["en", "pour", "fait", "sac", "cuir", "panier", "bijoux", "corbeille"]) else "en"
        records.append({"query_id": qid, "query_text": q_text, "language": lang})
    return pd.DataFrame(records)


def generate_click_log(catalog_df: pd.DataFrame, queries_df: pd.DataFrame, n_clicks: int) -> pd.DataFrame:
    records = []
    skus = catalog_df["sku"].tolist()
    query_ids = queries_df["query_id"].tolist()
    for i in range(n_clicks):
        records.append({
            "event_id": f"E{i+1:04d}",
            "query_id": random.choice(query_ids),
            "sku": random.choice(skus),
            "position": random.randint(1, 5),
            "timestamp": f"2026-04-{random.randint(1, 22):02d}T{random.randint(8, 20):02d}:{random.randint(0, 59):02d}:00"
        })
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Synthetic data generator for Made in Rwanda Recommender")
    parser.add_argument("--n_products", type=int, default=400)
    parser.add_argument("--n_queries", type=int, default=120)
    parser.add_argument("--n_clicks", type=int, default=600)
    parser.add_argument("--output_dir", type=str, default="data")
    parser.add_argument("--local_fraction", type=float, default=0.65)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Generating catalog ({args.n_products} products)...")
    catalog = generate_catalog(args.n_products, local_fraction=args.local_fraction)
    catalog.to_csv(os.path.join(args.output_dir, "catalog.csv"), index=False)

    print(f"Generating queries ({args.n_queries} queries)...")
    queries = generate_queries(args.n_queries)
    queries.to_csv(os.path.join(args.output_dir, "queries.csv"), index=False)

    print(f"Generating click log ({args.n_clicks} events)...")
    click_log = generate_click_log(catalog, queries, args.n_clicks)
    click_log.to_csv(os.path.join(args.output_dir, "click_log.csv"), index=False)

    print(f"Done. Files saved to '{args.output_dir}/'.")
    print(f"  catalog.csv   : {len(catalog)} rows")
    print(f"  queries.csv   : {len(queries)} rows")
    print(f"  click_log.csv : {len(click_log)} rows")


if __name__ == "__main__":
    main()
