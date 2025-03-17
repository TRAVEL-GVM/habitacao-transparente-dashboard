# tab7_exploratory_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy import stats

def show_exploratory_analysis_tab(df):
    st.header("Exploratory Data Analysis")

    # Explain what is the purpose of this tab

    st.markdown(
        """
        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 10px;">
            This tab allows you to explore the dataset and generate charts based on the data. 
            You can filter the data based on different columns and generate charts automatically. 
            The charts are generated based on the data and can provide insights into the distribution and relationships between different variables.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Data Filtering")

    # Create three columns for the controls
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # Housing situation filter
        if "housing_situation" in df.columns:
            housing_options = ["All"] + sorted(
                df["housing_situation"].dropna().unique().tolist()
            )
            selected_housing = st.selectbox("Housing Situation", housing_options)

        # Region filter
        if "distrito" in df.columns:
            district_options = ["All"] + sorted(
                df["distrito"].dropna().unique().tolist()
            )
            selected_district = st.selectbox("District", district_options)

    with col2:
        # Income filter
        if "rendimento_clean" in df.columns:
            income_options = ["All"] + sorted(
                df["rendimento_clean"].dropna().unique().tolist()
            )
            selected_income = st.selectbox("Income Bracket", income_options)

        # Satisfaction filter
        if "satisfaction_level" in df.columns:
            satisfaction_options = ["All"] + sorted(
                df["satisfaction_level"].dropna().unique().tolist()
            )
            selected_satisfaction = st.selectbox(
                "Satisfaction Level", satisfaction_options
            )

    with col3:
        # House type filter
        if "house_type" in df.columns:
            house_type_options = ["All"] + sorted(
                df["house_type"].dropna().unique().tolist()
            )
            selected_house_type = st.selectbox("House Type", house_type_options)

        # Education level filter
        if "education_level" in df.columns:
            education_options = ["All"] + sorted(
                df["education_level"].dropna().unique().tolist()
            )
            selected_education = st.selectbox("Education Level", education_options)

    # Apply filters to the dataframe
    filtered_df = df.copy()

    if "housing_situation" in df.columns and selected_housing != "All":
        filtered_df = filtered_df[filtered_df["housing_situation"] == selected_housing]

    if "distrito" in df.columns and selected_district != "All":
        filtered_df = filtered_df[filtered_df["distrito"] == selected_district]

    if "rendimento_clean" in df.columns and selected_income != "All":
        filtered_df = filtered_df[filtered_df["rendimento_clean"] == selected_income]

    if "satisfaction_level" in df.columns and selected_satisfaction != "All":
        filtered_df = filtered_df[
            filtered_df["satisfaction_level"] == selected_satisfaction
        ]

    if "house_type" in df.columns and selected_house_type != "All":
        filtered_df = filtered_df[filtered_df["house_type"] == selected_house_type]

    if "education_level" in df.columns and selected_education != "All":
        filtered_df = filtered_df[filtered_df["education_level"] == selected_education]

    # Show filtered data count
    st.write(f"Showing {len(filtered_df)} of {len(df)} records")

    # Show dataframe with filtered data
    with st.expander("View Data", expanded=False):
        st.dataframe(filtered_df, use_container_width=True)

    # Auto chart generation section
    st.subheader("Automatic Chart Generation")

    # Create two columns for chart controls
    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        # Select chart type
        chart_type = st.selectbox(
            "Chart Type",
            ["Bar Chart", "Histogram", "Scatter Plot", "Box Plot", "Pie Chart"],
        )

        # Get numeric and categorical columns for axis selection
        numeric_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = filtered_df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        # Remove complex list columns
        categorical_cols = [
            col
            for col in categorical_cols
            if not any(filtered_df[col].astype(str).str.contains("\[", na=False))
        ]

        # Add cleaned columns that might be useful
        for col in [
            "housing_situation",
            "satisfaction_level",
            "house_type",
            "education_level",
            "employment_status",
            "rendimento_clean",
            "bedroom_count",
        ]:
            if col in filtered_df.columns and col not in categorical_cols:
                categorical_cols.append(col)

    with chart_col2:
        # Dynamic options based on chart type
        if chart_type == "Bar Chart":
            x_axis = st.selectbox("X-Axis (Category)", categorical_cols)
            agg_option = st.selectbox("Aggregation", ["Count", "Mean", "Sum", "Median"])

            if agg_option != "Count":
                y_axis = st.selectbox("Y-Axis (Numeric)", numeric_cols)
            else:
                y_axis = None

        elif chart_type == "Histogram":
            x_axis = st.selectbox("X-Axis (Numeric)", numeric_cols)
            bins = st.slider("Number of Bins", min_value=5, max_value=50, value=20)
            y_axis = None

        elif chart_type == "Scatter Plot":
            x_axis = st.selectbox("X-Axis (Numeric)", numeric_cols)
            y_axis = st.selectbox("Y-Axis (Numeric)", numeric_cols)
            color_option = st.selectbox("Color By", ["None"] + categorical_cols)
            if color_option == "None":
                color_option = None

        elif chart_type == "Box Plot":
            x_axis = st.selectbox("X-Axis (Category)", categorical_cols)
            y_axis = st.selectbox("Y-Axis (Numeric)", numeric_cols)

        else:  # Pie Chart
            x_axis = st.selectbox("Category", categorical_cols)
            y_axis = None

    # Generate the chart
    if len(filtered_df) > 0:
        st.subheader("Generated Chart")

        if chart_type == "Bar Chart":
            if agg_option == "Count":
                # Fix for the bar chart - Create proper dataframe for value counts
                value_counts = filtered_df[x_axis].value_counts().reset_index()
                value_counts.columns = [x_axis, "count"]  # Properly rename columns

                fig = px.bar(
                    value_counts,
                    x=x_axis,  # Use the actual column name, not 'index'
                    y="count",
                    title=f"Count of {x_axis}",
                    labels={x_axis: x_axis, "count": "Count"},
                )
            else:
                agg_func = {"mean": np.mean, "sum": np.sum, "median": np.median}[
                    agg_option.lower()
                ]
                agg_data = (
                    filtered_df.groupby(x_axis)[y_axis].agg(agg_func).reset_index()
                )
                fig = px.bar(
                    agg_data,
                    x=x_axis,
                    y=y_axis,
                    title=f"{agg_option} of {y_axis} by {x_axis}",
                )

        elif chart_type == "Histogram":
            fig = px.histogram(
                filtered_df, x=x_axis, nbins=bins, title=f"Distribution of {x_axis}"
            )

        elif chart_type == "Scatter Plot":
            fig = px.scatter(
                filtered_df,
                x=x_axis,
                y=y_axis,
                color=color_option,
                title=f"{y_axis} vs {x_axis}",
            )

        elif chart_type == "Box Plot":
            fig = px.box(
                filtered_df,
                x=x_axis,
                y=y_axis,
                title=f"Distribution of {y_axis} by {x_axis}",
            )

        else:  # Pie Chart
            value_counts = filtered_df[x_axis].value_counts()
            fig = px.pie(
                names=value_counts.index,
                values=value_counts.values,
                title=f"Distribution of {x_axis}",
            )

        # Show the generated chart
        st.plotly_chart(fig, use_container_width=True)

        # Add chart description
        with st.expander("Chart Insights", expanded=False):
            if chart_type == "Bar Chart":
                if agg_option == "Count":
                    most_common = filtered_df[x_axis].value_counts().idxmax()
                    pct = (
                        filtered_df[x_axis].value_counts().max() / len(filtered_df)
                    ) * 100
                    st.write(
                        f"- Most common {x_axis}: {most_common} ({pct:.1f}% of data)"
                    )
                    st.write(
                        f"- Number of unique {x_axis} values: {filtered_df[x_axis].nunique()}"
                    )
                else:
                    agg_data = filtered_df.groupby(x_axis)[y_axis].agg(agg_func)
                    max_category = agg_data.idxmax()
                    min_category = agg_data.idxmin()
                    st.write(
                        f"- Highest {y_axis} ({agg_option}): {max_category} with {agg_data.max():.2f}"
                    )
                    st.write(
                        f"- Lowest {y_axis} ({agg_option}): {min_category} with {agg_data.min():.2f}"
                    )

            elif chart_type == "Histogram":
                st.write(f"- Average value: {filtered_df[x_axis].mean():.2f}")
                st.write(f"- Median value: {filtered_df[x_axis].median():.2f}")
                st.write(
                    f"- Range: {filtered_df[x_axis].min():.2f} to {filtered_df[x_axis].max():.2f}"
                )

            elif chart_type == "Scatter Plot":
                corr = filtered_df[[x_axis, y_axis]].corr().iloc[0, 1]
                st.write(f"- Correlation between {x_axis} and {y_axis}: {corr:.2f}")
                if abs(corr) > 0.7:
                    st.write("- Strong correlation detected")
                elif abs(corr) > 0.3:
                    st.write("- Moderate correlation detected")
                else:
                    st.write("- Weak correlation detected")

            elif chart_type == "Box Plot":
                grouped = filtered_df.groupby(x_axis)[y_axis]
                st.write(
                    f"- Category with highest median {y_axis}: {grouped.median().idxmax()}"
                )
                st.write(
                    f"- Category with lowest median {y_axis}: {grouped.median().idxmin()}"
                )
                st.write(f"- Category with most variability: {grouped.std().idxmax()}")

            else:  # Pie Chart
                most_common = filtered_df[x_axis].value_counts().idxmax()
                pct = (
                    filtered_df[x_axis].value_counts().max() / len(filtered_df)
                ) * 100
                st.write(f"- Most common {x_axis}: {most_common} ({pct:.1f}% of data)")
                st.write(f"- Number of categories: {filtered_df[x_axis].nunique()}")
    else:
        st.warning(
            "No data available with current filters. Please adjust your filters."
        )

    # Statistical summary section
    st.subheader("Statistical Summary")

    # Select columns for summary
    summary_cols = st.multiselect(
        "Select columns for summary statistics",
        numeric_cols,
        default=numeric_cols[:3] if len(numeric_cols) > 3 else numeric_cols,
    )

    if summary_cols:
        st.dataframe(filtered_df[summary_cols].describe(), use_container_width=True)

    # Correlation matrix
    if len(numeric_cols) > 1:
        with st.expander("Correlation Matrix", expanded=False):
            corr_cols = st.multiselect(
                "Select columns for correlation analysis",
                numeric_cols,
                default=numeric_cols[:5] if len(numeric_cols) > 5 else numeric_cols,
            )

            if corr_cols and len(corr_cols) > 1:
                corr_matrix = filtered_df[corr_cols].corr()

                # Create a heatmap for the correlation matrix
                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    color_continuous_scale="RdBu_r",
                    title="Correlation Matrix",
                )
                st.plotly_chart(fig, use_container_width=True)

                # Find the strongest correlations
                corr_pairs = []
                for i in range(len(corr_cols)):
                    for j in range(i + 1, len(corr_cols)):
                        corr_value = corr_matrix.iloc[i, j]
                        corr_pairs.append((corr_cols[i], corr_cols[j], corr_value))

                # Sort by absolute correlation value and show the top 5
                corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)

                st.write("Strongest correlations:")
                for col1, col2, corr in corr_pairs[:5]:
                    st.write(f"- {col1} and {col2}: {corr:.2f}")

    # Trend Analysis Section
    st.subheader("Trend Analysis")

    # Identify potential time-based columns
    time_columns = []
    for col in df.columns:
        if any(time_term in col.lower() for time_term in ['ano', 'year', 'date', 'time', 'period']):
            if col in filtered_df.columns:
                time_columns.append(col)

    # Check if we have any time-based columns
    if not time_columns:
        st.info("No time-based columns detected for trend analysis. Common time columns include those with 'ano', 'year', 'date', or 'time' in their names.")
    else:
        # Time column selection
        time_col = st.selectbox("Select Time Column", time_columns, index=time_columns.index("ano-compra") if "ano-compra" in time_columns else 0)
        
        # Variable selection
        trend_var_options = numeric_cols + categorical_cols
        trend_var = st.selectbox("Select Variable to Analyze", trend_var_options, index=trend_var_options.index("valor-compra") if "valor-compra" in trend_var_options else 0)
        
        # Analysis type selection
        analysis_type = st.radio(
            "Analysis Type",
            ["Time Series", "Year-over-Year Comparison", "Distribution Over Time"]
        )
        
        # Prepare data for analysis
        if time_col in filtered_df.columns and trend_var in filtered_df.columns:
            # Check if the time column is numeric (like years)
            if pd.api.types.is_numeric_dtype(filtered_df[time_col]):
                # For numeric time columns, like years
                has_valid_data = not filtered_df[time_col].isna().all() and not filtered_df[trend_var].isna().all()
                
                if has_valid_data:
                    # Sort data by time column
                    trend_data = filtered_df.sort_values(by=time_col)
                    
                    if analysis_type == "Time Series":
                        if pd.api.types.is_numeric_dtype(filtered_df[trend_var]):
                            # For numeric variables, calculate average per time period
                            agg_data = trend_data.groupby(time_col)[trend_var].agg(['mean', 'median', 'count']).reset_index()
                            
                            # Create time series plot
                            fig = px.line(
                                agg_data,
                                x=time_col,
                                y='mean',
                                title=f"Average {trend_var} Over Time",
                                labels={time_col: time_col, 'mean': f'Average {trend_var}'}
                            )
                            # Add confidence interval
                            fig.add_scatter(
                                x=agg_data[time_col],
                                y=agg_data['median'],
                                mode='lines',
                                line=dict(dash='dash', color='red'),
                                name='Median'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show data points count
                            st.write(f"Total data points: {len(trend_data)}")
                            
                            # Show key statistics
                            earliest = trend_data[time_col].min()
                            latest = trend_data[time_col].max()
                            earliest_avg = trend_data[trend_data[time_col] == earliest][trend_var].mean()
                            latest_avg = trend_data[trend_data[time_col] == latest][trend_var].mean()
                            
                            # Calculate overall change
                            change = latest_avg - earliest_avg
                            percent_change = (change / earliest_avg) * 100 if earliest_avg != 0 else 0
                            
                            st.write(f"From {earliest} to {latest}, {trend_var} changed by {change:.2f} ({percent_change:.1f}%)")
                            
                            # Trend analysis
                            if len(agg_data) > 1:
                                # Simple linear regression to determine trend
                                
                                x = agg_data[time_col].values
                                y = agg_data['mean'].values
                                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                                
                                trend_direction = "upward" if slope > 0 else "downward"
                                trend_strength = "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.3 else "weak"
                                
                                st.write(f"The data shows a {trend_strength} {trend_direction} trend (r² = {r_value**2:.2f})")
                        else:
                            # For categorical variables, show distribution over time
                            st.info(f"Selected variable '{trend_var}' is categorical. Showing distribution over time instead.")
                            
                            # Create a crosstab of time vs. category
                            crosstab = pd.crosstab(trend_data[time_col], trend_data[trend_var], normalize='index')
                            crosstab_long = crosstab.reset_index().melt(id_vars=[time_col])
                            
                            fig = px.area(
                                crosstab_long,
                                x=time_col,
                                y='value',
                                color='variable',
                                title=f"Distribution of {trend_var} Over Time",
                                labels={'value': 'Percentage', 'variable': trend_var}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    elif analysis_type == "Year-over-Year Comparison":
                        if pd.api.types.is_numeric_dtype(filtered_df[trend_var]):
                            # Get unique years/time periods
                            time_periods = sorted(filtered_df[time_col].unique())
                            
                            if len(time_periods) > 1:
                                # Calculate year-over-year change
                                yoy_data = []
                                for i in range(1, len(time_periods)):
                                    current_period = time_periods[i]
                                    previous_period = time_periods[i-1]
                                    
                                    current_avg = filtered_df[filtered_df[time_col] == current_period][trend_var].mean()
                                    previous_avg = filtered_df[filtered_df[time_col] == previous_period][trend_var].mean()
                                    
                                    change = current_avg - previous_avg
                                    pct_change = (change / previous_avg) * 100 if previous_avg != 0 else 0
                                    
                                    yoy_data.append({
                                        'Period': f"{previous_period} to {current_period}",
                                        'Change': change,
                                        'Percent_Change': pct_change
                                    })
                                
                                # Create dataframe for visualization
                                yoy_df = pd.DataFrame(yoy_data)
                                
                                # Create bar chart of changes
                                fig = px.bar(
                                    yoy_df,
                                    x='Period',
                                    y='Percent_Change',
                                    title=f"Year-over-Year Change in {trend_var}",
                                    labels={'Percent_Change': 'Percent Change (%)'}
                                )
                                
                                # Add color based on positive/negative change
                                fig.update_traces(marker_color=yoy_df['Percent_Change'].apply(
                                    lambda x: 'green' if x > 0 else 'red'
                                ))
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Show statistics
                                avg_change = yoy_df['Percent_Change'].mean()
                                max_change = yoy_df.loc[yoy_df['Percent_Change'].idxmax()]
                                min_change = yoy_df.loc[yoy_df['Percent_Change'].idxmin()]
                                
                                st.write(f"Average year-over-year change: {avg_change:.1f}%")
                                st.write(f"Largest increase: {max_change['Period']} ({max_change['Percent_Change']:.1f}%)")
                                st.write(f"Largest decrease: {min_change['Period']} ({min_change['Percent_Change']:.1f}%)")
                            else:
                                st.warning(f"Need at least two time periods for year-over-year comparison. Currently only have data for {time_periods[0]}.")
                        else:
                            st.info(f"Year-over-Year comparison requires numeric data. '{trend_var}' is categorical.")
                    
                    elif analysis_type == "Distribution Over Time":
                        # Create a box plot showing distribution of the variable over time
                        fig = px.box(
                            trend_data,
                            x=time_col,
                            y=trend_var if pd.api.types.is_numeric_dtype(filtered_df[trend_var]) else None,
                            color=time_col,
                            title=f"Distribution of {trend_var} Over Time",
                            notched=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Distribution statistics
                        with st.expander("Distribution Statistics", expanded=False):
                            dist_stats = trend_data.groupby(time_col)[trend_var].describe() if pd.api.types.is_numeric_dtype(filtered_df[trend_var]) else None
                            
                            if dist_stats is not None:
                                st.dataframe(dist_stats, use_container_width=True)
                                
                                # Variance over time
                                variance_over_time = trend_data.groupby(time_col)[trend_var].var().reset_index()
                                
                                fig_var = px.line(
                                    variance_over_time,
                                    x=time_col,
                                    y=trend_var,
                                    title=f"Variance in {trend_var} Over Time",
                                    markers=True
                                )
                                st.plotly_chart(fig_var, use_container_width=True)
                                
                                # Check if variance is increasing or decreasing
                                if len(variance_over_time) > 1:
                                    first_var = variance_over_time[trend_var].iloc[0]
                                    last_var = variance_over_time[trend_var].iloc[-1]
                                    
                                    if last_var > first_var:
                                        st.write(f"Variability in {trend_var} has increased over time.")
                                    else:
                                        st.write(f"Variability in {trend_var} has decreased over time.")
                            else:
                                # For categorical variables, show frequency distribution
                                freq_dist = pd.crosstab(trend_data[time_col], trend_data[trend_var])
                                st.dataframe(freq_dist, use_container_width=True)
                else:
                    st.warning("Selected columns contain no valid data for trend analysis.")
            else:
                st.info(f"The selected time column '{time_col}' is not numeric. Please convert it to numeric format for trend analysis.")
        else:
            st.warning("Please select valid columns for trend analysis.")