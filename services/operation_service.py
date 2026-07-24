import streamlit as st
import uuid
from datetime import datetime
from database.crud import insert_inward

def receive_stock(sku, item_name, quantity, user, reference):
    """Atomic operation to update stock and log transaction."""
    txn_id = str(uuid.uuid4())[:12].upper()
    
    with st.connection("sql").session as session:
        # 1. Update Inventory
        session.execute(
            'UPDATE "INVENTORY" SET "Current Stock" = "Current Stock" + :qty WHERE "SKU" = :sku',
            {"qty": quantity, "sku": sku}
        )
        
        # 2. Log in INVENTORY_TRANSACTIONS
        session.execute(
            '''INSERT INTO "INVENTORY_TRANSACTIONS" 
            ("Txn ID", "Timestamp", "Type", "Item Name", "Item Category", "SKU", "Quantity", "User", "Reference") 
            VALUES (:id, :ts, 'IN', :name, 'General', :sku, :qty, :user, :ref)''',
            {
                "id": txn_id, "ts": datetime.now(), "name": item_name, 
                "sku": sku, "qty": quantity, "user": user, "ref": reference
            }
        )
        session.commit()