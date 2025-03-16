# tab0_visao_geral.py
import json
import sys
from pathlib import Path

import folium
import plotly.express as px
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))
from config import SATISFACTION_COLORS, HOUSING_COLORS, BACKGROUND_COLORS, TEXT_COLORS


def show_visao_geral_tab(df):
    """
    Display the Overview (Visão Geral) tab with key metrics, interactive map, and affordability simulator.

    Parameters:
    df (DataFrame): The processed housing data
    """

    # Calculate key metrics
    total_responses = len(df)
    ownership_pct = (df["housing_situation"] == "Owned").mean() * 100
    renting_pct = (df["housing_situation"] == "Renting").mean() * 100
    living_with_others_pct = (
        df["housing_situation"] == "Living with others"
    ).mean() * 100

    # Calculate satisfaction score (1-5 scale)
    satisfaction_mapping = {
        "Very Satisfied": 5,
        "Satisfied": 4,
        "Neutral": 3,
        "Dissatisfied": 2,
        "Very Dissatisfied": 1,
    }
    df["satisfaction_score"] = df["satisfaction_level"].map(satisfaction_mapping)
    avg_satisfaction = df["satisfaction_score"].mean()

    # Header and Key Metrics Row with enhanced styling
    st.markdown(
        """
    <style>
    .metric-card {
        background-color: #e8f5e9;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        justify-content: center;
        height: 100%;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #2e7d32;
        margin: 5px 0;
    }
    .metric-label {
        font-size: 16px;
        color: #388e3c;
        margin-bottom: 10px;
    }
    .metric-icon {
        font-size: 32px;
        color: #2e7d32;
        margin-top: 5px;
    }
    .section-divider {
        height: 2px;
        background: linear-gradient(to right, #e8f5e9, #2e7d32, #e8f5e9);
        margin: 30px 0 20px 0;
        border-radius: 2px;
    }    
    .section-divider-space{
        margin: 30px 0 20px 0;
    }
    .header-title {
        color: #2e7d32;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .header-subtitle {
        color: #388e3c; 
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .info-card {
        background-color: #f1f8e9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .info-card-2 {
        background-color: #f1f8e9; 
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 20px; 
        border-left: 4px solid #66bb6a;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.header("Visão Geral da Habitação em Portugal")
    st.markdown(
        """
        <div class="info-card">
            Uma análise das condições habitacionais em Portugal. 
            O índice de satisfação demonstra uma avaliação moderadamente positiva das condições
            habitacionais em Portugal.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-label">Total de Respostas</div>
            <div class="metric-value">{total_responses}</div>
            <div class="metric-icon">👥</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-label">Propriedade</div>
            <div class="metric-value">{ownership_pct:.1f}%</div>
            <div class="metric-icon">🏠</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-label">Arrendamento</div>
            <div class="metric-value">{renting_pct:.1f}%</div>
            <div class="metric-icon">🏢</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-label">Vivendo com Outros</div>
            <div class="metric-value">{living_with_others_pct:.1f}%</div>
            <div class="metric-icon">👪</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-label">Indicador de Satisfação</div>
            <div class="metric-value">{avg_satisfaction:.1f}/5</div>
            <div class="metric-icon">⭐</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Add a styled divider and enhanced text
    st.markdown(
        """
    <div class="section-divider-space"></div>
    """,
        unsafe_allow_html=True,
    )

    # Housing Affordability Simulator
    st.subheader("Simulador de Acessibilidade Habitacional")

    st.markdown(
        """
    <div class="info-card">
        Calcule quanto pode gastar em habitação com base no seu rendimento anual.
        A regra geral é que as despesas com habitação não devem exceder 30% do rendimento bruto mensal.
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Income input
    income_input = st.slider(
        "Rendimento Anual (€)",
        min_value=10000,
        max_value=100000,
        value=30000,
        step=1000,
        format="€%d",
    )

    # Calculate affordability
    monthly_income = income_input / 12
    affordable_housing = monthly_income * 0.3

    # Display results with enhanced styling
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
        <div class="metric-card" style="height: 150px;">
            <div class="metric-label">Rendimento Mensal (€)</div>
            <div class="metric-value">{monthly_income:.2f}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
        <div class="metric-card" style="height: 150px;">
            <div class="metric-label">Custo Habitacional Mensal Recomendado (€)</div>
            <div class="metric-value">{affordable_housing:.2f}</div>
            <div class="metric-label">>30% do rendimento</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Add another section divider
    st.markdown('<div class="section-divider-space"></div>', unsafe_allow_html=True)

    # Interactive Map and KPI Section with enhanced header
    st.subheader("Análise Geográfica e Indicadores")

    # Create two columns: map and KPIs
    map_col, kpi_col = st.columns([6, 4])

    # Initialize session state for selected district
    if "selected_district" not in st.session_state:
        st.session_state.selected_district = "All"

    with map_col:
        # Calculate satisfaction score by district
        district_satisfaction = (
            df.groupby("distrito")["satisfaction_score"]
            .agg(["mean", "count"])
            .reset_index()
        )
        district_satisfaction = district_satisfaction.rename(
            columns={"mean": "satisfaction_score"}
        )

        try:
            # Load GeoJSON data for Portugal
            with open("distrito_all_s.geojson", "r") as f:
                portugal_geojson = json.load(f)

            # Normalize district names for matching
            district_satisfaction["distrito_normalized"] = (
                district_satisfaction["distrito"]
                .str.lower()
                .str.normalize("NFKD")
                .str.encode("ascii", errors="ignore")
                .str.decode("utf-8")
            )

            # Mapping of district names between datasets
            district_mapping = {
                "viana do castelo": "viana do castelo",
                "braga": "braga",
                "vila real": "vila real",
                "braganca": "braganca",
                "aveiro": "aveiro",
                "coimbra": "coimbra",
                "leiria": "leiria",
                "lisboa": "lisboa",
                "porto": "porto",
                "setubal": "setubal",
                "viseu": "viseu",
                "guarda": "guarda",
                "santarem": "santarem",
                "beja": "beja",
                "castelo branco": "castelo branco",
                "evora": "evora",
                "faro": "faro",
                "portalegre": "portalegre",
                "ilha da madeira": "madeira",
                "acores": "acores",
            }

            # Create a new column with matched district names
            district_satisfaction["distrito_geojson"] = district_satisfaction[
                "distrito_normalized"
            ].map(district_mapping)

            # Convert to dictionaries for easier access
            district_satisfaction_dict = district_satisfaction.set_index(
                "distrito_geojson"
            )["satisfaction_score"].to_dict()
            district_count_dict = district_satisfaction.set_index("distrito_geojson")[
                "count"
            ].to_dict()

            # Create map centered on Portugal
            m = folium.Map(
                location=[39.6, -8.0],
                zoom_start=6,
                tiles="CartoDB Positron",
                control_scale=True,
            )

            # Add title to the map
            title_html = """
                <div style="position: fixed; 
                            top: 10px; left: 50px; width: 300px; height: 30px; 
                            background-color: rgba(255, 255, 255, 0.8);
                            border-radius: 5px; 
                            font-size: 16pt; font-weight: bold;
                            text-align: center;
                            padding: 5px;
                            z-index: 9999;">
                    Satisfação Habitacional em Portugal
                </div>
                """
            m.get_root().html.add_child(folium.Element(title_html))

            # Style function for the GeoJSON
            def style_function(feature):
                district_name = feature["properties"]["Distrito"].lower()
                try:
                    score = district_satisfaction_dict[district_name]
                    if score < 1.5:
                        color = SATISFACTION_COLORS["Very Dissatisfied"]
                    elif score < 2.5:
                        color = SATISFACTION_COLORS["Dissatisfied"]
                    elif score < 3.5:
                        color = SATISFACTION_COLORS["Neutral"]
                    elif score < 4.5:
                        color = SATISFACTION_COLORS["Satisfied"]
                    else:
                        color = SATISFACTION_COLORS["Very Satisfied"]
                except KeyError:
                    color = "#f7f7f7"  # Gray for no data
                return {
                    "fillColor": color,
                    "weight": 1.5,
                    "opacity": 1,
                    "color": "white",
                    "dashArray": "",
                    "fillOpacity": 0.7,
                }

            # Highlight function
            def highlight_function(feature):
                return {
                    "weight": 3,
                    "color": "#666",
                    "dashArray": "",
                    "fillOpacity": 0.9,
                }

            # Add GeoJSON layer
            geojson = folium.GeoJson(
                portugal_geojson,
                name="Satisfaction by District",
                style_function=style_function,
                highlight_function=highlight_function,
                tooltip=folium.features.GeoJsonTooltip(
                    fields=["Distrito"],
                    aliases=["District:"],
                    style="background-color: white; color: #333333; font-weight: bold; font-family: Arial; font-size: 12px; padding: 10px; border-radius: 3px; box-shadow: 3px 3px 10px rgba(0,0,0,0.2);",
                ),
            )
            geojson.add_to(m)

            # Add custom popups with satisfaction data and click event
            for feature in portugal_geojson["features"]:
                district_name = feature["properties"]["Distrito"].lower()
                if district_name in district_satisfaction_dict:
                    score = district_satisfaction_dict[district_name]
                    count = district_count_dict[district_name]

                    # Get additional information for the district
                    district_data = df[df["distrito"].str.lower() == district_name]

                    # Calculate rent average, handling potential NaN values
                    avg_rent = district_data[
                        (district_data["housing_situation"] == "Renting")
                        & (district_data["valor-mensal-renda"].notna())
                    ]["valor-mensal-renda"].mean()

                    # Calculate purchase average, handling potential NaN values
                    avg_purchase = district_data[
                        (district_data["housing_situation"] == "Owned")
                        & (district_data["valor-compra"].notna())
                    ]["valor-compra"].mean()

                    # Calculate percentage of high rent burden, handling edge cases
                    rent_data = district_data[
                        district_data["housing_situation"] == "Renting"
                    ]
                    high_burden_pct = 0
                    if len(rent_data) > 0:
                        high_burden_pct = (
                            rent_data["rent_burden"]
                            .isin(["51-80% (High)", ">80% (Very High)"])
                            .mean()
                            * 100
                        )

                    def create_popup_html(
                        district_name,
                        score,
                        count,
                        avg_rent,
                        avg_purchase,
                        high_burden_pct,
                    ):
                        """Create an HTML popup with styled district information."""
                        # Determine satisfaction description and color based on score
                        if score >= 4.5:
                            description = "Muito Alta Satisfação"
                            color = "#2e7d32"
                        elif score >= 3.5:
                            description = "Alta Satisfação"
                            color = "#66bb6a"
                        elif score >= 2.5:
                            description = "Satisfação Média"
                            color = "#ffeb3b"
                        elif score >= 1.5:
                            description = "Baixa Satisfação"
                            color = "#fc8d59"
                        else:
                            description = "Muito Baixa Satisfação"
                            color = "#d73027"

                        # Format monetary values with thousands separator
                        avg_rent_formatted = (
                            f"{avg_rent:,.2f}".replace(",", "X")
                            .replace(".", ",")
                            .replace("X", ".")
                        )
                        avg_purchase_formatted = (
                            f"{avg_purchase:,.2f}".replace(",", "X")
                            .replace(".", ",")
                            .replace("X", ".")
                        )

                        html = f"""
                        <div style="font-family: Arial, sans-serif; padding: 10px; min-width: 200px;">
                            <h3 style="margin-top: 0; margin-bottom: 10px; color: #333; border-bottom: 2px solid {color};">
                                {district_name.capitalize()}
                            </h3>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-weight: bold;">Satisfação:</span>
                                <span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 10px;">
                                    {score:.2f}
                                </span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-weight: bold;">Status:</span>
                                <span>{description}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-weight: bold;">Renda Média:</span>
                                <span>€{avg_rent_formatted}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-weight: bold;">Preço Compra Médio:</span>
                                <span>€{avg_purchase_formatted}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-weight: bold;">Sobrecarga:</span>
                                <span>{high_burden_pct:.1f}%</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="font-weight: bold;">Respostas:</span>
                                <span>{count}</span>
                            </div>
                        </div>
                        """
                        return html

                    # Get coordinates for the popup (center of polygon)
                    coords = feature["geometry"]["coordinates"]
                    if feature["geometry"]["type"] == "Polygon":
                        # Calculate centroid of first polygon
                        lat_points = [point[1] for point in coords[0]]
                        lng_points = [point[0] for point in coords[0]]
                        center_lat = sum(lat_points) / len(lat_points)
                        center_lng = sum(lng_points) / len(lng_points)
                    else:  # MultiPolygon
                        # Take the center of the first polygon in the multipolygon
                        lat_points = [point[1] for point in coords[0][0]]
                        lng_points = [point[0] for point in coords[0][0]]
                        center_lat = sum(lat_points) / len(lat_points)
                        center_lng = sum(lng_points) / len(lng_points)

                    # Add a circle marker with popup
                    folium.CircleMarker(
                        location=[center_lat, center_lng],
                        radius=5,
                        color="#333333",
                        fill=True,
                        fill_color="#333333",
                        fill_opacity=0.7,
                        popup=folium.Popup(
                            html=create_popup_html(
                                district_name,
                                score,
                                count,
                                avg_rent if not pd.isna(avg_rent) else 0,
                                avg_purchase if not pd.isna(avg_purchase) else 0,
                                high_burden_pct,
                            ),
                            max_width=300,
                        ),
                    ).add_to(m)

            # Custom legend for satisfaction levels
            legend_html = """
                <div style="position: fixed; 
                            bottom: 10px; right: 10px; 
                            border-radius: 5px; 
                            background-color: rgba(255, 255, 255, 0.8);
                            z-index: 9999; font-size:12px;
                            padding: 5px; ">
                    <div style="text-align: center; margin-bottom: 5px; font-weight: bold;">Nível de Satisfação</div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background-color: #2e7d32; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Muito Alto (4.5 a 5.0)
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background-color: #66bb6a; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Alto (3.5 a 4.5)
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background-color: #ffeb3b; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Médio (2.5 a 3.5)
                    </div>
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="background-color: #ff9800; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Baixo (1.5 a 2.5)
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="background-color: #f44336; width: 20px; height: 20px; margin-right: 5px; solid #ccc;"></div>Muito Baixo (1.0 a 1.5)
                    </div>
                </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))

            # Add fullscreen button
            folium.plugins.Fullscreen(
                position="topleft",
                title="Expand map",
                title_cancel="Exit fullscreen",
                force_separate_button=True,
            ).add_to(m)

            # Display the map
            folium_static(m)

        except Exception as e:
            st.error(f"Error loading or processing the map: {e}")
            st.info(
                "Please ensure the GeoJSON file 'distrito_all_s.geojson' is available in the application directory."
            )
            # Fallback district selector
            st.session_state.selected_district = st.selectbox(
                "Selecione um distrito",
                ["All"] + sorted(df["distrito"].unique().tolist()),
                index=0,
            )
        # Note for users about the map
        st.markdown(
            """
            <div class="info-card">
                ℹ️ Clique nos pontos do mapa para ver detalhes por distrito.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_col:
        st.text("")
        # District selection without form - use selectbox instead
        st.write("Selecione um distrito:")
        st.session_state.selected_district = st.selectbox(
            "Selecione um distrito",
            ["All"] + sorted([d.capitalize() for d in district_mapping.keys()]),
            index=0,
            key="district_selector",
            label_visibility="collapsed",
        )

        # Filter data based on selected district
        if (
            st.session_state.selected_district
            and st.session_state.selected_district != "All"
        ):
            filtered_df = df[
                df["distrito"].str.lower() == st.session_state.selected_district.lower()
            ]
            region_title = st.session_state.selected_district.capitalize()
        else:
            filtered_df = df
            region_title = "Todo o País"

        # Calculate KPIs for the selected region
        avg_satisfaction = filtered_df["satisfaction_score"].mean()
        avg_rent = filtered_df[filtered_df["housing_situation"] == "Renting"][
            "valor-mensal-renda"
        ].mean()
        avg_purchase = filtered_df[filtered_df["housing_situation"] == "Owned"][
            "valor-compra"
        ].mean()

        # Rent burden percentage
        rent_burden_data = filtered_df[filtered_df["housing_situation"] == "Renting"]
        high_burden_pct = (
            rent_burden_data[
                rent_burden_data["rent_burden"].isin(
                    ["51-80% (High)", ">80% (Very High)"]
                )
            ].shape[0]
            / rent_burden_data.shape[0]
            * 100
            if not rent_burden_data.empty
            else 0
        )

        # Housing distribution donut chart
        housing_counts = filtered_df["housing_situation"].value_counts().reset_index()
        housing_counts.columns = ["Housing Situation", "Count"]

        fig = px.pie(
            housing_counts,
            values="Count",
            names="Housing Situation",
            color="Housing Situation",
            hole=0.6,
            color_discrete_map=HOUSING_COLORS,
            title="Distribuição Habitacional",
        )
        fig.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor=BACKGROUND_COLORS[3],
            font_color=TEXT_COLORS[2],
            title_font_color=TEXT_COLORS[0],
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Create an integrated KPI summary card with text that incorporates all values
        burden_severity = (
            "alta"
            if high_burden_pct > 40
            else "moderada"
            if high_burden_pct > 20
            else "baixa"
        )
        satisfaction_level = (
            "alta"
            if avg_satisfaction >= 4
            else "moderada"
            if avg_satisfaction >= 3
            else "baixa"
        )

        # Format rent and purchase prices with thousands separator
        avg_rent_formatted = (
            f"{avg_rent:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        avg_purchase_formatted = (
            f"{avg_purchase:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        # First paragraph
        st.markdown(
            f"""
        <p style="color: #333; line-height: 1.6; text-align: justify; margin-bottom: 15px;">
            Em <strong>{region_title}</strong>, a satisfação média com a habitação é <strong>{avg_satisfaction:.1f}/5</strong>, 
            considerada <strong>{satisfaction_level}</strong>. O preço médio de compra é de <strong>€{avg_purchase_formatted}</strong>, 
            enquanto o valor médio de arrendamento é de <strong>€{avg_rent_formatted}</strong> mensais.
        </p>
        """,
            unsafe_allow_html=True,
        )

        # Second paragraph
        st.markdown(
            f"""
        <p style="color: #333; line-height: 1.6; text-align: justify;">
            <strong>{high_burden_pct:.1f}%</strong> das pessoas em situação de arrendamento apresentam sobrecarga 
            habitacional, o que representa uma percentagem <strong>{burden_severity}</strong> de
            pessoas gastando mais de 50% do rendimento em habitação.
        </p>
        """,
            unsafe_allow_html=True,
        )

        # Close the main container
        st.markdown("</div>", unsafe_allow_html=True)
