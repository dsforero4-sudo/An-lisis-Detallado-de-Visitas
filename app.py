import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# 1. Configuración de página con Tema Oscuro (Dark Theme)
st.set_page_config(
    page_title="Pharmadvisor | E-Metrics BI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS Personalizados
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
    </style>
""", unsafe_allow_html=True)

st.title("E-Metrics BI — Pharmadvisor")
st.caption("Panel de Control & Auditoría de Calidad de Visitas Médicas (Interactivo en Vivo)")

# Función para calcular la Tasa Real de Copy-Paste
def get_copy_paste_rate(df_sub):
    total = len(df_sub)
    if total == 0:
        return 0.0
    
    # Si hay una frase principal que cubre >= 95% de las visitas del representante/subconjunto
    max_freq = df_sub['Comentario_str'].value_counts().max() if 'Comentario_str' in df_sub.columns else 0
    if (max_freq / total) >= 0.95 and total >= 10:
        return 100.0
    
    # Cálculo estándar de duplicidad
    dup_cnt = df_sub.duplicated(subset=['Comentario_str']).sum() if 'Comentario_str' in df_sub.columns else 0
    return round((dup_cnt / total) * 100, 1)

# 2. Carga de Archivo Excel/CSV
uploaded_file = st.file_uploader("Cargar Reporte de Visitas (Excel / CSV)", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    # Carga de datos
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]

    if 'Cod. visita' in df.columns:
        df_clean = df.drop_duplicates(subset=['Cod. visita']).copy()
    else:
        df_clean = df.copy()

    df_clean['Comentario_str'] = df_clean['Comentario'].astype(str).str.strip() if 'Comentario' in df_clean.columns else ""

    # 3. Barra de Filtros Dinámicos (Píldoras Superiores)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        regiones = ["Todas"] + sorted([str(x) for x in df_clean['Región'].dropna().unique()]) if 'Región' in df_clean.columns else ["Todas"]
        sel_region = st.selectbox("Región / Coordinación", regiones)

    with col2:
        lineas = ["Todas"] + sorted([str(x) for x in df_clean['Línea'].dropna().unique()]) if 'Línea' in df_clean.columns else ["Todas"]
        sel_linea = st.selectbox("Línea de Producto", lineas)

    with col3:
        reps = ["Todas"] + sorted([str(x) for x in df_clean['Representante'].dropna().unique()]) if 'Representante' in df_clean.columns else ["Todas"]
        sel_rep = st.selectbox("Representante", reps)

    # Filtrado dinámico
    df_filtered = df_clean.copy()
    if sel_region != "Todas":
        df_filtered = df_filtered[df_filtered['Región'] == sel_region]
    if sel_linea != "Todas":
        df_filtered = df_filtered[df_filtered['Línea'] == sel_linea]
    if sel_rep != "Todas":
        df_filtered = df_filtered[df_filtered['Representante'] == sel_rep]

    # Cálculos
    total_visitas = len(df_filtered)
    medicos = df_filtered['Médicos'].nunique() if 'Médicos' in df_filtered.columns else 0
    pct_dup = get_copy_paste_rate(df_filtered)
    score_calidad = max(0, round(100 - pct_dup, 1))

    # 4. Tarjetas KPI
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-label">TOTAL VISITAS</div><div class="kpi-value">{total_visitas:,}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-label">CONTACTOS ÚNICOS</div><div class="kpi-value">{medicos:,}</div></div>', unsafe_allow_html=True)
    
    color_dup = '#FF5252' if pct_dup > 50 else '#4CAF50'
    k3.markdown(f'<div class="kpi-card"><div class="kpi-label">TASA COPY-PASTE</div><div class="kpi-value" style="color:{color_dup};">{pct_dup:.1f}%</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card"><div class="kpi-label">SCORE CALIDAD</div><div class="kpi-value">{score_calidad}/100</div></div>', unsafe_allow_html=True)

    st.markdown("###")

    # 5. Gráficos Plotly Totalmente Dinámicos
    g1, g2 = st.columns(2)

    with g1:
        if 'Región' in df_filtered.columns and total_visitas > 0:
            reg_list = [{'Región': r, '% Duplicidad': get_copy_paste_rate(grp)} 
                        for r, grp in df_filtered.groupby('Región')]
            reg_df = pd.DataFrame(reg_list)
            
            fig1 = px.bar(reg_df, x='Región', y='% Duplicidad', color='% Duplicidad',
                          color_continuous_scale='Reds', template='plotly_dark',
                          title='<b>1. Nivel de Copy-Paste por Región (%)</b>')
            fig1.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=350)
            st.plotly_chart(fig1, use_container_width=True)

    with g2:
        prods = ['Fortini', 'Infatrini', 'Ketocal', 'Pepti', 'Syneo', 'Neocate', 'Anamix']
        prod_data = [{'Producto': p, 'Visitas': df_filtered['Comentario_str'].str.contains(p, case=False, na=False).sum()} for p in prods]
        prod_df = pd.DataFrame(prod_data).sort_values(by='Visitas', ascending=False)
        
        fig2 = px.bar(prod_df, x='Producto', y='Visitas', color='Visitas',
                      color_continuous_scale='Blues', template='plotly_dark',
                      title='<b>2. Cobertura de Marcas Mencionadas</b>')
        fig2.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=350)
        st.plotly_chart(fig2, use_container_width=True)

    g3, g4 = st.columns(2)

    with g3:
        themes = {
            'Beneficios de Producto': 'syneo|pepti|infatrini|fortini|neocate|ketocal',
            'Programa Pacientes (PAP)': 'pap|programa|fundacion|fundación',
            'Trámites Mipres / EPS': 'mipres|eps|autorizacion|autorización|formulacion',
            'Inicios / Muestras': 'inicio|inicios|muestra|muestras|probando',
            'Competencia': 's-26|s26|similac|nan|althera|nutramigen'
        }
        theme_data = [{'Eje Temático': t_name, 'Visitas': df_filtered['Comentario_str'].str.contains(t_kw, case=False, na=False).sum()} for t_name, t_kw in themes.items()]
        theme_df = pd.DataFrame(theme_data).sort_values(by='Visitas', ascending=True)

        fig3 = px.bar(theme_df, y='Eje Temático', x='Visitas', orientation='h',
                      color='Visitas', color_continuous_scale='Greens', template='plotly_dark',
                      title='<b>3. Ejes Temáticos y Barreras en Consultorio</b>')
        fig3.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=350)
        st.plotly_chart(fig3, use_container_width=True)

    with g4:
        if 'Representante' in df_filtered.columns:
            rep_list = [{'Representante': r, '% Copy-Paste': get_copy_paste_rate(grp)} 
                        for r, grp in df_filtered.groupby('Representante') if len(grp) >= 5]
            rep_df = pd.DataFrame(rep_list).sort_values(by='% Copy-Paste', ascending=False).head(10)

            fig4 = px.bar(rep_df, x='% Copy-Paste', y='Representante', orientation='h', color='% Copy-Paste',
                          color_continuous_scale='Reds', template='plotly_dark',
                          title='<b>4. Top 10 Reps — Mayor Riesgo Copy-Paste (%)</b>')
            fig4.update_layout(paper_bgcolor='#1A1F2C', plot_bgcolor='#262C3A', height=350, yaxis={'autorange': 'reversed'})
            st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("Por favor arrastra y suelta el archivo Excel de visitas para desplegar el Dashboard.")
