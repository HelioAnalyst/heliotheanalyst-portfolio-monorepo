"""Interactive visualization helpers using Plotly."""

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure


def create_interactive_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    chart_type: str = "line",
    title: Optional[str] = None,
    color_col: Optional[str] = None,
) -> Figure:
    """Create an interactive Plotly chart.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        chart_type: Type of chart (line, bar, scatter)
        title: Chart title
        color_col: Optional column for color grouping
        
    Returns:
        Plotly figure object
    """
    if chart_type == "line":
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
        )
    elif chart_type == "bar":
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
        )
    elif chart_type == "scatter":
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
        )
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        hovermode="x unified",
    )
    return fig


def create_dashboard_widget(
    metric_name: str,
    metric_value: float,
    delta: Optional[float] = None,
    delta_description: str = "vs previous period",
) -> go.Indicator:
    """Create a metric indicator widget for dashboards.
    
    Args:
        metric_name: Name of the metric
        metric_value: Current value
        delta: Change from previous period
        delta_description: Description of the delta
        
    Returns:
        Plotly indicator object
    """
    if delta is not None:
        indicator = go.Indicator(
            mode="number+delta",
            value=metric_value,
            title={"text": metric_name},
            delta={
                "reference": metric_value - delta,
                "relative": True,
                "valueformat": ".1%",
            },
        )
    else:
        indicator = go.Indicator(
            mode="number",
            value=metric_value,
            title={"text": metric_name},
        )
    
    return indicator


def create_interactive_heatmap(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    value_col: str,
    title: Optional[str] = None,
) -> Figure:
    """Create an interactive heatmap.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis categories
        y_col: Column name for y-axis categories
        value_col: Column name for values
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    fig = px.density_heatmap(
        df,
        x=x_col,
        y=y_col,
        z=value_col,
        title=title,
        color_continuous_scale="Viridis",
    )
    return fig
