import streamlit as st
import hashlib

def hash_password(password):
    """Fungsi enkripsi password sebelum masuk ke Database."""
    return hashlib.sha256(password.encode()).hexdigest()

def show_login_page(db):
    # Spacer atas agar letaknya di tengah layar
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Logo & Judul
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
    
    # Membuat 3 kolom agar form login ada tepat di tengah (rasio 1 : 1.5 : 1)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        # Menggunakan class CSS workspace-card milikmu agar temanya nyambung
        st.markdown('<div class="workspace-card" style="padding: 20px;">', unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["🔒 Login Server", "📝 Sign Up Akun"])
        
        # TAB LOGIN
        with tab_login:
            with st.form("login_form"):
                l_user = st.text_input("Username")
                l_pass = st.text_input("Password", type="password")
                if st.form_submit_button("Masuk ke Workspace", use_container_width=True):
                    res = db.execute_query("SELECT * FROM tb_akun WHERE username=%s AND password=%s", (l_user, hash_password(l_pass)), fetch=True)
                    if res:
                        st.session_state['username'] = l_user
                        st.session_state['driver_nickname'] = res[0]['driver_nickname']
                        st.session_state['is_guest'] = False # Mode Guest dimatikan
                        st.rerun() # Refresh untuk masuk ke halaman utama
                    else:
                        st.error("Username atau Password salah!")
        
        # TAB SIGN UP
        with tab_register:
            with st.form("register_form"):
                r_user = st.text_input("Username Baru")
                r_pass = st.text_input("Password Baru", type="password")
                if st.form_submit_button("Daftar Akun", use_container_width=True):
                    if db.execute_query("SELECT * FROM tb_akun WHERE username=%s", (r_user,), fetch=True):
                        st.error("Username sudah terdaftar!")
                    elif r_user and r_pass:
                        db.execute_query("INSERT INTO tb_akun (username, password, driver_nickname) VALUES (%s, %s, %s)", (r_user, hash_password(r_pass), ""))
                        st.success("Akun berhasil dibuat! Silakan buka tab Login.")
                    else:
                        st.error("Mohon lengkapi semua kolom!")
                        
        st.markdown("<hr style='border-color:#1a1c23; margin:20px 0px 10px 0px;'>", unsafe_allow_html=True)
        
        # TOMBOL MODE TAMU (TEMPORARY LOCAL)
        if st.button("🌐 Masuk sebagai Guest (Local Only)", use_container_width=True):
            st.session_state['is_guest'] = True
            st.session_state['username'] = None
            st.session_state['driver_nickname'] = None
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)