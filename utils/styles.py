import streamlit as st

def inject_global_css():
    st.markdown("""
    <style>
        /* 1. Reset Streamlit App Shell */
        [data-testid="stAppViewContainer"] {
            background-color: #0f172a; /* Slate 900 background */
            color: #f1f5f9;
        }

        /* 2. Custom Sidebar Styling (The Dock) */
        [data-testid="stSidebar"] {
            background-color: #1e293b;
            border-right: 1px solid #334155;
            width: 260px !important;
        }

        /* 3. Global Typography & Spacing */
        .block-container {
            padding: 2rem 3rem !important;
            max-width: 100% !important;
        }

        /* 4. Enterprise Component Classes */
        .page-title {
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            color: #f8fafc;
        }
        
        .page-subtitle {
            font-size: 1.1rem;
            color: #94a3b8;
            margin-bottom: 2rem;
        }

        /* 4. Enterprise KPI Card Styling */
        .kpi-card {
            background: #1e293b;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #334155;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .kpi-label {
            color: #94a3b8;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .kpi-value {
            color: #f1f5f9;
            font-size: 1.8rem;
            font-weight: 700;
        }
        

        .kpi-card:hover {
            transform: translateY(-3px);
            border-color: #4f46e5;
            box-shadow: 0 8px 20px rgba(0,0,0,.25);
        }

        .kpi-header{
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:12px;
        }



        .kpi-icon{
            font-size:1.4rem;
        }

        .kpi-value{
            color:#f1f5f9;
            font-size:2.2rem;
            font-weight:700;
            margin:8px 0;
        }

        .kpi-subtitle{
            color:#64748b;
            font-size:.8rem;
        }

        .kpi-positive{
            color:#22c55e;
        }

        .kpi-negative{
            color:#ef4444;
        }

        .kpi-warning{
            color:#f59e0b;
        }

                
        /* 5. Clean up Streamlit UI noise */
        #MainMenu, footer { visibility: hidden; }
        
        /* 6. Button Styling for Sidebar/Nav */
        div.stButton > button {
            background-color: transparent !important;
            border: none !important;
            color: #cbd5e1 !important;
            text-align: left !important;
            padding: 12px 20px !important;
            border-radius: 8px !important;
        }
        
        div.stButton > button:hover {
            background-color: #334155 !important;
            color: #ffffff !important;
        }
    </style>
    <style>
        .page-title-container {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 0px;
        }
        .page-icon {
            font-size: 1.8rem;
            line-height: 1;
        }
        .page-title {
            margin: 0 !important;
            padding: 0 !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }
    </style>
    """, unsafe_allow_html=True)