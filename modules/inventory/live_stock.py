import streamlit as st
from database.crud import load_table

def render():
    st.markdown('<h2 class="page-title">📦 Live Inventory</h2>', unsafe_allow_html=True)
    # Navigation

    if st.button("← Back to Dashboard"):
        st.session_state.active_module = "Overview"
        st.rerun()
    # 1. Fetch Data
    df = load_table("INVENTORY")
    df.columns = df.columns.str.strip() 

    # 2. Unified Horizontal Layout
    # Using 4 columns: [Search, Category, QuickView, Refresh]
    c1, c2, c3, c4 = st.columns([2, 1, 1, 0.5])

    with c1:
        search = st.text_input("🔍 Search by SKU or Name", placeholder="Type SKU or Product Name...")
    
    with c2:
        category = st.selectbox("Category", ["All"] + df["Category"].unique().tolist())

        

    # 3. Apply Filters
    if search:
        df = df[df["Item Name"].str.contains(search, case=False) | df["SKU"].str.contains(search, case=False)]
    if category != "All":
        df = df[df["Category"] == category]
        
    # 4. Interactive Inventory Table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "SKU": st.column_config.TextColumn("SKU"),
            "Item Name": st.column_config.TextColumn("Product Name"),
            "Category": st.column_config.TextColumn("Category"),
            "Current Stock": None,
            "Price": st.column_config.NumberColumn("Price (₹)", format="₹%d")
        }
    )