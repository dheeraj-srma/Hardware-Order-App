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
        .kpi-card-content {
            padding: 0.2rem 0.2rem 0 0.2rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(div.kpi-card-content) {
            background: linear-gradient(180deg, #1e293b 0%, #172033 100%) !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            padding: 1.1rem 1.2rem 0.9rem 1.2rem !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            margin-bottom: 0.75rem !important;
        }
        
        [data-testid="stVerticalBlockBorderWrapper"]:has(div.kpi-card-content):hover {
            transform: translateY(-3px) !important;
            border-color: #3b82f6 !important;
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.25) !important;
        }

        /* Click for Details Button INSIDE the Card */
        [data-testid="stVerticalBlockBorderWrapper"]:has(div.kpi-card-content) div.stButton > button {
            background: rgba(30, 41, 59, 0.6) !important;
            border: 1px solid #334155 !important;
            color: #94a3b8 !important;
            font-size: 0.78rem !important;
            font-weight: 500 !important;
            padding: 5px 12px !important;
            margin-top: 10px !important;
            border-radius: 6px !important;
            box-shadow: none !important;
            width: 100% !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(div.kpi-card-content) div.stButton > button:hover {
            background: #2563eb !important;
            color: #ffffff !important;
            border-color: #60a5fa !important;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;
        }
        
        .kpi-label {
            color: #94a3b8;
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .kpi-value {
            color: #f1f5f9;
            font-size: 1.9rem;
            font-weight: 750;
            margin: 6px 0;
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
        
        /* 6. Sidebar Navigation Buttons */
        [data-testid="stSidebar"] div.stButton > button {
            background-color: transparent !important;
            border: 1px solid transparent !important;
            color: #cbd5e1 !important;
            text-align: left !important;
            padding: 10px 16px !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            width: 100% !important;
            transition: all 0.2s ease !important;
        }
        
        [data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #334155 !important;
            border-color: #475569 !important;
            color: #ffffff !important;
        }

        /* 7. Main Workspace Action Buttons (Modular & Distinct) */
        [data-testid="stMainBlockContainer"] div.stButton > button,
        [data-testid="stAppViewContainer"] div.stButton > button:not([data-testid="stSidebar"] *) {
            background: linear-gradient(180deg, #1e293b 0%, #172033 100%) !important;
            border: 1px solid #334155 !important;
            color: #f1f5f9 !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            padding: 0.65rem 1.15rem !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
        }

        [data-testid="stMainBlockContainer"] div.stButton > button:hover,
        [data-testid="stAppViewContainer"] div.stButton > button:not([data-testid="stSidebar"] *):hover {
            background: linear-gradient(180deg, #2b3952 0%, #1e293b 100%) !important;
            border-color: #3b82f6 !important;
            color: #ffffff !important;
            box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3) !important;
            transform: translateY(-2px) !important;
        }

        [data-testid="stMainBlockContainer"] div.stButton > button[kind="primary"],
        [data-testid="stAppViewContainer"] div.stButton > button[kind="primary"] {
            background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%) !important;
            border-color: #3b82f6 !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35) !important;
        }

        [data-testid="stMainBlockContainer"] div.stButton > button[kind="primary"]:hover,
        [data-testid="stAppViewContainer"] div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(180deg, #1d4ed8 0%, #1e40af 100%) !important;
            border-color: #60a5fa !important;
            box-shadow: 0 6px 18px rgba(37, 99, 235, 0.45) !important;
            transform: translateY(-2px) !important;
        }

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