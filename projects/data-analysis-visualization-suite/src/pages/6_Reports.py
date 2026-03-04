#!/usr/bin/env python3
"""Reports page - Export data and analysis reports."""

import io
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Report Generation")

# Check if data is loaded
if "data" not in st.session_state:
    st.warning("⚠️ No data loaded. Please upload data in the Upload page first.")
    st.stop()

df = st.session_state["data"]
filename = st.session_state.get("filename", "data")

st.markdown(f"Generating reports for: **{filename}**")

# Report configuration
st.subheader("⚙️ Report Configuration")

report_name = st.text_input(
    "Report Name",
    value=f"Analysis_Report_{datetime.now().strftime('%Y%m%d')}",
)

include_summary = st.checkbox("Include Summary Statistics", value=True)
include_raw_data = st.checkbox("Include Raw Data Sample", value=True)
include_metadata = st.checkbox("Include Dataset Metadata", value=True)

# Export options
st.subheader("📥 Export Options")

export_col1, export_col2 = st.columns(2)

with export_col1:
    st.markdown("**CSV Export**")
    
    if st.button("📄 Export as CSV"):
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_buffer.getvalue(),
            file_name=f"{report_name}.csv",
            mime="text/csv",
        )

with export_col2:
    st.markdown("**Excel Export**")
    
    if st.button("📊 Export as Excel"):
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name="Data", index=False)
            
            # Summary statistics sheet
            if include_summary:
                numeric_df = df.select_dtypes(include=["number"])
                if len(numeric_df.columns) > 0:
                    summary = numeric_df.describe().T
                    summary.to_excel(writer, sheet_name="Summary Statistics")
            
            # Metadata sheet
            if include_metadata:
                metadata = pd.DataFrame({
                    "Column": df.columns,
                    "Data Type": df.dtypes.astype(str),
                    "Non-Null Count": df.count().values,
                    "Null Count": df.isna().sum().values,
                    "Unique Values": [df[col].nunique() for col in df.columns],
                })
                metadata.to_excel(writer, sheet_name="Metadata", index=False)
        
        excel_buffer.seek(0)
        
        st.download_button(
            label="⬇️ Download Excel",
            data=excel_buffer,
            file_name=f"{report_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# Report preview
st.subheader("👁️ Report Preview")

if include_summary:
    st.markdown("**Summary Statistics**")
    numeric_df = df.select_dtypes(include=["number"])
    if len(numeric_df.columns) > 0:
        st.dataframe(numeric_df.describe().T, use_container_width=True)
    else:
        st.info("No numeric columns for summary statistics.")

if include_metadata:
    st.markdown("**Dataset Metadata**")
    metadata = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Non-Null Count": df.count().values,
        "Null Count": df.isna().sum().values,
        "Unique Values": [df[col].nunique() for col in df.columns],
    })
    st.dataframe(metadata, use_container_width=True, hide_index=True)

if include_raw_data:
    st.markdown("**Data Preview (First 20 rows)**")
    st.dataframe(df.head(20), use_container_width=True)

# Data info
st.subheader("📋 Dataset Information")

info_col1, info_col2, info_col3, info_col4 = st.columns(4)
info_col1.metric("Total Rows", len(df))
info_col2.metric("Total Columns", len(df.columns))
info_col3.metric("Numeric Columns", len(df.select_dtypes(include=["number"]).columns))
info_col4.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")

# Footer note
st.markdown("---")
st.info("💡 Reports include the current state of your data including any cleaning operations performed.")
