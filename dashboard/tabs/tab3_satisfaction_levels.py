# tab3_satisfaction_levels.py
import json
import sys
from pathlib import Path

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import folium_static

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))
from config import BACKGROUND_COLORS, COLOR_SCALES, SATISFACTION_COLORS, TEXT_COLORS

# Create a numeric satisfaction score with Portuguese labels mapping to English values in the data
satisfaction_scores = {
    "Very Satisfied": 5,  # muito-satisfeito
    "Satisfied": 4,      # satisfeito
    "Neutral": 3,        # indiferente
    "Dissatisfied": 2,   # insatisfeito
    "Very Dissatisfied": 1, # muito-insatisfeito
}

# Mapping between English data values and Portuguese display labels
satisfaction_pt_labels = {
    "Very Satisfied": "Muito Satisfeito",
    "Satisfied": "Satisfeito",
    "Neutral": "Neutro",
    "Dissatisfied": "Insatisfeito",
    "Very Dissatisfied": "Muito Insatisfeito"
}

# Update SATISFACTION_COLORS with Portuguese labels if needed
SATISFACTION_COLORS_PT = {
    "Muito Satisfeito": SATISFACTION_COLORS["Very Satisfied"],
    "Satisfeito": SATISFACTION_COLORS["Satisfied"],
    "Neutro": SATISFACTION_COLORS["Neutral"],
    "Insatisfeito": SATISFACTION_COLORS["Dissatisfied"],
    "Muito Insatisfeito": SATISFACTION_COLORS["Very Dissatisfied"]
}


