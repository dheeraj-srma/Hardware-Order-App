import streamlit as st
import plotly.express as px
import pandas as pd
from utils.icons import get_lucide_html


import datetime
from database.crud import load_table


def render_trends_section(txn_df):
    st.markdown(f"<div style='display:flex; align-items:center; gap:8px; margin-bottom:12px;'><span style='margin-top:2px;'>{get_lucide_html('trending-up', size=22, color='warning')}</span><h3 style='margin:0; font-size:1.25rem; font-weight:700; color:#f8fafc;'>Operational Trends</h3></div>", unsafe_allow_html=True)
    
    # 1. Consolidate operational transaction records across all modules (2024 - 2026)
    records = []
    
    if not txn_df.empty and "Timestamp" in txn_df.columns:
        for _, r in txn_df.iterrows():
            records.append({
                "Timestamp": r.get("Timestamp"),
                "Type": r.get("Type", "OUT")
            })

    orders_df = load_table("ORDERS")
    if not orders_df.empty and "Timestamp" in orders_df.columns:
        for _, r in orders_df.iterrows():
            records.append({
                "Timestamp": r.get("Timestamp"),
                "Type": "OUT"
            })

    inwards_df = load_table("INWARDS")
    if not inwards_df.empty and "Timestamp" in inwards_df.columns:
        for _, r in inwards_df.iterrows():
            records.append({
                "Timestamp": r.get("Timestamp"),
                "Type": "IN"
            })

    returns_df = load_table("RETURNS")
    if not returns_df.empty and "Timestamp" in returns_df.columns:
        for _, r in returns_df.iterrows():
            cond = str(r.get("Condition", "")).upper()
            records.append({
                "Timestamp": r.get("Timestamp"),
                "Type": "RETURN_DEFECTIVE" if cond == "DEFECTIVE" else "RETURN_GOOD"
            })

    if not records:
        st.info("No transaction data available for trend analysis.")
        return

    combined_df = pd.DataFrame(records)
    combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'], format='ISO8601', errors="coerce")
    combined_df = combined_df.dropna(subset=['Timestamp'])
    
    if combined_df.empty:
        st.info("No valid timestamps found in transaction history.")
        return

    # Allow year navigation across full 2024 to 2026+ range
    abs_min_date = datetime.date(2024, 1, 1)
    abs_max_date = datetime.date(2026, 12, 31)
    
    data_min_date = combined_df['Timestamp'].min().date()
    data_max_date = combined_df['Timestamp'].max().date()

    min_date = min(abs_min_date, data_min_date)
    max_date = max(abs_max_date, data_max_date)
    
    # Default range: Last 30 days of available data
    default_end = data_max_date
    default_start = max(min_date, default_end - pd.Timedelta(days=30))

    # 2. Date Range Filter Controls
    col_start, col_end, _ = st.columns([1, 1, 2])
    with col_start:
        start_date = st.date_input(
            "Start Date",
            value=default_start,
            min_value=min_date,
            max_value=max_date,
            key="trend_start_date"
        )
    with col_end:
        end_date = st.date_input(
            "End Date",
            value=default_end,
            min_value=min_date,
            max_value=max_date,
            key="trend_end_date"
        )

    if start_date > end_date:
        st.warning("Start Date must be before or equal to End Date.")
        return

    # 3. Filter Data by Selected Date Range
    combined_df['DateOnly'] = combined_df['Timestamp'].dt.date
    filtered_df = combined_df[(combined_df['DateOnly'] >= start_date) & (combined_df['DateOnly'] <= end_date)].copy()
    
    if filtered_df.empty:
        st.info(f"No operational transactions recorded between {start_date} and {end_date}.")
        return

    # 3. Standardize and Humanize Transaction Types
    TYPE_MAP = {
        "IN": "Inward Stock",
        "OUT": "Sales Orders",
        "RETURN_GOOD": "Good Returns",
        "RETURN_DEFECTIVE": "Defective Returns",
        "REPLACEMENT_IN": "Replacements",
        "ADJUSTMENT": "Stock Adjustments"
    }
    
    filtered_df['Activity'] = filtered_df['Type'].astype(str).str.strip().str.upper().map(
        lambda t: TYPE_MAP.get(t, t.title())
    )
    
    # 4. Group by Date & Activity
    filtered_df['Date'] = filtered_df['Timestamp'].dt.date
    trend_data = filtered_df.groupby(['Date', 'Activity']).size().reset_index(name='Volume')
    
    COLOR_MAP = {
        "Inward Stock": "#3b82f6",
        "Sales Orders": "#22c55e",
        "Good Returns": "#f59e0b",
        "Defective Returns": "#ef4444",
        "Replacements": "#8b5cf6",
        "Stock Adjustments": "#06b6d4"
    }

    # 5. Build Smooth Interactive Plotly Figure
    fig = px.line(
        trend_data, 
        x='Date', 
        y='Volume', 
        color='Activity',
        color_discrete_map=COLOR_MAP,
        template="plotly_dark",
        markers=True
    )
    
    fig.update_traces(
        line=dict(width=3, shape='linear'),
        marker=dict(size=6, symbol="circle")
    )
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(15, 23, 42, 0.5)",
        margin=dict(l=10, r=10, t=30, b=10),
        height=310,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=None,
            font=dict(size=12, color="#94a3b8")
        ),
        xaxis=dict(
            title=None,
            showgrid=True,
            gridcolor="#334155",
            tickfont=dict(color="#94a3b8")
        ),
        yaxis=dict(
            title=dict(text="Transaction Volume", font=dict(color="#94a3b8", size=12)),
            showgrid=True,
            gridcolor="#334155",
            tickfont=dict(color="#94a3b8")
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 6. Trend Operational Metrics Strip below the chart
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)

    inward_count = len(filtered_df[filtered_df['Activity'] == 'Inward Stock'])
    sales_count = len(filtered_df[filtered_df['Activity'] == 'Sales Orders'])
    returns_count = len(filtered_df[filtered_df['Activity'].isin(['Good Returns', 'Defective Returns'])])
    total_volume = len(filtered_df)

    with m1:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; border: 1px solid #334155;">
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">Inward Shipments</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #3b82f6; margin-top: 2px;">{inward_count:,}</div>
                <div style="font-size: 0.7rem; color: #64748b;">Selected Period</div>
            </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; border: 1px solid #334155;">
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">Sales Orders</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #22c55e; margin-top: 2px;">{sales_count:,}</div>
                <div style="font-size: 0.7rem; color: #64748b;">Outbound Orders</div>
            </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; border: 1px solid #334155;">
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">Return Incidents</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #f59e0b; margin-top: 2px;">{returns_count:,}</div>
                <div style="font-size: 0.7rem; color: #64748b;">Quality Logs</div>
            </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; border: 1px solid #334155;">
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">Total Movements</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #06b6d4; margin-top: 2px;">{total_volume:,}</div>
                <div style="font-size: 0.7rem; color: #64748b;">Total Volume</div>
            </div>
        """, unsafe_allow_html=True)