import streamlit as st
from components.ui_helpers import apply_custom_css
from models.db_manager import DatabaseManager
from views.auth import show_login_page
from views.data_vault import render_sidebar_controls
from views.analytics import render_workspace_analytics

# 1. SETUP PAGE CONFIG
st.set_page_config(
    page_title="Automobilista 2 - Telemetry Vault",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. VARIABEL STATUS KEAMANAN & SESI
if 'username' not in st.session_state: st.session_state['username'] = None
if 'driver_nickname' not in st.session_state: st.session_state['driver_nickname'] = None
if 'guest_data' not in st.session_state: st.session_state['guest_data'] = None
if 'is_guest' not in st.session_state: st.session_state['is_guest'] = False

# 3. TERAPKAN CSS MOTEC 100vh
apply_custom_css()

# 4. INISIALISASI DATABASE
db = DatabaseManager()

# 5. GERBANG AUTENTIKASI (ROUTING)
# Jika belum login DAN bukan guest -> Tampilkan halaman khusus Login
if st.session_state['username'] is None and not st.session_state['is_guest']:
    show_login_page(db)
else:
    # Jika sudah lolos (Login atau Guest), tampilkan Dashboard Utama
    col_io, col_main = st.columns([1, 4.5], gap="small")
    
    with col_io:
        sesi_yang_dipilih = render_sidebar_controls(db)
    
    with col_main:
        render_workspace_analytics(db, sesi_yang_dipilih)