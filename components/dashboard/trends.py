import streamlit as st
import plotly.express as px
import pandas as pd

def render_trends_section(txn_df):
    st.subheader("📊 Operational Trends")
    
    # 1. Date Range Filter
    timeframe = st.radio("Trend Range", ["7 Days", "30 Days", "90 Days"], horizontal=True, key="trend_range")
    
    # 2. Prepare Data (Convert Timestamp column to datetime objects)
    txn_df['Timestamp'] = pd.to_datetime(txn_df['Timestamp'])
    
    # 3. Aggregate data by Date and Type
    trend_data = txn_df.groupby([txn_df['Timestamp'].dt.date, 'Type']).size().reset_index(name='Count')
    trend_data.columns = ['Date', 'Type', 'Count']
    
    # 4. Generate Interactive Chart
    fig = px.line(
        trend_data, 
        x='Date', 
        y='Count', 
        color='Type',
        template="plotly_dark",
        markers=True
    )
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)