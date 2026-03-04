#!/usr/bin/env python3
"""Anomaly Detection page - Detect outliers using statistical methods."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from scipy import stats

st.set_page_config(
    page_title="Anomaly Detection",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Anomaly Detection")

# Check if data is loaded
if "data" not in st.session_state:
    st.warning("⚠️ No data loaded. Please upload data in the Upload page first.")
    st.stop()

df = st.session_state["data"]

st.markdown(f"Detecting anomalies in: **{st.session_state.get('filename', 'Unnamed dataset')}**")

numeric_df = df.select_dtypes(include=["number"])

if len(numeric_df.columns) == 0:
    st.error("❌ No numeric columns found for anomaly detection.")
    st.stop()

# Method selection
st.subheader("⚙️ Detection Method")

method = st.radio(
    "Select detection method",
    ["Z-Score", "IQR (Interquartile Range)"],
    horizontal=True,
)

# Column selection
selected_cols = st.multiselect(
    "Select columns to analyze",
    numeric_df.columns,
    default=[numeric_df.columns[0]],
)

if not selected_cols:
    st.info("👆 Please select at least one column to analyze.")
    st.stop()

# Detection parameters
if method == "Z-Score":
    threshold = st.slider(
        "Z-Score Threshold",
        min_value=1.0,
        max_value=5.0,
        value=3.0,
        step=0.5,
        help="Points with |Z-Score| > threshold are considered anomalies",
    )
else:  # IQR
    multiplier = st.slider(
        "IQR Multiplier",
        min_value=1.0,
        max_value=3.0,
        value=1.5,
        step=0.1,
        help="Standard is 1.5 * IQR. Higher values = less sensitive",
    )

# Run detection
if st.button("🔍 Detect Anomalies"):
    all_anomalies = pd.Series([False] * len(df), index=df.index)
    results = []
    
    for col in selected_cols:
        col_data = df[col].dropna()
        
        if method == "Z-Score":
            z_scores = np.abs(stats.zscore(col_data))
            anomalies = z_scores > threshold
            anomaly_indices = col_data[anomalies].index
            all_anomalies.loc[anomaly_indices] = True
            
            results.append({
                "Column": col,
                "Method": f"Z-Score (>{threshold})",
                "Anomalies Found": anomalies.sum(),
                "Percentage": f"{(anomalies.sum() / len(col_data) * 100):.2f}%",
            })
            
        else:  # IQR
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR
            
            anomalies = (col_data < lower_bound) | (col_data > upper_bound)
            anomaly_indices = col_data[anomalies].index
            all_anomalies.loc[anomaly_indices] = True
            
            results.append({
                "Column": col,
                "Method": f"IQR ({multiplier}x)",
                "Anomalies Found": anomalies.sum(),
                "Percentage": f"{(anomalies.sum() / len(col_data) * 100):.2f}%",
            })
    
    # Display results summary
    st.subheader("📊 Detection Results")
    st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
    
    total_anomalies = all_anomalies.sum()
    st.metric("Total Anomalous Rows", f"{total_anomalies} / {len(df)}")
    
    # Visualizations
    st.subheader("📈 Visualizations")
    
    for col in selected_cols:
        col_data = df[col]
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 4))
        
        # Box plot
        axes[0].boxplot(col_data.dropna(), vert=True)
        axes[0].set_title(f"{col} - Box Plot")
        axes[0].set_ylabel(col)
        
        # Scatter plot with anomalies highlighted
        x_vals = range(len(col_data))
        normal_mask = ~all_anomalies.reindex(col_data.index, fill_value=False)
        anomaly_mask = all_anomalies.reindex(col_data.index, fill_value=False)
        
        axes[1].scatter(
            [x for x, m in zip(x_vals, normal_mask) if m],
            [v for v, m in zip(col_data, normal_mask) if m],
            alpha=0.6,
            label="Normal",
            c="blue",
        )
        axes[1].scatter(
            [x for x, m in zip(x_vals, anomaly_mask) if m],
            [v for v, m in zip(col_data, anomaly_mask) if m],
            alpha=0.8,
            label="Anomaly",
            c="red",
            marker="x",
            s=100,
        )
        axes[1].set_title(f"{col} - Anomaly Detection")
        axes[1].set_xlabel("Index")
        axes[1].set_ylabel(col)
        axes[1].legend()
        
        plt.tight_layout()
        st.pyplot(fig)
    
    # Anomaly data table
    if total_anomalies > 0:
        st.subheader("🔴 Anomalous Records")
        anomaly_df = df[all_anomalies]
        st.dataframe(anomaly_df, use_container_width=True)
        
        # Download option
        csv = anomaly_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Anomalies as CSV",
            data=csv,
            file_name="anomalies.csv",
            mime="text/csv",
        )
