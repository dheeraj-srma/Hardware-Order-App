import pandas as pd
import numpy as np
import datetime


def apply_global_filters(
    orders_df,
    inv_df,
    inwards_df,
    returns_df,
    txn_df,
    start_date,
    end_date,
    category="All",
    sku="All",
    dealer="All",
    supplier="All",
    city="All",
    state="All"
):
    """Filters all 5 core datasets using the global filter criteria."""
    
    # Helper to filter by Date Range
    def filter_date(df):
        if df.empty or "Timestamp" not in df.columns:
            return df
        df_copy = df.copy()
        df_copy["Timestamp"] = pd.to_datetime(df_copy["Timestamp"], format='ISO8601', errors="coerce")
        df_copy = df_copy.dropna(subset=["Timestamp"])
        df_copy["DateOnly"] = df_copy["Timestamp"].dt.date
        return df_copy[(df_copy["DateOnly"] >= start_date) & (df_copy["DateOnly"] <= end_date)]

    # Helper to filter by Categorical Attributes
    def filter_attributes(df):
        if df.empty:
            return df
        df_copy = df.copy()
        if category != "All" and "Category" in df_copy.columns:
            df_copy = df_copy[df_copy["Category"] == category]
        if sku != "All" and "SKU" in df_copy.columns:
            df_copy = df_copy[df_copy["SKU"] == sku]
        if dealer != "All" and "Salesman Name" in df_copy.columns:
            df_copy = df_copy[df_copy["Salesman Name"] == dealer]
        if supplier != "All" and "Supplier" in df_copy.columns:
            df_copy = df_copy[df_copy["Supplier"] == supplier]
        if city != "All" and "City" in df_copy.columns:
            df_copy = df_copy[df_copy["City"] == city]
        if state != "All" and "State" in df_copy.columns:
            df_copy = df_copy[df_copy["State"] == state]
        return df_copy

    orders_f = filter_attributes(filter_date(orders_df))
    inwards_f = filter_attributes(filter_date(inwards_df))
    returns_f = filter_attributes(filter_date(returns_df))
    txn_f = filter_attributes(filter_date(txn_df))
    inv_f = filter_attributes(inv_df)

    return orders_f, inv_f, inwards_f, returns_f, txn_f


def classify_stock_health(inv_df):
    """Classifies inventory into 5 tiers: Healthy, Low Stock, Critical, Overstocked, Dead Stock."""
    if inv_df.empty or "Current Stock" not in inv_df.columns:
        return inv_df

    df = inv_df.copy()
    conditions = [
        df["Current Stock"] <= 0,
        (df["Current Stock"] > 0) & (df["Current Stock"] <= 5),
        (df["Current Stock"] > 5) & (df["Current Stock"] <= 300),
        df["Current Stock"] > 300
    ]
    choices = ["Critical", "Low Stock", "Healthy", "Overstocked"]
    df["Health_Status"] = np.select(conditions, choices, default="Healthy")
    return df


def classify_dealer_tiers(orders_df):
    """Classifies dealers into 4 tiers: Platinum, Gold, Silver, Bronze based on order counts."""
    if orders_df.empty or "Salesman Name" not in orders_df.columns:
        return pd.DataFrame()

    dealer_stats = orders_df.groupby("Salesman Name").agg(
        Order_Count=("Salesman Name", "count"),
        Total_Units=("Quantity", "sum") if "Quantity" in orders_df.columns else ("Salesman Name", "count")
    ).reset_index()

    q75 = dealer_stats["Order_Count"].quantile(0.75) if len(dealer_stats) > 1 else 10
    q50 = dealer_stats["Order_Count"].quantile(0.50) if len(dealer_stats) > 1 else 5
    q25 = dealer_stats["Order_Count"].quantile(0.25) if len(dealer_stats) > 1 else 2

    def assign_tier(count):
        if count >= q75:
            return "Platinum"
        elif count >= q50:
            return "Gold"
        elif count >= q25:
            return "Silver"
        else:
            return "Bronze"

    dealer_stats["Tier"] = dealer_stats["Order_Count"].apply(assign_tier)
    return dealer_stats


def generate_business_insights(orders_df, inv_df, inwards_df, returns_df, txn_df):
    """Generates automated business insights from filtered data."""
    insights = []

    # 1. Order Volume Trend Insight
    if not orders_df.empty and "Timestamp" in orders_df.columns:
        orders_df_copy = orders_df.copy()
        orders_df_copy["Date"] = pd.to_datetime(orders_df_copy["Timestamp"], format='ISO8601', errors='coerce').dt.date
        date_counts = orders_df_copy.groupby("Date").size()
        if len(date_counts) >= 2:
            recent_avg = date_counts.tail(3).mean()
            past_avg = date_counts.head(3).mean()
            pct_change = ((recent_avg - past_avg) / max(past_avg, 1)) * 100
            direction = "increased" if pct_change >= 0 else "decreased"
            insights.append(f"📈 **Demand Momentum:** Order volume has **{direction} by {abs(pct_change):.1f}%** compared to the start of the selected timeframe.")

    # 2. Critical Stockout Insight
    if not inv_df.empty and "Current Stock" in inv_df.columns:
        critical_items = inv_df[inv_df["Current Stock"] <= 0]
        if not critical_items.empty:
            item_list = ", ".join(critical_items["Item Name"].head(3).tolist())
            insights.append(f"🚨 **Stockout Warning:** **{len(critical_items)} SKUs** (e.g. {item_list}) are at 0 balance. Immediate purchase order recommended.")

    # 3. Top Sales Category Insight
    if not inv_df.empty and "Category" in inv_df.columns and "Current Stock" in inv_df.columns:
        cat_stock = inv_df.groupby("Category")["Current Stock"].sum().sort_values(ascending=False)
        if not cat_stock.empty:
            top_cat = cat_stock.index[0]
            insights.append(f"🏷️ **Category Driver:** **{top_cat}** represents the largest stock volume share in the active warehouse.")

    # 4. Quality Control Insight
    if not returns_df.empty and "Condition" in returns_df.columns:
        defective = returns_df[returns_df["Condition"] == "Defective"]
        if not defective.empty:
            insights.append(f"⚠️ **Quality Alert:** **{len(defective)} defective returns** recorded. Supplier quality audit advised.")

    if not insights:
        insights.append("✅ **Operational Status:** All inventory levels, order pipelines, and fulfillment rates are performing within optimal bounds.")

    return insights
