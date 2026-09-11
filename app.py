import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# Configuración de página
st.set_page_config(
    page_title="Pharmadvisor | Business Intelligence Executive",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS ejecutivos y tarjetas KPI estructuradas
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
        font-size: 28px;
        font-weight: bold;
        margin: 0;
    }
    .kpi-section-title {
        color: #0088FF;
        font-size: 15px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 15px;
        margin-bottom: 8px;
        border-bottom: 1px solid rgba(0, 136, 255, 0.3);
        padding-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown("""
    <div class="ph-header">
        <div>
            <h1 class="ph-title">E Metrics BI Executive</h1>
            <span style="color: #9AA5B1; font-size: 13px;">Inteligencia de Prescripción Mipres & Auditoría de Visitas Pharmadvisor</span>
        </div>
        <div style="text-align: right;">
            <span style="color: #E6007E; font-weight: bold; font-size: 20px;">Pharm<span style="color: #FFFFFF;">ADVISOR</span></span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS (MIPRES Y VISITAS) ---
@st.cache_data
def cargar_datos_mipres(uploaded_file=None):
    source = uploaded_file if uploaded_file is not None else 'Base Mipres.xlsx'
    if not os.path.exists('Base Mipres.xlsx') and uploaded_file is None:
        return None
    try:
        df = pd.read_excel(source, sheet_name='Consolidado', header=1)
        df.columns = [str(c) for c in df.columns]
        for col in df.columns:
            if '2025' in col or '2026' in col or 'Total general' in col or 'Médicos Visitados' in col:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        return None

@st.cache_data
def cargar_datos_visitas(uploaded_file=None):
    excel_source = uploaded_file if uploaded_file is not None else 'listado_visitas_2026-09-07_11-44-08.xlsx'
    if not os.path.exists('listado_visitas_2026-09-07_11-44-08.xlsx') and uploaded_file is None:
        return None
    try:
        xls = pd.ExcelFile(excel_source)
        df = pd.read_excel(excel_source, sheet_name=xls.sheet_names[0])
        
        df['Torta_GCH'] = df['Pareto institución'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto GCH', 'Pareto Allergy'] else 'Inst. No Pareto')
        df['Torta_Allergy'] = df['Torta_GCH']
        df['Torta_Comb'] = df['Torta_GCH']
        
        def bin_ranking(val):
            return '1. Top Institución'
        df['Ranking_Bin_GCH'] = '1. General'
        df['Ranking_Bin_Allergy'] = '1. General'
        df['Ind Frecuencia médico'] = 1.0 # Indicador base
        df['Institución 1.1'] = df['Institución 1']
        
        return df
    except Exception as e:
        return None

# --- CARGADORES EN BARRA LATERAL ---
st.sidebar.subheader("Carga de Archivos")
uploaded_visitas = st.sidebar.file_uploader("Cargar Listado Visitas (Excel)", type=["xlsx"], key="visitas_up")
uploaded_mipres = st.sidebar.file_uploader("Cargar Base Mipres (Excel)", type=["xlsx"], key="mipres_up")

df_frec = cargar_datos_visitas(uploaded_visitas)
df_mipres = cargar_datos_mipres(uploaded_mipres)

# --- SELECTOR DE MERCADO ---
st.sidebar.markdown("---")
st.sidebar.subheader("Selección de Mercado")
mercado_seleccionado = st.sidebar.selectbox(
    "Línea Estratégica:",
    options=["Growth (GCH)", "Allergy", "Consolidado Total (GCH + Allergy)"],
    index=0
)

if mercado_seleccionado == "Growth (GCH)":
    col_vol_2026 = '2026'
    col_pareto = 'Pareto GCH'
    col_visita = 'Se visita Growth?'
elif mercado_seleccionado == "Allergy":
    col_vol_2026 = '2026.1'
    col_pareto = 'Pareto Allergy'
    col_visita = 'Se visita Allergy?'
else:
    col_vol_2026 = 'Vol_Consolidado'
    col_pareto = 'Pareto_Consolidado'
    col_visita = 'Visita_Consolidado'

tab_mipres, tab_visitas, tab_cualitativa = st.tabs([
    "📊 Inteligencia Mipres & Oportunidades", 
    "📈 Auditoría de Visitas & Paretización", 
    "🔎 Auditoría Cualitativa & Ventas"
])

# =========================================================================
# PESTAÑA 1: INTELIGENCIA MIPRES & OPORTUNIDADES COMERCIALES
# =========================================================================
with tab_mipres:
    st.subheader(f"Tablero Estratégico y Potencial de Mercado - Línea {mercado_seleccionado} (Base Mipres)")
    
    if df_mipres is not None:
        if mercado_seleccionado == "Consolidado Total (GCH + Allergy)":
            df_mipres['Vol_Consolidado'] = df_mipres['2026'].fillna(0) + df_mipres['2026.1'].fillna(0)
            
            def is_pareto_cons(row):
                pg = str(row.get('Pareto GCH', ''))
                pa = str(row.get('Pareto Allergy', ''))
                if 'Sí' in pg or 'Sí' in pa: return 'Sí'
                elif 'No está en' in pg and 'No está en' in pa: return 'No aplica'
                else: return 'No'
            df_mipres['Pareto_Consolidado'] = df_mipres.apply(is_pareto_cons, axis=1)

            def is_visita_cons(row):
                vg = str(row.get('Se visita Growth?', ''))
                va = str(row.get('Se visita Allergy?', ''))
                if 'Sí' in vg or 'Sí' in va: return 'Sí'
                return 'No'
            df_mipres['Visita_Consolidado'] = df_mipres.apply(is_visita_cons, axis=1)

        st.sidebar.markdown("---")
        st.sidebar.subheader("Filtros Estratégicos Mipres")
        regiones_mipres = sorted(df_mipres['Región'].dropna().unique()) if 'Región' in df_mipres.columns else []
        selected_regiones = st.sidebar.multiselect("Región Mipres", options=regiones_mipres, default=regiones_mipres, key="reg_mipres")
        
        df_mipres_filtered = df_mipres[df_mipres['Región'].isin(selected_regiones)] if 'Región' in df_mipres.columns else df_mipres
        
        if col_pareto in df_mipres_filtered.columns:
            if mercado_seleccionado == "Consolidado Total (GCH + Allergy)":
                df_mercado_valido = df_mipres_filtered[df_mipres_filtered[col_pareto] != 'No aplica']
            else:
                df_mercado_valido = df_mipres_filtered[~df_mipres_filtered[col_pareto].astype(str).str.contains('No está en', case=False, na=False)]
        else:
            df_mercado_valido = df_mipres_filtered
            
        total_mercado_valido = len(df_mercado_valido)
        
        if col_pareto in df_mercado_valido.columns and col_visita in df_mercado_valido.columns:
            df_pareto_only = df_mercado_valido[df_mercado_valido[col_pareto] == 'Sí']
            total_pareto = len(df_pareto_only)
            pct_pareto_sobre_total = (total_pareto / total_mercado_valido * 100) if total_mercado_valido > 0 else 0
            
            pareto_visitadas = len(df_pareto_only[df_pareto_only[col_visita] == 'Sí'])
            pareto_no_visitadas = len(df_pareto_only[df_pareto_only[col_visita] == 'No'])
            pct_no_visitadas_pareto = (pareto_no_visitadas / total_pareto * 100) if total_pareto > 0 else 0
            
            df_non_pareto = df_mercado_valido[df_mercado_valido[col_pareto] == 'No']
            non_pareto_visitadas = len(df_non_pareto[df_non_pareto[col_visita] == 'Sí'])
            
            prom_medicos_pareto = df_pareto_only['Médicos Visitados'].mean() if 'Médicos Visitados' in df_mercado_valido.columns else 0
            prom_medicos_non_pareto = df_non_pareto['Médicos Visitados'].mean() if 'Médicos Visitados' in df_mercado_valido.columns else 0
        else:
            total_pareto, pct_pareto_sobre_total, pareto_visitadas, pareto_no_visitadas, pct_no_visitadas_pareto, non_pareto_visitadas, prom_medicos_pareto, prom_medicos_non_pareto = 0, 0, 0, 0, 0, 0, 0, 0

        st.markdown('<div class="kpi-section-title">1. Dimensionamiento del Mercado</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Total Instituciones Válidas", f"{total_mercado_valido:,}")
        col2.metric("Instituciones Pareto", f"{total_pareto:,} ({pct_pareto_sobre_total:.1f}% del mercado)")

        st.markdown('<div class="kpi-section-title">2. Auditoría de Cobertura en Cuentas Pareto</div>', unsafe_allow_html=True)
        col3, col4, col5 = st.columns(3)
        col3.metric("Pareto Visitadas", f"{pareto_visitadas:,}")
        col4.metric("Pareto No Visitadas", f"{pareto_no_visitadas:,}")
        col5.metric("Brecha Pareto (Sin Visita)", f"{pct_no_visitadas_pareto:.1f}%", delta_color="inverse")

        st.markdown('<div class="kpi-section-title">3. Esfuerzo Comercial y Promedio de Médicos Visitados</div>', unsafe_allow_html=True)
        col6, col7, col8 = st.columns(3)
        col6.metric("No Pareto Visitadas", f"{non_pareto_visitadas:,}")
        col7.metric("Prom. Médicos Visitados (Pareto)", f"{prom_medicos_pareto:.1f}")
        col8.metric("Prom. Médicos Visitados (No Pareto)", f"{prom_medicos_non_pareto:.1f}")

        st.markdown("---")
        st.subheader(f"🎯 Top 20 Instituciones Pareto de Alto Volumen SIN Visita ({mercado_seleccionado})")
        if col_pareto in df_mipres_filtered.columns and col_visita in df_mipres_filtered.columns:
            df_brecha_pareto = df_mipres_filtered[
                (df_mipres_filtered[col_pareto] == 'Sí') & 
                (df_mipres_filtered[col_visita] == 'No')
            ].sort_values(by=col_vol_2026, ascending=False, na_position='last').head(20)
            
            if not df_brecha_pareto.empty:
                fig_brecha = px.bar(
                    df_brecha_pareto, x='Prestador', y=col_vol_2026, text=col_vol_2026,
                    template='plotly_dark', title=f"<b>Top 20 Potencial en Instituciones Pareto No Visitadas ({mercado_seleccionado})</b>",
                    color_discrete_sequence=['#E6007E']
                )
                fig_brecha.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=11)
                fig_brecha.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=480, xaxis={'tickangle': -35}, yaxis_title="Volumen Semestral Mipres (2026 H1)", margin=dict(t=50, b=130, l=40, r=20))
                st.plotly_chart(fig_brecha, use_container_width=True)

        st.markdown("---")
        st.subheader(f"📊 Top 20 Instituciones por Volumen Mipres y su Estatus de Visita ({mercado_seleccionado})")
        if col_vol_2026 in df_mipres_filtered.columns and col_visita in df_mipres_filtered.columns:
            df_cruce = df_mipres_filtered.sort_values(by=col_vol_2026, ascending=False, na_position='last').head(20).copy()
            df_cruce['Estatus Visita Pharmadvisor'] = df_cruce[col_visita].apply(lambda x: 'Visitada' if str(x).strip().lower() == 'sí' else 'No Visitada')
            
            fig_cruce = px.bar(
                df_cruce, x='Prestador', y=col_vol_2026, color='Estatus Visita Pharmadvisor', text=col_vol_2026,
                template='plotly_dark', title=f"<b>Top 20 Volumen H1 2026 y Cobertura Comercial Pharmadvisor</b>",
                color_discrete_map={'Visitada': '#0088FF', 'No Visitada': '#E6007E'}
            )
            fig_cruce.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=10)
            fig_cruce.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=500, xaxis={'tickangle': -35}, yaxis_title="Volumen H1 2026", margin=dict(t=50, b=140, l=40, r=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_cruce, use_container_width=True)

        st.markdown("##### Auditoría Completa de Oportunidades Mipres")
        st.dataframe(df_mipres_filtered, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Por favor carga el archivo 'Base Mipres.xlsx' mediante la barra lateral.")

# =========================================================================
# PESTAÑA 2: AUDITORÍA DE VISITAS & PARETIZACIÓN
# =========================================================================
with tab_visitas:
    st.subheader("Auditoría Comercial y Frecuencia de Visita (Pharmadvisor)")
    if df_frec is not None:
        st.markdown(f"<span style='color: #9AA5B1; font-size: 15px;'>Mostrando análisis para <b>{len(df_frec):,}</b> registros de visitas cargados.</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("Distribución de Visitas por Tipo de Clasificación Institucional")
        
        grouped = df_frec.groupby('Pareto institución')['Cod. visita'].count().reset_index()
        grouped.columns = ['Clasificación', 'Visitas']
        fig_pie = px.pie(grouped, names='Clasificación', values='Visitas', hole=0.5, template='plotly_dark', color_discrete_sequence=['#0088FF', '#E6007E', '#7B2CBF'])
        fig_pie.update_traces(textinfo='percent+value', textposition='inside')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("⚠️ No se encontró el archivo de visitas. Súbelo mediante la barra lateral.")

# =========================================================================
# PESTAÑA 3: AUDITORÍA CUALITATIVA & VENTAS (CON DATOS REALES DE COMENTARIOS)
# =========================================================================
with tab_cualitativa:
    st.subheader("🔎 Auditoría Cualitativa: Detección de Copy-Paste en Comentarios de Visitas")
    st.markdown("<span style='color: #9AA5B1;'>Análisis de duplicidad de textos, frases repetidas y calidad de registro de la fuerza de ventas basado en el archivo de visitas cargado.</span>", unsafe_allow_html=True)
    st.markdown("---")

    if df_frec is not None:
        df_frec['Comentario_Clean'] = df_frec['Comentario'].astype(str).str.strip().str.lower()
        df_frec['Comentario_Clean'] = df_frec['Comentario_Clean'].apply(lambda x: re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', x)))
        
        total_visitas_q = len(df_frec)
        rep_dup = df_frec.groupby('Representante')['Comentario_Clean'].apply(lambda x: (x.duplicated()).sum()).reset_index(name='Duplicados')
        rep_tot = df_frec.groupby('Representante')['Comentario_Clean'].count().reset_index(name='Total')
        rep_metrics = pd.merge(rep_tot, rep_dup)
        rep_metrics['Pct_CopyPaste'] = (rep_metrics['Duplicados'] / rep_metrics['Total']) * 100
        
        global_dup_count = rep_metrics['Duplicados'].sum()
        global_total_count = rep_metrics['Total'].sum()
        global_pct_cp = (global_dup_count / global_total_count) * 100 if global_total_count > 0 else 0

        col_qc1, col_qc2, col_qc3 = st.columns(3)
        col_qc1.metric("Índice Global de Duplicidad (Copy-Paste)", f"{global_pct_cp:.1f}%")
        col_qc2.metric("Comentarios Analizados", f"{global_total_count:,}")
        col_qc3.metric("Comentarios Duplicados Detectados", f"{global_dup_count:,}")

        st.markdown("---")
        st.subheader("📊 Porcentaje de Comentarios Repetidos (Copy-Paste) por Representante")
        
        fig_rep_cp = px.bar(
            rep_metrics.sort_values(by='Pct_CopyPaste', ascending=False),
            x='Representante', y='Pct_CopyPaste', text='Pct_CopyPaste',
            template='plotly_dark', title="<b>Índice de Copy-Paste por Representante</b>",
            color='Pct_CopyPaste', color_continuous_scale=['#0088FF', '#E6007E']
        )
        fig_rep_cp.update_traces(texttemplate='%{text:.1f}%', textposition='outside', textfont_size=10)
        fig_rep_cp.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=480, xaxis={'tickangle': -35}, yaxis_title="% Duplicidad Interna", margin=dict(t=50, b=140, l=40, r=20))
        st.plotly_chart(fig_rep_cp, use_container_width=True)

        st.markdown("##### Muestra de Comentarios y Objetivos Registrados")
        st.dataframe(df_frec[['Representante', 'Fecha visita', 'Institución 1', 'Objetivo', 'Comentario']].head(15), use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Carga el listado detallado de visitas en la barra lateral para procesar la auditoría cualitativa con datos reales.")
