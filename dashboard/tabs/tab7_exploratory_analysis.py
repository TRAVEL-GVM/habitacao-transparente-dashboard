# tab7_exploratory_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def show_exploratory_analysis_tab(df):
    st.header("Exploratory Data Analysis")
    
    # Create three columns for the controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        
        # Housing situation filter
        if 'housing_situation' in df.columns:
            housing_options = ["All"] + sorted(df['housing_situation'].dropna().unique().tolist())
            selected_housing = st.selectbox("Housing Situation", housing_options)
        
        # Region filter
        if 'distrito' in df.columns:
            district_options = ["All"] + sorted(df['distrito'].dropna().unique().tolist())
            selected_district = st.selectbox("District", district_options)
    
    with col2:
        # Income filter
        if 'rendimento_clean' in df.columns:
            income_options = ["All"] + sorted(df['rendimento_clean'].dropna().unique().tolist())
            selected_income = st.selectbox("Income Bracket", income_options)
        
        # Satisfaction filter
        if 'satisfaction_level' in df.columns:
            satisfaction_options = ["All"] + sorted(df['satisfaction_level'].dropna().unique().tolist())
            selected_satisfaction = st.selectbox("Satisfaction Level", satisfaction_options)
    
    with col3:
        # House type filter
        if 'house_type' in df.columns:
            house_type_options = ["All"] + sorted(df['house_type'].dropna().unique().tolist())
            selected_house_type = st.selectbox("House Type", house_type_options)
        
        # Education level filter
        if 'education_level' in df.columns:
            education_options = ["All"] + sorted(df['education_level'].dropna().unique().tolist())
            selected_education = st.selectbox("Education Level", education_options)
    
    # Apply filters to the dataframe
    filtered_df = df.copy()
    
    if 'housing_situation' in df.columns and selected_housing != "All":
        filtered_df = filtered_df[filtered_df['housing_situation'] == selected_housing]
    
    if 'distrito' in df.columns and selected_district != "All":
        filtered_df = filtered_df[filtered_df['distrito'] == selected_district]
    
    if 'rendimento_clean' in df.columns and selected_income != "All":
        filtered_df = filtered_df[filtered_df['rendimento_clean'] == selected_income]
    
    if 'satisfaction_level' in df.columns and selected_satisfaction != "All":
        filtered_df = filtered_df[filtered_df['satisfaction_level'] == selected_satisfaction]
    
    if 'house_type' in df.columns and selected_house_type != "All":
        filtered_df = filtered_df[filtered_df['house_type'] == selected_house_type]
    
    if 'education_level' in df.columns and selected_education != "All":
        filtered_df = filtered_df[filtered_df['education_level'] == selected_education]
    
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
            ["Bar Chart", "Histogram", "Scatter Plot", "Box Plot", "Pie Chart"]
        )
        
        # Get numeric and categorical columns for axis selection
        numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = filtered_df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Remove complex list columns
        categorical_cols = [col for col in categorical_cols if not any(filtered_df[col].astype(str).str.contains('\[', na=False))]
        
        # Add cleaned columns that might be useful
        for col in ['housing_situation', 'satisfaction_level', 'house_type', 'education_level', 'employment_status', 'rendimento_clean', 'bedroom_count']:
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
                fig = px.bar(
                    filtered_df[x_axis].value_counts().reset_index(), 
                    x='index', 
                    y=x_axis,
                    title=f"Count of {x_axis}",
                    labels={'index': x_axis, x_axis: 'Count'}
                )
            else:
                agg_func = {'mean': np.mean, 'sum': np.sum, 'median': np.median}[agg_option.lower()]
                agg_data = filtered_df.groupby(x_axis)[y_axis].agg(agg_func).reset_index()
                fig = px.bar(
                    agg_data, 
                    x=x_axis, 
                    y=y_axis,
                    title=f"{agg_option} of {y_axis} by {x_axis}"
                )
        
        elif chart_type == "Histogram":
            fig = px.histogram(
                filtered_df, 
                x=x_axis, 
                nbins=bins,
                title=f"Distribution of {x_axis}"
            )
        
        elif chart_type == "Scatter Plot":
            fig = px.scatter(
                filtered_df, 
                x=x_axis, 
                y=y_axis, 
                color=color_option,
                title=f"{y_axis} vs {x_axis}"
            )
        
        elif chart_type == "Box Plot":
            fig = px.box(
                filtered_df, 
                x=x_axis, 
                y=y_axis,
                title=f"Distribution of {y_axis} by {x_axis}"
            )
        
        else:  # Pie Chart
            value_counts = filtered_df[x_axis].value_counts()
            fig = px.pie(
                names=value_counts.index, 
                values=value_counts.values,
                title=f"Distribution of {x_axis}"
            )
        
        # Show the generated chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Add chart description
        with st.expander("Chart Insights", expanded=False):
            if chart_type == "Bar Chart":
                if agg_option == "Count":
                    most_common = filtered_df[x_axis].value_counts().idxmax()
                    pct = (filtered_df[x_axis].value_counts().max() / len(filtered_df)) * 100
                    st.write(f"- Most common {x_axis}: {most_common} ({pct:.1f}% of data)")
                    st.write(f"- Number of unique {x_axis} values: {filtered_df[x_axis].nunique()}")
                else:
                    agg_data = filtered_df.groupby(x_axis)[y_axis].agg(agg_func)
                    max_category = agg_data.idxmax()
                    min_category = agg_data.idxmin()
                    st.write(f"- Highest {y_axis} ({agg_option}): {max_category} with {agg_data.max():.2f}")
                    st.write(f"- Lowest {y_axis} ({agg_option}): {min_category} with {agg_data.min():.2f}")
            
            elif chart_type == "Histogram":
                st.write(f"- Average value: {filtered_df[x_axis].mean():.2f}")
                st.write(f"- Median value: {filtered_df[x_axis].median():.2f}")
                st.write(f"- Range: {filtered_df[x_axis].min():.2f} to {filtered_df[x_axis].max():.2f}")
            
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
                st.write(f"- Category with highest median {y_axis}: {grouped.median().idxmax()}")
                st.write(f"- Category with lowest median {y_axis}: {grouped.median().idxmin()}")
                st.write(f"- Category with most variability: {grouped.std().idxmax()}")
            
            else:  # Pie Chart
                most_common = filtered_df[x_axis].value_counts().idxmax()
                pct = (filtered_df[x_axis].value_counts().max() / len(filtered_df)) * 100
                st.write(f"- Most common {x_axis}: {most_common} ({pct:.1f}% of data)")
                st.write(f"- Number of categories: {filtered_df[x_axis].nunique()}")
    else:
        st.warning("No data available with current filters. Please adjust your filters.")
    
    # Statistical summary section
    st.subheader("Statistical Summary")
    
    # Select columns for summary
    summary_cols = st.multiselect(
        "Select columns for summary statistics", 
        numeric_cols,
        default=numeric_cols[:3] if len(numeric_cols) > 3 else numeric_cols
    )
    
    if summary_cols:
        st.dataframe(filtered_df[summary_cols].describe(), use_container_width=True)
    
    # Correlation matrix
    if len(numeric_cols) > 1:
        with st.expander("Correlation Matrix", expanded=False):
            corr_cols = st.multiselect(
                "Select columns for correlation analysis",
                numeric_cols,
                default=numeric_cols[:5] if len(numeric_cols) > 5 else numeric_cols
            )
            
            if corr_cols and len(corr_cols) > 1:
                corr_matrix = filtered_df[corr_cols].corr()
                
                # Create a heatmap for the correlation matrix
                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    color_continuous_scale='RdBu_r',
                    title="Correlation Matrix"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Find the strongest correlations
                corr_pairs = []
                for i in range(len(corr_cols)):
                    for j in range(i+1, len(corr_cols)):
                        corr_value = corr_matrix.iloc[i, j]
                        corr_pairs.append((corr_cols[i], corr_cols[j], corr_value))
                
                # Sort by absolute correlation value and show the top 5
                corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                
                st.write("Strongest correlations:")
                for col1, col2, corr in corr_pairs[:5]:
                    st.write(f"- {col1} and {col2}: {corr:.2f}")