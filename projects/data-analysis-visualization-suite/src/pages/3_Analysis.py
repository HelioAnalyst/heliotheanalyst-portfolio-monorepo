#!/usr/bin/env python3
"""Analysis page - Statistical analysis and correlations."""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Statistical Analysis",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Statistical Analysis")

# Check if data is loaded
if "data" not in st.session_state:
    st.warning("⚠️ No data loaded. Please upload data in the Upload page first.")
    st.stop()

df = st.session_state["data"]

st.markdown(f"Analyzing: **{st.session_state.get('filename', 'Unnamed dataset')}**")

# Summary Statistics
st.subheader("📊 Summary Statistics")

numeric_df = df.select_dtypes(include=["number"])

if len(numeric_df.columns) > 0:
    summary_stats = numeric_df.describe().T
    summary_stats["median"] = numeric_df.median()
    summary_stats["skewness"] = numeric_df.skew()
    summary_stats["kurtosis"] = numeric_df.kurtosis()
    
    # Reorder columns
    col_order = ["count", "mean", "std", "min", "25%", "50%", "median", "75%", "max", "skewness", "kurtosis"]
    summary_stats = summary_stats[[c for c in col_order if c in summary_stats.columns]]
    
    st.dataframe(summary_stats.style.format("{:.2f}"), use_container_width=True)
else:
    st.info("No numeric columns available for statistical analysis.")

# Column Analysis
st.subheader("🔎 Column Analysis")

selected_col = st.selectbox(
    "Select a column to analyze",
    df.columns,
)

if selected_col:
    col_data = df[selected_col]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Data Type", str(col_data.dtype))
    col2.metric("Unique Values", col_data.nunique())
    col3.metric("Non-Null Count", col_data.count())
    col4.metric("Null Count", col_data.isna().sum())
    
    # Value distribution for categorical columns
    if col_data.dtype == "object" or col_data.nunique() < 20:
        st.markdown("**Value Distribution:**")
        value_counts = col_data.value_counts().head(10)
        st.bar_chart(value_counts)
    
    # Distribution plot for numeric columns
    if pd.api.types.is_numeric_dtype(col_data):
        st.markdown("**Distribution:**")
        
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.histplot(col_data.dropna(), kde=True, ax=ax)
        ax.set_title(f"Distribution of {selected_col}")
        ax.set_xlabel(selected_col)
        st.pyplot(fig)

# Correlation Analysis
st.subheader("🔗 Correlation Analysis")

if len(numeric_df.columns) > 1:
    corr_method = st.radio(
        "Correlation Method",
        ["Pearson", "Spearman"],
        horizontal=True,
    )
    
    method = corr_method.lower()
    corr_matrix = numeric_df.corr(method=method)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="RdBu_r",
        center=0,
        fmt=".2f",
        ax=ax,
        square=True,
    )
    ax.set_title(f"{corr_method} Correlation Matrix")
    st.pyplot(fig)
    
    # Strong correlations
    st.markdown("**Strong Correlations (|r| > 0.7):**")
    
    strong_corr = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            corr_val = corr_matrix.iloc[i, j]
            if abs(corr_val) > 0.7:
                strong_corr.append({
                    "Column 1": corr_matrix.columns[i],
                    "Column 2": corr_matrix.columns[j],
                    "Correlation": round(corr_val, 3),
                })
    
    if strong_corr:
        st.dataframe(pd.DataFrame(strong_corr), use_container_width=True, hide_index=True)
    else:
        st.info("No strong correlations (|r| > 0.7) found.")

else:
    st.info("Need at least 2 numeric columns for correlation analysis.")

# Data Preview
st.subheader("👁️ Data Preview")
st.dataframe(df.head(20), use_container_width=True)
