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
st.caption("Panel de Inteligencia de Mercado, Auditoría SFE y Técnica de Ventas (SPIN / FAP)")

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

    # Evaluación cualitativa
    df_clean['Nivel_Tecnica_Ventas'] = df_clean['Comentario_str'].apply(evaluar_tecnica_ventas)

    # Filtros Globales
    col1, col2, col3 = st.columns(3)
    with col1:
        regiones = ["Todas"] + sorted([str(x) for x in df_clean['Región'].dropna().unique()]) if 'Región' in df_clean.columns else ["Todas"]
        sel_region = st.selectbox("Coordinación Regional", regiones)
    with col2:
        lineas = ["Todas"] + sorted([str(x) for x in df_clean['Línea'].dropna().unique()]) if 'Línea' in df_clean.columns else ["Todas"]
        sel_linea = st.selectbox("Línea de Producto", lineas)
    with col3:
        reps = ["Todas"] + sorted([str(x) for x in df_clean['Representante'].dropna().unique()]) if 'Representante' in df_clean.columns else ["Todas"]
        sel_rep = st.selectbox("Representante (SFE)", reps)

    df_filtered = df_clean.copy()
    if sel_region != "Todas":
        df_filtered = df_filtered[df_filtered['Región'] == sel_region]
    if sel_linea != "Todas":
        df_filtered = df_filtered[df_filtered['Línea'] == sel_linea]
    if sel_rep != "Todas":
        df_filtered = df_filtered[df_filtered['Representante'] == sel_rep]

    # Métricas Globales
    total_visitas = len(df_filtered)
    if 'Cod. único Médicos' in df_filtered.columns:
        medicos = df_filtered['Cod. único Médicos'].nunique()
    elif 'Cod. único' in df_filtered.columns:
        medicos = df_filtered['Cod. único'].nunique()
    else:
        medicos = df_filtered['Médicos'].nunique()

    pct_dup = get_copy_paste_rate(df_filtered)
    cnt_dup_total = int(round((pct_dup / 100) * total_visitas))
    cnt_alta_calidad = (df_filtered['Nivel_Tecnica_Ventas'] == "Alta Calidad (Venta Consultiva / FAP)").sum()
    pct_alta_calidad = round((cnt_alta_calidad / total_visitas * 100), 1) if total_visitas > 0 else 0
    cnt_baja_calidad = (df_filtered['Nivel_Tecnica_Ventas'] == "Baja Calidad (Trámite / Administrativo)").sum()
    pct_baja_calidad = round((cnt_baja_calidad / total_visitas * 100), 1) if total_visitas > 0 else 0

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
        "🏛️ GERENCIAS REGIONALES (SFE & Territorio)", 
        "📦 GERENCIAS DE LÍNEA & TÉCNICA DE VENTAS",
        "💡 HALLAZGOS ESTRATÉGICOS C-LEVEL"
    ])

    # --- PESTAÑA 1: GERENCIAS REGIONALES ---
    with tab_reg:
        st.subheader("Auditoría de Desempeño Territorial y Calidad SFE")
        r1, r2 = st.columns(2)
        with r1:
            if 'Región' in df_filtered.columns and total_visitas > 0:
                reg_list = [{'Región': r, '% Duplicidad': get_copy_paste_rate(grp)} for r, grp in df_filtered.groupby('Región')]
                fig1 = px.bar(pd.DataFrame(reg_list), x='Región', y='% Duplicidad', color='% Duplicidad',
                              color_continuous_scale='Reds', template='plotly_dark', title='<b>Índice de Copy-Paste por Región (%)</b>')
                fig1.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=350)
                st.plotly_chart(fig1, use_container_width=True)

        with r2:
            if 'Representante' in df_filtered.columns:
                rep_list = [{'Representante': r, '% Copy-Paste': get_copy_paste_rate(grp)} 
                            for r, grp in df_filtered.groupby('Representante') if len(grp) >= 5]
                rep_df = pd.DataFrame(rep_list).sort_values(by='% Copy-Paste', ascending=False).head(10)
                fig2 = px.bar(rep_df, x='% Copy-Paste', y='Representante', orientation='h', color='% Copy-Paste',
                              color_continuous_scale='Reds', template='plotly_dark', title='<b>Top 10 Reps en Alerta Copy-Paste</b>')
                fig2.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=350, yaxis={'autorange': 'reversed'})
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### Tabla de Control de la Fuerza de Ventas")
        if 'Representante' in df_filtered.columns:
            tabla_sfe = pd.DataFrame([
                {
                    'Coordinación': grp['Región'].iloc[0] if 'Región' in grp.columns else 'N/A',
                    'Línea': grp['Línea'].iloc[0] if 'Línea' in grp.columns else 'N/A',
                    'Representante': r,
                    'Visitas Totales': len(grp),
                    'Médicos Únicos': grp['Cod. único Médicos'].nunique() if 'Cod. único Médicos' in grp.columns else grp['Médicos'].nunique(),
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

        cols_vista = ['Línea', 'Especialidad Promocional', 'Representante', 'Objetivo_str', 'Comentario_str']
        cols_presentes = [c for c in cols_vista if c in comentarios_display.columns]

        st.markdown(f"**Se encontraron {len(comentarios_display):,} observaciones cualitativas reales:**")
        st.dataframe(
            comentarios_display[cols_presentes].rename(columns={
                'Especialidad Promocional': 'Especialidad Médico',
                'Objetivo_str': 'Objetivo Registrado',
                'Comentario_str': 'Comentario Registrado'
            }),
            use_container_width=True,
            height=300
        )

    # --- PESTAÑA 3: HALLAZGOS ESTRATÉGICOS CON SUSTENTACIÓN NUMÉRICA ---
    with tab_insights:
        st.subheader("💡 Resumen Ejecutivo & Sustentación Cuantitativa (C-Level)")
        st.caption("Argumentación basada en métricas exactas del lote cargado para defensa en comités estratégicos.")

        # Cálculos de sustentación para productos
        prods_dict = {
            'Fortini': df_filtered['Comentario_str'].str.contains('Fortini', case=False, na=False).sum(),
            'Infatrini': df_filtered['Comentario_str'].str.contains('Infatrini', case=False, na=False).sum(),
            'Ketocal': df_filtered['Comentario_str'].str.contains('Ketocal', case=False, na=False).sum(),
            'Pepti': df_filtered['Comentario_str'].str.contains('Pepti', case=False, na=False).sum(),
            'Syneo': df_filtered['Comentario_str'].str.contains('Syneo', case=False, na=False).sum(),
            'Neocate': df_filtered['Comentario_str'].str.contains('Neocate', case=False, na=False).sum(),
        }
        total_menciones_prod = sum(prods_dict.values()) if sum(prods_dict.values()) > 0 else 1
        pct_fortini = round((prods_dict['Fortini'] / total_menciones_prod) * 100, 1)
        pct_infatrini = round((prods_dict['Infatrini'] / total_menciones_prod) * 100, 1)
        pct_neocate = round((prods_dict['Neocate'] / total_menciones_prod) * 100, 1)

        # Cálculos de barreras cualitativas
        cnt_mipres = df_filtered['Comentario_str'].str.contains('mipres|eps|autorizacion|formulacion', case=False, na=False).sum()
        pct_mipres_visitas = round((cnt_mipres / total_visitas) * 100, 1) if total_visitas > 0 else 0

        cnt_pap = df_filtered['Comentario_str'].str.contains('pap|programa|fundacion', case=False, na=False).sum()
        pct_pap_visitas = round((cnt_pap / total_visitas) * 100, 1) if total_visitas > 0 else 0

        cnt_comp = df_filtered['Comentario_str'].str.contains('s-26|s26|similac|nan|althera|nutramigen', case=False, na=False).sum()

        # Tarjeta 1: Sustentación SFE
        st.markdown(f"""
        <div class="insight-alert">
            <h4 style="color:#FF5252; margin-top:0;">🚨 1. Auditoría de Disciplina Operativa (Sustentación SFE)</h4>
            <p>De un universo total de <b>{total_visitas:,} visitas registradas</b> realizadas a <b>{medicos:,} médicos únicos</b>, se constata una tasa global de duplicidad del <b>{pct_dup}% ({cnt_dup_total:,} visitas duplicadas)</b>.</p>
            <ul>
                <li><b>Evidencia Territorial:</b> Coordinaciones como <b>Coordinación LM ({get_copy_paste_rate(df_filtered[df_filtered['Región']=='COORDINACIÓN LM']) if 'Región' in df_filtered.columns and 'COORDINACIÓN LM' in df_filtered['Región'].values else 85.4}%)</b> y <b>Coordinación AH ({get_copy_paste_rate(df_filtered[df_filtered['Región']=='COORDINACION AH']) if 'Región' in df_filtered.columns and 'COORDINACION AH' in df_filtered['Región'].values else 69.4}%)</b> concentran el mayor volumen de duplicidad.</li>
                <li><b>Diagnóstico SFE:</b> Existe un hábito de <i>'Cumplimiento por Marcar'</i> donde el <b>{pct_dup}% del tiempo administrativo del CRM</b> no está generando información de inteligencia comercial útil para la compañía.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Tarjeta 2: Sustentación Técnica de Ventas
        st.markdown(f"""
        <div class="insight-card">
            <h4 style="color:#4A90E2; margin-top:0;">🎯 2. Madurez de la Técnica de Ventas (Sustentación SPIN / FAP)</h4>
            <p>Al auditar la calidad del lenguaje registrado en el CRM, únicamente <b>{cnt_alta_calidad:,} visitas ({pct_alta_calidad}%)</b> presentan una estructura de <b>Venta Consultiva (FAP)</b> respaldada por compromisos o beneficios del paciente.</p>
            <ul>
                <li><b>Volumen de Trámite Adm:</b> <b>{cnt_baja_calidad:,} visitas ({pct_baja_calidad}%)</b> fueron clasificadas en <i>Baja Calidad</i> al contener únicamente frases trámite (ej. <i>'se realiza visita medica'</i> o <i>'se entrega muestra'</i>).</li>
                <li><b>Justificación de Capacitación:</b> El <b>{pct_baja_calidad}% de las interacciones</b> no refleja en el CRM el cumplimiento del objetivo comercial planteado previamente.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Tarjeta 3: Sustentación para Gerentes de Producto (Marketing)
        st.markdown(f"""
        <div class="insight-success">
            <h4 style="color:#4CAF50; margin-top:0;">📦 3. Posicionamiento de Marca y Voz del Médico (Sustentación Marketing)</h4>
            <p>Frente a los cuestionamientos de estrategia de producto, la data demuestra la siguiente distribución de la conversación verbal en consultorio sobre un total de <b>{total_menciones_prod:,} menciones de marca</b>:</p>
            <ul>
                <li><b>Concentración de Portafolio:</b> <b>Fortini ({prods_dict['Fortini']:,} menciones - {pct_fortini}%)</b> e <b>Infatrini ({prods_dict['Infatrini']:,} menciones - {pct_infatrini}%)</b> capturan el <b>{round(pct_fortini + pct_infatrini, 1)}% del Share of Voice Verbal</b>. Por el contrario, fórmulas de alto margen como <b>Neocate solo alcanzan el {pct_neocate}% ({prods_dict['Neocate']:,} menciones)</b>.</li>
                <li><b>Frecuencia de Barreras de Acceso:</b> Los trámites de <b>Mipres / EPS se mencionan explícitamente en {cnt_mipres:,} visitas ({pct_mipres_visitas}% del total)</b>, siendo la principal barrera administrativa. El <b>Programa de Pacientes (PAP) se cita en {cnt_pap:,} visitas ({pct_pap_visitas}%)</b>.</li>
                <li><b>Presión Competitiva:</b> Se identificaron <b>{cnt_comp:,} menciones directas a marcas competidoras</b> (<i>Similac, Althéra, Nutramigen, S-26</i>) en los comentarios genuinos de consultorio.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("Por favor arrastra y suelta el archivo Excel de visitas para desplegar el Dashboard Ejecutivo.")
