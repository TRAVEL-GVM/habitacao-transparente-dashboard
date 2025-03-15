# tab2_geographic_analysis.py
import streamlit as st
import plotly.express as px

def show_geographic_analysis_tab(df):
    """
    Display the Geographic Analysis tab with visualizations and filters.
    
    Parameters:
    df (DataFrame): The processed housing data
    """
    st.header("Geographic Distribution")
    
    # Create map placeholders
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Districts distribution
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
        st.plotly_chart(fig)
        
    with col2:
        st.subheader("Top Districts")
        top_districts = df['distrito'].value_counts().reset_index()
        top_districts.columns = ['District', 'Count']
        top_districts = top_districts.head(5)
        
        st.dataframe(top_districts, hide_index=True)
    
    # Housing costs by region
    st.subheader("Housing Costs by Region")
    
    region_selector = st.selectbox(
        "Select Region to View Housing Costs",
        options=["All"] + sorted(df['distrito'].unique().tolist())
    )
    
    if region_selector != "All":
        region_df = df[df['distrito'] == region_selector]
    else:
        region_df = df
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rent costs by district
        rent_data = region_df[region_df['housing_situation'] == 'Renting']
        if not rent_data.empty and 'valor-mensal-renda' in rent_data.columns:
            fig = px.box(
                rent_data,
                x='distrito',
                y='valor-mensal-renda',
                color='distrito',
                title='Monthly Rent by District',
                labels={'valor-mensal-renda': 'Monthly Rent (€)', 'distrito': 'District'}
            )
            st.plotly_chart(fig)
        else:
            st.write("No rent data available for the selected filter.")
    
    with col2:
        # Purchase costs by district
        purchase_data = region_df[region_df['housing_situation'] == 'Owned']
        if not purchase_data.empty and 'valor-compra' in purchase_data.columns:
            fig = px.box(
                purchase_data,
                x='distrito',
                y='valor-compra',
                color='distrito',
                title='Property Purchase Price by District',
                labels={'valor-compra': 'Purchase Price (€)', 'distrito': 'District'}
            )
            st.plotly_chart(fig)
        else:
            st.write("No purchase data available for the selected filter.")