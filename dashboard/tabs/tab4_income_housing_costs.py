# tab4_income_housing_costs.py
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def show_income_housing_costs_tab(df):
    """
    Display "Income vs Housing Costs" tab with visualizations and filters.

    Parameters:
    df (DataFrame): The processed housing data
    """
    st.header("Income vs Housing Costs Analysis")

    # Rent burden analysis
    st.subheader("Rent Burden Analysis")

    col1, col2 = st.columns([2, 2])

    with col1:
        # Create pie chart of rent burden categories
        rent_data = df[df["housing_situation"] == "Renting"]
        if not rent_data.empty:
            rent_burden_counts = rent_data["rent_burden"].value_counts().reset_index()
            rent_burden_counts.columns = ["Rent Burden", "Count"]

            # Color map for rent burden
            burden_colors = {
                "≤30% (Affordable)": "#109618",  # Green
                "31-50% (Moderate)": "#FFA500",  # Orange
                "51-80% (High)": "#FF4500",  # OrangeRed
                ">80% (Very High)": "#DC143C",  # Crimson
                "Unknown": "#CCCCCC",  # Gray
            }

            fig = px.pie(
                rent_burden_counts,
                values="Count",
                names="Rent Burden",
                color="Rent Burden",
                color_discrete_map=burden_colors,
                title="Distribution of Rent Burden Categories",
            )
            st.plotly_chart(fig)

    with col2:
        # Create scatter plot of income vs rent
        if not rent_data.empty:
            # Ensure 'percentagem-renda-paga' is numeric
            rent_data.loc[:, "percentagem-renda-paga"] = pd.to_numeric(
                rent_data["percentagem-renda-paga"], errors="coerce"
            )

            rent_data = rent_data.dropna(subset=["percentagem-renda-paga"])
            fig = px.scatter(
                rent_data,
                x="rendimento_numerical",
                y="valor-mensal-renda",
                color="rent_burden",
                color_discrete_map=burden_colors,
                size=rent_data["percentagem-renda-paga"].tolist(),
                hover_data=["distrito", "percentagem-renda-paga"],
                title="Monthly Rent vs Income",
                labels={
                    "rendimento_numerical": "Annual Income (€)",
                    "valor-mensal-renda": "Monthly Rent (€)",
                    "rent_burden": "Rent Burden",
                },
            )

            # Add a 30% rent-to-income ratio reference line
            income_range = np.linspace(
                rent_data["rendimento_numerical"].min() or 0,
                rent_data["rendimento_numerical"].max() or 100000,
                100,
            )
            # 30% of monthly income (annual income / 12 * 0.3)
            recommended_rent = income_range / 12 * 0.3

            fig.add_trace(
                go.Scatter(
                    x=income_range,
                    y=recommended_rent,
                    mode="lines",
                    line=dict(color="black", dash="dash"),
                    name="30% Income (Recommended)",
                )
            )

            st.plotly_chart(fig)

    # Income to housing cost comparison
    st.subheader("Income to Housing Cost Comparison")

    # Income distribution by housing situation
    col1, col2 = st.columns([1, 1])

    with col1:
        # Box plot of income by housing situation
        fig = px.box(
            df,
            x="housing_situation",
            y="rendimento_numerical",
            color="housing_situation",
            color_discrete_map={
                "Renting": "#3366CC",
                "Owned": "#109618",
                "Living with others": "#FF9900",
            },
            title="Income Distribution by Housing Situation",
            labels={
                "housing_situation": "Housing Situation",
                "rendimento_numerical": "Annual Income (€)",
            },
        )
        st.plotly_chart(fig)

    with col2:
        # Calculate housing cost to income ratio
        housing_cost_data = df.copy()

        # Calculate monthly housing costs
        housing_cost_data["monthly_housing_cost"] = np.nan

        # For renters, use monthly rent
        renters_mask = housing_cost_data["housing_situation"] == "Renting"
        housing_cost_data.loc[renters_mask, "monthly_housing_cost"] = (
            housing_cost_data.loc[renters_mask, "valor-mensal-renda"]
        )

        # For owners, estimate monthly mortgage payment
        # Assume 25 year mortgage at 3% interest rate (simplified calculation)
        owners_mask = housing_cost_data["housing_situation"] == "Owned"
        # Monthly payment = P * r * (1+r)^n / ((1+r)^n - 1)
        # Where P = principal, r = monthly rate, n = number of payments
        r = 0.03 / 12  # Monthly interest rate
        n = 25 * 12  # Number of payments (25 years)

        # Calculate mortgage factor
        mortgage_factor = r * (1 + r) ** n / ((1 + r) ** n - 1)

        housing_cost_data.loc[owners_mask, "monthly_housing_cost"] = (
            housing_cost_data.loc[owners_mask, "valor-compra"] * mortgage_factor
        )

        # Calculate housing cost to income ratio
        housing_cost_data["monthly_income"] = (
            housing_cost_data["rendimento_numerical"] / 12
        )
        housing_cost_data["housing_cost_ratio"] = (
            housing_cost_data["monthly_housing_cost"]
            / housing_cost_data["monthly_income"]
            * 100
        )

        # Create categories for housing cost ratio
        housing_cost_data["cost_income_category"] = pd.cut(
            housing_cost_data["housing_cost_ratio"],
            bins=[0, 30, 50, 80, float("inf")],
            labels=["≤30%", "31-50%", "51-80%", ">80%"],
        )

        # Bar chart of housing cost to income ratio by situation
        cost_ratio_pivot = pd.crosstab(
            housing_cost_data["housing_situation"],
            housing_cost_data["cost_income_category"],
        ).reset_index()

        cost_ratio_melted = pd.melt(
            cost_ratio_pivot,
            id_vars=["housing_situation"],
            var_name="Cost to Income Ratio",
            value_name="Count",
        )

        fig = px.bar(
            cost_ratio_melted,
            x="housing_situation",
            y="Count",
            color="Cost to Income Ratio",
            title="Housing Cost to Income Ratio by Situation",
            labels={
                "housing_situation": "Housing Situation",
                "Count": "Number of Respondents",
            },
            color_discrete_sequence=["#109618", "#FFA500", "#FF4500", "#DC143C"],
        )
        st.plotly_chart(fig)

    # Rent trends over time
    st.subheader("Rent Affordability Trends")

    col1, col2 = st.columns([1, 1])

    with col1:
        # Extract year from rental start date
        rent_time_data = df[df["housing_situation"] == "Renting"].copy()
        rent_time_data["rental_year"] = (
            rent_time_data["ano-inicio-arrendamento"].astype(float).astype("Int64")
        )

        # Group by year and calculate average rent
        yearly_rent = (
            rent_time_data.groupby("rental_year")["valor-mensal-renda"]
            .mean()
            .reset_index()
        )
        yearly_rent = yearly_rent.sort_values("rental_year")

        fig = px.line(
            yearly_rent,
            x="rental_year",
            y="valor-mensal-renda",
            markers=True,
            title="Average Monthly Rent by Start Year",
            labels={
                "rental_year": "Rental Start Year",
                "valor-mensal-renda": "Average Monthly Rent (€)",
            },
        )
        st.plotly_chart(fig)

    with col2:
        # Calculate rent to income ratio over time
        rent_time_data["rent_income_ratio"] = (
            rent_time_data["valor-mensal-renda"]
            * 12
            / rent_time_data["rendimento_numerical"]
        ) * 100

        yearly_ratio = (
            rent_time_data.groupby("rental_year")["rent_income_ratio"]
            .mean()
            .reset_index()
        )
        yearly_ratio = yearly_ratio.sort_values("rental_year")

        fig = px.line(
            yearly_ratio,
            x="rental_year",
            y="rent_income_ratio",
            markers=True,
            title="Average Rent to Income Ratio by Start Year",
            labels={
                "rental_year": "Rental Start Year",
                "rent_income_ratio": "Rent to Income Ratio (%)",
            },
        )

        # Add a reference line at 30%
        fig.add_hline(
            y=30,
            line_dash="dash",
            line_color="red",
            annotation_text="30% Affordability Threshold",
            annotation_position="bottom right",
        )

        st.plotly_chart(fig)

    # Interactive income simulator
    st.subheader("Housing Affordability Simulator")
    st.markdown("""
    Use this simulator to calculate what housing costs would be affordable based on different income levels.
    The calculator uses the 30% rule: housing costs should not exceed 30% of gross monthly income.
    """)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        income_input = st.number_input(
            "Annual Income (€)", min_value=0, max_value=200000, value=30000, step=1000
        )

    with col2:
        # Calculate monthly income and affordable housing costs
        monthly_income = income_input / 12
        affordable_housing = monthly_income * 0.3

        st.metric("Monthly Income (€)", f"{monthly_income:.2f}")

    with col3:
        st.metric(
            "Affordable Monthly Housing Cost (€)",
            f"{affordable_housing:.2f}",
            delta="30% of income",
        )

    # Compare with market rates
    st.subheader("Compare with Market Rates")

    col1, col2 = st.columns(2)

    with col1:
        # Average rent by district
        district_rent = (
            df[df["housing_situation"] == "Renting"]
            .groupby("distrito")["valor-mensal-renda"]
            .mean()
            .reset_index()
        )
        district_rent.columns = ["District", "Average Rent"]
        district_rent = district_rent.sort_values("Average Rent", ascending=False)

        fig = px.bar(
            district_rent,
            x="District",
            y="Average Rent",
            title="Average Rent by District",
            labels={"Average Rent": "Average Monthly Rent (€)"},
        )

        # Add a line for affordable rent based on input
        fig.add_hline(
            y=affordable_housing,
            line_dash="dash",
            line_color="green",
            annotation_text="Your Affordable Rent",
            annotation_position="top right",
        )

        st.plotly_chart(fig)

    with col2:
        # Calculate affordability index
        district_affordability = district_rent.copy()
        district_affordability["Affordability Index"] = (
            affordable_housing / district_affordability["Average Rent"]
        )
        district_affordability["Affordable"] = (
            district_affordability["Affordability Index"] >= 1
        )
        district_affordability = district_affordability.sort_values(
            "Affordability Index", ascending=False
        )

        fig = px.bar(
            district_affordability,
            x="District",
            y="Affordability Index",
            color="Affordable",
            title="Housing Affordability Index by District",
            labels={"Affordability Index": "Affordability Index (>1 is affordable)"},
            color_discrete_map={True: "green", False: "red"},
        )

        # Add reference line at affordability threshold
        fig.add_hline(
            y=1,
            line_dash="dash",
            line_color="black",
            annotation_text="Affordability Threshold",
            annotation_position="bottom right",
        )

        st.plotly_chart(fig)
