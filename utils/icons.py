import streamlit as st

def lucide_icon(icon_name, size=28, color="currentColor"):
    svg_url = f"https://cdn.jsdelivr.net/npm/lucide-static@latest/icons/{icon_name}.svg"
    
    # We use explicit style to ensure the image respects the size
    icon_html = f"""
        <img src="{svg_url}" 
             width="{size}" 
             height="{size}" 
             style="width: {size}px; height: {size}px; vertical-align: middle; filter: invert(0.5) sepia(1) saturate(5) hue-rotate(180deg);" 
        />
    """
    st.markdown(icon_html, unsafe_allow_html=True)