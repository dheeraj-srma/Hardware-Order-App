import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Layout Configuration (Wide mode sets up the dual-column layout)
st.set_page_config(page_title="Nalka Metals Portal", layout="wide", page_icon="🚰")

# =========================================================================
# GLOBAL CSS: Strip sidebar and enforce high-contrast layout colors
# =========================================================================
st.markdown("""
    <style>
        /* Completely hides the left-hand sidebar container and toggle arrow */
        [data-testid="stSidebarCollapse"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
        
        /* Manager & Salesman Status Notification Banner (Crisp blue contrast) */
        .status-card { 
            padding: 15px; 
            border-radius: 10px; 
            background-color: #e3f2fd !important; 
            border-left: 5px solid #007bff; 
            margin-bottom: 20px;
            color: #0d47a1 !important;
        }
        .status-card h4, .status-card p, .status-card b { color: #0d47a1 !important; }
        
        /* Admin Audit Header Card (Muted amber contrast) */
        .admin-card { 
            padding: 15px; 
            border-radius: 10px; 
            background-color: #fff3cd !important; 
            border-left: 5px solid #ffc107; 
            margin-bottom: 20px;
            color: #856404 !important;
        }
        .admin-card b { color: #856404 !important; }
        
        /* Transaction form item container */
        .row-container { 
            padding: 12px; 
            border: 1px solid #eee; 
            border-radius: 8px; 
            margin-bottom: 8px; 
            background-color: #ffffff; 
        }
        .stButton>button { width: 100%; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Initialize Session Tracking States
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'form_rows' not in st.session_state:
    st.session_state.form_rows = 1

# =========================================================================
# 3. SECURITY GATEKEEPER: LOGIN LAYOUT SCREEN (Restored to Centered Layout)
# =========================================================================
if not st.session_state.authenticated:
    # Restored to the original layout: Logo centered perfectly above the title
    logo_left, logo_core, logo_right = st.columns([3, 2, 3])
    with logo_core:
        st.image("logo.png", use_container_width=True) 
    
    st.markdown("<h2 style='text-align: center; margin-top: 0;'>🔐 Secure Hardware Portal Login</h2>", unsafe_allow_html=True)
    st.write("") 
    
    # Restrict input field width using empty tracking columns
    login_left, login_mid, login_right = st.columns([3, 2, 3])
    with login_mid:
        st.write("Please log in to verify system permissions.")
        username = st.selectbox("Select Your Role", ["", "Salesman", "Manager", "Admin"])
        password = st.text_input("Enter Password", type="password")
        
        if st.button("Log In", type="primary"):
            if username == "Manager" and password == st.secrets["passwords"]["manager"]:
                st.session_state.authenticated = True
                st.session_state.user_role = "Manager"
                st.rerun()
            elif username == "Salesman" and password == st.secrets["passwords"]["salesman"]:
                st.session_state.authenticated = True
                st.session_state.user_role = "Salesman"
                st.rerun()
            elif username == "Admin" and password == st.secrets["passwords"]["admin"]:
                st.session_state.authenticated = True
                st.session_state.user_role = "Admin"
                st.rerun()
            else:
                st.error("❌ Invalid Password Configuration.")
    st.stop()

# =========================================================================
# 4. DATABASE CONNECTIVITY PIPELINE (Runs once logged in)
# =========================================================================
DB_URL = "https://docs.google.com/spreadsheets/d/15TIyrlHAGJQULh7605CZBJIXDGQYtGFNsZCmHhssqKg/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(name):
    try:
        df = conn.read(spreadsheet=DB_URL, worksheet=name, ttl=0)
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return pd.DataFrame()

inventory_df = load_sheet("Inventory")
if not inventory_df.empty:
    inventory_df['Item Name'] = inventory_df['Item Name'].fillna('').astype(str)
    item_list = [""] + inventory_df['Item Name'].tolist()
else:
    item_list = [""]

# =========================================================================
# 5. AUTHENTICATED WORKSPACE CONFIGURATIONS
# =========================================================================

# --- CLEARANCE LEVEL A: ADMIN CONTROL PANEL ---
if st.session_state.user_role == "Admin":
    # Keep the logo pinned to the upper left corner of the admin panel
    admin_logo_col, admin_title_col = st.columns([1, 5])
    with admin_logo_col:
        st.image("logo.png", use_container_width=True)
    with admin_title_col:
        st.markdown("<h1 style='color: #856404; margin-top: 10px; margin-bottom: 0;'>Admin Audit Command Center</h1>", unsafe_allow_html=True)
    
    ac1, ac2 = st.columns([3, 1])
    with ac1:
        st.markdown("""
        <div class="admin-card">
            <b>System Clearance level:</b> 🔑 Administrator | <b>Audit Scope:</b> Full Inward & Outward Historical Logs
        </div>
        """, unsafe_allow_html=True)
    with ac2:
        if st.button("🔒 Securely Log Out System", key="admin_logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.rerun()

    st.write("---")
    inwards_df = load_sheet("Inwards")
    orders_df = load_sheet("Orders")

    tab1, tab2, tab3 = st.tabs(["📊 Master Live Inventory", "📥 Inward Refill History", "🛒 Outward Sales History"])
    
    with tab1:
        st.subheader("Current Stock Balances")
        st.dataframe(inventory_df, hide_index=True, use_container_width=True)
        
    with tab2:
        st.subheader("Inward Audit Trail (Stock Additions)")
        if not inwards_df.empty and 'Timestamp' in inwards_df.columns:
            inwards_df = inwards_df.sort_values(by='Timestamp', ascending=False)
            st.dataframe(inwards_df, hide_index=True, use_container_width=True)
        else:
            st.info("ℹ️ No incoming shipments have been logged in the 'Inwards' sheet yet.")
            
    with tab3:
        st.subheader("Outward Audit Trail (Sales/Deductions)")
        if not orders_df.empty and 'Timestamp' in orders_df.columns:
            orders_df = orders_df.sort_values(by='Timestamp', ascending=False)
            st.dataframe(orders_df, hide_index=True, use_container_width=True)
        else:
            st.info("ℹ️ No dealer orders have been logged in the 'Orders' sheet yet.")

# --- CLEARANCE LEVEL B: OPERATIONAL ROLES (SALESMAN / MANAGER SPLIT SCREEN) ---
else:
    left_col, right_col = st.columns([2, 3], gap="large") 

    with left_col:
        # Pins logo to top-left corner of the operation desk
        st.image("logo.png", width=180)
        
        purpose_text = "Outward Order Logging" if st.session_state.user_role == "Salesman" else "Inward Warehouse Stock Refill"
        
        st.markdown(f"""
        <div class="status-card">
            <h4 style='margin:0; color:#333;'>Context Status</h4>
            <p style='margin:5px 0 0 0;'><b>Active Identity:</b> 👤 {st.session_state.user_role}</p>
            <p style='margin:2px 0 0 0;'><b>Operational Scope:</b> 🛠️ {purpose_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔒 Securely Log Out System", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.form_rows = 1
            st.rerun()
            
        st.write("---")
        st.subheader("📋 Action Entry Sheet")
        
        if st.session_state.user_role == "Salesman":
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                dealer_name = st.text_input("Dealer Name")
            with col_s2:
                shop_name = st.text_input("Shop Name")
                
            order_entries = []
            for i in range(st.session_state.form_rows):
                st.markdown('<div class="row-container">', unsafe_allow_html=True)
                r1, r2 = st.columns([3, 1])
                with r1:
                    item = st.selectbox(f"Select Product", options=item_list, key=f"sale_item_{i}")
                with r2:
                    qty = st.number_input(f"Qty", min_value=0, step=1, key=f"sale_qty_{i}")
                
                if item and qty > 0:
                    current_avail = inventory_df[inventory_df['Item Name'] == item]['Current Stock'].values
                    avail_stock = current_avail[0] if len(current_avail) > 0 else 0
                    if qty > avail_stock:
                        st.warning(f"⚠️ Only {int(avail_stock)} units in stock!")
                    order_entries.append({"Item Name": item, "Qty": qty})
                st.markdown('</div>', unsafe_allow_html=True)
                
            c1, c2 = st.columns(2)
            with c1:
                if st.button("➕ Add Item Row"):
                    st.session_state.form_rows += 1
                    st.rerun()
            with c2:
                if st.button("🗑️ Reset Form"):
                    st.session_state.form_rows = 1
                    st.rerun()
                    
            if st.button("🚀 Commit Outward Order", type="primary"):
                if not dealer_name or not shop_name or not order_entries:
                    st.error("⚠️ Complete all required entries.")
                else:
                    with st.spinner("Executing stock deductions..."):
                        new_orders = pd.DataFrame(order_entries)
                        new_orders['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_orders['Dealer Name'] = dealer_name
                        new_orders['Store Name'] = shop_name
                        
                        orders_df = load_sheet("Orders")
                        updated_orders = pd.concat([orders_df, new_orders], ignore_index=True)
                        conn.update(spreadsheet=DB_URL, worksheet="Orders", data=updated_orders)
                        
                        for row in order_entries:
                            inventory_df.loc[inventory_df['Item Name'] == row['Item Name'], 'Current Stock'] -= row['Qty']
                        conn.update(spreadsheet=DB_URL, worksheet="Inventory", data=inventory_df)
                        
                        st.success("✅ Order compiled successfully!")
                        st.session_state.form_rows = 1
                        st.rerun()

        elif st.session_state.user_role == "Manager":
            supplier = st.text_input("Supplier / Factory Source Name")
            
            inward_entries = []
            for i in range(st.session_state.form_rows):
                st.markdown('<div class="row-container">', unsafe_allow_html=True)
                r1, r2 = st.columns([3, 1])
                with r1:
                    item = st.selectbox(f"Select Product", options=item_list, key=f"mgr_item_{i}")
                with r2:
                    qty = st.number_input(f"Qty Received", min_value=0, step=1, key=f"mgr_qty_{i}")
                    
                if item and qty > 0:
                    inward_entries.append({"Item Name": item, "Qty": qty})
                st.markdown('</div>', unsafe_allow_html=True)
                
            c1, c2 = st.columns(2)
            with c1:
                if st.button("➕ Add Refill Row"):
                    st.session_state.form_rows += 1
                    st.rerun()
            with c2:
                if st.button("🗑️ Reset Form"):
                    st.session_state.form_rows = 1
                    st.rerun()
                    
            if st.button("📥 Commit Inward Stock", type="primary"):
                if not supplier or not inward_entries:
                    st.error("⚠️ Specify supplier and items.")
                else:
                    with st.spinner("Processing warehouse additions..."):
                        new_inwards = pd.DataFrame(inward_entries)
                        new_inwards['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_inwards['Supplier'] = supplier
                        
                        inwards_df = load_sheet("Inwards")
                        updated_inwards = pd.concat([inwards_df, new_inwards], ignore_index=True)
                        conn.update(spreadsheet=DB_URL, worksheet="Inwards", data=updated_inwards)
                        
                        for row in inward_entries:
                            if row['Item Name'] in inventory_df['Item Name'].values:
                                inventory_df.loc[inventory_df['Item Name'] == row['Item Name'], 'Current Stock'] += row['Qty']
                            else:
                                new_prod = pd.DataFrame([{"Item Name": row['Item Name'], "Current Stock": row['Qty']}])
                                inventory_df = pd.concat([inventory_df, new_prod], ignore_index=True)
                        conn.update(spreadsheet=DB_URL, worksheet="Inventory", data=inventory_df)
                        
                        st.success("✅ Inventory balance loaded upward!")
                        st.session_state.form_rows = 1
                        st.rerun()

    with right_col:
        st.subheader("📊 Live Master Inventory Ledger")
        if not inventory_df.empty and 'Current Stock' in inventory_df.columns:
            inventory_df['Current Stock'] = pd.to_numeric(inventory_df['Current Stock'], errors='coerce').fillna(0).astype(int)
            
            tot_kinds = len(inventory_df)
            tot_units = inventory_df['Current Stock'].sum()
            
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Tracked Variants", tot_kinds)
            m_col2.metric("Total Items on Floor", tot_units)
            
            st.write("---")
            search_term = st.text_input("🔍 Filter Inventory List Quick-Search", placeholder="Type item name to scan levels...")
            filtered_df = inventory_df[inventory_df['Item Name'].str.contains(search_term, case=False)] if search_term else inventory_df
            
            st.dataframe(filtered_df, hide_index=True, use_container_width=True, height=550)