import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="Pharmadvisor | Brand Performance & MIPRES ROI (V2)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS idénticos al Dashboard Pharmadvisor
st.markdown("""
    <style>
    .stApp { 
        background-color: #2D3346; 
        color: #FFFFFF; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .ph-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 15px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .ph-title {
        color: #E6007E;
        font-size: 30px;
        font-weight: bold;
        margin: 0;
    }
    .kpi-card {
        background-color: #1C202C;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .kpi-label { 
        color: #9AA5B1; 
        font-size: 11px; 
        font-weight: 700; 
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value { 
        color: #FFFFFF; 
        font-size: 28px; 
        font-weight: bold; 
        margin-top: 5px; 
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado visual
st.markdown("""
    <div class="ph-header">
        <div>
            <h1 class="ph-title">Brand Performance & MIPRES ROI Executive</h1>
            <span style="color: #9AA5B1; font-size: 13px;">Efectividad Comercial y Cobertura de Mercado | Pediátricos Danone</span>
        </div>
        <div style="text-align: right;">
            <span style="color: #E6007E; font-weight: bold; font-size: 20px;">Pharm<span style="color: #FFFFFF;">ADVISOR</span></span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.header("Carga de Archivos V2")
file_mipres = st.sidebar.file_uploader("1. Base MIPRES (Excel)", type=["xlsx"])
file_frec = st.sidebar.file_uploader("2. Indicador Frecuencia Médicos (Excel)", type=["xlsx"])

if file_mipres is not None and file_frec is not None:
    # Carga MIPRES
    df_mipres_raw = pd.read_excel(file_mipres, sheet_name='Consolidado')
    df_mipres_raw.columns = df_mipres_raw.iloc[0]
    df_mipres = df_mipres_raw.iloc[1:].copy()

    cols_mipres = ['col_0', 'Departamento', 'Prestador', 'GCH_2025', 'GCH_2026', 'GCH_Total', 'GCH_Región', 'GCH_Pareto', 
                   'GCH_cc', 'GCH_Ranking', 'Se_visita_Growth', 'Allergy_2025', 'Allergy_2026', 'Allergy_Total', 
                   'Allergy_Región', 'Allergy_Pareto', 'Allergy_cc', 'Allergy_Ranking', 'Se_visita_Allergy', 
                   'CC', 'Pareto_final', 'Medicos_Visitados', 'Pareto_GCH_final', 'Pareto_Allergy_final']
    df_mipres.columns = cols_mipres
    for c in ['GCH_2025', 'GCH_2026', 'GCH_Total', 'Allergy_2025', 'Allergy_2026', 'Allergy_Total']:
        df_mipres[c] = pd.to_numeric(df_mipres[c], errors='coerce').fillna(0)

    # Carga Frecuencia
    df_frec = pd.read_excel(file_frec, sheet_name='Indicador_frecuencia_medico')
    cycles = ['2026-1.1', '2026-2.1', '2026-3.1', '2026-4.1', '2026-5.1', '2026-6.1', '2026-7.1']
    df_frec['ciclos_visitados'] = df_frec[cycles].sum(axis=1)

    # Filtros
    f1, f2, f3 = st.columns(3)
    with f1:
        lineas_opt = ["Todas las Líneas"] + list(df_frec['Línea'].dropna().unique())
        sel_linea = st.selectbox("Línea Promocional", lineas_opt)
    with f2:
        reg_opt = ["Todas las Regiones"] + list(df_mipres['GCH_Región'].dropna().unique())
        sel_reg = st.selectbox("Región / Territorio", reg_opt)
    with f3:
        cat_opt = ["Todas las Categorías"] + list(df_frec['Categoría'].dropna().unique())
        sel_cat = st.selectbox("Categoría Médico", cat_opt)

    df_frec_filtered = df_frec.copy()
    if sel_linea != "Todas las Líneas":
        df_frec_filtered = df_frec_filtered[df_frec_filtered['Línea'] == sel_linea]
    if sel_cat != "Todas las Categorías":
        df_frec_filtered = df_frec_filtered[df_frec_filtered['Categoría'] == sel_cat]

    df_mipres_filtered = df_mipres.copy()
    if sel_reg != "Todas las Regiones":
        df_mipres_filtered = df_mipres_filtered[df_mipres_filtered['GCH_Región'] == sel_reg]

    # KPIs Principales
    tot_gch = df_mipres_filtered['GCH_Total'].sum()
    tot_all = df_mipres_filtered['Allergy_Total'].sum()
    tot_docs = df_frec_filtered['Código'].nunique()
    frec_prom = df_frec_filtered['Ind Frecuencia médico'].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-label">MERCADO MIPRES GROWTH</div><div class="kpi-value">${tot_gch:,.0f}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-label">MERCADO MIPRES ALLERGY</div><div class="kpi-value">${tot_all:,.0f}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card"><div class="kpi-label">MÉDICOS EN PANEL</div><div class="kpi-value">{tot_docs:,}</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card"><div class="kpi-label">FRECUENCIA PROMEDIO</div><div class="kpi-value" style="color:#A3FF00;">{frec_prom:.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("###")

    t1, t2 = st.tabs(["📊 BRAND AUDIT & MIPRES ROI", "🎯 TARGETING Y CONSISTENCIA PROMOCIONAL"])

    with t1:
        st.subheader("1. Cobertura de Presupuesto MIPRES (Captura vs. Fuga)")
        c1, c2 = st.columns(2)
        with c1:
            gch_vis = df_mipres_filtered.groupby('Se_visita_Growth')['GCH_Total'].sum().reset_index()
            fig_gch = px.pie(gch_vis, names='Se_visita_Growth', values='GCH_Total', hole=0.5,
                             title="<b>Growth (Fortini/Infatrini): Capturado vs. Sin Visita</b>",
                             color_discrete_map={'Sí': '#A3FF00', 'No': '#E6007E'}, template='plotly_dark')
            fig_gch.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=330)
            st.plotly_chart(fig_gch, use_container_width=True)

        with c2:
            all_vis = df_mipres_filtered.groupby('Se_visita_Allergy')['Allergy_Total'].sum().reset_index()
            fig_all = px.pie(all_vis, names='Se_visita_Allergy', values='Allergy_Total', hole=0.5,
                             title="<b>Allergy (Pepti/Neocate): Capturado vs. Sin Visita</b>",
                             color_discrete_map={'Sí': '#0088FF', 'No': '#E6007E'}, template='plotly_dark')
            fig_all.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=330)
            st.plotly_chart(fig_all, use_container_width=True)

        st.subheader("2. Intensidad de Visita por Especialidad Promocional")
        spec_df = df_frec_filtered.groupby('Especialidad')['Ind Frecuencia médico'].mean().reset_index().sort_values(by='Ind Frecuencia médico', ascending=True).tail(8)
        fig_spec = px.bar(spec_df, y='Especialidad', x='Ind Frecuencia médico', orientation='h',
                          title="<b>Frecuencia Promedio Lograda por Especialidad</b>",
                          color='Ind Frecuencia médico', color_continuous_scale=['#0088FF', '#A3FF00'], template='plotly_dark')
        fig_spec.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=350)
        st.plotly_chart(fig_spec, use_container_width=True)

    with t2:
        st.subheader("3. Consistencia Promocional (Fidelidad de Contacto en 7 Ciclos)")
        cons_df = df_frec_filtered['ciclos_visitados'].value_counts().reset_index()
        cons_df.columns = ['Ciclos Contactados', 'Médicos']
        cons_df['Ciclos Contactados'] = cons_df['Ciclos Contactados'].astype(str) + " Ciclos"
        
        fig_cons = px.bar(cons_df, x='Ciclos Contactados', y='Médicos', color='Médicos',
                          title="<b>Distribución de Regularidad de Visita en 7 Ciclos</b>",
                          color_continuous_scale=['#E6007E', '#0088FF', '#A3FF00'], template='plotly_dark')
        fig_cons.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=350)
        st.plotly_chart(fig_cons, use_container_width=True)

else:
    st.info("Por favor carga los dos archivos Excel en la barra lateral izquierda para desplegar el Tablero de Marca V2.")
