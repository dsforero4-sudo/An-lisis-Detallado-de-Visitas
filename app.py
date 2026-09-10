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

# Estilos CSS
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

# Encabezado
st.markdown("""
    <div class="ph-header">
        <div>
            <h1 class="ph-title">E Metrics BI Executive</h1>
            <span style="color: #9AA5B1; font-size: 13px;">Distribución de Médicos según Clasificación Institucional (Pareto 1)</span>
        </div>
        <div style="text-align: right;">
            <span style="color: #E6007E; font-weight: bold; font-size: 20px;">Pharm<span style="color: #FFFFFF;">ADVISOR</span></span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Carga segura con alternativa de uploader si no está el archivo en el repo
@st.cache_data
def cargar_analisis_pareto(uploaded_file=None):
    if uploaded_file is not None:
        excel_source = uploaded_file
    else:
        excel_path = 'Indicador_frecuencia_medicos.xlsx'
        if not os.path.exists(excel_path):
            return None
        excel_source = excel_path

    xls = pd.ExcelFile(excel_source)
    sheet_name = xls.sheet_names[0]
    df = pd.read_excel(excel_source, sheet_name=sheet_name)
    
    # Clasificación basada en la columna Pareto 1
    df['Torta_GCH'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto GCH'] else 'Inst. No Pareto')
    df['Torta_Allergy'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto Allergy'] else 'Inst. No Pareto')
    df['Torta_Comb'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto GCH', 'Pareto Allergy'] else 'Inst. No Pareto')
    
    return df

# Panel lateral para carga manual de respaldo si el archivo no está en GitHub
uploaded_file = st.sidebar.file_uploader("Cargar Indicador Frecuencia (Excel)", type=["xlsx"])

df_frec = cargar_analisis_pareto(uploaded_file)

if df_frec is not None:
    st.subheader("Distribución de Médicos por Tipo de Clasificación Institucional (Pareto vs. No Pareto)")

    col1, col2, col3 = st.columns(3)
    color_map = {'Inst. Pareto': '#0088FF', 'Inst. No Pareto': '#E6007E'}

    with col1:
        counts_gch = df_frec['Torta_GCH'].value_counts().reset_index()
        counts_gch.columns = ['Categoría', 'Médicos']
        fig1 = px.pie(
            counts_gch, names='Categoría', values='Médicos', hole=0.4,
            title="<b>1. Mercado Growth (GCH)</b>",
            color='Categoría', color_discrete_map=color_map, template='plotly_dark'
        )
        fig1.update_traces(textinfo='percent+label', textfont_size=13)
        fig1.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=360, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        counts_all = df_frec['Torta_Allergy'].value_counts().reset_index()
        counts_all.columns = ['Categoría', 'Médicos']
        fig2 = px.pie(
            counts_all, names='Categoría', values='Médicos', hole=0.4,
            title="<b>2. Mercado Allergy</b>",
            color='Categoría', color_discrete_map=color_map, template='plotly_dark'
        )
        fig2.update_traces(textinfo='percent+label', textfont_size=13)
        fig2.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=360, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        counts_comb = df_frec['Torta_Comb'].value_counts().reset_index()
        counts_comb.columns = ['Categoría', 'Médicos']
        fig3 = px.pie(
            counts_comb, names='Categoría', values='Médicos', hole=0.4,
            title="<b>3. Mercados Combinados</b>",
            color='Categoría', color_discrete_map=color_map, template='plotly_dark'
        )
        fig3.update_traces(textinfo='percent+label', textfont_size=13)
        fig3.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=360, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("⚠️ No se encontró el archivo 'Indicador_frecuencia_medicos.xlsx' en el repositorio de GitHub. Por favor, súbelo a la raíz de tu proyecto o cárgalo manualmente usando el selector de archivos en la barra lateral.")
