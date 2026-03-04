"""Static chart generation using matplotlib and seaborn."""

from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_time_series(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    title: Optional[str] = None,
    figsize: tuple = (12, 6),
) -> plt.Figure:
    """Plot a time series chart.
    
    Args:
        df: DataFrame containing the data
        date_col: Column name for dates
        value_col: Column name for values
        title: Chart title
        figsize: Figure size tuple
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(pd.to_datetime(df[date_col]), df[value_col], linewidth=2)
    ax.set_xlabel("Date")
    ax.set_ylabel(value_col)
    ax.set_title(title or f"{value_col} over Time")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def plot_distribution(
    df: pd.DataFrame,
    column: str,
    title: Optional[str] = None,
    figsize: tuple = (10, 6),
) -> plt.Figure:
    """Plot distribution histogram with KDE.
    
    Args:
        df: DataFrame containing the data
        column: Column name to plot
        title: Chart title
        figsize: Figure size tuple
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    sns.histplot(df[column], kde=True, ax=ax)
    ax.set_xlabel(column)
    ax.set_ylabel("Count")
    ax.set_title(title or f"Distribution of {column}")
    plt.tight_layout()
    return fig


def plot_correlation_heatmap(
    df: pd.DataFrame,
    title: Optional[str] = "Correlation Heatmap",
    figsize: tuple = (10, 8),
) -> plt.Figure:
    """Plot correlation heatmap for numeric columns.
    
    Args:
        df: DataFrame containing the data
        title: Chart title
        figsize: Figure size tuple
        
    Returns:
        Matplotlib figure object
    """
    numeric_df = df.select_dtypes(include=["float64", "int64"])
    corr = numeric_df.corr()
    
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, ax=ax, fmt=".2f")
    ax.set_title(title)
    plt.tight_layout()
    return fig


def plot_forecast(
    historical: pd.DataFrame,
    forecast: pd.DataFrame,
    date_col: str = "date",
    value_col: str = "value",
    title: Optional[str] = "Forecast",
    figsize: tuple = (12, 6),
) -> plt.Figure:
    """Plot historical data with forecast overlay.
    
    Args:
        historical: DataFrame with historical data
        forecast: DataFrame with forecast data
        date_col: Column name for dates
        value_col: Column name for values
        title: Chart title
        figsize: Figure size tuple
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot historical
    ax.plot(
        pd.to_datetime(historical[date_col]),
        historical[value_col],
        label="Historical",
        linewidth=2,
    )
    
    # Plot forecast
    ax.plot(
        pd.to_datetime(forecast[date_col]),
        forecast[value_col],
        label="Forecast",
        linewidth=2,
        linestyle="--",
    )
    
    # Plot confidence intervals if available
    if "lower_bound" in forecast.columns and "upper_bound" in forecast.columns:
        ax.fill_between(
            pd.to_datetime(forecast[date_col]),
            forecast["lower_bound"],
            forecast["upper_bound"],
            alpha=0.2,
            label="Confidence Interval",
        )
    
    ax.set_xlabel("Date")
    ax.set_ylabel(value_col)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig
