"""
Generates a realistic synthetic lead/customer dataset so the product can
be demonstrated end-to-end without external data.

Usage:
    python scripts/generate_sample_data.py --rows 5000 --out sample_data.csv
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

SOURCES = {
    # source: (weight, base_conversion_multiplier, avg_engagement_boost)
    "google_ads": (0.22, 1.15, 0.05),
    "organic_search": (0.20, 1.35, 0.10),
    "facebook_ads": (0.16, 0.75, -0.05),
    "linkedin": (0.14, 1.25, 0.08),
    "referral": (0.10, 1.60, 0.15),
    "content_marketing": (0.10, 1.10, 0.06),
    "affiliate": (0.08, 0.65, -0.08),
}
CAMPAIGNS = ["spring_launch", "always_on", "webinar_series", "product_hunt", "partner_promo", "retargeting"]
INDUSTRIES = ["SaaS", "E-commerce", "Fintech", "Healthcare", "Education", "Manufacturing", "Media"]
COUNTRIES = ["United States", "United Kingdom", "Germany", "India", "Canada", "Australia", "Brazil", "France"]
COMPANY_SIZES = ["1-10", "11-50", "51-200", "201-500", "500+"]
PRODUCTS = ["Core Platform", "Analytics Add-on", "Enterprise Suite"]
PLANS = ["Free", "Starter", "Pro", "Enterprise"]


def generate(n_rows: int, seed: int = 42, anomaly_days: int = 3) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    source_names = list(SOURCES.keys())
    source_weights = np.array([v[0] for v in SOURCES.values()])
    source_weights = source_weights / source_weights.sum()
    sources = rng.choice(source_names, size=n_rows, p=source_weights)

    start_date = datetime.utcnow() - timedelta(days=180)
    signup_offsets = rng.integers(0, 180, size=n_rows)
    # Inject a couple of anomalous high-volume days to demo anomaly detection
    anomaly_offsets = rng.choice(range(20, 170), size=anomaly_days, replace=False)
    extra_rows = []
    signup_dates = [start_date + timedelta(days=int(o)) for o in signup_offsets]

    campaigns = rng.choice(CAMPAIGNS, size=n_rows)
    industries = rng.choice(INDUSTRIES, size=n_rows)
    countries = rng.choice(COUNTRIES, size=n_rows)
    company_sizes = rng.choice(COMPANY_SIZES, size=n_rows, p=[0.35, 0.30, 0.20, 0.10, 0.05])
    products = rng.choice(PRODUCTS, size=n_rows, p=[0.6, 0.25, 0.15])
    plans = rng.choice(PLANS, size=n_rows, p=[0.35, 0.30, 0.25, 0.10])

    rows = []
    for i in range(n_rows):
        source = sources[i]
        weight, conv_mult, engagement_boost = SOURCES[source]
        signup_date = signup_dates[i]

        base_engagement = np.clip(rng.normal(55, 20) + engagement_boost * 100, 0, 100)

        # Funnel progression - each stage depends probabilistically on the previous
        reaches_trial = rng.random() < min(0.98, 0.55 * conv_mult)
        trial_start = signup_date + timedelta(days=int(rng.integers(0, 4))) if reaches_trial else None

        reaches_activation = reaches_trial and rng.random() < min(0.95, 0.5 * conv_mult + base_engagement / 300)
        activation_date = trial_start + timedelta(days=int(rng.integers(1, 8))) if reaches_activation and trial_start else None

        reaches_payment = reaches_activation and rng.random() < min(0.9, 0.35 * conv_mult + base_engagement / 400)
        payment_date = activation_date + timedelta(days=int(rng.integers(1, 14))) if reaches_payment and activation_date else None

        plan = plans[i] if reaches_payment else ("Free" if reaches_activation else None)
        revenue = 0.0
        if reaches_payment:
            plan_price = {"Free": 0, "Starter": rng.uniform(20, 60), "Pro": rng.uniform(80, 250), "Enterprise": rng.uniform(500, 2500)}
            revenue = round(float(plan_price.get(plan, rng.uniform(30, 150))), 2)

        sessions = max(0, int(rng.normal(8 + base_engagement / 8, 6)))
        pages_viewed = max(0, int(sessions * rng.uniform(1.5, 4.5)))
        emails_opened = max(0, int(rng.poisson(3 if reaches_trial else 1)))
        support_tickets = max(0, int(rng.poisson(0.4)))

        churn = None
        if reaches_payment:
            churn = bool(rng.random() < (0.25 if base_engagement < 40 else 0.08))

        status = "churned" if churn else ("paying" if reaches_payment else "activated" if reaches_activation else "trial" if reaches_trial else "lead")

        rows.append({
            "lead_id": f"L{i+1:06d}",
            "customer_id": f"C{i+1:06d}" if reaches_payment else None,
            "name": f"Contact {i+1}",
            "email": f"contact{i+1}@example.com",
            "signup_date": signup_date.strftime("%Y-%m-%d"),
            "source": source,
            "campaign": campaigns[i],
            "industry": industries[i],
            "country": countries[i],
            "company_size": company_sizes[i],
            "product": products[i],
            "plan": plan,
            "trial_start": trial_start.strftime("%Y-%m-%d") if trial_start else None,
            "activation_date": activation_date.strftime("%Y-%m-%d") if activation_date else None,
            "payment_date": payment_date.strftime("%Y-%m-%d") if payment_date else None,
            "revenue": revenue,
            "engagement_score": round(float(base_engagement), 1),
            "number_of_sessions": sessions,
            "pages_viewed": pages_viewed,
            "emails_opened": emails_opened,
            "support_tickets": support_tickets,
            "churn": churn,
            "status": status,
        })

    df = pd.DataFrame(rows)

    # Inject a small amount of messy data on purpose so the cleaning
    # pipeline has something real to do (duplicates, bad dates, negative
    # revenue, out-of-range engagement, inconsistent casing).
    dup_idx = rng.choice(df.index, size=max(1, n_rows // 100), replace=False)
    df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)

    bad_date_idx = rng.choice(df.index, size=max(1, n_rows // 200), replace=False)
    df.loc[bad_date_idx, "signup_date"] = "not-a-date"

    neg_rev_idx = rng.choice(df.index, size=max(1, n_rows // 300), replace=False)
    df.loc[neg_rev_idx, "revenue"] = -abs(df.loc[neg_rev_idx, "revenue"].fillna(10)) - 1

    oob_eng_idx = rng.choice(df.index, size=max(1, n_rows // 250), replace=False)
    df.loc[oob_eng_idx, "engagement_score"] = 150

    case_idx = rng.choice(df.index, size=max(1, n_rows // 20), replace=False)
    df.loc[case_idx, "source"] = df.loc[case_idx, "source"].str.upper()

    return df.sample(frac=1, random_state=seed).reset_index(drop=True)  # shuffle rows


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic lead/customer data.")
    parser.add_argument("--rows", type=int, default=5000, help="Number of base rows to generate.")
    parser.add_argument("--out", type=str, default="sample_data.csv", help="Output CSV path.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = generate(args.rows, seed=args.seed)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} rows ({args.rows} base + duplicates) to {args.out}")


if __name__ == "__main__":
    main()
