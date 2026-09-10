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

# Carga segura
@st.cache_data
def cargar_analisis_pareto(uploaded_file=None):
    excel_source = uploaded_file if uploaded_file is not None else 'Indicador_frecuencia_medicos.xlsx'
    if not os.path.exists(excel_path := 'Indicador_frecuencia_medicos.xlsx') and uploaded_file is None:
        return None

    xls = pd.ExcelFile(excel_source)
    sheet_name = xls.sheet_names[0]
    df = pd.read_excel(excel_source, sheet_name=sheet_name)
    
    # Clasificación basada en la columna Pareto 1
    df['Torta_GCH'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto GCH'] else 'Inst. No Pareto')
    df['Torta_Allergy'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto Allergy'] else 'Inst. No Pareto')
    df['Torta_Comb'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto GCH', 'Pareto Allergy'] else 'Inst. No Pareto')
    
    return df

uploaded_file = st.sidebar.file_uploader("Cargar Indicador Frecuencia (Excel)", type=["xlsx"])
df_frec = cargar_analisis_pareto(uploaded_file)

if df_frec is not None:
    st.subheader("Distribución de Médicos por Tipo de Clasificación Institucional (Pareto vs. No Pareto)")

    col1, col2, col3 = st.columns(3)
    color_map = {'Inst. Pareto': '#0088FF', 'Inst. No Pareto': '#E6007E'}

    def estilizar_grafica(df_data, titulo):
        fig = px.pie(
            df_data, names='Categoría', values='Médicos', hole=0.5,
            title=titulo, color='Categoría', color_discrete_map=color_map, template='plotly_dark'
        )
        # Forzar texto horizontal, claro y legible sin inclinaciones
        fig.update_traces(
            textinfo='percent+label',
            textposition='inside',
            insidetextorientation='horizontal',
            textfont_size=13
        )
        fig.update_layout(
            paper_bgcolor='#1C202C', 
            plot_bgcolor='#2D3346', 
            height=380, 
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=50, b=50, l=20, r=20)
        )
        return fig

    with col1:
        counts_gch = df_frec['Torta_GCH'].value_counts().reset_index()
        counts_gch.columns = ['Categoría', 'Médicos']
        st.plotly_chart(estilizar_grafica(counts_gch, "<b>1. Mercado Growth (GCH)</b>"), use_container_width=True)

    with col2:
        counts_all = df_frec['Torta_Allergy'].value_counts().reset_index()
        counts_all.columns = ['Categoría', 'Médicos']
        st.plotly_chart(estilizar_grafica(counts_all, "<b>2. Mercado Allergy</b>"), use_container_width=True)

    with col3:
        counts_comb = df_frec['Torta_Comb'].value_counts().reset_index()
        counts_comb.columns = ['Categoría', 'Médicos']
        st.plotly_chart(estilizar_grafica(counts_comb, "<b>3. Mercados Combinados</b>"), use_container_width=True)
else:
    st.warning("⚠️ No se encontró el archivo 'Indicador_frecuencia_medicos.xlsx'. Súbelo a la raíz del repositorio o cárgalo en la barra lateral.")
