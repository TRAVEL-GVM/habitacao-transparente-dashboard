#tab6_housing_types_sizes.py
import pandas as pd
import streamlit as st
import plotly.express as px

def show_housing_types_sizes_tab(df):
    """
    The "Housing Types & Sizes" tab provides the following visualizations:
    
    Distribution of housing types (apartments vs. houses) using a pie chart
    Bedroom distribution across the dataset using a bar chart
    Housing size distribution in square meters
    Comparison of housing sizes between apartments and houses using box plots
    Relationship between housing types and bedroom counts
    Analysis of housing sizes in relation to satisfaction levels
    Average housing size by household composition
    """
    st.header("Housing Types & Sizes Analysis")
    
    # Create columns for layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution of Housing Types")
        
        # Count housing types
        house_type_counts = df['house_type'].value_counts().reset_index()
        house_type_counts.columns = ['House Type', 'Count']
        
        # Create pie chart for housing types
        fig_house_type = px.pie(
            house_type_counts, 
            values='Count', 
            names='House Type',
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Distribution of Apartments vs Houses"
        )
        fig_house_type.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_house_type, use_container_width=True)

    with col2:
        st.subheader("Bedroom Distribution")
        
        # Count bedroom types
        bedroom_counts = df['bedroom_count'].value_counts().reset_index()
        bedroom_counts.columns = ['Bedrooms', 'Count']
        
        # Sort the bedroom counts in logical order
        bedroom_order = ['0', '1', '2', '3', '4+']
        bedroom_counts['Bedrooms'] = pd.Categorical(
            bedroom_counts['Bedrooms'], 
            categories=bedroom_order, 
            ordered=True
        )
        bedroom_counts = bedroom_counts.sort_values('Bedrooms')
        
        # Create bar chart for bedroom distribution
        fig_bedrooms = px.bar(
            bedroom_counts,
            x='Bedrooms',
            y='Count',
            color='Bedrooms',
            title="Number of Bedrooms Distribution",
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.plotly_chart(fig_bedrooms, use_container_width=True)

    # Housing area analysis
    st.subheader("Housing Size Analysis")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Create area bins and labels for better visualization
        area_bins = [0, 50, 100, 150, 200, 250, 300, 350, 400, 500]
        area_labels = ['0-50', '51-100', '101-150', '151-200', '201-250', '251-300', '301-350', '351-400', '400+']
        
        # Create a new column with binned areas
        df_with_area = df[df['area_numerical'].notna()].copy()
        df_with_area['area_binned'] = pd.cut(df_with_area['area_numerical'], bins=area_bins, labels=area_labels)
        
        # Count areas by bin
        area_counts = df_with_area['area_binned'].value_counts().reset_index()
        area_counts.columns = ['Area (m²)', 'Count']
        
        # Sort by area size
        area_counts['Area (m²)'] = pd.Categorical(
            area_counts['Area (m²)'], 
            categories=area_labels, 
            ordered=True
        )
        area_counts = area_counts.sort_values('Area (m²)')
        
        # Create histogram for area distribution
        fig_area = px.bar(
            area_counts,
            x='Area (m²)',
            y='Count',
            color='Area (m²)',
            title="Housing Size Distribution (m²)",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig_area, use_container_width=True)
    
    with col4:
        # Compare housing sizes across housing types
        # First ensure we have both columns with data
        valid_data = df[df['area_numerical'].notna() & df['house_type'].notna()]
        
        # Create boxplot comparing areas by housing type
        fig_area_by_type = px.box(
            valid_data,
            x='house_type',
            y='area_numerical',
            color='house_type',
            title="Housing Size by Type",
            labels={'area_numerical': 'Area (m²)', 'house_type': 'Housing Type'},
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_area_by_type, use_container_width=True)
    
    # Compare bedroom count with housing type
    st.subheader("Relationship Between Housing Types and Bedrooms")
    
    # Calculate the cross-tabulation of housing type and bedroom count
    housing_bedroom_data = pd.crosstab(
        df['house_type'], 
        df['bedroom_count'],
        margins=False
    ).reset_index()
    
    # Filter out rows with NaN values
    housing_bedroom_data = housing_bedroom_data.dropna()
    
    # Melt the dataframe for easier plotting
    housing_bedroom_melted = pd.melt(
        housing_bedroom_data,
        id_vars=['house_type'],
        var_name='bedroom_count',
        value_name='count'
    )
    
    # Create the grouped bar chart
    fig_housing_bedroom = px.bar(
        housing_bedroom_melted,
        x='house_type',
        y='count',
        color='bedroom_count',
        title="Housing Types by Number of Bedrooms",
        barmode='group',
        labels={'house_type': 'Housing Type', 'count': 'Count', 'bedroom_count': 'Bedrooms'},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_housing_bedroom, use_container_width=True)
    
    # Housing size by satisfaction level
    st.subheader("Housing Size and Satisfaction")
    
    # Filter records with both area and satisfaction data
    satisfaction_area_data = df[df['area_numerical'].notna() & df['satisfaction_level'].notna()].copy()
    
    # Order the satisfaction levels
    satisfaction_order = ['Very Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Satisfied']
    satisfaction_area_data['satisfaction_level'] = pd.Categorical(
        satisfaction_area_data['satisfaction_level'],
        categories=satisfaction_order,
        ordered=True
    )
    
    # Create box plot of housing area by satisfaction level
    fig_satisfaction_area = px.box(
        satisfaction_area_data,
        x='satisfaction_level',
        y='area_numerical',
        color='satisfaction_level',
        title="Housing Size by Satisfaction Level",
        labels={'area_numerical': 'Area (m²)', 'satisfaction_level': 'Satisfaction Level'},
        category_orders={'satisfaction_level': satisfaction_order},
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_satisfaction_area, use_container_width=True)
    
    # Housing size by household composition
    st.subheader("Housing Size by Household Composition")
    
    # Create a total household size column
    df['household_size'] = df['num-pessoas-nao-dependentes'].fillna(0) + df['num-pessoas-dependentes'].fillna(0)
    df['household_size'] = df['household_size'].astype(int)
    
    # Group household sizes 6 and above
    df['household_size_grouped'] = df['household_size'].apply(lambda x: '6+' if x >= 6 else str(int(x)))
    
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
    
    # Create bar chart of average area by household size
    fig_household_area = px.bar(
        avg_area_by_household,
        x='household_size_grouped',
        y='area_numerical',
        color='household_size_grouped',
        title="Average Housing Size by Household Size",
        labels={'area_numerical': 'Average Area (m²)', 'household_size_grouped': 'Household Size'},
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    st.plotly_chart(fig_household_area, use_container_width=True)