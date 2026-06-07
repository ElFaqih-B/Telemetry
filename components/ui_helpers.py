import streamlit as st

def apply_custom_css(is_logged_in=False):
    css_string = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background-color: #050506 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #f8f9fa;
    }
    
    /* SEMBUNYIKAN HEADER & TOOLBAR STREAMLIT */
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* STYLING MOTEC HEADER */
    .motec-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 12px 18px; background: linear-gradient(90deg, #0b0c10, #111318);
        border: 1px solid #1a1c23; border-radius: 8px; margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .brand-title { display: flex; align-items: center; gap: 8px; font-size: 18px; font-weight: 800; letter-spacing: 0.5px; color: #f8f9fa; }
    .brand-title .accent { color: #e51937; font-weight: 900; }
    .status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 4px; background: #151821; border: 1px solid #222631; color: #a0aec0; font-size: 12px; font-family: 'JetBrains Mono', monospace; font-weight: bold;}
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #00e676; box-shadow: 0 0 8px #00e676; }
    
    /* KUSTOMISASI TOMBOL LOGOUT BIAR MENYATU DENGAN TEMA */
    .stButton>button {
        border-radius: 6px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
    }
    """

    if is_logged_in:
        # SIDEBAR TERKUNCI PERMANEN (TIDAK BISA DITUTUP)
        css_string += """
        [data-testid="collapsedControl"] { display: none !important; }
        section[data-testid="stSidebar"] {
            width: 270px !important;
            min-width: 270px !important;
            background-color: #08090c !important;
            border-right: 1px solid #1a1c23 !important;
            transform: translateX(0px) !important; /* Paksa selalu terbuka */
        }
        </style>
        """
    else:
        # SIDEBAR HANCUR SAAT DI HALAMAN LOGIN
        css_string += """
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        </style>
        """
        
    st.markdown(css_string, unsafe_allow_html=True)


def render_motec_header(title, subtitle):
    st.markdown(
        f'<div class="motec-header"><div class="brand-title"><span class="accent">AUTO 2</span><span>| {title}</span></div><div class="status-badge"><span class="status-dot"></span>{subtitle}</div></div>', 
        unsafe_allow_html=True
    )


def find_col(cols, keywords, exclude=None):
    if exclude is None: exclude = []
    for c in cols:
        cl = c.lower().strip()
        if all(k in cl for k in keywords) and not any(ex in cl for ex in exclude): return c
    return None