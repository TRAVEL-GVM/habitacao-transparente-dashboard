# tab2_geographic_analysis.py
import streamlit as st
import plotly.express as px
import pandas as pd

def show_geographic_analysis_tab(df):
    """
    Display the Geographic Analysis tab with enhanced visualizations, explanations, and filters.
    
    Parameters:
    df (DataFrame): The processed housing data
    """
    st.header("Geographic Distribution")
    
    # Overview metrics
    st.subheader("Regional Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        total_districts = df['distrito'].nunique()
        st.metric("Total Districts", total_districts)
    with col2:
        most_expensive_district = df[df['housing_situation'] == 'Renting'].groupby('distrito')['valor-mensal-renda'].mean().idxmax()
        st.metric("Most Expensive District (Rent)", most_expensive_district.capitalize())
    with col3:
        highest_ownership = df.groupby('distrito')['housing_situation'].apply(lambda x: (x == 'Owned').mean() * 100).idxmax()
        st.metric("Highest Ownership Rate", highest_ownership.capitalize())
    
    st.markdown("""
    ### Understanding the Geographic Distribution
    This section shows how housing situations vary across different districts in Portugal. 
    The data reveals regional patterns in ownership, rental rates, and housing costs.
    """)
    
    # Create map placeholders
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Districts distribution with improved aesthetics
        st.subheader("Housing Distribution by District")
        district_counts = df.groupby(['distrito', 'housing_situation']).size().reset_index(name='count')
        fig = px.bar(
            district_counts,
            x='distrito',
            y='count',
            color='housing_situation',
            color_discrete_map={
                'Renting': '#3366CC', 
                'Owned': '#109618', 
                'Living with others': '#FF9900'
            },
            title='Housing Situations by District',
            labels={'distrito': 'District', 'count': 'Count', 'housing_situation': 'Housing Situation'}
        )
        fig.update_layout(
            xaxis_title="District",
            yaxis_title="Number of Residents",
            legend_title="Housing Situation",
            height=500
        )
        st.plotly_chart(fig)
        
        st.markdown("""
        **Key Insights:**
        - The chart shows the distribution of housing situations across Portugal's districts
        - Areas with higher bars indicate more survey participants from those regions
        - The color breakdown reveals ownership vs. rental patterns in each district
        """)
        
    with col2:
        st.subheader("Top Districts")
        top_districts = df['distrito'].value_counts().reset_index()
        top_districts.columns = ['District', 'Count']
        top_districts['District'] = top_districts['District'].str.capitalize()
        top_districts = top_districts.head(5)
        
        st.dataframe(top_districts, hide_index=True)
        
        # Add percentage calculation
        top_districts['Percentage'] = (top_districts['Count'] / top_districts['Count'].sum() * 100).round(1).astype(str) + '%'
        
        # Create a pie chart for top districts
        fig = px.pie(
            top_districts,
            values='Count',
            names='District',
            title='Distribution of Top 5 Districts'
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)
    
    # Housing situation by district
    st.subheader("Housing Situation Distribution")
    
    # Calculate percentages
    district_percentages = df.groupby('distrito')['housing_situation'].value_counts(normalize=True).mul(100).round(1).reset_index(name='percentage')
    district_percentages = district_percentages.rename(columns={'level_1': 'housing_situation'})
    district_percentages['distrito'] = district_percentages['distrito'].str.capitalize()
    
    fig = px.bar(
        district_percentages,
        x='distrito',
        y='percentage',
        color='housing_situation',
        title='Housing Situation Percentage by District',
        labels={'distrito': 'District', 'percentage': 'Percentage (%)', 'housing_situation': 'Housing Situation'},
        color_discrete_map={
            'Renting': '#3366CC', 
            'Owned': '#109618', 
            'Living with others': '#FF9900'
        }
    )
    fig.update_layout(
        xaxis_title="District",
        yaxis_title="Percentage of Residents",
        legend_title="Housing Situation",
        height=500
    )
    st.plotly_chart(fig)
    
    st.markdown("""
    **What This Shows:**
    - This chart normalizes the data to show the percentage breakdown of housing situations in each district
    - Districts with higher ownership rates may indicate more affordable housing markets or different cultural preferences
    - Areas with high rental percentages may suggest more transient populations or expensive housing markets
    """)
    
    # Housing costs by region
    st.subheader("Housing Costs by Region")
    
    region_selector = st.selectbox(
        "Select Region to View Housing Costs",
        options=["All"] + sorted(pd.Series(df['distrito'].unique()).str.capitalize().tolist())
    )
    
    if region_selector != "All":
        region_df = df[df['distrito'].str.capitalize() == region_selector]
        st.markdown(f"Analyzing housing costs for **{region_selector}** district")
    else:
        region_df = df
        st.markdown("Analyzing housing costs across **all districts**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rent costs by district
        rent_data = region_df[region_df['housing_situation'] == 'Renting']
        if not rent_data.empty and 'valor-mensal-renda' in rent_data.columns:
            # Calculate average rent
            avg_rent = rent_data['valor-mensal-renda'].mean().round(2)
            st.metric("Average Monthly Rent", f"€{avg_rent:.2f}")
            
            fig = px.box(
                rent_data,
                x='distrito',
                y='valor-mensal-renda',
                color='distrito',
                title='Monthly Rent by District',
                labels={'valor-mensal-renda': 'Monthly Rent (€)', 'distrito': 'District'}
            )
            fig.update_layout(
                xaxis_title="District",
                yaxis_title="Monthly Rent (€)",
                height=400
            )
            st.plotly_chart(fig)
            
            st.markdown("""
            **Rental Market Insights:**
            - The box plot shows the distribution of monthly rents across districts
            - The box represents the middle 50% of rent values, with the line showing the median
            - Outliers (points outside the whiskers) may represent luxury properties or potentially data anomalies
            """)
        else:
            st.write("No rent data available for the selected filter.")
    
    with col2:
        # Purchase costs by district
        purchase_data = region_df[region_df['housing_situation'] == 'Owned']
        if not purchase_data.empty and 'valor-compra' in purchase_data.columns:
            # Calculate average purchase price
            avg_purchase = purchase_data['valor-compra'].mean().round(2)
            st.metric("Average Purchase Price", f"€{avg_purchase:.2f}")
            
            fig = px.box(
                purchase_data,
                x='distrito',
                y='valor-compra',
                color='distrito',
                title='Property Purchase Price by District',
                labels={'valor-compra': 'Purchase Price (€)', 'distrito': 'District'}
            )
            fig.update_layout(
                xaxis_title="District",
                yaxis_title="Purchase Price (€)",
                height=400
            )
            st.plotly_chart(fig)
            
            st.markdown("""
            **Property Market Insights:**
            - The box plot shows the distribution of property purchase prices across districts
            - Wide boxes indicate greater variability in property prices within that district
            - The position of the box shows the general price level of that district's housing market
            """)
        else:
            st.write("No purchase data available for the selected filter.")
    
    # Add rent-to-income ratio analysis
    st.subheader("Affordability Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rent burden by district
        rent_burden_data = df[df['housing_situation'] == 'Renting'].dropna(subset=['rent_burden', 'distrito'])
        rent_burden_data['distrito'] = rent_burden_data['distrito'].str.capitalize()
        if not rent_burden_data.empty:
            burden_counts = rent_burden_data.groupby(['distrito', 'rent_burden']).size().reset_index(name='count')
            
            fig = px.bar(
                burden_counts,
                x='distrito',
                y='count',
                color='rent_burden',
                title='Rent Burden by District',
                labels={'distrito': 'District', 'count': 'Count', 'rent_burden': 'Rent Burden'},
                category_orders={
                    'rent_burden': ['≤30% (Affordable)', '31-50% (Moderate)', '51-80% (High)', '>80% (Very High)', 'Unknown']
                },
                color_discrete_sequence=px.colors.sequential.Reds
            )
            fig.update_layout(
                xaxis_title="District",
                yaxis_title="Number of Residents",
                legend_title="Rent Burden",
                height=500
            )
            st.plotly_chart(fig)
            
            st.markdown("""
            **Rent Burden Explained:**
            - Rent burden shows what percentage of income residents spend on housing
            - Areas with high proportions of residents spending >30% of income on rent may indicate affordability issues
            - The generally accepted threshold for affordable housing is spending no more than 30% of income on housing
            """)
        else:
            st.write("No rent burden data available for analysis.")
    
    with col2:
        # Property age by district
        if 'ano-compra' in df.columns:
            purchase_year_data = df[df['housing_situation'] == 'Owned'].dropna(subset=['ano-compra', 'distrito'])
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
                    title='Property Age by District',
                    labels={'property_age': 'Property Age (Years)', 'distrito': 'District'}
                )
                fig.update_layout(
                    xaxis_title="District",
                    yaxis_title="Property Age (Years)",
                    height=500
                )
                st.plotly_chart(fig)
                
                st.markdown("""
                **Property Age Analysis:**
                - This chart shows the age distribution of owned properties across districts
                - Newer properties (lower values) may indicate recent development or higher turnover
                - Older property stocks may suggest established neighborhoods or limited new construction
                """)
            else:
                st.write("No property age data available for analysis.")
        else:
            st.write("Property age data not available in the dataset.")