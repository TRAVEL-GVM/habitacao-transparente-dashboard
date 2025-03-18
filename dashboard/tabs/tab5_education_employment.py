#tab5_education_employment.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))
from config import *

def show_education_employment_tab(df):
    """
    Este separador fornece várias conclusões importantes:

    Como as situações habitacionais (arrendamento, propriedade, viver com outros) variam por nível educacional e situação profissional
    Níveis médios de rendimento para diferentes grupos educacionais
    Análise da sobrecarga de renda para diferentes situações profissionais
    Níveis de satisfação habitacional entre grupos educacionais e profissionais
    Razões para insatisfação habitacional divididas por nível educacional

    As visualizações utilizam uma combinação de gráficos de barras e mapas de calor para tornar as relações claras e intuitivas.
    O separador está organizado de forma a guiar o utilizador através de insights progressivamente mais profundos sobre como 
    a educação e o emprego se relacionam com as condições habitacionais em Portugal.
    """
    
    st.header("Análise de Educação e Emprego: Impacto nas Condições Habitacionais")
    
    # Introdução com estilo melhorado
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
    <h4 style="color: #2e7d32; margin-top: 0;">Visão Geral</h4>
    <p>Esta secção explora como os níveis educacionais e a situação profissional se relacionam com as situações 
    habitacionais, níveis de rendimento e satisfação com a habitação em Portugal.</p>
    <ul>
      <li><strong>Tendências Principais:</strong> Existe uma forte correlação entre nível educacional, situação profissional e condições habitacionais</li>
      <li><strong>Rendimento e Educação:</strong> Níveis educacionais mais elevados estão associados a rendimentos superiores e menor sobrecarga habitacional</li>
      <li><strong>Satisfação Habitacional:</strong> A satisfação com a habitação varia significativamente entre diferentes grupos profissionais e educacionais</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas principais
    # Calcular algumas estatísticas para as métricas rápidas
    avg_income = df[df['rendimento_numerical'].notna()]['rendimento_numerical'].mean()
    
    # Calcular percentagem de pessoas com educação superior
    higher_edu_count = df[df['education_level'].isin(["Bachelor's", "Master's", 'PhD'])].shape[0]
    higher_edu_pct = (higher_edu_count / df['education_level'].count()) * 100
    
    # Calcular percentagem de emprego a tempo inteiro
    fulltime_count = df[df['employment_status'] == 'Full-time'].shape[0]
    fulltime_pct = (fulltime_count / df['employment_status'].count()) * 100
    
    # Criar 3 colunas para métricas rápidas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Rendimento Médio Anual",
            value=f"{avg_income:.0f} €",
            help="Rendimento médio anual dos inquiridos"
        )
    
    with col2:
        st.metric(
            label="Educação Superior",
            value=f"{higher_edu_pct:.1f}%",
            help="Percentagem de inquiridos com formação superior (Licenciatura, Mestrado ou Doutoramento)"
        )
    
    with col3:
        st.metric(
            label="Emprego a Tempo Inteiro",
            value=f"{fulltime_pct:.1f}%",
            help="Percentagem de inquiridos empregados a tempo inteiro"
        )
    
    # SECÇÃO 1: EDUCAÇÃO E SITUAÇÃO HABITACIONAL
    st.subheader("Níveis Educacionais e Situação Habitacional")
    
    st.markdown("""
    Esta secção analisa como os diferentes níveis educacionais se relacionam com as situações habitacionais em Portugal,
    revelando padrões importantes na relação entre formação académica e acesso à habitação.
    """)
    
    # Criar colunas para visualizações
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição educacional por situação habitacional
        
        # Filtrar linhas com valores em falta
        filtered_df = df.dropna(subset=['education_level', 'housing_situation'])
        
        # Traduzir níveis educacionais
        education_mapping = {
            'Basic': 'Básico',
            'High School': 'Secundário',
            'Vocational': 'Profissional',
            "Bachelor's": 'Licenciatura',
            "Master's": 'Mestrado',
            'PhD': 'Doutoramento'
        }
        
        # Traduzir situações habitacionais
        housing_mapping = {
            'Arrendamento': 'Arrendamento',
            'Casa Própria': 'Propriedade',
            'Others': 'A viver com outros'
        }
        
        # Aplicar mapeamento
        filtered_df['education_level_pt'] = filtered_df['education_level'].map(education_mapping)
        filtered_df['housing_situation_pt'] = filtered_df['housing_situation'].map(housing_mapping)
        
        # Criar uma tabela cruzada para nível educacional vs situação habitacional
        education_housing_cross = pd.crosstab(
            filtered_df['education_level_pt'], 
            filtered_df['housing_situation_pt'],
            normalize='index'
        ) * 100
        
        # Criar um gráfico de barras empilhadas
        fig = px.bar(
            education_housing_cross.reset_index().melt(
                id_vars='education_level_pt',
                var_name='housing_situation_pt',
                value_name='percentage'
            ),
            x='education_level_pt',
            y='percentage',
            color='housing_situation_pt',
            title="Situação Habitacional por Nível Educacional (%)",
            labels={
                'education_level_pt': 'Nível Educacional',
                'percentage': 'Percentagem (%)',
                'housing_situation_pt': 'Situação Habitacional'
            },
            category_orders={
                'education_level_pt': ['Básico', 'Secundário', 'Profissional', 'Licenciatura', 'Mestrado', 'Doutoramento']
            },
            color_discrete_map={
                'Arrendamento': HOUSING_COLORS['Arrendamento'],
                'Propriedade': HOUSING_COLORS['Casa Própria'], 
                'A viver com outros': HOUSING_COLORS['Others']
            }
        )
        fig.update_layout(
            height=400,
            legend_title_text='Situação Habitacional',
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        Este gráfico mostra como as situações habitacionais variam entre diferentes níveis educacionais.
        Ajuda a identificar quais os grupos educacionais mais propensos a arrendar, possuir, ou viver com outros.
        """)
    
    with col2:
        # Rendimento médio por nível educacional

        # Filtrar linhas com valores em falta
        filtered_df = df.dropna(subset=['education_level', 'rendimento_numerical'])
        filtered_df['education_level_pt'] = filtered_df['education_level'].map(education_mapping)
        
        # Agrupar por nível educacional e calcular rendimento médio
        education_income = filtered_df.groupby('education_level_pt')['rendimento_numerical'].mean().reset_index()
        
        # Ordenar por uma ordem específica
        order = ['Básico', 'Secundário', 'Profissional', 'Licenciatura', 'Mestrado', 'Doutoramento']
        education_income['education_level_pt'] = pd.Categorical(
            education_income['education_level_pt'], 
            categories=order, 
            ordered=True
        )
        education_income = education_income.sort_values('education_level_pt')
        
        # Criar um gráfico de barras
        fig = px.bar(
            education_income,
            x='education_level_pt',
            y='rendimento_numerical',
            title="Rendimento Médio Anual por Nível Educacional (€)",
            labels={
                'education_level_pt': 'Nível Educacional',
                'rendimento_numerical': 'Rendimento Médio Anual (€)'
            },
            color='education_level_pt',
            color_discrete_sequence=PRIMARY_COLORS
        )
        fig.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        Este gráfico apresenta o rendimento médio anual em diferentes níveis educacionais,
        mostrando como o rendimento tipicamente aumenta com níveis educacionais mais elevados.
        """)
    
    # SECÇÃO 2: SITUAÇÃO PROFISSIONAL E HABITAÇÃO
    st.subheader("Situação Profissional e Condições Habitacionais")
    
    st.markdown("""
    Esta secção examina a relação entre a situação profissional e as condições habitacionais,
    com foco na sobrecarga do arrendamento e nos padrões habitacionais entre diferentes grupos profissionais.
    """)
    
    # Criar colunas para visualizações
    col1, col2 = st.columns(2)
    
    with col1:
        # Situação profissional por situação habitacional

        # Filtrar linhas com valores em falta
        filtered_df = df.dropna(subset=['employment_status', 'housing_situation'])
        
        # Traduzir situações profissionais
        employment_mapping = {
            'Full-time': 'Tempo Inteiro',
            'Part-time': 'Tempo Parcial',
            'Self-employed': 'Trabalhador Independente',
            'Unemployed': 'Desempregado',
            'Student': 'Estudante',
            'Retired': 'Reformado'
        }
        
        # Traduzir situações habitacionais (necessário neste escopo também)
        housing_mapping = {
            'Arrendamento': 'Arrendamento',
            'Casa Própria': 'Propriedade',
            'Others': 'A viver com outros'
        }
        
        # Aplicar mapeamentos
        filtered_df['employment_status_pt'] = filtered_df['employment_status'].map(employment_mapping)
        filtered_df['housing_situation_pt'] = filtered_df['housing_situation'].map(housing_mapping)
        
        # Criar uma tabela cruzada para situação profissional vs situação habitacional
        employment_housing_cross = pd.crosstab(
            filtered_df['employment_status_pt'], 
            filtered_df['housing_situation_pt'],
            normalize='index'
        ) * 100
        
        # Criar um gráfico de barras empilhadas
        fig = px.bar(
            employment_housing_cross.reset_index().melt(
                id_vars='employment_status_pt',
                var_name='housing_situation_pt',
                value_name='percentage'
            ),
            x='employment_status_pt',
            y='percentage',
            color='housing_situation_pt',
            title="Situação Habitacional por Situação Profissional (%)",
            labels={
                'employment_status_pt': 'Situação Profissional',
                'percentage': 'Percentagem (%)',
                'housing_situation_pt': 'Situação Habitacional'
            },
            category_orders={
                'employment_status_pt': ['Tempo Inteiro', 'Tempo Parcial', 'Trabalhador Independente', 'Desempregado', 'Estudante', 'Reformado']
            },
            color_discrete_map={
                'Arrendamento': HOUSING_COLORS['Arrendamento'],
                'Propriedade': HOUSING_COLORS['Casa Própria'], 
                'A viver com outros': HOUSING_COLORS['Others']
            }
        )
        fig.update_layout(
            height=400,
            legend_title_text='Situação Habitacional',
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        Esta visualização mostra a relação entre situação profissional e situações habitacionais.
        Ajuda a identificar quais os grupos profissionais mais propensos a arrendar, possuir, ou viver com outros.
        """)
    
    with col2:
        # Sobrecarga de renda por situação profissional
        # Filtrar apenas para arrendatários e linhas com dados válidos
        renters_df = df[df['housing_situation'] == 'Arrendamento'].dropna(subset=['employment_status', 'rent_burden'])
        renters_df['employment_status_pt'] = renters_df['employment_status'].map(employment_mapping)
        
        # Traduzir categorias de sobrecarga de renda
        burden_mapping = {
            '≤30% (Affordable)': '≤30% (Acessível)',
            '31-50% (Moderate)': '31-50% (Moderada)',
            '51-80% (High)': '51-80% (Alta)',
            '>80% (Very High)': '>80% (Muito Alta)',
            'Unknown': 'Desconhecida'
        }
        
        renters_df['rent_burden_pt'] = renters_df['rent_burden'].map(burden_mapping)
        
        # Criar uma tabela cruzada
        rent_burden_employment_cross = pd.crosstab(
            renters_df['employment_status_pt'], 
            renters_df['rent_burden_pt'],
            normalize='index'
        ) * 100
        
        # Criar gráfico de barras empilhadas
        fig = px.bar(
            rent_burden_employment_cross.reset_index().melt(
                id_vars='employment_status_pt',
                var_name='rent_burden_pt',
                value_name='percentage'
            ),
            x='employment_status_pt',
            y='percentage',
            color='rent_burden_pt',
            title="Sobrecarga de Renda por Situação Profissional (%)",
            labels={
                'employment_status_pt': 'Situação Profissional',
                'percentage': 'Percentagem (%)',
                'rent_burden_pt': 'Sobrecarga de Renda'
            },
            category_orders={
                'employment_status_pt': ['Tempo Inteiro', 'Tempo Parcial', 'Trabalhador Independente', 'Desempregado', 'Estudante', 'Reformado'],
                'rent_burden_pt': ['≤30% (Acessível)', '31-50% (Moderada)', '51-80% (Alta)', '>80% (Muito Alta)', 'Desconhecida']
            },
            color_discrete_map={
                '≤30% (Acessível)': RENT_BURDEN_COLORS['≤30% (Affordable)'],
                '31-50% (Moderada)': RENT_BURDEN_COLORS['31-50% (Moderate)'],
                '51-80% (Alta)': RENT_BURDEN_COLORS['51-80% (High)'],
                '>80% (Muito Alta)': RENT_BURDEN_COLORS['>80% (Very High)'],
                'Desconhecida': RENT_BURDEN_COLORS['Unknown']
            }
        )
        fig.update_layout(
            height=400,
            legend_title_text='Sobrecarga de Renda',
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        Esta visualização mostra a distribuição das categorias de sobrecarga de renda entre diferentes situações profissionais.
        Ajuda a identificar quais os grupos profissionais mais propensos a enfrentar custos habitacionais acessíveis ou inacessíveis.
        """)
    
    # SECÇÃO 3: SATISFAÇÃO HABITACIONAL
    st.subheader("Satisfação Habitacional por Educação e Emprego")
    
    st.markdown("""
    Esta secção analisa os níveis de satisfação habitacional entre diferentes grupos educacionais e profissionais,
    revelando como estas características socioeconómicas se relacionam com a perceção da qualidade habitacional.
    """)
    
    # Criar colunas para visualizações
    col1, col2 = st.columns(2)
    
    with col1:
        # Satisfação habitacional por nível educacional
        
        filtered_df = df.dropna(subset=['education_level', 'satisfaction_level'])
        filtered_df['education_level_pt'] = filtered_df['education_level'].map(education_mapping)
        
        # Traduzir níveis de satisfação
        satisfaction_mapping = {
            'Very Dissatisfied': 'Muito Insatisfeito',
            'Dissatisfied': 'Insatisfeito',
            'Neutral': 'Neutro',
            'Satisfied': 'Satisfeito',
            'Very Satisfied': 'Muito Satisfeito'
        }
        
        filtered_df['satisfaction_level_pt'] = filtered_df['satisfaction_level'].map(satisfaction_mapping)
        
        # Criar uma tabela cruzada
        education_satisfaction_cross = pd.crosstab(
            filtered_df['education_level_pt'], 
            filtered_df['satisfaction_level_pt'],
            normalize='index'
        ) * 100
        
        # Definir a ordem dos níveis de satisfação
        satisfaction_order = ['Muito Insatisfeito', 'Insatisfeito', 'Neutro', 'Satisfeito', 'Muito Satisfeito']
        
        # Certificar que todas as colunas estão presentes
        for level in satisfaction_order:
            if level not in education_satisfaction_cross.columns:
                education_satisfaction_cross[level] = 0
        
        # Reordenar as colunas
        education_satisfaction_cross = education_satisfaction_cross[satisfaction_order]
        
        # Criar um mapa de calor
        fig = px.imshow(
            education_satisfaction_cross,
            text_auto='.1f',
            aspect="auto",
            title="Satisfação Habitacional por Nível Educacional (%)",
            labels=dict(x="Nível de Satisfação", y="Nível Educacional", color="Percentagem (%)"),
            x=satisfaction_order,
            y=education_satisfaction_cross.index,
            color_continuous_scale=COLOR_SCALES['sequential']
        )
        fig.update_layout(
            height=400,
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Satisfação habitacional por situação profissional
        
        filtered_df = df.dropna(subset=['employment_status', 'satisfaction_level'])
        filtered_df['employment_status_pt'] = filtered_df['employment_status'].map(employment_mapping)
        filtered_df['satisfaction_level_pt'] = filtered_df['satisfaction_level'].map(satisfaction_mapping)
        
        # Criar uma tabela cruzada
        employment_satisfaction_cross = pd.crosstab(
            filtered_df['employment_status_pt'], 
            filtered_df['satisfaction_level_pt'],
            normalize='index'
        ) * 100
        
        # Certificar que todas as colunas estão presentes
        for level in satisfaction_order:
            if level not in employment_satisfaction_cross.columns:
                employment_satisfaction_cross[level] = 0
        
        # Reordenar as colunas
        employment_satisfaction_cross = employment_satisfaction_cross[satisfaction_order]
        
        # Criar um mapa de calor
        fig = px.imshow(
            employment_satisfaction_cross,
            text_auto='.1f',
            aspect="auto",
            title="Satisfação Habitacional por Situação Profissional (%)",
            labels=dict(x="Nível de Satisfação", y="Situação Profissional", color="Percentagem (%)"),
            x=satisfaction_order,
            y=employment_satisfaction_cross.index,
            color_continuous_scale=COLOR_SCALES['sequential']
        )
        fig.update_layout(
            height=400,
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    Estes mapas de calor mostram a distribuição dos níveis de satisfação habitacional entre diferentes níveis educacionais e situações profissionais.
    Verde mais escuro indica maior satisfação, enquanto vermelho mais escuro indica maior insatisfação.
    """)
    
    # SECÇÃO 4: RAZÕES DE INSATISFAÇÃO
    st.subheader("Razões de Insatisfação Habitacional por Nível Educacional")
    
    st.markdown("""
    Esta secção analisa as principais razões de insatisfação habitacional entre diferentes grupos educacionais,
    ajudando a identificar desafios específicos enfrentados por pessoas com diferentes níveis de formação.
    """)
    
    # Obter a lista de razões de insatisfação a partir dos nomes das colunas
    reason_columns = [col for col in df.columns if col.startswith('reason_')]
    
    # Traduzir razões para português
    reason_translation = {
        'reason_pago-demasiado': 'Pago Demasiado',
        'reason_falta-espaco': 'Falta de Espaço',
        'reason_habitacao-mau-estado': 'Habitação em Mau Estado',
        'reason_vivo-longe': 'Vivo Longe do Trabalho',
        'reason_quero-independecia': 'Quero Independência',
        'reason_dificuldades-financeiras': 'Dificuldades Financeiras',
        'reason_financeiramente-dependente': 'Dependência Financeira',
        'reason_vivo-longe-de-transportes': 'Longe de Transportes',
        'reason_vivo-zona-insegura': 'Zona Insegura',
        'reason_partilho-casa-com-desconhecidos': 'Partilho Casa com Desconhecidos'
    }
    
    # Criar um dataframe com níveis educacionais e razões de insatisfação
    dissatisfaction_by_education = pd.DataFrame()
    
    # Filtrar para inquiridos insatisfeitos
    dissatisfied_df = df[df['satisfaction_level'].isin(['Dissatisfied', 'Very Dissatisfied'])]
    dissatisfied_df['education_level_pt'] = dissatisfied_df['education_level'].map(education_mapping)
    
    # Calcular a percentagem de cada razão por nível educacional
    for reason in reason_columns:
        # Obter o nome de exibição para a razão
        reason_display = reason_translation.get(reason, reason.replace('reason_', '').replace('-', ' ').title())
        
        # Agrupar por nível educacional e calcular a percentagem com esta razão
        reason_by_education = dissatisfied_df.groupby('education_level_pt')[reason].mean() * 100
        dissatisfaction_by_education[reason_display] = reason_by_education
    
    # Redefinir índice para tornar o nível educacional uma coluna
    dissatisfaction_by_education = dissatisfaction_by_education.reset_index()
    
    # Transformar o dataframe para plotagem
    dissatisfaction_melted = dissatisfaction_by_education.melt(
        id_vars='education_level_pt',
        var_name='Razão',
        value_name='Percentagem'
    )
    
    # Definir ordem dos níveis educacionais
    education_order = ['Básico', 'Secundário', 'Profissional', 'Licenciatura', 'Mestrado', 'Doutoramento']
    dissatisfaction_melted['education_level_pt'] = pd.Categorical(
        dissatisfaction_melted['education_level_pt'],
        categories=education_order,
        ordered=True
    )
    
    # Criar um gráfico de barras agrupadas
    fig = px.bar(
        dissatisfaction_melted,
        x='education_level_pt',
        y='Percentagem',
        color='Razão',
        title="Razões de Insatisfação Habitacional por Nível Educacional",
        labels={
            'education_level_pt': 'Nível Educacional',
            'Percentagem': 'Percentagem (%)',
            'Razão': 'Motivo de Insatisfação'
        },
        barmode='group',
        color_discrete_sequence=CHART_COLORS
    )
    fig.update_layout(
        height=500,
        legend_title_text='Razão',
        plot_bgcolor=BACKGROUND_COLORS[0],
        paper_bgcolor=BACKGROUND_COLORS[3],
        font_color=TEXT_COLORS[2],
        title_font_color=TEXT_COLORS[0]
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Obter as razões mais comuns
    top_reasons = dissatisfaction_melted.groupby('Razão')['Percentagem'].mean().sort_values(ascending=False).head(3).index.tolist()
    
    st.markdown(f"""
    **Insights Principais:**
    
    - As três razões mais comuns para insatisfação habitacional são: {", ".join(top_reasons)}
    - Inquiridos com níveis educacionais mais altos (Licenciatura, Mestrado, Doutoramento) tendem a reportar insatisfação devido a custos elevados e problemas de localização
    - Inquiridos com níveis educacionais mais baixos reportam mais frequentemente problemas relacionados com o estado físico da habitação e dificuldades financeiras
    - A falta de espaço é uma preocupação transversal a todos os níveis educacionais, sugerindo um problema generalizado nas opções habitacionais disponíveis
    
    Estes insights indicam que diferentes grupos educacionais enfrentam desafios habitacionais distintos, o que sugere a necessidade de abordagens diversificadas nas políticas habitacionais.
    """)