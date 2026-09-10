# --- SECCIÓN 4: ANÁLISIS COMPARATIVO POR INSTITUCIÓN (BUBBLE / TREEMAP) ---
    st.markdown("---")
    st.subheader("Análisis por Institución: Tamaño por Frecuencia y Volumen de Médicos")

    instituciones_disponibles = sorted(df_final['Institución 1.1'].dropna().unique())
    selected_instituciones = st.multiselect(
        "Seleccionar Institución(es) para comparar:",
        options=instituciones_disponibles,
        default=instituciones_disponibles[:15] if len(instituciones_disponibles) >= 15 else instituciones_disponibles
    )

    if selected_instituciones:
        df_inst_filtered = df_final[df_final['Institución 1.1'].isin(selected_instituciones)]
        
        inst_summary = df_inst_filtered.groupby('Institución 1.1').agg(
            Cantidad_Medicos=('Código', 'count'),
            Frecuencia_Promedio=('Ind Frecuencia médico', 'mean')
        ).reset_index()
        
        total_sel = inst_summary['Cantidad_Medicos'].sum()
        inst_summary['Porcentaje'] = (inst_summary['Cantidad_Medicos'] / total_sel * 100) if total_sel > 0 else 0
        
        # Crear etiqueta personalizada: Porcentaje + Número de médicos
        inst_summary['Etiqueta'] = inst_summary.apply(
            lambda row: f"{row['Porcentaje']:.1f}% ({int(row['Cantidad_Medicos'])})", axis=1
        )
        
        inst_summary = inst_summary.sort_values(by='Cantidad_Medicos', ascending=False)

        # Gráfica de burbujas (Scatter) donde el tamaño está en función de la frecuencia
        fig_bubble = px.scatter(
            inst_summary, 
            x='Institución 1.1', 
            y='Cantidad_Medicos',
            size='Frecuencia_Promedio', 
            color='Frecuencia_Promedio',
            text='Etiqueta',
            color_continuous_scale='Bluered',
            template='plotly_dark',
            title="<b>Instituciones: Volumen de Médicos y Tamaño por Frecuencia de Visita</b>"
        )
        
        fig_bubble.update_traces(
            textposition='top center',
            textfont_size=11
        )
        
        fig_bubble.update_layout(
            paper_bgcolor='#1C202C',
            plot_bgcolor='#2D3346',
            height=480,
            xaxis_title="Institución",
            yaxis_title="Cantidad de Médicos",
            xaxis={'tickangle': -35},
            margin=dict(t=60, b=120, l=40, r=20),
            coloraxis_colorbar=dict(title="Freq. Promedio")
        )
        
        st.plotly_chart(fig_bubble, use_container_width=True)

        # Tabla detallada complementaria
        st.markdown("##### Detalle de Frecuencia, Porcentaje y Médicos por Institución")
        inst_summary_display = inst_summary[['Institución 1.1', 'Cantidad_Medicos', 'Porcentaje', 'Frecuencia_Promedio']].copy()
        inst_summary_display.columns = ['Institución', 'Cantidad de Médicos', '% del Total', 'Frecuencia Promedio']
        inst_summary_display['% del Total'] = inst_summary_display['% del Total'].round(1).astype(str) + '%'
        inst_summary_display['Frecuencia Promedio'] = inst_summary_display['Frecuencia Promedio'].round(2)
        st.dataframe(inst_summary_display, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ Por favor selecciona al menos una institución en el filtro superior para visualizar la comparativa.")
