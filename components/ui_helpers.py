import streamlit as st

def apply_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            overflow: hidden !important;
            height: 100vh !important;
            background-color: #050506 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        
        #MainMenu, footer, header { visibility: hidden; height: 0px; }
        .block-container { 
            padding: 0.5rem 1rem !important; 
            max-width: 100% !important;
            height: 100vh !important;
            display: flex;
            flex-direction: column;
        }
        
        .motec-header {
            display: flex; align-items: center; justify-content: space-between;
            padding: 6px 14px; background: #0b0c10;
            border: 1px solid #1a1c23; border-radius: 6px; margin-bottom: 6px;
        }
        .brand-title { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 800; letter-spacing: 0.5px; color: #f8f9fa; }
        .brand-title .accent { color: #e51937; font-weight: 900; }
        .status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 4px; background: #111318; border: 1px solid #222631; color: #a0aec0; font-size: 10px; font-family: 'JetBrains Mono', monospace; }
        .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #00e676; box-shadow: 0 0 8px #00e676; }
        
        .sidebar-panel {
            background: #0b0c10; border: 1px solid #1a1c23; border-radius: 6px; padding: 10px; height: 100%;
            overflow-y: auto; 
        }
        
        .motec-kpi-container {
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-bottom: 6px;
        }
        .motec-kpi-card {
            background: #0b0c10; border: 1px solid #1a1c23; border-radius: 4px; padding: 6px 10px;
            position: relative; overflow: hidden;
        }
        .motec-kpi-card::before {
            content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: #3a3f50;
        }
        .motec-kpi-card.speed::before { background: #ffcc00; }
        .motec-kpi-card.rpm::before { background: #e51937; }
        .motec-kpi-card.fuel::before { background: #00e676; }
        
        .motec-kpi-title { font-size: 9px; font-family: 'JetBrains Mono', monospace; color: #718096; text-transform: uppercase; font-weight: 700; }
        .motec-kpi-value-group { display: flex; align-items: baseline; justify-content: space-between; margin-top: 2px; }
        .motec-kpi-val { font-size: 20px; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #f8f9fa; line-height: 1; }
        .motec-kpi-unit { font-size: 10px; color: #4a5568; font-weight: bold; margin-left: 2px; }

        .stTabs [data-baseweb="tab-list"] { gap: 4px; background-color: #0b0c10; padding: 4px 4px 0px 4px; border-radius: 6px 6px 0px 0px; border: 1px solid #1a1c23; }
        .stTabs [data-baseweb="tab"] { background-color: transparent; border: none; padding: 4px 14px; color: #718096; font-size: 11px; font-weight: 700; font-family: 'JetBrains Mono', monospace; height: 28px;}
        .stTabs [aria-selected="true"] { background-color: #151821 !important; color: #f8f9fa !important; border-bottom: 2px solid #e51937 !important; border-radius: 4px 4px 0px 0px; }
        .stTabs [data-testid="stVerticalBlock"] { gap: 0px !important; }
        
        .workspace-card { 
            background: #0b0c10; border-left: 1px solid #1a1c23; border-right: 1px solid #1a1c23; border-bottom: 1px solid #1a1c23;
            border-radius: 0px 0px 6px 6px; padding: 4px; background-color: #08090c;
        }
        
        .stFileUploader section { padding: 0.2rem 1rem !important; min-height: 50px !important; background-color: #111318 !important; border: 1px dashed #2d3142 !important;}
        .stFileUploader label { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def find_col(cols, keywords, exclude=None):
    if exclude is None: exclude = []
    for c in cols:
        cl = c.lower().strip()
        if all(k in cl for k in keywords) and not any(ex in cl for ex in exclude): return c
    return None