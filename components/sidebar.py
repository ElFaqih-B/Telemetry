import streamlit as st
from streamlit_option_menu import option_menu

def render_sidebar():
    with st.sidebar:
        # 1. Custom Header Logo (Meniru Pojok Kiri Atas Gambar)
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 30px; padding: 10px 0;">
                <div style="background: linear-gradient(135deg, #2a0a10, #e51937); border-radius: 8px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(229, 25, 55, 0.2);">
                    <span style="font-size: 20px; color: white;">🏎️</span>
                </div>
                <div>
                    <div style="color: #e51937; font-weight: 800; font-size: 15px; letter-spacing: 0.5px; font-family: 'Plus Jakarta Sans', sans-serif;">Automobilista 2</div>
                    <div style="color: #718096; font-size: 11px; font-family: 'JetBrains Mono', monospace;">Telemetry Vault</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 2. Section Header
        st.markdown('<p style="color: #4a5568; font-size: 10px; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; font-family: \'Plus Jakarta Sans\', sans-serif;">ANALISIS UTAMA</p>', unsafe_allow_html=True)
        
        # 3. Menu Interaktif Elegan
        # Nama menu disesuaikan dengan fitur aplikasimu saat ini
        selected = option_menu(
            menu_title=None,
            options=["Dashboard Utama", "Data Vault", "Core Analytics"],
            icons=["grid-1x2", "database-add", "graph-up-arrow"], # Ikon dari Bootstrap Icons
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
                    "background-color": "#1a0b0e", # Warna latar merah gelap/transparan
                    "color": "#e51937",            # Teks warna merah tulisan
                    "icon-color": "#e51937",
                    "border-left": "3px solid #e51937", # Garis aksen merah di kiri
                    "border-radius": "0px 8px 8px 0px",
                    "font-weight": "700"
                },
            }
        )
        
        # Spacer untuk mendorong footer ke bawah
        st.markdown("<br>" * 10, unsafe_allow_html=True)
        
        # 4. Footer ala Mockup (Informasi Sirkuit)
        st.markdown("""
            <div style="border-top: 1px solid #1a1c23; padding-top: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="color: #a0aec0; font-size: 11px; font-weight: 700; font-family: 'Plus Jakarta Sans', sans-serif;">Circuit de la Sarthe</div>
                        <div style="color: #4a5568; font-size: 10px; font-family: 'JetBrains Mono', monospace;">Free Practice • AM2026</div>
                    </div>
                    <div style="background-color: #111318; padding: 6px 8px; border-radius: 6px; border: 1px solid #1a1c23;">
                        <span style="font-size: 12px; color: #718096;">🌙</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    return selected