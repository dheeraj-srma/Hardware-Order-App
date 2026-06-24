import math
from datetime import date, datetime

import uuid

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_gsheets import GSheetsConnection


st.set_page_config(
    page_title="Nalka Metals Portal",
    page_icon="NM",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_URL = "https://docs.google.com/spreadsheets/d/1hz6YQYPUicMGKc7c05a5X4S_W1Y_bbJDNK83XWviLYI/edit?usp=sharing"

SHEET_ALIASES = {
    "inventory": ["Inventory"],
    "orders": ["Orders"],
    "inwards": ["Inwards"],
    "returns": ["Returns"],
    "transactions": ["Inventory Transactions", "Inventory Transaction"],
    "dealers": ["Dealers", "Dealer Database"],
    "suppliers": ["Suppliers", "Supplier Database"],
}

COLOR_SEQUENCE = ["#1F77B4", "#2CA02C", "#FF7F0E", "#D62728", "#17BECF", "#9467BD"]
px.defaults.template = "plotly_dark"


st.markdown(
    """
    <style>
        :root {
            --app-bg: #0b0f17;
            --surface: #111827;
            --surface-2: #162033;
            --surface-3: #1f2937;
            --line: #273449;
            --text: #e8edf6;
            --muted: #98a2b3;
            --brand: #3b82f6;
            --brand-2: #22c55e;
            --danger: #f87171;
            --warning: #f59e0b;
        }

        .stApp {
            background: var(--app-bg);
            color: var(--text);
        }

        .block-container {
            max-width: 1440px;
            padding-top: 1.25rem;
            padding-bottom: 2.5rem;
        }

        h1, h2, h3 {
            color: var(--text);
            letter-spacing: 0;
        }

        p, label, span, div {
            letter-spacing: 0;
        }

        .app-hero {
            background: linear-gradient(135deg, rgba(59,130,246,0.20), rgba(34,197,94,0.08) 48%, rgba(17,24,39,0.78));
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 18px 20px;
            margin-bottom: 18px;
        }

        .app-eyebrow {
            color: #93c5fd;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        .app-title {
            color: var(--text);
            font-size: clamp(1.65rem, 2.4vw, 2.35rem);
            font-weight: 750;
            line-height: 1.1;
            margin: 0;
        }

        .app-subtitle {
            color: #c7d2e5;
            max-width: 880px;
            margin: 8px 0 0 0;
            font-size: 0.98rem;
        }

        .section-kicker {
            color: #93c5fd;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin: 18px 0 2px 0;
        }

        .section-title {
            color: var(--text);
            font-size: 1.45rem;
            font-weight: 730;
            margin: 0 0 12px 0;
        }

        .panel-note {
            color: var(--muted);
            font-size: 0.9rem;
            margin-top: -6px;
            margin-bottom: 14px;
        }

        [data-testid="stMetric"] {
            background: linear-gradient(180deg, #151f31, #101827);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px 18px;
            min-height: 112px;
            box-shadow: 0 14px 32px rgba(0, 0, 0, 0.18);
        }
        [data-testid="stMetric"] label,
        [data-testid="stMetric"] [data-testid="stMetricLabel"],
        [data-testid="stMetric"] [data-testid="stMetricValue"],
        [data-testid="stMetric"] div {
            color: var(--text) !important;
        }

        [data-testid="stMetric"] label,
        [data-testid="stMetric"] [data-testid="stMetricLabel"] {
            color: #a7b3c7 !important;
            font-size: 0.86rem !important;
        }

        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 760 !important;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
            background: var(--surface);
        }

        div[data-testid="stTabs"] button {
            color: #b8c2d6;
            border-radius: 8px 8px 0 0;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #ffffff;
            background: rgba(59, 130, 246, 0.16);
            border-bottom-color: #3b82f6;
        }

        .stButton > button {
            border-radius: 8px;
            border: 1px solid var(--line);
            background: #172033;
            color: var(--text);
            font-weight: 700;
            min-height: 40px;
        }

        .stButton > button[kind="primary"],
        .stButton > button:hover {
            border-color: #60a5fa;
            background: #1d4ed8;
            color: #ffffff;
        }

        input, textarea, [data-baseweb="select"] > div {
            border-radius: 8px !important;
        }
        .insight-card {
            border-left: 4px solid var(--brand);
            background: rgba(59,130,246,0.12);
            border-top: 1px solid rgba(59,130,246,0.18);
            border-right: 1px solid rgba(59,130,246,0.18);
            border-bottom: 1px solid rgba(59,130,246,0.18);
            border-radius: 8px;
            padding: 12px 14px;
            margin: 8px 0;
            color: #dbeafe;
            font-size: 0.95rem;
        }
        .risk-card {
            border-left: 4px solid var(--danger);
            background: rgba(248,113,113,0.12);
            border-top: 1px solid rgba(248,113,113,0.18);
            border-right: 1px solid rgba(248,113,113,0.18);
            border-bottom: 1px solid rgba(248,113,113,0.18);
            border-radius: 8px;
            padding: 12px 14px;
            margin: 8px 0;
            color: #fee2e2;
            font-size: 0.95rem;
        }
        .small-muted { color: var(--muted); font-size: 0.88rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    rename_map = {
        "Store Name": "Shop Name",
        "Item Category": "Category",
        "Quantity": "Qty",
        "Supplier Name": "Supplier",
    }
    return df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})


def render_hero(title: str, subtitle: str, eyebrow: str = "Nalka Metals") -> None:
    st.markdown(
        f"""
        <div class="app-hero">
            <div class="app-eyebrow">{eyebrow}</div>
            <div class="app-title">{title}</div>
            <div class="app-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section(title: str, kicker: str | None = None, note: str | None = None) -> None:
    kicker_html = f'<div class="section-kicker">{kicker}</div>' if kicker else ""
    note_html = f'<div class="panel-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        {kicker_html}
        <div class="section-title">{title}</div>
        {note_html}
        """,
        unsafe_allow_html=True,
    )


def ensure_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA
    return df


def parse_datetime_column(df: pd.DataFrame, column: str = "Timestamp") -> pd.DataFrame:
    df = df.copy()
    if column in df.columns:
        df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def parse_numeric_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    df = df.copy()
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    return df


def parse_text_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
            df[col] = df[col].replace("", pd.NA)
    return df


def standardize_table(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    df = clean_columns(df)
    if table_name == "inventory":
        df = ensure_columns(df, ["SKU", "Category", "Item Name", "Current Stock"])
        df = parse_text_columns(df, ["SKU", "Category", "Item Name"])
        df = parse_numeric_column(df, "Current Stock")
    elif table_name in {"orders", "inwards", "returns"}:
        df = ensure_columns(df, ["Timestamp", "Category", "SKU", "Item Name", "Qty"])
        df = parse_text_columns(
            df,
            ["SKU", "Category", "Item Name", "Dealer Name", "Shop Name", "Supplier", "Condition", "Reason", "Status", "City", "State"],
        )
        df = parse_datetime_column(df)
        df = parse_numeric_column(df, "Qty")
    elif table_name == "transactions":
        df = ensure_columns(df, ["Timestamp", "Type", "SKU", "Item Name", "Category", "Qty"])
        df = parse_text_columns(df, ["Type", "SKU", "Item Name", "Category", "User", "Reference"])
        df = parse_datetime_column(df)
        df = parse_numeric_column(df, "Qty")
    elif table_name == "dealers":
        df = ensure_columns(df, ["Dealer Name", "Shop Name", "City", "State", "Dealer Type"])
        df = parse_text_columns(df, ["Dealer Name", "Shop Name", "City", "State", "Dealer Type"])
    elif table_name == "suppliers":
        df = ensure_columns(df, ["Supplier", "City", "State", "Specialization"])
        df = parse_text_columns(df, ["Supplier", "City", "State", "Specialization"])
    return df


def read_first_available_sheet(conn: GSheetsConnection, table_name: str) -> pd.DataFrame:
    for sheet_name in SHEET_ALIASES[table_name]:
        try:
            data = conn.read(spreadsheet=DB_URL, worksheet=sheet_name, ttl=300)
            if isinstance(data, pd.DataFrame) and not data.empty:
                return standardize_table(data, table_name)
        except Exception:
            continue
    return standardize_table(pd.DataFrame(), table_name)


@st.cache_data(ttl=300, show_spinner=False)
def load_database() -> dict[str, pd.DataFrame]:
    conn = st.connection("gsheets", type=GSheetsConnection)
    return {name: read_first_available_sheet(conn, name) for name in SHEET_ALIASES}


def enrich_orders(orders: pd.DataFrame, dealers: pd.DataFrame) -> pd.DataFrame:
    orders = orders.copy()
    if orders.empty:
        return orders

    merge_cols = ["Dealer Name", "Shop Name"]
    has_dealer_key = all(col in orders.columns and col in dealers.columns for col in merge_cols)
    if has_dealer_key and not dealers.empty:
        dealer_lookup = dealers.drop_duplicates(merge_cols)[merge_cols + ["City", "State", "Dealer Type"]]
        orders = orders.merge(dealer_lookup, how="left", on=merge_cols, suffixes=("", "_Dealer"))
    elif "Dealer Name" in orders.columns and "Dealer Name" in dealers.columns and not dealers.empty:
        dealer_lookup = dealers.drop_duplicates("Dealer Name")[["Dealer Name", "City", "State", "Dealer Type"]]
        orders = orders.merge(dealer_lookup, how="left", on="Dealer Name", suffixes=("", "_Dealer"))

    return orders


def apply_order_filters(
    orders: pd.DataFrame,
    start_date: date,
    end_date: date,
    categories: list[str],
    skus: list[str],
    dealers: list[str],
    cities: list[str],
    states: list[str],
) -> pd.DataFrame:
    df = orders.copy()
    if "Timestamp" in df.columns:
        df = df[df["Timestamp"].dt.date.between(start_date, end_date)]
    if categories:
        df = df[df["Category"].isin(categories)]
    if skus:
        df = df[df["SKU"].isin(skus)]
    if dealers and "Dealer Name" in df.columns:
        df = df[df["Dealer Name"].isin(dealers)]
    if cities and "City" in df.columns:
        df = df[df["City"].isin(cities)]
    if states and "State" in df.columns:
        df = df[df["State"].isin(states)]
    return df


def apply_stock_filters(inventory: pd.DataFrame, categories: list[str], skus: list[str]) -> pd.DataFrame:
    df = inventory.copy()
    if categories:
        df = df[df["Category"].isin(categories)]
    if skus:
        df = df[df["SKU"].isin(skus)]
    return df


def apply_activity_filters(
    df: pd.DataFrame,
    start_date: date,
    end_date: date,
    categories: list[str],
    skus: list[str],
) -> pd.DataFrame:
    filtered = df.copy()
    if "Timestamp" in filtered.columns:
        filtered = filtered[filtered["Timestamp"].dt.date.between(start_date, end_date)]
    if categories:
        filtered = filtered[filtered["Category"].isin(categories)]
    if skus:
        filtered = filtered[filtered["SKU"].isin(skus)]
    return filtered


def period_summary(df: pd.DataFrame, freq: str, metric_name: str = "Qty") -> pd.DataFrame:
    if df.empty or "Timestamp" not in df.columns:
        return pd.DataFrame(columns=["Period", metric_name])
    grouped = (
        df.dropna(subset=["Timestamp"])
        .set_index("Timestamp")
        .resample(freq)["Qty"]
        .sum()
        .reset_index()
        .rename(columns={"Timestamp": "Period", "Qty": metric_name})
    )
    return grouped


def top_n(df: pd.DataFrame, group_col: str, value_col: str = "Qty", n: int = 10) -> pd.DataFrame:
    if df.empty or group_col not in df.columns:
        return pd.DataFrame(columns=[group_col, value_col])
    return (
        df.groupby(group_col, dropna=False)[value_col]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )


def percent_delta(current: float, previous: float) -> float | None:
    if previous == 0 or pd.isna(previous):
        return None
    return ((current - previous) / previous) * 100


def format_number(value: float) -> str:
    if pd.isna(value):
        return "0"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def make_line(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = px.line(df, x=x, y=y, markers=True, title=title, color_discrete_sequence=COLOR_SEQUENCE)
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=55, b=10),
        hovermode="x unified",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#dbe4f0"),
        title_font=dict(color="#f8fafc", size=17),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="#263244", zerolinecolor="#263244")
    fig.update_yaxes(gridcolor="#263244", zerolinecolor="#263244")
    return fig


def make_bar(df: pd.DataFrame, x: str, y: str, title: str, orientation: str = "v") -> go.Figure:
    fig = px.bar(df, x=x, y=y, title=title, orientation=orientation, color_discrete_sequence=COLOR_SEQUENCE)
    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=55, b=10),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#dbe4f0"),
        title_font=dict(color="#f8fafc", size=17),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="#263244", zerolinecolor="#263244")
    fig.update_yaxes(gridcolor="#263244", zerolinecolor="#263244")
    return fig


def show_insight(text: str, risk: bool = False) -> None:
    css_class = "risk-card" if risk else "insight-card"
    st.markdown(f'<div class="{css_class}">{text}</div>', unsafe_allow_html=True)


def generate_executive_insights(orders: pd.DataFrame, returns: pd.DataFrame, inventory: pd.DataFrame) -> list[tuple[str, bool]]:
    insights: list[tuple[str, bool]] = []
    monthly = period_summary(orders, "ME", "Demand")
    if len(monthly) >= 2:
        current = monthly.iloc[-1]["Demand"]
        previous = monthly.iloc[-2]["Demand"]
        delta = percent_delta(current, previous)
        if delta is not None:
            direction = "increased" if delta >= 0 else "decreased"
            insights.append((f"Monthly demand {direction} {abs(delta):.1f}% versus the previous month.", delta < -15))

    if "Category" in orders.columns and not orders.empty:
        category_perf = top_n(orders, "Category", "Qty", 1)
        if not category_perf.empty:
            row = category_perf.iloc[0]
            share = row["Qty"] / max(orders["Qty"].sum(), 1) * 100
            insights.append((f"{row['Category']} is the largest demand driver, contributing {share:.1f}% of filtered demand.", False))

    if not returns.empty and not orders.empty:
        return_rate = returns["Qty"].sum() / max(orders["Qty"].sum(), 1) * 100
        if return_rate > 8:
            insights.append((f"Return rate is elevated at {return_rate:.1f}%; review product quality and dealer handling patterns.", True))
        else:
            insights.append((f"Return rate is controlled at {return_rate:.1f}% of ordered units.", False))

    if not inventory.empty:
        critical_count = (inventory["Current Stock"] <= 0).sum()
        if critical_count:
            insights.append((f"{critical_count} SKUs have zero or negative stock and require replenishment review.", True))

    return insights[:5]


def classify_inventory(inventory: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    stock = inventory.copy()
    if not orders.empty and "SKU" in orders.columns:
        demand = orders.groupby("SKU").agg(
            **{
                "Total Demand": ("Qty", "sum"),
                "Avg Order Qty": ("Qty", "mean"),
                "Last Demand Date": ("Timestamp", "max"),
            }
        )
    else:
        demand = pd.DataFrame(columns=["Total Demand", "Avg Order Qty", "Last Demand Date"])
    stock = stock.merge(demand, how="left", left_on="SKU", right_index=True)
    stock["Total Demand"] = stock["Total Demand"].fillna(0)
    stock["Avg Order Qty"] = stock["Avg Order Qty"].fillna(0)
    stock["Last Demand Date"] = pd.to_datetime(stock["Last Demand Date"], errors="coerce")
    latest_order_date = pd.to_datetime(orders["Timestamp"], errors="coerce").max() if not orders.empty and "Timestamp" in orders.columns else pd.Timestamp.today()
    if pd.isna(latest_order_date):
        latest_order_date = pd.Timestamp.today()
    stock["Days Since Demand"] = (latest_order_date - stock["Last Demand Date"]).dt.days
    stock["Days Since Demand"] = stock["Days Since Demand"].fillna(9999).clip(lower=0)
    median_demand = stock.loc[stock["Total Demand"] > 0, "Total Demand"].median()
    median_demand = 1 if pd.isna(median_demand) or median_demand <= 0 else median_demand

    def classify(row: pd.Series) -> str:
        current = row["Current Stock"]
        demand_qty = row["Total Demand"]
        if demand_qty == 0 and current > 0:
            return "Dead Stock"
        if current <= 0:
            return "Critical"
        if current <= max(row["Avg Order Qty"], 3):
            return "Low Stock"
        if current > median_demand * 4 and demand_qty < median_demand:
            return "Overstocked"
        return "Healthy"

    stock["Stock Health"] = stock.apply(classify, axis=1)
    stock["Turnover Proxy"] = stock["Total Demand"] / stock["Current Stock"].replace(0, pd.NA)
    stock["Turnover Proxy"] = stock["Turnover Proxy"].replace([math.inf, -math.inf], pd.NA).fillna(0)
    stock["Reorder Risk"] = stock["Stock Health"].isin(["Critical", "Low Stock"])
    return stock


def declining_products(orders: pd.DataFrame, days: int = 90) -> pd.DataFrame:
    if orders.empty or "Timestamp" not in orders.columns:
        return pd.DataFrame(columns=["Item Name", "Previous Demand", "Recent Demand", "Demand Change %"])

    latest_date = orders["Timestamp"].max()
    recent_start = latest_date - pd.Timedelta(days=days)
    previous_start = latest_date - pd.Timedelta(days=days * 2)

    recent = orders[orders["Timestamp"].between(recent_start, latest_date)]
    previous = orders[orders["Timestamp"].between(previous_start, recent_start)]

    recent_demand = recent.groupby("Item Name")["Qty"].sum().rename("Recent Demand")
    previous_demand = previous.groupby("Item Name")["Qty"].sum().rename("Previous Demand")
    trend = pd.concat([previous_demand, recent_demand], axis=1).fillna(0).reset_index()
    trend = trend[trend["Previous Demand"] > 0]
    trend["Demand Change %"] = ((trend["Recent Demand"] - trend["Previous Demand"]) / trend["Previous Demand"] * 100).round(1)
    return trend.sort_values("Demand Change %").head(15)


def dealer_analytics(orders: pd.DataFrame) -> pd.DataFrame:
    if orders.empty or "Dealer Name" not in orders.columns:
        return pd.DataFrame(columns=["Dealer Name", "Demand Units", "Orders", "Active Days", "Last Order", "Activity Score", "Tier"])

    grouped = orders.groupby("Dealer Name").agg(
        **{
            "Demand Units": ("Qty", "sum"),
            "Orders": ("Order ID", "nunique") if "Order ID" in orders.columns else ("Timestamp", "count"),
            "Active Days": ("Timestamp", lambda x: x.dt.date.nunique()),
            "Last Order": ("Timestamp", "max"),
        }
    )
    grouped = grouped.reset_index()
    max_demand = max(grouped["Demand Units"].max(), 1)
    max_orders = max(grouped["Orders"].max(), 1)
    grouped["Recency Days"] = (orders["Timestamp"].max() - grouped["Last Order"]).dt.days.fillna(999)
    grouped["Activity Score"] = (
        (grouped["Demand Units"] / max_demand) * 55
        + (grouped["Orders"] / max_orders) * 30
        + (1 - grouped["Recency Days"].clip(upper=180) / 180) * 15
    ).round(1)
    grouped["Tier"] = pd.cut(
        grouped["Activity Score"],
        bins=[-1, 35, 60, 80, 100],
        labels=["Bronze", "Silver", "Gold", "Platinum"],
    ).astype(str)
    grouped["Churn Risk"] = grouped["Recency Days"].apply(lambda days: "High" if days > 90 else "Watch" if days > 45 else "Normal")
    return grouped.sort_values("Activity Score", ascending=False)


def supplier_analytics(inwards: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    if inwards.empty or "Supplier" not in inwards.columns:
        return pd.DataFrame(columns=["Supplier", "Inward Units", "Refills", "Defective Units", "Quality Score"])

    supplier = inwards.groupby("Supplier").agg(
        **{
            "Inward Units": ("Qty", "sum"),
            "Refills": ("Timestamp", "count"),
            "Categories": ("Category", "nunique"),
        }
    )

    defective_by_category = pd.DataFrame(columns=["Category", "Defective Units"])
    if not returns.empty and "Condition" in returns.columns:
        defective = returns[returns["Condition"].astype(str).str.contains("Defective", case=False, na=False)]
        defective_by_category = defective.groupby("Category")["Qty"].sum().reset_index(name="Defective Units")

    supplier_mix = inwards.groupby(["Supplier", "Category"])["Qty"].sum().reset_index()
    supplier_mix = supplier_mix.merge(defective_by_category, how="left", on="Category")
    supplier_mix["Defective Units"] = supplier_mix["Defective Units"].fillna(0)
    supplier_defects = supplier_mix.groupby("Supplier")["Defective Units"].sum()

    supplier["Defective Units"] = supplier.index.map(supplier_defects).fillna(0)
    supplier["Quality Score"] = (100 - supplier["Defective Units"] / supplier["Inward Units"].replace(0, pd.NA) * 100).fillna(100).clip(0, 100).round(1)
    return supplier.reset_index().sort_values("Inward Units", ascending=False)


def render_header() -> None:
    title_col, refresh_col = st.columns([6, 1])
    with title_col:
        render_hero(
            "BI Command Center",
            "Actionable management intelligence across orders, inventory, dealers, suppliers, returns, and regional demand.",
            "Admin analytics",
        )
    with refresh_col:
        st.write("")
        st.write("")
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()


def render_filters(data: dict[str, pd.DataFrame]) -> dict[str, object]:
    orders = enrich_orders(data["orders"], data["dealers"])
    returns = data["returns"]
    inwards = data["inwards"]

    all_dates = pd.concat(
        [
            orders.get("Timestamp", pd.Series(dtype="datetime64[ns]")),
            returns.get("Timestamp", pd.Series(dtype="datetime64[ns]")),
            inwards.get("Timestamp", pd.Series(dtype="datetime64[ns]")),
        ],
        ignore_index=True,
    ).dropna()

    default_start = all_dates.min().date() if not all_dates.empty else date.today()
    default_end = all_dates.max().date() if not all_dates.empty else date.today()

    st.sidebar.header("Business Filters")
    date_range = st.sidebar.date_input("Date Range", value=(default_start, default_end), min_value=default_start, max_value=default_end)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    categories = sorted(pd.concat([data["inventory"]["Category"], orders["Category"], returns["Category"], inwards["Category"]]).dropna().astype(str).unique())
    skus = sorted(pd.concat([data["inventory"]["SKU"], orders["SKU"], returns["SKU"], inwards["SKU"]]).dropna().astype(str).unique())
    dealer_names = sorted(orders["Dealer Name"].dropna().astype(str).unique()) if "Dealer Name" in orders.columns else []
    supplier_names = sorted(inwards["Supplier"].dropna().astype(str).unique()) if "Supplier" in inwards.columns else []
    cities = sorted(orders["City"].dropna().astype(str).unique()) if "City" in orders.columns else []
    states = sorted(orders["State"].dropna().astype(str).unique()) if "State" in orders.columns else []

    return {
        "start_date": start_date,
        "end_date": end_date,
        "categories": st.sidebar.multiselect("Category", categories),
        "skus": st.sidebar.multiselect("SKU", skus),
        "dealers": st.sidebar.multiselect("Dealer", dealer_names),
        "suppliers": st.sidebar.multiselect("Supplier", supplier_names),
        "cities": st.sidebar.multiselect("City", cities),
        "states": st.sidebar.multiselect("State", states),
    }


def render_executive_overview(orders: pd.DataFrame, inventory_health: pd.DataFrame, returns: pd.DataFrame, inwards: pd.DataFrame, data: dict[str, pd.DataFrame]) -> None:
    render_section("Executive Overview", "Business health", "A compact view of demand, stock, dealer reach, returns, and category mix.")
    total_order_rows = len(orders)
    total_units = inventory_health["Current Stock"].sum() if not inventory_health.empty else 0
    active_dealers = orders["Dealer Name"].nunique() if "Dealer Name" in orders.columns else 0
    suppliers = inwards["Supplier"].nunique() if "Supplier" in inwards.columns else data["suppliers"].shape[0]
    total_products = inventory_health["SKU"].nunique() if "SKU" in inventory_health.columns else len(inventory_health)
    ordered_units = orders["Qty"].sum() if not orders.empty else 0
    returned_units = returns["Qty"].sum() if not returns.empty else 0
    defective_units = (
        returns[returns["Condition"].astype(str).str.contains("Defective", case=False, na=False)]["Qty"].sum()
        if not returns.empty and "Condition" in returns.columns
        else 0
    )
    avg_monthly_sales = period_summary(orders, "ME", "Demand")["Demand"].mean() if not orders.empty else 0

    metrics = [
        ("Total Orders", format_number(total_order_rows)),
        ("Total Inventory Units", format_number(total_units)),
        ("Active Dealers", format_number(active_dealers)),
        ("Suppliers", format_number(suppliers)),
        ("Products", format_number(total_products)),
        ("Return Rate", f"{returned_units / max(ordered_units, 1) * 100:.1f}%"),
        ("Defect Rate", f"{defective_units / max(returned_units, 1) * 100:.1f}%"),
        ("Inventory Value Proxy", format_number(total_units)),
        ("Avg Monthly Sales", format_number(avg_monthly_sales)),
    ]
    metric_cols = st.columns(3)
    for idx, (label, value) in enumerate(metrics):
        metric_cols[idx % 3].metric(label, value)

    render_section("Executive Insights", "Auto-generated signals")
    for text, risk in generate_executive_insights(orders, returns, inventory_health):
        show_insight(text, risk=risk)

    c1, c2 = st.columns(2)
    monthly_orders = period_summary(orders.assign(Qty=1), "ME", "Orders")
    monthly_demand = period_summary(orders, "ME", "Demand")
    with c1:
        st.plotly_chart(make_line(monthly_orders, "Period", "Orders", "Monthly Orders Trend"), use_container_width=True)
    with c2:
        st.plotly_chart(make_line(monthly_demand, "Period", "Demand", "Monthly Demand Trend"), use_container_width=True)

    c3, c4 = st.columns(2)
    category = top_n(orders, "Category", "Qty", 12)
    with c3:
        fig = px.pie(category, names="Category", values="Qty", title="Category Contribution Analysis", color_discrete_sequence=COLOR_SEQUENCE)
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        st.plotly_chart(make_bar(category.sort_values("Qty"), "Qty", "Category", "Top Categories", "h"), use_container_width=True)

    growth = monthly_demand.copy()
    if not growth.empty:
        growth["Growth %"] = growth["Demand"].pct_change().mul(100).replace([math.inf, -math.inf], 0).fillna(0)
    st.plotly_chart(make_line(growth, "Period", "Growth %", "Business Growth Trend"), use_container_width=True)


def render_sales_intelligence(orders: pd.DataFrame) -> None:
    render_section("Sales Intelligence", "Demand behavior", "Trends, seasonality, top products, and products losing momentum.")
    c1, c2, c3 = st.columns(3)
    c1.plotly_chart(make_line(period_summary(orders, "D", "Demand"), "Period", "Demand", "Daily Sales Trend"), use_container_width=True)
    c2.plotly_chart(make_line(period_summary(orders, "W", "Demand"), "Period", "Demand", "Weekly Sales Trend"), use_container_width=True)
    c3.plotly_chart(make_line(period_summary(orders, "ME", "Demand"), "Period", "Demand", "Monthly Sales Trend"), use_container_width=True)

    c4, c5 = st.columns(2)
    c4.plotly_chart(make_bar(top_n(orders, "Category", "Qty", 10), "Category", "Qty", "Category Performance"), use_container_width=True)
    c5.plotly_chart(make_bar(top_n(orders, "Item Name", "Qty", 15).sort_values("Qty"), "Qty", "Item Name", "Product Performance", "h"), use_container_width=True)

    product = top_n(orders, "Item Name", "Qty", 50)
    if not product.empty:
        product["Cumulative Share"] = product["Qty"].cumsum() / product["Qty"].sum() * 100
        fig = go.Figure()
        fig.add_bar(x=product["Item Name"], y=product["Qty"], name="Demand Units")
        fig.add_scatter(x=product["Item Name"], y=product["Cumulative Share"], name="Cumulative Share", yaxis="y2")
        fig.update_layout(
            title="Product Pareto Analysis",
            height=420,
            yaxis2=dict(overlaying="y", side="right", ticksuffix="%"),
            margin=dict(l=10, r=10, t=55, b=80),
        )
        st.plotly_chart(fig, use_container_width=True)

    if not orders.empty:
        heat = orders.copy()
        heat["Weekday"] = heat["Timestamp"].dt.day_name()
        heat["Month"] = heat["Timestamp"].dt.strftime("%b")
        pivot = heat.pivot_table(index="Weekday", columns="Month", values="Qty", aggfunc="sum", fill_value=0)
        fig = px.imshow(pivot, title="Demand Heatmap by Weekday and Month", color_continuous_scale="Blues")
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)

        seasonal = heat.groupby(heat["Timestamp"].dt.month_name())["Qty"].sum().reset_index()
        seasonal["Month No"] = pd.to_datetime(seasonal["Timestamp"], format="%B").dt.month
        seasonal = seasonal.sort_values("Month No")
        st.plotly_chart(make_bar(seasonal, "Timestamp", "Qty", "Seasonal Demand Analysis"), use_container_width=True)

    decliners = declining_products(orders)
    if not decliners.empty:
        st.subheader("Products Losing Demand")
        st.dataframe(decliners, hide_index=True, use_container_width=True)


def render_inventory_intelligence(inventory_health: pd.DataFrame) -> None:
    render_section("Inventory Intelligence", "Stock efficiency", "Fast movers, slow movers, dead stock, aging, and replenishment risk.")
    c1, c2 = st.columns(2)
    health_counts = inventory_health["Stock Health"].value_counts().reset_index()
    health_counts.columns = ["Stock Health", "SKU Count"]
    c1.plotly_chart(make_bar(health_counts, "Stock Health", "SKU Count", "Stock Health Classification"), use_container_width=True)
    c2.plotly_chart(make_bar(top_n(inventory_health, "Category", "Current Stock", 12), "Category", "Current Stock", "Inventory Distribution"), use_container_width=True)

    c3, c4 = st.columns(2)
    c3.plotly_chart(make_bar(inventory_health.sort_values("Total Demand", ascending=False).head(15).sort_values("Total Demand"), "Total Demand", "Item Name", "Fast Moving Products", "h"), use_container_width=True)
    slow = inventory_health[inventory_health["Total Demand"] > 0].sort_values("Total Demand").head(15)
    c4.plotly_chart(make_bar(slow, "Total Demand", "Item Name", "Slow Moving Products", "h"), use_container_width=True)

    c5, c6 = st.columns(2)
    dead_stock = inventory_health[inventory_health["Stock Health"] == "Dead Stock"].sort_values("Current Stock", ascending=False).head(20)
    c5.dataframe(dead_stock[["SKU", "Item Name", "Category", "Current Stock", "Total Demand"]], hide_index=True, use_container_width=True)
    c5.caption("Dead Stock Analysis")
    reorder = inventory_health[inventory_health["Reorder Risk"]].sort_values(["Stock Health", "Current Stock"]).head(20)
    c6.dataframe(reorder[["SKU", "Item Name", "Category", "Current Stock", "Total Demand", "Stock Health"]], hide_index=True, use_container_width=True)
    c6.caption("Reorder Risk Dashboard")

    turnover = inventory_health.sort_values("Turnover Proxy", ascending=False).head(20)
    st.plotly_chart(make_bar(turnover.sort_values("Turnover Proxy"), "Turnover Proxy", "Item Name", "Inventory Turnover Analysis", "h"), use_container_width=True)

    aging_bins = inventory_health.copy()
    aging_bins["Aging Bucket"] = pd.cut(
        aging_bins["Days Since Demand"],
        bins=[-1, 30, 90, 180, 365, 10000],
        labels=["0-30 days", "31-90 days", "91-180 days", "181-365 days", "365+ days"],
    )
    aging = aging_bins.groupby("Aging Bucket", observed=False)["Current Stock"].sum().reset_index()
    st.plotly_chart(make_bar(aging, "Aging Bucket", "Current Stock", "Inventory Aging Analysis"), use_container_width=True)

    st.dataframe(
        inventory_health.sort_values(["Stock Health", "Current Stock"])[
            ["SKU", "Item Name", "Category", "Current Stock", "Total Demand", "Days Since Demand", "Turnover Proxy", "Stock Health"]
        ],
        hide_index=True,
        use_container_width=True,
        height=420,
    )


def render_dealer_intelligence(orders: pd.DataFrame) -> None:
    render_section("Dealer Intelligence", "Account performance", "Dealer value, frequency, activity score, tiers, and churn watchlist.")
    dealers = dealer_analytics(orders)
    c1, c2 = st.columns(2)
    c1.plotly_chart(make_bar(dealers.head(15).sort_values("Demand Units"), "Demand Units", "Dealer Name", "Top Dealers", "h"), use_container_width=True)
    tier_counts = dealers["Tier"].value_counts().reindex(["Platinum", "Gold", "Silver", "Bronze"]).dropna().reset_index()
    tier_counts.columns = ["Tier", "Dealers"]
    c2.plotly_chart(make_bar(tier_counts, "Tier", "Dealers", "Dealer Segmentation"), use_container_width=True)

    c3, c4 = st.columns(2)
    c3.plotly_chart(make_bar(dealers.head(15).sort_values("Orders"), "Orders", "Dealer Name", "Dealer Purchase Frequency", "h"), use_container_width=True)
    c4.plotly_chart(make_bar(dealers.head(15).sort_values("Activity Score"), "Activity Score", "Dealer Name", "Dealer Activity Score", "h"), use_container_width=True)

    churn = dealers[dealers["Churn Risk"].isin(["High", "Watch"])].sort_values("Recency Days", ascending=False)
    st.dataframe(churn[["Dealer Name", "Demand Units", "Orders", "Last Order", "Recency Days", "Tier", "Churn Risk"]], hide_index=True, use_container_width=True)


def render_geographic_intelligence(orders: pd.DataFrame) -> None:
    render_section("Geographic Intelligence", "Regional demand", "City, state, and regional growth patterns.")
    c1, c2 = st.columns(2)
    c1.plotly_chart(make_bar(top_n(orders, "City", "Qty", 15).sort_values("Qty"), "Qty", "City", "Orders by City", "h"), use_container_width=True)
    c2.plotly_chart(make_bar(top_n(orders, "State", "Qty", 15), "State", "Qty", "Orders by State"), use_container_width=True)

    if "State" in orders.columns and not orders.empty:
        monthly_region = orders.copy()
        monthly_region["Month"] = monthly_region["Timestamp"].dt.to_period("M").astype(str)
        pivot = monthly_region.pivot_table(index="State", columns="Month", values="Qty", aggfunc="sum", fill_value=0)
        fig = px.imshow(pivot, title="Regional Demand Heatmap", color_continuous_scale="Greens")
        fig.update_layout(height=460, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)

        region = monthly_region.groupby(["State", "Month"])["Qty"].sum().reset_index()
        fig = px.line(region, x="Month", y="Qty", color="State", title="Regional Growth Analysis", markers=True)
        fig.update_layout(height=430, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)


def render_returns_intelligence(returns: pd.DataFrame, orders: pd.DataFrame) -> None:
    render_section("Returns Intelligence", "Quality and replacement signals", "Return rate, defect rate, reasons, and category-level quality issues.")
    c1, c2, c3 = st.columns(3)
    returned_units = returns["Qty"].sum() if not returns.empty else 0
    ordered_units = orders["Qty"].sum() if not orders.empty else 0
    defective_units = returns[returns["Condition"].astype(str).str.contains("Defective", case=False, na=False)]["Qty"].sum() if "Condition" in returns.columns and not returns.empty else 0
    c1.metric("Return Rate", f"{returned_units / max(ordered_units, 1) * 100:.1f}%")
    c2.metric("Defect Rate", f"{defective_units / max(returned_units, 1) * 100:.1f}%")
    c3.metric("Returned Units", format_number(returned_units))

    c4, c5 = st.columns(2)
    c4.plotly_chart(make_line(period_summary(returns, "ME", "Returns"), "Period", "Returns", "Return Trends"), use_container_width=True)
    condition = top_n(returns, "Condition", "Qty", 10)
    c5.plotly_chart(make_bar(condition, "Condition", "Qty", "Good vs Defective Analysis"), use_container_width=True)

    c6, c7 = st.columns(2)
    c6.plotly_chart(make_bar(top_n(returns, "Item Name", "Qty", 15).sort_values("Qty"), "Qty", "Item Name", "Most Returned Products", "h"), use_container_width=True)
    c7.plotly_chart(make_bar(top_n(returns, "Category", "Qty", 12), "Category", "Qty", "Most Returned Categories"), use_container_width=True)

    if "Reason" in returns.columns:
        reasons = returns["Reason"].fillna("Unspecified").astype(str).value_counts().head(12).reset_index()
        reasons.columns = ["Reason", "Count"]
        st.plotly_chart(make_bar(reasons.sort_values("Count"), "Count", "Reason", "Return Reason Analysis", "h"), use_container_width=True)


def render_supplier_intelligence(inwards: pd.DataFrame, returns: pd.DataFrame, selected_suppliers: list[str]) -> None:
    render_section("Supplier Intelligence", "Supply performance", "Contribution, refill frequency, dependence, category mix, and quality score.")
    if selected_suppliers and "Supplier" in inwards.columns:
        inwards = inwards[inwards["Supplier"].isin(selected_suppliers)]

    suppliers = supplier_analytics(inwards, returns)
    c1, c2 = st.columns(2)
    c1.plotly_chart(make_bar(suppliers.head(15).sort_values("Inward Units"), "Inward Units", "Supplier", "Supplier Contribution", "h"), use_container_width=True)
    c2.plotly_chart(make_bar(suppliers.head(15), "Supplier", "Quality Score", "Supplier Quality Score"), use_container_width=True)

    c3, c4 = st.columns(2)
    c3.plotly_chart(make_bar(suppliers.head(15).sort_values("Refills"), "Refills", "Supplier", "Supplier Refill Frequency", "h"), use_container_width=True)
    dependence = suppliers.copy()
    if not dependence.empty:
        dependence["Dependence Share"] = dependence["Inward Units"] / dependence["Inward Units"].sum() * 100
    c4.plotly_chart(make_bar(dependence.head(15), "Supplier", "Dependence Share", "Supplier Dependence Analysis"), use_container_width=True)

    if not inwards.empty:
        mix = inwards.groupby(["Supplier", "Category"])["Qty"].sum().reset_index()
        fig = px.bar(mix, x="Supplier", y="Qty", color="Category", title="Supplier Category Mix", color_discrete_sequence=COLOR_SEQUENCE)
        fig.update_layout(height=440, margin=dict(l=10, r=10, t=55, b=80))
        st.plotly_chart(fig, use_container_width=True)


def render_bi_command_center() -> None:
    render_header()
    data = load_database()
    filters = render_filters(data)

    orders_enriched = enrich_orders(data["orders"], data["dealers"])
    orders = apply_order_filters(
        orders_enriched,
        filters["start_date"],
        filters["end_date"],
        filters["categories"],
        filters["skus"],
        filters["dealers"],
        filters["cities"],
        filters["states"],
    )
    inventory = apply_stock_filters(data["inventory"], filters["categories"], filters["skus"])
    returns = apply_activity_filters(data["returns"], filters["start_date"], filters["end_date"], filters["categories"], filters["skus"])
    inwards = apply_activity_filters(data["inwards"], filters["start_date"], filters["end_date"], filters["categories"], filters["skus"])

    if filters["suppliers"] and "Supplier" in inwards.columns:
        inwards = inwards[inwards["Supplier"].isin(filters["suppliers"])]

    inventory_health = classify_inventory(inventory, orders)

    missing_tables = [name for name, df in data.items() if df.empty]
    if missing_tables:
        st.warning(f"Some sheets could not be loaded or are empty: {', '.join(missing_tables)}")

    tabs = st.tabs(
        [
            "Executive Overview",
            "Sales Intelligence",
            "Inventory Intelligence",
            "Dealer Intelligence",
            "Geographic Intelligence",
            "Returns Intelligence",
            "Supplier Intelligence",
        ]
    )

    with tabs[0]:
        render_executive_overview(orders, inventory_health, returns, inwards, data)
    with tabs[1]:
        render_sales_intelligence(orders)
    with tabs[2]:
        render_inventory_intelligence(inventory_health)
    with tabs[3]:
        render_dealer_intelligence(orders)
    with tabs[4]:
        render_geographic_intelligence(orders)
    with tabs[5]:
        render_returns_intelligence(returns, orders)
    with tabs[6]:
        render_supplier_intelligence(inwards, returns, filters["suppliers"])

# 2. Initialize Global Session Tracking
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# Tracks a neat list of nested blocks: Each block has ONE category, and a sub-list of items
if 'form_structure' not in st.session_state:
    st.session_state.form_structure = [
        {"category": "", "items": [{"name": "", "qty": 0}]}
    ]

# =========================================================================
# GLOBAL CSS: Strip sidebar and enforce high-contrast layout colors
# =========================================================================
st.markdown("""
    <style>
        /* Sidebar remains available for the Admin BI command center filters. */
        
        /* Manager & Salesman Status Notification Banner (Crisp blue contrast) */
        .status-card { 
            padding: 15px; 
            border-radius: 10px; 
            background-color: #e3f2fd !important; 
            border-left: 5px solid #007bff; 
            margin-bottom: 20px;
            color: #0d47a1 !important;
        }
        .status-card h4, .status-card p, .status-card b { color: #0d47a1 !important; }
        
        /* Admin Audit Header Card (Muted amber contrast) */
        .admin-card { 
            padding: 15px; 
            border-radius: 10px; 
            background-color: #fff3cd !important; 
            border-left: 5px solid #ffc107; 
            margin-bottom: 20px;
            color: #856404 !important;
        }
        .admin-card b { color: #856404 !important; }
        
        /* Transaction form item container */
        .row-container { 
            padding: 12px; 
            border: 1px solid #eee; 
            border-radius: 8px; 
            margin-bottom: 8px; 
            background-color: #ffffff; 
        }
        .stButton>button { width: 100%; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Initialize Session Tracking States
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'form_rows' not in st.session_state:
    st.session_state.form_rows = 1

# =========================================================================
# 3. SECURITY GATEKEEPER: LOGIN LAYOUT SCREEN (Restored to Centered Layout)
# =========================================================================
if not st.session_state.authenticated:
    # Restored to the original layout: Logo centered perfectly above the title
    logo_left, logo_core, logo_right = st.columns([3, 2, 3])
    with logo_core:
        st.image("logo.png", use_container_width=True) 
    
    st.markdown("<h2 style='text-align: center; margin-top: 0;'>Hardware Portal Login</h2>", unsafe_allow_html=True)
    st.write("") 
    
    # Restrict input field width using empty tracking columns
    login_left, login_mid, login_right = st.columns([3, 2, 3])
    with login_mid:
        st.write("Please log in to verify system permissions.")
        username = st.selectbox("Select Your Role", ["", "Salesman", "Manager", "Admin"])
        # password = st.text_input("Enter Password", type="password")
        
        if st.button("Log In", type="primary"):
            if username == "Manager": #and password == st.secrets["passwords"]["manager"]:
                st.session_state.authenticated = True
                st.session_state.user_role = "Manager"
                st.rerun()
            elif username == "Salesman": #and password == st.secrets["passwords"]["salesman"]:
                st.session_state.authenticated = True
                st.session_state.user_role = "Salesman"
                st.rerun()
            elif username == "Admin": #and password == st.secrets["passwords"]["admin"]:
                st.session_state.authenticated = True
                st.session_state.user_role = "Admin"
                st.rerun()
            else:
                st.error("❌ Invalid Password Configuration.")
    st.stop()

# =========================================================================
# 4. DATABASE CONNECTIVITY PIPELINE (Runs once logged in)
# =========================================================================
DB_URL = "https://docs.google.com/spreadsheets/d/1hz6YQYPUicMGKc7c05a5X4S_W1Y_bbJDNK83XWviLYI/"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(name):
    try:
        df = conn.read(spreadsheet=DB_URL, worksheet=name, ttl=100)
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return pd.DataFrame()

inventory_df = load_sheet("Inventory")
if not inventory_df.empty:
    inventory_df['Item Name'] = inventory_df['Item Name'].fillna('').astype(str)
    item_list = [""] + inventory_df['Item Name'].tolist()
else:
    item_list = [""]

# =========================================================================
# 5. AUTHENTICATED WORKSPACE CONFIGURATIONS
# =========================================================================

# --- CLEARANCE LEVEL A: ADMIN CONTROL PANEL ---
if st.session_state.user_role == "Admin":
    # Keep the logo pinned to the upper left corner of the admin panel
    admin_logo_col, admin_title_col = st.columns([1, 5])
    with admin_logo_col:
        st.image("logo.png", use_container_width=True)
    with admin_title_col:
        st.markdown("<h1 style='color: #856404; margin-top: 10px; margin-bottom: 0;'>Admin Center</h1>", unsafe_allow_html=True)
    
    ac1, ac2 = st.columns([3, 1])
    with ac1:
        st.markdown("""
        <div class="admin-card">
            <b>System Clearance level:</b> Administrator | <b>Audit Scope:</b> Full Inward & Outward Historical Logs
        </div>
        """, unsafe_allow_html=True)
    with ac2:
        if st.button(" Log Out ", key="admin_logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.rerun()

    st.write("---")
    inwards_df = load_sheet("Inwards")
    orders_df = load_sheet("Orders")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Master Live Inventory",
        "Inward Refill History",
        "Outward Sales History",
        "Replacements",
        "BI Command Center",
    ])
    
    with tab1:
        st.subheader("Current Stock Balances")
        st.dataframe(inventory_df, hide_index=True, use_container_width=True)
        
    with tab2:
        st.subheader("Inward Refill")
        if not inwards_df.empty and 'Timestamp' in inwards_df.columns:
            inwards_df = inwards_df.sort_values(by='Timestamp', ascending=False)
            st.dataframe(inwards_df, hide_index=True, use_container_width=True)
        else:
            st.info("ℹ️ No incoming shipments yet.")
            
    with tab3:
        st.subheader("Outward Orders")
        if not orders_df.empty and 'Timestamp' in orders_df.columns:
            orders_df = orders_df.sort_values(by='Timestamp', ascending=False)
            st.dataframe(orders_df, hide_index=True, use_container_width=True)
        else:
            st.info("ℹ️ No dealer orders yet.")

    with tab4:
        st.subheader("🔄 Return & Replacements")
        returns_df = load_sheet("Returns")
        if not returns_df.empty:
            if 'Timestamp' in returns_df.columns:
                returns_df = returns_df.sort_values(by='Timestamp', ascending=False)
            st.dataframe(returns_df, hide_index=True, use_container_width=True)
        else:
            st.info("No return transactions logged yet.")

    with tab5:
        render_bi_command_center()

# --- CLEARANCE LEVEL B: OPERATIONAL ROLES (SALESMAN / MANAGER) ---

else:
    left_col, right_col = st.columns([2, 3], gap="large") 

    with left_col:
        st.image("logo.png", width=180)
        
        purpose_text = "Outward Order Logging" if st.session_state.user_role == "Salesman" else "Inward Stock / Returns Hub"
        
        st.markdown(f"""
        <div class="status-card">
            <h4 style='margin:0; color:#333;'>Context Status</h4>
            <p style='margin:5px 0 0 0;'><b>Active Identity:</b> 👤 {st.session_state.user_role}</p>
            <p style='margin:2px 0 0 0;'><b>Operational Scope:</b> 🛠️ {purpose_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔒 Log Out", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.form_structure = [{"category": "", "items": [{"name": "", "qty": 0}]}]
            st.rerun()
            
        st.subheader("📋 Action Entry Sheet")
        
        # Pull global category definitions from your master inventory sheet
        if not inventory_df.empty and 'Category' in inventory_df.columns:
            categories_list = [""] + sorted(inventory_df['Category'].dropna().unique().tolist())
        else:
            categories_list = [""]

        # =========================================================================
        # BRANCH 1: SALESMAN WORKFLOW (Completely Isolated Order Entry)
        # =========================================================================
        if st.session_state.user_role == "Salesman":
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                dealer_name = st.text_input("Dealer Name")
            with col_s2:
                shop_name = st.text_input("Shop Name")
                
            final_transaction_payload = []

            # Multi-category block engine specifically for order taking
            for c_idx, cat_block in enumerate(st.session_state.form_structure):
                #st.markdown(f"<div style='background-color: #f1f3f5; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #ced4da;'>", unsafe_allow_html=True)
                
                selected_cat = st.selectbox(
                    f" Select Category ", 
                    options=categories_list, 
                    key=f"sales_cat_sel_{c_idx}"
                )
                st.session_state.form_structure[c_idx]["category"] = selected_cat

                item_options = [""] + sorted(inventory_df[inventory_df['Category'] == selected_cat]['Item Name'].tolist()) if selected_cat else [""]

                for i_idx in range(len(cat_block["items"])):
                    #st.markdown('<div class="row-container">', unsafe_allow_html=True)
                    rc1, rc2 = st.columns([3, 1])
                    with rc1:
                        item_name = st.selectbox(f"Product", options=item_options, key=f"sales_item_{c_idx}_{i_idx}")
                    with rc2:
                        item_qty = st.number_input(f"Qty", min_value=0, step=1, key=f"sales_qty_{c_idx}_{i_idx}")
                    
                    st.session_state.form_structure[c_idx]["items"][i_idx]["name"] = item_name
                    st.session_state.form_structure[c_idx]["items"][i_idx]["qty"] = item_qty

                    if selected_cat and item_name and item_qty > 0:
                        current_avail = inventory_df[inventory_df['Item Name'] == item_name]['Current Stock'].values
                        avail_stock = current_avail[0] if len(current_avail) > 0 else 0
                        if item_qty > avail_stock:
                            st.warning(f"⚠️ Only {int(avail_stock)} units left in stock!")
                        
                        final_transaction_payload.append({"Category": selected_cat, "Item Name": item_name, "Qty": item_qty})
                    #st.markdown('</div>', unsafe_allow_html=True)

                if selected_cat:
                    with st.columns([1, 3])[0]:
                        if st.button("➕ Item", key=f"sales_add_item_{c_idx}"):
                            st.session_state.form_structure[c_idx]["items"].append({"name": "", "qty": 0})
                            st.rerun()

                #st.markdown("</div>", unsafe_allow_html=True)

            gc1, gc2 = st.columns(2)
            with gc1:
                if st.button(" Add New Category", type="secondary", key="sales_add_cat_btn"):
                    st.session_state.form_structure.append({"category": "", "items": [{"name": "", "qty": 0}]})
                    st.rerun()
            with gc2:
                if st.button("🗑️ Reset", key="sales_reset_btn"):
                    st.session_state.form_structure = [{"category": "", "items": [{"name": "", "qty": 0}]}]
                    st.rerun()

            st.write("")

            if st.button("🚀 Place Order", type="primary", key="sales_commit_btn"):
                if not dealer_name or not shop_name or not final_transaction_payload:
                    st.error("⚠️ Complete all required details and add at least one valid item.")
                else:
                    with st.spinner("Processing Order..."):
                        new_orders = pd.DataFrame(final_transaction_payload)
                        new_orders['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_orders['Dealer Name'] = dealer_name
                        new_orders['Store Name'] = shop_name
                        
                        orders_df = load_sheet("Orders")
                        updated_orders = pd.concat([orders_df, new_orders[['Timestamp', 'Dealer Name', 'Store Name', 'Category', 'Item Name', 'Qty']]], ignore_index=True)
                        conn.update(spreadsheet=DB_URL, worksheet="Orders", data=updated_orders)
                        
                        for row in final_transaction_payload:
                            inventory_df.loc[inventory_df['Item Name'] == row['Item Name'], 'Current Stock'] -= row['Qty']
                        conn.update(spreadsheet=DB_URL, worksheet="Inventory", data=inventory_df)
                        
                        st.success("✅ Order successfull!")
                        st.session_state.form_structure = [{"category": "", "items": [{"name": "", "qty": 0}]}]
                        st.rerun()

        # =========================================================================
        # BRANCH 2: MANAGER WORKFLOW (Fully Trapped Under Toggle Logic)
        # =========================================================================
        elif st.session_state.user_role == "Manager":
            import uuid
            
            manager_mode = st.radio("Choose Action", ["Stock Refill", "🔄 Process Return"], horizontal=True)
            
            # --- MODE A: REFILL ---
            if manager_mode == "Stock Refill":
                supplier = st.text_input("Supplier Name")
                final_transaction_payload = []

                for c_idx, cat_block in enumerate(st.session_state.form_structure):
                    #st.markdown(f"<div style='background-color: #f1f3f5; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #ced4da;'>", unsafe_allow_html=True)
                    
                    selected_cat = st.selectbox(
                        f"Select Category", 
                        options=categories_list, 
                        key=f"cat_sel_refill_{c_idx}"
                    )
                    st.session_state.form_structure[c_idx]["category"] = selected_cat

                    item_options = [""] + sorted(inventory_df[inventory_df['Category'] == selected_cat]['Item Name'].tolist()) if selected_cat else [""]

                    for i_idx in range(len(cat_block["items"])):
                        #st.markdown('<div class="row-container">', unsafe_allow_html=True)
                        rc1, rc2 = st.columns([3, 1])
                        with rc1:
                            item_name = st.selectbox(f"Product", options=item_options, key=f"item_refill_{c_idx}_{i_idx}")
                        with rc2:
                            item_qty = st.number_input(f"Qty", min_value=0, step=1, key=f"qty_refill_{c_idx}_{i_idx}")
                        
                        st.session_state.form_structure[c_idx]["items"][i_idx]["name"] = item_name
                        st.session_state.form_structure[c_idx]["items"][i_idx]["qty"] = item_qty

                        if selected_cat and item_name and item_qty > 0:
                            sku_val = inventory_df[inventory_df['Item Name'] == item_name]['SKU'].values
                            current_sku = sku_val[0] if len(sku_val) > 0 else "N/A"
                            
                            final_transaction_payload.append({
                                "Category": selected_cat, 
                                "Item Name": item_name, 
                                "Qty": item_qty,
                                "SKU": current_sku
                            })
                        #st.markdown('</div>', unsafe_allow_html=True)

                    if selected_cat:
                        with st.columns([1, 3])[0]:
                            if st.button("➕ Item", key=f"add_item_row_refill_{c_idx}"):
                                st.session_state.form_structure[c_idx]["items"].append({"name": "", "qty": 0})
                                st.rerun()

                    #st.markdown("</div>", unsafe_allow_html=True)

                gc1, gc2 = st.columns(2)
                with gc1:
                    if st.button("Add New Category", type="secondary", key="add_cat_refill_btn"):
                        st.session_state.form_structure.append({"category": "", "items": [{"name": "", "qty": 0}]})
                        st.rerun()
                with gc2:
                    if st.button("Reset", key="reset_refill_btn"):
                        st.session_state.form_structure = [{"category": "", "items": [{"name": "", "qty": 0}]}]
                        st.rerun()

                st.write("")

                if st.button("Commit Inward", type="primary", key="commit_refill_btn"):
                    if not supplier or not final_transaction_payload:
                        st.error("⚠️ Complete all required fields.")
                    else:
                        with st.spinner("Processing additions..."):
                            new_inwards = pd.DataFrame(final_transaction_payload)
                            new_inwards['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            new_inwards['Supplier'] = supplier
                            
                            inwards_df = load_sheet("Inwards")
                            updated_inwards = pd.concat([inwards_df, new_inwards[['Timestamp', 'Supplier', 'Category', 'Item Name', 'Qty']]], ignore_index=True)
                            conn.update(spreadsheet=DB_URL, worksheet="Inwards", data=updated_inwards)
                            
                            txn_df = load_sheet("Inventory Transaction")
                            txn_rows = []

                            for row in final_transaction_payload:
                                txn_rows.append({
                                    "Txn ID": f"IN-{uuid.uuid4().hex[:8]}",
                                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "Type": "IN",
                                    "Item Name": row["Item Name"],
                                    "Item Category": row["Category"],
                                    "SKU": row["SKU"],
                                    "Quantity": row["Qty"],
                                    "User": "Manager",
                                    "Reference": supplier
                                })

                            updated_txn = pd.concat([txn_df, pd.DataFrame(txn_rows)], ignore_index=True)
                            conn.update(spreadsheet=DB_URL, worksheet="Inventory Transaction", data=updated_txn)
                            
                            for row in final_transaction_payload:
                                inventory_df.loc[inventory_df['Item Name'] == row['Item Name'], 'Current Stock'] += row['Qty']
                            conn.update(spreadsheet=DB_URL, worksheet="Inventory", data=inventory_df)
                            
                            st.success("✅ Warehouse balances updated!")
                            st.session_state.form_structure = [{"category": "", "items": [{"name": "", "qty": 0}]}]
                            st.rerun()

            # --- MODE B: PROCESS RETURNS ---
            elif manager_mode == "🔄 Process Return":
                st.write("### Log Returned Hardware")
                
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    ret_dealer = st.text_input("Dealer Name", key="ret_dealer_input")
                with col_r2:
                    ret_shop = st.text_input("Shop Name", key="ret_shop_input")
                    
                ret_cat = st.selectbox("Select Item Category", options=categories_list, key="ret_cat_select_return")
                item_opts = [""] + sorted(inventory_df[inventory_df['Category'] == ret_cat]['Item Name'].tolist()) if ret_cat else [""]
                
                #st.markdown('<div class="row-container">', unsafe_allow_html=True)
                rc1, rc2 = st.columns([3, 1])
                with rc1:
                    ret_item = st.selectbox("Select Product Name", options=item_opts, key="ret_item_select_return")
                with rc2:
                    ret_qty = st.number_input("Return Qty", min_value=0, step=1, key="ret_qty_input_return")
                st.markdown('</div>', unsafe_allow_html=True)
                
                ret_condition = st.radio("Quality / Condition Inspection Result", ["Good Item (Restock to Sellable Inventory)", "Defective Item (Send to Company for Replacement)"], key="ret_condition_radio")
                ret_reason = st.text_area("Reason for Return / Defect Details", key="ret_reason_area")
                
                if st.button("💾 Process and Log Return", type="primary", key="commit_return_btn"):
                    if not ret_dealer or not ret_shop or not ret_item or ret_qty <= 0 or not ret_reason:
                        st.error("⚠️ Please fill out all return details completely.")
                    else:
                        with st.spinner("Processing logging details..."):
                            is_good = "Good Item" in ret_condition
                            status_text = "Restocked" if is_good else "Pending Factory Replacement"
                            condition_tag = "Good" if is_good else "Defective"
                            
                            return_row = {
                                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Dealer Name": ret_dealer,
                                "Store Name": ret_shop,
                                "Category": ret_cat,
                                "Item Name": ret_item,
                                "Qty": ret_qty,
                                "Condition": condition_tag,
                                "Reason": ret_reason,
                                "Status": status_text
                            }
                            
                            new_returns_df = pd.DataFrame([return_row])
                            old_returns_df = load_sheet("Returns")
                            updated_returns = pd.concat([old_returns_df, new_returns_df], ignore_index=True)
                            conn.update(spreadsheet=DB_URL, worksheet="Returns", data=updated_returns)
                            
                            if is_good:
                                # Safe Type Casting to protect math modifications
                                inventory_df['Current Stock'] = pd.to_numeric(inventory_df['Current Stock'], errors='coerce').fillna(0).astype(int)
                                
                                if ret_item in inventory_df['Item Name'].values:
                                    inventory_df.loc[inventory_df['Item Name'] == ret_item, 'Current Stock'] += int(ret_qty)
                                    
                                    # Crucial Connection Update Execution Call Added
                                    conn.update(spreadsheet=DB_URL, worksheet="Inventory", data=inventory_df)
                                    st.success(f"✅ Processed! {ret_qty} units added back into live stock balances.")
                                else:
                                    st.error(f"❌ Error: Product '{ret_item}' was not found in the Inventory Database.")
                            else:
                                st.warning("⚠️ Item marked Defective! Logged to tracker database for factory handling. Live balances left unchanged.")
                                
                            st.rerun()

    # Right column displays your live monitor interface uniformly

    with right_col:
        st.subheader("📊 Live Master Inventory Ledger")
        if not inventory_df.empty and 'Current Stock' in inventory_df.columns:
            inventory_df['Current Stock'] = pd.to_numeric(inventory_df['Current Stock'], errors='coerce').fillna(0).astype(int)
            
            tot_kinds = len(inventory_df)
            tot_units = inventory_df['Current Stock'].sum()
            
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Tracked Variants", tot_kinds)
            m_col2.metric("Total Items on Floor", tot_units)
            
            st.write("---")
            search_term = st.text_input("🔍 Filter Inventory List Quick-Search", placeholder="Type item name to scan levels...")
            filtered_df = inventory_df[inventory_df['Item Name'].str.contains(search_term, case=False)] if search_term else inventory_df
            
            st.dataframe(filtered_df, hide_index=True, use_container_width=True, height=550)
