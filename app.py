# --- SECCIÓN 4: ANÁLISIS COMPARATIVO POR INSTITUCIÓN ---
    st.markdown("---")
    st.subheader("Análisis por Institución: Volumen de Médicos vs. Frecuencia de Visita")

    # Selector multiselección de instituciones basado en el DataFrame filtrado previamente por Distrito/Línea/Representante
    instituciones_disponibles = sorted(df_final['Institución 1.1'].dropna().unique())
    selected_instituciones = st.multiselect(
        "Seleccionar Institución(es) para comparar:",
        options=instituciones_disponibles,
        default=instituciones_disponibles[:10] if len(instituciones_disponibles) >= 10 else instituciones_disponibles
    )

    if selected_instituciones:
        df_inst_filtered = df_final[df_final['Institución 1.1'].isin(selected_instituciones)]
        
        # Agrupar por institución
        inst_summary = df_inst_filtered.groupby('Institución 1.1').agg(
            Cantidad_Medicos=('Código', 'count'),
            Frecuencia_Promedio=('Ind Frecuencia médico', 'mean')
        ).reset_index()
        
        # Ordenar por cantidad de médicos de mayor a menor para mejor visualización
        inst_summary = inst_summary.sort_values(by='Cantidad_Medicos', ascending=False)

        # Gráfica de barras dual / combinada con Plotly
        fig_inst_comp = px.bar(
            inst_summary, x='Institución 1.1', y='Cantidad_Medicos',
            text='Cantidad_Medicos', template='plotly_dark',
            title="<b>Cantidad de Médicos por Institución Seleccionada</b>",
            color_discrete_sequence=['#0088FF']
        )
        fig_inst_comp.update_traces(textposition='outside')
        fig_inst_comp.update_layout(
            paper_bgcolor='#1C202C',
            plot_bgcolor='#2D3346',
            height=420,
            xaxis_title="Institución",
            yaxis_title="Cantidad de Médicos",
            xaxis={'tickangle': -30},
            margin=dict(t=50, b=100, l=40, r=20)
        )
        st.plotly_chart(fig_inst_comp, use_container_width=True)

        # Tabla detallada complementaria
        st.markdown("##### Detalle de Frecuencia Promedio e Indicadores por Institución")
        inst_summary_display = inst_summary.copy()
        inst_summary_display.columns = ['Institución', 'Cantidad de Médicos', 'Frecuencia Promedio']
        inst_summary_display['Frecuencia Promedio'] = inst_summary_display['Frecuencia Promedio'].round(2)
        st.dataframe(inst_summary_display, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ Por favor selecciona al menos una institución en el filtro superior para visualizar la comparativa.")