def show_satisfaction_levels_tab(df):
    """
    Display the Satisfaction Levels tab with visualizations, filters, and explanatory text.

    Parameters:
    df (DataFrame): The processed housing data
    """
    st.header("Análise de Níveis de Satisfação Habitacional")

    # Introdução com estilo melhorado
    st.markdown(
        """
    <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
    <h4 style="color: #2e7d32; margin-top: 0;">Visão Geral</h4>
    <p>Esta secção fornece uma análise aprofundada dos níveis de satisfação habitacional em Portugal, 
    explorando como diferentes fatores socioeconómicos influenciam a perceção da qualidade habitacional.</p>
    <ul>
        <li><strong>Tendências Principais:</strong> Existe uma variação significativa na satisfação habitacional entre diferentes grupos demográficos</li>
        <li><strong>Fatores de Influência:</strong> Rendimento, localização, tipo de habitação e situação profissional impactam diretamente a satisfação</li>
        <li><strong>Desafios Identificados:</strong> Altos custos habitacionais e inadequação do espaço são grandes contribuintes para a insatisfação</li>
    </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Métricas principais
    # Calcular algumas estatísticas para as métricas rápidas
    total_responses = len(df)

    # Calcular percentagem de níveis de satisfação
    satisfaction_counts = df["satisfaction_level"].value_counts(normalize=True) * 100

    satisfied_pct = satisfaction_counts.get(
        "Very Satisfied", 0
    ) + satisfaction_counts.get("Satisfied", 0)
    dissatisfied_pct = satisfaction_counts.get(
        "Very Dissatisfied", 0
    ) + satisfaction_counts.get("Dissatisfied", 0)

    # Criar 3 colunas para métricas rápidas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total de Respostas",
            value=total_responses,
            help="Número total de respostas no inquérito",
        )

    with col2:
        st.metric(
            label="Taxa de Satisfação",
            value=f"{satisfied_pct:.1f}%",
            help="Percentagem de respostas 'Satisfeito' ou 'Muito Satisfeito'",
        )

    with col3:
        st.metric(
            label="Taxa de Insatisfação",
            value=f"{dissatisfied_pct:.1f}%",
            help="Percentagem de respostas 'Insatisfeito' ou 'Muito Insatisfeito'",
        )
    # Define better income bracket ordering and visualization
    income_order = [
        "sem-rendimento",
        "<7001",
        "7001-12000",
        "12001-20000",
        "20001-35000",
        "35001-50000",
        "50001-80000",
        ">80001",
    ]

    # More human-readable income labels for display
    income_labels = {
        "sem-rendimento": "Sem Rendimento",
        "<7001": "Até €7.000",
        "7001-12000": "€7.001-€12.000",
        "12001-20000": "€12.001-€20.000",
        "20001-35000": "€20.001-€35.000",
        "35001-50000": "€35.001-€50.000",
        "50001-80000": "€50.001-€80.000",
        ">80001": "Mais de €80.000",
    }

    # Create a categorical variable for income with proper ordering
    df["income_category"] = pd.Categorical(
        df["rendimento-anual"].fillna("Unknown"),
        categories=income_order + ["Unknown"],
        ordered=True,
    )

    # Interactive filter by satisfaction level
    st.subheader("Explorar Demografia por Nível de Satisfação")
    st.markdown("""
    Esta secção permite explorar como os níveis de satisfação variam entre diferentes grupos de rendimento.
    Utilize os filtros abaixo para focar em níveis específicos de satisfação e escalões de rendimento para descobrir padrões.
    """)

    # Two-column layout for filters
    col1, col2 = st.columns(2)

    with col1:
        # Create a list of satisfaction levels with translated display but keep original values for filtering
        satisfaction_options = [(level, satisfaction_pt_labels[level]) 
                               for level in df["satisfaction_level"].dropna().unique()]
        
        selected_satisfaction_display = st.multiselect(
            "Selecione Níveis de Satisfação",
            options=[option[1] for option in satisfaction_options],
            default=[option[1] for option in satisfaction_options],
        )
        
        # Convert back to original values for filtering
        selected_satisfaction = [level[0] for level in satisfaction_options 
                                if level[1] in selected_satisfaction_display]

    with col2:
        selected_income = st.multiselect(
            "Selecione Escalões de Rendimento",
            options=[
                income_labels[inc]
                for inc in income_order
                if inc in df["rendimento-anual"].unique()
            ],
            default=[
                income_labels[inc]
                for inc in income_order
                if inc in df["rendimento-anual"].unique()
            ],
            format_func=lambda x: x,
        )

        # Convert back to original format for filtering
        selected_income_original = [
            key for key, value in income_labels.items() if value in selected_income
        ]

    # Apply filters
    if selected_satisfaction and selected_income_original:
        filtered_df = df[
            (df["satisfaction_level"].isin(selected_satisfaction))
            & (df["rendimento-anual"].isin(selected_income_original))
        ]
    elif selected_satisfaction:
        filtered_df = df[df["satisfaction_level"].isin(selected_satisfaction)]
    elif selected_income_original:
        filtered_df = df[df["rendimento-anual"].isin(selected_income_original)]
    else:
        filtered_df = df

    # Income vs. Satisfaction Analysis
    st.subheader("Análise de Rendimento vs. Satisfação")

    # Create tabs for different visualizations
    income_tab1, income_tab2, income_tab3 = st.tabs(
        ["Distribuição", "Satisfação Média", "Análise Detalhada"]
    )

    with income_tab1:
        # Group by ordered income category for better visualization
        income_satisfaction = (
            filtered_df.groupby("income_category")["satisfaction_level"]
            .value_counts(normalize=True)
            .mul(100)
            .round(1)
            .unstack()
            .fillna(0)
        )

        # Replace category names with more readable versions for the chart
        income_satisfaction.index = income_satisfaction.index.map(
            lambda x: income_labels.get(x, x)
        )
        
        # Replace English column names with Portuguese labels
        income_satisfaction.columns = [satisfaction_pt_labels.get(col, col) for col in income_satisfaction.columns]

        fig1 = px.bar(
            income_satisfaction,
            barmode="stack",
            title="Distribuição de Satisfação por Escalão de Rendimento (%)",
            labels={"income_category": "Rendimento Anual", "value": "Percentagem"},
            color_discrete_map=SATISFACTION_COLORS_PT,
        )
        fig1.update_layout(
            legend_title="Nível de Satisfação",
            height=500,
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0],
        )
        st.plotly_chart(fig1, use_container_width=True)

    with income_tab2:
        # Calculate average satisfaction score by income bracket (using categorical ordering)
        filtered_df["satisfaction_score"] = filtered_df["satisfaction_level"].map(
            satisfaction_scores
        )

        # Group by income category to maintain proper order
        avg_satisfaction = (
            filtered_df.groupby("income_category")["satisfaction_score"]
            .mean()
            .reset_index()
        )
        avg_satisfaction.columns = ["Escalão de Rendimento", "Pontuação Média de Satisfação"]

        # Replace with readable labels
        avg_satisfaction["Escalão de Rendimento"] = avg_satisfaction["Escalão de Rendimento"].map(
            lambda x: income_labels.get(x, x)
        )

        fig2 = px.bar(
            avg_satisfaction,
            x="Escalão de Rendimento",
            y="Pontuação Média de Satisfação",
            title="Pontuação Média de Satisfação por Escalão de Rendimento",
            color="Pontuação Média de Satisfação",
            color_continuous_scale=COLOR_SCALES["sequential"],
            text_auto=".2f",
        )
        fig2.update_layout(
            height=500,
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0],
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Calculate correlation
        corr = filtered_df["rendimento_numerical"].corr(
            filtered_df["satisfaction_score"]
        )

        st.metric(
            label="Correlação Rendimento-Satisfação",
            value=f"{corr:.2f}",
            delta=f"Correlação {'positiva' if corr > 0 else 'negativa'}",
            delta_color="normal",
        )

    with income_tab3:
        # Two columns for detailed analysis
        col1, col2 = st.columns([3, 2])

        with col1:
            # Create income groups for visualization
            filtered_df["income_group"] = pd.cut(
                filtered_df["rendimento_numerical"],
                bins=[0, 7000, 12000, 20000, 35000, 50000, 80000, float("inf")],
                labels=[
                    "Sem/Baixo Rendimento",
                    "€7K-€12K",
                    "€12K-€20K",
                    "€20K-€35K",
                    "€35K-€50K",
                    "€50K-€80K",
                    "Mais de €80K",
                ],
            )

            # Handle NaN values in 'area_numerical' column
            filtered_df["area_numerical"] = filtered_df["area_numerical"].fillna(0)

            # Create a mapping for housing situation labels
            housing_situation_pt = {
                "Renting": "Arrendamento",
                "Owned": "Propriedade",
                "Living with others": "A viver com outros"
            }
            
            # Create a new copy with Portuguese housing situation labels for visualization
            viz_df = filtered_df.copy()
            viz_df["housing_situation_pt"] = viz_df["housing_situation"].map(housing_situation_pt)

            # Scatter plot with better grouping, labels and theme
            fig3 = px.scatter(
                viz_df,
                x="rendimento_numerical",
                y="satisfaction_score",
                color="housing_situation_pt",
                size="area_numerical",
                hover_data=["distrito", "concelho", "income_group"],
                opacity=0.7,
                title="Rendimento vs. Satisfação (Tamanho = Área Habitacional)",
                labels={
                    "rendimento_numerical": "Rendimento Anual (€)",
                    "satisfaction_score": "Pontuação de Satisfação (1-5)",
                    "housing_situation_pt": "Situação Habitacional"
                },
                color_discrete_sequence=COLOR_SCALES["qualitative"]
            )

            # Add income group reference lines
            for income_level in [7000, 12000, 20000, 35000, 50000, 80000]:
                fig3.add_vline(
                    x=income_level,
                    line_dash="dash",
                    line_color=TEXT_COLORS[1],
                    opacity=0.5
                )

            fig3.update_layout(
                height=450,
                plot_bgcolor=BACKGROUND_COLORS[0],
                paper_bgcolor=BACKGROUND_COLORS[3],
                font_color=TEXT_COLORS[2],
                title_font_color=TEXT_COLORS[0]
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col2:
            # Key insights based on the data with improved income grouping
            st.subheader("Insights Principais")

            # Define income groups for analysis
            income_groups = {
                "Baixo Rendimento": filtered_df[filtered_df["rendimento_numerical"] < 12000],
                "Rendimento Médio": filtered_df[
                    (filtered_df["rendimento_numerical"] >= 12000)
                    & (filtered_df["rendimento_numerical"] < 35000)
                ],
                "Rendimento Alto": filtered_df[
                    (filtered_df["rendimento_numerical"] >= 35000)
                    & (filtered_df["rendimento_numerical"] < 80000)
                ],
                "Rendimento Muito Alto": filtered_df[
                    filtered_df["rendimento_numerical"] >= 80000
                ],
            }

            # Calculate satisfaction by income group
            income_group_satisfaction = {
                group: data["satisfaction_score"].mean()
                for group, data in income_groups.items()
                if not data.empty
            }

            # Calculate by ownership within income groups
            ownership_by_income = {}
            for group, data in income_groups.items():
                if not data.empty:
                    owned = data[data["housing_situation"] == "Owned"][
                        "satisfaction_score"
                    ].mean()
                    rented = data[data["housing_situation"] == "Renting"][
                        "satisfaction_score"
                    ].mean()
                    ownership_by_income[group] = (owned, rented)

            # Display metrics
            st.markdown("**Satisfação por Grupo de Rendimento:**")
            for group, score in income_group_satisfaction.items():
                st.metric(label=group, value=f"{score:.2f}/5")

            st.markdown("**Interação Rendimento-Propriedade:**")
            for group, (owned, rented) in ownership_by_income.items():
                if not (pd.isna(owned) or pd.isna(rented)):
                    st.markdown(
                        f"**{group}**: Própria {owned:.2f} vs Arrendada {rented:.2f} (Dif: {owned - rented:.2f})"
                    )

    # Overview of satisfaction by housing situation
    st.subheader("Satisfação Habitacional por Tipo de Situação")

    col1, col2 = st.columns([3, 2])

    with col1:
        # Create a heatmap of satisfaction by housing situation
        satisfaction_pivot = pd.crosstab(
            df["housing_situation"], df["satisfaction_level"]
        )

        # Map housing situation names to Portuguese
        satisfaction_pivot.index = satisfaction_pivot.index.map(
            lambda x: housing_situation_pt.get(x, x)
        )

        # Reorder columns for better visualization
        ordered_cols = [
            "Very Satisfied",
            "Satisfied",
            "Neutral",
            "Dissatisfied",
            "Very Dissatisfied",
        ]
        ordered_cols = [
            col for col in ordered_cols if col in satisfaction_pivot.columns
        ]
        satisfaction_pivot = satisfaction_pivot[ordered_cols]
        
        # Translate column names to Portuguese
        satisfaction_pivot.columns = [satisfaction_pt_labels.get(col, col) for col in satisfaction_pivot.columns]

        fig = px.imshow(
            satisfaction_pivot,
            text_auto=True,
            color_continuous_scale=COLOR_SCALES["sequential"],
            title="Níveis de Satisfação por Situação Habitacional",
            labels={
                "x": "Nível de Satisfação",
                "y": "Situação Habitacional",
                "color": "Contagem",
            },
        )
        fig.update_layout(
            height=400,
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0],
        )
        st.plotly_chart(fig)

        # Add explanation for the heatmap
        st.markdown("""
        **Insight:** Este mapa de calor mostra a distribuição dos níveis de satisfação entre diferentes situações habitacionais. 
        O azul mais escuro indica contagens mais elevadas. Os proprietários tendem a reportar níveis de satisfação mais elevados em comparação com os arrendatários, 
        provavelmente devido a maior segurança habitacional e controlo sobre o seu espaço habitacional.
        """)

    with col2:
        # Pie chart of overall satisfaction - Create a copy with translated labels
        satisfaction_counts_df = df["satisfaction_level"].value_counts().reset_index()
        satisfaction_counts_df.columns = ["Nível de Satisfação", "Contagem"]
        
        # Map English to Portuguese satisfaction levels
        satisfaction_counts_df["Nível de Satisfação"] = satisfaction_counts_df["Nível de Satisfação"].map(
            satisfaction_pt_labels
        )

        fig = px.pie(
            satisfaction_counts_df,
            values="Contagem",
            names="Nível de Satisfação",
            color="Nível de Satisfação",
            color_discrete_map=SATISFACTION_COLORS_PT,
            title="Distribuição Geral de Satisfação",
        )
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[3],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0],
        )
        st.plotly_chart(fig)

        # Calculate and display the percentage of satisfied vs dissatisfied
        satisfied_pct = (
            satisfaction_counts[
                satisfaction_counts.index.isin(
                    ["Very Satisfied", "Satisfied"]
                )
            ].sum()
            * 100
        )
        dissatisfied_pct = (
            satisfaction_counts[
                satisfaction_counts.index.isin(
                    ["Dissatisfied", "Very Dissatisfied"]
                )
            ].sum()
            * 100
        )

        st.metric("Taxa de Satisfação Geral", f"{satisfied_pct:.1f}%")
        st.metric("Taxa de Insatisfação Geral", f"{dissatisfied_pct:.1f}%")

        st.markdown("""
        **Insight:** O gráfico circular ilustra a distribuição geral da satisfação habitacional. 
        A taxa de satisfação indica a percentagem de inquiridos que estão "Satisfeitos" ou "Muito Satisfeitos" 
        com a sua situação habitacional atual.
        """)

    # Reasons for dissatisfaction
    st.subheader("Razões Comuns para a Insatisfação")
    st.markdown("""
    Compreender porque as pessoas estão insatisfeitas com a sua habitação ajuda a identificar áreas-chave para intervenção política.
    O gráfico abaixo mostra as razões mais comuns citadas pelos inquiridos que expressaram insatisfação.
    """)

    # Extract dissatisfaction reasons
    dissatisfaction_cols = [col for col in df.columns if col.startswith("reason_")]
    reason_mapping = {
        "reason_pago-demasiado": "Pago demasiado",
        "reason_falta-espaco": "Falta de espaço",
        "reason_habitacao-mau-estado": "Habitação em mau estado",
        "reason_vivo-longe": "Vivo longe do trabalho/serviços",
        "reason_quero-independecia": "Quero independência",
        "reason_dificuldades-financeiras": "Dificuldades financeiras",
        "reason_financeiramente-dependente": "Dependência financeira",
        "reason_vivo-longe-de-transportes": "Longe de transportes",
        "reason_vivo-zona-insegura": "Zona insegura",
        "reason_partilho-casa-com-desconhecidos": "Partilho casa com desconhecidos",
    }

    # Calculate frequencies of each reason
    reason_counts = {}
    for col in dissatisfaction_cols:
        if col in reason_mapping:
            reason_counts[reason_mapping[col]] = df[col].sum()

    reason_df = pd.DataFrame(
        {"Razão": list(reason_counts.keys()), "Contagem": list(reason_counts.values())}
    ).sort_values("Contagem", ascending=False)

    # Create horizontal bar chart
    fig = px.bar(
        reason_df,
        y="Razão",
        x="Contagem",
        orientation="h",
        color="Contagem",
        color_continuous_scale=COLOR_SCALES["sequential"],
        title="Razões para Insatisfação Habitacional",
    )
    fig.update_layout(
        plot_bgcolor=BACKGROUND_COLORS[0],
        paper_bgcolor=BACKGROUND_COLORS[3],
        font_color=TEXT_COLORS[2],
        title_font_color=TEXT_COLORS[0],
    )
    st.plotly_chart(fig)

    # Add explanation for the dissatisfaction reasons
    top_reasons = reason_df.head(3)["Razão"].tolist()
    st.markdown(f"""
    **Conclusões Principais:**
    - As três principais razões para insatisfação são: {", ".join(top_reasons)}
    - Preocupações financeiras (sobrecarga de custos e dificuldades financeiras) são fatores proeminentes na insatisfação habitacional
    - Problemas de localização (distância do trabalho/serviços e transportes) afetam significativamente a satisfação
    - A qualidade da habitação e as limitações de espaço também desempenham papéis importantes na insatisfação
    
    Estas conclusões sugerem que as intervenções políticas devem focar-se na acessibilidade, eficiência de localização e qualidade habitacional.
    """)

    # Interactive filter by satisfaction level
    st.subheader("Explorar Demografia por Nível de Satisfação")
    st.markdown("""
    Esta secção permite explorar como os níveis de satisfação variam entre diferentes grupos demográficos.
    Utilize o filtro multisseleção abaixo para focar em níveis específicos de satisfação e ver como se relacionam com o rendimento e características habitacionais.
    """)

    # Create a list of satisfaction levels with translated display but keep original values for filtering
    satisfaction_options = [(level, satisfaction_pt_labels.get(level, level)) 
                            for level in df["satisfaction_level"].unique()]
    
    selected_satisfaction_display = st.multiselect(
        "Selecione Níveis de Satisfação para Explorar",
        options=[option[1] for option in satisfaction_options],
        default=[option[1] for option in satisfaction_options],
    )
    
    # Convert back to original values for filtering
    selected_satisfaction = [level[0] for level in satisfaction_options 
                             if level[1] in selected_satisfaction_display]

    if selected_satisfaction:
        filtered_df = df[df["satisfaction_level"].isin(selected_satisfaction)]
    else:
        filtered_df = df

    # Income vs. satisfaction
    st.subheader("Rendimento vs. Satisfação")



    # Satisfaction by income - only compute this once
    income_satisfaction = (
        filtered_df.groupby("rendimento_clean")["satisfaction_level"]
        .value_counts()
        .unstack()
        .fillna(0)
    )

    # Convert column names to Portuguese
    income_satisfaction.columns = [satisfaction_pt_labels.get(col, col) for col in income_satisfaction.columns]

    # Create only one chart
    fig = px.bar(
        income_satisfaction,
        barmode="stack",
        title="Níveis de Satisfação por Escalão de Rendimento",
        labels={"rendimento_clean": "Rendimento Anual (€)", "value": "Contagem"},
        color_discrete_map=SATISFACTION_COLORS_PT,
    )

    # Display the chart only once
    st.plotly_chart(fig)

    # Calculate correlation between income and satisfaction
    filtered_df["satisfaction_score"] = filtered_df["satisfaction_level"].map(
        satisfaction_scores
    )

    # Calculate correlation
    corr = filtered_df["rendimento_numerical"].corr(filtered_df["satisfaction_score"])

    st.markdown(f"""
    Relação Rendimento-Satisfação:
    - Correlação entre rendimento e satisfação: {corr:.2f}
    - Escalões de rendimento mais elevados tendem a reportar níveis de satisfação mais elevados
    - Isto sugere que os recursos financeiros desempenham um papel significativo na satisfação habitacional
    """)

    # Correlation between rent burden and satisfaction for renters
    st.subheader("Sobrecarga de Renda vs. Satisfação")
    st.markdown("""
    Esta análise examina como a proporção do rendimento gasto em renda afeta os níveis de satisfação.
    A sobrecarga de renda é um indicador crítico da acessibilidade habitacional e pode afetar significativamente a qualidade de vida.
    """)

    renters_df = filtered_df[filtered_df["housing_situation"] == "Renting"]
    if not renters_df.empty:
        rent_satisfaction = pd.crosstab(
            renters_df["rent_burden"], renters_df["satisfaction_level"]
        ).reset_index()

        # Melt the dataframe for visualization
        rent_satisfaction_melted = pd.melt(
            rent_satisfaction,
            id_vars=["rent_burden"],
            var_name="Nível de Satisfação",
            value_name="Contagem",
        )
        
        # Map English satisfaction levels to Portuguese in melted dataframe
        rent_satisfaction_melted["Nível de Satisfação"] = rent_satisfaction_melted["Nível de Satisfação"].map(
            satisfaction_pt_labels
        )

        # Create an ordered category for rent burden
        rent_burden_order = [
            "≤30% (Affordable)",
            "31-50% (Moderate)",
            "51-80% (High)",
            ">80% (Very High)",
            "Unknown",
        ]
        
        # Translate rent burden categories
        rent_burden_pt = {
            "≤30% (Affordable)": "≤30% (Acessível)",
            "31-50% (Moderate)": "31-50% (Moderada)",
            "51-80% (High)": "51-80% (Alta)",
            ">80% (Very High)": ">80% (Muito Alta)",
            "Unknown": "Desconhecida"
        }
        
        rent_satisfaction_melted["rent_burden"] = pd.Categorical(
            rent_satisfaction_melted["rent_burden"],
            categories=rent_burden_order,
            ordered=True,
        )
        
        # Apply translation to display labels while keeping original categories for ordering
        rent_satisfaction_melted["rent_burden_pt"] = rent_satisfaction_melted["rent_burden"].map(
            lambda x: rent_burden_pt.get(x, x)
        )

        rent_satisfaction_melted = rent_satisfaction_melted.sort_values("rent_burden")

        fig = px.bar(
            rent_satisfaction_melted,
            x="rent_burden_pt",  # Use Portuguese labels for display
            y="Contagem",
            color="Nível de Satisfação",
            color_discrete_map=SATISFACTION_COLORS_PT,
            title="Níveis de Satisfação por Sobrecarga de Renda (% do Rendimento)",
            labels={"rent_burden_pt": "Renda como % do Rendimento"},
        )
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0],
        )
        st.plotly_chart(fig)

        # Calculate average satisfaction by rent burden
        renters_df["satisfaction_score"] = renters_df["satisfaction_level"].map(
            satisfaction_scores
        )
        avg_satisfaction_by_burden = (
            renters_df.groupby("rent_burden")["satisfaction_score"].mean().reset_index()
        )

        # Find the rent burden with highest and lowest satisfaction
        highest_satisfaction = avg_satisfaction_by_burden.loc[
            avg_satisfaction_by_burden["satisfaction_score"].idxmax()
        ]
        lowest_satisfaction = avg_satisfaction_by_burden.loc[
            avg_satisfaction_by_burden["satisfaction_score"].idxmin()
        ]
        
        # Translate burden categories for display
        highest_satisfaction_cat = rent_burden_pt.get(highest_satisfaction["rent_burden"], 
                                                    highest_satisfaction["rent_burden"])
        lowest_satisfaction_cat = rent_burden_pt.get(lowest_satisfaction["rent_burden"], 
                                                   lowest_satisfaction["rent_burden"])

        st.markdown(f"""
        **Análise de Sobrecarga de Renda:**
        - A categoria de sobrecarga de renda mais acessível ({highest_satisfaction_cat}) mostra as maiores taxas de satisfação com uma pontuação média de {highest_satisfaction["satisfaction_score"]:.2f}
        - A satisfação diminui à medida que a sobrecarga de renda aumenta, com o declínio mais acentuado ocorrendo quando a renda excede 50% do rendimento
        - Os arrendatários que gastam mais de 80% do seu rendimento em habitação mostram os níveis de satisfação mais baixos com uma pontuação média de {lowest_satisfaction["satisfaction_score"]:.2f}
        - O limiar de 30% (comummente utilizado como medida de acessibilidade habitacional) parece ser um marcador significativo para a satisfação
        
        Esta análise suporta a importância de políticas de controlo de rendas e habitação acessível para melhorar a satisfação habitacional geral.
        """)
    else:
        st.write("Não há dados de arrendamento disponíveis para os níveis de satisfação selecionados.")

    col1, col2 = st.columns([3, 2])

    with col1:
        # Satisfaction by district - map visualization
        st.subheader("Distribuição Geográfica da Satisfação")
        st.markdown("""
        As seguintes visualizações mostram como a satisfação habitacional varia entre diferentes regiões de Portugal.
        Estes padrões geográficos podem ajudar a identificar áreas que possam requerer políticas habitacionais direcionadas.
        """)

        # Define satisfaction weights with Portuguese descriptions
        satisfaction_weights = {
            "Very Satisfied": 2,  # Muito Satisfeito
            "Satisfied": 1,       # Satisfeito
            "Neutral": 0,         # Neutro
            "Dissatisfied": -1,   # Insatisfeito
            "Very Dissatisfied": -2, # Muito Insatisfeito
        }

        # Convert satisfaction levels to numeric scores
        filtered_df.loc[:, "satisfaction_numeric"] = filtered_df["satisfaction_level"].map(
            satisfaction_weights
        )

        # Calculate mean satisfaction score by district
        district_satisfaction = (
            filtered_df.groupby("distrito")["satisfaction_numeric"]
            .agg(["mean", "count"])
            .reset_index()
        )
        district_satisfaction = district_satisfaction.rename(
            columns={"mean": "satisfaction_score"}
        )

        # Create visualization
        fig = px.bar(
            district_satisfaction,
            x="distrito",
            y="satisfaction_score",
            color="satisfaction_score",
            color_continuous_scale=COLOR_SCALES["diverging"],
            title="Pontuação Média de Satisfação por Distrito",
            labels={
                "distrito": "Distrito",
                "satisfaction_score": "Pontuação de Satisfação (-2 a +2)",
            },
            hover_data=["count"],  # Include count in hover information
        )

        # Improve the layout
        fig.update_layout(
            xaxis_title="Distrito",
            yaxis_title="Pontuação de Satisfação (-2 a +2)",
            yaxis=dict(
                tickmode="linear",
                tick0=-2,
                dtick=0.5,
                range=[-2.1, 2.1],  # Set fixed range for better comparison
            ),
        )

        st.plotly_chart(fig)

        # Identify districts with highest and lowest satisfaction
        district_satisfaction = district_satisfaction.sort_values(
            "satisfaction_score", ascending=False
        )
        highest_district = district_satisfaction.iloc[0]["distrito"]
        lowest_district = district_satisfaction.iloc[-1]["distrito"]

        st.markdown(f"""
        **Insights Geográficos:**
        - {highest_district} apresenta a pontuação média de satisfação mais elevada
        - {lowest_district} apresenta a pontuação média de satisfação mais baixa
        - As áreas urbanas tendem a ter níveis de satisfação mais variados, provavelmente devido a custos habitacionais mais elevados mas melhores serviços
        - As áreas rurais apresentam padrões de satisfação elevada (habitação acessível, qualidade de vida) ou baixa satisfação (falta de serviços, oportunidades de emprego)
        """)

    with col2:
        # Map visualization using GeoJSON data for Portuguese districts
        st.subheader("Mapa de Satisfação de Portugal")
        st.markdown("""
        Este mapa interativo visualiza os níveis de satisfação habitacional nos distritos de Portugal.
        Áreas verdes indicam maior satisfação, enquanto áreas vermelhas mostram regiões com pontuações de satisfação mais baixas.
        Passe o cursor sobre os distritos para ver os seus nomes, e clique para estatísticas detalhadas de satisfação.
        """)

        # Custom function to create a more informative popup with statistics and styling
        def create_popup_html(district_name, score, count):
            """Create an HTML popup with styled district information."""
            # Determine satisfaction description and color based on score
            if score >= 1.5:
                description = "Satisfação Muito Alta"
                color = "#1a9850"
            elif score >= 0.5:
                description = "Satisfação Alta"
                color = "#91cf60"
            elif score >= -0.5:
                description = "Satisfação Neutra"
                color = "#fee08b"
            elif score >= -1.5:
                description = "Satisfação Baixa"
                color = "#fc8d59"
            else:
                description = "Satisfação Muito Baixa"
                color = "#d73027"

            # Create HTML with better styling
            html = f"""
            <div style="font-family: Arial, sans-serif; padding: 2px; ">
                <h3 style="margin-top: 0; margin-bottom: 10px; color: #333; border-bottom: 2px solid {color};">{district_name.capitalize()}</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: bold;">Pontuação de Satisfação:</span>
                    <span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 10px;">{score:.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: bold;">Estado:</span>
                    <span>{description}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-weight: bold;">Tamanho da Amostra:</span>
                    <span>{count} respostas</span>
                </div>
            </div>
            """
            return html

        # Load the GeoJSON file
        try:
            with open("distrito_all_s.geojson", "r") as f:
                portugal_geojson = json.load(f)

            # Ensure district names match between your dataset and GeoJSON
            # You might need to normalize district names (lowercase, remove accents, etc.)
            district_satisfaction["distrito_normalized"] = (
                district_satisfaction["distrito"]
                .str.lower()
                .str.normalize("NFKD")
                .str.encode("ascii", errors="ignore")
                .str.decode("utf-8")
            )

            # Create a dictionary for mapping district names from your dataset to GeoJSON
            district_mapping = {
                "viana do castelo": "viana do castelo",
                "braga": "braga",
                "vila real": "vila real",
                "braganca": "braganca",
                "aveiro": "aveiro",
                "coimbra": "coimbra",
                "leiria": "leiria",
                "lisboa": "lisboa",
                "porto": "porto",
                "setubal": "setubal",
                "viseu": "viseu",
                "guarda": "guarda",
                "santarem": "santarem",
                "beja": "beja",
                "castelo branco": "castelo branco",
                "evora": "evora",
                "faro": "faro",
                "portalegre": "portalegre",
                "ilha da madeira": "madeira",
                "acores": "acores",
            }

            # Create a new column with matched district names
            district_satisfaction["distrito_geojson"] = district_satisfaction[
                "distrito_normalized"
            ].map(district_mapping)

            # Convert data to dictionary for easier access
            district_satisfaction_dict = district_satisfaction.set_index(
                "distrito_geojson"
            )["satisfaction_score"].to_dict()
            district_count_dict = district_satisfaction.set_index("distrito_geojson")[
                "count"
            ].to_dict()

            # Create a base map centered on continental Portugal with better styling
            m = folium.Map(
                location=[39.6, -8.0],
                zoom_start=6,
                tiles="CartoDB Positron",  # Cleaner, more modern base map
                control_scale=True,  # Add scale bar
            )

            # Add a title to the map
            title_html = """
                    <div style="position: fixed; 
                                top: 10px; left: 50px; width: 300px; height: 30px; 
                                background-color: rgba(255, 255, 255, 0.8);
                                border-radius: 5px; 
                                font-size: 16pt; font-weight: bold;
                                text-align: center;
                                padding: 5px;
                                z-index: 9999;">
                        Satisfação Habitacional em Portugal
                    </div>
                    """
            m.get_root().html.add_child(folium.Element(title_html))

            # Define a better style function with a stronger color scale
            def style_function(feature):
                district_name = feature["properties"]["Distrito"].lower()
                try:
                    score = district_satisfaction_dict[district_name]
                    # Calculate color based on score (-2 to +2)
                    if score < -1.5:
                        # Map satisfaction levels to the Portuguese equivalents but use English values for color mapping
                        color = SATISFACTION_COLORS["Very Dissatisfied"]
                    elif score < -0.5:
                        color = SATISFACTION_COLORS["Dissatisfied"]
                    elif score < 0.5:
                        color = SATISFACTION_COLORS["Neutral"]
                    elif score < 1.5:
                        color = SATISFACTION_COLORS["Satisfied"]
                    else:
                        color = SATISFACTION_COLORS["Very Satisfied"]
                except KeyError:
                    color = "#f7f7f7"  # Gray for districts with no data

                return {
                    "fillColor": color,
                    "weight": 1.5,
                    "opacity": 1,
                    "color": "white",  # White border to distinguish districts
                    "dashArray": "",
                    "fillOpacity": 0.7,  # Slightly more opaque
                }

            # Define a highlight function for better interactivity
            def highlight_function(feature):
                return {
                    "weight": 3,
                    "color": "#666",
                    "dashArray": "",
                    "fillOpacity": 0.9,
                }

            # Add GeoJson with custom popups and styling
            folium.GeoJson(
                portugal_geojson,
                name="Satisfaction by District",
                style_function=style_function,
                highlight_function=highlight_function,
                tooltip=folium.features.GeoJsonTooltip(
                    fields=["Distrito"],
                    aliases=["Distrito:"],
                    style="background-color: white; color: #333333; font-weight: bold; font-family: Arial; font-size: 12px; padding: 10px; border-radius: 3px; box-shadow: 3px 3px 10px rgba(0,0,0,0.2);",
                ),
            ).add_to(m)

            # Add custom popups with satisfaction data
            for feature in portugal_geojson["features"]:
                district_name = feature["properties"]["Distrito"].lower()
                if district_name in district_satisfaction_dict:
                    score = district_satisfaction_dict[district_name]
                    count = district_count_dict[district_name]

                    # Get coordinates for the popup (center of polygon)
                    coords = feature["geometry"]["coordinates"]
                    if feature["geometry"]["type"] == "Polygon":
                        # Calculate centroid of first polygon
                        lat_points = [point[1] for point in coords[0]]
                        lng_points = [point[0] for point in coords[0]]
                        center_lat = sum(lat_points) / len(lat_points)
                        center_lng = sum(lng_points) / len(lng_points)
                    else:  # MultiPolygon
                        # Take the center of the first polygon in the multipolygon
                        lat_points = [point[1] for point in coords[0][0]]
                        lng_points = [point[0] for point in coords[0][0]]
                        center_lat = sum(lat_points) / len(lat_points)
                        center_lng = sum(lng_points) / len(lng_points)

                    # Add a circle marker with popup
                    folium.CircleMarker(
                        location=[center_lat, center_lng],
                        radius=5,
                        color="#333333",
                        fill=True,
                        fill_color="#333333",
                        fill_opacity=0.7,
                        popup=folium.Popup(
                            html=create_popup_html(
                                feature["properties"]["Distrito"], score, count
                            ),
                            max_width=300,
                        ),
                    ).add_to(m)

            # Add a custom legend with Portuguese satisfaction levels
            legend_html = """
                <div style="position: fixed; 
                            bottom: 10px; right: 10px; 
                            border-radius: 5px; 
                            background-color: rgba(255, 255, 255, 0.8);
                            z-index: 9999; font-size:12px;
                            padding: 5px; ">
                    <div style="text-align: center; margin-bottom: 5px; font-weight: bold;">Nível de Satisfação</div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background-color: #1a9850; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Muito Alto (1,5 a 2,0)
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background-color: #91cf60; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Alto (0,5 a 1,5)
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background-color: #fee08b; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Neutro (-0,5 a 0,5)
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background-color: #fc8d59; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Baixo (-1,5 a -0,5)
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="background-color: #d73027; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Muito Baixo (-2,0 a -1,5)
                    </div>
                </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))

            # Add mini map for context
            minimap = folium.plugins.MiniMap(toggle_display=True)
            m.add_child(minimap)

            # Add fullscreen button
            folium.plugins.Fullscreen(
                position="topleft",
                title="Expandir mapa",
                title_cancel="Sair do ecrã inteiro",
                force_separate_button=True,
            ).add_to(m)

            # Add search functionality
            folium.plugins.Search(
                layer=folium.GeoJson(portugal_geojson),
                geom_type="Polygon",
                placeholder="Procurar um distrito",
                collapsed=True,
                search_label="Distrito",
            ).add_to(m)

            # Display the map
            folium_static(m, width=800, height=400)

            # Add contextual information about the map
            st.markdown("""
            **Insights da Análise do Mapa:**
            
            - **Variações Regionais**: O mapa revela disparidades significativas na satisfação habitacional entre diferentes regiões de Portugal.
            - **Divisão Urbano-Rural**: Os grandes centros urbanos como Lisboa e Porto apresentam padrões de satisfação distintos em comparação com as áreas rurais.
            - **Litoral vs. Interior**: Os distritos costeiros geralmente demonstram perfis de satisfação diferentes dos das regiões interiores.
            - **Consideração do Tamanho da Amostra**: Ao interpretar estes dados, note que alguns distritos podem ter tamanhos de amostra menores, o que poderia afetar a fiabilidade das suas pontuações de satisfação.
            
            Clique em qualquer marcador de distrito para ver estatísticas detalhadas de satisfação.
            """)

        except Exception as e:
            st.error(f"Erro ao carregar ou processar o mapa: {e}")
            st.info(
                "Por favor, certifique-se de que o ficheiro GeoJSON 'distrito_all_s.geojson' está disponível no diretório da aplicação."
            )