#tab5_education_employment.py
import streamlit as st
import pandas as pd
import plotly.express as px

def show_education_employment_tab(df):
    """
    This tab provides several key insights:

    How housing situations (renting, owning, living with others) vary by education level and employment status
    Average income levels for different education groups
    Rent burden analysis for different employment statuses
    Housing satisfaction levels across education and employment groups
    Reasons for housing dissatisfaction broken down by education level

    The visualizations use a combination of bar charts and heatmaps to make the relationships clear and intuitive. 
    The tab is organized in a way that leads the user through progressively deeper insights about how education and employment relate to housing conditions in Portugal.
    """
    
    st.header("Education & Employment Analysis")
    st.markdown("""
    This section explores how education levels and employment status relate to housing situations,
    income levels, and housing satisfaction in Portugal.
    """)
    
    # Create two columns for the first row of visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Education distribution by housing situation
        st.subheader("Education Level by Housing Situation")
        
        # Filter out rows with missing values
        filtered_df = df.dropna(subset=['education_level', 'housing_situation'])
        
        # Create a crosstab for education level vs housing situation
        education_housing_cross = pd.crosstab(
            filtered_df['education_level'], 
            filtered_df['housing_situation'],
            normalize='index'
        ) * 100
        
        # Create a stacked bar chart
        fig = px.bar(
            education_housing_cross.reset_index().melt(
                id_vars='education_level',
                var_name='housing_situation',
                value_name='percentage'
            ),
            x='education_level',
            y='percentage',
            color='housing_situation',
            title="Housing Situation by Education Level (%)",
            labels={
                'education_level': 'Education Level',
                'percentage': 'Percentage (%)',
                'housing_situation': 'Housing Situation'
            },
            category_orders={
                'education_level': ['Basic', 'High School', 'Vocational', "Bachelor's", "Master's", 'PhD']
            },
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(height=400, legend_title_text='Housing Situation')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        This chart shows how housing situations vary across different education levels.
        It helps identify which education groups are more likely to rent, own, or live with others.
        """)
    
    with col2:
        # Employment status distribution by housing situation
        st.subheader("Employment Status by Housing Situation")
        
        # Filter out rows with missing values
        filtered_df = df.dropna(subset=['employment_status', 'housing_situation'])
        
        # Create a crosstab for employment status vs housing situation
        employment_housing_cross = pd.crosstab(
            filtered_df['employment_status'], 
            filtered_df['housing_situation'],
            normalize='index'
        ) * 100
        
        # Create a stacked bar chart
        fig = px.bar(
            employment_housing_cross.reset_index().melt(
                id_vars='employment_status',
                var_name='housing_situation',
                value_name='percentage'
            ),
            x='employment_status',
            y='percentage',
            color='housing_situation',
            title="Housing Situation by Employment Status (%)",
            labels={
                'employment_status': 'Employment Status',
                'percentage': 'Percentage (%)',
                'housing_situation': 'Housing Situation'
            },
            category_orders={
                'employment_status': ['Full-time', 'Part-time', 'Self-employed', 'Unemployed', 'Student', 'Retired']
            },
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(height=400, legend_title_text='Housing Situation')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        This visualization shows the relationship between employment status and housing situations.
        It helps identify which employment groups are more likely to rent, own, or live with others.
        """)
    
    # Create two columns for the second row of visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Income distribution by education level
        st.subheader("Average Income by Education Level")
        
        # Filter out rows with missing values
        filtered_df = df.dropna(subset=['education_level', 'rendimento_numerical'])
        
        # Group by education level and calculate mean income
        education_income = filtered_df.groupby('education_level')['rendimento_numerical'].mean().reset_index()
        
        # Sort by a specific order
        order = ['Basic', 'High School', 'Vocational', "Bachelor's", "Master's", 'PhD']
        education_income['education_level'] = pd.Categorical(
            education_income['education_level'], 
            categories=order, 
            ordered=True
        )
        education_income = education_income.sort_values('education_level')
        
        # Create a bar chart
        fig = px.bar(
            education_income,
            x='education_level',
            y='rendimento_numerical',
            title="Average Annual Income by Education Level (€)",
            labels={
                'education_level': 'Education Level',
                'rendimento_numerical': 'Average Annual Income (€)'
            },
            color='education_level',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        This chart displays the average annual income across different education levels,
        showing how income typically increases with higher education attainment.
        """)
    
    with col2:
        # Rent burden by employment status
        st.subheader("Rent Burden by Employment Status")
        
        # Filter for renters only and rows with valid data
        renters_df = df[df['housing_situation'] == 'Renting'].dropna(subset=['employment_status', 'rent_burden'])
        
        # Create a crosstab
        rent_burden_employment_cross = pd.crosstab(
            renters_df['employment_status'], 
            renters_df['rent_burden'],
            normalize='index'
        ) * 100
        
        # Create a stacked bar chart
        fig = px.bar(
            rent_burden_employment_cross.reset_index().melt(
                id_vars='employment_status',
                var_name='rent_burden',
                value_name='percentage'
            ),
            x='employment_status',
            y='percentage',
            color='rent_burden',
            title="Rent Burden by Employment Status (%)",
            labels={
                'employment_status': 'Employment Status',
                'percentage': 'Percentage (%)',
                'rent_burden': 'Rent Burden'
            },
            category_orders={
                'employment_status': ['Full-time', 'Part-time', 'Self-employed', 'Unemployed', 'Student', 'Retired'],
                'rent_burden': ['≤30% (Affordable)', '31-50% (Moderate)', '51-80% (High)', '>80% (Very High)', 'Unknown']
            },
            color_discrete_sequence=px.colors.sequential.RdBu_r
        )
        fig.update_layout(height=400, legend_title_text='Rent Burden')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        This visualization shows the distribution of rent burden categories across different employment statuses.
        It helps identify which employment groups are most likely to face affordable or unaffordable housing costs.
        """)
    
    # Third row of visualizations
    st.subheader("Housing Satisfaction by Education and Employment")
    
    # Create columns for the third row
    col1, col2 = st.columns(2)
    
    with col1:
        # Housing satisfaction by education level
        filtered_df = df.dropna(subset=['education_level', 'satisfaction_level'])
        
        # Create a crosstab
        education_satisfaction_cross = pd.crosstab(
            filtered_df['education_level'], 
            filtered_df['satisfaction_level'],
            normalize='index'
        ) * 100
        
        # Create a heatmap
        fig = px.imshow(
            education_satisfaction_cross,
            text_auto='.1f',
            aspect="auto",
            title="Housing Satisfaction by Education Level (%)",
            labels=dict(x="Satisfaction Level", y="Education Level", color="Percentage (%)"),
            x=['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied'],
            y=education_satisfaction_cross.index,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Housing satisfaction by employment status
        filtered_df = df.dropna(subset=['employment_status', 'satisfaction_level'])
        
        # Create a crosstab
        employment_satisfaction_cross = pd.crosstab(
            filtered_df['employment_status'], 
            filtered_df['satisfaction_level'],
            normalize='index'
        ) * 100
        
        # Create a heatmap
        fig = px.imshow(
            employment_satisfaction_cross,
            text_auto='.1f',
            aspect="auto",
            title="Housing Satisfaction by Employment Status (%)",
            labels=dict(x="Satisfaction Level", y="Employment Status", color="Percentage (%)"),
            x=['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied'],
            y=employment_satisfaction_cross.index,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    These heatmaps show the distribution of housing satisfaction levels across different education levels and employment statuses.
    Darker green indicates higher satisfaction, while darker red indicates higher dissatisfaction.
    """)
    
    # Add a final row with a combined analysis
    st.subheader("Reasons for Housing Dissatisfaction by Education Level")
    
    # Get the list of dissatisfaction reasons from the column names
    reason_columns = [col for col in df.columns if col.startswith('reason_')]
    
    # Create a dataframe with education levels and dissatisfaction reasons
    dissatisfaction_by_education = pd.DataFrame()
    
    # Filter for dissatisfied respondents
    dissatisfied_df = df[df['satisfaction_level'].isin(['Dissatisfied', 'Very Dissatisfied'])]
    
    # Calculate the percentage of each reason by education level
    for reason in reason_columns:
        # Get the display name for the reason
        reason_display = reason.replace('reason_', '').replace('-', ' ').title()
        
        # Group by education level and calculate the percentage with this reason
        reason_by_education = dissatisfied_df.groupby('education_level')[reason].mean() * 100
        dissatisfaction_by_education[reason_display] = reason_by_education
    
    # Reset index to make education level a column
    dissatisfaction_by_education = dissatisfaction_by_education.reset_index()
    
    # Melt the dataframe for plotting
    dissatisfaction_melted = dissatisfaction_by_education.melt(
        id_vars='education_level',
        var_name='Reason',
        value_name='Percentage'
    )
    
    # Create a grouped bar chart
    fig = px.bar(
        dissatisfaction_melted,
        x='education_level',
        y='Percentage',
        color='Reason',
        title="Reasons for Housing Dissatisfaction by Education Level",
        labels={
            'education_level': 'Education Level',
            'Percentage': 'Percentage (%)',
            'Reason': 'Dissatisfaction Reason'
        },
        category_orders={
            'education_level': ['Basic', 'High School', 'Vocational', "Bachelor's", "Master's", 'PhD']
        },
        barmode='group'
    )
    fig.update_layout(height=500, legend_title_text='Reason')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    This chart displays the primary reasons for housing dissatisfaction broken down by education level.
    It helps identify which issues are most prevalent for each education group.
    """)