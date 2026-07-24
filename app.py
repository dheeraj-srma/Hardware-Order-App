import math
from datetime import date, datetime
import uuid
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from database.client import supabase

# ── Database layer ────────────────────────────────────────────────────────────
from database.crud import (
    load_table,
    insert_order,
    insert_inward,
    insert_return,
    get_inventory,
    get_orders,
)
from database.client import supabase

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nalka Metals Portal",
    page_icon="NM",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLOR_SEQUENCE = ["#1F77B4", "#2CA02C", "#FF7F0E", "#D62728", "#17BECF", "#9467BD"]
px.defaults.template = "plotly_dark"


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────
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

        .stApp { background: var(--app-bg); color: var(--text); }
        .block-container { max-width: 1440px; padding-top: 1.25rem; padding-bottom: 2.5rem; }
        h1, h2, h3 { color: var(--text); letter-spacing: 0; }
        p, label, span, div { letter-spacing: 0; }

        .app-hero {
            background: linear-gradient(135deg, rgba(59,130,246,0.20), rgba(34,197,94,0.08) 48%, rgba(17,24,39,0.78));
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 18px 20px;
            margin-bottom: 18px;
        }
        .app-eyebrow { color: #93c5fd; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
        .app-title { color: var(--text); font-size: clamp(1.65rem, 2.4vw, 2.35rem); font-weight: 750; line-height: 1.1; margin: 0; }
        .app-subtitle { color: #c7d2e5; max-width: 880px; margin: 8px 0 0 0; font-size: 0.98rem; }

        .section-kicker { color: #93c5fd; font-size: 0.76rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin: 18px 0 2px 0; }
        .section-title { color: var(--text); font-size: 1.45rem; font-weight: 730; margin: 0 0 12px 0; }
        .panel-note { color: var(--muted); font-size: 0.9rem; margin-top: -6px; margin-bottom: 14px; }

        [data-testid="stMetric"] {
            background: linear-gradient(180deg, #151f31, #101827);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px 18px;
            min-height: 112px;
            box-shadow: 0 14px 32px rgba(0,0,0,0.18);
        }
        [data-testid="stMetric"] label,
        [data-testid="stMetric"] [data-testid="stMetricLabel"],
        [data-testid="stMetric"] [data-testid="stMetricValue"],
        [data-testid="stMetric"] div { color: var(--text) !important; }
        [data-testid="stMetric"] label,
        [data-testid="stMetric"] [data-testid="stMetricLabel"] { color: #a7b3c7 !important; font-size: 0.86rem !important; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 760 !important; }

        div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 8px; overflow: hidden; background: var(--surface); }
        div[data-testid="stTabs"] button { color: #b8c2d6; border-radius: 8px 8px 0 0; }
        div[data-testid="stTabs"] button[aria-selected="true"] { color: #ffffff; background: rgba(59,130,246,0.16); border-bottom-color: #3b82f6; }

        .stButton > button { border-radius: 8px; border: 1px solid var(--line); background: #172033; color: var(--text); font-weight: 700; min-height: 40px; }
        .stButton > button[kind="primary"], .stButton > button:hover { border-color: #60a5fa; background: #1d4ed8; color: #ffffff; }
        input, textarea, [data-baseweb="select"] > div { border-radius: 8px !important; }

        .insight-card {
            border-left: 4px solid var(--brand);
            background: rgba(59,130,246,0.12);
            border-top: 1px solid rgba(59,130,246,0.18);
            border-right: 1px solid rgba(59,130,246,0.18);
            border-bottom: 1px solid rgba(59,130,246,0.18);
            border-radius: 8px; padding: 12px 14px; margin: 8px 0; color: #dbeafe; font-size: 0.95rem;
        }
        .risk-card {
            border-left: 4px solid var(--danger);
            background: rgba(248,113,113,0.12);
            border-top: 1px solid rgba(248,113,113,0.18);
            border-right: 1px solid rgba(248,113,113,0.18);
            border-bottom: 1px solid rgba(248,113,113,0.18);
            border-radius: 8px; padding: 12px 14px; margin: 8px 0; color: #fee2e2; font-size: 0.95rem;
        }
        .small-muted { color: var(--muted); font-size: 0.88rem; }

        .status-card {
            padding: 15px; border-radius: 10px; background-color: #e3f2fd !important;
            border-left: 5px solid #007bff; margin-bottom: 20px; color: #0d47a1 !important;
        }
        .status-card h4, .status-card p, .status-card b { color: #0d47a1 !important; }
        .admin-card {
            padding: 15px; border-radius: 10px; background-color: #fff3cd !important;
            border-left: 5px solid #ffc107; margin-bottom: 20px; color: #856404 !important;
        }
        .admin-card b { color: #856404 !important; }
        .row-container { padding: 12px; border: 1px solid #eee; border-radius: 8px; margin-bottom: 8px; background-color: #ffffff; }
        .stButton>button { width: 100%; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# PURE DATA-PROCESSING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise column names coming from Supabase (any casing / snake_case)."""
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    # Comprehensive rename map — covers snake_case, camelCase, and alternate spellings
    rename_map = {
        # Timestamp variants
        "timestamp":        "Timestamp",
        "created_at":       "Timestamp",
        "order_date":       "Timestamp",
        "date":             "Timestamp",
        "Date":             "Timestamp",
        # Qty variants
        "quantity":         "Qty",
        "Quantity":         "Qty",
        "qty":              "Qty",
        # Item name variants
        "item_name":        "Item Name",
        "itemname":         "Item Name",
        "product_name":     "Item Name",
        "product":          "Item Name",
        # SKU variants
        "sku":              "SKU",
        # Category variants
        "category":         "Category",
        "item_category":    "Category",
        "Item Category":    "Category",
        # Salesman variants (formerly Dealer)
        "salesman_name":    "Salesman Name",
        "salesmanname":     "Salesman Name",
        "dealer_name":      "Salesman Name",
        "dealername":       "Salesman Name",
        "Dealer Name":      "Salesman Name",
        # Shop variants
        "shop_name":        "Shop Name",
        "shopname":         "Shop Name",
        "store_name":       "Shop Name",
        "Store Name":       "Shop Name",
        # Supplier variants
        "supplier_name":    "Supplier",
        "supplier":         "Supplier",
        "Supplier Name":    "Supplier",
        # Order ID variants
        "order_id":         "Order ID",
        "orderid":          "Order ID",
        "Order Id":         "Order ID",
        # Stock variants
        "current_stock":    "Current Stock",
        "stock":            "Current Stock",
        "balance":          "Current Stock",
        # Location variants
        "city":             "City",
        "state":            "State",
        # Condition / reason / status
        "condition":        "Condition",
        "reason":           "Reason",
        "status":           "Status",
        # Salesman type variants (formerly Dealer type)
        "salesman_type":    "Salesman Type",
        "salesmantype":     "Salesman Type",
        "dealer_type":      "Salesman Type",
        "dealertype":       "Salesman Type",
        "Dealer Type":      "Salesman Type",
        # Salesman ID variants (formerly Dealer ID)
        "salesman_id":      "Salesman ID",
        "salesmanid":       "Salesman ID",
        "dealer_id":        "Salesman ID",
        "dealerid":         "Salesman ID",
        "Dealer ID":        "Salesman ID",
        # Specialization
        "specialization":   "Specialization",
        # Transaction type
        "type":             "Type",
        "transaction_type": "Type",
        # User / reference
        "user":             "User",
        "reference":        "Reference",
        "ref":              "Reference",
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
    st.markdown(f"{kicker_html}<div class='section-title'>{title}</div>{note_html}", unsafe_allow_html=True)


def ensure_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA
    return df


def parse_datetime_column(df: pd.DataFrame, column: str = "Timestamp") -> pd.DataFrame:
    df = df.copy()
    if column in df.columns:
        df[column] = pd.to_datetime(df[column], errors="coerce", utc=True)
        # Strip timezone so downstream .dt.date comparisons work simply
        df[column] = df[column].dt.tz_localize(None) if df[column].dt.tz is None else df[column].dt.tz_convert(None)
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
    """Clean and type-cast a raw Supabase DataFrame."""
    if df.empty:
        return df
    df = clean_columns(df)
    if table_name == "inventory":
        df = ensure_columns(df, ["SKU", "Category", "Item Name", "Current Stock"])
        df = parse_text_columns(df, ["SKU", "Category", "Item Name"])
        df = parse_numeric_column(df, "Current Stock")
    elif table_name in {"orders", "inwards", "returns"}:
        df = ensure_columns(df, ["Timestamp", "Category", "SKU", "Item Name", "Qty"])
        df = parse_text_columns(
            df, ["SKU", "Category", "Item Name", "Salesman Name", "Shop Name",
                 "Supplier", "Condition", "Reason", "Status", "City", "State"],
        )
        df = parse_datetime_column(df)
        df = parse_numeric_column(df, "Qty")
        # Drop rows where Timestamp couldn't be parsed — they break resampling
        if "Timestamp" in df.columns:
            df = df.dropna(subset=["Timestamp"])
    elif table_name == "transactions":
        df = ensure_columns(df, ["Timestamp", "Type", "SKU", "Item Name", "Category", "Qty"])
        df = parse_text_columns(df, ["Type", "SKU", "Item Name", "Category", "User", "Reference"])
        df = parse_datetime_column(df)
        df = parse_numeric_column(df, "Qty")
        if "Timestamp" in df.columns:
            df = df.dropna(subset=["Timestamp"])
    elif table_name == "dealers":
        df = ensure_columns(df, ["Salesman Name", "Shop Name", "City", "State", "Salesman Type"])
        df = parse_text_columns(df, ["Salesman Name", "Shop Name", "City", "State", "Salesman Type"])
    elif table_name == "suppliers":
        df = ensure_columns(df, ["Supplier", "City", "State", "Specialization"])
        df = parse_text_columns(df, ["Supplier", "City", "State", "Specialization"])
    return df

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INITIALISATION
# ─────────────────────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "form_structure" not in st.session_state:
    st.session_state.form_structure = [{"category": "", "items": [{"name": "", "qty": 0}]}]
if "form_rows" not in st.session_state:
    st.session_state.form_rows = 1


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN SCREEN
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    logo_left, logo_core, logo_right = st.columns([3, 2, 3])
    with logo_core:
        st.image("logo.png", use_container_width=True)

    st.markdown("<h2 style='text-align: center; margin-top: 0;'>Hardware Portal Login</h2>", unsafe_allow_html=True)
    st.write("")

    login_left, login_mid, login_right = st.columns([3, 2, 3])
    with login_mid:
        st.write("Please log in to verify system permissions.")
        username = st.selectbox("Select Your Role", ["", "Salesman", "Manager", "Customer"])

        if st.button("Log In", type="primary"):
            if username in ("Salesman", "Manager", "Customer"):
                st.session_state.authenticated = True
                st.session_state.user_role = username
                st.rerun()
            else:
                st.error("❌ Invalid Password Configuration.")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE: load inventory once after login
# ─────────────────────────────────────────────────────────────────────────────
dealers_df = load_table("DEALERS")
inventory_df = load_table("INVENTORY")
if not inventory_df.empty:
    inventory_df = clean_columns(inventory_df)
    inventory_df["Item Name"]     = inventory_df["Item Name"].fillna("").astype(str) if "Item Name" in inventory_df.columns else ""
    inventory_df["Current Stock"] = pd.to_numeric(inventory_df.get("Current Stock", 0), errors="coerce").fillna(0).astype(int)
    item_list = [""] + inventory_df["Item Name"].tolist()
else:
    item_list = [""]
   


# ─────────────────────────────────────────────────────────────────────────────
# SALESMAN / MANAGER PANEL
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.user_role in ["Salesman", "Manager", "Customer"]:
    left_col, right_col = st.columns([2, 3], gap="large")

    with left_col:
        st.image("logo.png", width=180)

        purpose_text = "Outward Order Logging" if st.session_state.user_role == "Salesman" else "Inward Stock / Returns Hub"
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:6px 12px;background-color:#e3f2fd;border-radius:6px;
                    font-size:0.85rem;color:#0d47a1;margin-bottom:12px;border:1px solid #bbdefb;">
            <span>👤 <b>Role:</b> {st.session_state.user_role}</span>
            <span>🛠️ <b>Scope:</b> {purpose_text}</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔒 Log Out", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.form_structure = [{"category": "", "items": [{"name": "", "qty": 0}]}]
            st.rerun()

        st.subheader("📋 Action Entry Sheet")

        categories_list = (
            [""] + sorted(inventory_df["Category"].dropna().unique().tolist())
            if not inventory_df.empty and "Category" in inventory_df.columns
            else [""])

         # ── SALESMAN WORKFLOW ────────────────────────────────────────────────
        if st.session_state.user_role in ["Salesman", "Customer"]:

            # Decide which column to use
            if st.session_state.user_role == "Salesman":
                person_column = "Salesman Name"
                person_label = "Salesman"

            elif st.session_state.user_role == "Customer":
                person_column = "Salesman Name"
                person_label = "Customer"

            dealers_df = load_table("DEALERS")
            locations_df = load_table("LOCATIONS")
            if not locations_df.empty:
                locations_df = clean_columns(locations_df)


            col_s1, col_s2 = st.columns(2)
            with col_s1:
                person_list = sorted(dealers_df[person_column].dropna().unique().tolist())
                selected_person = st.selectbox(person_label, person_list, key="person_select")
            filtered_person = dealers_df[dealers_df[person_column]==selected_person]

            with col_s2:
                shop_list = sorted(filtered_person["Shop Name"].dropna().unique().tolist())
                selected_shop = st.selectbox("Shop Name",shop_list,key="shop_select")

            dealer_match = filtered_person[filtered_person["Shop Name"] == selected_shop]
            if dealer_match.empty:
                st.error("Salesman / Shop combination not found.")
                st.stop()

            dealer_record = dealer_match.iloc[0]

            salesman_id = dealer_record["Salesman ID"]
            salesman_name = dealer_record["Salesman Name"]
            shop_name = dealer_record["Shop Name"]
            state = dealer_record["State"]
            city = dealer_record["City"]
            col_l1, col_l2 = st.columns(2)

            with col_l1:
                st.text_input("State",value=state,disabled=True,key="salesman_state")

            with col_l2:
                st.text_input("City",value=city,disabled=True,key="salesman_city")


            location_match = locations_df[(locations_df["State"] == state) &(locations_df["City"] == city)]

            if location_match.empty:
                st.error("Location not found.")
                st.stop()

            location_id = location_match.iloc[0]["Location ID"]

            final_transaction_payload = []


            for c_idx, cat_block in enumerate(st.session_state.form_structure):
                selected_cat = st.selectbox(
                    "Select Category", options=categories_list, key=f"sales_cat_sel_{c_idx}"
                )
                st.session_state.form_structure[c_idx]["category"] = selected_cat

                item_options = (
                    [""] + sorted(inventory_df[inventory_df["Category"] == selected_cat]["Item Name"].tolist())
                    if selected_cat and "Category" in inventory_df.columns else [""]
                )

                for i_idx in range(len(cat_block["items"])):
                    rc1, rc2 = st.columns([3, 1])
                    with rc1:
                        item_name = st.selectbox("Product", options=item_options, key=f"sales_item_{c_idx}_{i_idx}")
                    with rc2:
                        item_qty = st.number_input("Qty", min_value=0, step=1, key=f"sales_qty_{c_idx}_{i_idx}")

                    st.session_state.form_structure[c_idx]["items"][i_idx]["name"] = item_name
                    st.session_state.form_structure[c_idx]["items"][i_idx]["qty"]  = item_qty

                    if selected_cat and item_name and item_qty > 0:
                        current_avail = inventory_df[inventory_df["Item Name"] == item_name]["Current Stock"].values
                        avail_stock = int(current_avail[0]) if len(current_avail) > 0 else 0
                        if item_qty > avail_stock:
                            st.warning(f"⚠️ Only {avail_stock} units left in stock!")

                        final_transaction_payload.append({
                            "Category":  selected_cat,
                            "Item Name": item_name,
                            "Qty":       item_qty,
                        })

                if selected_cat:
                    with st.columns([1, 3])[0]:
                        if st.button("➕ Item", key=f"sales_add_item_{c_idx}"):
                            st.session_state.form_structure[c_idx]["items"].append({"name": "", "qty": 0})
                            st.rerun()

            gc1, gc2 = st.columns(2)
            with gc1:
                if st.button("Add New Category", type="secondary", key="sales_add_cat_btn"):
                    st.session_state.form_structure.append({"category": "", "items": [{"name": "", "qty": 0}]})
                    st.rerun()
            with gc2:
                if st.button("🗑️ Reset", key="sales_reset_btn"):
                    st.session_state.form_structure = [{"category": "", "items": [{"name": "", "qty": 0}]}]
                    st.rerun()

            st.write("")

            if st.button("🚀 Place Order", type="primary", key="sales_commit_btn"):
                if not salesman_name or not selected_shop or not final_transaction_payload:
                    st.error("⚠️ Complete all required details and add at least one valid item.")
                else:
                    with st.spinner("Processing Order..."):
                        order_id  = f"ORD-{uuid.uuid4().hex[:8]}"
                        salesman_id = dealer_record["Salesman ID"]
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        location_id = location_match.iloc[0]["Location ID"]

                        order_rows = []
                        for row in final_transaction_payload:
                            item_record = inventory_df[inventory_df["Item Name"] == row["Item Name"]].iloc[0]
                            sku = item_record["SKU"]
                            price = item_record["Price"]
                            if item_record.empty:
                                continue

                            item_record = item_record.iloc[0]
                            
                            order_rows.append({
                                "Order ID":      order_id,
                                "Timestamp":     timestamp,
                                "Salesman Name": salesman_name,
                                "Shop Name":     shop_name,
                                "Category":      row["Category"],
                                "SKU":           sku,
                                "Item Name":     row["Item Name"],
                                "Qty":           item_record["Qty"],
                                "City":          city,
                                "State":         state,
                                "Order ID":      order_id,
                                "Location ID":   location_id,
                                "Price":         price,
                                "Salesman ID":   salesman_id,
                                "Total Price": price * row["Qty"],
                            })

                        if insert_order(order_rows):
                            st.success("✅ Order placed successfully!")
                            st.session_state.form_structure = [{"category": "", "items": [{"name": "", "qty": 0}]}]
                            st.rerun()
        

        # ── MANAGER WORKFLOW ─────────────────────────────────────────────────
        elif st.session_state.user_role == "Manager":
            manager_mode = st.radio("Choose Action", ["Stock Refill", "🔄 Process Return"], horizontal=True)

            # ── MODE A: REFILL ───────────────────────────────────────────────
            if manager_mode == "Stock Refill":
                supplier = st.text_input("Supplier Name")
                final_transaction_payload = []

                for c_idx, cat_block in enumerate(st.session_state.form_structure):
                    selected_cat = st.selectbox(
                        "Select Category", options=categories_list, key=f"cat_sel_refill_{c_idx}"
                    )
                    st.session_state.form_structure[c_idx]["category"] = selected_cat

                    item_options = (
                        [""] + sorted(inventory_df[inventory_df["Category"] == selected_cat]["Item Name"].tolist())
                        if selected_cat and "Category" in inventory_df.columns else [""]
                    )

                    for i_idx in range(len(cat_block["items"])):
                        rc1, rc2 = st.columns([3, 1])
                        with rc1:
                            item_name = st.selectbox("Product", options=item_options, key=f"item_refill_{c_idx}_{i_idx}")
                        with rc2:
                            item_qty = st.number_input("Qty", min_value=0, step=1, key=f"qty_refill_{c_idx}_{i_idx}")

                        st.session_state.form_structure[c_idx]["items"][i_idx]["name"] = item_name
                        st.session_state.form_structure[c_idx]["items"][i_idx]["qty"]  = item_qty

                        if selected_cat and item_name and item_qty > 0:
                            sku_val = inventory_df[inventory_df["Item Name"] == item_name]["SKU"].values
                            current_sku = sku_val[0] if len(sku_val) > 0 else "N/A"
                            final_transaction_payload.append({
                                "Category":  selected_cat,
                                "Item Name": item_name,
                                "Qty":       item_qty,
                                "SKU":       current_sku,
                            })

                    if selected_cat:
                        with st.columns([1, 3])[0]:
                            if st.button("➕ Item", key=f"add_item_row_refill_{c_idx}"):
                                st.session_state.form_structure[c_idx]["items"].append({"name": "", "qty": 0})
                                st.rerun()

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
                            if insert_inward(final_transaction_payload, supplier):
                                st.success("✅ Warehouse balances updated!")
                                st.session_state.form_structure = [{"category": "", "items": [{"name": "", "qty": 0}]}]
                                st.rerun()

            # ── MODE B: PROCESS RETURN ───────────────────────────────────────
            elif manager_mode == "🔄 Process Return":
                st.write("### Log Returned Hardware")

                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    ret_dealer = st.text_input("Salesman Name", key="ret_dealer_input")
                with col_r2:
                    ret_shop = st.text_input("Shop Name", key="ret_shop_input")

                ret_cat = st.selectbox("Select Item Category", options=categories_list, key="ret_cat_select_return")
                item_opts = (
                    [""] + sorted(inventory_df[inventory_df["Category"] == ret_cat]["Item Name"].tolist())
                    if ret_cat and "Category" in inventory_df.columns else [""]
                )

                rc1, rc2 = st.columns([3, 1])
                with rc1:
                    ret_item = st.selectbox("Select Product Name", options=item_opts, key="ret_item_select_return")
                with rc2:
                    ret_qty = st.number_input("Return Qty", min_value=0, step=1, key="ret_qty_input_return")
                st.markdown("</div>", unsafe_allow_html=True)

                ret_condition = st.radio(
                    "Quality / Condition Inspection Result",
                    ["Good Item (Restock to Sellable Inventory)", "Defective Item (Send to Company for Replacement)"],
                    key="ret_condition_radio",
                )
                ret_reason = st.text_area("Reason for Return / Defect Details", key="ret_reason_area")

                if st.button("💾 Process and Log Return", type="primary", key="commit_return_btn"):
                    if not ret_dealer or not ret_shop or not ret_item or ret_qty <= 0 or not ret_reason:
                        st.error("⚠️ Please fill out all return details completely.")
                    else:
                        with st.spinner("Processing logging details..."):
                            is_good      = "Good Item" in ret_condition
                            status_text  = "Restocked" if is_good else "Pending Factory Replacement"
                            condition_tag = "Good" if is_good else "Defective"

                            sku_vals = inventory_df.loc[inventory_df["Item Name"] == ret_item, "SKU"]
                            ret_sku  = sku_vals.iloc[0] if not sku_vals.empty else "N/A"

                            return_row = {
                                "Timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Salesman Name": ret_dealer,
                                "Store Name":    ret_shop,
                                "Category":      ret_cat,
                                "SKU":           ret_sku,
                                "Item Name":     ret_item,
                                "Qty":           ret_qty,
                                "Condition":     condition_tag,
                                "Reason":        ret_reason,
                                "Status":        status_text,
                            }

                            if insert_return(return_row):
                                if is_good:
                                    st.success(f"✅ Processed! {ret_qty} units added back into live stock balances.")
                                else:
                                    st.warning("⚠️ Item marked Defective! Logged to tracker database for factory handling. Live balances left unchanged.")
                                st.rerun()

    # ── RIGHT COLUMN: LIVE INVENTORY LEDGER ──────────────────────────────────
    with right_col:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        st.subheader("📊 Live Master Inventory Ledger")
        search_query = st.text_input(
            "🔍 Search Inventory Ledger",
            placeholder="Type product name or category to filter...",
            key="global_ledger_search",
        )

        try:
            inventory_df = load_table("INVENTORY")

            if inventory_df.empty:
                st.warning("⚠️ The Inventory table appears to be empty.")
            else:
                inventory_df = clean_columns(inventory_df)
                inventory_df["Current Stock"] = pd.to_numeric(inventory_df.get("Current Stock", 0), errors="coerce").fillna(0).astype(int)

                active_selections = {}
                for cat_block in st.session_state.form_structure:
                    for item_row in cat_block.get("items", []):
                        name = item_row.get("name")
                        qty  = item_row.get("qty", 0)
                        if name and qty > 0:
                            active_selections[name] = active_selections.get(name, 0) + int(qty)

                display_df = inventory_df[["Category", "Item Name", "Current Stock"]].copy()

                def calculate_row_status(row):
                    item_name = row["Item Name"]
                    available = row["Current Stock"]
                    if item_name not in active_selections:
                        return pd.Series([2, "Normal"])
                    selected_qty = active_selections[item_name]
                    if selected_qty > available:
                        return pd.Series([0, "Red"])
                    elif (available - selected_qty) <= 5:
                        return pd.Series([0, "Yellow"])
                    else:
                        return pd.Series([1, "Green"])

                display_df[["_sort_priority", "_color_status"]] = display_df.apply(calculate_row_status, axis=1)

                if search_query:
                    q = search_query.lower()
                    display_df = display_df[
                        display_df["Item Name"].str.lower().str.contains(q, na=False)
                        | display_df["Category"].str.lower().str.contains(q, na=False)
                    ]

                display_df = display_df.sort_values(
                    by=["_sort_priority", "Category", "Item Name"],
                    ascending=[True, True, True],
                ).reset_index(drop=True)

                status_map = display_df["_color_status"].to_dict()
                clean_df   = display_df.drop(columns=["_sort_priority", "_color_status"])

                def apply_row_outlines(row):
                    status = status_map.get(row.name, "Normal")
                    if status == "Red":
                        return ["border-top: 2px solid #ff4d4f !important; border-bottom: 2px solid #ff4d4f !important; font-weight: bold; color: #ff4d4f;"] * len(row)
                    elif status == "Yellow":
                        return ["border-top: 2px solid #ffc107 !important; border-bottom: 2px solid #ffc107 !important; font-weight: bold; color: #b78103;"] * len(row)
                    elif status == "Green":
                        return ["border-top: 2px solid #52c41a !important; border-bottom: 2px solid #52c41a !important; font-weight: bold; color: #52c41a;"] * len(row)
                    else:
                        return [""] * len(row)

                st.markdown("""
                    <style>
                        div[data-testid="stDataFrame"] { width: 100% !important; max-width: 100% !important; }
                    </style>
                """, unsafe_allow_html=True)

                st.dataframe(
                    clean_df.style.apply(apply_row_outlines, axis=1),
                    hide_index=True,
                    use_container_width=True,
                    height=600,
                )

        except Exception as e:
            st.error(f"❌ Failed to load active inventory ledger: {str(e)}")