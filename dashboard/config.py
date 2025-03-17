# Primary Colors (More distinct green shades with greater contrast)
PRIMARY_COLORS = ["#1b5e20", "#388e3c", "#66bb6a", "#a5d6a7"]

# Secondary Colors (More pleasing green variations)
SECONDARY_COLORS = ["#2e7d32", "#43a047", "#66bb6a", "#a5d6a7"]

# Neutral Colors (Light background shades)
NEUTRAL_COLORS = ["#e8f5e9", "#c8e6c9", "#a5d6a7", "#81c784"]

# Accent Colors (More vibrant and diverse)
ACCENT_COLORS = ["#7cb342", "#9ccc65", "#c0ca33", "#dce775"]

# Additional Palette (For charts with many series - complementary colors)
EXTENDED_COLORS = ["#5d4037", "#8d6e63", "#0277bd", "#039be5", "#7b1fa2", "#9c27b0", "#ef6c00", "#f57c00"]

# Text Colors (Dark to medium for readability)
TEXT_COLORS = ["#1b5e20", "#2e7d32", "#424242", "#616161"]

# Background Colors (Light green to white)
BACKGROUND_COLORS = ["#e8f5e9", "#f1f8e9", "#f9fbe7", "#ffffff"]

# Chart Colors (Expanded selection for multiple series)
CHART_COLORS = [
    PRIMARY_COLORS[0],
    SECONDARY_COLORS[0],
    ACCENT_COLORS[0],
    EXTENDED_COLORS[0],
    EXTENDED_COLORS[2],
    PRIMARY_COLORS[1],
    SECONDARY_COLORS[1],
    ACCENT_COLORS[1],
    EXTENDED_COLORS[1],
    EXTENDED_COLORS[3],
    EXTENDED_COLORS[4],
    EXTENDED_COLORS[6],
]

# Satisfaction Color Scale (Matching design doc exactly)
SATISFACTION_COLORS = {
    "Very Satisfied": "#2e7d32",  # Dark green
    "Satisfied": "#66bb6a",  # Medium green
    "Neutral": "#ffeb3b",  # Yellow
    "Dissatisfied": "#ff9800",  # Orange
    "Very Dissatisfied": "#f44336",  # Red
}

# Housing Situation Colors (Improved green palette)
HOUSING_COLORS = {
    "Renting": "#1b5e20",  # Dark green
    "Owned": "#2e7d32",  # Medium-dark green
    "Living with others": "#8bc34a",  # Bright lime green
}

# Rent Burden Colors (Using a green to red gradient)
RENT_BURDEN_COLORS = {
    "≤30% (Affordable)": PRIMARY_COLORS[0],  # Dark green
    "31-50% (Moderate)": "#ffeb3b",  # Yellow
    "51-80% (High)": "#ff9800",  # Orange
    ">80% (Very High)": "#f44336",  # Red
    "Unknown": "#cccccc",  # Gray
}

# Color scales for different visualization types
COLOR_SCALES = {
    "sequential": [
        "#e8f5e9",
        "#c8e6c9",
        "#81c784",
        "#4caf50",
        "#2e7d32",
    ],  # Light to dark green
    "diverging": [
        "#f44336",
        "#ffeb3b",
        "#ffffff",
        "#66bb6a",
        "#2e7d32",
    ],  # Red to green
    "qualitative": [
        PRIMARY_COLORS[0],
        SECONDARY_COLORS[0],
        ACCENT_COLORS[0],
        EXTENDED_COLORS[2],
        EXTENDED_COLORS[4],
        EXTENDED_COLORS[6],
        PRIMARY_COLORS[1],
        SECONDARY_COLORS[1],
    ],  # More diverse palette
}

# Additional color combinations for specific visualizations
VISUALIZATION_COLORS = {
    "heatmap": "RdYlGn",  # Red-Yellow-Green colorscale
    "choropleth": "Greens",  # Green sequential colorscale
    "density": "Viridis",  # Default density colorscale
    "correlation": "RdBu",  # Red-Blue diverging colorscale
}