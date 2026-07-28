import streamlit as st
from utils.icons import get_lucide_html

def render_sidebar():
    with st.sidebar:
        # Header/Logo Area
        st.image("logo.png", use_container_width=True)
        st.markdown("<p style='color: #64748b; font-size: 0.78rem; margin-top: -10px; margin-bottom: 20px; text-align: center;'>Admin Center</p>", unsafe_allow_html=True)
        
        # Navigation Items
        nav_items = {
            "Overview": "Overview",
            "Inventory": "Inventory",
            "Orders": "Orders",
            "Inwards": "Inwards",
            "Suppliers": "Suppliers",
            "Returns": "Returns",
            "Transactions": "Transactions",
            "Analytics": "Analytics",
            "Reports": "Reports",
            "Settings": "Settings"
        }
        
        for label, module in nav_items.items():
            if st.button(label, use_container_width=True, key=module):
                st.session_state.active_module = module
                st.rerun()

        # Footer space
        st.markdown("---")
        st.markdown('<p style="color:#475569; font-size:0.75rem; text-align:center;">v1.0.0 Enterprise</p>', unsafe_allow_html=True)