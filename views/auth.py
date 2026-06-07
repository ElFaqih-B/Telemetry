import streamlit as st
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def show_login_page(db):
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 30px;">
            <span style="font-size: 50px;">🏎️</span>
            <h1 style="color: #f8f9fa; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; margin-bottom: 0px;">AUTOMOBILISTA 2</h1>
            <p style="color: #e51937; font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 700; letter-spacing: 2px;">TELEMETRY DATA VAULT</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown('<div class="workspace-card" style="padding: 20px;">', unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["🔒 Masuk", "📝 Daftar Akun"])
        
        with tab_login:
            with st.form("login_form"):
                l_email = st.text_input("Email")
                l_pass = st.text_input("Password", type="password")
                if st.form_submit_button("Masuk", use_container_width=True):
                    res = db.execute_query("SELECT * FROM pengguna WHERE email=%s AND password_hash=%s", (l_email, hash_password(l_pass)), fetch=True)
                    if res:
                        st.session_state['is_logged_in'] = True
                        st.session_state['current_user_name'] = res[0]['nama_lengkap']
                        st.session_state['current_user_id'] = res[0]['id_user']
                        st.success("Autentikasi berhasil!")
                        st.rerun()
                    else:
                        st.error("Email atau Password salah!")
        
        with tab_register:
            with st.form("register_form"):
                r_nama = st.text_input("Nama Lengkap")
                r_email = st.text_input("Email")
                r_pass = st.text_input("Password", type="password")
                r_conf = st.text_input("Konfirmasi Password", type="password")
                if st.form_submit_button("Daftarkan Akun", use_container_width=True):
                    if r_pass != r_conf:
                        st.error("Konfirmasi password tidak cocok!")
                    elif db.execute_query("SELECT * FROM pengguna WHERE email=%s", (r_email,), fetch=True):
                        st.error("Email sudah terdaftar!")
                    elif r_nama and r_email and r_pass:
                        db.execute_query("INSERT INTO pengguna (nama_lengkap, email, password_hash, role_pengguna) VALUES (%s, %s, %s, %s)", 
                                         (r_nama, r_email, hash_password(r_pass), "Driver"))
                        st.success("Akun berhasil dibuat! Silakan buka tab Masuk.")
                    else:
                        st.error("Mohon lengkapi semua kolom!")
                        
        st.markdown('</div>', unsafe_allow_html=True)