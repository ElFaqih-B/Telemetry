import streamlit as st
import pandas as pd
import datetime
from components.ui_helpers import find_col

def extract_driver_name(file_bytes):
    content = file_bytes.decode('utf-8', errors='ignore').split('\n')
    for line in content[:15]:
        if line.startswith('"Driver"'):
            parts = line.split(',')
            if len(parts) > 1: return parts[1].strip('"')
    return "Unknown Driver"

def render_sidebar_controls(db):
    st.markdown('<div class="sidebar-panel">', unsafe_allow_html=True)
    
    # 1. STATUS AKUN & TOMBOL KELUAR
    if st.session_state.get('username'):
        st.markdown(f"<div style='color:#00e676; font-size:12px; font-family:\"JetBrains Mono\"; margin-bottom:4px;'>🟢 Auth: <b>{st.session_state['username']}</b></div>", unsafe_allow_html=True)
        if st.session_state.get('driver_nickname'):
             st.markdown(f"<div style='color:#718096; font-size:11px; margin-bottom:10px; font-family:\"JetBrains Mono\";'>Game ID: {st.session_state['driver_nickname']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:#ffcc00; font-size:12px; font-family:\"JetBrains Mono\"; margin-bottom:10px;'>🟡 Mode: <b>GUEST (Local)</b></div>", unsafe_allow_html=True)

    if st.button("Log Out / Exit Workspace", use_container_width=True):
        st.session_state['username'] = None
        st.session_state['driver_nickname'] = None
        st.session_state['guest_data'] = None
        st.session_state['is_guest'] = False
        st.rerun()

    st.markdown("<hr style='border-color:#1a1c23; margin:10px 0;'>", unsafe_allow_html=True)
    
    # 2. DATA INGESTION ENGINE
    st.markdown('<div style="font-size: 11px; font-family:\'JetBrains Mono\'; color:#718096; margin-bottom:10px; font-weight:bold;">1. DATA INGESTION</div>', unsafe_allow_html=True)
    with st.form("ingestion_form", clear_on_submit=True):
        uploaded_file = st.file_uploader("Telemetry CSV Ingest", type=["csv"])
        if st.form_submit_button("Upload & Render", use_container_width=True):
            if uploaded_file is not None:
                with st.spinner("Memproses Data..."):
                    raw_bytes = uploaded_file.getvalue()
                    extracted_nickname = extract_driver_name(raw_bytes)
                    uploaded_file.seek(0)
                    df_raw = pd.read_csv(uploaded_file, skiprows=14)
                    df_raw.columns = [str(c).lower().strip() for c in df_raw.columns]
                    df_raw = df_raw.iloc[1:].reset_index(drop=True).apply(pd.to_numeric, errors="coerce").iloc[::2].reset_index(drop=True)
                    
                    cols = list(df_raw.columns)
                    df_clean = pd.DataFrame()
                    df_clean['lap_distance'] = df_raw[find_col(cols, ["distance"])] if find_col(cols, ["distance"]) else df_raw.index
                    df_clean['speed'] = df_raw[find_col(cols, ["ground speed"])] if find_col(cols, ["ground speed"]) else 0
                    df_clean['gear'] = df_raw[find_col(cols, ["gear"])] if find_col(cols, ["gear"]) else 0
                    df_clean['rpm'] = df_raw[find_col(cols, ["engine rpm"], exclude=["max", "limit"])] if find_col(cols, ["engine rpm"], exclude=["max", "limit"]) else 0
                    df_clean['throttle'] = df_raw[find_col(cols, ["throttle pos"])] if find_col(cols, ["throttle pos"]) else 0
                    df_clean['brake'] = df_raw[find_col(cols, ["brake pos"])] if find_col(cols, ["brake pos"]) else 0
                    df_clean['fuel_level'] = df_raw[find_col(cols, ["fuel level"], exclude=["pres", "cap"])] if find_col(cols, ["fuel level"], exclude=["pres", "cap"]) else 0
                    df_clean['oil_temp'] = df_raw[find_col(cols, ["eng oil temp"])] if find_col(cols, ["eng oil temp"]) else 0
                    df_clean['oil_pres'] = df_raw[find_col(cols, ["eng oil pres"])] if find_col(cols, ["eng oil pres"]) else 0
                    
                    if st.session_state.get('username'):
                        user = st.session_state['username']
                        db.execute_query("UPDATE tb_akun SET driver_nickname = %s WHERE username = %s", (extracted_nickname, user))
                        st.session_state['driver_nickname'] = extracted_nickname

                        sesi_baru = f"SES-{datetime.datetime.now().strftime('%H%M%S')}"
                        db.execute_query("INSERT INTO tb_sesi_latihan (id_sesi, id_mobil, username, tipe_sesi, waktu_unggah) VALUES (%s, %s, %s, %s, NOW())", (sesi_baru, 'LMDh-POR963', user, 'Free Practice'))
                        db.insert_bulk_telemetry(sesi_baru, df_clean)
                        st.success(f"Tersimpan di Akun! Nickname: {extracted_nickname}")
                    else:
                        st.session_state['guest_data'] = {'df': df_clean, 'nickname': extracted_nickname}
                        st.info(f"Mode Guest. Tersimpan Lokal. Driver: {extracted_nickname}")
            else:
                st.error("Upload CSV terlebih dahulu!")

    st.markdown("<hr style='border-color:#1a1c23; margin:10px 0;'>", unsafe_allow_html=True)
    
    # 3. SELECT SESSION
    st.markdown('<div style="font-size: 11px; font-family:\'JetBrains Mono\'; color:#718096; margin-bottom:4px; font-weight:bold;">2. SELECT SESSION</div>', unsafe_allow_html=True)
    opsi_sesi = []
    if st.session_state.get('guest_data'): opsi_sesi.append("GUEST SESSION (Local)")
    if st.session_state.get('username'):
        sesi_tersedia = db.execute_query("SELECT id_sesi FROM tb_sesi_latihan WHERE username=%s ORDER BY waktu_unggah DESC", (st.session_state['username'],), fetch=True)
        if sesi_tersedia: opsi_sesi.extend([s['id_sesi'] for s in sesi_tersedia])

    selected_sesi = st.selectbox("Arsip:", opsi_sesi, label_visibility="collapsed") if opsi_sesi else None

    # 4. CRUD PEMBALAP (HANYA MUNCUL JIKA LOGIN)
    if st.session_state.get('username'):
        st.markdown("<hr style='border-color:#1a1c23; margin:10px 0;'>", unsafe_allow_html=True)
        st.markdown('<div style="font-size: 11px; font-family:\'JetBrains Mono\'; color:#718096; margin-bottom:4px; font-weight:bold;">3. MANAJEMEN PEMBALAP</div>', unsafe_allow_html=True)
        with st.expander("Buka Menu CRUD"):
            data_pembalap = db.execute_query("SELECT id_pembalap, nama_pembalap FROM tb_pembalap", fetch=True)
            if data_pembalap: st.dataframe(pd.DataFrame(data_pembalap), use_container_width=True, hide_index=True)
            
            with st.form("tambah_pembalap"):
                new_id = st.text_input("ID (Contoh: DRV-002)")
                new_nama = st.text_input("Nama Pembalap")
                if st.form_submit_button("Tambah"):
                    if new_id and new_nama:
                        db.execute_query("INSERT INTO tb_pembalap (id_pembalap, nama_pembalap) VALUES (%s, %s)", (new_id, new_nama))
                        st.success("Ditambahkan!")
            with st.form("hapus_pembalap"):
                opsi_hapus = [p['id_pembalap'] for p in data_pembalap] if data_pembalap else []
                id_to_delete = st.selectbox("Hapus ID", opsi_hapus)
                if st.form_submit_button("Hapus"):
                    if id_to_delete:
                        db.execute_query("DELETE FROM tb_pembalap WHERE id_pembalap = %s", (id_to_delete,))
                        st.success("Dihapus!")

    st.markdown('</div>', unsafe_allow_html=True)
    return selected_sesi