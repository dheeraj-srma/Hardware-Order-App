import streamlit as st
from database.crud import load_table, adjust_stock

def render():
    st.markdown('<h2 class="page-title">⚖️ Stock Adjustments</h2>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Reconcile system stock against a physical count.</p>', unsafe_allow_html=True)

    if st.button("← Back to Dashboard"):
        st.session_state.active_module = "Overview"
        st.rerun()

    df = load_table("INVENTORY")
    if df.empty or "Category" not in df.columns or "SKU" not in df.columns:
        st.warning("⚠️ No inventory items found.")
        return

    categories = df["Category"].dropna().unique().tolist()

    with st.form("adjustment_form", clear_on_submit=False):
        st.markdown("### Adjustment Details")
        
        # 1. Category selection
        selected_category = st.selectbox("Category", categories, key="adj_category")
        
        # Filter dataframe strictly by chosen category
        filtered_df = df[df["Category"] == selected_category]
        available_items = filtered_df["Item Name"].dropna().unique().tolist() if not filtered_df.empty else []

        col1, col2 = st.columns(2)
        
        with col1:
            # 2. Item Name selection (restricted to the selected category)
            selected_item_name = st.selectbox("Item Name", available_items, key="adj_item_name")
            
            # 3. Auto-select SKU and current stock based on item and category
            sku_matched_row = filtered_df[filtered_df["Item Name"] == selected_item_name]
            selected_sku = sku_matched_row.iloc[0]["SKU"] if not sku_matched_row.empty else ""
            
            current_val = int(sku_matched_row.iloc[0].get("Current Stock", 0) or 0) if not sku_matched_row.empty else 0
            
            st.text_input("SKU (Auto-Selected)", value=selected_sku, disabled=True)
            st.info(f"Current System Stock: **{current_val}**")

        with col2:
            new_quantity = st.number_input("New Physical Count", min_value=0, step=1, value=current_val)
            reason = st.selectbox("Reason", ["Physical Verification", "Damaged Goods", "Lost", "Other"])

        submitted = st.form_submit_button("Confirm Adjustment", type="primary")

        if submitted:
            if not selected_sku:
                st.error("❌ Could not resolve a valid SKU for the selected Category and Item.")
            else:
                with st.spinner("Applying adjustment..."):
                    # Pass selected_category, selected_sku, selected_item_name, new_quantity, current_val, and reason
                    if adjust_stock(selected_sku, selected_item_name, selected_category, int(new_quantity), current_val, reason):
                        st.success(f"Successfully adjusted {selected_item_name} ({selected_sku}) to {new_quantity}!")
                        st.rerun()