import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_workspace_analytics(db, selected_sesi):
    mode_text = "GUEST MODE (LOCAL)" if selected_sesi == "GUEST SESSION (Local)" else "SYNC"
    
    st.markdown(
        f'<div class="motec-header"><div class="brand-title"><span class="accent">AUTOMOBILISTA 2</span><span>| TELEMETRY WORKSPACE</span></div><div class="status-badge"><span class="status-dot"></span>{mode_text}</div></div>', 
        unsafe_allow_html=True
    )

    if selected_sesi:
        if selected_sesi == "GUEST SESSION (Local)":
            df = st.session_state['guest_data']['df']
            driver_name = st.session_state['guest_data']['nickname']
            st.markdown(f"<div style='color:#a0aec0; font-size:12px; margin-bottom:5px; font-family:\"JetBrains Mono\";'>Driver Automobilista: <b style='color:#ffcc00;'>{driver_name}</b> (Data Tidak Disimpan ke Server)</div>", unsafe_allow_html=True)
        else:
            conn = db.connect()
            df = pd.read_sql(f"SELECT * FROM tb_log_telemetri WHERE id_sesi = '{selected_sesi}' ORDER BY id_log ASC", conn)
            
            # Tarik otomatis Nickname dari relasi Database Akun
            cur = conn.cursor(dictionary=True)
            cur.execute(f"SELECT a.driver_nickname FROM tb_akun a JOIN tb_sesi_latihan s ON a.username = s.username WHERE s.id_sesi = '{selected_sesi}'")
            res = cur.fetchone()
            conn.close()
            
            driver_name = res['driver_nickname'] if res else "Unknown"
            st.markdown(f"<div style='color:#00e676; font-size:12px; margin-bottom:5px; font-family:\"JetBrains Mono\";'>Driver Automobilista: <b>{driver_name}</b> (Cloud Sync)</div>", unsafe_allow_html=True)

        # Plotly Mapping
        timecol = "lap_distance" if "lap_distance" in df.columns and df["lap_distance"].sum() > 0 else ("id_log" if "id_log" in df.columns else df.index)
        spdcol = "speed_kmh" if "speed_kmh" in df.columns else "speed"
        rpmcol = "rpm"
        gearcol = "gear"
        thrcol = "throttle_input" if "throttle_input" in df.columns else "throttle"
        brkcol = "brake_input" if "brake_input" in df.columns else "brake"
        fuelcol = "fuel_level"
        oiltempcol = "oil_temp"
        oilpresscol = "oil_pressure" if "oil_pressure" in df.columns else "oil_pres"

        maxspd = df[spdcol].max() if spdcol in df.columns else 0
        avgspd = df[spdcol].mean() if spdcol in df.columns else 0
        maxrpm = df[rpmcol].max() if rpmcol in df.columns else 0
        maxfuel = df[fuelcol].max() if fuelcol in df.columns else 0

        st.markdown(f"""
            <div class="motec-kpi-container">
                <div class="motec-kpi-card speed"><div class="motec-kpi-title">V_MAX (SPEED)</div><div class="motec-kpi-value-group"><span class="motec-kpi-val" style="color:#ffcc00">{maxspd:.1f}</span><span class="motec-kpi-unit">KM/H</span></div></div>
                <div class="motec-kpi-card"><div class="motec-kpi-title">V_AVG (SPEED)</div><div class="motec-kpi-value-group"><span class="motec-kpi-val">{avgspd:.1f}</span><span class="motec-kpi-unit">KM/H</span></div></div>
                <div class="motec-kpi-card rpm"><div class="motec-kpi-title">RPM_MAX</div><div class="motec-kpi-value-group"><span class="motec-kpi-val" style="color:#e51937">{maxrpm:.0f}</span><span class="motec-kpi-unit">RPM</span></div></div>
                <div class="motec-kpi-card fuel"><div class="motec-kpi-title">MAX_FUEL_LOGGED</div><div class="motec-kpi-value-group"><span class="motec-kpi-val" style="color:#00e676">{maxfuel:.1f}</span><span class="motec-kpi-unit">L</span></div></div>
            </div>
            """, unsafe_allow_html=True)

        tab_driver, tab_health = st.tabs(["📊 ANALYSIS: DRIVER INPUTS", "🔧 ANALYSIS: VEHICLE HEALTH"])

        layout_motec = dict(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#07080a", font=dict(color="#a0aec0", family="JetBrains Mono", size=10),
            margin=dict(l=45, r=45, t=15, b=10), height=380, hovermode="x unified", dragmode="zoom", showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1, font=dict(size=10), bgcolor="rgba(0,0,0,0)", borderwidth=0),
            hoverlabel=dict(bgcolor="#111318", font_size=11, font_family="JetBrains Mono")
        )
        grid_style = dict(showgrid=True, gridcolor="#13161f", zeroline=False, linecolor="#1a1c23")

        with tab_driver:
            st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.40, 0.35, 0.25], specs=[[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}]])
            if spdcol in df.columns: fig.add_trace(go.Scattergl(x=df[timecol], y=df[spdcol], name="Speed", line=dict(color="#ffcc00", width=1.5)), row=1, col=1)
            if gearcol in df.columns: fig.add_trace(go.Scattergl(x=df[timecol], y=df[gearcol], name="Gear", line=dict(color="#00b0ff", width=1.2, shape="hv")), row=1, col=1, secondary_y=True)
            if rpmcol in df.columns: fig.add_trace(go.Scattergl(x=df[timecol], y=df[rpmcol], name="RPM", line=dict(color="#e51937", width=1.2)), row=2, col=1)
            if thrcol in df.columns: fig.add_trace(go.Scattergl(x=df[timecol], y=df[thrcol], name="Throttle", line=dict(color="#00e676", width=1.2, shape="hv")), row=3, col=1)
            if brkcol in df.columns: fig.add_trace(go.Scattergl(x=df[timecol], y=df[brkcol], name="Brake", line=dict(color="#ff2d2d", width=1.2, shape="hv")), row=3, col=1)
            
            fig.update_layout(**layout_motec)
            fig.update_xaxes(showspikes=True, spikemode="across", spikecolor="#a0aec0", spikethickness=1, spikesnap="cursor", row=3, col=1, **grid_style)
            fig.update_xaxes(row=1, col=1, **grid_style); fig.update_xaxes(row=2, col=1, **grid_style)
            fig.update_yaxes(**grid_style); fig.update_yaxes(fixedrange=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "scrollZoom": True})
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_health:
            st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
            fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.5], specs=[[{"secondary_y": True}], [{"secondary_y": True}]])
            if fuelcol in df.columns: fig2.add_trace(go.Scattergl(x=df[timecol], y=df[fuelcol], name="Fuel Lvl", line=dict(color="#00e676", width=1.5)), row=1, col=1, secondary_y=False)
            if oiltempcol in df.columns: fig2.add_trace(go.Scattergl(x=df[timecol], y=df[oiltempcol], name="Oil Temp", line=dict(color="#ff6d00", width=1.5)), row=2, col=1, secondary_y=False)
            if oilpresscol in df.columns: fig2.add_trace(go.Scattergl(x=df[timecol], y=df[oilpresscol], name="Oil Pres", line=dict(color="#00b0ff", width=1.2)), row=2, col=1, secondary_y=True)
            
            fig2.update_layout(**layout_motec)
            fig2.update_xaxes(showspikes=True, spikemode="across", spikecolor="#a0aec0", spikethickness=1, spikesnap="cursor", row=2, col=1, **grid_style)
            fig2.update_xaxes(row=1, col=1, **grid_style)
            fig2.update_yaxes(**grid_style); fig2.update_yaxes(fixedrange=True)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False, "scrollZoom": True})
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("💡 Login/Upload CSV di panel kiri untuk merender Workspace.")