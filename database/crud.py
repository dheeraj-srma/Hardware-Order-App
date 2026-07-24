"""
database/crud.py
All database operations for the Nalka Metals Portal.
The UI layer (modules/*) must only call functions defined here — no module
should open its own database connection. Everything goes through the
Supabase REST client so there is a single, consistent write path.
"""

import uuid
import logging
from datetime import datetime

import pandas as pd
import streamlit as st

from database.client import supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


_ROLE_TO_ENUM = {
    "Admin":     "admin",
    "Manager":   "warehouse_mgr",
    "Salesman":  "ops_team",
    "Customer":  "ops_team",
}

# ---------------------------------------------------------------------------
# COLUMN NORMALIZATION
# ---------------------------------------------------------------------------
# Supabase/Postgres column names can drift in casing (snake_case vs Title
# Case). Every load_table() call runs through this so the rest of the app
# can rely on one consistent naming scheme regardless of the raw schema.

_RENAME_MAP = {
    "timestamp": "Timestamp", "created_at": "Timestamp", "order_date": "Timestamp", "date": "Timestamp",
    "quantity": "Quantity", "qty": "Quantity",
    "item_name": "Item Name", "itemname": "Item Name", "product_name": "Item Name", "product": "Item Name",
    "sku": "SKU",
    "category": "Category", "item_category": "Category",
    "salesman_name": "Salesman Name", "dealer_name": "Salesman Name",
    "shop_name": "Shop Name", "store_name": "Shop Name",
    "supplier_name": "Supplier", "supplier": "Supplier",
    "order_id": "Order ID", "orderid": "Order ID",
    "current_stock": "Current Stock", "stock": "Current Stock", "balance": "Current Stock",
    "city": "City", "state": "State",
    "condition": "Condition", "reason": "Reason", "status": "Status",
    "salesman_type": "Salesman Type", "dealer_type": "Salesman Type",
    "salesman_id": "Salesman ID", "dealer_id": "Salesman ID",
    "specialization": "Specialization",
    "type": "Type", "transaction_type": "Type",
    "user": "User", "reference": "Reference", "ref": "Reference",
    "txn_id": "Txn ID", "location_id": "Location ID", "price": "Price",
    "supplier_id": "Supplier ID",
}


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise column names coming from Supabase (any casing / snake_case)."""
    if df.empty:
        return df
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    df = df.rename(columns={k: v for k, v in _RENAME_MAP.items() if k in df.columns})
    return df


# ---------------------------------------------------------------------------
# GENERIC LOADER
# ---------------------------------------------------------------------------

def load_table(table_name: str) -> pd.DataFrame:
    try:
        response = supabase.table(table_name).select("*").execute()
        data = response.data
        if data:
            return clean_columns(pd.DataFrame(data))
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to load table '{table_name}': {e}")
        logger.exception("load_table(%s) failed", table_name)
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# ORDERS
# ---------------------------------------------------------------------------

def insert_order(order_rows: list[dict], user_role: str = "Manager") -> bool:
    """Insert a new order (one row per line-item) with Status='Pending'."""
    txn_user = _ROLE_TO_ENUM.get(user_role, "ops_team")
    try:
        formatted_rows = []
        for r in order_rows:
            qty_val = r.get("Qty") or r.get("Quantity") or 0
            location_id = r.get("Location ID") or _get_location_id(r.get("City", ""))
            formatted_rows.append({
                "Order ID":      r["Order ID"],
                "Timestamp":     r["Timestamp"],
                "Salesman ID":   r.get("Salesman ID") or None,
                "Salesman Name": r.get("Salesman Name", ""),
                "Shop Name":     r.get("Shop Name", ""),
                "City":          r.get("City", ""),
                "State":         r.get("State", ""),
                "Item Name":     r.get("Item Name", ""),
                "Category":      r.get("Category", ""),
                "SKU":           r.get("SKU", ""),
                "Quantity":      int(qty_val),
                "Location ID":   location_id,
                "Status":        "Pending",
                "User":          txn_user,
            })

        supabase.table("ORDERS").insert(formatted_rows).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to place order: {e}")
        logger.exception("insert_order failed")
        return False


def get_orders() -> pd.DataFrame:
    return load_table("ORDERS")


def approve_order(order_id: str) -> bool:
    """
    Approve every line-item that shares an Order ID: mark it Approved,
    deduct the exact quantity ordered for its own SKU (not a subquery that
    only matches the first row), and log an audit transaction per item.
    """
    try:
        orders_df = load_table("ORDERS")
        if orders_df.empty or "Order ID" not in orders_df.columns:
            st.error("No orders found.")
            return False

        line_items = orders_df[orders_df["Order ID"] == order_id]
        if line_items.empty:
            st.error(f"Order {order_id} not found.")
            return False

        for _, row in line_items.iterrows():
            sku = row.get("SKU", "")
            qty = int(row.get("Quantity", 0) or 0)
            if sku and qty:
                _deduct_inventory(sku, qty)
                insert_inventory_transaction({
                    "Txn ID":        f"ORD-{uuid.uuid4().hex[:8]}",
                    "Timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Type":          "OUT",
                    "SKU":           sku,
                    "Item Name":     row.get("Item Name", ""),
                    "Item Category": row.get("Category", ""),
                    "Quantity":      qty,
                    "User":          row.get("Salesman Name", ""),
                    "Reference":     order_id,
                })

        supabase.table("ORDERS").update({"Status": "Approved"}).eq("Order ID", order_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to approve order {order_id}: {e}")
        logger.exception("approve_order failed")
        return False


def delete_order(order_id: str) -> bool:
    try:
        supabase.table("ORDERS").delete().eq("Order ID", order_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to delete order: {e}")
        return False


def update_order(order_id: str, fields: dict) -> bool:
    try:
        supabase.table("ORDERS").update(fields).eq("Order ID", order_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to update order: {e}")
        return False


# ---------------------------------------------------------------------------
# INWARDS (REFILLS)
# ---------------------------------------------------------------------------

def insert_inward(sku: str, item_name: str, category: str, supplier: str, qty: int, reference: str = "") -> bool:
    """Record an inward shipment: log it, add stock, and write an audit transaction."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        supabase.table("INWARDS").insert({
            "Timestamp": timestamp,
            "Supplier":  supplier,
            "Category":  category,
            "Item Name": item_name,
            "SKU":       sku,
            "Quantity":  int(qty),
            "Reference": reference,
        }).execute()

        _add_inventory(sku, int(qty))
        insert_inventory_transaction({
            "Txn ID":        f"INW-{uuid.uuid4().hex[:8]}",
            "Timestamp":     timestamp,
            "Type":          "IN",
            "SKU":           sku,
            "Item Name":     item_name,
            "Item Category": category,
            "Quantity":      int(qty),
            "User":          supplier,
            "Reference":     reference,
        })

        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to commit inward: {e}")
        logger.exception("insert_inward failed")
        return False


