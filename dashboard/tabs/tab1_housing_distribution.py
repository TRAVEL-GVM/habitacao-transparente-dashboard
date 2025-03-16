# tab1_housing_distribution.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))
from config import *


def show_housing_distribution_tab(df):
    """
    Apresenta a distribuição das situações habitacionais em Portugal com visualizações aprimoradas, insights e filtros.

    Parâmetros:
    df (DataFrame): Os dados habitacionais processados
    """
    st.header("Distribuição de Situações Habitacionais")

    # Introdução com estilo melhorado
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32;">
    <h4 style="color: #2e7d32; margin-top: 0;">Visão Geral</h4>
    <p>Esta secção analisa como os residentes portugueses estão distribuídos em diferentes situações habitacionais,
    revelando padrões complexos de posse, arrendamento e arranjos de vida compartilhada.</p>
    <ul>
      <li><strong>Situações Habitacionais:</strong> Arrendamento, Propriedade e Vivendo com Outros</li>
      <li><strong>Tendências Principais:</strong> Variações significativas nas situações habitacionais entre diferentes grupos etários</li>
      <li><strong>Análise Detalhada:</strong> Distribuição e fatores que influenciam as escolhas habitacionais em Portugal</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        # Calculate percentages for better context
        housing_counts = df["housing_situation"].value_counts().reset_index()
        housing_counts.columns = ["Housing Situation", "Count"]
        total = housing_counts["Count"].sum()
        housing_counts["Percentage"] = (housing_counts["Count"] / total * 100).round(
            1
        ).astype(str) + "%"

        # Create enhanced pie chart with percentages using HOUSING_COLORS
        fig = px.pie(
            housing_counts,
            values="Count",
            names="Housing Situation",
            color="Housing Situation",
            color_discrete_map=HOUSING_COLORS,
            title="Distribuição das Situações Habitacionais",
            hover_data=["Percentage"],
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[3],  # White background
            paper_bgcolor=BACKGROUND_COLORS[3],  # White paper
            title_font_color=TEXT_COLORS[0],    # Dark green title
            font_color=TEXT_COLORS[2],          # Medium green text
        )
        st.plotly_chart(fig)

        # Add insights below the chart
        dominant_situation = housing_counts.iloc[housing_counts["Count"].argmax()][
            "Housing Situation"
        ]
        st.markdown(f"""
        **Principais Conclusões:**
        - {dominant_situation} é a situação habitacional mais comum em Portugal
        - {housing_counts.iloc[housing_counts["Count"].argmax()]["Percentage"]} dos inquiridos encontram-se em {dominant_situation.lower() if dominant_situation != "Living with others" else "vivem com outros"}
        """)

    with col2:
        st.subheader("Situação Habitacional por Faixa Etária")
        # Extract birth year range for age groups and improve labeling
        df["birth_period"] = df["ano_nascimento_interval"].str.extract(r"\[(\d+)")
        df["birth_period"] = pd.to_numeric(df["birth_period"], errors="coerce")

        # Calculate approximate current age (as of 2025)
        df["approx_age"] = 2025 - df["birth_period"]

        df["age_group"] = pd.cut(
            df["birth_period"],
            bins=[1960, 1970, 1980, 1990, 2000, 2025],
            labels=[
                "1960s (~55-65)",
                "1970s (~45-55)",
                "1980s (~35-45)",
                "1990s (~25-35)",
                "2000s+ (<25)",
            ],
        )

        # Pivot table for housing situation by age group
        pivot_data = (
            pd.crosstab(df["age_group"], df["housing_situation"], normalize="index")
            * 100
        )
        pivot_data = pivot_data.round(1).reset_index()
        pivot_data_melted = pd.melt(
            pivot_data,
            id_vars=["age_group"],
            var_name="Housing Situation",
            value_name="Percentage",
        )

        fig = px.bar(
            pivot_data_melted,
            x="age_group",
            y="Percentage",
            color="Housing Situation",
            color_discrete_map=HOUSING_COLORS,  # Use consistent housing colors
            title="Situação Habitacional por Década de Nascimento",
            labels={
                "age_group": "Década de Nascimento (Intervalo Etário)",
                "Percentage": "Percentagem (%)",
            },
        )
        fig.update_layout(
            xaxis_title="Década de Nascimento (Intervalo Etário Aproximado)",
            plot_bgcolor=BACKGROUND_COLORS[0],    # Light green background
            paper_bgcolor=BACKGROUND_COLORS[3],   # White paper
            font_color=TEXT_COLORS[2],           # Medium green text
            title_font_color=TEXT_COLORS[0],     # Dark green title
            legend_title_font_color=TEXT_COLORS[1],  # Dark green legend title
            xaxis=dict(
                tickfont=dict(color=TEXT_COLORS[2]),  # Medium green tick labels
                title_font=dict(color=TEXT_COLORS[1])  # Dark green axis title
            ),
            yaxis=dict(
                tickfont=dict(color=TEXT_COLORS[2]),  # Medium green tick labels
                title_font=dict(color=TEXT_COLORS[1])  # Dark green axis title
            ),
        )
        st.plotly_chart(fig)

        # Add insights about generational differences
        st.markdown("""
        **Tendências Geracionais:**
        - As gerações mais novas (nascidas entre os anos 1990-2000) apresentam taxas mais elevadas de arrendamento e de viver com outros
        - A propriedade aumenta significativamente com a idade, atingindo o pico nas gerações mais velhas
        - Estes padrões refletem as condições económicas e os desafios de acessibilidade à habitação enfrentados pelos portugueses mais jovens
        """)

    # Housing situation filters - now with more context
    st.subheader("Explorar Situações Habitacionais em Detalhe")
    st.markdown("""
    Selecione uma situação habitacional específica abaixo para explorar métricas e padrões detalhados dentro desse grupo.
    Isto permite uma análise mais profunda dos fatores que afetam as diferentes situações habitacionais.
    """)

    # Adiciona mapeamento entre os rótulos em português e os valores dos dados
    map_housing = {
        "Arrendamento": "Renting",
        "Própria": "Owned",
        "Vivendo com outros": "Living with others"
    }
    selected_situation = st.selectbox(
        "Selecione a Situação Habitacional a Explorar",
        options=list(map_housing.keys()) + ["Todas"]
    )

    if selected_situation != "Todas":
        filtered_df = df[df["housing_situation"] == map_housing[selected_situation]]
    else:
        filtered_df = df

    # Display enhanced statistics based on filter
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Contagem Total", len(filtered_df))
    with col2:
        avg_birth = filtered_df["birth_period"].mean()
        if not pd.isna(avg_birth):
            st.metric("Ano de Nascimento Médio", f"{avg_birth:.0f}")
            st.caption(f"Idade Aproximada: {2025 - avg_birth:.0f}")
    with col3:
        if selected_situation == "Arrendamento":
            avg_rent = filtered_df["valor-mensal-renda"].mean()
            if not pd.isna(avg_rent):
                st.metric("Renda Mensal Média", f"€{avg_rent:.2f}")
        elif selected_situation == "Própria":
            avg_price = filtered_df["valor-compra"].mean()
            if not pd.isna(avg_price):
                st.metric("Preço Médio de Compra", f"€{avg_price:.2f}")
    with col4:
        if selected_situation != "Todas":
            try:
                # Average area for the selected housing situation
                avg_area = filtered_df["area_numerical"].mean()
                if not pd.isna(avg_area):
                    st.metric("Área Média de Habitação", f"{avg_area:.0f} m²")
            except Exception:
                pass

    # Additional visualization for the selected housing situation
    if selected_situation != "Todas":
        st.subheader(f"{selected_situation} - Distribuição do Nível de Educação")

        # Create education level distribution visualization
        edu_counts = filtered_df["education_level"].value_counts().reset_index()
        edu_counts.columns = ["Education Level", "Count"]

        # Sort education levels by a logical order
        education_order = [
            "Basic",
            "High School",
            "Vocational",
            "Bachelor's",
            "Master's",
            "PhD",
        ]
        edu_counts["Education Level"] = pd.Categorical(
            edu_counts["Education Level"], categories=education_order, ordered=True
        )
        edu_counts = edu_counts.sort_values("Education Level")

        fig = px.bar(
            edu_counts,
            x="Education Level",
            y="Count",
            color="Education Level",
            color_discrete_sequence=PRIMARY_COLORS,  # Use primary color palette
            title=f"Distribuição do Nível de Educação para {selected_situation}",
        )
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            showlegend=False  # Hide legend since colors are just for aesthetics
        )
        st.plotly_chart(fig)

        st.markdown(f"""
        Este gráfico mostra a distribuição do nível de educação entre as pessoas na situação habitacional "{selected_situation}".
        O nível de educação pode influenciar significativamente as escolhas de habitação e as oportunidades, devido ao seu impacto no potencial de rendimento e na estabilidade financeira.
        """)

        # Display financial metrics if available for the housing situation
        if selected_situation == "Arrendamento":
            st.subheader("Análise do Peso da Renda")

            # Create donut chart for rent burden categories
            rent_burden_counts = filtered_df["rent_burden"].value_counts().reset_index()
            rent_burden_counts.columns = ["Rent Burden", "Count"]

            fig = px.pie(
                rent_burden_counts,
                values="Count",
                names="Rent Burden",
                title="Distribuição do Peso da Renda",
                hole=0.4,
                color="Rent Burden",
                color_discrete_map=RENT_BURDEN_COLORS,
            )
            st.plotly_chart(fig)

            st.markdown("""
            **Explicação do Peso da Renda:**
            - **≤30% (Acessível)**: Os custos de habitação são geralmente considerados acessíveis quando não ultrapassam os 30% do rendimento familiar
            - **31-50% (Moderado)**: Estes domicílios enfrentam alguma pressão financeira devido aos custos de habitação
            - **51-80% (Elevado)**: Os custos de habitação criam uma pressão financeira significativa
            - **>80% (Muito Elevado)**: Pressão financeira extrema devido aos custos de habitação
            
            Pesos de renda mais elevados frequentemente levam a uma redução dos gastos noutras necessidades e à dificuldade em poupar para o futuro.
            """)
