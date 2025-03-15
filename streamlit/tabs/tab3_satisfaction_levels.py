# tab3_satisfaction_levels.py
import streamlit as st
import pandas as pd
import plotly.express as px

def show_satisfaction_levels_tab(df):
    """
    Display the Satisfaction Levels tab with visualizations and filters.
    
    Parameters:
    df (DataFrame): The processed housing data
    """
    st.header("Housing Satisfaction Analysis")
    
    # Overview of satisfaction by housing situation
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Create a heatmap of satisfaction by housing situation
        satisfaction_pivot = pd.crosstab(
            df['housing_situation'], 
            df['satisfaction_level']
        )
        
        # Reorder columns for better visualization
        ordered_cols = ['Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied']
        ordered_cols = [col for col in ordered_cols if col in satisfaction_pivot.columns]
        satisfaction_pivot = satisfaction_pivot[ordered_cols]
        
        fig = px.imshow(
            satisfaction_pivot,
            text_auto=True,
            color_continuous_scale='Blues',
            title='Satisfaction Levels by Housing Situation',
            labels={'x': 'Satisfaction Level', 'y': 'Housing Situation', 'color': 'Count'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig)
    
    with col2:
        # Pie chart of overall satisfaction
        satisfaction_counts = df['satisfaction_level'].value_counts().reset_index()
        satisfaction_counts.columns = ['Satisfaction Level', 'Count']
        
        # Create color map that matches satisfaction level
        color_map = {
            'Very Satisfied': '#1a9850',  # Dark green
            'Satisfied': '#91cf60',      # Light green
            'Neutral': '#ffffbf',        # Yellow
            'Dissatisfied': '#fc8d59',   # Orange
            'Very Dissatisfied': '#d73027'  # Red
        }
        
        fig = px.pie(
            satisfaction_counts, 
            values='Count', 
            names='Satisfaction Level',
            color='Satisfaction Level',
            color_discrete_map=color_map,
            title='Overall Satisfaction Distribution'
        )
        st.plotly_chart(fig)
    
    # Reasons for dissatisfaction
    st.subheader("Common Reasons for Dissatisfaction")
    
    # Extract dissatisfaction reasons
    dissatisfaction_cols = [col for col in df.columns if col.startswith('reason_')]
    reason_mapping = {
        'reason_pago-demasiado': 'Paying too much',
        'reason_falta-espaco': 'Lack of space',
        'reason_habitacao-mau-estado': 'Poor housing condition',
        'reason_vivo-longe': 'Living far from work/amenities',
        'reason_quero-independecia': 'Want independence',
        'reason_dificuldades-financeiras': 'Financial difficulties',
        'reason_financeiramente-dependente': 'Financially dependent',
        'reason_vivo-longe-de-transportes': 'Far from transportation',
        'reason_vivo-zona-insegura': 'Living in unsafe area',
        'reason_partilho-casa-com-desconhecidos': 'Sharing with strangers'
    }
    
    # Calculate frequencies of each reason
    reason_counts = {}
    for col in dissatisfaction_cols:
        if col in reason_mapping:
            reason_counts[reason_mapping[col]] = df[col].sum()
    
    reason_df = pd.DataFrame({
        'Reason': list(reason_counts.keys()),
        'Count': list(reason_counts.values())
    }).sort_values('Count', ascending=False)
    
    # Create horizontal bar chart
    fig = px.bar(
        reason_df,
        y='Reason',
        x='Count',
        orientation='h',
        color='Count',
        color_continuous_scale='Reds',
        title='Reasons for Housing Dissatisfaction'
    )
    st.plotly_chart(fig)
    
    # Interactive filter by satisfaction level
    st.subheader("Explore Demographics by Satisfaction Level")
    
    selected_satisfaction = st.multiselect(
        "Select Satisfaction Levels to Explore",
        options=df['satisfaction_level'].unique(),
        default=df['satisfaction_level'].unique()
    )
    
    if selected_satisfaction:
        filtered_df = df[df['satisfaction_level'].isin(selected_satisfaction)]
    else:
        filtered_df = df
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Satisfaction by income
        income_satisfaction = filtered_df.groupby('rendimento-anual')['satisfaction_level'].value_counts().unstack().fillna(0)
        
        fig = px.bar(
            income_satisfaction,
            barmode='stack',
            title='Satisfaction Levels by Income Bracket',
            labels={'rendimento-anual': 'Annual Income (€)', 'value': 'Count'}
        )
        st.plotly_chart(fig)
    
    with col2:
        # Satisfaction by housing type and size
        housing_type_satisfaction = filtered_df.groupby(['house_type', 'bedroom_count']).size().reset_index(name='count')
        
        fig = px.bar(
            housing_type_satisfaction,
            x='house_type',
            y='count',
            color='bedroom_count',
            title='Housing Types and Sizes',
            barmode='group',
            labels={'house_type': 'Housing Type', 'count': 'Count', 'bedroom_count': 'Number of Bedrooms'}
        )
        st.plotly_chart(fig)
    
    # Correlation between rent burden and satisfaction for renters
    st.subheader("Rent Burden vs. Satisfaction")
    
    renters_df = filtered_df[filtered_df['housing_situation'] == 'Renting']
    if not renters_df.empty:
        rent_satisfaction = pd.crosstab(
            renters_df['rent_burden'], 
            renters_df['satisfaction_level']
        ).reset_index()
        
        # Melt the dataframe for visualization
        rent_satisfaction_melted = pd.melt(
            rent_satisfaction,
            id_vars=['rent_burden'],
            var_name='Satisfaction Level',
            value_name='Count'
        )
        
        # Create an ordered category for rent burden
        rent_burden_order = ['≤30% (Affordable)', '31-50% (Moderate)', '51-80% (High)', '>80% (Very High)', 'Unknown']
        rent_satisfaction_melted['rent_burden'] = pd.Categorical(
            rent_satisfaction_melted['rent_burden'],
            categories=rent_burden_order,
            ordered=True
        )
        
        rent_satisfaction_melted = rent_satisfaction_melted.sort_values('rent_burden')
        
        fig = px.bar(
            rent_satisfaction_melted,
            x='rent_burden',
            y='Count',
            color='Satisfaction Level',
            color_discrete_map=color_map,
            title='Satisfaction Levels by Rent Burden (% of Income)',
            labels={'rent_burden': 'Rent as % of Income'}
        )
        st.plotly_chart(fig)
    else:
        st.write("No rental data available for the selected satisfaction levels.")
    
    # Satisfaction by district - map visualization
    st.subheader("Geographic Distribution of Satisfaction")

    # Define satisfaction weights
    satisfaction_weights = {
        'Very Satisfied': 2,
        'Satisfied': 1,
        'Neutral': 0,
        'Dissatisfied': -1,
        'Very Dissatisfied': -2
    }

    # Convert satisfaction levels to numeric scores
    filtered_df.loc[:, 'satisfaction_numeric'] = filtered_df['satisfaction_level'].map(satisfaction_weights)

    # Calculate mean satisfaction score by district
    district_satisfaction = filtered_df.groupby('distrito')['satisfaction_numeric'].agg(['mean', 'count']).reset_index()
    district_satisfaction = district_satisfaction.rename(columns={'mean': 'satisfaction_score'})

    # Create visualization
    fig = px.bar(
        district_satisfaction,
        x='distrito',
        y='satisfaction_score',
        color='satisfaction_score',
        color_continuous_scale='RdYlGn',
        title='Average Satisfaction Score by District',
        labels={'distrito': 'District', 'satisfaction_score': 'Satisfaction Score (-2 to +2)'},
        hover_data=['count']  # Include count in hover information
    )

    # Improve the layout
    fig.update_layout(
        xaxis_title="District",
        yaxis_title="Satisfaction Score (-2 to +2)",
        yaxis=dict(
            tickmode='linear',
            tick0=-2,
            dtick=0.5,
            range=[-2.1, 2.1]  # Set fixed range for better comparison
        )
    )

    st.plotly_chart(fig)

    # Map visualization using GeoJSON data for Portuguese districts
    st.subheader("Satisfaction Map of Portugal")

    # Load the GeoJSON data
    import json

    # Load the GeoJSON file
    with open('distrito_all_s.geojson', 'r') as f:
        portugal_geojson = json.load(f)

    # Ensure district names match between your dataset and GeoJSON
    # You might need to normalize district names (lowercase, remove accents, etc.)
    district_satisfaction['distrito_normalized'] = district_satisfaction['distrito'].str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    # Create a dictionary for mapping district names from your dataset to GeoJSON
    # This step is necessary if district names don't match exactly
    district_mapping = {
        'viana do castelo': 'viana do castelo',
        'braga': 'braga',
        'vila real': 'vila real',
        'braganca': 'braganca',
        'aveiro': 'aveiro',
        'coimbra': 'coimbra',
        'leiria': 'leiria',
        'lisboa': 'lisboa',
        'porto': 'porto',
        'setubal': 'setubal',
        'viseu': 'viseu',
        'guarda': 'guarda',
        'santarem': 'santarem',
        'beja': 'beja',
        'castelo branco': 'castelo branco',
        'evora': 'evora',
        'faro': 'faro',
        'portalegre': 'portalegre',
        'ilha da madeira': 'madeira',
        'acores': 'acores',
        # Add other districts as needed
    }

    # Create a new column with matched district names
    district_satisfaction['distrito_geojson'] = district_satisfaction['distrito_normalized'].map(district_mapping)

    # Create the choropleth map
    import folium
    from streamlit_folium import folium_static

    # Create a base map centered on Portugal
    m = folium.Map(location=[39.6, -8.0], zoom_start=7)

    # Create the choropleth layer
    folium.Choropleth(
        geo_data=portugal_geojson,
        name='choropleth',
        data=district_satisfaction,
        columns=['distrito_geojson', 'satisfaction_score'],
        key_on='feature.properties.Distrito',  # This should match the district property name in your GeoJSON
        fill_color='RdYlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Satisfaction Score (-2 to +2)',
        highlight=True
    ).add_to(m)

    # Add tooltips to show district name and satisfaction score
    tooltip = folium.features.GeoJsonTooltip(
        fields=['Distrito'],  # Fields from the GeoJSON to display
        aliases=['District:'],  # Labels for the fields
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    )

    # Add the GeoJSON with tooltips to the map
    folium.GeoJson(
        portugal_geojson,
        name='District Info',
        tooltip=tooltip,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.0
        }
    ).add_to(m)

    # Add a layer control
    folium.LayerControl().add_to(m)

    # Display the map
    folium_static(m)

    # Optional: Add a more detailed popup with statistics
    district_satisfaction_dict = district_satisfaction.set_index('distrito_geojson')['satisfaction_score'].to_dict()
    district_count_dict = district_satisfaction.set_index('distrito_geojson')['count'].to_dict()

    # Create a detailed map with custom popups
    m_detailed = folium.Map(location=[39.6, -8.0], zoom_start=7)

    def style_function(feature):
        district_name = feature['properties']['Distrito'].lower()
        try:
            score = district_satisfaction_dict[district_name]
            # Calculate color based on score (-2 to +2)
            # Red for negative, yellow for neutral, green for positive
            if score < -1:
                color = '#d73027'  # Strong red
            elif score < 0:
                color = '#fc8d59'  # Light red
            elif score == 0:
                color = '#fee08b'  # Yellow
            elif score < 1:
                color = '#d9ef8b'  # Light green
            else:
                color = '#91cf60'  # Strong green
        except KeyError:
            color = '#f7f7f7'  # Gray for districts with no data
        
        return {
            'fillColor': color,
            'weight': 1,
            'opacity': 1,
            'color': 'white',
            'dashArray': '3',
            'fillOpacity': 0.7
        }

    def highlight_function(feature):
        return {
            'weight': 3,
            'color': '#666',
            'dashArray': '',
            'fillOpacity': 0.7
        }

    # Create HTML for the popup
    def create_popup_html(district_name):
        try:
            score = district_satisfaction_dict[district_name]
            count = district_count_dict[district_name]
            return f"""
            <div style="width: 200px">
                <h4>{district_name}</h4>
                <p><strong>Satisfaction Score:</strong> {score:.2f}</p>
                <p><strong>Number of Responses:</strong> {count}</p>
            </div>
            """
        except KeyError:
            return f"""
            <div style="width: 200px">
                <h4>{district_name}</h4>
                <p>No data available</p>
            </div>
            """

    # Add GeoJSON with custom popups and styling
    folium.GeoJson(
        portugal_geojson,
        name='Districts',
        style_function=style_function,
        #highlight_function=highlight_function,
        #tooltip=folium.features.GeoJsonTooltip(fields=['Distrito'], aliases=['District:']),
        popup=folium.features.GeoJsonPopup(
            fields=['Distrito'],
            aliases=[''],
            localize=True,
            labels=False,
            style="background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;",
            max_width=300,
        )
    ).add_to(m_detailed)

    # Add a legend
    # legend_html = '''
    # <div style="position: fixed; 
    #     bottom: 50px; right: 50px; width: 180px; height: 180px; 
    #     border:2px solid grey; z-index:9999; font-size:14px; padding: 10px;
    #     background-color: white; border-radius: 5px;">
    #     <p style="margin-bottom: 5px; font-weight: bold;">Satisfaction Score</p>
    #     <div style="display: flex; align-items: center; margin-bottom: 5px;">
    #         <div style="background-color: #d73027; width: 20px; height: 20px; margin-right: 5px;"></div>
    #         <div>Very Negative (-2 to -1)</div>
    #     </div>
    #     <div style="display: flex; align-items: center; margin-bottom: 5px;">
    #         <div style="background-color: #fc8d59; width: 20px; height: 20px; margin-right: 5px;"></div>
    #         <div>Negative (-1 to 0)</div>
    #     </div>
    #     <div style="display: flex; align-items: center; margin-bottom: 5px;">
    #         <div style="background-color: #fee08b; width: 20px; height: 20px; margin-right: 5px;"></div>
    #         <div>Neutral (0)</div>
    #     </div>
    #     <div style="display: flex; align-items: center; margin-bottom: 5px;">
    #         <div style="background-color: #d9ef8b; width: 20px; height: 20px; margin-right: 5px;"></div>
    #         <div>Positive (0 to 1)</div>
    #     </div>
    #     <div style="display: flex; align-items: center;">
    #         <div style="background-color: #91cf60; width: 20px; height: 20px; margin-right: 5px;"></div>
    #         <div>Very Positive (1 to 2)</div>
    #     </div>
    # </div>
    # '''

    # m_detailed.get_root().html.add_child(folium.Element(legend_html))

    # # Display the detailed map
    # st.subheader("Detailed Satisfaction Map with Custom Styling")
    # folium_static(m_detailed)