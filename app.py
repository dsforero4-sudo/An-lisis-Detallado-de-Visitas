import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración de página
st.set_page_config(
    page_title="Pharmadvisor | Pareto Distribution BI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS ejecutivos
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
            <span style="color: #9AA5B1; font-size: 13px;">Auditoría, Cobertura e Índice de Frecuencia de Visita Médica</span>
        </div>
        <div style="text-align: right;">
            <span style="color: #E6007E; font-weight: bold; font-size: 20px;">Pharm<span style="color: #FFFFFF;">ADVISOR</span></span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Carga segura de datos
@st.cache_data
def cargar_datos(uploaded_file=None):
    excel_source = uploaded_file if uploaded_file is not None else 'Indicador_frecuencia_medicos.xlsx'
    if not os.path.exists('Indicador_frecuencia_medicos.xlsx') and uploaded_file is None:
        return None

    xls = pd.ExcelFile(excel_source)
    sheet_name = xls.sheet_names[0]
    df = pd.read_excel(excel_source, sheet_name=sheet_name)
    
    # Clasificación institucional Pareto 1
    df['Torta_GCH'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto GCH'] else 'Inst. No Pareto')
    df['Torta_Allergy'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto Allergy'] else 'Inst. No Pareto')
    df['Torta_Comb'] = df['Pareto 1'].apply(lambda x: 'Inst. Pareto' if str(x) in ['Pareto Ambas', 'Pareto GCH', 'Pareto Allergy'] else 'Inst. No Pareto')
    
    return df

uploaded_file = st.sidebar.file_uploader("Cargar Indicador Frecuencia (Excel)", type=["xlsx"])
df_frec = cargar_datos(uploaded_file)

if df_frec is not None:
    # --- FILTROS EN CASCADA (MULTISELECCIÓN) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtros Comerciales")

    # 1. Distrito
    distritos_disponibles = sorted(df_frec['Distrito'].dropna().unique())
    selected_distritos = st.sidebar.multiselect("Distrito", options=distritos_disponibles, default=distritos_disponibles)
    
    # Filtrado en cascada para Línea
    df_filtered = df_frec[df_frec['Distrito'].isin(selected_distritos)]
    lineas_disponibles = sorted(df_filtered['Línea'].dropna().unique())
    selected_lineas = st.sidebar.multiselect("Línea", options=lineas_disponibles, default=lineas_disponibles)
    
    # Filtrado en cascada para Categoría
    df_filtered = df_filtered[df_filtered['Línea'].isin(selected_lineas)]
    categorias_disponibles = sorted(df_filtered['Categoría'].dropna().unique())
    selected_categorias = st.sidebar.multiselect("Categoría del Médico", options=categorias_disponibles, default=categorias_disponibles)
    
    # Filtrado en cascada para Representante
    df_filtered = df_filtered[df_filtered['Categoría'].isin(selected_categorias)]
    representantes_disponibles = sorted(df_filtered['Representante'].dropna().unique())
    selected_representantes = st.sidebar.multiselect("Representante", options=representantes_disponibles, default=representantes_disponibles)

    # DataFrame final filtrado
    df_final = df_filtered[df_filtered['Representante'].isin(selected_representantes)]

    total_medicos_filtrados = len(df_final)
    st.markdown(f"<span style='color: #9AA5B1; font-size: 15px;'>Mostrando análisis para <b>{total_medicos_filtrados:,}</b> registros médicos seleccionados.</span>", unsafe_allow_html=True)
    st.markdown("---")

    # --- SECCIÓN 1: DISTRIBUCIÓN POR TIPO DE INSTITUCIÓN (DONAS) ---
    st.subheader("Distribución de Médicos por Tipo de Clasificación Institucional (Pareto vs. No Pareto)")

    col1, col2, col3 = st.columns(3)
    color_map = {'Inst. Pareto': '#0088FF', 'Inst. No Pareto': '#E6007E'}

    def estilizar_grafica_con_cantidad(df_data, titulo, col_categoria):
        grouped = df_data.groupby(col_categoria)['Código'].count().reset_index()
        grouped.columns = ['Categoría', 'Médicos']
        
        fig = px.pie(
            grouped, names='Categoría', values='Médicos', hole=0.5,
            title=titulo, color='Categoría', color_discrete_map=color_map, template='plotly_dark'
        )
        
        fig.update_traces(
            textinfo='percent+value',
            textposition='inside',
            insidetextorientation='horizontal',
            textfont_size=12
        )
        fig.update_layout(
            paper_bgcolor='#1C202C', 
            plot_bgcolor='#2D3346', 
            height=370, 
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            margin=dict(t=50, b=60, l=20, r=20)
        )
        return fig

    with col1:
        st.plotly_chart(estilizar_grafica_con_cantidad(df_final, "<b>1. Mercado Growth (GCH)</b>", 'Torta_GCH'), use_container_width=True)

    with col2:
        st.plotly_chart(estilizar_grafica_con_cantidad(df_final, "<b>2. Mercado Allergy</b>", 'Torta_Allergy'), use_container_width=True)

    with col3:
        st.plotly_chart(estilizar_grafica_con_cantidad(df_final, "<b>3. Mercados Combinados</b>", 'Torta_Comb'), use_container_width=True)

    st.markdown("---")

    # --- SECCIÓN 2: ÍNDICE DE FRECUENCIA PROMEDIO (BARRAS) ---
    st.subheader("Índice de Frecuencia Promedio de Visita: Pareto vs No Pareto")

    col_freq1, col_freq2, col_freq3 = st.columns(3)

    def grafica_frecuencia_barras(df_data, titulo, col_cat):
        freq_df = df_data.groupby(col_cat)['Ind Frecuencia médico'].mean().reset_index()
        freq_df.columns = ['Clasificación', 'Frecuencia Promedio']
        
        fig = px.bar(
            freq_df, x='Clasificación', y='Frecuencia Promedio',
            text='Frecuencia Promedio', color='Clasificación',
            color_discrete_map=color_map, template='plotly_dark',
            title=titulo
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', textfont_size=13)
        fig.update_layout(
            paper_bgcolor='#1C202C',
            plot_bgcolor='#2D3346',
            height=340,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Índice Promedio",
            margin=dict(t=50, b=30, l=20, r=20)
        )
        return fig

    with col_freq1:
        st.plotly_chart(grafica_frecuencia_barras(df_final, "<b>Frecuencia GCH</b>", 'Torta_GCH'), use_container_width=True)

    with col_freq2:
        st.plotly_chart(grafica_frecuencia_barras(df_final, "<b>Frecuencia Allergy</b>", 'Torta_Allergy'), use_container_width=True)

    with col_freq3:
        st.plotly_chart(grafica_frecuencia_barras(df_final, "<b>Frecuencia Combinada</b>", 'Torta_Comb'), use_container_width=True)

else:
    st.warning("⚠️ No se encontró el archivo 'Indicador_frecuencia_medicos.xlsx'. Súbelo a la raíz del repositorio o cárgalo mediante la barra lateral.")
