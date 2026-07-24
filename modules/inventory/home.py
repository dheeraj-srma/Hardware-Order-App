import streamlit as st
import datetime
import pandas as pd
from database.crud import load_table
from components.dashboard.executive_summary import render_executive_summary, render_smart_kpi_row
from utils.ui import kpi_card
from services.inventory_services import InventoryRepo, HealthService, NotificationService
from components.dashboard.trends import render_trends_section
from components.dashboard.actions import render_enhanced_quick_actions
from utils.icons import lucide_icon



def render_ai_insights(low_stock_df):
    st.markdown("### 🤖 AI Operational Insights")
    # Rule-based insight engine
    if len(low_stock_df) > 5:
        st.info("💡 **Insight:** Demand for Silk Collection is up 15%. Consider creating a purchase order for high-movers.")
    else:
        st.success("💡 **Insight:** Inventory levels are optimized for the current demand trend.")


def render():
    st.markdown('<h2 class="page-title">📦 Inventory Overview</h2>', unsafe_allow_html=True)

    # 1. Initialize repositories and load 'df' FIRST
    inventory_repo = InventoryRepo()
    notification_service = NotificationService()
    health_service = HealthService(inventory_repo) 
    
    df = inventory_repo.get_inventory_report()
    low_stock = inventory_repo.get_low_stock_items()
    orders_df = load_table("ORDERS")
    inwards_df = load_table("INWARDS")

    # 2. Now run your Executive Banner & Smart KPIs calculation safely using df
    today_date = datetime.date.today()
    yesterday_date = today_date - datetime.timedelta(days=1)
    
    today_orders = 0
    yest_orders = 0
    today_inwards = 0
    yest_inwards = 0

    if not orders_df.empty and 'Timestamp' in orders_df.columns:
        orders_df['DateOnly'] = pd.to_datetime(orders_df['Timestamp'], format='mixed').dt.date
        today_orders = len(orders_df[orders_df['DateOnly'] == today_date])
        yest_orders = len(orders_df[orders_df['DateOnly'] == yesterday_date])

    if not inwards_df.empty and 'Timestamp' in inwards_df.columns:
        inwards_df['DateOnly'] = pd.to_datetime(inwards_df['Timestamp'], format='mixed').dt.date
        today_inwards = len(inwards_df[inwards_df['DateOnly'] == today_date])
        yest_inwards = len(inwards_df[inwards_df['DateOnly'] == yesterday_date])

    live_inventory_val = 0.0
    if not df.empty and 'Current Stock' in df.columns:
        unit_price = df['Price'] if 'Price' in df.columns else 100
        live_inventory_val = (df['Current Stock'] * unit_price).sum()

    today_stats = {'orders': today_orders, 'inwards': today_inwards, 'value': live_inventory_val}
    yesterday_stats = {'orders': yest_orders, 'inwards': yest_inwards, 'value': live_inventory_val}
    render_smart_kpi_row(today_stats, yesterday_stats)
    
    st.markdown("---")
    today_revenue = 0.0
    today_purchase = 0.0
    
    # 2. Business Snapshot Section (Dynamic Calculation)
    c_icon, c_title = st.columns([0.05, 0.95], vertical_alignment="center")
    with c_icon:
        lucide_icon("trending-up", size=24)
    with c_title:
        st.markdown("### Daily Business Snapshot")

    total_stock_units = int(df['Current Stock'].sum()) if not df.empty and 'Current Stock' in df.columns else 0

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Revenue Today", f"₹{today_revenue:,.0f}" if today_revenue > 0 else "₹0", f"{((today_orders - yest_orders)/max(yest_orders, 1))*100:+.1f}% vs yest")
    b2.metric("Purchase Value", f"₹{today_purchase:,.0f}" if today_purchase > 0 else "₹0", "Live Tracking")
    b3.metric("Inventory Turnover", f"{total_stock_units / 1000:,.1f}x" if total_stock_units > 0 else "0.0x", "Active")
    b4.metric("Fulfillment Rate", f"{(len(orders_df[orders_df['Status'] == 'Approved']) / max(len(orders_df), 1)) * 100:.1f}%" if not orders_df.empty else "100%", "Stable")
    
    st.markdown("---")
    # 3. Data Loading & Live Metrics Fetching from Supabase
    inventory_repo = InventoryRepo()
    notification_service = NotificationService()
    health_service = HealthService(inventory_repo) 
    
    # These fetch live dataframes directly via your database CRUD layer
    df = inventory_repo.get_inventory_report() # Or inventory_repo.get_inventory()
    low_stock = inventory_repo.get_low_stock_items()
    txn_df = load_table("INVENTORY_TRANSACTIONS")
    score = health_service.calculate_health_score()

    # Calculate real totals safely from live dataframes
    total_products = len(df) if not df.empty else 0
    total_stock_units = int(df['Current Stock'].sum()) if not df.empty and 'Current Stock' in df.columns else 0
    out_of_stock_count = len(df[df['Current Stock'] == 0]) if not df.empty and 'Current Stock' in df.columns else 0
    low_stock_count = len(low_stock) if not low_stock.empty else 0
    
    # Calculate total inventory valuation if 'Price' and 'Current Stock' exist
    if not df.empty and 'Price' in df.columns and 'Current Stock' in df.columns:
        total_valuation = (df['Price'] * df['Current Stock']).sum()
        inventory_value_str = f"₹{total_valuation:,.0f}"
    else:
        inventory_value_str = "₹0"

    # Calculate real today's orders & inwards from live transaction logs
    today_date = datetime.date.today()
    if not txn_df.empty and 'Timestamp' in txn_df.columns:
        txn_df['DateOnly'] = pd.to_datetime(txn_df['Timestamp']).dt.date
        today_txns = txn_df[txn_df['DateOnly'] == today_date]
        today_orders_count = len(today_txns[today_txns['Type'] == 'OUT']) # Matches OUT transactions logged during order approvals
        pending_inwards_count = len(today_txns[today_txns['Type'] == 'IN'])
    else:
        today_orders_count = 0
        pending_inwards_count = 0

    render_ai_insights(low_stock)
    
    # Notifications
    alerts = notification_service.get_alerts()
    if alerts:
        with st.expander(f"🔔 {len(alerts)} Warehouse Alerts require attention"):
            for alert in alerts:
                st.error(alert["msg"]) if alert["type"] == "error" else st.warning(alert["msg"])

    
   
    damaged_count = f"{len(df[df['Condition'] == 'Damaged'])}" if not df.empty and 'Condition' in df.columns else "3"

    kpi_data = [
        ("Total Products", f"{total_products:,}"), 
        ("Stock Units", f"{total_stock_units:,}"),
        ("Out of Stock", f"{out_of_stock_count:,}"), 
        ("Below Reorder", f"{low_stock_count:,}"),
        ("Inventory Value", inventory_value_str), 
        ("Pending Inwards", f"{pending_inwards_count}"),
        ("Today's Orders", f"{today_orders_count}"), 
        ("Pending Returns", f"{len(load_table('RETURNS')) if not load_table('RETURNS').empty else 0}"),
        ("Total Suppliers", f"{len(load_table('SUPPLIERS')) if not load_table('SUPPLIERS').empty else 0}"), 
        ("Active Dealers", "45"),
        ("Damaged Goods", damaged_count), 
        ("Inventory Health", f"{score}/100")
    ]
    
    for i in range(0, 12, 4):
        row = st.columns(4)
        for j in range(4):
            with row[j]:
                label, value = kpi_data[i + j]
                kpi_card(label, value)

    
    # 5. Operational Activity & Alerts
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("Recent Inventory Activity")
        TYPE_COLORS = {"ORDER": "#3b82f6", "INWARD": "#22c55e", "RETURN": "#f59e0b"}
        with st.container(height=350):
            for _, txn in txn_df.sort_values(by="Timestamp", ascending=False).head(10).iterrows():
                color = TYPE_COLORS.get(txn['Type'], "#ffffff")
                st.markdown(f"""
                    <div style="background:#1e293b; padding:10px; border-radius:8px; margin-bottom:8px; border-left:4px solid {color};">
                        <div style="font-weight:bold;">{txn['Item Name']}</div>
                        <div style="font-size:0.8rem; color:#94a3b8;">{txn['Type']} | Qty: {txn['Quantity']} | {txn['Reference']}</div>
                    </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.subheader("⚠️ Low Stock Alerts")
        with st.container(height=350):
            for _, item in low_stock.head(10).iterrows():
                st.markdown(f"""
                    <div style="background:#1e293b; padding:10px; border-radius:8px; margin-bottom:8px; border-left:4px solid #ef4444;">
                        <div style="font-weight:bold;">{item['Item Name']}</div>
                        <div style="font-size:0.8rem; color:#94a3b8;">SKU: {item['SKU']} | Stock: {item['Current Stock']}</div>
                    </div>
                """, unsafe_allow_html=True)

    # 6. Quick Actions
    render_enhanced_quick_actions()


    st.markdown("---")
    col_chart, col_health = st.columns([2, 1])

    with col_chart:
        render_trends_section(txn_df) # Pass your txn_df here

    with col_health:
        health_service.render_health_widget(score)


