import streamlit as st
import pandas as pd
import datetime
from components.ui_helpers import find_col

def extract_vehicle_from_csv(file_bytes):
    """Mendeteksi nama mobil langsung dari raw text file CSV Automobilista"""
    content = file_bytes.decode('utf-8', errors='ignore').split('\n')
    for line in content[:20]:
        if line.startswith('"Vehicle"'):
            parts = line.split(',')
            if len(parts) > 1: return parts[1].strip('"\r')
    return "Unknown Vehicle"

def render_data_vault(db):
    st.markdown("### 🗄️ Manajemen Arsip & Ingesti Data")
    st.write("Unggah file CSV telemetri Anda. Sistem akan mendeteksi kendaraan secara otomatis.")
    
    with st.form("ingesti_form"):
        col1, col2 = st.columns(2)
        with col1:
            input_pembalap = st.text_input("Nama Pembalap")
        with col2:
            sel_tipe = st.selectbox("Tipe Sesi", ["Free Practice", "Qualifying", "Race", "Time Trial"])
        
        uploaded_file = st.file_uploader("Tarik dan lepas file CSV di sini", type=["csv"])
        submit_btn = st.form_submit_button("Proses Data Telemetri", type="primary")

        if submit_btn:
            if uploaded_file and input_pembalap:
                with st.spinner("Membaca dan mendeteksi data CSV..."):
                    raw_bytes = uploaded_file.getvalue()
                    detected_vehicle = extract_vehicle_from_csv(raw_bytes)
                    
                    # 1. Pastikan Kelas Default "AUTO" Ada
                    cek_kelas = db.execute_query("SELECT id_kelas FROM kelas_balap WHERE id_kelas='AUTO'", fetch=True)
                    if not cek_kelas:
                        db.execute_query("INSERT INTO kelas_balap (id_kelas, nama_kelas) VALUES ('AUTO', 'Auto Detected')")
                    
                    # 2. Registrasi Mobil yang Terdeteksi jika belum ada
                    cek_mobil = db.execute_query("SELECT id_mobil FROM mobil WHERE model_kendaraan=%s", (detected_vehicle,), fetch=True)
                    if not cek_mobil:
                        id_mobil_gen = f"AUTO-{hash(detected_vehicle) % 10000:04d}"
                        db.execute_query("INSERT INTO mobil (id_mobil, id_kelas, pabrikan, model_kendaraan) VALUES (%s, %s, %s, %s)", 
                                        (id_mobil_gen, 'AUTO', 'AM2', detected_vehicle))
                        final_id_mobil = id_mobil_gen
                    else:
                        final_id_mobil = cek_mobil[0]['id_mobil']

                    # 3. Handle Pembalap
                    pembalap_id = f"DRV-{hash(input_pembalap) % 10000:04d}"
                    cek_pembalap = db.execute_query("SELECT id_pembalap FROM pembalap WHERE nama_pembalap=%s", (input_pembalap,), fetch=True)
                    if not cek_pembalap:
                        db.execute_query("INSERT INTO pembalap (id_pembalap, nama_pembalap) VALUES (%s, %s)", (pembalap_id, input_pembalap))
                    else:
                        pembalap_id = cek_pembalap[0]['id_pembalap']
                    
                    # 4. Parsing Pandas
                    uploaded_file.seek(0)
                    df_raw = pd.read_csv(uploaded_file, skiprows=14)
                    df_raw.columns = [str(c).lower().strip() for c in df_raw.columns]
                    df_raw = df_raw.iloc[1:].reset_index(drop=True).apply(pd.to_numeric, errors="coerce").iloc[::2].reset_index(drop=True)
                    
                    cols = list(df_raw.columns)
                    df_clean = pd.DataFrame()
                    df_clean['lap_number'] = df_raw[find_col(cols, ["lap"])] if find_col(cols, ["lap"], exclude=["distance", "time"]) else 1
                    df_clean['lap_distance'] = df_raw[find_col(cols, ["distance"])] if find_col(cols, ["distance"]) else df_raw.index
                    df_clean['speed'] = df_raw[find_col(cols, ["ground speed"])] if find_col(cols, ["ground speed"]) else 0
                    df_clean['gear'] = df_raw[find_col(cols, ["gear"])] if find_col(cols, ["gear"]) else 0
                    df_clean['rpm'] = df_raw[find_col(cols, ["engine rpm"], exclude=["max", "limit"])] if find_col(cols, ["engine rpm"], exclude=["max", "limit"]) else 0
                    df_clean['throttle'] = df_raw[find_col(cols, ["throttle pos"])] if find_col(cols, ["throttle pos"]) else 0
                    df_clean['brake'] = df_raw[find_col(cols, ["brake pos"])] if find_col(cols, ["brake pos"]) else 0
                    df_clean['fuel_level'] = df_raw[find_col(cols, ["fuel level"], exclude=["pres", "cap"])] if find_col(cols, ["fuel level"], exclude=["pres", "cap"]) else 0
                    df_clean['oil_temp'] = df_raw[find_col(cols, ["eng oil temp"])] if find_col(cols, ["eng oil temp"]) else 0
                    df_clean['oil_pres'] = df_raw[find_col(cols, ["eng oil pres"])] if find_col(cols, ["eng oil pres"]) else 0
                    
                    sesi_baru = f"SES-{datetime.datetime.now().strftime('%H%M%S')}"
                    user_id = st.session_state['current_user_id']
                    db.execute_query("INSERT INTO sesi_latihan (id_sesi, id_mobil, id_pembalap, id_user, tipe_sesi, waktu_unggahan) VALUES (%s, %s, %s, %s, %s, NOW())", 
                                    (sesi_baru, final_id_mobil, pembalap_id, user_id, sel_tipe))
                    
                    if db.insert_bulk_telemetry(sesi_baru, df_clean):
                        st.success(f"Berhasil! Kendaraan terdeteksi: **{detected_vehicle}**. Sesi: {sesi_baru}")
                    else:
                        st.error("Gagal memasukkan data telemetri ke pangkalan data.")
            else:
                st.error("Harap isi Nama Pembalap dan pastikan CSV terunggah!")
                
    st.markdown("<hr style='border-color: #1a1c23;'>", unsafe_allow_html=True)
    st.markdown("#### Riwayat Arsip Sesi Anda")
    q = """
    SELECT s.id_sesi, m.model_kendaraan as 'Mobil', p.nama_pembalap as 'Diunggah Oleh', s.tipe_sesi, s.waktu_unggahan as 'Waktu Unggah'
    FROM sesi_latihan s
    JOIN mobil m ON s.id_mobil = m.id_mobil
    JOIN pembalap p ON s.id_pembalap = p.id_pembalap
    WHERE s.id_user = %s
    ORDER BY s.waktu_unggahan DESC
    """
    arsip = db.execute_query(q, (st.session_state.get('current_user_id', 0),), fetch=True)
    
    if arsip:
        df_arsip = pd.DataFrame(arsip)
        st.dataframe(df_arsip, use_container_width=True, hide_index=True)
        
        with st.form("hapus_sesi_form"):
            col_del, col_btn = st.columns([3, 1])
            with col_del:
                del_sesi = st.selectbox("Pilih Sesi untuk dihapus (🗑️):", df_arsip['id_sesi'])
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Hapus Data", use_container_width=True):
                    db.execute_query("DELETE FROM sesi_latihan WHERE id_sesi = %s", (del_sesi,))
                    st.success(f"Sesi {del_sesi} telah dihapus!")
                    st.rerun()
    else:
        st.info("Belum ada data historis yang diunggah.")