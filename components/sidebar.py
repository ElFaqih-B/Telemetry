import streamlit as st
from streamlit_option_menu import option_menu

def render_sidebar():
    with st.sidebar:
        # Header Logo
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 25px; padding: 5px 0;">
                <div style="background: linear-gradient(135deg, #1a0b0e, #e51937); border-radius: 8px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(229, 25, 55, 0.2);">
                    <span style="font-size: 20px; color: white;">🏎️</span>
                </div>
                <div>
                    <div style="color: #e51937; font-weight: 800; font-size: 15px; letter-spacing: 0.5px; font-family: 'Plus Jakarta Sans', sans-serif;">Automobilista 2</div>
                    <div style="color: #718096; font-size: 11px; font-family: 'JetBrains Mono', monospace;">Telemetry Vault</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Section Header
        st.markdown('<p style="color: #4a5568; font-size: 10px; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; font-family: \'Plus Jakarta Sans\', sans-serif;">ANALISIS UTAMA</p>', unsafe_allow_html=True)
        
        # Menu
        selected = option_menu(
            menu_title=None,
            options=["Dashboard Utama", "Data Vault", "Core Analytics"],
            icons=["grid-1x2", "database-add", "graph-up-arrow"], 
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent", "border": "none"},
                "icon": {"color": "#718096", "font-size": "14px"}, 
                "nav-link": {
                    "font-size": "13px", 
                    "text-align": "left", 
                    "margin": "4px 0px",
                    "padding": "10px 15px",
                    "color": "#a0aec0",
                    "font-family": "'Plus Jakarta Sans', sans-serif",
                    "font-weight": "600",
                    "border-radius": "8px",
                },
                "nav-link-selected": {
                    "background-color": "#1a0b0e",
                    "color": "#e51937",            
                    "icon-color": "#e51937",
                    "border-left": "3px solid #e51937", 
                    "border-radius": "0px 8px 8px 0px",
                    "font-weight": "700"
                },
            }
        )
        
    return selected