import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración de página
st.set_page_config(
    page_title="Pharmadvisor | Pareto Distribution BI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS Pharmadvisor
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
    </style>
""", unsafe_allow_html=True)

# Encabezado visual
st.markdown("""
    <div class="ph-header">
        <div>
            <h1 class="ph-title">E Metrics BI Executive</h1>
            <span style="color: #9AA5B1; font-size: 13px;">Distribución de Médicos según Clasificación Institucional MIPRES</span>
        </div>
        <div style="text-align: right;">
            <span style="color: #E6007E; font-weight: bold; font-size: 20px;">Pharm<span style="color: #FFFFFF;">ADVISOR</span></span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Carga automática de datos con cache
@st.cache_data
def cargar_datos_locales():
    file_mipres = 'Base Mipres.xlsx'
    file_frec = 'Indicador_frecuencia_medicos.xlsx'
    
    if os.path.exists(file_mipres) and os.path.exists(file_frec):
        df_mipres_raw = pd.read_excel(file_mipres, sheet_name='Consolidado')
        df_mipres_raw.columns = df_mipres_raw.iloc[0]
        df_mipres = df_mipres_raw.iloc[1:].copy()

        cols_mipres = ['col_0', 'Departamento', 'Prestador', 'GCH_2025', 'GCH_2026', 'GCH_Total', 'GCH_Región', 'GCH_Pareto', 
                       'GCH_cc', 'GCH_Ranking', 'Se_visita_Growth', 'Allergy_2025', 'Allergy_2026', 'Allergy_Total', 
                       'Allergy_Región', 'Allergy_Pareto', 'Allergy_cc', 'Allergy_Ranking', 'Se_visita_Allergy', 
                       'CC', 'Pareto_final', 'Medicos_Visitados', 'Pareto_GCH_final', 'Pareto_Allergy_final']
        df_mipres.columns = cols_mipres

        df_frec = pd.read_excel(file_frec, sheet_name='Indicador_frecuencia_medico')
        return df_mipres, df_frec
    return None, None

df_mipres, df_frec = cargar_datos_locales()

# Selector manual en barra lateral por si no existen los archivos locales
if df_mipres is None or df_frec is None:
    st.sidebar.header("Carga de Archivos")
    uploaded_mipres = st.sidebar.file_uploader("Cargar Base MIPRES (Excel)", type=["xlsx"])
    uploaded_frec = st.sidebar.file_uploader("Cargar Indicador Frecuencia (Excel)", type=["xlsx"])
    
    if uploaded_mipres and uploaded_frec:
        df_mipres_raw = pd.read_excel(uploaded_mipres, sheet_name='Consolidado')
        df_mipres_raw.columns = df_mipres_raw.iloc[0]
        df_mipres = df_mipres_raw.iloc[1:].copy()

        cols_mipres = ['col_0', 'Departamento', 'Prestador', 'GCH_2025', 'GCH_2026', 'GCH_Total', 'GCH_Región', 'GCH_Pareto', 
                       'GCH_cc', 'GCH_Ranking', 'Se_visita_Growth', 'Allergy_2025', 'Allergy_2026', 'Allergy_Total', 
                       'Allergy_Región', 'Allergy_Pareto', 'Allergy_cc', 'Allergy_Ranking', 'Se_visita_Allergy', 
                       'CC', 'Pareto_final', 'Medicos_Visitados', 'Pareto_GCH_final', 'Pareto_Allergy_final']
        df_mipres.columns = cols_mipres

        df_frec = pd.read_excel(uploaded_frec, sheet_name='Indicador_frecuencia_medico')

if df_mipres is not None and df_frec is not None:
    st.subheader("Distribución de Médicos por Tipo de Institución (Pareto vs. No Pareto)")

    # Procesamiento para mapeo de instituciones
    df_mipres_grouped = df_mipres.groupby('CC').agg({
        'Pareto_GCH_final': 'first',
        'Pareto_Allergy_final': 'first',
        'Pareto_final': 'first'
    }).reset_index()

    mipres_map = df_mipres_grouped.set_index('CC').to_dict('index')

    df_inst1 = df_frec[['Código', 'Línea', 'Institución 1.1']].rename(columns={'Institución 1.1': 'CC_Matched'})
    df_inst2 = df_frec[['Código', 'Línea', 'Institución 2']].rename(columns={'Institución 2': 'CC_Matched'})

    inst_all = pd.concat([df_inst1, df_inst2])
    inst_all = inst_all[~inst_all['CC_Matched'].isin(['0', '', None]) & inst_all['CC_Matched'].notna()].drop_duplicates(subset=['Código', 'CC_Matched'])

    inst_all['Pareto_GCH'] = inst_all['CC_Matched'].apply(lambda x: mipres_map.get(x, {}).get('Pareto_GCH_final', 'No'))
    inst_all['Pareto_Allergy'] = inst_all['CC_Matched'].apply(lambda x: mipres_map.get(x, {}).get('Pareto_Allergy_final', 'No'))
    inst_all['Pareto_Final'] = inst_all['CC_Matched'].apply(lambda x: mipres_map.get(x, {}).get('Pareto_final', 'No ambas'))

    doc_summary = inst_all.groupby('Código').agg(
        Es_Pareto_GCH=('Pareto_GCH', lambda x: 'Inst. Pareto' if 'Sí' in list(x) else 'Inst. No Pareto'),
        Es_Pareto_Allergy=('Pareto_Allergy', lambda x: 'Inst. Pareto' if 'Sí' in list(x) else 'Inst. No Pareto'),
        Es_Pareto_Combinado=('Pareto_Final', lambda x: 'Inst. Pareto' if any(k in str(list(x)) for k in ['Pareto Ambas', 'Pareto GCH', 'Pareto Allergy']) else 'Inst. No Pareto')
    ).reset_index()

    col1, col2, col3 = st.columns(3)
    color_map = {'Inst. No Pareto': '#E6007E', 'Inst. Pareto': '#0088FF'}

    with col1:
        counts_gch = doc_summary['Es_Pareto_GCH'].value_counts().reset_index()
        counts_gch.columns = ['Categoría', 'Médicos']
        fig_gch = px.pie(
            counts_gch, names='Categoría', values='Médicos', hole=0.4,
            title="<b>1. Mercado Growth (GCH)</b>",
            color='Categoría', color_discrete_map=color_map, template='plotly_dark'
        )
        fig_gch.update_traces(textinfo='percent+label', textfont_size=13)
        fig_gch.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=360, showlegend=False)
        st.plotly_chart(fig_gch, use_container_width=True)

    with col2:
        counts_all = doc_summary['Es_Pareto_Allergy'].value_counts().reset_index()
        counts_all.columns = ['Categoría', 'Médicos']
        fig_all = px.pie(
            counts_all, names='Categoría', values='Médicos', hole=0.4,
            title="<b>2. Mercado Allergy</b>",
            color='Categoría', color_discrete_map=color_map, template='plotly_dark'
        )
        fig_all.update_traces(textinfo='percent+label', textfont_size=13)
        fig_all.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=360, showlegend=False)
        st.plotly_chart(fig_all, use_container_width=True)

    with col3:
        counts_comb = doc_summary['Es_Pareto_Combinado'].value_counts().reset_index()
        counts_comb.columns = ['Categoría', 'Médicos']
        fig_comb = px.pie(
            counts_comb, names='Categoría', values='Médicos', hole=0.4,
            title="<b>3. Mercados Combinados</b>",
            color='Categoría', color_discrete_map=color_map, template='plotly_dark'
        )
        fig_comb.update_traces(textinfo='percent+label', textfont_size=13)
        fig_comb.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=360, showlegend=False)
        st.plotly_chart(fig_comb, use_container_width=True)

else:
    st.info("Carga los archivos Excel 'Base Mipres.xlsx' e 'Indicador_frecuencia_medicos.xlsx' desde la barra lateral o asegúrate de que estén subidos en la raíz del repositorio de GitHub.")
