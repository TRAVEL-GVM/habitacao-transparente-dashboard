#tab4_income_housing_costs.py
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import sys
from pathlib import Path

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))
from config import *


def show_income_housing_costs_tab(df):
    """
    Este separador analisa detalhadamente a relação entre rendimento e custos habitacionais, focando-se em:
    
    - Análise da sobrecarga de renda e sua distribuição entre diferentes segmentos
    - Comparação entre rendimento e custos habitacionais para proprietários e arrendatários
    - Tendências de acessibilidade de rendas ao longo do tempo
    - Simulador interativo para calcular custos habitacionais acessíveis com base no rendimento
    - Comparação com valores médios de mercado em diferentes distritos
    
    As visualizações utilizam uma combinação de gráficos circulares, de dispersão, de barras e lineares 
    para destacar os padrões de acessibilidade habitacional em Portugal.
    """
    st.header("Análise de Rendimento vs Custos Habitacionais")
    
    # Introdução com estilo melhorado
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
    <h4 style="color: #2e7d32; margin-top: 0;">Visão Geral</h4>
    <p>Esta secção analisa a relação entre os rendimentos e os custos habitacionais em Portugal, destacando questões 
    de acessibilidade e sobrecarga financeira.</p>
    <ul>
      <li><strong>Tendências Principais:</strong> Existe uma significativa disparidade na proporção do rendimento gasto em habitação entre diferentes grupos</li>
      <li><strong>Sobrecarga Habitacional:</strong> Uma percentagem considerável de portugueses gasta mais de 30% do seu rendimento em custos habitacionais</li>
      <li><strong>Variação Regional:</strong> A acessibilidade habitacional varia significativamente entre distritos</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # Calcular algumas estatísticas para as métricas rápidas
    rent_data = df[df["housing_situation"] == "Renting"]
    
    # Calcular percentagem de inquiridos com sobrecarga alta
    high_burden_count = rent_data[rent_data["rent_burden"].isin(["51-80% (High)", ">80% (Very High)"])].shape[0]
    high_burden_pct = (high_burden_count / rent_data.shape[0] * 100) if not rent_data.empty else 0
    
    # Calcular renda média
    avg_rent = rent_data["valor-mensal-renda"].mean() if not rent_data.empty else 0
    
    # Calcular valor médio de compra
    owned_data = df[df["housing_situation"] == "Owned"]
    avg_purchase = owned_data["valor-compra"].mean() if not owned_data.empty else 0
    
    # Criar 3 colunas para métricas rápidas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Sobrecarga Habitacional",
            value=f"{high_burden_pct:.1f}%",
            help="Percentagem de arrendatários que gastam mais de 50% do rendimento em habitação"
        )
    
    with col2:
        st.metric(
            label="Renda Média Mensal",
            value=f"{avg_rent:.2f} €",
            help="Valor médio de renda mensal para arrendatários"
        )
    
    with col3:
        st.metric(
            label="Preço Médio de Compra",
            value=f"{avg_purchase:.2f} €",
            help="Valor médio de compra para proprietários"
        )

    # Análise de sobrecarga de renda
    st.subheader("Análise de Sobrecarga de Renda")
    st.markdown("""
    Esta secção examina a percentagem do rendimento que as pessoas gastam em habitação, 
    com foco particular na sobrecarga de renda entre diferentes grupos e níveis de rendimento.
    """)

    col1, col2 = st.columns([2, 2])

    with col1:
        # Traduzir categorias de sobrecarga de renda
        burden_mapping = {
            '≤30% (Affordable)': '≤30% (Acessível)',
            '31-50% (Moderate)': '31-50% (Moderada)',
            '51-80% (High)': '51-80% (Alta)',
            '>80% (Very High)': '>80% (Muito Alta)',
            'Unknown': 'Desconhecida'
        }
        
        # Criar gráfico circular das categorias de sobrecarga de renda
        if not rent_data.empty:
            rent_burden_counts = rent_data["rent_burden"].value_counts().reset_index()
            rent_burden_counts.columns = ["Sobrecarga de Renda", "Contagem"]
            
            # Mapear categorias para português
            rent_burden_counts["Sobrecarga de Renda"] = rent_burden_counts["Sobrecarga de Renda"].map(
                burden_mapping
            )

            fig = px.pie(
                rent_burden_counts,
                values="Contagem",
                names="Sobrecarga de Renda",
                color="Sobrecarga de Renda",
                color_discrete_map={
                    '≤30% (Acessível)': RENT_BURDEN_COLORS['≤30% (Affordable)'],
                    '31-50% (Moderada)': RENT_BURDEN_COLORS['31-50% (Moderate)'],
                    '51-80% (Alta)': RENT_BURDEN_COLORS['51-80% (High)'],
                    '>80% (Muito Alta)': RENT_BURDEN_COLORS['>80% (Very High)'],
                    'Desconhecida': RENT_BURDEN_COLORS['Unknown']
                },
                title="Distribuição de Categorias de Sobrecarga de Renda",
            )
            fig.update_layout(
                plot_bgcolor=BACKGROUND_COLORS[0],
                paper_bgcolor=BACKGROUND_COLORS[3],
                font_color=TEXT_COLORS[2],
                title_font_color=TEXT_COLORS[0]
            )
            st.plotly_chart(fig)

    with col2:
        # Criar gráfico de dispersão rendimento vs renda
        if not rent_data.empty:
            # Garantir que 'percentagem-renda-paga' é numérico
            rent_data.loc[:, "percentagem-renda-paga"] = pd.to_numeric(
                rent_data["percentagem-renda-paga"], errors="coerce"
            )

            # Mapear sobrecarga para português
            rent_data_pt = rent_data.copy()
            rent_data_pt["sobrecarga_renda"] = rent_data_pt["rent_burden"].map(burden_mapping)

            rent_data_pt = rent_data_pt.dropna(subset=["percentagem-renda-paga"])
            fig = px.scatter(
                rent_data_pt,
                x="rendimento_numerical",
                y="valor-mensal-renda",
                color="sobrecarga_renda",
                color_discrete_map={
                    '≤30% (Acessível)': RENT_BURDEN_COLORS['≤30% (Affordable)'],
                    '31-50% (Moderada)': RENT_BURDEN_COLORS['31-50% (Moderate)'],
                    '51-80% (Alta)': RENT_BURDEN_COLORS['51-80% (High)'],
                    '>80% (Muito Alta)': RENT_BURDEN_COLORS['>80% (Very High)'],
                    'Desconhecida': RENT_BURDEN_COLORS['Unknown']
                },
                size=rent_data_pt["percentagem-renda-paga"].tolist(),
                hover_data=["distrito", "percentagem-renda-paga"],
                title="Renda Mensal vs Rendimento",
                labels={
                    "rendimento_numerical": "Rendimento Anual (€)",
                    "valor-mensal-renda": "Renda Mensal (€)",
                    "sobrecarga_renda": "Sobrecarga de Renda",
                },
            )
            fig.update_layout(
                plot_bgcolor=BACKGROUND_COLORS[0],
                paper_bgcolor=BACKGROUND_COLORS[3],
                font_color=TEXT_COLORS[2],
                title_font_color=TEXT_COLORS[0]
            )

            # Adicionar linha de referência para rácio renda-rendimento de 30%
            income_range = np.linspace(
                rent_data_pt["rendimento_numerical"].min() or 0,
                rent_data_pt["rendimento_numerical"].max() or 100000,
                100,
            )
            # 30% do rendimento mensal (rendimento anual / 12 * 0.3)
            recommended_rent = income_range / 12 * 0.3

            fig.add_trace(
                go.Scatter(
                    x=income_range,
                    y=recommended_rent,
                    mode="lines",
                    line=dict(color=TEXT_COLORS[0], dash="dash"),
                    name="30% do Rendimento (Recomendado)",
                )
            )

            st.plotly_chart(fig)

    # Comparação rendimento para custo habitacional
    st.subheader("Comparação entre Rendimento e Custo Habitacional")
    st.markdown("""
    Esta secção compara o rendimento com os custos habitacionais entre diferentes situações habitacionais,
    analisando como os custos habitacionais variam em relação ao rendimento.
    """)

    # Distribuição de rendimento por situação habitacional
    col1, col2 = st.columns([1, 1])

    with col1:
        # Traduzir situações habitacionais
        housing_mapping = {
            'Renting': 'Arrendamento',
            'Owned': 'Propriedade',
            'Living with others': 'A viver com outros'
        }
        
        # Aplicar mapeamento
        df_pt = df.copy()
        df_pt['situacao_habitacional'] = df_pt['housing_situation'].map(housing_mapping)
        
        # Gráfico de caixa de rendimento por situação habitacional
        fig = px.box(
            df_pt,
            x="situacao_habitacional",
            y="rendimento_numerical",
            color="situacao_habitacional",
            color_discrete_map={
                'Arrendamento': HOUSING_COLORS['Renting'],
                'Propriedade': HOUSING_COLORS['Owned'],
                'A viver com outros': HOUSING_COLORS['Living with others']
            },
            title="Distribuição de Rendimento por Situação Habitacional",
            labels={
                "situacao_habitacional": "Situação Habitacional",
                "rendimento_numerical": "Rendimento Anual (€)",
            },
        )
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig)

    with col2:
        # Calcular rácio custo habitacional para rendimento
        housing_cost_data = df.copy()

        # Calcular custos habitacionais mensais
        housing_cost_data["monthly_housing_cost"] = np.nan

        # Para arrendatários, usar renda mensal
        renters_mask = housing_cost_data["housing_situation"] == "Renting"
        housing_cost_data.loc[renters_mask, "monthly_housing_cost"] = (
            housing_cost_data.loc[renters_mask, "valor-mensal-renda"]
        )

        # Para proprietários, estimar pagamento mensal da hipoteca
        # Assumir hipoteca de 25 anos a 3% de taxa de juro (cálculo simplificado)
        owners_mask = housing_cost_data["housing_situation"] == "Owned"
        # Pagamento mensal = P * r * (1+r)^n / ((1+r)^n - 1)
        # Onde P = principal, r = taxa mensal, n = número de pagamentos
        r = 0.03 / 12  # Taxa de juro mensal
        n = 25 * 12  # Número de pagamentos (25 anos)

        # Calcular fator da hipoteca
        mortgage_factor = r * (1 + r) ** n / ((1 + r) ** n - 1)

        housing_cost_data.loc[owners_mask, "monthly_housing_cost"] = (
            housing_cost_data.loc[owners_mask, "valor-compra"] * mortgage_factor
        )

        # Calcular rácio custo habitacional para rendimento
        housing_cost_data["monthly_income"] = (
            housing_cost_data["rendimento_numerical"] / 12
        )
        housing_cost_data["housing_cost_ratio"] = (
            housing_cost_data["monthly_housing_cost"]
            / housing_cost_data["monthly_income"]
            * 100
        )

        # Criar categorias para rácio custo habitacional
        housing_cost_data["cost_income_category"] = pd.cut(
            housing_cost_data["housing_cost_ratio"],
            bins=[0, 30, 50, 80, float("inf")],
            labels=["≤30%", "31-50%", "51-80%", ">80%"],
        )
        
        # Traduzir situações habitacionais
        housing_cost_data['situacao_habitacional'] = housing_cost_data['housing_situation'].map(housing_mapping)

        # Gráfico de barras de rácio custo habitacional para rendimento por situação
        cost_ratio_pivot = pd.crosstab(
            housing_cost_data["situacao_habitacional"],
            housing_cost_data["cost_income_category"],
        ).reset_index()

        cost_ratio_melted = pd.melt(
            cost_ratio_pivot,
            id_vars=["situacao_habitacional"],
            var_name="Rácio Custo/Rendimento",
            value_name="Contagem",
        )

        fig = px.bar(
            cost_ratio_melted,
            x="situacao_habitacional",
            y="Contagem",
            color="Rácio Custo/Rendimento",
            title="Rácio Custo Habitacional/Rendimento por Situação",
            labels={
                "situacao_habitacional": "Situação Habitacional",
                "Contagem": "Número de Inquiridos",
            },
            color_discrete_sequence=COLOR_SCALES['sequential'],
        )
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig)

    # Tendências de acessibilidade de renda ao longo do tempo
    st.subheader("Tendências de Acessibilidade de Renda")
    st.markdown("""
    Esta secção examina como a acessibilidade da renda evoluiu ao longo do tempo,
    analisando as rendas médias e os rácios renda-rendimento por ano de início do arrendamento.
    """)

    col1, col2 = st.columns([1, 1])

    with col1:
        # Extrair ano da data de início do arrendamento
        rent_time_data = df[df["housing_situation"] == "Renting"].copy()
        rent_time_data["rental_year"] = (
            rent_time_data["ano-inicio-arrendamento"].astype(float).astype("Int64")
        )

        # Agrupar por ano e calcular renda média
        yearly_rent = (
            rent_time_data.groupby("rental_year")["valor-mensal-renda"]
            .mean()
            .reset_index()
        )
        yearly_rent = yearly_rent.sort_values("rental_year")

        fig = px.line(
            yearly_rent,
            x="rental_year",
            y="valor-mensal-renda",
            markers=True,
            title="Renda Média Mensal por Ano de Início",
            labels={
                "rental_year": "Ano de Início do Arrendamento",
                "valor-mensal-renda": "Renda Média Mensal (€)",
            },
            color_discrete_sequence=[PRIMARY_COLORS[0]]
        )
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig)

    with col2:
        # Calcular rácio renda para rendimento ao longo do tempo
        rent_time_data["rent_income_ratio"] = (
            rent_time_data["valor-mensal-renda"]
            * 12
            / rent_time_data["rendimento_numerical"]
        ) * 100

        yearly_ratio = (
            rent_time_data.groupby("rental_year")["rent_income_ratio"]
            .mean()
            .reset_index()
        )
        yearly_ratio = yearly_ratio.sort_values("rental_year")

        fig = px.line(
            yearly_ratio,
            x="rental_year",
            y="rent_income_ratio",
            markers=True,
            title="Rácio Médio Renda/Rendimento por Ano de Início",
            labels={
                "rental_year": "Ano de Início do Arrendamento",
                "rent_income_ratio": "Rácio Renda/Rendimento (%)",
            },
            color_discrete_sequence=[SECONDARY_COLORS[0]]
        )
        fig.add_hline(
            y=30,
            line_dash="dash",
            line_color=RENT_BURDEN_COLORS['≤30% (Affordable)'],
            annotation_text="Limiar de Acessibilidade 30%",
            annotation_position="bottom right",
        )
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig)

    # Simulador interativo de acessibilidade
    st.subheader("Simulador de Acessibilidade Habitacional")
    st.markdown("""
    Utilize este simulador para calcular quais os custos habitacionais que seriam acessíveis com base em diferentes níveis de rendimento.
    O calculador utiliza a regra dos 30%: os custos habitacionais não devem exceder 30% do rendimento mensal bruto.
    """)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        income_input = st.number_input(
            "Rendimento Anual (€)", min_value=0, max_value=200000, value=30000, step=1000
        )

    with col2:
        # Calcular rendimento mensal e custos habitacionais acessíveis
        monthly_income = income_input / 12
        affordable_housing = monthly_income * 0.3

        st.metric("Rendimento Mensal (€)", f"{monthly_income:.2f}")

    with col3:
        st.metric(
            "Custo Habitacional Mensal Acessível (€)",
            f"{affordable_housing:.2f}",
            delta="30% do rendimento",
        )

    # Comparar com valores de mercado
    st.subheader("Comparação com Valores de Mercado")
    st.markdown("""
    Esta secção compara os custos habitacionais acessíveis calculados com as médias de mercado por distrito,
    ajudando a identificar quais os distritos mais acessíveis para diferentes níveis de rendimento.
    """)

    col1, col2 = st.columns(2)

    with col1:
        # Renda média por distrito
        district_rent = (
            df[df["housing_situation"] == "Renting"]
            .groupby("distrito")["valor-mensal-renda"]
            .mean()
            .reset_index()
        )
        district_rent.columns = ["Distrito", "Renda Média"]
        district_rent = district_rent.sort_values("Renda Média", ascending=False)

        fig = px.bar(
            district_rent,
            x="Distrito",
            y="Renda Média",
            title="Renda Média por Distrito",
            labels={"Renda Média": "Renda Média Mensal (€)"},
            color_discrete_sequence=[PRIMARY_COLORS[0]]
        )

        # Adicionar linha para renda acessível com base no input
        fig.add_hline(
            y=affordable_housing,
            line_dash="dash",
            line_color=RENT_BURDEN_COLORS['≤30% (Affordable)'],
            annotation_text="Sua Renda Acessível",
            annotation_position="top right",
        )

        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig)

    with col2:
        # Calcular índice de acessibilidade
        district_affordability = district_rent.copy()
        district_affordability["Índice de Acessibilidade"] = (
            affordable_housing / district_affordability["Renda Média"]
        )
        district_affordability["Acessível"] = (
            district_affordability["Índice de Acessibilidade"] >= 1
        )
        district_affordability = district_affordability.sort_values(
            "Índice de Acessibilidade", ascending=False
        )

        fig = px.bar(
            district_affordability,
            x="Distrito",
            y="Índice de Acessibilidade",
            color="Acessível",
            title="Índice de Acessibilidade Habitacional por Distrito",
            labels={"Índice de Acessibilidade": "Índice de Acessibilidade (>1 é acessível)"},
            color_discrete_map={True: RENT_BURDEN_COLORS['≤30% (Affordable)'], 
                              False: RENT_BURDEN_COLORS['>80% (Very High)']},
        )
        fig.add_hline(
            y=1,
            line_dash="dash",
            line_color=TEXT_COLORS[0],
            annotation_text="Limiar de Acessibilidade",
            annotation_position="bottom right",
        )
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig)
        
    # Adicionar insights finais
    st.markdown("""
    **Insights-Chave sobre Acessibilidade Habitacional:**
    
    - **Sobrecarga de Renda:** Uma proporção significativa dos arrendatários portugueses enfrenta sobrecarga de renda, gastando mais de 30% do seu rendimento em habitação
    - **Disparidades entre Proprietários e Arrendatários:** Os proprietários tendem a ter rendimentos mais elevados e menor sobrecarga habitacional comparativamente aos arrendatários
    - **Evolução Temporal:** As rendas têm aumentado mais rapidamente do que os rendimentos nos últimos anos, levando a um declínio na acessibilidade
    - **Variações Regionais:** Existe uma grande variação na acessibilidade habitacional entre os distritos portugueses, com áreas urbanas a apresentarem desafios particulares
    - **Rendimento e Acessibilidade:** Para muitos portugueses com rendimentos médios ou baixos, encontrar habitação acessível nos centros urbanos é extremamente difícil
    
    Estes padrões sugerem a necessidade de políticas habitacionais específicas direcionadas para melhorar a acessibilidade, especialmente para famílias de rendimentos baixos e médios nos centros urbanos com elevados custos habitacionais.
    """)