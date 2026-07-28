# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import streamlit.components.v1 as components
from utils import styles  # Import your styles module
from components import sidebar, header
from modules.inventory import home, live_stock, adjustments, transactions, add_item, product_details
from modules.orders import orders
from modules.suppliers import manage
from modules.inwards import inwards
from modules.returns import returns
from modules.analytics import analytics
from modules.reports import generate_reports


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nalka Metals | Operational Admin Center",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .stButton > button { border-radius: 8px; border: 1px solid var(--line); background: #172033; color: var(--text); font-weight: 700; min-height: 40px; }
    .stButton > button[kind="primary"], .stButton > button:hover { border-color: #60a5fa; background: #1d4ed8; color: #ffffff; }
    input, textarea, [data-baseweb="select"] > div { border-radius: 8px !important; }

    /* Force columns to maintain layout on mobile */
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 100px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

styles.inject_global_css()


# 2. Global State Initialization
if 'active_module' not in st.session_state:
    st.session_state.active_module = "Overview"
if 'last_module' not in st.session_state:
    st.session_state.last_module = "Overview"


def reset_scroll_position():
    """Scrolls the workspace to the top on module navigation."""
    components.html(
        """
        <script>
            var mainContainer = window.parent.document.querySelector('.main') || window.parent.document.querySelector('[data-testid="stMain"]');
            if (mainContainer) {
                mainContainer.scrollTop = 0;
            }
            window.parent.scrollTo(0, 0);
        </script>
        """,
        height=0,
    )


# 4. Main Workspace Orchestrator
# This keeps the header and sidebar fixed, only replacing the content area
def render_main_workspace():
    # If module changed, auto-scroll to top
    if st.session_state.active_module != st.session_state.last_module:
        st.session_state.last_module = st.session_state.active_module
        reset_scroll_position()

    header.render_header()
    
    # Ensure this map correctly points to the imported module objects
    module_map = {
        "Overview": home,
        "Inventory": live_stock,
        "Adjustments": adjustments,
        "Transactions": transactions,
        "Orders": orders,
        "Suppliers": manage,
        "Inwards": inwards,
        "Returns": returns, 
        "Analytics": analytics,
        "Reports": generate_reports,
        "Inventory Add": add_item,
        "Product Details": product_details,
        "Product Catalogue": live_stock
    }
    
    current_module = module_map.get(st.session_state.active_module)
    
    if current_module and hasattr(current_module, 'render'):
        current_module.render()
    else:
        st.error(f"Module {st.session_state.active_module} is missing the render() function.")

# 5. Execute Layout
render_main_workspace()