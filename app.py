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
            <span style="color: #9AA5B1; font-size: 13px;">Auditoría, Proporción Institucional e Índice de Frecuencia</span>
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

    distritos_disponibles = sorted(df_frec['Distrito'].dropna().unique())
    selected_distritos = st.sidebar.multiselect("Distrito", options=distritos_disponibles, default=distritos_disponibles)
    
    df_filtered = df_frec[df_frec['Distrito'].isin(selected_distritos)]
    lineas_disponibles = sorted(df_filtered['Línea'].dropna().unique())
    selected_lineas = st.sidebar.multiselect("Línea", options=lineas_disponibles, default=lineas_disponibles)
    
    df_filtered = df_filtered[df_filtered['Línea'].isin(selected_lineas)]
    categorias_disponibles = sorted(df_filtered['Categoría'].dropna().unique())
    selected_categorias = st.sidebar.multiselect("Categoría del Médico", options=categorias_disponibles, default=categorias_disponibles)
    
    df_filtered = df_filtered[df_filtered['Categoría'].isin(selected_categorias)]
    representantes_disponibles = sorted(df_filtered['Representante'].dropna().unique())
    selected_representantes = st.sidebar.multiselect("Representante", options=representantes_disponibles, default=representantes_disponibles)

    df_final = df_filtered[df_filtered['Representante'].isin(selected_representantes)]

    total_medicos_filtrados = len(df_final)
    st.markdown(f"<span style='color: #9AA5B1; font-size: 15px;'>Mostrando análisis para <b>{total_medicos_filtrados:,}</b> registros médicos seleccionados.</span>", unsafe_allow_html=True)
    st.markdown("---")

    color_map = {'Inst. Pareto': '#0088FF', 'Inst. No Pareto': '#E6007E'}

    # Función segura para asegurar integridad de categorías en Plotly
    def asegurar_categorias(df_grouped, col_name, val_col):
        categorias_base = pd.DataFrame({'Clasificación': ['Inst. Pareto', 'Inst. No Pareto']})
        merged = pd.merge(categorias_base, df_grouped, on='Clasificación', how='left').fillna({val_col: 0})
        return merged

    # --- SECCIÓN: PROPORCIÓN INSTITUCIONAL VS MÉDICOS ---
    st.subheader("Análisis Proporcional: Peso de Instituciones vs. Volumen de Médicos")

    col_prop1, col_prop2 = st.columns(2)

    with col_prop1:
        inst_prop = df_final.groupby('Torta_Comb')['Institución 1.1'].nunique().reset_index()
        inst_prop.columns = ['Clasificación', 'Cantidad Instituciones']
        inst_prop = asegurar_categorias(inst_prop, 'Clasificación', 'Cantidad Instituciones')
        
        fig_inst = px.pie(
            inst_prop, names='Clasificación', values='Cantidad Instituciones', hole=0.5,
            title="<b>Proporción de Instituciones Únicas</b>", color='Clasificación',
            color_discrete_map=color_map, template='plotly_dark'
        )
        fig_inst.update_traces(textinfo='percent+value', textposition='inside', insidetextorientation='horizontal')
        fig_inst.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=350, showlegend=True,
                               legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_inst, use_container_width=True)

    with col_prop2:
        freq_inst = df_final.groupby('Torta_Comb')['Ind Frecuencia médico'].mean().reset_index()
        freq_inst.columns = ['Clasificación', 'Frecuencia_Promedio']
        freq_inst = asegurar_categorias(freq_inst, 'Clasificación', 'Frecuencia_Promedio')
        
        fig_freq_peso = px.bar(
            freq_inst, x='Clasificación', y='Frecuencia_Promedio',
            text='Frecuencia_Promedio', color='Clasificación',
            color_discrete_map=color_map, template='plotly_dark',
            title="<b>Índice de Frecuencia Promedio (Normalizado)</b>"
        )
        fig_freq_peso.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_freq_peso.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=350, showlegend=False,
                                    xaxis_title="", yaxis_title="Frecuencia Promedio")
        st.plotly_chart(fig_freq_peso, use_container_width=True)

    st.markdown("---")

    # --- SECCIÓN: ÍNDICE DE FRECUENCIA POR MERCADO ---
    st.subheader("Índice de Frecuencia Promedio de Visita: Pareto vs No Pareto")

    col_freq1, col_freq2, col_freq3 = st.columns(3)

    def grafica_frecuencia_barras(df_data, titulo, col_cat):
        freq_df = df_data.groupby(col_cat)['Ind Frecuencia médico'].mean().reset_index()
        freq_df.columns = ['Clasificación', 'Frecuencia Promedio']
        freq_df = asegurar_categorias(freq_df, 'Clasificación', 'Frecuencia Promedio')
        
        fig = px.bar(
            freq_df, x='Clasificación', y='Frecuencia Promedio',
            text='Frecuencia Promedio', color='Clasificación',
            color_discrete_map=color_map, template='plotly_dark',
            title=titulo
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', textfont_size=13)
        fig.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=340, showlegend=False,
                            xaxis_title="", yaxis_title="Índice Promedio", margin=dict(t=50, b=30, l=20, r=20))
        return fig

    with col_freq1:
        st.plotly_chart(grafica_frecuencia_barras(df_final, "<b>Frecuencia GCH</b>", 'Torta_GCH'), use_container_width=True)

    with col_freq2:
        st.plotly_chart(grafica_frecuencia_barras(df_final, "<b>Frecuencia Allergy</b>", 'Torta_Allergy'), use_container_width=True)

    with col_freq3:
        st.plotly_chart(grafica_frecuencia_barras(df_final, "<b>Frecuencia Combinada</b>", 'Torta_Comb'), use_container_width=True)

else:
    st.warning("⚠️ No se encontró el archivo 'Indicador_frecuencia_medicos.xlsx'. Súbelo a la raíz del repositorio o cárgalo mediante la barra lateral.")
