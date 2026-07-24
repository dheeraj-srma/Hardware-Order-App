import streamlit as st
import pandas as pd
from database.crud import load_table, insert_inward


def render():
    st.markdown('<h2 class="page-title">📦 Inwards (Procurement)</h2>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Record stock received from suppliers.</p>', unsafe_allow_html=True)

    if st.button("← Back to Dashboard"):
        st.session_state.active_module = "Overview"
        st.rerun()

    suppliers = load_table("SUPPLIERS")
    inventory = load_table("INVENTORY")

    if suppliers.empty or "Supplier Name" not in suppliers.columns:
        st.warning("⚠️ No suppliers found. Add one under Suppliers first.")
        return
    if inventory.empty or "SKU" not in inventory.columns or "Category" not in inventory.columns:
        st.warning("⚠️ No inventory items found.")
        return

    categories = inventory["Category"].dropna().unique().tolist()

    with st.form("inwards_form"):
        st.markdown("### Procurement Details")
        
        # 1. Category Filter Dropdown
        selected_category = st.selectbox("Category", categories, key="inward_category")
        
        # Filter inventory rows matching the chosen category
        filtered_inventory = inventory[inventory["Category"] == selected_category]
        available_items = filtered_inventory["Item Name"].dropna().unique().tolist() if not filtered_inventory.empty else []

        col1, col2 = st.columns(2)
        with col1:
            supplier = st.selectbox("Select Supplier", suppliers["Supplier Name"].dropna().tolist())
            
            # 2. Item Name Filter Dropdown (Strictly filtered by category)
            selected_item_name = st.selectbox("Item Name", available_items, key="inward_item_name")
            
            # 3. Auto-select SKU and current stock based on category and item selection
            sku_matched_row = filtered_inventory[filtered_inventory["Item Name"] == selected_item_name]
            sku = sku_matched_row.iloc[0]["SKU"] if not sku_matched_row.empty else ""
            current_stock = int(sku_matched_row.iloc[0].get("Current Stock", 0) or 0) if not sku_matched_row.empty else 0
            
            st.text_input("SKU (Auto-Selected)", value=sku, disabled=True)
            st.info(f"Current System Stock: **{current_stock}**")

        with col2:
            qty = st.number_input("Quantity Received", min_value=1, step=1, value=1)
            ref = st.text_input("Reference/Invoice Number")

        if st.form_submit_button("🚀 Record Inward Shipment", type="primary"):
            if not sku:
                st.error("❌ Could not resolve a valid SKU for the selected Category and Item.")
            else:
                with st.spinner("Recording shipment and updating stock..."):
                    if insert_inward(sku, selected_item_name, selected_category, supplier, int(qty)):
                        st.success(f"Successfully added {qty} units to {selected_item_name} ({sku}) from {supplier}!")
                        st.rerun()

    st.divider()
    st.markdown('<div class="section-label">Recent Inwards</div>', unsafe_allow_html=True)
    inwards_df = load_table("INWARDS")
    if inwards_df.empty:
        st.info("No inward shipments recorded yet.")
    else:
        ts_col = "Timestamp" if "Timestamp" in inwards_df.columns else None
        st.dataframe(
            inwards_df.sort_values(ts_col, ascending=False) if ts_col else inwards_df,
            use_container_width=True,
            hide_index=True,
            height=360,
        )