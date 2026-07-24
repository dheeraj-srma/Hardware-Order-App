import streamlit as st
from services.inventory_services import InventoryRepo

def render():
    st.markdown("## ➕ Add New Product Master")
    
    # Navigation
    if st.button("← Back to Dashboard"):
        st.session_state.active_module = "Overview"
        st.rerun()

    inventory_repo = InventoryRepo()
    
    # Fetch categories for the dropdown
    available_categories = inventory_repo.get_all_categories()

    with st.form("new_product_form", clear_on_submit=True):
        name = st.text_input("Product Name*")
        sku = st.text_input("SKU/Barcode*")
        
        # Dropdown populated from database
        category = st.selectbox("Category", options=available_categories if available_categories else ["General"])
        
        base_price = st.number_input("Base Purchase Price", min_value=0.0, format="%.2f")
        
        
        submitted = st.form_submit_button("Save New Product")
        
        if submitted:
            if name and sku:
                success = inventory_repo.add_new_item_master(name, sku, category, base_price)
                if success:
                    st.success(f"Product '{name}' added successfully!")
                else:
                    st.error("Failed to save product. Check database connection.")
            else:
                st.error("Name and SKU are mandatory.")