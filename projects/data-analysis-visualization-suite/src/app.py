#!/usr/bin/env python3
"""Streamlit Home page for Data Analysis & Visualization Suite."""

import platform

import pandas as pd
import sklearn
import streamlit as st

st.set_page_config(
    page_title="Data Analysis Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for clean styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .feature-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        color: #666;
        font-size: 0.95rem;
    }
    .footer {
        text-align: center;
        color: #888;
        padding: 2rem 0;
        border-top: 1px solid #eee;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">📊 Data Analysis & Visualization Suite</p>', unsafe_allow_html=True)

st.markdown("""
Welcome to the **Data Analysis & Visualization Suite** - a comprehensive toolkit for 
data exploration, cleaning, analysis, and reporting.
""")

# Features Section
st.subheader("✨ Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <p class="feature-title">📤 Upload Data</p>
        <p class="feature-desc">Import CSV and Excel files with automatic type detection</p>
    </div>
    <div class="feature-card">
        <p class="feature-title">🧹 Data Cleaning</p>
        <p class="feature-desc">Handle missing values, remove duplicates, detect outliers</p>
    </div>
    <div class="feature-card">
        <p class="feature-title">📈 Statistical Analysis</p>
        <p class="feature-desc">Summary statistics, correlations, and distributions</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <p class="feature-title">🔍 Anomaly Detection</p>
        <p class="feature-desc">Identify outliers using Z-score, IQR, and ML methods</p>
    </div>
    <div class="feature-card">
        <p class="feature-title">🔮 Forecasting</p>
        <p class="feature-desc">Time series prediction with confidence intervals</p>
    </div>
    <div class="feature-card">
        <p class="feature-title">📄 Report Generation</p>
        <p class="feature-desc">Export PDF and Excel reports with one click</p>
    </div>
    """, unsafe_allow_html=True)

# Quick Start Section
st.subheader("🚀 Quick Start")

st.markdown("""
1. **Upload** your data in the Upload page (CSV or Excel)
2. **Clean** your data by handling missing values and outliers
3. **Analyze** with statistical summaries and correlations
4. **Detect** anomalies using multiple methods
5. **Forecast** future trends with time series analysis
6. **Export** professional reports

Use the **sidebar navigation** on the left to explore each feature.
""")

# System Information Section
st.subheader("ℹ️ System Information")

info_col1, info_col2, info_col3, info_col4 = st.columns(4)

with info_col1:
    st.metric(
        label="Python Version",
        value=f"{platform.python_version()}",
    )

with info_col2:
    st.metric(
        label="Pandas Version",
        value=f"{pd.__version__}",
    )

with info_col3:
    st.metric(
        label="Scikit-learn",
        value=f"{sklearn.__version__}",
    )

with info_col4:
    st.metric(
        label="Streamlit",
        value=f"{st.__version__}",
    )

# Footer
st.markdown("""
<div class="footer">
    <p>Built with ❤️ by <strong>HelioTheAnalyst</strong></p>
    <p style="font-size: 0.85rem; margin-top: 0.5rem;">
        Data Analysis & Visualization Suite v1.0.0
    </p>
</div>
""", unsafe_allow_html=True)
