import streamlit as st
import pandas as pd
from database.crud import load_table
from utils.icons import get_lucide_html
from modules.analytics.sections import (
    render_section_executive_overview,
    render_section_sales_intelligence,
    render_section_inventory_intelligence,
    render_section_dealer_intelligence,
    render_section_geographic_intelligence,
    render_section_returns_intelligence,
    render_section_supplier_intelligence,
)


def render():
    # ---------------------------------------------------------
    # TOP HEADER & BACK NAVIGATION
    # ---------------------------------------------------------
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Dashboard"):
            st.session_state.active_module = "Overview"
            st.rerun()

    # Load Core Raw Datasets directly
    inv_df = load_table("INVENTORY")
    orders_df = load_table("ORDERS")
    inwards_df = load_table("INWARDS")
    returns_df = load_table("RETURNS")
    txn_df = load_table("INVENTORY_TRANSACTIONS")

    # ---------------------------------------------------------
    # THE 7 ENTERPRISE BI SECTIONS
    # ---------------------------------------------------------
    (
        tab_exec,
        tab_sales,
        tab_inv,
        tab_dealer,
        tab_geo,
        tab_returns,
        tab_supplier,
    ) = st.tabs([
        "1. Executive Overview",
        "2. Sales Intelligence",
        "3. Inventory Intelligence",
        "4. Dealer Intelligence",
        "5. Geographic Intelligence",
        "6. Returns Intelligence",
        "7. Supplier Intelligence",
    ])

    with tab_exec:
        render_section_executive_overview(orders_df, inv_df, inwards_df, returns_df, txn_df)

    with tab_sales:
        render_section_sales_intelligence(orders_df, inv_df, txn_df)

    with tab_inv:
        render_section_inventory_intelligence(inv_df, txn_df)

    with tab_dealer:
        render_section_dealer_intelligence(orders_df)

    with tab_geo:
        render_section_geographic_intelligence(orders_df)

    with tab_returns:
        render_section_returns_intelligence(returns_df, orders_df)

    with tab_supplier:
        render_section_supplier_intelligence(inwards_df, returns_df)
