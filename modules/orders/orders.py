import streamlit as st
from database.crud import load_table, approve_order
from sqlalchemy import text
from utils.icons import get_lucide_html

def render():
    st.markdown('<p class="page-subtitle">Review, search, and approve incoming orders.</p>', unsafe_allow_html=True)

    if st.button("Back to Dashboard"):
        st.session_state.active_module = "Overview"
        st.rerun()

    df = load_table("ORDERS")
    if df.empty or "Status" not in df.columns:
        st.info("No orders recorded yet.")
        return

    search_col, status_col = st.columns([3, 1])
    with search_col:
        search = st.text_input("Search by Order ID, SKU, Item, or Salesman", placeholder="Type to filter...")
    with status_col:
        status_filter = st.selectbox("Status", ["All"] + sorted(df["Status"].dropna().unique().tolist()))

    filtered = df.copy()
    if search:
        q = search.lower()
        mask = False
        for col in ["Order ID", "SKU", "Item Name", "Salesman Name"]:
            if col in filtered.columns:
                mask = mask | filtered[col].astype(str).str.lower().str.contains(q, na=False)
        filtered = filtered[mask]
    if status_filter != "All":
        filtered = filtered[filtered["Status"] == status_filter]

    pending = filtered[filtered["Status"] == "Pending"]
    approved = filtered[filtered["Status"] == "Approved"].sort_values(by="Timestamp", ascending=False).head(20)

    st.markdown('<div class="section-label">Pending Orders</div>', unsafe_allow_html=True)
    if pending.empty:
        st.info("No pending orders match the current filters.")
    else:
        st.dataframe(
            pending,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Salesman ID": None,
                "Location ID": None,
                "Order ID": st.column_config.TextColumn("Order ID", width="small"),
                "Timestamp": st.column_config.DatetimeColumn("Ordered At", format="DD/MM/YYYY HH:mm"),
                "Quantity": st.column_config.NumberColumn("Qty", format="%d"),
            },
        )

        pending_order_ids = pending["Order ID"].dropna().unique().tolist()
        order_id = st.selectbox("Select Order ID to Approve", pending_order_ids)

        if st.button("Approve & Deduct Stock", type="primary", key="approve_ordr"):
            with st.spinner("Approving order and updating stock..."):
                if approve_order(order_id):
                    st.success(f"Order {order_id} approved and inventory updated!")
                    st.rerun()

    st.divider()

    st.markdown('<div class="section-label">Recently Approved</div>', unsafe_allow_html=True)
    if approved.empty:
        st.write("No recently approved orders match the current filters.")
    else:
        st.dataframe(
            approved,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Salesman ID": None,
                "Location ID": None,
                "Status": None,
                "Timestamp": st.column_config.DatetimeColumn("Approved At", format="DD/MM HH:mm"),
            },
        )
