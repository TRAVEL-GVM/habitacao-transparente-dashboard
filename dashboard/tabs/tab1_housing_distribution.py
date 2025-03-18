# tab1_housing_distribution.py
import streamlit as st
import pandas as pd
import numpy as np
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
    <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 10px;">
    <h4 style="color: #2e7d32; margin-top: 0;">Visão Geral</h4>
    <p>Esta secção analisa como os residentes portugueses estão distribuídos em diferentes situações habitacionais,
    revelando padrões complexos de posse, arrendamento e arranjos de vida compartilhada.</p>
    <ul>
      <li><strong>Situações Habitacionais:</strong> Arrendamento, Casa Própria ou Outro</li>
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
        - **{dominant_situation}** é a situação habitacional mais comum em Portugal
        - **{housing_counts.iloc[housing_counts["Count"].argmax()]["Percentage"]}** dos inquiridos encontram-se em {dominant_situation.lower() if dominant_situation != "Others" else "vivem com outros"}
        """)

    with col2:
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
        "Arrendamento": "Arrendamento",
        "Casa Própria": "Casa Própria",
        "Others": "Others"
    }
    selected_situation = st.selectbox(
        "Selecione a Situação Habitacional a Explorar",
        options=list(map_housing.values()) + ["Todas"]
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
        elif selected_situation == "Casa Própria":
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

        # Translate education levels to Portuguese
        translation_map = {
            "Basic": "Básico",
            "High School": "Secundário",
            "Vocational": "Profissional",
            "Bachelor's": "Licenciatura",
            "Master's": "Mestrado",
            "PhD": "Doutoramento",
        }
        edu_counts["Education Level"] = edu_counts["Education Level"].map(translation_map)

        # Sort education levels by a logical order
        education_order = [
            "Básico",
            "Secundário",
            "Profissional",
            "Licenciatura",
            "Mestrado",
            "Doutoramento",
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
            labels={"Education Level": "Nível de Educação", "Count": "Contagem"}
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

    # Secção para estratégias de compra e arrendamento
    st.header("Estratégias de Compra e Arrendamento")
    
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 10px;">
    <h4 style="color: #2e7d32; margin-top: 0;">Análise de Estratégias</h4>
    <p>Esta secção analisa as principais estratégias utilizadas pelos residentes portugueses para arrendar ou comprar habitação,
    revelando diferentes abordagens e necessidades no mercado imobiliário.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Criar duas colunas para as análises de arrendamento e compra
    col1, col2 = st.columns(2)

    # Função para verificar valores únicos nas estratégias
    def check_unique_strategies(df):
        # Para estratégias de arrendamento
        rent_strategies = set()
        for strategies in df['estrategia-arrendamento'].dropna():
            if isinstance(strategies, list):
                for strategy in strategies:
                    rent_strategies.add(strategy)
        
        # Limpar os valores de rent_strategies
        cleaned_rent_strategies = set()
        for strategy in rent_strategies:
            # Substituir underscores e dash por espaços e capitalizar primeira letra
            cleaned_strategy = strategy.replace('_', ' ').replace('-', ' ').capitalize()
            cleaned_rent_strategies.add(cleaned_strategy)
        
        print("Valores únicos em estrategia-arrendamento:")
        print(sorted(list(cleaned_rent_strategies)))
        
        # Para estratégias de compra
        buy_strategies = set()
        for strategies in df['estrategia-compra'].dropna():
            if isinstance(strategies, list):
                for strategy in strategies:
                    buy_strategies.add(strategy)
        
        # Limpar os valores de buy_strategies
        cleaned_buy_strategies = set()
        for strategy in buy_strategies:
            # Substituir underscores por espaços e capitalizar primeira letra
            cleaned_strategy = strategy.replace('_', ' ').replace('-', ' ').capitalize()
            cleaned_buy_strategies.add(cleaned_strategy)
        
        print("\nValores únicos em estrategia-compra:")
        print(sorted(list(cleaned_buy_strategies)))
        
        return cleaned_rent_strategies, cleaned_buy_strategies

    # Para executar esta verificação, você adicionaria este bloco temporariamente no início da função
    # show_housing_distribution_tab ou o executaria em uma célula Jupyter separada antes de finalizar o código
    rent_unique, buy_unique = check_unique_strategies(df)

    # Criar mapas a partir dos valores únicos
    rent_strategy_map = {strategy.lower().replace(' ', '-'): strategy for strategy in rent_unique}
    buy_strategy_map = {strategy.lower().replace(' ', '-'): strategy for strategy in buy_unique}

    
    with col1:
        st.subheader("Estratégias de Arrendamento")
        
        # Processar os dados de estratégia de arrendamento
        # Extrair todas as estratégias mencionadas por respondentes
        rent_strategies = []
        for strategies in df['estrategia-arrendamento'].dropna():
            if isinstance(strategies, list):
                rent_strategies.extend(strategies)
        
        rent_strategy_counts = pd.Series(rent_strategies).value_counts().reset_index()
        rent_strategy_counts.columns = ["Estratégia", "Contagem"]
        
        rent_strategy_counts['Estratégia'] = rent_strategy_counts['Estratégia'].map(rent_strategy_map)
        
        # Criar gráfico de barras para estratégias de arrendamento
        fig = px.bar(
            rent_strategy_counts,
            x="Estratégia",
            y="Contagem",
            color="Estratégia",
            color_discrete_sequence=PRIMARY_COLORS,
            title="Estratégias Utilizadas para Encontrar Arrendamento",
            labels={"Estratégia": "Estratégia de Arrendamento", "Contagem": "Número de Pessoas"}
        )
        fig.update_layout(
            xaxis_title="Estratégia de Arrendamento",
            yaxis_title="Número de Pessoas",
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            showlegend=False,
            xaxis={'categoryorder':'total descending'}
        )
        st.plotly_chart(fig)
        
        # Adicionar insights sobre as estratégias de arrendamento
        top_rent_strategy = rent_strategy_counts.iloc[0]['Estratégia']
        st.markdown(f"""
        **Principais Conclusões:**
        - A estratégia mais comum para encontrar arrendamento é através de {top_rent_strategy}
        - {rent_strategy_counts.iloc[0]['Contagem']} pessoas utilizaram esta estratégia
        - O mercado de arrendamento em Portugal é fortemente influenciado por redes pessoais e plataformas online
        """)
        
        # Análise adicional: Relação entre estratégia de arrendamento e valor da renda
        st.subheader("Valor da Renda por Estratégia")
        
        # Criar um dataframe para armazenar valor médio de renda por estratégia
        rent_values_by_strategy = []
        
        for strategy in rent_strategy_map.keys():
            strategy_df = df[df['estrategia-arrendamento'].apply(
                lambda x: isinstance(x, list) and strategy in x
            )]
            
            avg_rent = strategy_df['valor-mensal-renda'].mean()
            if not pd.isna(avg_rent):
                rent_values_by_strategy.append({
                    'Estratégia': rent_strategy_map.get(strategy, strategy),
                    'Renda Média': avg_rent
                })
        
        rent_values_df = pd.DataFrame(rent_values_by_strategy)
        
        if not rent_values_df.empty:
            # Ordenar por valor de renda
            rent_values_df = rent_values_df.sort_values('Renda Média', ascending=False)
            
            fig = px.bar(
                rent_values_df,
                x="Estratégia",
                y="Renda Média",
                color="Estratégia",
                color_discrete_sequence=PRIMARY_COLORS,
                title="Renda Média Mensal por Estratégia de Arrendamento",
                labels={"Renda Média": "Valor Médio da Renda (€)"}
            )
            fig.update_layout(
                plot_bgcolor=BACKGROUND_COLORS[0],
                paper_bgcolor=BACKGROUND_COLORS[3],
                showlegend=False
            )
            st.plotly_chart(fig)
            
            st.markdown("""
            Este gráfico mostra a relação entre as estratégias utilizadas para encontrar arrendamento e o valor médio 
            da renda mensal. Diferentes canais de procura podem estar associados a diferentes segmentos do mercado imobiliário.
            """)
    
    with col2:
        st.subheader("Estratégias de Compra")
        
        # Processar os dados de estratégia de compra
        buy_strategies = []
        for strategies in df['estrategia-compra'].dropna():
            if isinstance(strategies, list):
                buy_strategies.extend(strategies)
        
        buy_strategy_counts = pd.Series(buy_strategies).value_counts().reset_index()
        buy_strategy_counts.columns = ["Estratégia", "Contagem"]
        
        buy_strategy_counts['Estratégia'] = buy_strategy_counts['Estratégia'].map(buy_strategy_map)
        
        # Criar gráfico de barras para estratégias de compra
        fig = px.bar(
            buy_strategy_counts,
            x="Estratégia",
            y="Contagem",
            color="Estratégia",
            color_discrete_sequence=PRIMARY_COLORS,
            title="Estratégias Utilizadas para Compra de Habitação",
            labels={"Estratégia": "Estratégia de Compra", "Contagem": "Número de Pessoas"}
        )
        fig.update_layout(
            xaxis_title="Estratégia de Compra",
            yaxis_title="Número de Pessoas",
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            showlegend=False,
            xaxis={'categoryorder':'total descending'}
        )
        st.plotly_chart(fig)
        
        # Adicionar insights sobre as estratégias de compra
        top_buy_strategy = buy_strategy_counts.iloc[0]['Estratégia']
        st.markdown(f"""
        **Principais Conclusões:**
        - A estratégia mais comum para compra de habitação é através de {top_buy_strategy}
        - {buy_strategy_counts.iloc[0]['Contagem']} pessoas utilizaram esta estratégia
        - O mercado de compra em Portugal demonstra padrões distintos em comparação com o mercado de arrendamento
        """)
        
        # Análise adicional: Relação entre estratégia de compra e valor da propriedade
        st.subheader("Valor de Compra por Estratégia")
        
        # Criar um dataframe para armazenar valor médio de compra por estratégia
        purchase_values_by_strategy = []
        
        for strategy in buy_strategy_map.keys():
            strategy_df = df[df['estrategia-compra'].apply(
                lambda x: isinstance(x, list) and strategy in x
            )]
            
            avg_purchase = strategy_df['valor-compra'].mean()
            if not pd.isna(avg_purchase):
                purchase_values_by_strategy.append({
                    'Estratégia': buy_strategy_map.get(strategy, strategy),
                    'Valor Médio': avg_purchase
                })
        
        purchase_values_df = pd.DataFrame(purchase_values_by_strategy)
        
        if not purchase_values_df.empty:
            # Ordenar por valor de compra
            purchase_values_df = purchase_values_df.sort_values('Valor Médio', ascending=False)
            
            fig = px.bar(
                purchase_values_df,
                x="Estratégia",
                y="Valor Médio",
                color="Estratégia",
                color_discrete_sequence=PRIMARY_COLORS,
                title="Valor Médio de Compra por Estratégia",
                labels={"Valor Médio": "Valor Médio de Compra (€)"}
            )
            fig.update_layout(
                plot_bgcolor=BACKGROUND_COLORS[0],
                paper_bgcolor=BACKGROUND_COLORS[3],
                showlegend=False
            )
            st.plotly_chart(fig)
            
            st.markdown("""
            Este gráfico mostra a relação entre as estratégias utilizadas para compra de habitação e o valor médio 
            de compra. As diferentes estratégias podem estar associadas a diferentes segmentos de preço no mercado imobiliário.
            """)
    
    # Análise comparativa entre anos de início de arrendamento/compra e valores
    st.subheader("Evolução Temporal dos Valores de Habitação")
    
    # Criar tabs para separar análises de arrendamento e compra
    rent_tab, buy_tab = st.tabs(["Evolução de Arrendamento", "Evolução de Compra"])
    
    with rent_tab:
        # Filtrar dados válidos para análise de arrendamento
        rent_time_df = df[df['ano-inicio-arrendamento'].notna() & 
                         df['valor-mensal-renda'].notna()].copy()
        
        if not rent_time_df.empty:
            # Agrupar por ano de início do arrendamento
            rent_time_df['ano-inicio-arrendamento'] = rent_time_df['ano-inicio-arrendamento'].astype(int)
            rent_year_groups = rent_time_df.groupby('ano-inicio-arrendamento')['valor-mensal-renda'].mean().reset_index()
            rent_year_groups.columns = ['Ano de Início', 'Renda Média']
            
            # Criar gráfico de linha para evolução do valor de renda ao longo do tempo
            fig = px.line(
                rent_year_groups,
                x='Ano de Início',
                y='Renda Média',
                markers=True,
                title='Evolução do Valor Médio da Renda por Ano de Início',
                labels={'Renda Média': 'Valor Médio da Renda (€)'}
            )
            fig.update_layout(
                plot_bgcolor=BACKGROUND_COLORS[0],
                paper_bgcolor=BACKGROUND_COLORS[3],
                xaxis=dict(
                    tickmode='linear',
                    tick0=rent_year_groups['Ano de Início'].min(),
                    dtick=5  # Mostrar ticks a cada 5 anos
                )
            )
            st.plotly_chart(fig)
            
            st.markdown("""
            Este gráfico mostra como o valor médio das rendas mudou ao longo do tempo, representando
            contratos de arrendamento iniciados em diferentes anos. Note que estes valores refletem
            os contratos ainda ativos e não necessariamente o valor médio de mercado em cada ano.
            """)
    
    with buy_tab:
        # Filtrar dados válidos para análise de compra
        buy_time_df = df[df['ano-compra'].notna() & 
                        df['valor-compra'].notna()].copy()
        
        if not buy_time_df.empty:
            # Agrupar por ano de compra
            buy_time_df['ano-compra'] = buy_time_df['ano-compra'].astype(int)
            buy_year_groups = buy_time_df.groupby('ano-compra')['valor-compra'].mean().reset_index()
            buy_year_groups.columns = ['Ano de Compra', 'Valor Médio']
            
            # Criar gráfico de linha para evolução do valor de compra ao longo do tempo
            fig = px.line(
                buy_year_groups,
                x='Ano de Compra',
                y='Valor Médio',
                markers=True,
                title='Evolução do Valor Médio de Compra por Ano',
                labels={'Valor Médio': 'Valor Médio de Compra (€)'}
            )
            fig.update_layout(
                plot_bgcolor=BACKGROUND_COLORS[0],
                paper_bgcolor=BACKGROUND_COLORS[3],
                xaxis=dict(
                    tickmode='linear',
                    tick0=buy_year_groups['Ano de Compra'].min(),
                    dtick=5  # Mostrar ticks a cada 5 anos
                )
            )
            st.plotly_chart(fig)
            
            st.markdown("""
            Este gráfico mostra como o valor médio das compras de habitação mudou ao longo do tempo,
            representando aquisições realizadas em diferentes anos. Note que estes valores não estão 
            ajustados para inflação e refletem os valores reportados pelos respondentes.
            """)
    
    # Análise da relação entre estratégias e satisfação
    st.subheader("Estratégias e Níveis de Satisfação")
    
    # Criar um dataframe para análise de satisfação por estratégia
    satisfaction_by_strategy = []
    
    # Mapear níveis de satisfação para valores numéricos para cálculo de média
    satisfaction_map = {
        'muito-satisfeito': 5,
        'satisfeito': 4,
        'indiferente': 3,
        'insatisfeito': 2,
        'muito-insatisfeito': 1
    }
    
    # Função para extrair o valor numérico da satisfação principal
    def get_satisfaction_value(satisfacao_list):
        if isinstance(satisfacao_list, list) and len(satisfacao_list) > 0:
            return satisfaction_map.get(satisfacao_list[0], np.nan)
        return np.nan
    
    # Aplicar função para criar coluna numérica de satisfação
    df['satisfaction_numeric'] = df['satisfacao'].apply(get_satisfaction_value)
    
    # Analisar satisfação para estratégias de arrendamento
    for strategy in rent_strategy_map.keys():
        strategy_df = df[df['estrategia-arrendamento'].apply(
            lambda x: isinstance(x, list) and strategy in x
        )]
        
        avg_satisfaction = strategy_df['satisfaction_numeric'].mean()
        if not pd.isna(avg_satisfaction):
            satisfaction_by_strategy.append({
                'Estratégia': rent_strategy_map.get(strategy, strategy),
                'Satisfação Média': avg_satisfaction,
                'Tipo': 'Arrendamento'
            })
    
    # Analisar satisfação para estratégias de compra
    for strategy in buy_strategy_map.keys():
        strategy_df = df[df['estrategia-compra'].apply(
            lambda x: isinstance(x, list) and strategy in x
        )]
        
        avg_satisfaction = strategy_df['satisfaction_numeric'].mean()
        if not pd.isna(avg_satisfaction):
            satisfaction_by_strategy.append({
                'Estratégia': buy_strategy_map.get(strategy, strategy),
                'Satisfação Média': avg_satisfaction,
                'Tipo': 'Compra'
            })
    
    satisfaction_df = pd.DataFrame(satisfaction_by_strategy)
    
    if not satisfaction_df.empty:
        # Criar gráfico comparativo de satisfação por estratégia e tipo
        fig = px.bar(
            satisfaction_df,
            x='Estratégia',
            y='Satisfação Média',
            color='Tipo',
            barmode='group',
            title='Nível de Satisfação Médio por Estratégia de Habitação',
            color_discrete_map={
                'Arrendamento': PRIMARY_COLORS[0],
                'Compra': PRIMARY_COLORS[1]
            }
        )
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            xaxis={'categoryorder':'total descending'},
            yaxis=dict(
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['Muito Insatisfeito', 'Insatisfeito', 'Indiferente', 'Satisfeito', 'Muito Satisfeito']
            )
        )
        st.plotly_chart(fig)
        
        st.markdown("""
        Este gráfico mostra a relação entre as estratégias utilizadas para encontrar habitação e o nível 
        médio de satisfação dos residentes. A comparação entre estratégias de arrendamento e compra revela 
        insights importantes sobre a eficácia de diferentes abordagens no mercado imobiliário português.
        """)