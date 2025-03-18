# tab2_geographic_analysis.py
import streamlit as st
import plotly.express as px
import pandas as pd
from config import *

def show_geographic_analysis_tab(df):
    """
    Este separador fornece uma análise detalhada da distribuição geográfica da habitação em Portugal,
    revelando padrões regionais em propriedade, arrendamento, custos habitacionais e sobrecarga financeira.
    
    As visualizações combinam mapas, gráficos de barras e gráficos de caixa para destacar as variações regionais
    nos padrões habitacionais e ajudar a identificar regiões com desafios específicos de acessibilidade.
    
    Parameters:
    df (DataFrame): The processed housing data
    """
    st.header("Análise da Distribuição Geográfica")
    
    # Introdução com estilo melhorado
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
    <h4 style="color: #2e7d32; margin-top: 0;">Visão Geral</h4>
    <p>Esta secção apresenta uma análise geográfica das situações habitacionais em Portugal, 
    mostrando como os padrões habitacionais variam entre diferentes regiões do país.</p>
    <ul>
      <li><strong>Tendências Principais:</strong> Existem variações regionais significativas nas taxas de propriedade, arrendamento e custos habitacionais</li>
      <li><strong>Variação Regional:</strong> Distritos urbanos mostram padrões habitacionais distintos em comparação com áreas rurais</li>
      <li><strong>Sobrecarga Habitacional:</strong> A acessibilidade habitacional varia consideravelmente entre diferentes regiões de Portugal</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        total_districts = df['distrito'].nunique()
        st.metric("Total de Distritos", total_districts)
    with col2:
        most_expensive_district = df[df['housing_situation'] == 'Arrendamento'].groupby('distrito')['valor-mensal-renda'].mean().idxmax()
        st.metric("Distrito Mais Caro (Arrendamento)", most_expensive_district.capitalize())
    with col3:
        highest_ownership = df.groupby('distrito')['housing_situation'].apply(lambda x: (x == 'Casa Própria').mean() * 100).idxmax()
        st.metric("Taxa Mais Alta de Propriedade", highest_ownership.capitalize())
    
    # Create map placeholders
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Districts distribution with improved aesthetics
        st.subheader("Distribuição Habitacional por Distrito")
        district_counts = df.groupby(['distrito', 'housing_situation']).size().reset_index(name='count')
        fig = px.bar(
            district_counts,
            x='distrito',
            y='count',
            color='housing_situation',
            color_discrete_map=HOUSING_COLORS,
            title='Situações Habitacionais por Distrito',
            labels={'distrito': 'Distrito', 'count': 'Contagem', 'housing_situation': 'Situação Habitacional'}
        )
        fig.update_layout(
            xaxis_title="Distrito",
            yaxis_title="Número de Residentes",
            legend_title="Situação Habitacional",
            height=500,
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig)
        
        st.markdown("""
        **Principais Insights:**
        - O gráfico mostra a distribuição das situações habitacionais pelos distritos de Portugal
        - Áreas com barras mais altas indicam mais participantes do inquérito dessas regiões
        - A divisão por cores revela padrões de propriedade vs. arrendamento em cada distrito
        """)
        
    with col2:
        st.subheader("Principais Distritos")
        top_districts = df['distrito'].value_counts().reset_index()
        top_districts.columns = ['Distrito', 'Contagem']
        top_districts['Distrito'] = top_districts['Distrito'].str.capitalize()
        top_districts = top_districts.head(5)
        
        st.dataframe(top_districts, hide_index=True)
        
        # Add percentage calculation
        top_districts['Percentagem'] = (top_districts['Contagem'] / top_districts['Contagem'].sum() * 100).round(1).astype(str) + '%'
        
        # Create a pie chart for top districts
        fig = px.pie(
            top_districts,
            values='Contagem',
            names='Distrito',
            title='Distribuição dos 5 Principais Distritos',
            color_discrete_sequence=PRIMARY_COLORS
        )
        fig.update_layout(
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)
    
    # Housing situation by district
    st.subheader("Distribuição das Situações Habitacionais")
    
    # Calculate percentages
    district_percentages = df.groupby('distrito')['housing_situation'].value_counts(normalize=True).mul(100).round(1).reset_index(name='percentage')
    district_percentages = district_percentages.rename(columns={'level_1': 'housing_situation'})
    district_percentages['distrito'] = district_percentages['distrito'].str.capitalize()
    
    fig = px.bar(
        district_percentages,
        x='distrito',
        y='percentage',
        color='housing_situation',
        title='Percentagem de Situações Habitacionais por Distrito',
        labels={'distrito': 'Distrito', 'percentage': 'Percentagem (%)', 'housing_situation': 'Situação Habitacional'},
        color_discrete_map=HOUSING_COLORS
    )
    fig.update_layout(
        xaxis_title="Distrito",
        yaxis_title="Percentagem de Residentes",
        legend_title="Situação Habitacional",
        height=500,
        plot_bgcolor=BACKGROUND_COLORS[0],
        paper_bgcolor=BACKGROUND_COLORS[3],
        font_color=TEXT_COLORS[2],
        title_font_color=TEXT_COLORS[0]
    )
    st.plotly_chart(fig)
    
    st.markdown("""
    **O Que Isto Mostra:**
    - Este gráfico normaliza os dados para mostrar a distribuição percentual das situações habitacionais em cada distrito
    - Distritos com taxas mais elevadas de propriedade podem indicar mercados habitacionais mais acessíveis ou diferentes preferências culturais
    - Áreas com altas percentagens de arrendamento podem sugerir populações mais transitórias ou mercados habitacionais mais caros
    """)
    
    # Housing costs by region
    st.subheader("Custos Habitacionais por Região")
    
    region_selector = st.selectbox(
        "Selecione uma Região para Ver os Custos Habitacionais",
        options=["Todas"] + sorted(pd.Series(df['distrito'].unique()).str.capitalize().tolist())
    )
    
    if region_selector != "Todas":
        region_df = df[df['distrito'].str.capitalize() == region_selector]
        st.markdown(f"A analisar custos habitacionais para o distrito de **{region_selector}**")
    else:
        region_df = df
        st.markdown("A analisar custos habitacionais em **todos os distritos**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rent costs by district
        rent_data = region_df[region_df['housing_situation'] == 'Arrendamento']
        if not rent_data.empty and 'valor-mensal-renda' in rent_data.columns:
            # Calculate average rent
            avg_rent = rent_data['valor-mensal-renda'].mean().round(2)
            st.metric("Renda Mensal Média", f"€{avg_rent:.2f}")
            
            fig = px.box(
                rent_data,
                x='distrito',
                y='valor-mensal-renda',
                color='distrito',
                title='Renda Mensal por Distrito',
                labels={'valor-mensal-renda': 'Renda Mensal (€)', 'distrito': 'Distrito'},
                color_discrete_sequence=PRIMARY_COLORS
            )
            fig.update_layout(
                xaxis_title="Distrito",
                yaxis_title="Renda Mensal (€)",
                height=400,
                plot_bgcolor=BACKGROUND_COLORS[0],
                paper_bgcolor=BACKGROUND_COLORS[3],
                font_color=TEXT_COLORS[2],
                title_font_color=TEXT_COLORS[0]
            )
            st.plotly_chart(fig)
            
            st.markdown("""
            **Insights do Mercado de Arrendamento:**
            - O gráfico de caixa mostra a distribuição das rendas mensais pelos distritos
            - A caixa representa os 50% centrais dos valores de renda, com a linha a mostrar a mediana
            - Outliers (pontos fora dos bigodes) podem representar propriedades de luxo ou potencialmente anomalias nos dados
            """)
        else:
            st.write("Não há dados de arrendamento disponíveis para o filtro selecionado.")
    
    with col2:
        # Purchase costs by district
        purchase_data = region_df[region_df['housing_situation'] == 'Casa Própria']
        if not purchase_data.empty and 'valor-compra' in purchase_data.columns:
            # Calculate average purchase price
            avg_purchase = purchase_data['valor-compra'].mean().round(2)
            st.metric("Preço Médio de Compra", f"€{avg_purchase:.2f}")
            
            fig = px.box(
                purchase_data,
                x='distrito',
                y='valor-compra',
                color='distrito',
                title='Preço de Compra de Imóveis por Distrito',
                labels={'valor-compra': 'Preço de Compra (€)', 'distrito': 'Distrito'},
                color_discrete_sequence=SECONDARY_COLORS
            )
            fig.update_layout(
                xaxis_title="Distrito",
                yaxis_title="Preço de Compra (€)",
                height=400,
                plot_bgcolor=BACKGROUND_COLORS[0],
                paper_bgcolor=BACKGROUND_COLORS[3],
                font_color=TEXT_COLORS[2],
                title_font_color=TEXT_COLORS[0]
            )
            st.plotly_chart(fig)
            
            st.markdown("""
            **Insights do Mercado Imobiliário:**
            - O gráfico de caixa mostra a distribuição dos preços de compra de imóveis pelos distritos
            - Caixas mais largas indicam maior variabilidade nos preços dos imóveis dentro desse distrito
            - A posição da caixa mostra o nível geral de preços do mercado habitacional desse distrito
            """)
        else:
            st.write("Não há dados de compra disponíveis para o filtro selecionado.")
    
    # Add rent-to-income ratio analysis
    st.subheader("Análise de Acessibilidade")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rent burden by district
        rent_burden_data = df[df['housing_situation'] == 'Arrendamento'].dropna(subset=['rent_burden', 'distrito'])
        rent_burden_data['distrito'] = rent_burden_data['distrito'].str.capitalize()
        if not rent_burden_data.empty:
            burden_counts = rent_burden_data.groupby(['distrito', 'rent_burden']).size().reset_index(name='count')
            
            fig = px.bar(
                burden_counts,
                x='distrito',
                y='count',
                color='rent_burden',
                title='Sobrecarga de Renda por Distrito',
                labels={'distrito': 'Distrito', 'count': 'Contagem', 'rent_burden': 'Sobrecarga de Renda'},
                category_orders={
                    'rent_burden': ['≤30% (Affordable)', '31-50% (Moderate)', '51-80% (High)', '>80% (Very High)', 'Unknown']
                },
                color_discrete_map=RENT_BURDEN_COLORS
            )
            fig.update_layout(
                xaxis_title="Distrito",
                yaxis_title="Número de Residentes",
                legend_title="Sobrecarga de Renda",
                height=500,
                plot_bgcolor=BACKGROUND_COLORS[0],
                paper_bgcolor=BACKGROUND_COLORS[3],
                font_color=TEXT_COLORS[2],
                title_font_color=TEXT_COLORS[0]
            )
            st.plotly_chart(fig)
            
            st.markdown("""
            **Explicação da Sobrecarga de Renda:**
            - A sobrecarga de renda mostra que percentagem do rendimento os residentes gastam em habitação
            - Áreas com elevadas proporções de residentes a gastar >30% do rendimento em renda podem indicar problemas de acessibilidade
            - O limiar geralmente aceite para habitação acessível é gastar não mais do que 30% do rendimento em habitação
            """)
        else:
            st.write("Não há dados de sobrecarga de renda disponíveis para análise.")
    
    with col2:
        # Property age by district
        if 'ano-compra' in df.columns:
            purchase_year_data = df[df['housing_situation'] == 'Casa Própria'].dropna(subset=['ano-compra', 'distrito'])
            purchase_year_data['distrito'] = purchase_year_data['distrito'].str.capitalize()
            if not purchase_year_data.empty:
                # Calculate property age
                current_year = 2025  # Current year of analysis
                purchase_year_data['property_age'] = current_year - purchase_year_data['ano-compra']
                
                fig = px.box(
                    purchase_year_data,
                    x='distrito',
                    y='property_age',
                    color='distrito',
                    title='Idade dos Imóveis por Distrito',
                    labels={'property_age': 'Idade do Imóvel (Anos)', 'distrito': 'Distrito'},
                    color_discrete_sequence=ACCENT_COLORS
                )
                fig.update_layout(
                    xaxis_title="Distrito",
                    yaxis_title="Idade do Imóvel (Anos)",
                    height=500,
                    plot_bgcolor=BACKGROUND_COLORS[0],
                    paper_bgcolor=BACKGROUND_COLORS[3],
                    font_color=TEXT_COLORS[2],
                    title_font_color=TEXT_COLORS[0]
                )
                st.plotly_chart(fig)
                
                st.markdown("""
                **Análise da Idade dos Imóveis:**
                - Este gráfico mostra a distribuição da idade dos imóveis próprios pelos distritos
                - Imóveis mais novos (valores mais baixos) podem indicar desenvolvimento recente ou maior rotatividade
                - Parques habitacionais mais antigos podem sugerir bairros estabelecidos ou construção nova limitada
                """)
            else:
                st.write("Não há dados sobre a idade dos imóveis disponíveis para análise.")
        else:
            st.write("Dados sobre a idade dos imóveis não disponíveis no conjunto de dados.")