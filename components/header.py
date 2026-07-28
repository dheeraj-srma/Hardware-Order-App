from utils.icons import get_lucide_html
import streamlit as st

MODULE_HEADERS = {
    "Overview": ("package", "primary", "Inventory Overview"),
    "Inventory": ("package", "primary", "Live Inventory"),
    "Orders": ("shopping-cart", "green", "Order Management"),
    "Inwards": ("arrow-down-to-line", "green", "Inwards (Procurement)"),
    "Returns": ("rotate-ccw", "warning", "Returns & Quality Control"),
    "Suppliers": ("building-2", "cyan", "Supplier Management"),
    "Adjustments": ("sliders", "warning", "Stock Adjustments"),
    "Transactions": ("receipt", "cyan", "Master Transaction Ledger"),
    "Analytics": ("bar-chart-3", "purple", "Analytics & Business Intelligence"),
    "Reports": ("file-text", "primary", "Executive Report Generation & Export"),
    "Inventory Add": ("plus-circle", "green", "Add Product Master"),
    "Product Details": ("clipboard-list", "primary", "Product Details"),
}


def render_header():
    """
    Renders the fixed header area for the Admin Center.
    """
    # Create the header container
    header_container = st.container()
    
    with header_container:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 1. Top Logo
            st.image("logo.png", width=180)
            
            # 2. Subtitle of the page directly below the logo
            active = st.session_state.get("active_module", "Overview")
            icon_name, icon_color, display_title = MODULE_HEADERS.get(active, ("layout-dashboard", "primary", active))
            icon_html = get_lucide_html(icon_name, size=22, color=icon_color)
            
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 6px; margin-bottom: 2px;">
                    <div>{icon_html}</div>
                    <h2 style='margin: 0; font-size: 1.25rem; color: #94a3b8; font-weight: 600; letter-spacing: 0.02em;'>
                        {display_title}
                    </h2>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            # Right-aligned utility actions
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.button("Alerts", key="notifications")
            with col_b:
                st.button("Profile", key="profile")
        
        # Horizontal rule to separate header from content
        st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid #334155;'>", unsafe_allow_html=True)