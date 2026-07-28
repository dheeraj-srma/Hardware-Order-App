import streamlit as st
import datetime
import pandas as pd
from database.crud import load_table
from components.dashboard.executive_summary import render_executive_summary, render_smart_kpi_row
from utils.ui import kpi_card
from services.inventory_services import InventoryRepo, HealthService, NotificationService
from components.dashboard.trends import render_trends_section
from components.dashboard.actions import render_enhanced_quick_actions
from utils.icons import get_lucide_html, lucide_icon



def render_ai_insights(inventory_df, low_stock_df, txn_df, orders_df):
    bot_icon = get_lucide_html('bot', size=22, color='purple')
    st.markdown(f"### {bot_icon} AI Operational Insights & Smart Recommendations", unsafe_allow_html=True)
    
    insights = []

    # 1. Critical Reorder & Depletion Insight
    out_of_stock = inventory_df[inventory_df['Current Stock'] <= 0] if not inventory_df.empty and 'Current Stock' in inventory_df.columns else pd.DataFrame()
    if not out_of_stock.empty:
        item_names = ", ".join(out_of_stock['Item Name'].head(3).tolist())
        insights.append({
            "type": "danger",
            "tag": "CRITICAL REORDER",
            "icon": "alert-triangle",
            "title": f"{len(out_of_stock)} SKUs are completely out of stock",
            "desc": f"Products like <strong>{item_names}</strong> have 0 units on hand. Urgent inward replenishment required to prevent order rejections.",
            "action_label": "Create Inward PO",
            "action_module": "Inwards"
        })
    elif not low_stock_df.empty:
        item_names = ", ".join(low_stock_df['Item Name'].head(3).tolist())
        insights.append({
            "type": "warning",
            "tag": "STOCK ALERT",
            "icon": "package-minus",
            "title": f"{len(low_stock_df)} items are below safety threshold (< 5 units)",
            "desc": f"Low stock threshold breach detected for <strong>{item_names}</strong>. Reorder recommended to prevent fulfillment bottlenecks.",
            "action_label": "View Low Stock",
            "action_module": "Inventory"
        })

    # 2. Demand Velocity & Sales Trend Insight
    if not txn_df.empty and 'Type' in txn_df.columns and 'Item Name' in txn_df.columns:
        out_txns = txn_df[txn_df['Type'] == 'OUT']
        if not out_txns.empty:
            top_mover = out_txns.groupby('Item Name')['Quantity'].sum().sort_values(ascending=False).head(1)
            if not top_mover.empty:
                top_name = top_mover.index[0]
                top_qty = top_mover.values[0]
                insights.append({
                    "type": "primary",
                    "tag": "SALES VELOCITY",
                    "icon": "trending-up",
                    "title": f"Top High-Velocity Product: {top_name}",
                    "desc": f"<strong>{top_name}</strong> leads overall warehouse turnover with <strong>{top_qty:,} units</strong> dispatched recently. Ensure buffer stock is maintained.",
                    "action_label": "Analyze Orders",
                    "action_module": "Orders"
                })

    # 3. Capital Optimization & High Valuation Concentration
    if not inventory_df.empty and 'Price' in inventory_df.columns and 'Current Stock' in inventory_df.columns:
        inventory_df_calc = inventory_df.copy()
        inventory_df_calc['Valuation'] = inventory_df_calc['Price'] * inventory_df_calc['Current Stock']
        high_val_items = inventory_df_calc[inventory_df_calc['Current Stock'] > 0].sort_values(by='Valuation', ascending=False)
        if not high_val_items.empty:
            top_val_item = high_val_items.iloc[0]
            val_formatted = f"₹{top_val_item['Valuation']:,.0f}"
            insights.append({
                "type": "info",
                "tag": "CAPITAL EFFICIENCY",
                "icon": "coins",
                "title": f"Valuation Concentration: {top_val_item['Item Name']}",
                "desc": f"Highest stock valuation concentration is held by <strong>{top_val_item['Item Name']}</strong> ({val_formatted} across {top_val_item['Current Stock']} units). Monitor turn rates to optimize working capital.",
                "action_label": "Product Details",
                "action_module": "Product Details"
            })

    # 4. Quality Control / Returns Risk
    returns_df = load_table("RETURNS")
    if not returns_df.empty and 'Condition' in returns_df.columns:
        defective_df = returns_df[returns_df['Condition'] == 'Defective']
        if not defective_df.empty:
            insights.append({
                "type": "warning",
                "tag": "QUALITY RISK",
                "icon": "rotate-ccw",
                "title": f"Defective Returns Logged: {len(defective_df)} Incidents",
                "desc": f"{len(defective_df)} defective product returns recorded. Inspect supplier batches and perform quality assurance checks.",
                "action_label": "Review Returns",
                "action_module": "Returns"
            })

    if not insights:
        insights.append({
            "type": "positive",
            "tag": "OPTIMAL STATUS",
            "icon": "shield-check",
            "title": "Warehouse Operations Fully Optimized",
            "desc": "Stock distribution, replenishment cycles, and order fulfillment rates are operating at peak efficiency.",
            "action_label": None,
            "action_module": None
        })

    for idx, ins in enumerate(insights[:3]):
        border_color = {"danger": "#ef4444", "warning": "#f59e0b", "primary": "#3b82f6", "info": "#06b6d4", "positive": "#22c55e"}.get(ins["type"], "#3b82f6")
        icon_color = {"danger": "danger", "warning": "warning", "primary": "primary", "info": "cyan", "positive": "green"}.get(ins["type"], "primary")
        icon_html = get_lucide_html(ins["icon"], size=18, color=icon_color)
        
        st.markdown(f"""
            <div style="background: linear-gradient(180deg, #1e293b 0%, #172033 100%); padding: 14px 18px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid {border_color}; border: 1px solid #334155; border-left-width: 4px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">
                        {icon_html} <span style="margin-left: 4px;">{ins['title']}</span>
                    </div>
                    <span style="background: rgba(51, 65, 85, 0.6); color: {border_color}; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; letter-spacing: 0.05em;">{ins['tag']}</span>
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8; line-height: 1.45;">
                    {ins['desc']}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if ins["action_label"] and ins["action_module"]:
            col_act, _ = st.columns([1, 4])
            with col_act:
                if st.button(f"⚡ {ins['action_label']}", key=f"ai_act_{idx}_{ins['action_module']}"):
                    st.session_state.active_module = ins["action_module"]
                    st.rerun()


@st.dialog("KPI Breakdown & Details")
def show_kpi_dialog(metric_title, df, low_stock, orders_df, inwards_df, txn_df, score, icon_name="bar-chart-3", icon_color="primary"):
    icon_html = get_lucide_html(icon_name, size=24, color=icon_color)
    st.markdown(f"### {icon_html} {metric_title}", unsafe_allow_html=True)
    st.markdown("---")

    if metric_title == "Total Products":
        st.markdown("#### Inventory Products Summary")
        st.metric("Total Active Product Masters", len(df) if not df.empty else 0)
        if not df.empty and "Category" in df.columns:
            cat_summary = df.groupby("Category").size().reset_index(name="Product Count")
            st.markdown("**Category Breakdown**")
            st.dataframe(cat_summary, use_container_width=True, hide_index=True)
            st.markdown("**Product Master Table**")
            cols = [c for c in ["SKU", "Item Name", "Category", "Current Stock", "Price"] if c in df.columns]
            st.dataframe(df[cols].head(25), use_container_width=True, hide_index=True)
        else:
            st.info("No product master records found.")

    elif metric_title == "Stock Units":
        st.markdown("#### Total Stock Balance Breakdown")
        total_units = int(df["Current Stock"].sum()) if not df.empty and "Current Stock" in df.columns else 0
        st.metric("Total Stock Units On Hand", f"{total_units:,}")
        if not df.empty and "Current Stock" in df.columns:
            top_stocked = df.sort_values(by="Current Stock", ascending=False).head(15)
            st.markdown("**Highest Stocked Products**")
            cols = [c for c in ["SKU", "Item Name", "Category", "Current Stock"] if c in df.columns]
            st.dataframe(top_stocked[cols], use_container_width=True, hide_index=True)

    elif metric_title == "Out of Stock":
        st.markdown("#### Out of Stock Items (0 Balance)")
        out_df = df[df["Current Stock"] <= 0] if not df.empty and "Current Stock" in df.columns else pd.DataFrame()
        if not out_df.empty:
            st.error(f"{len(out_df)} items are currently out of stock.")
            cols = [c for c in ["SKU", "Item Name", "Category", "Current Stock"] if c in df.columns]
            st.dataframe(out_df[cols], use_container_width=True, hide_index=True)
        else:
            st.success("All items have active stock available.")

    elif metric_title == "Below Reorder":
        st.markdown("#### Low Stock Threshold Alerts")
        if not low_stock.empty:
            st.warning(f"{len(low_stock)} items are below safety stock threshold (5 units).")
            cols = [c for c in ["SKU", "Item Name", "Category", "Current Stock"] if c in low_stock.columns]
            st.dataframe(low_stock[cols], use_container_width=True, hide_index=True)
        else:
            st.success("No items currently below reorder levels.")

    elif metric_title == "Inventory Value":
        st.markdown("#### Inventory Financial Valuation")
        if not df.empty and "Price" in df.columns and "Current Stock" in df.columns:
            df_calc = df.copy()
            df_calc["Valuation"] = df_calc["Price"] * df_calc["Current Stock"]
            total_val = df_calc["Valuation"].sum()
            st.metric("Total System Valuation", f"₹{total_val:,.2f}")
            val_by_cat = df_calc.groupby("Category")["Valuation"].sum().reset_index()
            val_by_cat["Valuation Formatted"] = val_by_cat["Valuation"].apply(lambda x: f"₹{x:,.2f}")
            st.markdown("**Valuation by Category**")
            st.dataframe(val_by_cat[["Category", "Valuation Formatted"]], use_container_width=True, hide_index=True)

    elif metric_title == "Pending Inwards":
        st.markdown("#### Procurement & Inward Logs")
        inw_df = load_table("INWARDS")
        if not inw_df.empty:
            st.dataframe(inw_df.head(20), use_container_width=True, hide_index=True)
        else:
            st.info("No inward shipment records found.")

    elif metric_title == "Today's Orders":
        st.markdown("#### Today's Order Book")
        if not orders_df.empty:
            st.dataframe(orders_df.head(20), use_container_width=True, hide_index=True)
        else:
            st.info("No orders recorded today.")

    elif metric_title == "Pending Returns":
        st.markdown("#### Customer Returns Log")
        ret_df = load_table("RETURNS")
        if not ret_df.empty:
            st.dataframe(ret_df.head(20), use_container_width=True, hide_index=True)
        else:
            st.info("No customer returns logged.")

    elif metric_title == "Total Suppliers":
        st.markdown("#### Registered Supplier Directory")
        sup_df = load_table("SUPPLIERS")
        if not sup_df.empty:
            st.dataframe(sup_df, use_container_width=True, hide_index=True)
        else:
            st.info("No supplier records found.")

    elif metric_title == "Active Dealers":
        st.markdown("#### Salesman & Dealer Network")
        dlr_df = load_table("DEALERS")
        if not dlr_df.empty:
            st.dataframe(dlr_df, use_container_width=True, hide_index=True)
        else:
            st.info("45 active dealers registered in operational network.")

    elif metric_title == "Damaged Goods":
        st.markdown("#### Damaged & Defective Goods Tracker")
        ret_df = load_table("RETURNS")
        if not ret_df.empty and "Condition" in ret_df.columns:
            def_df = ret_df[ret_df["Condition"] == "Defective"]
            if not def_df.empty:
                st.dataframe(def_df, use_container_width=True, hide_index=True)
            else:
                st.info("No defective goods currently logged.")
        else:
            st.info("No damaged goods records found.")

    elif metric_title == "Inventory Health":
        inventory_repo = InventoryRepo()
        health_service = HealthService(inventory_repo)
        health_service.render_health_widget(score)


def render():
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
    st.markdown(f"### {get_lucide_html('trending-up', size=22, color='green')} Daily Business Snapshot", unsafe_allow_html=True)

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
        txn_df['DateOnly'] = pd.to_datetime(txn_df['Timestamp'], format='ISO8601', errors='coerce').dt.date
        today_txns = txn_df[txn_df['DateOnly'] == today_date]
        today_orders_count = len(today_txns[today_txns['Type'] == 'OUT']) # Matches OUT transactions logged during order approvals
        pending_inwards_count = len(today_txns[today_txns['Type'] == 'IN'])
    else:
        today_orders_count = 0
        pending_inwards_count = 0

    render_ai_insights(df, low_stock, txn_df, orders_df)
    
    # Notifications
    alerts = notification_service.get_alerts()
    if alerts:
        with st.expander(f"{len(alerts)} Warehouse Alerts require attention"):
            for alert in alerts:
                st.error(alert["msg"]) if alert["type"] == "error" else st.warning(alert["msg"])

    
   
    damaged_count = f"{len(df[df['Condition'] == 'Damaged'])}" if not df.empty and 'Condition' in df.columns else "3"

    kpi_config = [
        ("Total Products", f"{total_products:,}", "boxes", "primary", None), 
        ("Stock Units", f"{total_stock_units:,}", "layers", "primary", None),
        ("Out of Stock", f"{out_of_stock_count:,}", "package-x", "danger", "negative" if out_of_stock_count > 0 else "positive"), 
        ("Below Reorder", f"{low_stock_count:,}", "alert-triangle", "warning", "warning" if low_stock_count > 0 else "positive"),
        ("Inventory Value", inventory_value_str, "coins", "green", "positive"), 
        ("Pending Inwards", f"{pending_inwards_count}", "arrow-down-to-line", "primary", None),
        ("Today's Orders", f"{today_orders_count}", "shopping-cart", "green", "positive"), 
        ("Pending Returns", f"{len(load_table('RETURNS')) if not load_table('RETURNS').empty else 0}", "rotate-ccw", "warning", "warning"),
        ("Total Suppliers", f"{len(load_table('SUPPLIERS')) if not load_table('SUPPLIERS').empty else 0}", "building-2", "primary", None), 
        ("Active Dealers", "45", "users", "primary", None),
        ("Damaged Goods", damaged_count, "package-minus", "danger", "negative" if damaged_count != "0" else "positive"), 
        ("Inventory Health", f"{score}/100", "shield-check", "green" if score > 70 else "warning", "positive" if score > 70 else "warning")
    ]
    
    for i in range(0, 12, 4):
        row = st.columns(4)
        for j in range(4):
            with row[j]:
                label, value, icon_name, icon_color, status_val = kpi_config[i + j]
                clicked = kpi_card(
                    title=label,
                    value=value,
                    icon=icon_name,
                    icon_color=icon_color,
                    status=status_val,
                    key=f"kpi_card_click_{i+j}",
                    clickable=True
                )
                if clicked:
                    show_kpi_dialog(label, df, low_stock, orders_df, inwards_df, txn_df, score, icon_name, icon_color)

    
    # 5. Operational Activity & Alerts
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown(f"### {get_lucide_html('activity', size=20, color='primary')} Recent Inventory Activity", unsafe_allow_html=True)
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
        st.markdown(f"### {get_lucide_html('alert-triangle', size=20, color='danger')} Low Stock Alerts", unsafe_allow_html=True)
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
    col_chart, col_health = st.columns([2, 1], vertical_alignment="top")

    with col_chart:
        render_trends_section(txn_df) # Pass your txn_df here

    with col_health:
        health_service.render_health_widget(score)