# ---------------------------------------------------------------------------
# RETURNS
# ---------------------------------------------------------------------------

def insert_return(return_row: dict) -> bool:
    try:
        # Generate unique Return ID and extract fields matching your table schema
        payload = {
            "Return ID":     f"RET-{uuid.uuid4().hex[:8]}",
            "Timestamp":     return_row.get("Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "Salesman Name": return_row.get("Salesman Name", "Manager"),
            "Shop Name":     return_row.get("Shop Name", ""),
            "Item Name":     return_row.get("Item Name", ""),
            "Category":      return_row.get("Category", ""),
            "SKU":           return_row.get("SKU", ""),
            "Quantity":      int(return_row.get("Quantity", 0)),
            "Condition":     return_row.get("Condition", "Good"),
            "Reason":        return_row.get("Reason", "Damaged"),
            "Status":        return_row.get("Status", "Restocked"),
        }
        
        supabase.table("RETURNS").insert(payload).execute()

        condition = str(payload.get("Condition", ""))
        is_good = "Good" in condition or return_row.get("Action") == "Return to Stock"
        qty = int(payload.get("Quantity", 0))

        if is_good and qty:
            _add_inventory(payload["SKU"], qty)

        insert_inventory_transaction({
            "Txn ID":        f"TRX-{uuid.uuid4().hex[:8]}",
            "Timestamp":     payload["Timestamp"],
            "Type":          "RETURN_GOOD" if is_good else "RETURN_DEFECTIVE",
            "SKU":           payload["SKU"],
            "Item Name":     payload["Item Name"],
            "Item Category": payload["Category"],
            "Quantity":      qty,
            "User":          payload["Salesman Name"],
            "Reference":     f"Shop: {payload['Shop Name']} | Reason: {payload['Reason']}",
        })

        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to log return: {e}")
        logger.exception("insert_return failed")
        return False

# ---------------------------------------------------------------------------
# SUPPLIERS
# ---------------------------------------------------------------------------

def add_supplier(name: str, city: str, state: str = "", specialization: str = "") -> bool:
    try:
        new_id = f"SUP-{uuid.uuid4().hex[:6].upper()}"
        supabase.table("SUPPLIERS").insert({
            "Supplier ID":    new_id,
            "Supplier":       name,
            "City":           city,
            "State":          state,
            "Specialization": specialization,
        }).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to add supplier: {e}")
        logger.exception("add_supplier failed")
        return False


# ---------------------------------------------------------------------------
# INVENTORY
# ---------------------------------------------------------------------------

def get_inventory() -> pd.DataFrame:
    return load_table("INVENTORY")


def update_inventory_stock(sku: str, new_stock: int) -> bool:
    try:
        supabase.table("INVENTORY").update({"Current Stock": int(new_stock)}).eq("SKU", sku).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to update inventory for SKU '{sku}': {e}")
        return False


from datetime import datetime
import streamlit as st

def adjust_stock(sku, item_name, category, new_qty, old_qty, reason):
    try:
        # 1. Update the master INVENTORY table
        supabase.table("INVENTORY").update({"Current Stock": new_qty}).eq("SKU", sku).execute()

        # 2. Fetch the latest Txn ID to generate the next sequential ID (e.g., "TXN-0000001")
        response = supabase.table("INVENTORY_TRANSACTIONS").select('"Txn ID"').order('"Txn ID"', desc=True).limit(1).execute()
        
        next_id_str = "TXN-0000001"
        if response.data and len(response.data) > 0:
            last_id = response.data[0].get("Txn ID", "")
            if last_id.startswith("TXN-"):
                try:
                    num_part = int(last_id.split("-")[1])
                    next_id_str = f"TXN-{num_part + 1:07d}"
                except ValueError:
                    pass

        # 3. Record the adjustment adhering to schema limits (Reference max 12 chars)
        diff = new_qty - old_qty
        txn_row = {
            "Txn ID":        next_id_str,
            "Timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Type":          "ADJUSTMENT", # Make sure this matches your txn_type_enum values
            "Item Name":     item_name,
            "Item Category": category,
            "SKU":           sku,
            "Quantity":      new_qty,
            "User":          st.session_state.get("user_name", "Manager"), # Must match txn_user_enum
            "Reference":     f"{new_qty} units 'ADJUSTED'", # Kept strictly under 12 characters to satisfy character varying(12)
        }
        
        supabase.table("INVENTORY_TRANSACTIONS").insert(txn_row).execute()
        
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to log stock adjustment: {e}")
        return False


def add_inventory_item(name: str, sku: str, category: str, price: float) -> bool:
    try:
        supabase.table("INVENTORY").insert({
            "Item Name":     name,
            "SKU":           sku,
            "Category":      category,
            "Price":         float(price),
            "Current Stock": 0,
        }).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Failed to add product: {e}")
        logger.exception("add_inventory_item failed")
        return False


# ---------------------------------------------------------------------------
# INVENTORY TRANSACTIONS
# ---------------------------------------------------------------------------

def insert_inventory_transaction(row: dict) -> bool:
    try:
        supabase.table("INVENTORY_TRANSACTIONS").insert(row).execute()
        return True
    except Exception as e:
        st.error(f"Failed to log inventory transaction: {e}")
        logger.exception("insert_inventory_transaction failed")
        return False


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------

def _get_current_stock(sku: str) -> int:
    try:
        # Must use select("*") — PostgREST strips spaces from "Current Stock"
        # and would otherwise query a non-existent "CurrentStock" column.
        res = supabase.table("INVENTORY").select("*").eq("SKU", sku).execute()
        if res.data:
            return int(res.data[0].get("Current Stock", 0) or 0)
        return 0
    except Exception:
        logger.exception("_get_current_stock failed for sku=%s", sku)
        return 0


def _deduct_inventory(sku: str, qty: int) -> None:
    current = _get_current_stock(sku)
    new_stock = max(current - int(qty), 0)
    update_inventory_stock(sku, new_stock)


def _add_inventory(sku: str, qty: int) -> None:
    current = _get_current_stock(sku)
    new_stock = current + int(qty)
    update_inventory_stock(sku, new_stock)


def _get_location_id(city: str):
    if not city:
        return None
    try:
        res = supabase.table("LOCATIONS").select("*").eq("City", city).execute()
        if res.data:
            return res.data[0].get("Location ID")
        return None
    except Exception:
        return None
