import streamlit as st
from database.crud import load_table
from utils.ui import kpi_card




def render():
    st.markdown(
        '<h2 class="page-title">📜 Master Transaction Ledger</h2>',
        unsafe_allow_html=True
    )

    df = load_table("INVENTORY_TRANSACTIONS")

    if df.empty:
        st.warning("No transaction history available.")
        return

    df["Type"] = (
        df["Type"]
        .astype(str)
        .str.strip()
        .str.upper()
    )


    orders_df = df[df["Type"] == "OUT"]

    inward_df = df[
        df["Type"].isin([
            "IN",
            "REPLACEMENT_IN"
        ])
    ]

    returns_df = df[
        df["Type"].isin([
            "RETURN_GOOD",
            "RETURN_DEFECTIVE"
        ])
    ]

    replacement_df = df[
        df["Type"] == "REPLACEMENT_IN"
    ]


    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "OUTGOING",
            f"{len(orders_df):,}",
            "🛒",
            "Sales Orders"
        )

    with c2:
        kpi_card(
            "INCOMING",
            f"{len(inward_df):,}",
            "📦",
            "Stock Received",
            "positive"
        )

    with c3:
        kpi_card(
            "RETURNS",
            f"{len(returns_df):,}",
            "↩️",
            "Goods Returned",
            "warning"
        )

    with c4:
        kpi_card(
            "REPLACEMENTS",
            f"{len(replacement_df):,}",
            "🔄",
            "Replacement Stock",
            "info"
        )

    st.write("")

    # ====================================================
    # Helper
    # ====================================================

    def render_table(title, icon, data):

        st.subheader(f"{icon} {title}")

        if data.empty:
            st.info("No records available.")
            return

        st.dataframe(
            data.sort_values(
                "Timestamp",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True,
            height=600,
            column_config={
                "Txn ID": st.column_config.TextColumn(
                    "Txn ID",
                    width="small"
                ),
                "Timestamp": st.column_config.DatetimeColumn(
                    "Timestamp",
                    format="DD/MM/YYYY HH:mm"
                )
            }
        )


    tab1, tab2, tab3, tab4 = st.tabs([

        f"🛒 Orders ({len(orders_df)})",

        f"📦 Inwards ({len(inward_df)})",

        f"↩️ Returns ({len(returns_df)})",

        "📜 Audit Trail"

    ])

    with tab1:

        render_table(
            "Recent Orders",
            "🛒",
            orders_df
        )

    with tab2:

        render_table(
            "Recent Inwards",
            "📦",
            inward_df
        )

    with tab3:

        render_table(
            "Recent Returns",
            "↩️",
            returns_df
        )

    with tab4:

        render_table(
            "Complete Transaction History",
            "📜",
            df
        )