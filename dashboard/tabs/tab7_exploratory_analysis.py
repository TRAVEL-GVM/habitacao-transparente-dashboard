# tab7_exploratory_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy import stats

def show_exploratory_analysis_tab(df):
    st.header("Análise Exploratória de Dados")

    # Explain what is the purpose of this tab

    st.markdown(
        """
        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 10px;">
            Este separador permite-lhe explorar o conjunto de dados e gerar gráficos baseados nos dados. 
            Pode filtrar os dados com base em diferentes colunas e gerar gráficos automaticamente. 
            Os gráficos são gerados com base nos dados e podem fornecer insights sobre a distribuição e relações entre diferentes variáveis.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Filtragem de Dados")

    # Create three columns for the controls
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # Housing situation filter
        if "housing_situation" in df.columns:
            # Criar mapeamento de valores em inglês para português
            housing_mapping = {
                "Owned": "Casa Própria",
                "Renting": "Arrendamento",
                "Living with others": "A viver com outros",
                "All": "Todos"
            }
            
            # Obter valores únicos e aplicar mapeamento
            housing_values = sorted(df["housing_situation"].dropna().unique().tolist())
            housing_options = ["Todos"] + [housing_mapping.get(val, val) for val in housing_values]
            
            # Criar opção reversa de mapeamento para usar na filtragem
            reverse_housing_mapping = {v: k for k, v in housing_mapping.items() if k != "All"}
            
            selected_housing_pt = st.selectbox("Situação Habitacional", housing_options)
            
            # Converter seleção em português para o valor em inglês para filtragem
            selected_housing = reverse_housing_mapping.get(selected_housing_pt, selected_housing_pt) if selected_housing_pt != "Todos" else "Todos"

        # Region filter
        if "distrito" in df.columns:
            district_options = ["Todos"] + sorted(
                df["distrito"].dropna().unique().tolist()
            )
            selected_district = st.selectbox("Distrito", district_options)

    with col2:
        # Income filter
        if "rendimento_clean" in df.columns:
            # Criar mapeamento para escalões de rendimento
            income_mapping = {
                "sem-rendimento": "Sem rendimento",
                "<7001": "Até €7.000",
                "7001-12000": "€7.001-€12.000",
                "12001-20000": "€12.001-€20.000",
                "20001-35000": "€20.001-€35.000",
                "35001-50000": "€35.001-€50.000",
                "50001-80000": "€50.001-€80.000",
                ">80001": "Mais de €80.000",
                "All": "Todos"
            }
            
            # Obter valores únicos e aplicar mapeamento
            income_values = sorted(df["rendimento_clean"].dropna().unique().tolist())
            income_options = ["Todos"] + [income_mapping.get(val, val) for val in income_values]
            
            # Criar opção reversa de mapeamento
            reverse_income_mapping = {v: k for k, v in income_mapping.items() if k != "All"}
            
            selected_income_pt = st.selectbox("Escalão de Rendimento", income_options)
            
            # Converter seleção para o valor em inglês
            selected_income = reverse_income_mapping.get(selected_income_pt, selected_income_pt) if selected_income_pt != "Todos" else "Todos"

        # Satisfaction filter
        if "satisfaction_level" in df.columns:
            # Criar mapeamento para níveis de satisfação
            satisfaction_mapping = {
                "Very Satisfied": "Muito Satisfeito",
                "Satisfied": "Satisfeito",
                "Neutral": "Neutro",
                "Dissatisfied": "Insatisfeito",
                "Very Dissatisfied": "Muito Insatisfeito",
                "All": "Todos"
            }
            
            # Obter valores únicos e aplicar mapeamento
            satisfaction_values = sorted(df["satisfaction_level"].dropna().unique().tolist())
            satisfaction_options = ["Todos"] + [satisfaction_mapping.get(val, val) for val in satisfaction_values]
            
            # Criar opção reversa de mapeamento
            reverse_satisfaction_mapping = {v: k for k, v in satisfaction_mapping.items() if k != "All"}
            
            selected_satisfaction_pt = st.selectbox("Nível de Satisfação", satisfaction_options)
            
            # Converter seleção para o valor em inglês
            selected_satisfaction = reverse_satisfaction_mapping.get(selected_satisfaction_pt, selected_satisfaction_pt) if selected_satisfaction_pt != "Todos" else "Todos"

    with col3:
        # House type filter
        if "house_type" in df.columns:
            # Criar mapeamento para tipo de habitação
            house_type_mapping = {
                "Apartment": "Apartamento",
                "House": "Moradia",
                "All": "Todos"
            }
            
            # Obter valores únicos e aplicar mapeamento
            house_type_values = sorted(df["house_type"].dropna().unique().tolist())
            house_type_options = ["Todos"] + [house_type_mapping.get(val, val) for val in house_type_values]
            
            # Criar opção reversa de mapeamento
            reverse_house_type_mapping = {v: k for k, v in house_type_mapping.items() if k != "All"}
            
            selected_house_type_pt = st.selectbox("Tipo de Habitação", house_type_options)
            
            # Converter seleção para o valor em inglês
            selected_house_type = reverse_house_type_mapping.get(selected_house_type_pt, selected_house_type_pt) if selected_house_type_pt != "Todos" else "Todos"

        # Education level filter
        if "education_level" in df.columns:
            # Criar mapeamento para níveis de educação
            education_mapping = {
                "Basic": "Básico",
                "High School": "Secundário",
                "Vocational": "Profissional",
                "Bachelor's": "Licenciatura",
                "Master's": "Mestrado",
                "PhD": "Doutoramento",
                "All": "Todos"
            }
            
            # Obter valores únicos e aplicar mapeamento
            education_values = sorted(df["education_level"].dropna().unique().tolist())
            education_options = ["Todos"] + [education_mapping.get(val, val) for val in education_values]
            
            # Criar opção reversa de mapeamento
            reverse_education_mapping = {v: k for k, v in education_mapping.items() if k != "All"}
            
            selected_education_pt = st.selectbox("Nível de Educação", education_options)
            
            # Converter seleção para o valor em inglês
            selected_education = reverse_education_mapping.get(selected_education_pt, selected_education_pt) if selected_education_pt != "Todos" else "Todos"

    # Apply filters to the dataframe
    filtered_df = df.copy()

    if "housing_situation" in df.columns and selected_housing != "Todos":
        filtered_df = filtered_df[filtered_df["housing_situation"] == selected_housing]

    if "distrito" in df.columns and selected_district != "Todos":
        filtered_df = filtered_df[filtered_df["distrito"] == selected_district]

    if "rendimento_clean" in df.columns and selected_income != "Todos":
        filtered_df = filtered_df[filtered_df["rendimento_clean"] == selected_income]

    if "satisfaction_level" in df.columns and selected_satisfaction != "Todos":
        filtered_df = filtered_df[
            filtered_df["satisfaction_level"] == selected_satisfaction
        ]

    if "house_type" in df.columns and selected_house_type != "Todos":
        filtered_df = filtered_df[filtered_df["house_type"] == selected_house_type]

    if "education_level" in df.columns and selected_education != "Todos":
        filtered_df = filtered_df[filtered_df["education_level"] == selected_education]

    # Show filtered data count
    st.write(f"A mostrar {len(filtered_df)} de {len(df)} registos")

    # Show dataframe with filtered data
    with st.expander("Ver Dados", expanded=False):
        st.dataframe(filtered_df, use_container_width=True)

    # Auto chart generation section
    st.subheader("Geração Automática de Gráficos")

    # Create two columns for chart controls
    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        # Select chart type
        chart_type = st.selectbox(
            "Tipo de Gráfico",
            ["Gráfico de Barras", "Histograma", "Gráfico de Dispersão", "Gráfico de Caixa", "Gráfico Circular"],
        )

        # Get numeric and categorical columns for axis selection
        numeric_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = filtered_df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        # Remove complex list columns
        categorical_cols = [
            col
            for col in categorical_cols
            if not any(filtered_df[col].astype(str).str.contains("\[", na=False))
        ]

        # Add cleaned columns that might be useful
        for col in [
            "housing_situation",
            "satisfaction_level",
            "house_type",
            "education_level",
            "employment_status",
            "rendimento_clean",
            "bedroom_count",
        ]:
            if col in filtered_df.columns and col not in categorical_cols:
                categorical_cols.append(col)

    with chart_col2:
        # Dynamic options based on chart type
        if chart_type == "Gráfico de Barras":
            x_axis = st.selectbox("Eixo X (Categoria)", categorical_cols)
            agg_option = st.selectbox("Agregação", ["Contagem", "Média", "Soma", "Mediana"])

            if agg_option != "Contagem":
                y_axis = st.selectbox("Eixo Y (Numérico)", numeric_cols)
            else:
                y_axis = None

        elif chart_type == "Histograma":
            x_axis = st.selectbox("Eixo X (Numérico)", numeric_cols)
            bins = st.slider("Número de Intervalos", min_value=5, max_value=50, value=20)
            y_axis = None

        elif chart_type == "Gráfico de Dispersão":
            x_axis = st.selectbox("Eixo X (Numérico)", numeric_cols)
            y_axis = st.selectbox("Eixo Y (Numérico)", numeric_cols)
            color_option = st.selectbox("Cor Por", ["Nenhum"] + categorical_cols)
            if color_option == "Nenhum":
                color_option = None

        elif chart_type == "Gráfico de Caixa":
            x_axis = st.selectbox("Eixo X (Categoria)", categorical_cols)
            y_axis = st.selectbox("Eixo Y (Numérico)", numeric_cols)

        else:  # Pie Chart
            x_axis = st.selectbox("Categoria", categorical_cols)
            y_axis = None

    # Generate the chart
    if len(filtered_df) > 0:
        st.subheader("Gráfico Gerado")

        if chart_type == "Gráfico de Barras":
            if agg_option == "Contagem":
                # Fix for the bar chart - Create proper dataframe for value counts
                value_counts = filtered_df[x_axis].value_counts().reset_index()
                value_counts.columns = [x_axis, "count"]  # Properly rename columns

                fig = px.bar(
                    value_counts,
                    x=x_axis,  # Use the actual column name, not 'index'
                    y="count",
                    title=f"Contagem de {x_axis}",
                    labels={x_axis: x_axis, "count": "Contagem"},
                )
            else:
                agg_func = {"média": np.mean, "soma": np.sum, "mediana": np.median}[
                    agg_option.lower()
                ]
                agg_data = (
                    filtered_df.groupby(x_axis)[y_axis].agg(agg_func).reset_index()
                )
                fig = px.bar(
                    agg_data,
                    x=x_axis,
                    y=y_axis,
                    title=f"{agg_option} de {y_axis} por {x_axis}",
                )

        elif chart_type == "Histograma":
            fig = px.histogram(
                filtered_df, x=x_axis, nbins=bins, title=f"Distribuição de {x_axis}"
            )

        elif chart_type == "Gráfico de Dispersão":
            fig = px.scatter(
                filtered_df,
                x=x_axis,
                y=y_axis,
                color=color_option,
                title=f"{y_axis} vs {x_axis}",
            )

        elif chart_type == "Gráfico de Caixa":
            fig = px.box(
                filtered_df,
                x=x_axis,
                y=y_axis,
                title=f"Distribuição de {y_axis} por {x_axis}",
            )

        else:  # Pie Chart
            value_counts = filtered_df[x_axis].value_counts()
            fig = px.pie(
                names=value_counts.index,
                values=value_counts.values,
                title=f"Distribuição de {x_axis}",
            )

        # Show the generated chart
        st.plotly_chart(fig, use_container_width=True)

        # Add chart description
        with st.expander("Insights do Gráfico", expanded=False):
            if chart_type == "Gráfico de Barras":
                if agg_option == "Contagem":
                    most_common = filtered_df[x_axis].value_counts().idxmax()
                    pct = (
                        filtered_df[x_axis].value_counts().max() / len(filtered_df)
                    ) * 100
                    st.write(
                        f"- {x_axis} mais comum: {most_common} ({pct:.1f}% dos dados)"
                    )
                    st.write(
                        f"- Número de valores únicos de {x_axis}: {filtered_df[x_axis].nunique()}"
                    )
                else:
                    agg_data = filtered_df.groupby(x_axis)[y_axis].agg(agg_func)
                    max_category = agg_data.idxmax()
                    min_category = agg_data.idxmin()
                    st.write(
                        f"- {y_axis} mais alto ({agg_option}): {max_category} com {agg_data.max():.2f}"
                    )
                    st.write(
                        f"- {y_axis} mais baixo ({agg_option}): {min_category} com {agg_data.min():.2f}"
                    )

            elif chart_type == "Histograma":
                st.write(f"- Valor médio: {filtered_df[x_axis].mean():.2f}")
                st.write(f"- Valor mediano: {filtered_df[x_axis].median():.2f}")
                st.write(
                    f"- Intervalo: {filtered_df[x_axis].min():.2f} a {filtered_df[x_axis].max():.2f}"
                )

            elif chart_type == "Gráfico de Dispersão":
                corr = filtered_df[[x_axis, y_axis]].corr().iloc[0, 1]
                st.write(f"- Correlação entre {x_axis} e {y_axis}: {corr:.2f}")
                if abs(corr) > 0.7:
                    st.write("- Correlação forte detetada")
                elif abs(corr) > 0.3:
                    st.write("- Correlação moderada detetada")
                else:
                    st.write("- Correlação fraca detetada")

            elif chart_type == "Gráfico de Caixa":
                grouped = filtered_df.groupby(x_axis)[y_axis]
                st.write(
                    f"- Categoria com {y_axis} mediano mais alto: {grouped.median().idxmax()}"
                )
                st.write(
                    f"- Categoria com {y_axis} mediano mais baixo: {grouped.median().idxmin()}"
                )
                st.write(f"- Categoria com maior variabilidade: {grouped.std().idxmax()}")

            else:  # Pie Chart
                most_common = filtered_df[x_axis].value_counts().idxmax()
                pct = (
                    filtered_df[x_axis].value_counts().max() / len(filtered_df)
                ) * 100
                st.write(f"- {x_axis} mais comum: {most_common} ({pct:.1f}% dos dados)")
                st.write(f"- Número de categorias: {filtered_df[x_axis].nunique()}")
    else:
        st.warning(
            "Não há dados disponíveis com os filtros atuais. Por favor, ajuste os seus filtros."
        )

    # Statistical summary section
    st.subheader("Resumo Estatístico")

    # Select columns for summary
    summary_cols = st.multiselect(
        "Selecione colunas para estatísticas resumidas",
        numeric_cols,
        default=numeric_cols[:3] if len(numeric_cols) > 3 else numeric_cols,
    )

    if summary_cols:
        st.dataframe(filtered_df[summary_cols].describe(), use_container_width=True)

    # Correlation matrix
    if len(numeric_cols) > 1:
        with st.expander("Matriz de Correlação", expanded=False):
            corr_cols = st.multiselect(
                "Selecione colunas para análise de correlação",
                numeric_cols,
                default=numeric_cols[:5] if len(numeric_cols) > 5 else numeric_cols,
            )

            if corr_cols and len(corr_cols) > 1:
                corr_matrix = filtered_df[corr_cols].corr()

                # Create a heatmap for the correlation matrix
                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    color_continuous_scale="RdBu_r",
                    title="Matriz de Correlação",
                )
                st.plotly_chart(fig, use_container_width=True)

                # Find the strongest correlations
                corr_pairs = []
                for i in range(len(corr_cols)):
                    for j in range(i + 1, len(corr_cols)):
                        corr_value = corr_matrix.iloc[i, j]
                        corr_pairs.append((corr_cols[i], corr_cols[j], corr_value))

                # Sort by absolute correlation value and show the top 5
                corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)

                st.write("Correlações mais fortes:")
                for col1, col2, corr in corr_pairs[:5]:
                    st.write(f"- {col1} e {col2}: {corr:.2f}")

    # Trend Analysis Section
    st.subheader("Análise de Tendências")

    # Identify potential time-based columns
    time_columns = []
    for col in df.columns:
        if any(time_term in col.lower() for time_term in ['ano', 'year', 'date', 'time', 'period']):
            if col in filtered_df.columns:
                time_columns.append(col)

    # Check if we have any time-based columns
    if not time_columns:
        st.info("Não foram detetadas colunas temporais para análise de tendências. Colunas temporais comuns incluem aquelas com 'ano', 'year', 'date', ou 'time' nos seus nomes.")
    else:
        # Time column selection
        time_col = st.selectbox("Selecione Coluna Temporal", time_columns, index=time_columns.index("ano-compra") if "ano-compra" in time_columns else 0)
        
        # Variable selection
        trend_var_options = numeric_cols + categorical_cols
        trend_var = st.selectbox("Selecione Variável para Analisar", trend_var_options, index=trend_var_options.index("valor-compra") if "valor-compra" in trend_var_options else 0)
        
        # Analysis type selection
        analysis_type = st.radio(
            "Tipo de Análise",
            ["Série Temporal", "Comparação Ano a Ano", "Distribuição ao Longo do Tempo"]
        )
        
        # Prepare data for analysis
        if time_col in filtered_df.columns and trend_var in filtered_df.columns:
            # Check if the time column is numeric (like years)
            if pd.api.types.is_numeric_dtype(filtered_df[time_col]):
                # For numeric time columns, like years
                has_valid_data = not filtered_df[time_col].isna().all() and not filtered_df[trend_var].isna().all()
                
                if has_valid_data:
                    # Sort data by time column
                    trend_data = filtered_df.sort_values(by=time_col)
                    
                    if analysis_type == "Série Temporal":
                        if pd.api.types.is_numeric_dtype(filtered_df[trend_var]):
                            # For numeric variables, calculate average per time period
                            agg_data = trend_data.groupby(time_col)[trend_var].agg(['mean', 'median', 'count']).reset_index()
                            
                            # Create time series plot
                            fig = px.line(
                                agg_data,
                                x=time_col,
                                y='mean',
                                title=f"Média de {trend_var} ao Longo do Tempo",
                                labels={time_col: time_col, 'mean': f'Média de {trend_var}'}
                            )
                            # Add confidence interval
                            fig.add_scatter(
                                x=agg_data[time_col],
                                y=agg_data['median'],
                                mode='lines',
                                line=dict(dash='dash', color='red'),
                                name='Mediana'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show data points count
                            st.write(f"Total de pontos de dados: {len(trend_data)}")
                            
                            # Show key statistics
                            earliest = trend_data[time_col].min()
                            latest = trend_data[time_col].max()
                            earliest_avg = trend_data[trend_data[time_col] == earliest][trend_var].mean()
                            latest_avg = trend_data[trend_data[time_col] == latest][trend_var].mean()
                            
                            # Calculate overall change
                            change = latest_avg - earliest_avg
                            percent_change = (change / earliest_avg) * 100 if earliest_avg != 0 else 0
                            
                            st.write(f"De {earliest} até {latest}, {trend_var} mudou em {change:.2f} ({percent_change:.1f}%)")
                            
                            # Trend analysis
                            if len(agg_data) > 1:
                                # Simple linear regression to determine trend
                                
                                x = agg_data[time_col].values
                                y = agg_data['mean'].values
                                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                                
                                trend_direction = "ascendente" if slope > 0 else "descendente"
                                trend_strength = "forte" if abs(r_value) > 0.7 else "moderada" if abs(r_value) > 0.3 else "fraca"
                                
                                st.write(f"Os dados mostram uma tendência {trend_strength} {trend_direction} (r² = {r_value**2:.2f})")
                        else:
                            # For categorical variables, show distribution over time
                            st.info(f"A variável selecionada '{trend_var}' é categórica. A mostrar distribuição ao longo do tempo.")
                            
                            # Create a crosstab of time vs. category
                            crosstab = pd.crosstab(trend_data[time_col], trend_data[trend_var], normalize='index')
                            crosstab_long = crosstab.reset_index().melt(id_vars=[time_col])
                            
                            fig = px.area(
                                crosstab_long,
                                x=time_col,
                                y='value',
                                color='variable',
                                title=f"Distribuição de {trend_var} ao Longo do Tempo",
                                labels={'value': 'Percentagem', 'variable': trend_var}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    elif analysis_type == "Comparação Ano a Ano":
                        if pd.api.types.is_numeric_dtype(filtered_df[trend_var]):
                            # Get unique years/time periods
                            time_periods = sorted(filtered_df[time_col].unique())
                            
                            if len(time_periods) > 1:
                                # Calculate year-over-year change
                                yoy_data = []
                                for i in range(1, len(time_periods)):
                                    current_period = time_periods[i]
                                    previous_period = time_periods[i-1]
                                    
                                    current_avg = filtered_df[filtered_df[time_col] == current_period][trend_var].mean()
                                    previous_avg = filtered_df[filtered_df[time_col] == previous_period][trend_var].mean()
                                    
                                    change = current_avg - previous_avg
                                    pct_change = (change / previous_avg) * 100 if previous_avg != 0 else 0
                                    
                                    yoy_data.append({
                                        'Period': f"{previous_period} para {current_period}",
                                        'Change': change,
                                        'Percent_Change': pct_change
                                    })
                                
                                # Create dataframe for visualization
                                yoy_df = pd.DataFrame(yoy_data)
                                
                                # Create bar chart of changes
                                fig = px.bar(
                                    yoy_df,
                                    x='Period',
                                    y='Percent_Change',
                                    title=f"Mudança Ano a Ano em {trend_var}",
                                    labels={'Percent_Change': 'Mudança Percentual (%)'}
                                )
                                
                                # Add color based on positive/negative change
                                fig.update_traces(marker_color=yoy_df['Percent_Change'].apply(
                                    lambda x: 'green' if x > 0 else 'red'
                                ))
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Show statistics
                                avg_change = yoy_df['Percent_Change'].mean()
                                max_change = yoy_df.loc[yoy_df['Percent_Change'].idxmax()]
                                min_change = yoy_df.loc[yoy_df['Percent_Change'].idxmin()]
                                
                                st.write(f"Mudança média ano a ano: {avg_change:.1f}%")
                                st.write(f"Maior aumento: {max_change['Period']} ({max_change['Percent_Change']:.1f}%)")
                                st.write(f"Maior diminuição: {min_change['Period']} ({min_change['Percent_Change']:.1f}%)")
                            else:
                                st.warning(f"São necessários pelo menos dois períodos temporais para comparação ano a ano. Atualmente só há dados para {time_periods[0]}.")
                        else:
                            st.info(f"A comparação ano a ano requer dados numéricos. '{trend_var}' é categórica.")
                    
                    elif analysis_type == "Distribuição ao Longo do Tempo":
                        # Create a box plot showing distribution of the variable over time
                        fig = px.box(
                            trend_data,
                            x=time_col,
                            y=trend_var if pd.api.types.is_numeric_dtype(filtered_df[trend_var]) else None,
                            color=time_col,
                            title=f"Distribuição de {trend_var} ao Longo do Tempo",
                            notched=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Distribution statistics
                        with st.expander("Estatísticas de Distribuição", expanded=False):
                            dist_stats = trend_data.groupby(time_col)[trend_var].describe() if pd.api.types.is_numeric_dtype(filtered_df[trend_var]) else None
                            
                            if dist_stats is not None:
                                st.dataframe(dist_stats, use_container_width=True)
                                
                                # Variance over time
                                variance_over_time = trend_data.groupby(time_col)[trend_var].var().reset_index()
                                
                                fig_var = px.line(
                                    variance_over_time,
                                    x=time_col,
                                    y=trend_var,
                                    title=f"Variância em {trend_var} ao Longo do Tempo",
                                    markers=True
                                )
                                st.plotly_chart(fig_var, use_container_width=True)
                                
                                # Check if variance is increasing or decreasing
                                if len(variance_over_time) > 1:
                                    first_var = variance_over_time[trend_var].iloc[0]
                                    last_var = variance_over_time[trend_var].iloc[-1]
                                    
                                    if last_var > first_var:
                                        st.write(f"A variabilidade em {trend_var} aumentou ao longo do tempo.")
                                    else:
                                        st.write(f"A variabilidade em {trend_var} diminuiu ao longo do tempo.")
                            else:
                                # For categorical variables, show frequency distribution
                                freq_dist = pd.crosstab(trend_data[time_col], trend_data[trend_var])
                                st.dataframe(freq_dist, use_container_width=True)
                else:
                    st.warning("As colunas selecionadas não contêm dados válidos para análise de tendências.")
            else:
                st.info(f"A coluna temporal selecionada '{time_col}' não é numérica. Por favor, converta-a para formato numérico para análise de tendências.")
        else:
            st.warning("Por favor, selecione colunas válidas para análise de tendências.")