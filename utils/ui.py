from textwrap import dedent
import streamlit as st
from utils.icons import get_lucide_html


def kpi_card(
    title,
    value,
    icon="bar-chart-3",
    subtitle="",
    status=None,
    icon_color="currentColor",
    key=None,
    clickable=True,
) -> bool:

    status_class = ""
    if status == "positive":
        status_class = "kpi-positive"
    elif status == "negative":
        status_class = "kpi-negative"
    elif status == "warning":
        status_class = "kpi-warning"

    # If icon is a raw icon name (without HTML tags), convert it to Lucide HTML
    if isinstance(icon, str) and not ("<img" in icon or "<svg" in icon or "<div" in icon):
        icon_html = get_lucide_html(icon, size=24, color=icon_color, margin_right=0)
    else:
        icon_html = icon

    sub_html = f'<div class="kpi-subtitle {status_class}">{subtitle}</div>' if subtitle else ""

    card_body = dedent(f"""
    <div class="kpi-card-content">
        <div class="kpi-header">
            <div class="kpi-label">{title}</div>
            <div class="kpi-icon">{icon_html}</div>
        </div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>
    """)

    clicked = False
    with st.container(border=True):
        st.markdown(card_body, unsafe_allow_html=True)
        if clickable:
            clean_title = title.lower().replace(' ', '_').replace("'", "")
            btn_key = key or f"kpi_btn_{clean_title}"
            clicked = st.button("Click for details →", key=btn_key, use_container_width=True)
            
    return clicked


