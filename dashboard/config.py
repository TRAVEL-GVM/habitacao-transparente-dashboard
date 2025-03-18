# Primary Colors (Dark to light green shades)
PRIMARY_COLORS = ["#2e7d32", "#43a047", "#66bb6a", "#a5d6a7"]

# Secondary Colors (Alternative green shades)
SECONDARY_COLORS = ["#388e3c", "#4caf50", "#81c784", "#c8e6c9"]

# Neutral Colors (Very light to medium green)
NEUTRAL_COLORS = ["#e8f5e9", "#c8e6c9", "#a5d6a7", "#81c784"]

# Accent Colors (Lime green shades)
ACCENT_COLORS = ["#689f38", "#8bc34a", "#aed581", "#dcedc8"]

# Extended Colors (For charts with many series)
EXTENDED_COLORS = ["#5d4037", "#8d6e63", "#0277bd", "#039be5", "#7b1fa2", "#9c27b0", "#ef6c00", "#f57c00"]

# Text Colors (Very dark to medium green for text)
TEXT_COLORS = ["#1b5e20", "#2e7d32", "#388e3c", "#43a047"]

# Background Colors (Very light green to white)
BACKGROUND_COLORS = ["#e8f5e9", "#f1f8e9", "#f9fbe7", "#ffffff"]

# Chart Colors (Main colors for visualizations with expanded options for multiple series)
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

# Housing Situation Colors (Using primary and accent colors)
HOUSING_COLORS = {
    "Arrendamento": PRIMARY_COLORS[0],  # Dark green
    "Casa Própria": SECONDARY_COLORS[0],  # Alternative green
    "Others": ACCENT_COLORS[0],  # Lime green
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
    ],  # Mix of color families
}

# Additional color combinations for specific visualizations
VISUALIZATION_COLORS = {
    "heatmap": "RdYlGn",  # Red-Yellow-Green colorscale
    "choropleth": "Greens",  # Green sequential colorscale
    "density": "Viridis",  # Default density colorscale
    "correlation": "RdBu",  # Red-Blue diverging colorscale
}