import streamlit as st
from components.ui_helpers import render_motec_header
from models.db_manager import DatabaseManager

def show_dashboard():
    render_motec_header("DASHBOARD", "SYSTEM OVERVIEW")
    
    st.write("### 🏁 Pusat Data Telemetri - Automobilista 2")
    st.write("Sistem Gudang Data (Data Vault) untuk mengarsipkan dan menganalisis performa mobil balap secara sistematis.")
    
    db = DatabaseManager()
    
    sesi_count = db.execute_query("SELECT COUNT(*) as total FROM sesi_latihan", fetch=True)
    kelas_count = db.execute_query("SELECT COUNT(*) as total FROM kelas_balap", fetch=True)
    log_count = db.execute_query("SELECT COUNT(*) as total FROM log_telemetri", fetch=True)
    
    total_sesi = sesi_count[0]['total'] if sesi_count else 0
    total_kelas = kelas_count[0]['total'] if kelas_count else 0
    total_log = log_count[0]['total'] if log_count else 0
    
    st.markdown('<div class="motec-kpi-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Sesi Tersimpan", value=f"{total_sesi} Sesi") 
    with col2:
        st.metric(label="Total Kelas Balap Aktif", value=f"{total_kelas} Kelas") 
    with col3:
        st.metric(label="Total Baris Telemetri", value=f"{total_log:,} Baris") 
    st.markdown('</div>', unsafe_allow_html=True)