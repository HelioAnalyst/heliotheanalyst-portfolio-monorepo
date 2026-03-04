#!/usr/bin/env python3
"""Streamlit app for Data Analysis & Visualization Suite."""

import streamlit as st

st.set_page_config(
    page_title="Data Analysis Suite",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Data Analysis & Visualization Suite")

st.markdown("""
Welcome to the Data Analysis & Visualization Suite - a comprehensive toolkit for 
data analysis, cleaning, anomaly detection, and forecasting.

## Features

- **📤 Upload Data**: Import CSV, Excel files
- **🧹 Data Cleaning**: Handle missing values, outliers
- **📈 Analysis**: Statistical analysis and correlations
- **🔍 Anomaly Detection**: Identify outliers and anomalies
- **🔮 Forecasting**: Time series prediction
- **📄 Reports**: Generate PDF and Excel reports

## Quick Start

1. Use the sidebar to navigate between pages
2. Upload your data in the **Upload** page
3. Clean and analyze your data
4. Generate insights and forecasts
5. Export reports

## Sample Data

A sample dataset is available at `data/sample.csv` for testing.
""")

st.sidebar.title("Navigation")
st.sidebar.info("Select a page from the sidebar to get started.")

# Show system info
st.subheader("System Information")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Python Version", "3.11+")

with col2:
    st.metric("Pandas Version", "2.1+")

with col3:
    st.metric("Scikit-learn", "1.3+")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ by HelioTheAnalyst")
