from database.crud import load_table
import streamlit as st
from utils.icons import lucide_icon
from database.crud import load_table, add_inventory_item

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
        header_col1, header_col2 = st.columns([0.1, 0.9], vertical_alignment="center")
    
        with header_col1:
            lucide_icon("shield-check", size=120) 
        with header_col2:
            st.markdown("### Inventory Health")

        st.progress(score / 100)

        c1, c2, c3 = st.columns(3)
        c1.metric("Healthy", "847")
        c2.metric("Warning", "23")
        c3.metric("Critical", "3")

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
