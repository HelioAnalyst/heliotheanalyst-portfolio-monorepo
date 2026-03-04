#!/usr/bin/env python3
"""Forecasting page - Simple time series forecasting."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression

st.set_page_config(
    page_title="Forecasting",
    page_icon="🔮",
    layout="wide",
)

st.title("🔮 Time Series Forecasting")

# Check if data is loaded
if "data" not in st.session_state:
    st.warning("⚠️ No data loaded. Please upload data in the Upload page first.")
    st.stop()

df = st.session_state["data"]

st.markdown(f"Forecasting for: **{st.session_state.get('filename', 'Unnamed dataset')}**")

# Detect datetime columns
datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

# Also check for object columns that might be dates
for col in df.select_dtypes(include=["object"]).columns:
    try:
        pd.to_datetime(df[col])
        datetime_cols.append(col)
    except (ValueError, TypeError):
        pass

numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

if len(datetime_cols) == 0:
    st.error("❌ No datetime column found. Please ensure your data has a date column.")
    st.stop()

if len(numeric_cols) == 0:
    st.error("❌ No numeric columns found for forecasting.")
    st.stop()

# Column selection
st.subheader("⚙️ Forecast Configuration")

date_col = st.selectbox(
    "Select date column",
    datetime_cols,
)

target_col = st.selectbox(
    "Select value column to forecast",
    numeric_cols,
)

# Convert date column if needed
if date_col in df.columns:
    df[date_col] = pd.to_datetime(df[date_col])

# Forecast horizon
forecast_days = st.slider(
    "Forecast Horizon (days)",
    min_value=7,
    max_value=90,
    value=14,
    step=7,
)

if st.button("🔮 Generate Forecast"):
    with st.spinner("Generating forecast..."):
        # Prepare data
        df_sorted = df.sort_values(by=date_col).reset_index(drop=True)
        
        # Create time-based features
        df_sorted["days_since_start"] = (df_sorted[date_col] - df_sorted[date_col].min()).dt.days
        
        # Handle missing values
        df_clean = df_sorted.dropna(subset=[target_col, "days_since_start"])
        
        if len(df_clean) < 10:
            st.error("❌ Not enough data points for forecasting (minimum 10 required).")
            st.stop()
        
        X = df_clean[["days_since_start"]].values
        y = df_clean[target_col].values
        
        # Fit model
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate future dates
        last_date = df_sorted[date_col].max()
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=forecast_days,
            freq="D",
        )
        
        last_day = df_clean["days_since_start"].max()
        future_days = np.array(range(last_day + 1, last_day + 1 + forecast_days)).reshape(-1, 1)
        
        # Predict
        predictions = model.predict(future_days)
        
        # Calculate confidence interval (simple approach)
        residuals = y - model.predict(X)
        mse = np.mean(residuals ** 2)
        std_error = np.sqrt(mse)
        
        lower_bound = predictions - 1.96 * std_error
        upper_bound = predictions + 1.96 * std_error
        
        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            "date": future_dates,
            "forecast": predictions.round(2),
            "lower_bound": lower_bound.round(2),
            "upper_bound": upper_bound.round(2),
        })
        
        # Display results
        st.subheader("📊 Forecast Results")
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Historical Mean", f"{y.mean():.2f}")
        metric_col2.metric("Forecast Mean", f"{predictions.mean():.2f}")
        metric_col3.metric("Trend", "📈 Up" if model.coef_[0] > 0 else "📉 Down")
        
        # Forecast table
        st.dataframe(forecast_df, use_container_width=True, hide_index=True)
        
        # Visualization
        st.subheader("📈 Forecast Visualization")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Historical data
        ax.plot(
            df_clean[date_col],
            df_clean[target_col],
            label="Historical",
            color="blue",
            alpha=0.7,
        )
        
        # Forecast
        ax.plot(
            forecast_df["date"],
            forecast_df["forecast"],
            label="Forecast",
            color="green",
            linestyle="--",
        )
        
        # Confidence interval
        ax.fill_between(
            forecast_df["date"],
            forecast_df["lower_bound"],
            forecast_df["upper_bound"],
            alpha=0.2,
            color="green",
            label="95% Confidence Interval",
        )
        
        ax.set_xlabel("Date")
        ax.set_ylabel(target_col)
        ax.set_title(f"{target_col} Forecast - Next {forecast_days} Days")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Download forecast
        csv = forecast_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Forecast as CSV",
            data=csv,
            file_name="forecast.csv",
            mime="text/csv",
        )
