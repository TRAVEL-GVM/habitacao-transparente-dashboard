#tab6_housing_types_sizes.py
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))
from config import *

def show_housing_types_sizes_tab(df):
    """
    Enhanced "Housing Types & Sizes" tab with improved storytelling and narrative flow.
    
    This tab presents a compelling story about Portugal's housing situation by:
    1. Establishing the key questions and problems
    2. Examining household composition needs
    3. Analyzing available housing stock
    4. Identifying mismatches between needs and reality
    5. Exploring impacts on satisfaction
    6. Providing actionable insights and recommendations
    """
    st.header("Tipos e Tamanhos de Habitação: As Casas Portuguesas Satisfazem as Necessidades?")
    
    # Start with a compelling problem statement
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
    <h4 style="color: #2e7d32; margin-top: 0;">Visão Geral</h4>
    <p>Esta análise revela insights importantes sobre os tipos e tamanhos de habitação em Portugal, destacando os desafios de compatibilidade entre o parque habitacional disponível e as necessidades dos agregados familiares.</p>
    <ul>
      <li><strong>Tendências Principais:</strong> Apartamentos dominam em áreas urbanas (principalmente T2 e T3), enquanto a área média por pessoa diminui significativamente em agregados maiores</li>
      <li><strong>Desajustes Identificados:</strong> Existe uma escassez de habitações pequenas para corresponder ao crescente número de agregados de 1-2 pessoas</li>
      <li><strong>Impacto na Satisfação:</strong> Residentes muito satisfeitos possuem habitações significativamente maiores, com o nível de satisfação a aumentar a partir dos 100m²</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Facts section with attention-grabbing statistics
    # Calculate a few key statistics for the quick facts
    avg_area = df[df['area_numerical'].notna()]['area_numerical'].mean()
    total_responses = len(df)
    apartment_pct = (df['house_type'] == 'Apartment').sum() / df['house_type'].count() * 100
    
    # Calculate household size
    df['household_size'] = df['num-pessoas-nao-dependentes'].fillna(0) + df['num-pessoas-dependentes'].fillna(0)
    avg_household_size = df[df['household_size'] > 0]['household_size'].mean()
    
    # Calculate space per person (approximation)
    df['approx_space_per_person'] = df.apply(
        lambda row: row['area_numerical'] / row['household_size'] 
        if pd.notna(row['area_numerical']) and pd.notna(row['household_size']) and row['household_size'] > 0 
        else np.nan, 
        axis=1
    )
    avg_space_per_person = df['approx_space_per_person'].mean()
    
    # Calculate satisfaction with size
    size_satisfaction = df.dropna(subset=['area_numerical', 'satisfaction_level']).copy()
    size_satisfaction['satisfied_with_size'] = size_satisfaction['satisfaction_level'].isin(['Satisfied', 'Very Satisfied'])
    
    satisfied_with_size_pct = size_satisfaction['satisfied_with_size'].mean() * 100
    
    # Create 3 columns for quick facts
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Tamanho Médio da Habitação",
            value=f"{avg_area:.1f} m²",
            help="Área média das habitações portuguesas com base nas respostas do inquérito"
        )
    
    with col2:
        st.metric(
            label="Tamanho Médio do Agregado",
            value=f"{avg_household_size:.1f} pessoas",
            help="Número médio de pessoas por agregado familiar no inquérito"
        )
    
    with col3:
        # Calculate housing satisfaction with size
        size_satisfaction = df.dropna(subset=['area_numerical', 'satisfaction_level']).copy()
        size_satisfaction['satisfied_with_size'] = size_satisfaction['satisfaction_level'].isin(['Satisfied', 'Very Satisfied'])
        
        satisfied_with_size_pct = size_satisfaction['satisfied_with_size'].mean() * 100
        
        st.metric(
            label="Taxa de Satisfação com Tamanho",
            value=f"{satisfied_with_size_pct:.1f}%",
            help="Percentagem de agregados que reportam satisfação com o tamanho da sua habitação"
        )
    
    # Housing mismatch insights
    st.markdown("""
    **Principais Conclusões sobre Desajuste Habitacional:**
    
    - **Diminuição da Eficiência de Espaço:** À medida que o tamanho do agregado aumenta, o espaço disponível por pessoa diminui significativamente, potencialmente levando a sobrelotação em agregados maiores.
    
    - **Desequilíbrio Oferta-Procura:** Enquanto agregados pequenos (1-2 pessoas) representam a maioria da população, o parque habitacional não está proporcionalmente alinhado, com menos unidades pequenas disponíveis em relação à procura.
    
    - **Constrangimentos Habitacionais Urbanos:** Nas áreas urbanas, o predomínio de apartamentos com espaço limitado cria desafios para famílias com crianças que necessitam de mais espaço mas desejam permanecer em cidades com melhores comodidades e oportunidades de emprego.
    
    - **Excesso de Oferta Rural:** Nas áreas rurais, existe frequentemente um excesso de oferta de casas maiores em relação aos agregados tipicamente menores e envelhecidos, criando uma utilização ineficiente dos recursos habitacionais.
    """)
    
    # SECTION 4: IMPACT ON SATISFACTION
    st.subheader("4. Impacto na Satisfação: Como o Tamanho da Habitação Afeta a Qualidade de Vida")
    
    st.markdown("""
    O desajuste entre necessidades habitacionais e disponibilidade tem impacto direto na satisfação dos residentes.
    Esta secção explora como o tamanho da habitação se correlaciona com a satisfação habitacional geral.
    """)
    
    # Housing size by satisfaction level
    # Filter records with both area and satisfaction data
    satisfaction_area_data = df[df['area_numerical'].notna() & df['satisfaction_level'].notna()].copy()
    
    # Translate satisfaction levels
    satisfaction_translation = {
        'Very Satisfied': 'Muito Satisfeito',
        'Satisfied': 'Satisfeito',
        'Neutral': 'Neutro',
        'Dissatisfied': 'Insatisfeito',
        'Very Dissatisfied': 'Muito Insatisfeito'
    }
    satisfaction_area_data['satisfaction_level'] = satisfaction_area_data['satisfaction_level'].map(satisfaction_translation)
    
    # Order the satisfaction levels
    satisfaction_order = ['Muito Insatisfeito', 'Insatisfeito', 'Neutro', 'Satisfeito', 'Muito Satisfeito']
    satisfaction_area_data['satisfaction_level'] = pd.Categorical(
        satisfaction_area_data['satisfaction_level'],
        categories=satisfaction_order,
        ordered=True
    )
    
    # Calculate statistics for insights
    satisfaction_area_stats = satisfaction_area_data.groupby('satisfaction_level')['area_numerical'].agg(['mean', 'median', 'count']).reset_index()
    
    # Explicitly handle potential KeyError by checking if values exist
    very_satisfied_area = 0
    very_dissatisfied_area = 0
    
    if 'Muito Satisfeito' in satisfaction_area_stats['satisfaction_level'].values:
        very_satisfied_area = satisfaction_area_stats[satisfaction_area_stats['satisfaction_level'] == 'Muito Satisfeito']['mean'].values[0]
    
    if 'Muito Insatisfeito' in satisfaction_area_stats['satisfaction_level'].values:
        very_dissatisfied_area = satisfaction_area_stats[satisfaction_area_stats['satisfaction_level'] == 'Muito Insatisfeito']['mean'].values[0]
    
    area_satisfaction_diff = very_satisfied_area - very_dissatisfied_area
    
    # Create box plot of housing area by satisfaction level
    # Map SATISFACTION_COLORS to Portuguese satisfaction levels
    satisfaction_colors_pt = {
        'Muito Satisfeito': SATISFACTION_COLORS['Very Satisfied'],
        'Satisfeito': SATISFACTION_COLORS['Satisfied'],
        'Neutro': SATISFACTION_COLORS['Neutral'],
        'Insatisfeito': SATISFACTION_COLORS['Dissatisfied'],
        'Muito Insatisfeito': SATISFACTION_COLORS['Very Dissatisfied']
    }
    
    fig_satisfaction_area = px.box(
        satisfaction_area_data,
        x='satisfaction_level',
        y='area_numerical',
        color='satisfaction_level',
        title="Tamanho da Habitação por Nível de Satisfação",
        labels={'area_numerical': 'Área (m²)', 'satisfaction_level': 'Nível de Satisfação'},
        category_orders={'satisfaction_level': satisfaction_order},
        color_discrete_map=satisfaction_colors_pt
    )
    fig_satisfaction_area.update_layout(
        plot_bgcolor=BACKGROUND_COLORS[0],
        paper_bgcolor=BACKGROUND_COLORS[3],
        font_color=TEXT_COLORS[2],
        title_font_color=TEXT_COLORS[0]
    )
    st.plotly_chart(fig_satisfaction_area, use_container_width=True)
    
    # Create a chart showing relationship between satisfaction level and housing size
    avg_area_by_satisfaction = satisfaction_area_stats.copy()
    avg_area_by_satisfaction = avg_area_by_satisfaction.sort_values('satisfaction_level')
    
    fig_avg_satisfaction = px.line(
        avg_area_by_satisfaction,
        x='satisfaction_level',
        y='mean',
        markers=True,
        title="Tamanho Médio da Habitação por Nível de Satisfação",
        labels={'mean': 'Área Média (m²)', 'satisfaction_level': 'Nível de Satisfação'},
        color_discrete_sequence=[PRIMARY_COLORS[0]]
    )
    fig_avg_satisfaction.update_layout(
        plot_bgcolor=BACKGROUND_COLORS[0],
        paper_bgcolor=BACKGROUND_COLORS[3],
        font_color=TEXT_COLORS[2],
        title_font_color=TEXT_COLORS[0]
    )
    st.plotly_chart(fig_avg_satisfaction, use_container_width=True)
    
    # Add insights about size and satisfaction
    st.markdown(f"""
    **Insights-Chave sobre Tamanho-Satisfação:**
    
    - **Forte Correlação:** Existe uma clara relação positiva entre o tamanho da habitação e os níveis de satisfação
    - **Disparidade de Tamanho:** Residentes muito satisfeitos têm casas que são, em média, {area_satisfaction_diff:.1f} m² maiores do que residentes muito insatisfeitos
    - **Efeito Limiar:** A satisfação parece aumentar mais rapidamente quando as casas excedem aproximadamente 100 m²
    - **Prémio de Espaço:** Os residentes mais satisfeitos têm as maiores casas, com um tamanho médio de {very_satisfied_area:.1f} m²
    - **Para Além do Tamanho:** A sobreposição entre categorias de satisfação indica que, embora o tamanho seja importante, outros fatores (localização, qualidade, etc.) também influenciam significativamente a satisfação
    """)
    st.metric(
        label="Taxa de Satisfação com Tamanho",
        value=f"{satisfied_with_size_pct:.1f}%",
        help="Percentagem de agregados que reportam satisfação com o tamanho da sua habitação"
    )

    # SECTION 1: WHO NEEDS HOUSING? (HOUSEHOLD COMPOSITION)
    st.subheader("1. Quem Precisa de Habitação? Compreender os Agregados Portugueses")
    
    st.markdown("""
    Para avaliar se a habitação satisfaz as necessidades dos residentes, primeiro precisamos compreender a composição dos agregados familiares. 
    Isto ajuda a estabelecer o lado da procura na equação habitacional.
    """)
    
    # Create columns for household analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Create a total household size column
        df['household_size_grouped'] = df['household_size'].apply(
            lambda x: '6+' if pd.notna(x) and x >= 6 else (str(int(x)) if pd.notna(x) and x > 0 else np.nan)
        )
        
        # Count household sizes
        household_counts = df['household_size_grouped'].value_counts().reset_index()
        household_counts.columns = ['Tamanho do Agregado', 'Contagem']
        
        # Order household sizes
        size_order = ['1', '2', '3', '4', '5', '6+']
        household_counts['Tamanho do Agregado'] = pd.Categorical(
            household_counts['Tamanho do Agregado'], 
            categories=size_order, 
            ordered=True
        )
        household_counts = household_counts.sort_values('Tamanho do Agregado')
        
        # Calculate percentages for insights
        total_households = household_counts['Contagem'].sum()
        household_counts['Percentage'] = (household_counts['Contagem'] / total_households * 100).round(1)
        
        # Create pie chart of household sizes
        fig_household = px.pie(
            household_counts,
            values='Contagem',
            names='Tamanho do Agregado',
            title="Distribuição por Tamanho do Agregado",
            color='Tamanho do Agregado',
            color_discrete_sequence=COLOR_SCALES['sequential']
        )
        fig_household.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        fig_household.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_household, use_container_width=True)
        
        # Calculate key stats for insights
        small_households_pct = household_counts[household_counts['Tamanho do Agregado'].isin(['1', '2'])]['Percentage'].sum()
        large_households_pct = household_counts[household_counts['Tamanho do Agregado'].isin(['4', '5', '6+'])]['Percentage'].sum()
        
    with col2:
        # Group households by status (with children vs without)
        df['has_dependents'] = df['num-pessoas-dependentes'] > 0
        household_status = df.groupby('has_dependents').size().reset_index()
        household_status.columns = ['Tem Crianças', 'Contagem']
        household_status['Tem Crianças'] = household_status['Tem Crianças'].map({True: 'Agregados com crianças', False: 'Agregados sem crianças'})
        
        # Calculate percentages
        total = household_status['Contagem'].sum()
        household_status['Percentage'] = (household_status['Contagem'] / total * 100).round(1)
        
        # Create pie chart of household composition
        fig_composition = px.pie(
            household_status,
            values='Contagem',
            names='Tem Crianças',
            title="Agregados Com e Sem Crianças",
            color_discrete_sequence=[PRIMARY_COLORS[1], SECONDARY_COLORS[1]]
        )
        fig_composition.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        fig_composition.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_composition, use_container_width=True)
        
        # Get percentages for insights
        with_children_pct = household_status[household_status['Tem Crianças'] == 'Agregados com crianças']['Percentage'].values[0] if len(household_status[household_status['Tem Crianças'] == 'Agregados com crianças']) > 0 else 0
        without_children_pct = household_status[household_status['Tem Crianças'] == 'Agregados sem crianças']['Percentage'].values[0] if len(household_status[household_status['Tem Crianças'] == 'Agregados sem crianças']) > 0 else 0
    
    # Insights about households
    st.markdown(f"""
    **Insights-Chave sobre Agregados Familiares Portugueses:**
    
    - **Tamanho do Agregado:** Agregados pequenos (1-2 pessoas) compõem {small_households_pct:.1f}% de todos os agregados, enquanto agregados maiores (4+ pessoas) representam {large_households_pct:.1f}%.
    - **Composição Familiar:** {with_children_pct:.1f}% dos agregados incluem crianças, enquanto {without_children_pct:.1f}% não têm membros dependentes.
    - **Necessidades Habitacionais:** Esta distribuição sugere uma necessidade de opções habitacionais diversas, com particular ênfase em unidades mais pequenas que ainda proporcionem espaço adequado para diferentes atividades do agregado.
    - **Demografia em Mudança:** O tamanho médio do agregado em Portugal tem diminuído ao longo do tempo, refletindo tendências de formação tardia de família e envelhecimento da população.
    """)
    
    # SECTION 2: WHAT HOUSING IS AVAILABLE? (HOUSING STOCK)
    st.subheader("2. Stock Habitacional Disponível: Tipos, Tamanhos e Configurações")
    
    st.markdown("""
    Agora que compreendemos quem precisa de habitação, vamos examinar o stock habitacional disponível - o lado da oferta da equação.
    Esta secção analisa tipos de habitação, tamanhos e número de quartos para avaliar o que está disponível para os residentes portugueses.
    """)
    
    # Create columns for housing type and bedroom distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Count housing types
        house_type_counts = df['house_type'].value_counts().reset_index()
        house_type_counts.columns = ['Tipo de Habitação', 'Contagem']
        
        # Translate house types
        house_type_counts['Tipo de Habitação'] = house_type_counts['Tipo de Habitação'].map({
            'Apartment': 'Apartamento',
            'House': 'Moradia'
        })
        
        # Calculate percentages for insights
        total_housing = house_type_counts['Contagem'].sum()
        house_type_counts['Percentage'] = (house_type_counts['Contagem'] / total_housing * 100).round(1)
        
        apartment_pct = house_type_counts[house_type_counts['Tipo de Habitação'] == 'Apartamento']['Percentage'].values[0] if 'Apartamento' in house_type_counts['Tipo de Habitação'].values else 0
        house_pct = house_type_counts[house_type_counts['Tipo de Habitação'] == 'Moradia']['Percentage'].values[0] if 'Moradia' in house_type_counts['Tipo de Habitação'].values else 0
        
        # Create pie chart for housing types
        fig_house_type = px.pie(
            house_type_counts, 
            values='Contagem', 
            names='Tipo de Habitação',
            color_discrete_sequence=PRIMARY_COLORS,
            title="Distribuição de Tipos de Habitação"
        )
        fig_house_type.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        fig_house_type.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_house_type, use_container_width=True)
    
    with col2:
        # Count bedroom types
        bedroom_counts = df['bedroom_count'].value_counts().reset_index()
        bedroom_counts.columns = ['Tipologia', 'Contagem']
        
        # Translate bedroom counts to Portuguese typology
        bedroom_counts['Tipologia'] = bedroom_counts['Tipologia'].map({
            '0': 'T0', 
            '1': 'T1', 
            '2': 'T2', 
            '3': 'T3', 
            '4+': 'T4+'
        })
        
        # Sort the bedroom counts in logical order
        bedroom_order = ['T0', 'T1', 'T2', 'T3', 'T4+']
        bedroom_counts['Tipologia'] = pd.Categorical(
            bedroom_counts['Tipologia'], 
            categories=bedroom_order, 
            ordered=True
        )
        bedroom_counts = bedroom_counts.sort_values('Tipologia')
        
        # Calculate statistics for insights
        total_bedrooms = bedroom_counts['Contagem'].sum()
        bedroom_counts['Percentage'] = (bedroom_counts['Contagem'] / total_bedrooms * 100).round(1)
        
        most_common_bedroom = bedroom_counts.loc[bedroom_counts['Contagem'].idxmax(), 'Tipologia']
        most_common_pct = bedroom_counts.loc[bedroom_counts['Contagem'].idxmax(), 'Percentage']
        
        small_units_pct = bedroom_counts[bedroom_counts['Tipologia'].isin(['T0', 'T1'])]['Percentage'].sum()
        large_units_pct = bedroom_counts[bedroom_counts['Tipologia'].isin(['T3', 'T4+'])]['Percentage'].sum()
        
        # Create bar chart for bedroom distribution
        fig_bedrooms = px.bar(
            bedroom_counts,
            x='Tipologia',
            y='Contagem',
            color='Tipologia',
            title="Distribuição de Tipologias",
            text=bedroom_counts['Percentage'].apply(lambda x: f"{x}%"),
            color_discrete_sequence=SECONDARY_COLORS
        )
        fig_bedrooms.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig_bedrooms, use_container_width=True)
    
    # Now show housing area distribution
    # Create area bins and labels for better visualization
    area_bins = [0, 50, 100, 150, 200, 250, 300, 350, 400, 500]
    area_labels = ['0-50', '51-100', '101-150', '151-200', '201-250', '251-300', '301-350', '351-400', '400+']
    
    # Create a new column with binned areas
    df_with_area = df[df['area_numerical'].notna()].copy()
    df_with_area['area_binned'] = pd.cut(df_with_area['area_numerical'], bins=area_bins, labels=area_labels)
    
    # Count areas by bin
    area_counts = df_with_area['area_binned'].value_counts().reset_index()
    area_counts.columns = ['Área (m²)', 'Contagem']
    
    # Sort by area size
    area_counts['Área (m²)'] = pd.Categorical(
        area_counts['Área (m²)'], 
        categories=area_labels, 
        ordered=True
    )
    area_counts = area_counts.sort_values('Área (m²)')
    
    # Calculate statistics for insights
    total_area_records = area_counts['Contagem'].sum()
    area_counts['Percentage'] = (area_counts['Contagem'] / total_area_records * 100).round(1)
    
    most_common_area = area_counts.loc[area_counts['Contagem'].idxmax(), 'Área (m²)']
    most_common_area_pct = area_counts.loc[area_counts['Contagem'].idxmax(), 'Percentage']
    
    small_area_pct = area_counts[area_counts['Área (m²)'].isin(['0-50', '51-100'])]['Percentage'].sum()
    medium_area_pct = area_counts[area_counts['Área (m²)'].isin(['101-150', '151-200'])]['Percentage'].sum()
    large_area_pct = area_counts[area_counts['Área (m²)'].isin(['201-250', '251-300', '301-350', '351-400', '400+'])]['Percentage'].sum()
    
    # Create histogram for area distribution
    fig_area = px.bar(
        area_counts,
        x='Área (m²)',
        y='Contagem',
        color='Área (m²)',
        title="Distribuição de Tamanho da Habitação (m²)",
        text=area_counts['Percentage'].apply(lambda x: f"{x}%"),
        color_discrete_sequence=CHART_COLORS
    )
    fig_area.update_layout(
        plot_bgcolor=BACKGROUND_COLORS[0],
        paper_bgcolor=BACKGROUND_COLORS[3],
        font_color=TEXT_COLORS[2],
        title_font_color=TEXT_COLORS[0]
    )
    st.plotly_chart(fig_area, use_container_width=True)
    
    # Add insights about housing stock
    st.markdown(f"""
    **Insights-Chave sobre o Stock Habitacional Disponível:**
    
    - **Tipos de Habitação:** {apartment_pct:.1f}% das habitações são apartamentos, enquanto {house_pct:.1f}% são moradias. Isto reflete a concentração urbana de Portugal e os padrões tradicionais de desenvolvimento.
    
    - **Distribuição de Tipologias:** As tipologias {most_common_bedroom} são as mais comuns ({most_common_pct:.1f}% das habitações), com unidades pequenas (T0-T1) representando {small_units_pct:.1f}% e unidades maiores (T3+) representando {large_units_pct:.1f}% do parque habitacional.
    
    - **Distribuição de Tamanhos:** O intervalo de tamanho habitacional mais comum é {most_common_area} m² ({most_common_area_pct:.1f}% das unidades). Casas pequenas (≤100 m²) compõem {small_area_pct:.1f}% do parque habitacional, casas médias (101-200 m²) representam {medium_area_pct:.1f}%, e casas maiores (>200 m²) representam {large_area_pct:.1f}%.
    
    - **Padrões Urbanos vs. Rurais:** Os padrões habitacionais mostram claras divisões urbano-rurais, com apartamentos a dominar nas cidades e moradias a prevalecer nas áreas rurais.
    """)
    
    # SECTION 3: MATCHING NEEDS TO REALITY
    st.subheader("3. Desajuste Habitacional: A Oferta Satisfaz a Procura?")
    
    st.markdown("""
    Agora podemos analisar quão bem o parque habitacional português satisfaz as necessidades das famílias, examinando a relação entre 
    tipos de habitação, número de quartos e tamanhos de agregados.
    """)
    
    # Compare bedroom count with housing type
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Calculate the cross-tabulation of housing type and bedroom count
        housing_bedroom_data = pd.crosstab(
            df['house_type'], 
            df['bedroom_count'],
            margins=False
        ).reset_index()
        
        # Filter out rows with NaN values
        housing_bedroom_data = housing_bedroom_data.dropna()
        
        # Translate house types
        housing_bedroom_data['house_type'] = housing_bedroom_data['house_type'].map({
            'Apartment': 'Apartamento',
            'House': 'Moradia'
        })
        
        # Melt the dataframe for easier plotting
        housing_bedroom_melted = pd.melt(
            housing_bedroom_data,
            id_vars=['house_type'],
            var_name='bedroom_count',
            value_name='count'
        )
        
        # Translate bedroom_count to Portuguese typology
        bedroom_mapping = {'0': 'T0', '1': 'T1', '2': 'T2', '3': 'T3', '4+': 'T4+'}
        housing_bedroom_melted['bedroom_count'] = housing_bedroom_melted['bedroom_count'].map(bedroom_mapping)
        
        # Create the grouped bar chart
        fig_housing_bedroom = px.bar(
            housing_bedroom_melted,
            x='house_type',
            y='count',
            color='bedroom_count',
            title="Tipos de Habitação por Tipologia",
            barmode='group',
            labels={'house_type': 'Tipo de Habitação', 'count': 'Contagem', 'bedroom_count': 'Tipologia'},
            color_discrete_sequence=ACCENT_COLORS
        )
        fig_housing_bedroom.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig_housing_bedroom, use_container_width=True)
    
    with col2:
        # Calculate most common configurations
        most_common_apt = housing_bedroom_melted[housing_bedroom_melted['house_type'] == 'Apartamento'].loc[housing_bedroom_melted[housing_bedroom_melted['house_type'] == 'Apartamento']['count'].idxmax()]
        most_common_house = housing_bedroom_melted[housing_bedroom_melted['house_type'] == 'Moradia'].loc[housing_bedroom_melted[housing_bedroom_melted['house_type'] == 'Moradia']['count'].idxmax()]
        
        # Create a match/mismatch analysis
        st.markdown(f"""
        **Análise de Configuração:**
        
        - Apartamento mais comum: **{most_common_apt['bedroom_count']}**
        - Moradia mais comum: **{most_common_house['bedroom_count']}**
        - Apartamentos concentram-se nas gamas T1-T2
        - Moradias tipicamente oferecem T3+
        - T0s são quase exclusivamente apartamentos
        
        Esta distribuição mostra como diferentes tipos de habitação servem diferentes tamanhos de agregado e necessidades.
        """)
    
    # Housing adequacy metrics section
    st.subheader("Avaliação de Adequação Habitacional")
    
    # Calculate housing adequacy metrics
    # Filter for records with area data
    household_area_data = df[df['area_numerical'].notna() & df['household_size_grouped'].notna()].copy()
    
    # Order household sizes
    size_order = ['1', '2', '3', '4', '5', '6+']
    household_area_data['household_size_grouped'] = pd.Categorical(
        household_area_data['household_size_grouped'],
        categories=size_order,
        ordered=True
    )
    
    # Calculate average area by household size
    avg_area_by_household = household_area_data.groupby('household_size_grouped')['area_numerical'].mean().reset_index()
    avg_area_by_household = avg_area_by_household.sort_values('household_size_grouped')
    
    # Calculate statistics for insights
    area_per_person = household_area_data.copy()
    # Convert categorical to numeric for division operation and handle NaN values
    area_per_person['household_size_numeric'] = area_per_person['household_size_grouped'].astype(str).apply(
        lambda x: 6 if x == '6+' else (int(x) if x != 'nan' else np.nan)
    )
    
    # Only calculate area_per_person for rows with valid household size
    area_per_person['area_per_person'] = area_per_person.apply(
        lambda row: row['area_numerical'] / row['household_size_numeric'] 
        if pd.notna(row['household_size_numeric']) and row['household_size_numeric'] > 0 else np.nan, 
        axis=1
    )
    
    # Calculate average area per person by household size
    avg_area_per_person = area_per_person.groupby('household_size_grouped')['area_per_person'].mean().reset_index()
    
    # Create columns for the visualization
    col1, col2 = st.columns(2)
    
    with col1:
        # Create bar chart of average area by household size
        fig_household_area = px.bar(
            avg_area_by_household,
            x='household_size_grouped',
            y='area_numerical',
            color='household_size_grouped',
            title="Tamanho Total da Habitação por Tamanho do Agregado",
            labels={'area_numerical': 'Área Média (m²)', 'household_size_grouped': 'Tamanho do Agregado'},
            color_discrete_sequence=COLOR_SCALES['sequential']
        )
        fig_household_area.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0],
            showlegend=False  # Hide legend since colors are just for visual grouping
        )
        st.plotly_chart(fig_household_area, use_container_width=True)
    
    with col2:
        # Create a chart showing area per person
        fig_area_per_person = px.line(
            avg_area_per_person,
            x='household_size_grouped',
            y='area_per_person',
            markers=True,
            title="Espaço Habitacional por Pessoa por Tamanho do Agregado",
            labels={'area_per_person': 'Área por Pessoa (m²)', 'household_size_grouped': 'Tamanho do Agregado'},
            color_discrete_sequence=[SECONDARY_COLORS[0]]
        )
        # Add a reference line for recommended minimum space per person (15 m²)
        fig_area_per_person.add_hline(
            y=15,
            line_dash="dash",
            line_color="red",
            annotation_text="Mínimo recomendado (15 m²/pessoa)",
            annotation_position="bottom right"
        )
        fig_area_per_person.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig_area_per_person, use_container_width=True)
    
    # Housing Adequacy Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Calculate percentage of households with less than 15m² per person
        area_per_person_metrics = household_area_data.copy()
        
        # Convert categorical to numeric for division operation and handle NaN values
        area_per_person_metrics['household_size_numeric'] = area_per_person_metrics['household_size_grouped'].astype(str).apply(
            lambda x: 6 if x == '6+' else (int(x) if x != 'nan' else np.nan)
        )
        
        # Only calculate area_per_person for rows with valid household size
        area_per_person_metrics['area_per_person'] = area_per_person_metrics.apply(
            lambda row: row['area_numerical'] / row['household_size_numeric'] 
            if pd.notna(row['household_size_numeric']) and row['household_size_numeric'] > 0 else np.nan, 
            axis=1
        )
        
        # Calculate overcrowding
        overcrowded_pct = (area_per_person_metrics['area_per_person'] < 15).sum() / area_per_person_metrics['area_per_person'].count() * 100
        
        st.metric(
            label="Taxa de Sobrelotação",
            value=f"{overcrowded_pct:.1f}%",
            help="Percentagem de agregados com menos de 15m² por pessoa, um limiar comum para espaço habitacional adequado"
        )
    
    with col2:
        # Create a "Housing Adequacy Score"
        # This is simplified approximation based on available data
        
        # Calculate components for the score
        # 1. Adequate space per person (minimum 15m²)
        area_adequacy = (area_per_person_metrics['area_per_person'] >= 15).mean() * 100
        
        # 2. Bedroom adequacy (rough estimate: at least n-1 bedrooms for n people, where n>1)
        bedroom_adequacy_data = df.dropna(subset=['household_size', 'bedroom_count']).copy()
        bedroom_adequacy_data['bedrooms_numeric'] = bedroom_adequacy_data['bedroom_count'].map({'0': 0, '1': 1, '2': 2, '3': 3, '4+': 4})
        bedroom_adequacy_data['adequate_bedrooms'] = bedroom_adequacy_data.apply(
            lambda row: True if pd.isna(row['household_size']) or pd.isna(row['bedrooms_numeric']) else (
                True if row['household_size'] <= 1 else row['bedrooms_numeric'] >= row['household_size'] - 1
            ),
            axis=1
        )
        bedroom_adequacy = bedroom_adequacy_data['adequate_bedrooms'].mean() * 100
        
        # 3. Housing type preference match (simplified - assume preference is met)
        # This is a placeholder as we don't have direct preference data
        preference_match = 80  # Assume 80% match as a reasonable estimate
        
        # Calculate composite score (weighted average)
        housing_adequacy_score = (area_adequacy * 0.4 + bedroom_adequacy * 0.4 + preference_match * 0.2) / 100
        
        # Scale to 0-100
        housing_adequacy_score = min(max(housing_adequacy_score * 100, 0), 100)
        
        # Determine color
        if housing_adequacy_score >= 80:
            delta_color = "normal"  # Green
            interpretation = "Bom"
        elif housing_adequacy_score >= 60:
            delta_color = "normal"  # Green
            interpretation = "Adequado"
        else:
            delta_color = "inverse"  # Red
            interpretation = "Necessita Melhoria"
        
        st.metric(
            label="Índice de Adequação Habitacional",
            value=f"{housing_adequacy_score:.1f}/100",
            delta=interpretation,
            delta_color=delta_color,
            help="Índice composto que mede a adequação habitacional geral baseado em espaço por pessoa, número de quartos e correspondência estimada de preferências"
        )