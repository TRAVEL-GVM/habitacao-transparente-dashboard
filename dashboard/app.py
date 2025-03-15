import os

import numpy as np
import pandas as pd
import streamlit as st
from tabs.tab1_housing_distribution import show_housing_distribution_tab
from tabs.tab2_geographic_analysis import show_geographic_analysis_tab
from tabs.tab3_satisfaction_levels import show_satisfaction_levels_tab
from tabs.tab4_income_housing_costs import show_income_housing_costs_tab
from tabs.tab5_education_employment import show_education_employment_tab
from tabs.tab6_housing_types_sizes import show_housing_types_sizes_tab

# Set page configuration
st.set_page_config(layout="wide", page_title="Dashboard do Habitação Transparente")

# Define function to load data
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()  # Return empty dataframe if loading fails

    # Process the data for easier analysis
    # Clean list-like columns
    for col in ['situacao-habitacional', 'tipo-casa', 'tipologia', 'situacao-profissional', 
                'satisfacao', 'estrategia-arrendamento', 'insatisfacao-motivos', 'estrategia-compra']:
        if col in df.columns:
            df[col] = df[col].str.replace('[', '').str.replace(']', '').str.replace("'", '').str.split(', ')
            # Extract first value for simplicity
            df[col + '_primary'] = df[col].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x)
    
    # Parse income brackets for easier categorization
    def parse_income(income_str):
        # Handle NaN values
        if pd.isna(income_str):
            return np.nan, np.nan
        
        # Extract the income range from brackets if present
        if isinstance(income_str, list):
            if not income_str:  # Empty list
                return np.nan, np.nan
            income_str = income_str[0]  # Take the first element if it's a list
        
        # Remove any extraneous characters or whitespace
        clean_income_str = str(income_str).strip().lower()
        
        # Income bracket mapping
        income_mapping = {
            'sem-rendimento': 0,
            '<7001': 3500,
            '7001-12000': 9500,
            '12001-20000': 16000,
            '20001-35000': 27500,
            '35001-50000': 42500,
            '50001-80000': 65000,
            '>80001': 100000
        }
        
        # Return mapped value if direct match exists
        if clean_income_str in income_mapping:
            return clean_income_str, income_mapping[clean_income_str]
        
        # Handle edge cases with regex pattern matching
        import re
        
        # Match patterns like "<7001", "7001-12000", ">80001"
        pattern = r'(<|>)?(\d+)(?:-(\d+))?'
        match = re.match(pattern, clean_income_str)
        
        if match:
            prefix, start, end = match.groups()
            
            # Standardize the format for cleaned string
            if prefix == '<':
                clean_str = f"<{start}"
                value = float(start) / 2  # Half of upper bound
            elif prefix == '>':
                clean_str = f">{start}"
                value = float(start) * 1.25  # 25% more than lower bound
            elif end:  # Range like "7001-12000"
                clean_str = f"{start}-{end}"
                value = (float(start) + float(end)) / 2  # Midpoint
            else:  # Single value
                clean_str = start
                value = float(start)
                
            return clean_str, value
        
        # If no patterns matched
        return np.nan, np.nan

    # Apply the function to the dataframe and create two new columns
    cleaned_values = df['rendimento-anual'].apply(parse_income)
    df['rendimento_clean'] = [x[0] for x in cleaned_values]
    df['rendimento_numerical'] = [x[1] for x in cleaned_values]
    
    # Create a clean housing situation column
    df['housing_situation'] = df['situacao-habitacional_primary'].map({
        'arrendo': 'Renting',
        'comprei': 'Owned',
        'outrem': 'Living with others'
    })
    
    # Clean satisfaction levels
    df['satisfaction_level'] = df['satisfacao_primary'].map({
        'muito-satisfeito': 'Very Satisfied',
        'satisfeito': 'Satisfied',
        'indiferente': 'Neutral',
        'insatisfeito': 'Dissatisfied',
        'muito-insatisfeito': 'Very Dissatisfied'
    })
    
    # Extract numeric values from area-util
    def parse_area(area_str):
        if pd.isna(area_str):
            return np.nan
        elif area_str == '>400':
            return 450
        elif '-' in area_str:
            try:
                min_val, max_val = map(int, area_str.split('-'))
                return (min_val + max_val) / 2
            except ValueError:
                return np.nan
        else:
            return np.nan
    
    df['area_numerical'] = df['area-util'].apply(parse_area)
    
    # Create rent percentage categories
    def categorize_rent_percentage(pct):
        if pd.isna(pct):
            return "Unknown"
        try:
            pct = float(pct)
        except ValueError:
            return "Unknown"
        if pct <= 30:
            return "≤30% (Affordable)"
        elif pct <= 50:
            return "31-50% (Moderate)"
        elif pct <= 80:
            return "51-80% (High)"
        else:
            return ">80% (Very High)"
    
    df['rent_burden'] = df['percentagem-renda-paga'].apply(categorize_rent_percentage)
    
    # Create house type and typology columns
    df['house_type'] = df['tipo-casa_primary'].map({
        'apartamento': 'Apartment',
        'moradia': 'House'
    })
    
    # Clean typology
    df['bedroom_count'] = df['tipologia_primary'].map({
        'T0': '0',
        'T1': '1',
        'T2': '2',
        'T3': '3',
        'T4+': '4+'
    })
    
    # Process dissatisfaction reasons
    dissatisfaction_reasons = [
        'pago-demasiado', 'falta-espaco', 'habitacao-mau-estado', 
        'vivo-longe', 'quero-independecia', 'dificuldades-financeiras',
        'financeiramente-dependente', 'vivo-longe-de-transportes',
        'vivo-zona-insegura', 'partilho-casa-com-desconhecidos'
    ]
    
    for reason in dissatisfaction_reasons:
        df[f'reason_{reason}'] = df['insatisfacao-motivos'].apply(
            lambda x: 1 if isinstance(x, list) and reason in x else 0
        )
    
    # Clean professional situation
    df['employment_status'] = df['situacao-profissional_primary'].map({
        'empregado-tempo-inteiro': 'Full-time',
        'empregado-tempo-parcial': 'Part-time',
        'independente': 'Self-employed',
        'desempregado': 'Unemployed',
        'estudante': 'Student',
        'reformado': 'Retired'
    })
    
    # Clean education levels
    df['education_level'] = df['educacao'].map({
        'licenciatura': "Bachelor's",
        'mestrado': "Master's",
        'doutoramento': 'PhD',
        'secundario': 'High School',
        'profissional': 'Vocational',
        'basico': 'Basic'
    })
    
    return df

# Set file path for data loading
file_path = os.getcwd() + "/data.csv"

# Load the data from root folder
df = load_data(file_path)

# Create dashboard title and introduction
st.title("Dashboard do Habitação Transparente")
st.markdown("""
This interactive dashboard visualizes housing conditions in Portugal, including ownership patterns, 
geographic distribution, satisfaction levels, and financial aspects.
""")

# Create tabs for different insights
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Housing Distribution", 
    "Geographic Analysis", 
    "Satisfaction Levels", 
    "Income vs Housing Costs",
    "Education & Employment",
    "Housing Types & Sizes"
])

with tab1:
    show_housing_distribution_tab(df)

with tab2:
    show_geographic_analysis_tab(df)

with tab3:
    show_satisfaction_levels_tab(df)

with tab4:
    show_income_housing_costs_tab(df)
    
with tab5:
    show_education_employment_tab(df)

with tab6:
    show_housing_types_sizes_tab(df)