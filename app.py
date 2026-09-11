import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración de página
st.set_page_config(
    page_title="Pharmadvisor | Business Intelligence Executive",
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
            <span style="color: #9AA5B1; font-size: 13px;">Inteligencia de Prescripción Mipres & Auditoría de Visitas Pharmadvisor</span>
        </div>
        <div style="text-align: right;">
            <span style="color: #E6007E; font-weight: bold; font-size: 20px;">Pharm<span style="color: #FFFFFF;">ADVISOR</span></span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS (MIPRES Y PHARMADVISOR) ---
@st.cache_data
def cargar_datos_mipres(uploaded_file=None):
    source = uploaded_file if uploaded_file is not None else 'Base Mipres.xlsx'
    if not os.path.exists('Base Mipres.xlsx') and uploaded_file is None:
        return None
    try:
        df = pd.read_excel(source, sheet_name='Consolidado', header=1)
        for col in ['2025', '2026', 'Total general', '2025.1', '2026.1', 'Total general.1', 'Médicos Visitados']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        return None

@st.cache_data
def cargar_datos_visitas(uploaded_file=None):
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

# --- CARGADORES EN BARRA LATERAL ---
st.sidebar.subheader("Carga de Archivos")
uploaded_visitas = st.sidebar.file_uploader("Cargar Indicador Frecuencia (Excel)", type=["xlsx"], key="visitas_up")
uploaded_mipres = st.sidebar.file_uploader("Cargar Base Mipres (Excel)", type=["xlsx"], key="mipres_up")

df_frec = cargar_datos_visitas(uploaded_visitas)
df_mipres = cargar_datos_mipres(uploaded_mipres)

# --- DEFINICIÓN DE PESTAÑAS PRINCIPALES ---
tab_mipres, tab_visitas = st.tabs(["📊 Inteligencia Mipres & Oportunidades", "📈 Auditoría de Visitas & Paretización"])

# =========================================================================
# PESTAÑA 1: INTELIGENCIA MIPRES & OPORTUNIDADES COMERCIALES (ESTRATÉGICA)
# =========================================================================
with tab_mipres:
    st.subheader("Tablero de Oportunidades Estratégicas y Potencial de Mercado (Base Mipres)")
    
    if df_mipres is not None:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Filtros Estratégicos Mipres")
        
        regiones_mipres = sorted(df_mipres['Región'].dropna().unique()) if 'Región' in df_mipres.columns else []
        selected_regiones = st.sidebar.multiselect("Región Mipres", options=regiones_mipres, default=regiones_mipres, key="reg_mipres")
        
        df_mipres_filtered = df_mipres[df_mipres['Región'].isin(selected_regiones)] if 'Región' in df_mipres.columns else df_mipres
        
        # KPIs Ejecutivos de Alto Impacto
        total_vol_2026 = df_mipres_filtered['2026'].sum(skipna=True) if '2026' in df_mipres_filtered.columns else 0
        total_vol_2025 = df_mipres_filtered['2025'].sum(skipna=True) if '2025' in df_mipres_filtered.columns else 0
        crecimiento_mercado = ((total_vol_2026 - total_vol_2025) / total_vol_2025 * 100) if total_vol_2025 > 0 else 0
        
        # Porcentaje de instituciones sin visita comercial Growth
        if 'Se visita Growth?' in df_mipres_filtered.columns:
            sin_visita_count = len(df_mipres_filtered[df_mipres_filtered['Se visita Growth?'] == 'No'])
            pct_sin_visita = (sin_visita_count / len(df_mipres_filtered) * 100) if len(df_mipres_filtered) > 0 else 0
        else:
            pct_sin_visita = 0

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Volumen Total Mipres (2026)", f"{total_vol_2026:,.1f}", delta=f"{crecimiento_mercado:+.1f}% vs 2025")
        kpi2.metric("Instituciones Analizadas", f"{len(df_mipres_filtered):,}")
        kpi3.metric("Brecha de Cobertura (Sin Visita Growth)", f"{pct_sin_visita:.1f}%", delta_color="inverse")

        st.markdown("---")
        
        # 1. ANÁLISIS DE CUENTAS CLAVE NO VISITADAS (TOP 15 OPORTUNIDADES)
        st.subheader("🎯 Top 15 Instituciones de Alto Volumen Comercial SIN Visita (Oportunidad de Apertura)")
        
        if 'Se visita Growth?' in df_mipres_filtered.columns and 'Total general' in df_mipres_filtered.columns:
            # Filtrar exclusivamente las que NO se visitan
            df_brecha = df_mipres_filtered[df_mipres_filtered['Se visita Growth?'] == 'No'].sort_values(by='Total general', ascending=False, na_position='last').head(15)
            
            if not df_brecha.empty:
                fig_brecha = px.bar(
                    df_brecha,
                    x='Prestador',
                    y='Total general',
                    text='Total general',
                    template='plotly_dark',
                    title="<b>Potencial No Capturado (Volumen Mipres en Instituciones No Visitadas)</b>",
                    color_discrete_sequence=['#E6007E']
                )
                fig_brecha.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=11)
                fig_brecha.update_layout(
                    paper_bgcolor='#1C202C',
                    plot_bgcolor='#2D3346',
                    height=450,
                    xaxis={'tickangle': -35},
                    yaxis_title="Volumen Acumulado Mipres",
                    margin=dict(t=50, b=120, l=40, r=20)
                )
                st.plotly_chart(fig_brecha, use_container_width=True)
            else:
                st.success("🎉 ¡Excelente cobertura! No hay instituciones en esta selección con estatus 'No' en visitas Growth.")

        st.markdown("---")

        # 2. COMPARATIVA DE CRECIMIENTO 2025 vs 2026 POR INSTITUCIÓN PARETO
        st.subheader("📈 Dinámica de Prescripción: Comparativo de Volumen 2025 vs 2026")
        
        if '2025' in df_mipres_filtered.columns and '2026' in df_mipres_filtered.columns:
            # Top 15 instituciones por volumen total
            df_dinamica = df_mipres_filtered.sort_values(by='Total general', ascending=False, na_position='last').head(12)
            
            # Reestructurar para gráfico agrupado
            df_melted = df_dinamica.melt(id_vars=['Prestador', 'Región'], value_vars=['2025', '2026'], var_name='Año', value_name='Volumen')
            
            fig_dinamica = px.bar(
                df_melted,
                x='Prestador',
                y='Volumen',
                color='Año',
                barmode='group',
                template='plotly_dark',
                title="<b>Evolución del Volumen de Prescripción por Institución Líder</b>",
                color_discrete_map={'2025': '#9AA5B1', '2026': '#0088FF'}
            )
            fig_dinamica.update_layout(
                paper_bgcolor='#1C202C',
                plot_bgcolor='#2D3346',
                height=450,
                xaxis={'tickangle': -35},
                margin=dict(t=50, b=120, l=40, r=20)
            )
            st.plotly_chart(fig_dinamica, use_container_width=True)

        st.markdown("##### Auditoría Completa de Oportunidades Mipres")
        st.dataframe(df_mipres_filtered, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Por favor carga el archivo 'Base Mipres.xlsx' mediante la barra lateral para habilitar la inteligencia comercial.")

# =========================================================================
# PESTAÑA 2: AUDITORÍA DE VISITAS & PARETIZACIÓN (PHARMADVISOR)
# =========================================================================
with tab_visitas:
    st.subheader("Auditoría Comercial y Frecuencia de Visita (Pharmadvisor)")
    
    if df_frec is not None:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Filtros Comerciales Pharmadvisor")

        distritos_disponibles = sorted(df_frec['Distrito'].dropna().unique())
        selected_distritos = st.sidebar.multiselect("Distrito", options=distritos_disponibles, default=distritos_disponibles, key="dist_ph")
        
        df_filtered = df_frec[df_frec['Distrito'].isin(selected_distritos)]
        lineas_disponibles = sorted(df_filtered['Línea'].dropna().unique())
        selected_lineas = st.sidebar.multiselect("Línea", options=lineas_disponibles, default=lineas_disponibles, key="lin_ph")
        
        df_filtered = df_filtered[df_filtered['Línea'].isin(selected_lineas)]
        categorias_disponibles = sorted(df_filtered['Categoría'].dropna().unique())
        selected_categorias = st.sidebar.multiselect("Categoría del Médico", options=categorias_disponibles, default=categorias_disponibles, key="cat_ph")
        
        df_filtered = df_filtered[df_filtered['Categoría'].isin(selected_categorias)]
        representantes_disponibles = sorted(df_filtered['Representante'].dropna().unique())
        selected_representantes = st.sidebar.multiselect("Representante", options=representantes_disponibles, default=representantes_disponibles, key="rep_ph")

        df_final = df_filtered[df_filtered['Representante'].isin(selected_representantes)]

        total_medicos_filtrados = len(df_final)
        st.markdown(f"<span style='color: #9AA5B1; font-size: 15px;'>Mostrando análisis para <b>{total_medicos_filtrados:,}</b> registros médicos seleccionados.</span>", unsafe_allow_html=True)
        st.markdown("---")

        # SECCIÓN 1: DONAS INSTITUCIONALES
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
            fig.update_traces(textinfo='percent+value', textposition='inside', insidetextorientation='horizontal', textfont_size=12)
            fig.update_layout(
                paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=370, showlegend=True,
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

        # SECCIÓN 2: FRECUENCIA BARRAS
        st.subheader("Índice de Frecuencia Promedio de Visita: Pareto vs No Pareto")
        col_freq1, col_freq2, col_freq3 = st.columns(3)

        def grafica_frecuencia_barras(df_data, titulo, col_cat):
            freq_df = df_data.groupby(col_cat)['Ind Frecuencia médico'].mean().reset_index()
            freq_df.columns = ['Clasificación', 'Frecuencia Promedio']
            fig = px.bar(
                freq_df, x='Clasificación', y='Frecuencia Promedio',
                text='Frecuencia Promedio', color='Clasificación',
                color_discrete_map=color_map, template='plotly_dark', title=titulo
            )
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', textfont_size=13)
            fig.update_layout(
                paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=340, showlegend=False,
                xaxis_title="", yaxis_title="Índice Promedio", margin=dict(t=50, b=30, l=20, r=20)
            )
            return fig

        with col_freq1:
            st.plotly_chart(grafica_frecuencia_barras(df_final, "<b>Frecuencia GCH</b>", 'Torta_GCH'), use_container_width=True)
        with col_freq2:
            st.plotly_chart(grafica_frecuencia_barras(df_final, "<b>Frecuencia Allergy</b>", 'Torta_Allergy'), use_container_width=True)
        with col_freq3:
            st.plotly_chart(grafica_frecuencia_barras(df_final, "<b>Frecuencia Combinada</b>", 'Torta_Comb'), use_container_width=True)

        st.markdown("---")

        # SECCIÓN 3: RANKING
        st.subheader("Índice de Frecuencia Promedio según Posición en el Ranking de Paretización")
        col_rank1, col_rank2 = st.columns(2)

        def grafica_frecuencia_ranking(df_data, col_bin, titulo):
            if col_bin not in df_data.columns:
                return px.line(title=titulo)
            rank_df = df_data.groupby(col_bin)['Ind Frecuencia médico'].mean().reset_index()
            rank_df.columns = ['Rango de Ranking', 'Frecuencia Promedio']
            rank_df = rank_df.sort_values('Rango de Ranking')
            fig = px.line(
                rank_df, x='Rango de Ranking', y='Frecuencia Promedio',
                markers=True, text='Frecuencia Promedio', template='plotly_dark',
                title=titulo, color_discrete_sequence=['#0088FF']
            )
            fig.update_traces(texttemplate='%{text:.2f}', textposition='top center', textfont_size=12, line=dict(width=3))
            fig.update_layout(
                paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=370,
                xaxis_title="Rango de Posición en Ranking", yaxis_title="Frecuencia Promedio",
                margin=dict(t=50, b=50, l=20, r=20)
            )
            return fig

        with col_rank1:
            st.plotly_chart(grafica_frecuencia_ranking(df_final, 'Ranking_Bin_GCH', "<b>Frecuencia vs Ranking GCH</b>"), use_container_width=True)
        with col_rank2:
            st.plotly_chart(grafica_frecuencia_ranking(df_final, 'Ranking_Bin_Allergy', "<b>Frecuencia vs Ranking Allergy</b>"), use_container_width=True)

        # SECCIÓN 4: INSTITUCIÓN ORDENADA POR RANKING Y % FRECUENCIA HORIZONTAL
        st.markdown("---")
        st.subheader("Análisis por Institución: Frecuencia Promedio Ordenada por Ranking")

        instituciones_disponibles = sorted(df_final['Institución 1.1'].dropna().unique())
        selected_instituciones = st.multiselect(
            "Seleccionar Institución(es) para comparar:",
            options=instituciones_disponibles,
            default=instituciones_disponibles[:12] if len(instituciones_disponibles) >= 12 else instituciones_disponibles,
            key="inst_multiselect"
        )

        if selected_instituciones:
            df_inst_filtered = df_final[df_final['Institución 1.1'].isin(selected_instituciones)]
            
            def parse_rank(val):
                try:
                    return float(val)
                except:
                    return 999999.0

            df_inst_filtered['Numeric_Rank'] = df_inst_filtered['Ranking GCH'].apply(parse_rank)
            
            inst_summary = df_inst_filtered.groupby('Institución 1.1').agg(
                Best_Ranking=('Numeric_Rank', 'min'),
                Cantidad_Medicos=('Código', 'count'),
                Frecuencia_Promedio=('Ind Frecuencia médico', 'mean')
            ).reset_index()
            
            inst_summary = inst_summary.sort_values(by='Best_Ranking', ascending=True)
            inst_summary['Etiqueta_Freq_Pct'] = inst_summary['Frecuencia_Promedio'].apply(lambda x: f"{x * 100:.1f}%")

            fig_bar = px.bar(
                inst_summary, 
                x='Institución 1.1', 
                y='Frecuencia_Promedio',
                text='Etiqueta_Freq_Pct',
                template='plotly_dark',
                title="<b>Índice de Frecuencia Promedio (Ordenado por Ranking)</b>",
                color_discrete_sequence=['#0088FF']
            )
            
            fig_bar.update_traces(
                textposition='inside',
                textfont_size=11,
                textfont_color='white'
            )
            
            fig_bar.update_layout(
                paper_bgcolor='#1C202C',
                plot_bgcolor='#2D3346',
                height=500,
                xaxis_title="Institución (Orden de Ranking)",
                yaxis_title="Índice de Frecuencia Promedio",
                xaxis={'tickangle': -35},
                margin=dict(t=60, b=130, l=40, r=20),
                showlegend=False
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("##### Detalle de Ranking, Frecuencia y Médicos por Institución")
            inst_summary_display = inst_summary[['Institución 1.1', 'Best_Ranking', 'Frecuencia_Promedio', 'Cantidad_Medicos']].copy()
            inst_summary_display['Best_Ranking'] = inst_summary_display['Best_Ranking'].apply(lambda x: int(x) if x < 999999 else 'N/A')
            inst_summary_display.columns = ['Institución', 'Mejor Ranking', 'Frecuencia Promedio', 'Cantidad de Médicos']
            inst_summary_display['Frecuencia Promedio'] = inst_summary_display['Frecuencia Promedio'].round(2)
            st.dataframe(inst_summary_display, use_category_width=True, hide_index=True)
        else:
            st.info("ℹ️ Por favor selecciona al menos una institución en el filtro superior para visualizar la comparativa.")
    else:
        st.warning("⚠️ No se encontró el archivo 'Indicador_frecuencia_medicos.xlsx'. Súbelo mediante la barra lateral.")
