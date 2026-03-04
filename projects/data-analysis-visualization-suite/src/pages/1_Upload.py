#!/usr/bin/env python3
"""Upload page - Import CSV/Excel files and preview data."""

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Upload Data",
    page_icon="📤",
    layout="wide",
)

st.title("📤 Upload Data")

st.markdown("""
Upload your dataset to begin analysis. Supported formats:
- **CSV** (.csv)
- **Excel** (.xlsx, .xls)
""")

# File upload section
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "xlsx", "xls"],
    help="Upload a CSV or Excel file to analyze",
)

if uploaded_file is not None:
    try:
        # Load data based on file type
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Store in session state for other pages
        st.session_state["data"] = df
        st.session_state["filename"] = uploaded_file.name
        
        st.success(f"✅ Successfully loaded **{uploaded_file.name}**")
        
        # Data preview
        st.subheader("📋 Data Preview")
        
        preview_col1, preview_col2, preview_col3 = st.columns(3)
        preview_col1.metric("Rows", len(df))
        preview_col2.metric("Columns", len(df.columns))
        preview_col3.metric("Missing Values", df.isna().sum().sum())
        
        st.dataframe(df.head(10), use_container_width=True)
        
        # Column info
        st.subheader("📊 Column Information")
        
        col_info = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str),
            "Non-Null": df.count().values,
            "Null": df.isna().sum().values,
        })
        
        st.dataframe(col_info, use_container_width=True, hide_index=True)
        
        # Data types summary
        st.subheader("📈 Data Types Summary")
        
        dtype_counts = df.dtypes.value_counts()
        
        dtype_col1, dtype_col2, dtype_col3 = st.columns(3)
        
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
        
        dtype_col1.metric("Numeric Columns", len(numeric_cols))
        dtype_col2.metric("Text Columns", len(categorical_cols))
        dtype_col3.metric("DateTime Columns", len(datetime_cols))
        
        if numeric_cols:
            st.caption(f"**Numeric:** {', '.join(numeric_cols[:5])}{'...' if len(numeric_cols) > 5 else ''}")
        if categorical_cols:
            st.caption(f"**Text:** {', '.join(categorical_cols[:5])}{'...' if len(categorical_cols) > 5 else ''}")
        
        st.info("💡 Your data is now loaded! Navigate to other pages using the sidebar to analyze and visualize.")
        
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        st.info("Please check that your file is a valid CSV or Excel file.")

else:
    # Sample data option
    st.info("👆 Upload a file above, or use the sample data for testing.")
    
    if st.button("📁 Load Sample Data"):
        # Create sample dataset
        import numpy as np
        from datetime import datetime, timedelta
        
        np.random.seed(42)
        dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
        
        sample_df = pd.DataFrame({
            "date": dates,
            "product_id": np.random.choice(["A", "B", "C", "D"], 100),
            "sales": np.random.normal(1000, 200, 100).round(2),
            "quantity": np.random.randint(10, 100, 100),
            "customer_rating": np.random.choice([1, 2, 3, 4, 5, None], 100, p=[0.05, 0.05, 0.1, 0.3, 0.4, 0.1]),
            "region": np.random.choice(["North", "South", "East", "West"], 100),
        })
        
        # Add some outliers
        outlier_indices = np.random.choice(100, 5, replace=False)
        sample_df.loc[outlier_indices, "sales"] = sample_df.loc[outlier_indices, "sales"] * 3
        
        st.session_state["data"] = sample_df
        st.session_state["filename"] = "sample_data.csv"
        
        st.success("✅ Sample data loaded!")
        st.rerun()
