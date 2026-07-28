import datetime
import streamlit as st
from database.crud import load_table, insert_return
from utils.icons import get_lucide_html

def render():
    st.markdown("""
        <p class="page-subtitle">Log customer returns, map conditions to reasons, and route stock accordingly.</p>
    """, unsafe_allow_html=True)

    if st.button("Back to Dashboard"):
        st.session_state.active_module = "Overview"
        st.rerun()

    inventory = load_table("INVENTORY")
    if inventory.empty or "Category" not in inventory.columns:
        st.warning("No inventory items found.")
        return
    
    categories = inventory["Category"].dropna().unique().tolist()

    with st.form("returns_form", clear_on_submit=False):
        st.markdown("### Return Details Form")
        
        # Category is at the top of the form
        selected_category = st.selectbox(
            "Category", 
            categories, 
            key="form_category"
        )
        
        filtered_inventory = inventory[inventory["Category"] == selected_category]
        available_items = filtered_inventory["Item Name"].dropna().unique().tolist() if not filtered_inventory.empty else []

        col1, col2 = st.columns(2)
        
        with col1:
            selected_item_name = st.selectbox("Item Name", available_items)
            
            # Auto-select SKU based on choices
            sku_matched_row = filtered_inventory[filtered_inventory["Item Name"] == selected_item_name]
            auto_sku = sku_matched_row.iloc[0]["SKU"] if not sku_matched_row.empty else ""
            
            st.text_input("SKU (Auto-Selected)", value=auto_sku, disabled=True)
            qty = st.number_input("Quantity", min_value=1, step=1)
            salesman_name = st.text_input("Salesman Name", placeholder="Enter salesman name...")

        with col2:
            shop_name = st.text_input("Shop Name / Customer", placeholder="e.g., Sharma Hardware Store")
            
            # Condition placed between Shop Name and Reason box
            condition = st.selectbox(
                "Condition", 
                ["Good", "Defective"], 
                key="form_condition"
            )
            
            # Dynamic reason mapping based on condition choice
            if condition == "Good":
                reason_options = ["Customer Changed Mind", "Excess Inventory", "Wrong Item Ordered"]
                default_status = "Restocked"
                action_label = "Action: Return to Stock"
            else:
                reason_options = ["Leakage", "Packaging Failure", "Damaged in Transit", "Defective Quality"]
                default_status = "Replacement Completed"
                action_label = "Action: Replacement / Write-off"

            reason = st.selectbox("Reason", reason_options)
            
            st.markdown(f"**Assigned Status:** `{default_status}`")
            st.info(action_label)

        submitted = st.form_submit_button("Process Return")

        if submitted:
            if not shop_name.strip():
                st.error("Please provide the Shop Name.")
            elif not salesman_name.strip():
                st.error("Please provide the Salesman Name.")
            elif not auto_sku:
                st.error("Could not resolve a valid SKU for the selected Category and Item.")
            else:
                return_row = {
                    "Timestamp":     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Salesman Name": salesman_name,
                    "Shop Name":     shop_name,
                    "SKU":           auto_sku,
                    "Item Name":     selected_item_name,
                    "Category":      selected_category,
                    "Quantity":      int(qty),
                    "Condition":     condition,      
                    "Reason":        reason,         
                    "Status":        default_status, 
                    "Action":        "Return to Stock" if condition == "Good" else "Discard/Write-off",
                }
                
                with st.spinner("Processing return..."):
                    if insert_return(return_row):
                        st.success(f"Return for {selected_item_name} ({auto_sku}) processed successfully!")
                        st.rerun()

    st.divider()
    st.markdown('<div class="section-label">Recent Returns</div>', unsafe_allow_html=True)
    returns_df = load_table("RETURNS")
    if returns_df.empty:
        st.info("No returns logged yet.")
    else:
        ts_col = "Timestamp" if "Timestamp" in returns_df.columns else None
        st.dataframe(
            returns_df.sort_values(ts_col, ascending=False) if ts_col else returns_df,
            use_container_width=True,
            hide_index=True,
            height=360,
        )