import streamlit as st
import datetime

def render_executive_summary():
    """Renders the top-level Executive Briefing banner."""
    # Logic: Get count of orders/shipments today
    today = datetime.date.today()
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%); padding: 1.5rem; border-radius: 12px; border-left: 5px solid #3b82f6; margin-bottom: 2rem;">
        <h3 style="margin: 0; color: #f8fafc;">Good Morning, Warehouse Manager</h3>
        <p style="margin: 5px 0 0 0; color: #94a3b8;">
            Operations are steady. <b>12 new orders</b> arrived today. <b>3 pending approvals</b> require your attention.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_smart_kpi_row(data_today, data_yesterday):
    """Renders the row of KPI cards with trend analysis."""
    c1, c2, c3, c4 = st.columns(4)
    
    # Calculate deltas for display
    def get_delta(curr, prev):
        diff = curr - prev
        pct = (diff / prev * 100) if prev > 0 else 0
        return f"{diff:+d} ({pct:+.1f}%)"

    with c1:
        st.metric("Today's Orders", data_today['orders'], get_delta(data_today['orders'], data_yesterday['orders']))
    with c2:
        st.metric("Inward Shipments", data_today['inwards'], get_delta(data_today['inwards'], data_yesterday['inwards']))
    with c3:
        st.metric("Inventory Value", f"₹{data_today['value']/100000:.1f}L", f"₹{(data_today['value']-data_yesterday['value'])/1000:.1f}K")
    with c4:
        st.metric("Health Score", "97%", "0.5% ▲")