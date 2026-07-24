import streamlit as st
from utils import styles  # Import your styles module
from components import sidebar, header
from modules.inventory import home, live_stock, adjustments, transactions, add_item, product_details
from modules.orders import orders
from modules.suppliers import manage
from modules.inwards import inwards
from modules.returns import returns


st.markdown(
    """
    <style>
    .stButton > button { border-radius: 8px; border: 1px solid var(--line); background: #172033; color: var(--text); font-weight: 700; min-height: 40px; }
    .stButton > button[kind="primary"], .stButton > button:hover { border-color: #60a5fa; background: #1d4ed8; color: #ffffff; }
    input, textarea, [data-baseweb="select"] > div { border-radius: 8px !important; }

    </style>
    
    <style>
    /* Force columns to maintain layout on mobile */
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 100px !important;
    }
    </style>
    """,

    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nalka Metals Portal",
    page_icon="NM",
    layout="wide",
    initial_sidebar_state="expanded",
)


styles.inject_global_css()



# 1. Page Configuration
st.set_page_config(
    page_title="Nalka Metals | Admin Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Global State Initialization
if 'active_module' not in st.session_state:
    st.session_state.active_module = "Overview"




# 4. Main Workspace Orchestrator
# This keeps the header and sidebar fixed, only replacing the content area
def render_main_workspace():
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
        "Transactions": transactions,
        "Inventory Add": add_item,
        "Product Details": product_details,
        "Product Catalogue": live_stock
    }
    
    # Use .get() but ensure the module has a 'render' function
    current_module = module_map.get(st.session_state.active_module)
    
    if current_module and hasattr(current_module, 'render'):
        current_module.render()
    else:
        st.error(f"Module {st.session_state.active_module} is missing the render() function.")

# 5. Execute Layout
render_main_workspace()