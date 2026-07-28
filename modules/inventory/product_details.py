import streamlit as st
from database.crud import load_table
from utils.icons import get_lucide_html

def render():
    if st.button("Back to Dashboard"):
        st.session_state.active_module = "Overview"
        st.rerun()

    # 1. Fetch Inventory to populate the search
    inventory = load_table("INVENTORY")
    
    # Create a display list (SKU - Item Name) for easy searching
    inventory['Display'] = inventory['SKU'] + " - " + inventory['Item Name']
    product_list = inventory['Display'].tolist()

    # 2. Selection UI
    selected_display = st.selectbox("Select a product to view details:", options=[""] + product_list)

    if selected_display:
        # Extract SKU from the selection
        selected_sku = selected_display.split(" - ")[0]
        product = inventory[inventory["SKU"] == selected_sku].iloc[0]
        
        # 3. Header & Info
        st.markdown(f"### {product['Item Name']}")
        st.write(f"**SKU:** {selected_sku} | **Category:** {product['Category']}")
        
        # 4. KPI Summary
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Stock", product["Current Stock"])
        col2.metric("Unit Price", f"₹{product['Price']:,}")
        col3.metric("Inventory Value", f"₹{(product['Current Stock'] * product['Price']):,}")
        
        st.markdown("---")
        
        # 5. Movement Timeline
        st.markdown(f"### {get_lucide_html('history', size=22, color='purple')} Movement History", unsafe_allow_html=True)
        txns = load_table("INVENTORY_TRANSACTIONS")
        product_history = txns[txns["SKU"] == selected_sku].sort_values(by="Timestamp", ascending=False)
        
        if not product_history.empty:
            st.dataframe(product_history[["Timestamp", "Type", "Quantity", "Reference"]], use_container_width=True, hide_index=True)
        else:
            st.info("No movement history for this item.")
    else:
        st.info("Please select a product from the dropdown above to begin.")