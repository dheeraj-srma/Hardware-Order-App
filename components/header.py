import streamlit as st
from components.search import render_global_search


def render_header():
    """
    Renders the fixed header area for the Admin Center.
    """


    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader("Nalka Metals Portal")
    with c2:
        render_global_search() # Search bar appears in the top right

    # Create the header container
    header_container = st.container()
    
    with header_container:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Displays the title of the current module being viewed
            st.markdown(f"""
                <h1 style='margin: 0; font-size: 1.5rem; color: #f1f5f9;'>
                    {st.session_state.active_module}
                </h1>
            """, unsafe_allow_html=True)
            
        with col2:
            # Right-aligned utility actions
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.button("🔔", key="notifications")
            with col_b:
                st.button("👤", key="profile")
        
        # Horizontal rule to separate header from content
        st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid #334155;'>", unsafe_allow_html=True)