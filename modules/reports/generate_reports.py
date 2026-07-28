import streamlit as st
import pandas as pd
import io
import datetime
from database.crud import load_table
from utils.icons import get_lucide_html
from utils.ui import kpi_card


def render():
    # Header & Back Button
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Dashboard"):
            st.session_state.active_module = "Overview"
            st.rerun()

    st.markdown(f"### {get_lucide_html('file-text', size=24, color='primary')} Executive Report Generation & Export Center", unsafe_allow_html=True)
    st.markdown("<p class='page-subtitle'>Configure custom filters, preview live data, and export operational reports in CSV or Excel format.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # 1. Report Selector & Filter Controls
    col_rep_type, col_start, col_end = st.columns([2, 1, 1])

    with col_rep_type:
        report_type = st.selectbox(
            "Select Report Type",
            options=[
                "Inventory Valuation & Stock Status Report",
                "Sales & Customer Orders Report",
                "Procurement & Inward Stock Report",
                "Returns & Quality Audit Report",
                "Master Transaction Ledger Report",
                "Executive BI Operational Summary Report"
            ],
            key="rep_type_select"
        )

    # Default Date Range
    min_date = datetime.date(2023, 1, 1)
    max_date = datetime.date.today()

    with col_start:
        start_date = st.date_input("Start Date", value=datetime.date(2024, 1, 1), min_value=min_date, max_value=max_date, key="rep_start_date")
    with col_end:
        end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="rep_end_date")

    # 2. Data Loading & Report Data Preparation
    report_df = pd.DataFrame()
    report_filename = "Nalka_Metals_Report.csv"
    summary_metrics = {}

    if report_type == "Inventory Valuation & Stock Status Report":
        inv_df = load_table("INVENTORY")
        if not inv_df.empty:
            report_df = inv_df.copy()
            if "Price" in report_df.columns and "Current Stock" in report_df.columns:
                report_df["Total Valuation (₹)"] = report_df["Price"] * report_df["Current Stock"]
            report_filename = f"Inventory_Valuation_Report_{start_date}_to_{end_date}.csv"
            summary_metrics = {
                "Total Master SKUs": len(report_df),
                "Total Units On Hand": int(report_df["Current Stock"].sum()) if "Current Stock" in report_df.columns else 0,
                "Total Asset Valuation": f"₹{(report_df['Total Valuation (₹)'].sum() if 'Total Valuation (₹)' in report_df.columns else 0):,.0f}"
            }

    elif report_type == "Sales & Customer Orders Report":
        orders_df = load_table("ORDERS")
        if not orders_df.empty:
            df = orders_df.copy()
            if "Timestamp" in df.columns:
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], format='ISO8601', errors="coerce")
                df = df.dropna(subset=["Timestamp"])
                df["Date"] = df["Timestamp"].dt.date
                df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
            report_df = df
            report_filename = f"Sales_Orders_Report_{start_date}_to_{end_date}.csv"
            summary_metrics = {
                "Total Orders Logged": len(report_df),
                "Total Units Ordered": int(report_df["Quantity"].sum()) if "Quantity" in report_df.columns else 0,
                "Approved Orders": len(report_df[report_df["Status"] == "Approved"]) if "Status" in report_df.columns else 0
            }

    elif report_type == "Procurement & Inward Stock Report":
        inwards_df = load_table("INWARDS")
        if not inwards_df.empty:
            df = inwards_df.copy()
            if "Timestamp" in df.columns:
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], format='ISO8601', errors="coerce")
                df = df.dropna(subset=["Timestamp"])
                df["Date"] = df["Timestamp"].dt.date
                df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
            report_df = df
            report_filename = f"Inward_Procurement_Report_{start_date}_to_{end_date}.csv"
            summary_metrics = {
                "Inward Shipments Logged": len(report_df),
                "Total Units Refilled": int(report_df["Quantity"].sum()) if "Quantity" in report_df.columns else 0,
                "Unique Suppliers": len(report_df["Supplier"].unique()) if "Supplier" in report_df.columns else 0
            }

    elif report_type == "Returns & Quality Audit Report":
        returns_df = load_table("RETURNS")
        if not returns_df.empty:
            df = returns_df.copy()
            if "Timestamp" in df.columns:
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], format='ISO8601', errors="coerce")
                df = df.dropna(subset=["Timestamp"])
                df["Date"] = df["Timestamp"].dt.date
                df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
            report_df = df
            report_filename = f"Returns_Quality_Audit_Report_{start_date}_to_{end_date}.csv"
            summary_metrics = {
                "Total Return Incidents": len(report_df),
                "Defective Items": len(report_df[report_df["Condition"] == "Defective"]) if "Condition" in report_df.columns else 0,
                "Good Return Items": len(report_df[report_df["Condition"] == "Good"]) if "Condition" in report_df.columns else 0
            }

    elif report_type == "Master Transaction Ledger Report":
        txn_df = load_table("INVENTORY_TRANSACTIONS")
        if not txn_df.empty:
            df = txn_df.copy()
            if "Timestamp" in df.columns:
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], format='ISO8601', errors="coerce")
                df = df.dropna(subset=["Timestamp"])
                df["Date"] = df["Timestamp"].dt.date
                df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
            report_df = df
            report_filename = f"Master_Transaction_Ledger_{start_date}_to_{end_date}.csv"
            summary_metrics = {
                "Total Transactions": len(report_df),
                "Inward Stock Movements": len(report_df[report_df["Type"] == "IN"]) if "Type" in report_df.columns else 0,
                "Sales Order Dispatches": len(report_df[report_df["Type"] == "OUT"]) if "Type" in report_df.columns else 0
            }

    elif report_type == "Executive BI Operational Summary Report":
        inv_df = load_table("INVENTORY")
        orders_df = load_table("ORDERS")
        inwards_df = load_table("INWARDS")
        returns_df = load_table("RETURNS")
        
        summary_rows = [
            {"Metric Category": "Inventory Portfolio", "Metric Name": "Total Master SKUs", "Metric Value": len(inv_df)},
            {"Metric Category": "Inventory Portfolio", "Metric Name": "Total Units On Hand", "Metric Value": int(inv_df["Current Stock"].sum()) if not inv_df.empty and "Current Stock" in inv_df.columns else 0},
            {"Metric Category": "Inventory Portfolio", "Metric Name": "Total Asset Valuation (₹)", "Metric Value": f"₹{(inv_df['Price'] * inv_df['Current Stock']).sum():,.0f}" if not inv_df.empty and "Price" in inv_df.columns and "Current Stock" in inv_df.columns else "₹0"},
            {"Metric Category": "Sales Operations", "Metric Name": "Total Customer Orders", "Metric Value": len(orders_df)},
            {"Metric Category": "Sales Operations", "Metric Name": "Approved Orders Count", "Metric Value": len(orders_df[orders_df["Status"] == "Approved"]) if not orders_df.empty and "Status" in orders_df.columns else 0},
            {"Metric Category": "Procurement", "Metric Name": "Inward Shipments Logged", "Metric Value": len(inwards_df)},
            {"Metric Category": "Procurement", "Metric Name": "Total Inward Units Refilled", "Metric Value": int(inwards_df["Quantity"].sum()) if not inwards_df.empty and "Quantity" in inwards_df.columns else 0},
            {"Metric Category": "Quality Control", "Metric Name": "Total Return Incidents", "Metric Value": len(returns_df)},
            {"Metric Category": "Quality Control", "Metric Name": "Defective Items Logged", "Metric Value": len(returns_df[returns_df["Condition"] == "Defective"]) if not returns_df.empty and "Condition" in returns_df.columns else 0}
        ]
        report_df = pd.DataFrame(summary_rows)
        report_filename = f"Executive_BI_Operational_Summary_{datetime.date.today()}.csv"
        summary_metrics = {
            "Summary Metrics Exported": len(report_df),
            "Report Date": str(datetime.date.today()),
            "Status": "Verified Executive Audit"
        }

    # 3. Render Summary Metrics KPI Cards
    if summary_metrics:
        c1, c2, c3 = st.columns(3)
        cols_list = [c1, c2, c3]
        for i, (k, v) in enumerate(summary_metrics.items()):
            with cols_list[i % 3]:
                kpi_card(title=k, value=str(v), icon="file-spreadsheet", subtitle="Report Metric", status="positive", icon_color="primary", clickable=False)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Export Buttons & Interactive Preview Table
    if not report_df.empty:
        col_down1, _ = st.columns([2, 2])
        
        csv_buffer = report_df.to_csv(index=False).encode('utf-8')
        
        with col_down1:
            st.download_button(
                label="📥 Download Report (CSV)",
                data=csv_buffer,
                file_name=report_filename,
                mime="text/csv",
                type="primary",
                use_container_width=True
            )
        
        st.markdown(f"#### {get_lucide_html('table', size=20, color='cyan')} Interactive Report Preview ({len(report_df):,} Records)", unsafe_allow_html=True)
        st.dataframe(report_df, use_container_width=True, hide_index=True, height=450)
    else:
        st.info("No records found for the selected report filters.")
