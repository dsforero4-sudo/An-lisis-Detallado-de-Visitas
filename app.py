import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# 1. Configuración de página
st.set_page_config(
    page_title="Pharmadvisor | E-Metrics BI Executive",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #1A1F2C; color: #FFFFFF; }
    .kpi-card {
        background-color: #262C3A;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .kpi-label { color: #9AA5B1; font-size: 11px; font-weight: 600; text-transform: uppercase; }
    .kpi-value { color: #FFFFFF; font-size: 26px; font-weight: bold; margin-top: 5px; }
    .insight-card {
        background-color: #262C3A;
        border-left: 5px solid #4A90E2;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 20px;
    }
    .insight-alert {
        background-color: #262C3A;
        border-left: 5px solid #FF5252;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 20px;
    }
    .insight-success {
        background-color: #262C3A;
        border-left: 5px solid #4CAF50;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Pharmadvisor | E-Metrics BI Executive")
st.caption("Panel de Inteligencia de Mercado, Alignment SFE, Cuentas Pareto y Técnica de Ventas (SPIN / FAP)")

# Función de Copy-Paste
def get_copy_paste_rate(df_sub):
    total = len(df_sub)
    if total == 0:
        return 0.0
    max_freq = df_sub['Comentario_str'].value_counts().max() if 'Comentario_str' in df_sub.columns else 0
    if (max_freq / total) >= 0.95 and total >= 10:
        return 100.0
    dup_cnt = df_sub.duplicated(subset=['Comentario_str']).sum() if 'Comentario_str' in df_sub.columns else 0
    return round((dup_cnt / total) * 100, 1)

# Función de Calificación de Técnica de Ventas (SPIN / FAP)
def evaluar_tecnica_ventas(texto):
    txt = str(texto).lower()
    kw_spin = ['beneficio', 'beneficios', 'paciente', 'pacientes', 'adherencia', 'tolerancia', 
               'iniciar', 'inicios', 'compromiso', 'acepta', 'formula', 'formulacion', 
               'diferencia', 'diferenciador', 'falla de medro', 'alergia', 'reflujo', 'efectividad']
    
    score_spin = sum(1 for kw in kw_spin if kw in txt)
    
    if score_spin >= 2:
        return "Alta Calidad (Venta Consultiva / FAP)"
    elif score_spin == 1:
        return "Calidad Media (Presentación de Producto)"
    else:
        return "Baja Calidad (Trámite / Administrativo)"

# Función segura para clasificar Categoría TOP vs Estándar
def normalizar_categoria(val):
    if pd.isna(val):
        return 'Médico Estándar / Sin Cat.'
    val_str = str(val).strip().upper()
    if val_str in ['NAN', 'NONE', '', 'NULL']:
        return 'Médico Estándar / Sin Cat.'
    if 'TOP' in val_str:
        return 'Médico TOP'
    return 'Médico Estándar / Sin Cat.'

# Función segura para clasificar Institución Pareto
def normalizar_pareto(val):
    if pd.isna(val):
        return 'Institución No Pareto'
    val_str = str(val).strip().upper()
    if val_str in ['NAN', 'NONE', '', 'NULL', 'NO', 'FALSE', '0']:
        return 'Institución No Pareto'
    if any(k in val_str for k in ['SI', 'SÍ', 'PARETO', '1', 'TRUE']):
        return 'Institución Pareto'
    return 'Institución No Pareto'

uploaded_file = st.file_uploader("Cargar Reporte de Visitas (Excel / CSV)", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]

    if 'Cod. visita' in df.columns:
        df_clean = df.drop_duplicates(subset=['Cod. visita']).copy()
    else:
        df_clean = df.copy()

    df_clean['Comentario_str'] = df_clean['Comentario'].astype(str).str.strip() if 'Comentario' in df_clean.columns else ""
    df_clean['Objetivo_str'] = df_clean['Objetivo'].astype(str).str.strip() if 'Objetivo' in df_clean.columns else ""

    col_cat = 'Categoría' if 'Categoría' in df_clean.columns else ('Categoria' if 'Categoria' in df_clean.columns else None)
    col_pareto = [c for c in df_clean.columns if 'pareto' in c.lower()]
    col_pareto_name = col_pareto[0] if col_pareto else None

    # Normalización Segura de Categoría
    if col_cat:
        df_clean['Cat_Clean'] = df_clean[col_cat].apply(normalizar_categoria)
    else:
        df_clean['Cat_Clean'] = 'Médico Estándar / Sin Cat.'

    # Normalización Segura de Pareto
    if col_pareto_name:
        df_clean['Pareto_Clean'] = df_clean[col_pareto_name].apply(normalizar_pareto)
    else:
        df_clean['Pareto_Clean'] = 'Institución No Pareto'

    # Evaluación cualitativa
    df_clean['Nivel_Tecnica_Ventas'] = df_clean['Comentario_str'].apply(evaluar_tecnica_ventas)

    # 3. BARRA DE FILTROS GLOBALES
    c_f1, c_f2, c_f3, c_f4, c_f5 = st.columns([1.2, 1.2, 1.2, 1, 1])
    
    with c_f1:
        regiones = ["Todas"] + sorted([str(x) for x in df_clean['Región'].dropna().unique()]) if 'Región' in df_clean.columns else ["Todas"]
        sel_region = st.selectbox("Coordinación Regional", regiones)
    with c_f2:
        lineas = ["Todas"] + sorted([str(x) for x in df_clean['Línea'].dropna().unique()]) if 'Línea' in df_clean.columns else ["Todas"]
        sel_linea = st.selectbox("Línea de Producto", lineas)
    with c_f3:
        reps = ["Todas"] + sorted([str(x) for x in df_clean['Representante'].dropna().unique()]) if 'Representante' in df_clean.columns else ["Todas"]
        sel_rep = st.selectbox("Representante (SFE)", reps)
    with c_f4:
        sel_cat = st.selectbox("Categoría Médico", ["Todas", "Médico TOP", "Médico Estándar / Sin Cat."])
    with c_f5:
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        only_pareto = st.checkbox("Solo Cuentas Pareto 🏥", value=False)

    # Filtrado dinámico
    df_filtered = df_clean.copy()
    if sel_region != "Todas":
        df_filtered = df_filtered[df_filtered['Región'] == sel_region]
    if sel_linea != "Todas":
        df_filtered = df_filtered[df_filtered['Línea'] == sel_linea]
    if sel_rep != "Todas":
        df_filtered = df_filtered[df_filtered['Representante'] == sel_rep]
    if sel_cat != "Todas":
        df_filtered = df_filtered[df_filtered['Cat_Clean'] == sel_cat]
    if only_pareto:
        df_filtered = df_filtered[df_filtered['Pareto_Clean'] == 'Institución Pareto']

    # Métricas Globales
    total_visitas = len(df_filtered)
    doc_id_col = 'Cod. único Médicos' if 'Cod. único Médicos' in df_filtered.columns else ('Cod. único' if 'Cod. único' in df_filtered.columns else 'Médicos')
    medicos = df_filtered[doc_id_col].nunique() if doc_id_col in df_filtered.columns else 0

    pct_dup = get_copy_paste_rate(df_filtered)
    cnt_dup_total = int(round((pct_dup / 100) * total_visitas))
    cnt_alta_calidad = (df_filtered['Nivel_Tecnica_Ventas'] == "Alta Calidad (Venta Consultiva / FAP)").sum()
    pct_alta_calidad = round((cnt_alta_calidad / total_visitas * 100), 1) if total_visitas > 0 else 0

    # Tarjetas KPI
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-label">TOTAL VISITAS ÚNICAS</div><div class="kpi-value">{total_visitas:,}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-label">MÉDICOS CONTACTADOS</div><div class="kpi-value">{medicos:,}</div></div>', unsafe_allow_html=True)
    color_dup = '#FF5252' if pct_dup > 50 else '#4CAF50'
    k3.markdown(f'<div class="kpi-card"><div class="kpi-label">TASA COPY-PASTE</div><div class="kpi-value" style="color:{color_dup};">{pct_dup:.1f}%</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card"><div class="kpi-label">ÍNDICE VENTA CONSULTIVA</div><div class="kpi-value" style="color:#4A90E2;">{pct_alta_calidad}%</div></div>', unsafe_allow_html=True)

    st.markdown("###")

    # 3 Pestañas
    tab_reg, tab_linea, tab_insights = st.tabs([
        "🏛️ GERENCIAS REGIONALES (SFE & Targeting TOP)", 
        "📦 GERENCIAS DE LÍNEA & TÉCNICA DE VENTAS",
        "💡 HALLAZGOS ESTRATÉGICOS C-LEVEL"
    ])

    # --- PESTAÑA 1: GERENCIAS REGIONALES ---
    with tab_reg:
        st.subheader("Auditoría Territorial y Alignment: Médicos TOP vs. Cuentas Pareto")
        
        r1, r2 = st.columns(2)
        with r1:
            if 'Región' in df_filtered.columns and total_visitas > 0:
                reg_list = [{'Región': r, '% Duplicidad': get_copy_paste_rate(grp)} for r, grp in df_filtered.groupby('Región')]
                fig1 = px.bar(pd.DataFrame(reg_list), x='Región', y='% Duplicidad', color='% Duplicidad',
                              color_continuous_scale='Reds', template='plotly_dark', title='<b>1. Índice de Copy-Paste por Región (%)</b>')
                fig1.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=330)
                st.plotly_chart(fig1, use_container_width=True)

        with r2:
            if 'Representante' in df_filtered.columns:
                rep_list = [{'Representante': r, '% Copy-Paste': get_copy_paste_rate(grp)} 
                            for r, grp in df_filtered.groupby('Representante') if len(grp) >= 5]
                rep_df = pd.DataFrame(rep_list).sort_values(by='% Copy-Paste', ascending=False).head(10)
                fig2 = px.bar(rep_df, x='% Copy-Paste', y='Representante', orientation='h', color='% Copy-Paste',
                              color_continuous_scale='Reds', template='plotly_dark', title='<b>2. Top 10 Reps en Alerta Copy-Paste</b>')
                fig2.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=330, yaxis={'autorange': 'reversed'})
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("###")
        p1, p2 = st.columns(2)
        
        with p1:
            if total_visitas > 0:
                doc_cat_df = df_filtered.groupby(doc_id_col)['Cat_Clean'].first().value_counts().reset_index()
                doc_cat_df.columns = ['Categoría', 'Médicos Únicos']
                fig_cat_pie = px.pie(doc_cat_df, names='Categoría', values='Médicos Únicos', hole=0.4,
                                     template='plotly_dark', title='<b>3. Composición del Panel de Médicos Únicos (TOP vs Estándar)</b>',
                                     color_discrete_map={'Médico TOP': '#4A90E2', 'Médico Estándar / Sin Cat.': '#9AA5B1'})
                fig_cat_pie.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=330)
                st.plotly_chart(fig_cat_pie, use_container_width=True)

        with p2:
            if total_visitas > 0:
                # MATRIZ HEATMAP 2x2 (Con 'Médico TOP' arriba)
                cross_df = df_filtered.groupby([doc_id_col, 'Cat_Clean'])['Pareto_Clean'].first().reset_index()
                heatmap_data = pd.crosstab(cross_df['Cat_Clean'], cross_df['Pareto_Clean'])
                
                # Reordenar filas para colocar a los Médicos TOP en la parte superior
                order_rows = [r for r in ['Médico TOP', 'Médico Estándar / Sin Cat.'] if r in heatmap_data.index]
                order_cols = [c for c in ['Institución Pareto', 'Institución No Pareto'] if c in heatmap_data.columns]
                heatmap_data = heatmap_data.reindex(index=order_rows, columns=order_cols)
                
                fig_cross = px.imshow(
                    heatmap_data,
                    text_auto=True,
                    color_continuous_scale='Greens',
                    template='plotly_dark',
                    title='<b>4. Matriz Heatmap: Conteo de Médicos por Cuadrante</b>'
                )
                
                fig_cross.update_layout(
                    paper_bgcolor='#1A1F2C', 
                    plot_bgcolor='#262C3A', 
                    height=330, 
                    xaxis_title="Tipo de Institución",
                    yaxis_title="Categoría Médico"
                )
                st.plotly_chart(fig_cross, use_container_width=True)

        st.markdown("#### Tabla de Control de la Fuerza de Ventas")
        if 'Representante' in df_filtered.columns:
            tabla_sfe = pd.DataFrame([
                {
                    'Coordinación': grp['Región'].iloc[0] if 'Región' in grp.columns else 'N/A',
                    'Línea': grp['Línea'].iloc[0] if 'Línea' in grp.columns else 'N/A',
                    'Representante': r,
                    'Visitas Totales': len(grp),
                    'Médicos Únicos': grp[doc_id_col].nunique(),
                    'Médicos TOP': grp[grp['Cat_Clean']=='Médico TOP'][doc_id_col].nunique(),
                    '% Visitas Pareto': round((grp['Pareto_Clean'].value_counts().get('Institución Pareto', 0) / len(grp)) * 100, 1),
                    '% Copy-Paste': get_copy_paste_rate(grp)
                } for r, grp in df_filtered.groupby('Representante')
            ]).sort_values(by='% Copy-Paste', ascending=False)
            st.dataframe(tabla_sfe, use_container_width=True)

    # --- PESTAÑA 2: GERENCIAS DE LÍNEA & TÉCNICA DE VENTAS ---
    with tab_linea:
        st.subheader("Análisis de Marcas, Share of Voice, Técnica de Ventas y Temas")
        l1, l2 = st.columns(2)

        with l1:
            calidad_df = df_filtered['Nivel_Tecnica_Ventas'].value_counts().reset_index()
            calidad_df.columns = ['Nivel de Calidad', 'Visitas']
            fig_cal = px.pie(calidad_df, names='Nivel de Calidad', values='Visitas', hole=0.4,
                             color_discrete_sequence=['#4CAF50', '#FFC107', '#FF5252'],
                             template='plotly_dark', title='<b>1. Evaluación Cualitativa del Registro (SPIN / FAP)</b>')
            fig_cal.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=350)
            st.plotly_chart(fig_cal, use_container_width=True)

        with l2:
            prods = ['Fortini', 'Infatrini', 'Ketocal', 'Pepti', 'Syneo', 'Neocate', 'Anamix']
            prod_data = [{'Producto': p, 'Visitas': df_filtered['Comentario_str'].str.contains(p, case=False, na=False).sum()} for p in prods]
            prod_df = pd.DataFrame(prod_data).sort_values(by='Visitas', ascending=False)
            fig3 = px.bar(prod_df, x='Producto', y='Visitas', color='Visitas',
                          color_continuous_scale='Blues', template='plotly_dark', title='<b>2. Menciones por Producto (Share of Voice)</b>')
            fig3.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=350)
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("###")
        themes = {
            'Beneficios de Producto': 'syneo|pepti|infatrini|fortini|neocate|ketocal',
            'Programa Pacientes (PAP)': 'pap|programa|fundacion|fundación',
            'Trámites Mipres / EPS': 'mipres|eps|autorizacion|autorización|formulacion',
            'Inicios / Muestras': 'inicio|inicios|muestra|muestras|probando',
            'Competencia Mencionada': 's-26|s26|similac|nan|althera|nutramigen'
        }
        theme_data = [{'Eje Temático': t_name, 'Visitas': df_filtered['Comentario_str'].str.contains(t_kw, case=False, na=False).sum()} for t_name, t_kw in themes.items()]
        theme_df = pd.DataFrame(theme_data).sort_values(by='Visitas', ascending=True)
        fig4 = px.bar(theme_df, y='Eje Temático', x='Visitas', orientation='h',
                      color='Visitas', color_continuous_scale='Greens', template='plotly_dark',
                      title='<b>3. Ejes Temáticos y Barreras detectadas en Consultorio</b>')
        fig4.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=320)
        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 💬 Módulos de Voz del Médico (Comentarios Reales de Consultorio)")
        
        comentarios_genuinos = df_filtered[~df_filtered.duplicated(subset=['Representante', 'Comentario_str'], keep=False)].copy()
        
        c1, c2 = st.columns([1, 1])
        with c1:
            filtro_nivel = st.selectbox("Filtrar por Nivel de Calidad Comercial:", 
                                        ["Todos los Comentarios Genuinos", "Alta Calidad (Venta Consultiva / FAP)", "Calidad Media (Presentación de Producto)", "Baja Calidad (Trámite / Administrativo)"])
        with c2:
            kw_input = st.text_input("🔍 Buscar por Palabra Clave (Ej: Mipres, Sabor, Aceptación, Muestra, Competencia, PAP)", "")

        comentarios_display = comentarios_genuinos.copy()
        if filtro_nivel != "Todos los Comentarios Genuinos":
            comentarios_display = comentarios_display[comentarios_display['Nivel_Tecnica_Ventas'] == filtro_nivel]
        if kw_input:
            comentarios_display = comentarios_display[comentarios_display['Comentario_str'].str.contains(kw_input, case=False, na=False)]

        cols_vista = ['Línea', 'Especialidad Promocional', 'Representante', 'Objetivo_str', 'Comentario_str', 'Cat_Clean', 'Pareto_Clean']
        cols_presentes = [c for c in cols_vista if c in comentarios_display.columns]

        st.markdown(f"**Se encontraron {len(comentarios_display):,} observaciones cualitativas reales:**")
        st.dataframe(
            comentarios_display[cols_presentes].rename(columns={
                'Especialidad Promocional': 'Especialidad Médico',
                'Objetivo_str': 'Objetivo Registrado',
                'Comentario_str': 'Comentario Registrado',
                'Cat_Clean': 'Categoría',
                'Pareto_Clean': 'Institución Pareto'
            }),
            use_container_width=True,
            height=300
        )

    # --- PESTAÑA 3: HALLAZGOS ESTRATÉGICOS C-LEVEL ---
    with tab_insights:
        st.subheader("💡 Resumen Ejecutivo & Sustentación Cuantitativa (C-Level)")
        st.caption("Argumentación basada en métricas exactas, Targeting de Médicos TOP y Cuentas Pareto.")

        docs_top = df_filtered[df_filtered['Cat_Clean']=='Médico TOP'][doc_id_col].nunique() if doc_id_col in df_filtered.columns else 0
        pct_top = round((docs_top / medicos) * 100, 1) if medicos > 0 else 0

        docs_top_pareto = df_filtered[(df_filtered['Cat_Clean']=='Médico TOP') & (df_filtered['Pareto_Clean']=='Institución Pareto')][doc_id_col].nunique() if doc_id_col in df_filtered.columns else 0
        pct_top_in_pareto = round((docs_top_pareto / docs_top) * 100, 1) if docs_top > 0 else 0

        st.markdown(f"""
        <div class="insight-alert">
            <h4 style="color:#FF5252; margin-top:0;">🚨 1. Evaluación de Criterio de Selección de Médicos TOP (Targeting SFE)</h4>
            <p>Los representantes seleccionaron un total de <b>{docs_top:,} médicos TOP ({pct_top}% del panel contactado)</b>. Al auditar su ubicación institucional:</p>
            <ul>
                <li><b>Alineación con Cuentas Clave:</b> Únicamente el <b>{pct_top_in_pareto}% de los médicos TOP seleccionados ({docs_top_pareto:,} médicos)</b> pertenecen a Instituciones Pareto.</li>
                <li><b>Oportunidad de Calibración:</b> El restante <b>{round(100 - pct_top_in_pareto, 1)}% de los médicos clasificados como TOP</b> son atendidos en instituciones periféricas (No Pareto), lo que evidencia la necesidad de calibrar el criterio de selección de los representantes con la gerencia comercial.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card">
            <h4 style="color:#4A90E2; margin-top:0;">🎯 2. Madurez de la Técnica de Ventas (Sustentación SPIN / FAP)</h4>
            <p>Al auditar el registro en CRM, únicamente <b>{cnt_alta_calidad:,} visitas ({pct_alta_calidad}%)</b> presentan una estructura de <b>Venta Consultiva (FAP)</b> respaldada por compromisos o beneficios del paciente.</p>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("Por favor arrastra y suelta el archivo Excel de visitas para desplegar el Dashboard Ejecutivo.")
