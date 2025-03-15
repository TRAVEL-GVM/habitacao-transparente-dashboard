# tab1_housing_distribution.py
import streamlit as st
import pandas as pd
import plotly.express as px

def show_housing_distribution_tab(df):
    """
    Display the Housing Distribution tab with visualizations and filters.
    
    Parameters:
    df (DataFrame): The processed housing data
    """
    st.header("Housing Situation Distribution")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        housing_counts = df['housing_situation'].value_counts().reset_index()
        housing_counts.columns = ['Housing Situation', 'Count']
        
        # Create pie chart
        fig = px.pie(
            housing_counts, 
            values='Count', 
            names='Housing Situation',
            color='Housing Situation',
            color_discrete_map={
                'Renting': '#3366CC', 
                'Owned': '#109618', 
                'Living with others': '#FF9900'
            },
            title='Distribution of Housing Situations'
        )
        st.plotly_chart(fig)
    
    with col2:
        st.subheader("Housing Situation by Age Group")
        # Extract birth year range for age groups
        df['birth_period'] = df['ano_nascimento_interval'].str.extract(r'\[(\d+)')
        df['birth_period'] = pd.to_numeric(df['birth_period'], errors='coerce')
        df['age_group'] = pd.cut(
            df['birth_period'], 
            bins=[1960, 1970, 1980, 1990, 2000, 2025],
            labels=['1960s', '1970s', '1980s', '1990s', '2000s+']
        )
        
        # Pivot table for housing situation by age group
        pivot_data = pd.crosstab(df['age_group'], df['housing_situation']).reset_index()
        pivot_data_melted = pd.melt(
            pivot_data, 
            id_vars=['age_group'], 
            var_name='Housing Situation', 
            value_name='Count'
        )
        
        fig = px.bar(
            pivot_data_melted, 
            x='age_group', 
            y='Count', 
            color='Housing Situation',
            color_discrete_map={
                'Renting': '#3366CC', 
                'Owned': '#109618', 
                'Living with others': '#FF9900'
            },
            title='Housing Situation by Birth Decade',
            labels={'age_group': 'Birth Decade'}
        )
        st.plotly_chart(fig)
    
    # Housing situation filters
    st.subheader("Explore Housing Situations")
    selected_situation = st.selectbox(
        "Select Housing Situation to Explore", 
        options=["All", "Renting", "Owned", "Living with others"]
    )
    
    if selected_situation != "All":
        filtered_df = df[df['housing_situation'] == selected_situation]
    else:
        filtered_df = df
    
    # Display statistics based on filter
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Count", len(filtered_df))
    with col2:
        st.metric("Average Birth Year", f"{filtered_df['birth_period'].mean():.0f}")
    with col3:
        if selected_situation == "Renting":
            avg_rent = filtered_df['valor-mensal-renda'].mean()
            st.metric("Average Monthly Rent", f"€{avg_rent:.2f}")
        elif selected_situation == "Owned":
            avg_price = filtered_df['valor-compra'].mean()
            st.metric("Average Purchase Price", f"€{avg_price:.2f}")