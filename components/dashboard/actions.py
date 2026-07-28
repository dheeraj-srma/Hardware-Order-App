import streamlit as st
from utils.icons import get_lucide_html


def render_enhanced_quick_actions():
    st.markdown(f"### {get_lucide_html('zap', size=22, color='warning')} Quick Actions", unsafe_allow_html=True)
    
    # Primary Workflow (Highest Frequency)
    row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)
    with row1_c1:
        if st.button("Receive Stock", use_container_width=True):
            st.session_state.active_module = "Inwards"
            st.rerun()
    with row1_c2:
        if st.button("Approve Orders", use_container_width=True):
            st.session_state.active_module = "Orders"
            st.rerun()
    with row1_c3:
        if st.button("Process Returns", use_container_width=True):
            st.session_state.active_module = "Returns"
            st.rerun()
    with row1_c4:
        if st.button("Add Product", use_container_width=True):
            st.session_state.active_module = "Inventory Add"
            st.rerun()

    # Secondary/Admin Actions
    row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)
    with row2_c1:
        if st.button("Create Supplier", use_container_width=True):
            st.session_state.active_module = "Suppliers"
    with row2_c2:
        if st.button("Open Analytics", use_container_width=True):
            st.session_state.active_module = "Analytics"
    with row2_c3:
        if st.button("Export Inventory", use_container_width=True):
            # Integrate your existing export function here
            st.toast("Inventory Exported")
    with row2_c4:
        if st.button("Gen. Purchase Order", use_container_width=True):
            st.session_state.active_module = "PO_Generator"
            
    # Utility/Maintenance Actions
    with st.expander("System Utilities"):
        sub1, sub2, sub3, sub4, sub5  = st.columns([2,2,2,2,2])
        with sub1:
            if st.button("Adjust Stock"):
                st.session_state.active_module = "Adjustments"
        with sub2:
            if st.button("Backup Database"):
                # Call your existing backup logic
                st.info("Database backed up successfully.")
        with sub3:
            if st.button("Generate Report"):
                st.session_state.active_module = "Reports"

        with sub4:
            if st.button("Product Details"):
                st.session_state.active_module = "Product Details"

        with sub5:
            if st.button("Product Catalogue"):
                st.session_state.active_module = "Product Catalogue"


    
