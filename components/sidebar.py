import streamlit as st

def render_sidebar():
    with st.sidebar:
        # Header/Logo Area
        st.markdown("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #ffffff; font-size: 1.5rem; margin: 0;">NALKA METALS</h2>
                <p style="color: #64748b; font-size: 0.8rem;">Admin Center</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation Items
        # We store the mapping and current state here to update the main view
        nav_items = {
            "🏠 Overview": "Overview",
            "📦 Inventory": "Inventory",
            "🛒 Orders": "Orders",
            "📥 Inwards": "Inwards",
            "🏢 Suppliers": "Suppliers",
            "↩ Returns": "Returns",
            "📜 Transactions": "Transactions",
            "⚙ Settings": "Settings"
        }
        
        for label, module in nav_items.items():
            if st.button(label, use_container_width=True, key=module):
                st.session_state.active_module = module
                st.rerun()

        # Footer space
        st.markdown("---")
        st.markdown('<p style="color:#475569; font-size:0.75rem; text-align:center;">v1.0.0 Enterprise</p>', unsafe_allow_html=True)