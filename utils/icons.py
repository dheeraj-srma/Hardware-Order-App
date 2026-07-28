import streamlit as st

def get_lucide_html(icon_name: str, size: int = 20, color: str = "currentColor", margin_right: int = 6, style_extra: str = "") -> str:
    """Generates an HTML string for a Lucide icon suitable for embedding in st.markdown."""
    svg_url = f"https://cdn.jsdelivr.net/npm/lucide-static@latest/icons/{icon_name}.svg"
    
    filter_style = "filter: brightness(0) invert(1);"
    if color in ["primary", "#3b82f6", "blue"]:
        filter_style = "filter: invert(48%) sepia(79%) saturate(2476%) hue-rotate(200deg);"
    elif color in ["green", "positive", "#22c55e"]:
        filter_style = "filter: invert(62%) sepia(85%) saturate(417%) hue-rotate(92deg);"
    elif color in ["warning", "#f59e0b", "yellow"]:
        filter_style = "filter: invert(74%) sepia(61%) saturate(1637%) hue-rotate(354deg);"
    elif color in ["danger", "negative", "#ef4444", "red"]:
        filter_style = "filter: invert(59%) sepia(88%) saturate(2132%) hue-rotate(325deg);"
    elif color in ["purple", "#8b5cf6"]:
        filter_style = "filter: invert(53%) sepia(85%) saturate(2250%) hue-rotate(228deg);"
    elif color in ["cyan", "#06b6d4"]:
        filter_style = "filter: invert(65%) sepia(74%) saturate(2150%) hue-rotate(155deg);"
    elif color in ["indigo", "#6366f1"]:
        filter_style = "filter: invert(45%) sepia(80%) saturate(2500%) hue-rotate(218deg);"

    margin_css = f"margin-right: {margin_right}px;" if margin_right > 0 else ""
    img_style = f"width: {size}px; height: {size}px; vertical-align: middle; {margin_css} display: inline-block; {filter_style} {style_extra}"
    return f'<img src="{svg_url}" width="{size}" height="{size}" style="{img_style}" alt="{icon_name}" />'

def lucide_icon(icon_name: str, size: int = 28, color: str = "currentColor", margin_right: int = 6, style_extra: str = ""):
    """Renders a Lucide icon directly to Streamlit."""
    html_code = get_lucide_html(icon_name, size=size, color=color, margin_right=margin_right, style_extra=style_extra)
    st.markdown(html_code, unsafe_allow_html=True)