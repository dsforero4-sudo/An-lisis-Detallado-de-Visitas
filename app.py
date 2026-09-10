import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Función para procesar y agrupar la distribución de médicos Pareto vs No Pareto
def generar_graficas_torta_pareto(df_frec, df_mipres):
    # Consolidar mapeo de instituciones MIPRES
    df_mipres_grouped = df_mipres.groupby('CC').agg({
        'Pareto_GCH_final': 'first',
        'Pareto_Allergy_final': 'first',
        'Pareto_final': 'first'
    }).reset_index()

    mipres_map = df_mipres_grouped.set_index('CC').to_dict('index')

    # Unir Institución 1.1 e Institución 2 del archivo de frecuencia
    df_inst1 = df_frec[['Código', 'Línea', 'Institución 1.1']].rename(columns={'Institución 1.1': 'CC_Matched'})
    df_inst2 = df_frec[['Código', 'Línea', 'Institución 2']].rename(columns={'Institución 2': 'CC_Matched'})

    inst_all = pd.concat([df_inst1, df_inst2])
    inst_all = inst_all[~inst_all['CC_Matched'].isin(['0', '', None]) & inst_all['CC_Matched'].notna()].drop_duplicates(subset=['Código', 'CC_Matched'])

    inst_all['Pareto_GCH'] = inst_all['CC_Matched'].apply(lambda x: mipres_map.get(x, {}).get('Pareto_GCH_final', 'No'))
    inst_all['Pareto_Allergy'] = inst_all['CC_Matched'].apply(lambda x: mipres_map.get(x, {}).get('Pareto_Allergy_final', 'No'))
    inst_all['Pareto_Final'] = inst_all['CC_Matched'].apply(lambda x: mipres_map.get(x, {}).get('Pareto_final', 'No ambas'))

    # Agrupar banderas a nivel de médico
    doc_summary = inst_all.groupby('Código').agg(
        Es_Pareto_GCH=('Pareto_GCH', lambda x: 'Inst. Pareto' if 'Sí' in list(x) else 'Inst. No Pareto'),
        Es_Pareto_Allergy=('Pareto_Allergy', lambda x: 'Inst. Pareto' if 'Sí' in list(x) else 'Inst. No Pareto'),
        Es_Pareto_Combinado=('Pareto_Final', lambda x: 'Inst. Pareto' if any(k in str(list(x)) for k in ['Pareto Ambas', 'Pareto GCH', 'Pareto Allergy']) else 'Inst. No Pareto')
    ).reset_index()

    return doc_summary

# 2. Renderizado en Streamlit (3 columnas)
st.subheader("Distribución de Médicos por Tipo de Institución (Pareto vs. No Pareto)")

# Se asume que df_frec y df_mipres ya están cargados en el flujo principal
if 'df_frec' in locals() and 'df_mipres' in locals():
    doc_summary = generar_graficas_torta_pareto(df_frec, df_mipres)

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
        fig_gch.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=320)
        st.plotly_chart(fig_gch, use_container_width=True)

    with col2:
        counts_all = doc_summary['Es_Pareto_Allergy'].value_counts().reset_index()
        counts_all.columns = ['Categoría', 'Médicos']
        fig_all = px.pie(
            counts_all, names='Categoría', values='Médicos', hole=0.4,
            title="<b>2. Mercado Allergy</b>",
            color='Categoría', color_discrete_map=color_map, template='plotly_dark'
        )
        fig_all.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=320)
        st.plotly_chart(fig_all, use_container_width=True)

    with col3:
        counts_comb = doc_summary['Es_Pareto_Combinado'].value_counts().reset_index()
        counts_comb.columns = ['Categoría', 'Médicos']
        fig_comb = px.pie(
            counts_comb, names='Categoría', values='Médicos', hole=0.4,
            title="<b>3. Mercados Combinados</b>",
            color='Categoría', color_discrete_map=color_map, template='plotly_dark'
        )
        fig_comb.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=320)
        st.plotly_chart(fig_comb, use_container_width=True)
