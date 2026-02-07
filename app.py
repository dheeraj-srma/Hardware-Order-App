import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Hardware Order Portal", layout="centered")

conn = st.connection("gsheets", type=GSheetsConnection)

# -------------------------------
# Load inventory
# -------------------------------
@st.cache_data(ttl=600)
def load_inventory():
    return conn.read(worksheet="Inventory")

inventory = load_inventory()


inventory['Item Name'] = inventory['Item Name'].astype(str)
inventory['Category'] = inventory['Category'].astype(str)
inventory['SKU'] = inventory['SKU'].astype(str)

categories = sorted(inventory["Category"].unique().tolist())

# -------------------------------
# UI
# -------------------------------

st.markdown("""
<style>
img {
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1,4])

with col1:
    st.image("logo.png")

with col2:
    st.markdown("## Order Portal")


# Dealer info
c1, c2 = st.columns(2)
with c1:
    dealer_name = st.text_input("Dealer Name")
with c2:
    shop_name = st.text_input("Shop Name")

st.write("---")
st.subheader("📋 Build Your Order")

# Track number of category sections
if "num_rows" not in st.session_state:
    st.session_state.num_rows = 1

order_data = []

# -------------------------------
# Category sections
# -------------------------------
for i in range(st.session_state.num_rows):
    st.markdown("---")
    st.markdown(f"### Item {i+1}")

    category = st.selectbox(
        "Select Category",
        [""] + categories,
        key=f"cat_{i}"
    )

    if category:
        category_items = inventory[
            inventory["Category"] == category
        ]

        item_names = category_items["Item Name"].tolist()

        selected_items = st.multiselect(
            "Select Items",
            item_names,
            key=f"items_{i}"
        )

        for item in selected_items:
            qty = st.number_input(
                f"Qty for {item}",
                min_value=0,
                step=1,
                key=f"qty_{i}_{item}"
            )

            if qty > 0:
                sku = category_items.loc[
                    category_items["Item Name"] == item,
                    "SKU"
                ].values[0]

                order_data.append({
                    "Item Name": item,
                    "Category": category,
                    "SKU": sku,
                    "Qty": qty
                })

# -------------------------------
# Buttons
# -------------------------------
colA, colB = st.columns(2)

with colA:
    if st.button("➕ Add Item"):
        st.session_state.num_rows += 1

with colB:
    if st.button("🗑️ Reset"):
        st.session_state.num_rows = 1

st.write("---")

# -------------------------------
# Submit order
# -------------------------------
if st.button("🚀 Submit Order", type="primary"):
    if not dealer_name or not shop_name:
        st.error("Dealer and Shop name required")
    elif not order_data:
        st.error("Add at least one item with quantity")
    else:
        orders_df = conn.read(worksheet="Orders", ttl=60)

        today = datetime.now().strftime("%Y%m%d")
        if orders_df is not None and not orders_df.empty:
            today_orders = orders_df[
                orders_df["Order ID"].astype(str).str.contains(today, na=False)
            ]
            count = len(today_orders) + 1
        else:
            count = 1

        order_id = f"ORD-{today}-{str(count).zfill(3)}"

        final_rows = []
        for row in order_data:
            final_rows.append({
                "Order ID": order_id,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Dealer Name": dealer_name,
                "Shop Name": shop_name,
                **row
            })

        final_df = pd.DataFrame(final_rows)

        existing_orders = conn.read(worksheet="Orders", ttl=60)

        if existing_orders is None or existing_orders.empty:
            updated_orders = final_df
        else:
            updated_orders = pd.concat(
                [existing_orders, final_df],
                ignore_index=True
            )

        conn.update(worksheet="Orders", data=updated_orders)

        st.success(f"✅ Order {order_id} submitted!")
        st.balloons()

        st.session_state.num_rows = 1

# -------------------------------
# Footer
# -------------------------------
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 10px;
        right: 15px;
        font-size: 12px;
        color: gray;
        opacity: 0.8;
    }
    </style>
    <div class="footer">
        Made by Dheeraj Sharma
    </div>
    """,
    unsafe_allow_html=True
)
