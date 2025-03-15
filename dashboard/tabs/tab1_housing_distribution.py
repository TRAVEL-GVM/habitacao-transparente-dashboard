# tab1_housing_distribution.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))
from config import *


def show_housing_distribution_tab(df):
    """
    Display the Housing Distribution tab with enhanced visualizations, insights, and filters.

    Parameters:
    df (DataFrame): The processed housing data
    """
    st.header("Housing Situation Distribution")

    # Overview explanation
    st.markdown("""
    This section analyzes how Portuguese residents are distributed across different housing situations:
    - **Renting**: People who rent their homes
    - **Owned**: People who own their homes through purchase or inheritance
    - **Living with others**: People living with family or in shared accommodations
    
    The charts below show the overall distribution and how housing situations differ across age groups.
    """)

    col1, col2 = st.columns([1, 1])

    with col1:
        # Calculate percentages for better context
        housing_counts = df["housing_situation"].value_counts().reset_index()
        housing_counts.columns = ["Housing Situation", "Count"]
        total = housing_counts["Count"].sum()
        housing_counts["Percentage"] = (housing_counts["Count"] / total * 100).round(
            1
        ).astype(str) + "%"

        # Create enhanced pie chart with percentages using HOUSING_COLORS
        fig = px.pie(
            housing_counts,
            values="Count",
            names="Housing Situation",
            color="Housing Situation",
            color_discrete_map=HOUSING_COLORS,
            title="Distribution of Housing Situations",
            hover_data=["Percentage"],
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[3],  # White background
            paper_bgcolor=BACKGROUND_COLORS[3],  # White paper
            title_font_color=TEXT_COLORS[0],    # Dark green title
            font_color=TEXT_COLORS[2],          # Medium green text
        )
        st.plotly_chart(fig)

        # Add insights below the chart
        dominant_situation = housing_counts.iloc[housing_counts["Count"].argmax()][
            "Housing Situation"
        ]
        st.markdown(f"""
        **Key Insights:**
        - {dominant_situation} is the most common housing situation in Portugal
        - {housing_counts.iloc[housing_counts["Count"].argmax()]["Percentage"]} of respondents {dominant_situation.lower() if dominant_situation != "Living with others" else "are living with others"}
        """)

    with col2:
        st.subheader("Housing Situation by Age Group")
        # Extract birth year range for age groups and improve labeling
        df["birth_period"] = df["ano_nascimento_interval"].str.extract(r"\[(\d+)")
        df["birth_period"] = pd.to_numeric(df["birth_period"], errors="coerce")

        # Calculate approximate current age (as of 2025)
        df["approx_age"] = 2025 - df["birth_period"]

        df["age_group"] = pd.cut(
            df["birth_period"],
            bins=[1960, 1970, 1980, 1990, 2000, 2025],
            labels=[
                "1960s (~55-65)",
                "1970s (~45-55)",
                "1980s (~35-45)",
                "1990s (~25-35)",
                "2000s+ (<25)",
            ],
        )

        # Pivot table for housing situation by age group
        pivot_data = (
            pd.crosstab(df["age_group"], df["housing_situation"], normalize="index")
            * 100
        )
        pivot_data = pivot_data.round(1).reset_index()
        pivot_data_melted = pd.melt(
            pivot_data,
            id_vars=["age_group"],
            var_name="Housing Situation",
            value_name="Percentage",
        )

        fig = px.bar(
            pivot_data_melted,
            x="age_group",
            y="Percentage",
            color="Housing Situation",
            color_discrete_map=HOUSING_COLORS,  # Use consistent housing colors
            title="Housing Situation by Birth Decade",
            labels={
                "age_group": "Birth Decade (Age Range)",
                "Percentage": "Percentage (%)",
            },
        )
        fig.update_layout(
            xaxis_title="Birth Decade (Approximate Age Range)",
            plot_bgcolor=BACKGROUND_COLORS[0],    # Light green background
            paper_bgcolor=BACKGROUND_COLORS[3],   # White paper
            font_color=TEXT_COLORS[2],           # Medium green text
            title_font_color=TEXT_COLORS[0],     # Dark green title
            legend_title_font_color=TEXT_COLORS[1],  # Dark green legend title
            xaxis=dict(
                tickfont=dict(color=TEXT_COLORS[2]),  # Medium green tick labels
                title_font=dict(color=TEXT_COLORS[1])  # Dark green axis title
            ),
            yaxis=dict(
                tickfont=dict(color=TEXT_COLORS[2]),  # Medium green tick labels
                title_font=dict(color=TEXT_COLORS[1])  # Dark green axis title
            ),
        )
        st.plotly_chart(fig)

        # Add insights about generational differences
        st.markdown("""
        **Generational Trends:**
        - Younger generations (born in 1990s-2000s) show higher rates of renting and living with others
        - Home ownership increases significantly with age, peaking in the older generations
        - These patterns reflect changing economic conditions and housing affordability challenges facing younger Portuguese citizens
        """)

    # Housing situation filters - now with more context
    st.subheader("Explore Housing Situations in Detail")
    st.markdown("""
    Select a specific housing situation below to explore detailed metrics and patterns within that group.
    This allows for deeper analysis of factors affecting different housing situations.
    """)

    selected_situation = st.selectbox(
        "Select Housing Situation to Explore",
        options=["Renting", "Owned", "Living with others", "All"]
    )

    if selected_situation != "All":
        filtered_df = df[df["housing_situation"] == selected_situation]
    else:
        filtered_df = df

    # Display enhanced statistics based on filter
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Count", len(filtered_df))
    with col2:
        avg_birth = filtered_df["birth_period"].mean()
        if not pd.isna(avg_birth):
            st.metric("Average Birth Year", f"{avg_birth:.0f}")
            st.caption(f"Approx. Age: {2025 - avg_birth:.0f}")
    with col3:
        if selected_situation == "Renting":
            avg_rent = filtered_df["valor-mensal-renda"].mean()
            if not pd.isna(avg_rent):
                st.metric("Average Monthly Rent", f"€{avg_rent:.2f}")
        elif selected_situation == "Owned":
            avg_price = filtered_df["valor-compra"].mean()
            if not pd.isna(avg_price):
                st.metric("Average Purchase Price", f"€{avg_price:.2f}")
    with col4:
        if selected_situation != "All":
            try:
                # Average area for the selected housing situation
                avg_area = filtered_df["area_numerical"].mean()
                if not pd.isna(avg_area):
                    st.metric("Average Living Area", f"{avg_area:.0f} m²")
            except Exception:
                pass

    # Additional visualization for the selected housing situation
    if selected_situation != "All":
        st.subheader(f"{selected_situation} - Education Level Distribution")

        # Create education level distribution visualization
        edu_counts = filtered_df["education_level"].value_counts().reset_index()
        edu_counts.columns = ["Education Level", "Count"]

        # Sort education levels by a logical order
        education_order = [
            "Basic",
            "High School",
            "Vocational",
            "Bachelor's",
            "Master's",
            "PhD",
        ]
        edu_counts["Education Level"] = pd.Categorical(
            edu_counts["Education Level"], categories=education_order, ordered=True
        )
        edu_counts = edu_counts.sort_values("Education Level")

        fig = px.bar(
            edu_counts,
            x="Education Level",
            y="Count",
            color="Education Level",
            color_discrete_sequence=PRIMARY_COLORS,  # Use primary color palette
            title=f"Education Level Distribution for {selected_situation}",
        )
        fig.update_layout(
            plot_bgcolor=BACKGROUND_COLORS[0],
            paper_bgcolor=BACKGROUND_COLORS[3],
            showlegend=False  # Hide legend since colors are just for aesthetics
        )
        st.plotly_chart(fig)

        st.markdown(f"""
        This chart shows the education level distribution among people in the "{selected_situation}" housing situation.
        Education level can significantly influence housing choices and opportunities due to its impact on income potential
        and financial stability.
        """)

        # Display financial metrics if available for the housing situation
        if selected_situation == "Renting":
            st.subheader("Rent Burden Analysis")

            # Create donut chart for rent burden categories
            rent_burden_counts = filtered_df["rent_burden"].value_counts().reset_index()
            rent_burden_counts.columns = ["Rent Burden", "Count"]

            fig = px.pie(
                rent_burden_counts,
                values="Count",
                names="Rent Burden",
                title="Distribution of Rent Burden",
                hole=0.4,
                color="Rent Burden",
                color_discrete_map=RENT_BURDEN_COLORS,
            )
            st.plotly_chart(fig)

            st.markdown("""
            **Rent Burden Explanation:**
            - **≤30% (Affordable)**: Housing costs are generally considered affordable when they consume no more than 30% of household income
            - **31-50% (Moderate)**: These households face some financial pressure from housing costs
            - **51-80% (High)**: Housing costs create significant financial strain
            - **>80% (Very High)**: Extreme financial pressure from housing costs
            
            Higher rent burdens often lead to reduced spending on other necessities and difficulty saving for the future.
            """)
