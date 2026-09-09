import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

# 1. Configuración de página
st.set_page_config(
    page_title="Pharmadvisor | E-Metrics BI Executive",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS idénticos al Dashboard Pharmadvisor / E Metrics BI
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
        font-size: 32px;
        font-weight: bold;
        margin: 0;
    }
    
    .kpi-card {
        background-color: #1C202C;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .kpi-label { 
        color: #9AA5B1; 
        font-size: 11px; 
        font-weight: 700; 
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value { 
        color: #FFFFFF; 
        font-size: 30px; 
        font-weight: bold; 
        margin-top: 5px; 
    }
    
    .insight-card {
        background-color: #1C202C;
        border-left: 5px solid #0088FF;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .insight-alert {
        background-color: #1C202C;
        border-left: 5px solid #E6007E;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .insight-success {
        background-color: #1C202C;
        border-left: 5px solid #A3FF00;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado visual Pharmadvisor
st.markdown("""
    <div class="ph-header">
        <div>
            <h1 class="ph-title">E Metrics BI Executive</h1>
            <span style="color: #9AA5B1; font-size: 13px;">Servicio CRM y de Productividad para su negocio farmacéutico</span>
        </div>
        <div style="text-align: right;">
            <span style="color: #E6007E; font-weight: bold; font-size: 20px;">Pharm<span style="color: #FFFFFF;">ADVISOR</span></span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Función para calcular duplicidad
def get_copy_paste_rate(df_sub):
    total = len(df_sub)
    if total == 0:
        return 0.0
    max_freq = df_sub['Comentario_str'].value_counts().max() if 'Comentario_str' in df_sub.columns else 0
    if (max_freq / total) >= 0.95 and total >= 10:
        return 100.0
    dup_cnt = df_sub.duplicated(subset=['Comentario_str']).sum() if 'Comentario_str' in df_sub.columns else 0
    return round((dup_cnt / total) * 100, 1)

# EVALUACIÓN DE TÉCNICA DE VENTAS Y ACUERDOS PHARMADVISOR (7 PASOS / SOLUCIÓN 1 PENALIZACIÓN)
def evaluar_tecnica_pharmadvisor(row, dup_series):
    comentario = str(row.get('Comentario_str', '')).lower().strip()
    
    # SOLUCIÓN 1: Penalización inmediata si el comentario está duplicado (Copy-Paste)
    if dup_series.get(row.name, False):
        return "Baja Calidad (Trámite / Copy-Paste)"
    
    if len(comentario) < 10 or comentario in ['nan', 'none', '-', '', 'se realiza visita', 'se deja muestra', 'se saluda']:
        return "Baja Calidad (Trámite / Copy-Paste)"
    
    # Palabras clave del Modelo Pharmadvisor (Cierre de Acuerdo / Venta / Compromiso Comercial)
    kw_cierre_acuerdo = [
        'acuerdo', 'compromiso', 'acepta', 'iniciar', 'reiniciar', 'aumentar', 'sostener', 'mantener', 
        'probar', 'prescribira', 'prescribirá', 'formulard', 'pedido', 'millones', 'millos', 'se logró', 
        'se logro', 'aprobado', 'conciliar', 'gestiono', 'gestionó'
    ]
    kw_actitud_manejo = [
        'objecion', 'objeción', 'indiferente', 'esceptico', 'escéptico', 'costo', 'sabor', 'mipres', 
        'eps', 'cambia', 'prefiere', 'mencion', 'pqr', 'cartera', 'revisó', 'reviso', 'cotización', 'cotizacion'
    ]
    kw_beneficios_historia = [
        'beneficio', 'ventaja', 'diferencia', 'estudio', 'evidencia', 'paciente', 'tolerancia', 
        'adherencia', 'falla de medro', 'alergia', 'aplv', 'precio', 'descuento', 'portafolio'
    ]

    # Detección de cierres negativos o quejas no resueltas
    if any(k in comentario for k in ['queja', 'bloqueo', 'no alcanza', 'perdieron', 'diferencia quedamos']):
        return "Baja Calidad (Trámite / Copy-Paste)"

    has_cierre = any(k in comentario for k in kw_cierre_acuerdo)
    has_actitud = any(k in comentario for k in kw_actitud_manejo)
    has_beneficio = any(k in comentario for k in kw_beneficios_historia)

    # Nivel 1: Alta Calidad (Persuasión y Cierre de Acuerdo - Pasos 4 a 7 de Pharmadvisor)
    if (has_cierre and (has_beneficio or has_actitud)) or (has_cierre and any(char.isdigit() for char in comentario)):
        return "Alta Calidad (Persuasión / Cierre de Acuerdo)"
    
    # Nivel 2: Calidad Media (Seguimiento / Historia de Beneficios / Gestión)
    elif has_beneficio or has_actitud or has_cierre:
        return "Calidad Media (Historia de Beneficios)"
    
    # Nivel 3: Baja Calidad (Trámite de Muestras o Sin Propuesta)
    else:
        return "Baja Calidad (Trámite / Copy-Paste)"

def normalizar_categoria(val):
    if pd.isna(val): return 'Médico Estándar / Sin Cat.'
    val_str = str(val).strip().upper()
    if val_str in ['NAN', 'NONE', '', 'NULL', '-']: return 'Médico Estándar / Sin Cat.'
    if 'TOP' in val_str: return 'Médico TOP'
    return 'Médico Estándar / Sin Cat.'

def normalizar_pareto(val):
    if pd.isna(val): return 'Institución No Pareto'
    val_str = str(val).strip().upper()
    if val_str in ['NAN', 'NONE', '', 'NULL', 'NO', 'FALSE', '0', '-']: return 'Institución No Pareto'
    if any(k in val_str for k in ['SI', 'SÍ', 'PARETO', '1', 'TRUE']): return 'Institución Pareto'
    return 'Institución No Pareto'

uploaded_file = st.file_uploader("Cargar Reporte de Visitas (Excel / CSV)", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]

    df_clean = df.drop_duplicates(subset=['Cod. visita']).copy() if 'Cod. visita' in df.columns else df.copy()

    # DETECCIÓN AUTOMÁTICA DEL CAMPO PRINCIPAL DE TEXTO (Comentario vs. Acuerdo Logrado)
    col_acuerdo_list = [c for c in df_clean.columns if 'acuerdo' in str(c).lower()]
    col_comentario_list = [c for c in df_clean.columns if 'comentario' in str(c).lower() and 'impacto' not in str(c).lower()]
    
    col_acuerdo_name = col_acuerdo_list[0] if col_acuerdo_list else None
    col_comentario_name = col_comentario_list[0] if col_comentario_list else None

    def extraer_texto_evaluacion(row):
        acuerdo_val = str(row.get(col_acuerdo_name, '')).strip() if col_acuerdo_name else ''
        comentario_val = str(row.get(col_comentario_name, '')).strip() if col_comentario_name else ''
        
        # Prioridad a 'Acuerdo logrado' si 'Comentario' es nulo, vacio o '-'
        if (pd.isna(comentario_val) or comentario_val in ['-', '', 'nan', 'None']) and acuerdo_val not in ['-', '', 'nan', 'None']:
            return acuerdo_val
        return comentario_val

    df_clean['Comentario_str'] = df_clean.apply(extraer_texto_evaluacion, axis=1)
    df_clean['Objetivo_str'] = df_clean['Objetivo'].astype(str).str.strip() if 'Objetivo' in df_clean.columns else ""

    col_cat = 'Categoría' if 'Categoría' in df_clean.columns else ('Categoria' if 'Categoria' in df_clean.columns else None)
    col_pareto = [c for c in df_clean.columns if 'pareto' in c.lower()]
    col_pareto_name = col_pareto[0] if col_pareto else None
    
    col_ciclo = [c for c in df_clean.columns if 'ciclo' in c.lower()]
    col_ciclo_name = col_ciclo[0] if col_ciclo else None

    # BÚSQUEDA SEGURA Y DINÁMICA DE COLUMNAS DE MÉDICO / CLIENTE Y REPRESENTANTE
    doc_candidates = [c for c in df_clean.columns if any(k in str(c).lower() for k in ['único', 'unico', 'médico', 'medico', 'cliente', 'nombre'])]
    if doc_candidates:
        doc_id_col = doc_candidates[0]
    else:
        df_clean['ID_Temp_Medico'] = df_clean.index
        doc_id_col = 'ID_Temp_Medico'

    rep_candidates = [c for c in df_clean.columns if any(k in str(c).lower() for k in ['representante', 'visitador', 'rep'])]
    col_rep_name = rep_candidates[0] if rep_candidates else None

    # Búsqueda de Persona Contactada
    contacto_candidates = [c for c in df_clean.columns if any(k in str(c).lower() for k in ['nombres y apellidos', 'persona visitada', 'contacto'])]
    col_contacto_name = contacto_candidates[0] if contacto_candidates else doc_id_col

    df_clean['Cat_Clean'] = df_clean[col_cat].apply(normalizar_categoria) if col_cat else 'Médico Estándar / Sin Cat.'
    df_clean['Pareto_Clean'] = df_clean[col_pareto_name].apply(normalizar_pareto) if col_pareto_name else 'Institución No Pareto'

    # Detección de Duplicados Globales
    dup_mask = df_clean.duplicated(subset=['Comentario_str'], keep=False) & (df_clean['Comentario_str'] != "") & (df_clean['Comentario_str'] != "-")
    df_clean['Nivel_Tecnica_Ventas'] = df_clean.apply(lambda r: evaluar_tecnica_pharmadvisor(r, dup_mask), axis=1)

    # FILTROS GLOBALES EN CASCADA (MULTISELECT)
    df_step = df_clean.copy()

    c_f0, c_f1, c_f2, c_f3, c_f4, c_f5 = st.columns([1, 1.2, 1.2, 1.2, 1, 0.8])
    
    with c_f0:
        if col_ciclo_name:
            ciclos_opt = sorted([str(x) for x in df_step[col_ciclo_name].dropna().unique()])
            sel_ciclo = st.multiselect("Ciclo", ciclos_opt)
            if sel_ciclo:
                df_step = df_step[df_step[col_ciclo_name].astype(str).isin(sel_ciclo)]

    with c_f1:
        reg_opt = sorted([str(x) for x in df_step['Región'].dropna().unique()]) if 'Región' in df_step.columns else []
        sel_region = st.multiselect("Coordinación Regional", reg_opt)
        if sel_region and 'Región' in df_step.columns:
            df_step = df_step[df_step['Región'].astype(str).isin(sel_region)]

    with c_f2:
        lin_opt = sorted([str(x) for x in df_step['Línea'].dropna().unique()]) if 'Línea' in df_step.columns else []
        sel_linea = st.multiselect("Línea de Producto", lin_opt)
        if sel_linea and 'Línea' in df_step.columns:
            df_step = df_step[df_step['Línea'].astype(str).isin(sel_linea)]

    with c_f3:
        rep_opt = sorted([str(x) for x in df_step[col_rep_name].dropna().unique()]) if col_rep_name else []
        sel_rep = st.multiselect("Representante (SFE)", rep_opt)
        if sel_rep and col_rep_name:
            df_step = df_step[df_step[col_rep_name].astype(str).isin(sel_rep)]

    with c_f4:
        cat_opt = sorted([str(x) for x in df_step['Cat_Clean'].dropna().unique()])
        sel_cat = st.multiselect("Categoría Médico / Cliente", cat_opt)
        if sel_cat:
            df_step = df_step[df_step['Cat_Clean'].astype(str).isin(sel_cat)]

    with c_f5:
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        only_pareto = st.checkbox("Solo Cuentas Pareto 🏥", value=False)
        if only_pareto:
            df_step = df_step[df_step['Pareto_Clean'] == 'Institución Pareto']

    df_filtered = df_step.copy()

    total_visitas = len(df_filtered)
    medicos = df_filtered[doc_id_col].nunique() if doc_id_col in df_filtered.columns else 0

    pct_dup = get_copy_paste_rate(df_filtered)
    cnt_dup_total = int(round((pct_dup / 100) * total_visitas))
    cnt_alta_calidad = (df_filtered['Nivel_Tecnica_Ventas'] == "Alta Calidad (Persuasión / Cierre de Acuerdo)").sum()
    pct_alta_calidad = round((cnt_alta_calidad / total_visitas * 100), 1) if total_visitas > 0 else 0

    # TARJETAS KPI
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-label">TOTAL VISITAS ÚNICAS</div><div class="kpi-value">{total_visitas:,}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-label">MÉDICOS / CLIENTES CONTACTADOS</div><div class="kpi-value">{medicos:,}</div></div>', unsafe_allow_html=True)
    color_dup = '#E6007E' if pct_dup > 50 else '#A3FF00'
    k3.markdown(f'<div class="kpi-card"><div class="kpi-label">TASA COPY-PASTE</div><div class="kpi-value" style="color:{color_dup};">{pct_dup:.1f}%</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card"><div class="kpi-label">ÍNDICE PERSUASIÓN & ACUERDO</div><div class="kpi-value" style="color:#0088FF;">{pct_alta_calidad}%</div></div>', unsafe_allow_html=True)

    st.markdown("###")

    tab_reg, tab_linea, tab_insights = st.tabs([
        "🏛️ GERENCIAS REGIONALES (SFE & Targeting TOP)", 
        "📦 GERENCIAS DE LÍNEA & TÉCNICA DE VENTAS",
        "💡 HALLAZGOS ESTRATÉGICOS C-LEVEL"
    ])

    # --- PESTAÑA 1: GERENCIAS REGIONALES ---
    with tab_reg:
        st.subheader("Auditoría Territorial y Alignment: Médicos/Clientes TOP vs. Cuentas Pareto")
        
        r1, r2 = st.columns(2)
        with r1:
            if 'Región' in df_filtered.columns and total_visitas > 0:
                reg_list = [{'Región': r, '% Duplicidad': get_copy_paste_rate(grp)} for r, grp in df_filtered.groupby('Región')]
                fig1 = px.bar(pd.DataFrame(reg_list), x='Región', y='% Duplicidad', color='% Duplicidad',
                              color_continuous_scale=['#0088FF', '#E6007E'], template='plotly_dark', title='<b>1. Índice de Copy-Paste por Región (%)</b>')
                fig1.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=330)
                st.plotly_chart(fig1, use_container_width=True)

        with r2:
            if col_rep_name:
                rep_list = [{'Representante': r, '% Copy-Paste': get_copy_paste_rate(grp)} 
                            for r, grp in df_filtered.groupby(col_rep_name) if len(grp) >= 1]
                rep_df = pd.DataFrame(rep_list).sort_values(by='% Copy-Paste', ascending=False).head(10)
                fig2 = px.bar(rep_df, x='% Copy-Paste', y='Representante', orientation='h', color='% Copy-Paste',
                              color_continuous_scale=['#0088FF', '#E6007E'], template='plotly_dark', title='<b>2. Top 10 Reps en Alerta Copy-Paste</b>')
                fig2.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=330, yaxis={'autorange': 'reversed'})
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("###")
        p1, p2 = st.columns(2)
        
        with p1:
            if total_visitas > 0:
                doc_cat_df = df_filtered.groupby(doc_id_col)['Cat_Clean'].first().value_counts().reset_index()
                doc_cat_df.columns = ['Categoría', 'Contactos Únicos']
                fig_cat_pie = px.pie(doc_cat_df, names='Categoría', values='Contactos Únicos', hole=0.5,
                                     template='plotly_dark', title='<b>3. Composición del Panel de Contactos Únicos (TOP vs Estándar)</b>',
                                     color_discrete_map={'Médico TOP': '#E6007E', 'Médico Estándar / Sin Cat.': '#0088FF'})
                fig_cat_pie.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=330)
                st.plotly_chart(fig_cat_pie, use_container_width=True)

        with p2:
            if total_visitas > 0:
                cross_df = df_filtered.groupby([doc_id_col, 'Cat_Clean'])['Pareto_Clean'].first().reset_index()
                ct = pd.crosstab(cross_df['Cat_Clean'], cross_df['Pareto_Clean'])
                
                v_top_no_pareto = ct.loc['Médico TOP', 'Institución No Pareto'] if ('Médico TOP' in ct.index and 'Institución No Pareto' in ct.columns) else 0
                v_top_pareto = ct.loc['Médico TOP', 'Institución Pareto'] if ('Médico TOP' in ct.index and 'Institución Pareto' in ct.columns) else 0
                v_est_no_pareto = ct.loc['Médico Estándar / Sin Cat.', 'Institución No Pareto'] if ('Médico Estándar / Sin Cat.' in ct.index and 'Institución No Pareto' in ct.columns) else 0
                v_est_pareto = ct.loc['Médico Estándar / Sin Cat.', 'Institución Pareto'] if ('Médico Estándar / Sin Cat.' in ct.index and 'Institución Pareto' in ct.columns) else 0

                tot_top = v_top_no_pareto + v_top_pareto
                tot_est = v_est_no_pareto + v_est_pareto

                p_top_no_pareto = round((v_top_no_pareto / tot_top * 100), 1) if tot_top > 0 else 0
                p_top_pareto = round((v_top_pareto / tot_top * 100), 1) if tot_top > 0 else 0
                p_est_no_pareto = round((v_est_no_pareto / tot_est * 100), 1) if tot_est > 0 else 0
                p_est_pareto = round((v_est_pareto / tot_est * 100), 1) if tot_est > 0 else 0

                color_matrix = [[0.2, 1.0], [0.0, 0.6]]
                text_matrix = [
                    [f"<b>{v_top_no_pareto:,}</b><br>({p_top_no_pareto}%)", f"<b>{v_top_pareto:,}</b><br>({p_top_pareto}%)"],
                    [f"<b>{v_est_no_pareto:,}</b><br>({p_est_no_pareto}%)", f"<b>{v_est_pareto:,}</b><br>({p_est_pareto}%)"]
                ]

                sem_colorscale = [
                    [0.0, '#2D3346'],
                    [0.2, '#E6007E'],
                    [0.6, '#FFB300'],
                    [1.0, '#A3FF00']
                ]

                fig_cross = px.imshow(
                    color_matrix,
                    x=['Institución No Pareto', 'Institución Pareto'],
                    y=['Médico TOP', 'Médico Estándar / Sin Cat.'],
                    color_continuous_scale=sem_colorscale,
                    template='plotly_dark',
                    title='<b>4. Matriz Alignment Semáforo: Ubicación de Contactos TOP</b>'
                )

                fig_cross.update_traces(
                    text=text_matrix,
                    texttemplate="%{text}",
                    textfont=dict(size=16, color="white")
                )

                fig_cross.update_layout(
                    paper_bgcolor='#1C202C', 
                    plot_bgcolor='#2D3346', 
                    height=330, 
                    coloraxis_showscale=False,
                    xaxis_title="Tipo de Institución",
                    yaxis_title="Categoría Contacto"
                )
                st.plotly_chart(fig_cross, use_container_width=True)

        st.markdown("#### Tabla de Control de la Fuerza de Ventas")
        if col_rep_name:
            tabla_sfe = pd.DataFrame([
                {
                    'Coordinación': grp['Región'].iloc[0] if 'Región' in grp.columns else 'N/A',
                    'Línea': grp['Línea'].iloc[0] if 'Línea' in grp.columns else 'N/A',
                    'Representante': r,
                    'Visitas Totales': len(grp),
                    'Contactos Únicos': grp[doc_id_col].nunique(),
                    'Contactos TOP': grp[grp['Cat_Clean']=='Médico TOP'][doc_id_col].nunique(),
                    '% Visitas Pareto': round((grp['Pareto_Clean'].value_counts().get('Institución Pareto', 0) / len(grp)) * 100, 1),
                    '% Copy-Paste': get_copy_paste_rate(grp)
                } for r, grp in df_filtered.groupby(col_rep_name)
            ]).sort_values(by='% Copy-Paste', ascending=False)
            st.dataframe(tabla_sfe, use_container_width=True)

    # --- PESTAÑA 2: GERENCIAS DE LÍNEA & TÉCNICA DE VENTAS ---
    with tab_linea:
        st.subheader("Análisis de Marcas, Share of Voice y Técnica de Ventas / Acuerdos (Pharmadvisor)")
        l1, l2 = st.columns(2)

        with l1:
            calidad_df = df_filtered['Nivel_Tecnica_Ventas'].value_counts().reset_index()
            calidad_df.columns = ['Nivel de Calidad', 'Visitas']
            
            color_semaforo_map = {
                'Alta Calidad (Persuasión / Cierre de Acuerdo)': '#4CAF50',
                'Calidad Media (Historia de Beneficios)': '#FFB300',
                'Baja Calidad (Trámite / Copy-Paste)': '#E53935'
            }

            fig_cal = px.pie(
                calidad_df, 
                names='Nivel de Calidad', 
                values='Visitas', 
                hole=0.5,
                color='Nivel de Calidad',
                color_discrete_map=color_semaforo_map,
                template='plotly_dark', 
                title='<b>1. Calidad de Visita / Cierre de Acuerdo (Modelo Pharmadvisor)</b>'
            )
            fig_cal.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=350)
            st.plotly_chart(fig_cal, use_container_width=True)

        with l2:
            prods = ['Fortini', 'Infatrini', 'Ketocal', 'Pepti', 'Syneo', 'Neocate', 'Anamix']
            prod_data = [{'Producto': p, 'Visitas': df_filtered['Comentario_str'].str.contains(p, case=False, na=False).sum()} for p in prods]
            prod_df = pd.DataFrame(prod_data).sort_values(by='Visitas', ascending=False)
            
            fig3 = px.bar(
                prod_df, 
                x='Producto', 
                y='Visitas', 
                color='Visitas',
                color_continuous_scale=['#263238', '#0088FF', '#4DD0E1'], 
                template='plotly_dark', 
                title='<b>2. Menciones por Producto (Share of Voice)</b>'
            )
            fig3.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=350)
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("###")
        themes = {
            'Gestión Comercial / Pedidos / Montos': 'pedido|millones|millos|aprobado|recaudo|cartera',
            'Trámites Mipres / EPS / PQR': 'mipres|eps|autorizacion|pqr|devolución|devolucion',
            'Beneficios de Producto / Portafolio': 'beneficio|ventaja|portafolio|muestra|presentación',
            'Programa Pacientes (PAP)': 'pap|programa|fundacion|fundación',
            'Competencia Mencionada': 's-26|s26|similac|nan|althera|nutramigen|precios'
        }
        theme_data = [{'Eje Temático': t_name, 'Visitas': df_filtered['Comentario_str'].str.contains(t_kw, case=False, na=False).sum()} for t_name, t_kw in themes.items()]
        theme_df = pd.DataFrame(theme_data).sort_values(by='Visitas', ascending=True)
        
        fig4 = px.bar(
            theme_df, 
            y='Eje Temático', 
            x='Visitas', 
            orientation='h',
            color='Visitas', 
            color_continuous_scale=['#263238', '#4DD0E1'], 
            template='plotly_dark',
            title='<b>3. Ejes Temáticos, Gestiones y Barreras detectadas</b>'
        )
        fig4.update_layout(paper_bgcolor='#1C202C', plot_bgcolor='#2D3346', height=320)
        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 💬 Módulos de Voz del Cliente (Comentarios y Acuerdos Reales)")
        
        subset_dup = [col_rep_name, 'Comentario_str'] if col_rep_name else ['Comentario_str']
        comentarios_genuinos = df_filtered[~df_filtered.duplicated(subset=subset_dup, keep=False)].copy()
        
        c1, c2 = st.columns([1, 1])
        with c1:
            filtro_nivel = st.selectbox("Filtrar por Nivel de Calidad Comercial:", 
                                        ["Todos los Comentarios Genuinos", "Alta Calidad (Persuasión / Cierre de Acuerdo)", "Calidad Media (Historia de Beneficios)", "Baja Calidad (Trámite / Copy-Paste)"])
        with c2:
            kw_input = st.text_input("🔍 Buscar por Palabra Clave (Ej: Pedido, Cartera, Mipres, PQR, Competencia, Millones)", "")

        comentarios_display = comentarios_genuinos.copy()
        if filtro_nivel != "Todos los Comentarios Genuinos":
            comentarios_display = comentarios_display[comentarios_display['Nivel_Tecnica_Ventas'] == filtro_nivel]
        if kw_input:
            comentarios_display = comentarios_display[comentarios_display['Comentario_str'].str.contains(kw_input, case=False, na=False)]

        cols_vista = ['Línea', col_rep_name, doc_id_col, col_contacto_name, 'Objetivo_str', 'Comentario_str', 'Cat_Clean', 'Pareto_Clean']
        cols_presentes = [c for c in cols_vista if c in comentarios_display.columns]

        st.markdown(f"**Se encontraron {len(comentarios_display):,} observaciones / acuerdos cualitativos:**")
        st.dataframe(
            comentarios_display[cols_presentes].rename(columns={
                col_rep_name: 'Representante',
                doc_id_col: 'Cliente / Institución',
                col_contacto_name: 'Persona Contactada',
                'Objetivo_str': 'Objetivo Registrado',
                'Comentario_str': 'Comentario / Acuerdo Logrado',
                'Cat_Clean': 'Categoría',
                'Pareto_Clean': 'Institución Pareto'
            }),
            use_container_width=True,
            height=300
        )

    # --- PESTAÑA 3: HALLAZGOS ESTRATÉGICOS COMPLETOS ---
    with tab_insights:
        st.subheader("💡 Resumen Ejecutivo & Sustentación Cuantitativa Integral (C-Level)")
        st.caption("Síntesis automática basada en el modelo de Persuasión y Acuerdos Pharmadvisor.")

        cnt_baja_calidad = (df_filtered['Nivel_Tecnica_Ventas'] == "Baja Calidad (Trámite / Copy-Paste)").sum()
        pct_baja_calidad = round((cnt_baja_calidad / total_visitas * 100), 1) if total_visitas > 0 else 0

        docs_top = df_filtered[df_filtered['Cat_Clean']=='Médico TOP'][doc_id_col].nunique() if doc_id_col in df_filtered.columns else 0
        pct_top = round((docs_top / medicos) * 100, 1) if medicos > 0 else 0

        docs_top_pareto = df_filtered[(df_filtered['Cat_Clean']=='Médico TOP') & (df_filtered['Pareto_Clean']=='Institución Pareto')][doc_id_col].nunique() if doc_id_col in df_filtered.columns else 0
        pct_top_in_pareto = round((docs_top_pareto / docs_top) * 100, 1) if docs_top > 0 else 0
        docs_top_no_pareto = docs_top - docs_top_pareto

        cnt_mipres = df_filtered['Comentario_str'].str.contains('mipres|eps|autorizacion|formulacion|pqr', case=False, na=False).sum()
        pct_mipres = round((cnt_mipres / total_visitas) * 100, 1) if total_visitas > 0 else 0

        st.markdown(f"""
        <div class="insight-alert">
            <h4 style="color:#E6007E; margin-top:0;">🚨 1. Auditoría de Disciplina Operativa & Cobertura (SFE)</h4>
            <p>Se auditó un volumen de <b>{total_visitas:,} visitas/gestiones</b> realizadas a <b>{medicos:,} contactos únicos</b>, encontrando una tasa de duplicidad del <b>{pct_dup}% ({cnt_dup_total:,} visitas copy-paste)</b>.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-card">
            <h4 style="color:#0088FF; margin-top:0;">🎯 2. Evaluación Cualitativa de Acuerdos (Modelo Pharmadvisor)</h4>
            <p>Bajo la metodología de Persuasión y Cierre de Acuerdo, un <b>{pct_alta_calidad}% ({cnt_alta_calidad:,} registros)</b> alcanzaron acuerdos comerciales concretos o compromisos de acción inmediata.</p>
            <ul>
                <li><b>Seguimiento y Trámite:</b> Un <b>{pct_baja_calidad}% ({cnt_baja_calidad:,} registros)</b> corresponden a frases vacías, quejas no resueltas o registros duplicados.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("Por favor arrastra y suelta el archivo Excel de visitas para desplegar el Dashboard Ejecutivo.")
