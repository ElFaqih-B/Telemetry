import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from components.ui_helpers import render_motec_header

def render_workspace_analytics(db):
    render_motec_header("CORE ANALYTICS", "TELEMETRY WORKSPACE")
    
    # === FILTER DIPINDAH KE DALAM KANVAS ===
    st.markdown('<div class="workspace-card" style="margin-bottom: 25px;">', unsafe_allow_html=True)
    st.markdown("<h5 style='color: #f8f9fa; font-family: \"Plus Jakarta Sans\", sans-serif; margin-bottom: 15px; font-weight: 700;'>🔍 Filter Analisis</h5>", unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    kelas_rows = db.execute_query("SELECT id_kelas, nama_kelas FROM kelas_balap", fetch=True)
    kelas_opts = {k['nama_kelas']: k['id_kelas'] for k in kelas_rows} if kelas_rows else {}
    
    with col_f1:
        sel_kelas_name = st.selectbox("1. Kelas Kendaraan", list(kelas_opts.keys())) if kelas_opts else None
        sel_kelas = kelas_opts.get(sel_kelas_name) if sel_kelas_name else None
    
    sel_mobil = None
    with col_f2:
        if sel_kelas:
            mobil_rows = db.execute_query("SELECT id_mobil, model_kendaraan FROM mobil WHERE id_kelas=%s", (sel_kelas,), fetch=True)
            mobil_opts = {m['model_kendaraan']: m['id_mobil'] for m in mobil_rows} if mobil_rows else {}
            sel_mobil_name = st.selectbox("2. Mobil Terdeteksi", list(mobil_opts.keys())) if mobil_opts else None
            sel_mobil = mobil_opts.get(sel_mobil_name) if sel_mobil_name else None
        else:
            st.selectbox("2. Mobil Terdeteksi", ["Pilih Kelas Dulu"], disabled=True)
            
    selected_sesi = None
    with col_f3:
        if sel_mobil:
            sesi_rows = db.execute_query("SELECT id_sesi, waktu_unggahan FROM sesi_latihan WHERE id_mobil=%s AND id_user=%s ORDER BY waktu_unggahan DESC", 
                                        (sel_mobil, st.session_state.get('current_user_id', 0)), fetch=True)
            sesi_opts = {f"{s['id_sesi']} ({s['waktu_unggahan']})": s['id_sesi'] for s in sesi_rows} if sesi_rows else {}
            sel_sesi_label = st.selectbox("3. ID Sesi Historis", list(sesi_opts.keys())) if sesi_opts else None
            selected_sesi = sesi_opts.get(sel_sesi_label) if sel_sesi_label else None
        else:
            st.selectbox("3. ID Sesi Historis", ["Pilih Mobil Dulu"], disabled=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
    # =======================================

    if not selected_sesi:
        st.info("💡 Silakan lengkapi urutan filter di atas untuk mulai menganalisis telemetri.")
        return

    conn = db.connect()
    df = pd.read_sql(f"SELECT * FROM log_telemetri WHERE id_sesi = '{selected_sesi}' ORDER BY id_log ASC", conn)
    conn.close()

    if df.empty:
        st.warning("Data telemetri kosong untuk sesi ini.")
        return

    timecol, spdcol, rpmcol, gearcol, thrcol, brkcol, fuelcol, oiltempcol, oilpresscol, lapcol = "lap_distance", "speed_kmh", "rpm", "gear", "throttle_input", "brake_input", "fuel_level", "oil_temp", "oil_pressure", "lap_number"

    # KPI Sektor
    maxspd = df[spdcol].max() if spdcol in df.columns else 0
    avgspd = df[spdcol].mean() if spdcol in df.columns else 0
    maxrpm = df[rpmcol].max() if rpmcol in df.columns else 0
    
    st.markdown('<div class="motec-kpi-container">', unsafe_allow_html=True)
    kcol1, kcol2, kcol3, kcol4 = st.columns(4)
    kcol1.metric("Top Speed", f"{maxspd:.1f} km/h")
    kcol2.metric("Avg Speed", f"{avgspd:.1f} km/h")
    kcol3.metric("Max RPM", f"{maxrpm:.0f} RPM")
    kcol4.metric("Sisa Fuel", f"{df[fuelcol].iloc[-1]:.1f} L" if fuelcol in df.columns and not df.empty else "N/A")
    st.markdown('</div>', unsafe_allow_html=True)

    tab_driver, tab_health, tab_compare = st.tabs(["📊 Driver Inputs", "🔧 Vehicle Health", "⏱️ Lap Comparison"])

    layout_motec = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#07080a", font=dict(color="#a0aec0", family="JetBrains Mono", size=10),
        margin=dict(l=45, r=45, t=15, b=10), hovermode="x unified", dragmode="pan", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1, font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
    )
    
    # KONFIGURASI STRETCH GRAPH (Membebaskan axis-X agar bisa digeser dan di-zoom pakai scroll)
    x_axis_style = dict(showgrid=True, gridcolor="#13161f", zeroline=False, linecolor="#1a1c23", fixedrange=False) 
    y_axis_style = dict(showgrid=True, gridcolor="#13161f", zeroline=False, linecolor="#1a1c23", fixedrange=True) 

    with tab_driver:
        st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.4, 0.3, 0.3], specs=[[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}]])
        if spdcol in df.columns: fig.add_trace(go.Scattergl(x=df[timecol], y=df[spdcol], name="Speed", line=dict(color="#ffcc00", width=1.5)), row=1, col=1)
        if gearcol in df.columns: fig.add_trace(go.Scattergl(x=df[timecol], y=df[gearcol], name="Gear", line=dict(color="#00b0ff", width=1.2, shape="hv")), row=1, col=1, secondary_y=True)
        if rpmcol in df.columns: fig.add_trace(go.Scattergl(x=df[timecol], y=df[rpmcol], name="RPM", line=dict(color="#e51937", width=1.2)), row=2, col=1)
        if thrcol in df.columns: fig.add_trace(go.Scattergl(x=df[timecol], y=df[thrcol], name="Throttle", line=dict(color="#00e676", width=1.2, shape="hv")), row=3, col=1)
        if brkcol in df.columns: fig.add_trace(go.Scattergl(x=df[timecol], y=df[brkcol], name="Brake", line=dict(color="#ff2d2d", width=1.2, shape="hv")), row=3, col=1)
        
        fig.update_layout(height=500, **layout_motec)
        fig.update_xaxes(**x_axis_style)
        fig.update_yaxes(**y_axis_style)
        # Parameter config di bawah yang mengaktifkan fitur Scroll Zoom Mouse
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_health:
        st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
        fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5, 0.5], specs=[[{"secondary_y": False}], [{"secondary_y": True}]])
        if fuelcol in df.columns: fig2.add_trace(go.Scattergl(x=df[timecol], y=df[fuelcol], name="Fuel Lvl", line=dict(color="#00e676", width=1.5)), row=1, col=1)
        if oiltempcol in df.columns: fig2.add_trace(go.Scattergl(x=df[timecol], y=df[oiltempcol], name="Oil Temp", line=dict(color="#ff6d00", width=1.5)), row=2, col=1)
        if oilpresscol in df.columns: fig2.add_trace(go.Scattergl(x=df[timecol], y=df[oilpresscol], name="Oil Pres", line=dict(color="#00b0ff", width=1.2)), row=2, col=1, secondary_y=True)
        
        fig2.update_layout(height=400, **layout_motec)
        fig2.update_xaxes(**x_axis_style)
        fig2.update_yaxes(**y_axis_style)
        st.plotly_chart(fig2, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_compare:
        st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
        laps_available = df[lapcol].unique() if lapcol in df.columns else []
        col_lap_a, col_lap_b = st.columns(2)
        
        with col_lap_a:
            lap_a = st.selectbox("Pilih Lap A", laps_available, key="lap_a")
        with col_lap_b:
            lap_b = st.selectbox("Pilih Lap B", laps_available, key="lap_b")
            
        if lap_a is not None and lap_b is not None:
            df_a = df[df[lapcol] == lap_a]
            df_b = df[df[lapcol] == lap_b]
            
            fig3 = go.Figure()
            dist_a = df_a[timecol] - df_a[timecol].min()
            dist_b = df_b[timecol] - df_b[timecol].min()
            
            fig3.add_trace(go.Scattergl(x=dist_a, y=df_a[spdcol], name=f"Lap {lap_a} Speed", line=dict(color="#00ffff", width=2)))
            fig3.add_trace(go.Scattergl(x=dist_b, y=df_b[spdcol], name=f"Lap {lap_b} Speed", line=dict(color="#ff00ff", width=2)))
            
            fig3.update_layout(height=400, title="Speed Trace Comparison (Scroll untuk Zoom Area Pengereman)", **layout_motec)
            fig3.update_xaxes(title="Jarak Lintasan", **x_axis_style)
            fig3.update_yaxes(title="Speed (km/h)", **y_axis_style)
            st.plotly_chart(fig3, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)