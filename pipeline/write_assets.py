content = '''from dagster import asset, Output
from pymongo import MongoClient
from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np

DB_URI = "postgresql://ecommerce_user:ecommerce_pass@localhost:5432/ecommerce_db"
MONGO_URI = "mongodb://localhost:27017/"

@asset(group_name="criteo")
def criteo_raw():
    client = MongoClient(MONGO_URI)
    db = client["ecommerce_db"]
    df = pd.DataFrame(list(db["criteo_raw"].find()))
    df = df.drop(columns=["_id"], errors="ignore")
    return Output(df, metadata={"num_records": len(df)})

@asset(group_name="criteo")
def criteo_clean(criteo_raw):
    df = criteo_raw.copy()
    if "time_since_last_click" not in df.columns:
        return Output(df, metadata={"num_records": len(df), "note": "already processed"})
    before = len(df)
    df = df.drop_duplicates()
    df["time_since_last_click"] = pd.to_numeric(df["time_since_last_click"], errors="coerce")
    df["time_since_last_click"] = df["time_since_last_click"].replace(-1, None)
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    df["cost"] = df["cost"].fillna(df["cost"].median())
    df["cpo"] = pd.to_numeric(df["cpo"], errors="coerce")
    df["cpo"] = df["cpo"].fillna(df["cpo"].median())
    df["campaign"] = df["campaign"].astype(str).str.replace("CAMP_", "", regex=False).str.upper()
    df["campaign"] = df["campaign"].replace("NAN", None).fillna("UNKNOWN")
    df["conversion"] = pd.to_numeric(df["conversion"], errors="coerce")
    df["attribution"] = pd.to_numeric(df["attribution"], errors="coerce")
    df["click"] = pd.to_numeric(df["click"], errors="coerce")
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["timestamp"] = pd.to_datetime(
        df["timestamp"].where(df["timestamp"] > 0), unit="s", errors="coerce"
    )
    cost_99 = df["cost"].quantile(0.99)
    df = df[df["cost"] <= cost_99]
    if "conversion_rate" not in df.columns:
        campaign_conversions = df.groupby("campaign")["conversion"].mean()
        df["conversion_rate"] = df["campaign"].map(campaign_conversions)
    if "click_recency_bucket" not in df.columns:
        def time_bucket(val):
            if pd.isnull(val): return "no_click"
            elif val < 3600: return "within_1hr"
            elif val < 86400: return "within_1day"
            elif val < 604800: return "within_1week"
            else: return "over_1week"
        df["click_recency_bucket"] = df["time_since_last_click"].apply(time_bucket)
    if "event_date" not in df.columns:
        df["event_date"] = df["timestamp"].dt.date.astype(str)
        df["event_hour"] = df["timestamp"].dt.hour
        df["event_dayofweek"] = df["timestamp"].dt.day_name()
    return Output(df, metadata={"num_records": len(df), "rows_removed": before - len(df)})

@asset(group_name="criteo")
def criteo_to_postgres(criteo_clean):
    engine = create_engine(DB_URI)
    df = criteo_clean.copy()
    if "timestamp" in df.columns:
        df["timestamp"] = df["timestamp"].astype(str)
    df.to_sql("criteo_clean", engine, if_exists="replace", index=False)
    result = pd.read_sql("SELECT COUNT(*) as count FROM criteo_clean", engine)
    return Output(int(result["count"][0]), metadata={"rows_loaded": int(result["count"][0])})

@asset(group_name="amazon")
def amazon_raw():
    client = MongoClient(MONGO_URI)
    db = client["ecommerce_db"]
    df = pd.DataFrame(list(db["amazon_raw"].find()))
    df = df.drop(columns=["_id"], errors="ignore")
    return Output(df, metadata={"num_records": len(df)})

@asset(group_name="amazon")
def amazon_clean(amazon_raw):
    df = amazon_raw.copy()
    if "Order Date" in df.columns:
        df = df.rename(columns={
            "Order Date": "order_date",
            "Purchase Price Per Unit": "price_per_unit",
            "Quantity": "quantity",
            "Shipping Address State": "state",
            "Title": "title",
            "ASIN/ISBN (Product Code)": "product_code",
            "Category": "category",
            "Survey ResponseID": "customer_id"
        })
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["price_per_unit"] = pd.to_numeric(df["price_per_unit"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    if "title" in df.columns:
        df["title"] = df["title"].fillna("Unknown")
    df = df.dropna(subset=["price_per_unit", "quantity"])
    if "line_revenue" not in df.columns:
        df["line_revenue"] = df["price_per_unit"] * df["quantity"]
    if "is_cancellation" not in df.columns:
        df["is_cancellation"] = ((df["quantity"] < 0) | (df["price_per_unit"] == 0)).astype(int)
    if "invoice_hour" not in df.columns:
        df["invoice_hour"] = df["order_date"].dt.hour
        df["day_of_week"] = df["order_date"].dt.day_name()
        df["is_weekend"] = df["order_date"].dt.dayofweek.isin([5, 6]).astype(int)
        df["quarter"] = df["order_date"].dt.quarter
        df["month"] = df["order_date"].dt.month
        df["year"] = df["order_date"].dt.year
    if "price_band" not in df.columns:
        def price_band(price):
            if price < 10: return "under_10"
            elif price < 25: return "10_to_25"
            elif price < 50: return "25_to_50"
            elif price < 100: return "50_to_100"
            else: return "over_100"
        df["price_band"] = df["price_per_unit"].apply(price_band)
    return Output(df, metadata={"num_records": len(df)})

@asset(group_name="amazon")
def amazon_rfm(amazon_clean):
    df = amazon_clean.copy()
    if "segment" in df.columns:
        rfm = df[["customer_id", "r_score", "f_score", "m_score", "rfm_score", "segment"]].drop_duplicates()
        return Output(rfm, metadata={"num_customers": len(rfm)})
    df_orders = df[df["is_cancellation"] == 0].copy()
    reference_date = df_orders["order_date"].max() + pd.Timedelta(days=1)
    rfm = df_orders.groupby("customer_id").agg(
        recency=("order_date", lambda x: (reference_date - x.max()).days),
        frequency=("order_date", "count"),
        monetary=("line_revenue", "sum")
    ).reset_index()
    rfm["r_score"] = pd.qcut(rfm["recency"], q=4, labels=[4,3,2,1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=4, labels=[1,2,3,4]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), q=4, labels=[1,2,3,4]).astype(int)
    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]
    def rfm_segment(score):
        if score >= 10: return "Champions"
        elif score >= 7: return "Loyal"
        elif score >= 5: return "At Risk"
        else: return "Lapsed"
    rfm["segment"] = rfm["rfm_score"].apply(rfm_segment)
    return Output(rfm, metadata={"num_customers": len(rfm)})

@asset(group_name="amazon")
def amazon_to_postgres(amazon_clean, amazon_rfm):
    engine = create_engine(DB_URI)
    df = amazon_clean.copy()
    df["order_date"] = df["order_date"].astype(str)
    df.to_sql("amazon_clean", engine, if_exists="replace", index=False)
    amazon_rfm.to_sql("amazon_rfm", engine, if_exists="replace", index=False)
    r1 = pd.read_sql("SELECT COUNT(*) as count FROM amazon_clean", engine)
    r2 = pd.read_sql("SELECT COUNT(*) as count FROM amazon_rfm", engine)
    return Output(
        {"amazon_clean": int(r1["count"][0]), "amazon_rfm": int(r2["count"][0])},
        metadata={"amazon_clean_rows": int(r1["count"][0]), "amazon_rfm_rows": int(r2["count"][0])}
    )

@asset(group_name="uci")
def uci_raw():
    client = MongoClient(MONGO_URI)
    db = client["ecommerce_db"]
    df = pd.DataFrame(list(db["uci_raw"].find()))
    df = df.drop(columns=["_id"], errors="ignore")
    return Output(df, metadata={"num_records": len(df)})

@asset(group_name="uci")
def uci_clean(uci_raw):
    df = uci_raw.copy()
    df = df.drop_duplicates()
    if "Revenue" in df.columns:
        df = df.rename(columns={"Revenue": "is_conversion"})
    df["is_conversion"] = df["is_conversion"].astype(int)
    df["Weekend"] = df["Weekend"].astype(int)
    if "visitor_type_encoded" not in df.columns:
        le = LabelEncoder()
        df["visitor_type_encoded"] = le.fit_transform(df["VisitorType"])
        df["month_encoded"] = le.fit_transform(df["Month"])
    if "total_pages" not in df.columns:
        df["total_pages"] = df["Administrative"] + df["Informational"] + df["ProductRelated"]
        df["total_duration"] = (
            df["Administrative_Duration"] +
            df["Informational_Duration"] +
            df["ProductRelated_Duration"]
        )
        df["avg_duration_per_page"] = df.apply(
            lambda row: row["total_duration"] / row["total_pages"]
            if row["total_pages"] > 0 else 0, axis=1
        )
    if "high_intent" not in df.columns:
        median_pv = df["PageValues"].median()
        df["high_intent"] = (df["PageValues"] > median_pv).astype(int)
        df["is_bounce"] = (df["BounceRates"] > df["BounceRates"].median()).astype(int)
        df["session_quality"] = (
            df["PageValues"] * 0.4 +
            (1 - df["BounceRates"]) * 0.3 +
            (1 - df["ExitRates"]) * 0.3
        )
    return Output(df, metadata={"num_records": len(df), "conversion_rate": float(df["is_conversion"].mean() * 100)})

@asset(group_name="uci")
def uci_to_postgres(uci_clean):
    engine = create_engine(DB_URI)
    uci_clean.to_sql("uci_clean", engine, if_exists="replace", index=False)
    result = pd.read_sql("SELECT COUNT(*) as count FROM uci_clean", engine)
    return Output(int(result["count"][0]), metadata={"rows_loaded": int(result["count"][0])})
'''

with open("pipeline/assets.py", "w") as f:
    f.write(content.strip())

print("assets.py written successfully")
print("Lines:", len(content.strip().splitlines()))
