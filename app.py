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

# --- CARGADORES DE LOS 3 ARCHIVOS EN BARRA LATERAL ---
st.sidebar.subheader("Carga de Archivos")
uploaded_frec = st.sidebar.file_uploader("1. Indicador Frecuencia (Pestaña 2)", type=["xlsx"], key="frec_up")
uploaded_mipres = st.sidebar.file_uploader("2. Base Mipres (Pestaña 1)", type=["xlsx"], key="mipres_up")
uploaded_detallado = st.sidebar.file_uploader("3. Detalle Visitas/Comentarios (Pestaña 3)", type=["xlsx"], key="det_up")

# --- FUNCIONES DE CARGA ---
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
def cargar_datos_frecuencia(uploaded_file=None):
    excel_source = uploaded_file if uploaded_file is not None else 'Indicador_frecuencia_medicos.xlsx'
    if not os.path.exists('Indicador_frecuencia_medicos.xlsx') and uploaded_file is None:
        return None
    try:
        xls = pd.ExcelFile(excel_source)
        df = pd.read_excel(excel_source, sheet_name=xls.sheet_names[0])
        df['Torta_GCH'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto GCH'] else 'Inst. No Pareto')
        df['Torta_Allergy'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto Allergy'] else 'Inst. No Pareto')
        df['Torta_Comb'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto GCH', 'Pareto Allergy'] else 'Inst. No Pareto')
        
        def bin_ranking(val):
            try:
                v = float(val)
                if v <= 50: return '1. Top 50'
                elif v <= 200: return '2. 51 - 200'
                elif v <= 500: return '3. 201 - 500'
                elif v <= 1000: return '4. 501 - 1000'
                else: return '5. 1000+'
            except:
                return '6. Sin Ranking / No Cruza'

        if 'Ranking GCH' in df.columns:
            df['Ranking_Bin_GCH'] = df['Ranking GCH'].apply(bin_ranking)
        if 'Ranking Allergy' in df.columns:
            df['Ranking_Bin_Allergy'] = df['Ranking Allergy'].apply(bin_ranking)
        return df
    except Exception as e:
        return None

@st.cache_data
def cargar_datos_detallado(uploaded_file=None):
    excel_source = uploaded_file if uploaded_file is not None else 'listado_visitas_2026-09-07_11-44-08.xlsx'
    if not os.path.exists('listado_visitas_2026-09-07_11-44-08.xlsx') and uploaded_file is None:
        return None
    try:
        xls = pd.ExcelFile(excel_source)
        df = pd.read_excel(excel_source, sheet_name=xls.sheet_names[0])
        return df
    except Exception as e:
        return None

df_mipres = cargar_datos_mipres(uploaded_mipres)
df_frec = cargar_datos_frecuencia(uploaded_frec)
df_det = cargar_datos_detallado(uploaded_detallado)

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
        st.warning("⚠️ Por favor carga el archivo 'Base Mipres.xlsx' mediante el segundo cargador en la barra lateral.")

# =========================================================================
# PESTAÑA 2: AUDITORÍA DE VISITAS & PARETIZACIÓN (INDICADOR FRECUENCIA)
# =========================================================================
with tab_visitas:
    st.subheader("Auditoría Comercial y Frecuencia de Visita (Pharmadvisor)")
    if df_frec is not None:
        distritos_disponibles = sorted(df_frec['Distrito'].dropna().unique()) if 'Distrito' in df_frec.columns else []
        selected_distritos = st.sidebar.multiselect("Distrito", options=distritos_disponibles, default=distritos_disponibles, key="dist_ph")
        
        df_filtered = df_frec[df_frec['Distrito'].isin(selected_distritos)] if 'Distrito' in df_frec.columns else df_frec
        
        st.markdown(f"<span style='color: #9AA5B1; font-size: 15px;'>Mostrando análisis para <b>{len(df_filtered):,}</b> registros médicos seleccionados.</span>", unsafe_allow_html=True)
        st.markdown("---")

        st.subheader("Distribución de Médicos por Tipo de Clasificación Institucional (Pareto vs. No Pareto)")
        col1, col2, col3 = st.columns(3)
        color_map = {'Inst. Pareto': '#0088FF', 'Inst. No Pareto': '#E6007E'}

        def estilizar_grafica_con_cantidad(df_data, titulo, col_categoria):
            if col_categoria not in df_data.columns or 'Código' not in df_data.columns: return px.pie(title=titulo)
            grouped = df_data.groupby(col_categoria)['Código'].count().reset_index()
            grouped.columns = ['Categoría', 'Médicos']
            fig = px.pie(grouped, names='Categoría', values='Médicos', hole=0.5, title=titulo, color='Categoría', color_discrete_map=color_map, template='plotly_dark')
            fig.update_traces(textinfo='percent+value', textposition='inside', insidetextorientation='horizontal', textfont_size=12)
            fig.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=370, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5), margin=dict(t=50, b=60, l=20, r=20))
            return fig

        with col1:
            st.plotly_chart(estilizar_grafica_con_cantidad(df_filtered, "<b>1. Mercado Growth (GCH)</b>", 'Torta_GCH'), use_container_width=True)
        with col2:
            st.plotly_chart(estilizar_grafica_con_cantidad(df_filtered, "<b>2. Mercado Allergy</b>", 'Torta_Allergy'), use_container_width=True)
        with col3:
            st.plotly_chart(estilizar_grafica_con_cantidad(df_filtered, "<b>3. Mercados Combinados</b>", 'Torta_Comb'), use_container_width=True)
    else:
        st.warning("⚠️ Por favor carga el archivo 'Indicador Frecuencia' en el primer cargador de la barra lateral.")

# =========================================================================
# PESTAÑA 3: AUDITORÍA CUALITATIVA & VENTAS (LISTADO DETALLADO VISITAS)
# =========================================================================
with tab_cualitativa:
    st.subheader("🔎 Auditoría Cualitativa: Detección de Copy-Paste en Comentarios de Visitas")
    st.markdown("<span style='color: #9AA5B1;'>Análisis de duplicidad de textos, frases repetidas y calidad de registro basado en el listado detallado de visitas cargado.</span>", unsafe_allow_html=True)
    st.markdown("---")

    if df_det is not None:
        if 'Comentario' in df_det.columns and 'Representante' in df_det.columns:
            df_det['Comentario_Clean'] = df_det['Comentario'].astype(str).str.strip().str.lower()
            df_det['Comentario_Clean'] = df_det['Comentario_Clean'].apply(lambda x: re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', x)))
            
            rep_dup = df_det.groupby('Representante')['Comentario_Clean'].apply(lambda x: (x.duplicated()).sum()).reset_index(name='Duplicados')
            rep_tot = df_det.groupby('Representante')['Comentario_Clean'].count().reset_index(name='Total')
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
            display_cols = [c for c in ['Representante', 'Fecha visita', 'Institución 1', 'Objetivo', 'Comentario'] if c in df_det.columns]
            st.dataframe(df_det[display_cols].head(15), use_container_width=True, hide_index=True)
        else:
            st.error("El archivo cargado no contiene las columnas requeridas ('Representante' y 'Comentario').")
    else:
        st.warning("⚠️ Por favor carga el **Listado Detallado de Visitas** en el tercer cargador de la barra lateral para procesar la auditoría cualitativa.")
