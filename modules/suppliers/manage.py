import streamlit as st
from database.crud import load_table, add_supplier


def render():
    st.markdown('<h2 class="page-title">🏢 Supplier Management</h2>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">View and register your supplier network.</p>', unsafe_allow_html=True)

    if st.button("← Back to Dashboard"):
        st.session_state.active_module = "Overview"
        st.rerun()

    df = load_table("SUPPLIERS")

    search = st.text_input("🔍 Search suppliers by name or city", placeholder="Type to filter...")
    if search and not df.empty:
        q = search.lower()
        mask = False
        for col in ["Supplier", "City", "State"]:
            if col in df.columns:
                mask = mask | df[col].astype(str).str.lower().str.contains(q, na=False)
        df = df[mask]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Supplier ID": None,
            "Supplier": st.column_config.TextColumn("Supplier Name"),
            "City": st.column_config.TextColumn("City"),
        },
    )

    with st.expander("➕ Add New Supplier"):
        with st.form("add_supplier"):
            name = st.text_input("Supplier Name")
            city = st.text_input("City")
            state = st.text_input("State")
            specialization = st.text_input("Specialization (optional)")

            if st.form_submit_button("Register Supplier"):
                if not name or not city:
                    st.error("⚠️ Supplier name and city are required.")
                else:
                    with st.spinner("Registering supplier..."):
                        if add_supplier(name, city, state, specialization):
                            st.success(f"Supplier {name} added!")
                            st.rerun()
