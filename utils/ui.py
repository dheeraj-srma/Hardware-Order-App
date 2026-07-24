from textwrap import dedent
import streamlit as st


def kpi_card(
    title,
    value,
    icon="📊",
    subtitle="",
    status=None,
):

    status_class = ""

    if status == "positive":
        status_class = "kpi-positive"

    elif status == "negative":
        status_class = "kpi-negative"

    elif status == "warning":
        status_class = "kpi-warning"

    html = dedent(f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <div class="kpi-label">{title}</div>
            <div class="kpi-icon">{icon}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle {status_class}">{subtitle}</div>
    </div>
    """)

    st.markdown(html, unsafe_allow_html=True)