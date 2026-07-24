import streamlit as st

def render_global_search():
    # Placeholder for the search input
    search_query = st.text_input("🔍 Global Search...", placeholder="SKU, Order ID, Supplier...", label_visibility="collapsed")
    
    if search_query:
        # Example logic: redirect based on query prefix
        if search_query.startswith("SKU"):
            st.query_params["sku"] = search_query
            st.session_state.active_module = "Inventory"
            st.rerun()
        elif search_query.startswith("ORD"):
            st.session_state.active_module = "Orders"
            st.rerun()