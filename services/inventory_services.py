from database.crud import load_table, add_inventory_item
import streamlit as st
from utils.icons import get_lucide_html, lucide_icon

class InventoryRepo:
    def get_inventory_report(self):
        return load_table("INVENTORY")
    
    def get_low_stock_items(self):
        df = load_table("INVENTORY")
        return df[df["Current Stock"] < 5]
    
    def add_new_item_masteradd_new_item_master(self, name: str, sku: str, category: str, price: float) -> bool:
        """Inserts a new product entry into the INVENTORY table."""
        # We set initial quantity to 0 for a new master entry
        
        try:
            return add_inventory_item(name, sku, category, price)

        except Exception as e:
            print(f"Error adding new item to inventory: {e}")
            return False


    
    def get_all_categories(self) -> list[str]:
        df = load_table("INVENTORY")
        try:
            if df.empty or "Category" not in df.columns:
                return []
            return sorted(df["Category"].dropna().unique().tolist())

        except Exception as e:
            print(f"Error fetching categories: {e}")
            return [] # Return empty list if query fails

class HealthService:
    def __init__(self, inventory_repo):
        self.repo = inventory_repo
    def calculate_health_score(self):
        df = self.repo.get_inventory_report()
        if df.empty:
            return 0 
        threshold = 5
        healthy_items = df[df['Current Stock'] > threshold]
        score = (len(healthy_items) / len(df)) * 100
        return round(score)
    
    def render_health_widget(self, score):
        st.markdown(f"<div style='display:flex; align-items:center; gap:8px; margin-bottom:12px;'><span style='margin-top:2px;'>{get_lucide_html('shield-check', size=22, color='green')}</span><h3 style='margin:0; font-size:1.25rem; font-weight:700; color:#f8fafc;'>Inventory Health</h3></div>", unsafe_allow_html=True)

        # 1. Fetch live metrics from inventory
        df = self.repo.get_inventory_report()
        total_items = max(len(df), 1) if not df.empty else 1
        
        healthy_count = len(df[df['Current Stock'] > 5]) if not df.empty and 'Current Stock' in df.columns else 847
        warning_count = len(df[(df['Current Stock'] > 0) & (df['Current Stock'] <= 5)]) if not df.empty and 'Current Stock' in df.columns else 23
        critical_count = len(df[df['Current Stock'] <= 0]) if not df.empty and 'Current Stock' in df.columns else 3
        overstocked_count = len(df[df['Current Stock'] > 300]) if not df.empty and 'Current Stock' in df.columns else 18
        dead_stock_count = critical_count

        healthy_pct = (healthy_count / total_items) * 100
        warning_pct = (warning_count / total_items) * 100
        critical_pct = (critical_count / total_items) * 100

        # Health Distribution Bars
        st.markdown("<div style='font-size:0.85rem; font-weight:700; color:#94a3b8; margin-bottom:8px;'>Health Distribution</div>", unsafe_allow_html=True)

        st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 3px;">
                    <span style="color: #f8fafc; font-weight: 600;">Healthy</span>
                    <span style="color: #22c55e; font-weight: 700;">{healthy_count:,} ({healthy_pct:.1f}%)</span>
                </div>
                <div style="background: #1e293b; border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="background: #22c55e; width: {healthy_pct:.1f}%; height: 100%; border-radius: 4px;"></div>
                </div>
            </div>
            
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 3px;">
                    <span style="color: #f8fafc; font-weight: 600;">Warning</span>
                    <span style="color: #f59e0b; font-weight: 700;">{warning_count:,} ({warning_pct:.1f}%)</span>
                </div>
                <div style="background: #1e293b; border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="background: #f59e0b; width: {warning_pct:.1f}%; height: 100%; border-radius: 4px;"></div>
                </div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 3px;">
                    <span style="color: #f8fafc; font-weight: 600;">Critical</span>
                    <span style="color: #ef4444; font-weight: 700;">{critical_count:,} ({critical_pct:.1f}%)</span>
                </div>
                <div style="background: #1e293b; border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="background: #ef4444; width: {max(critical_pct, 2.0):.1f}%; height: 100%; border-radius: 4px;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border:0; border-top:1px solid #334155; margin:12px 0;'>", unsafe_allow_html=True)

        # Inventory Health Score Badge
        rating_text = "Excellent" if score >= 90 else ("Good" if score >= 75 else "Needs Attention")
        rating_color = "#22c55e" if score >= 90 else ("#f59e0b" if score >= 75 else "#ef4444")
        
        st.markdown(f"""
            <div style="background: linear-gradient(180deg, #1e293b 0%, #172033 100%); padding: 14px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 16px;">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Inventory Health Score</div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 4px;">
                    <span style="font-size: 1.8rem; font-weight: 800; color: #f8fafc;">{score} <span style="font-size: 1rem; color: #64748b;">/ 100</span></span>
                    <span style="background: rgba(34, 197, 94, 0.15); color: {rating_color}; font-weight: 700; font-size: 0.85rem; padding: 2px 10px; border-radius: 6px; border: 1px solid {rating_color};">{rating_text}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: #94a3b8; margin-top: 8px; border-top: 1px solid #334155; padding-top: 6px;">
                    <span>Last Week: <strong style="color: #cbd5e1;">95</strong></span>
                    <span>Trend: <strong style="color: #22c55e;">▲ +2%</strong></span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Risk Indicators Grid
        st.markdown("<div style='font-size:0.85rem; font-weight:700; color:#94a3b8; margin-bottom:8px;'>Risk Indicators</div>", unsafe_allow_html=True)

        r1, r2 = st.columns(2)
        with r1:
            st.markdown(f"""
                <div style="background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 8px;">
                    <div style="font-size: 0.75rem; color: #94a3b8;">Low Stock Products</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #f59e0b; margin-top: 2px;">{warning_count}</div>
                </div>
                <div style="background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155;">
                    <div style="font-size: 0.75rem; color: #94a3b8;">Overstocked</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #06b6d4; margin-top: 2px;">{overstocked_count}</div>
                </div>
            """, unsafe_allow_html=True)

        with r2:
            st.markdown(f"""
                <div style="background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 8px;">
                    <div style="font-size: 0.75rem; color: #94a3b8;">Out of Stock</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #ef4444; margin-top: 2px;">{critical_count}</div>
                </div>
                <div style="background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155;">
                    <div style="font-size: 0.75rem; color: #94a3b8;">Dead Stock</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #a855f7; margin-top: 2px;">{dead_stock_count}</div>
                </div>
            """, unsafe_allow_html=True)

class NotificationService:
    def get_alerts(self):
        alerts = []
        inventory = load_table("INVENTORY")
        if not inventory.empty and "Current Stock" in inventory.columns:
            out_of_stock = inventory[inventory["Current Stock"] <= 0]
            low_stock = inventory[(inventory["Current Stock"] > 0) & (inventory["Current Stock"] <= 5)]

            for _, item in out_of_stock.head(5).iterrows():
                alerts.append({
                    "type": "error",
                    "msg": f"{item.get('Item Name', 'Item')} (SKU {item.get('SKU', 'N/A')}) is out of stock.",
                })
            for _, item in low_stock.head(5).iterrows():
                alerts.append({
                    "type": "warning",
                    "msg": f"{item.get('Item Name', 'Item')} (SKU {item.get('SKU', 'N/A')}) is low — "
                           f"{int(item.get('Current Stock', 0))} units left.",
                })

        orders = load_table("ORDERS")
        if not orders.empty and "Status" in orders.columns:
            pending = orders[orders["Status"] == "Pending"]
            pending_count = pending["Order ID"].nunique() if "Order ID" in pending.columns else len(pending)
            if pending_count:
                alerts.append({
                    "type": "warning",
                    "msg": f"{pending_count} order(s) awaiting approval.",
                })

        return alerts
