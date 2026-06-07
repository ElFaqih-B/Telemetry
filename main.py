import streamlit as st
from components.ui_helpers import apply_custom_css
from models.db_manager import DatabaseManager
from views.auth import show_login_page
from views.dashboard import show_dashboard
from views.data_vault import render_data_vault
from views.analytics import render_workspace_analytics
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Automobilista 2 - Telemetry Vault",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded", # Pastikan sidebar terekspansi dari awal
)

# 1. Inisialisasi Status
if 'is_logged_in' not in st.session_state: 
    st.session_state['is_logged_in'] = False
    st.session_state['current_user_name'] = None
    st.session_state['current_user_id'] = None

# 2. Terapkan CSS Dinamis
apply_custom_css(is_logged_in=st.session_state['is_logged_in'])

db = DatabaseManager()
db.setup_database()

# 3. Routing Halaman
if not st.session_state['is_logged_in']:
    show_login_page(db)
else:
    # --- RENDER SIDEBAR ATAS ---
    menu = render_sidebar()
    
    # --- RENDER SIDEBAR BAWAH (LOGOUT & FOOTER) ---
    with st.sidebar:
        # Spacer ajaib untuk mendorong konten ke bawah (sesuaikan tinggi vh jika layar terlalu besar/kecil)
        st.markdown('<div style="min-height: 54vh;"></div>', unsafe_allow_html=True)
        
        # Tombol Logout
        if st.button("Logout / Keluar Area", use_container_width=True):
            st.cache_data.clear()
            for key in st.session_state.keys():
                del st.session_state[key]
            st.session_state['is_logged_in'] = False
            st.rerun()

        # Footer ala Foto Kedua

    # --- TAMPILKAN KONTEN HALAMAN ---
    if menu == "Dashboard Utama":
        show_dashboard()
    elif menu == "Data Vault":
        render_data_vault(db)
    elif menu == "Core Analytics":
        render_workspace_analytics(db)