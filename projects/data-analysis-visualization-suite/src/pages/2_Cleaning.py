#!/usr/bin/env python3
"""Data Cleaning page - Handle missing values and outliers."""

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Data Cleaning",
    page_icon="🧹",
    layout="wide",
)

st.title("🧹 Data Cleaning")

# Check if data is loaded
if "data" not in st.session_state:
    st.warning("⚠️ No data loaded. Please upload data in the Upload page first.")
    st.stop()

df = st.session_state["data"].copy()
original_shape = df.shape

st.markdown(f"Working with: **{st.session_state.get('filename', 'Unnamed dataset')}**")

# Data quality summary
st.subheader("📊 Data Quality Summary")

quality_col1, quality_col2, quality_col3, quality_col4 = st.columns(4)

missing_total = df.isna().sum().sum()
duplicate_count = df.duplicated().sum()

quality_col1.metric("Total Rows", original_shape[0])
quality_col2.metric("Total Columns", original_shape[1])
quality_col3.metric("Missing Values", missing_total)
quality_col4.metric("Duplicate Rows", duplicate_count)

# Missing values section
st.subheader("📝 Handle Missing Values")

missing_by_col = df.isna().sum()
missing_cols = missing_by_col[missing_by_col > 0]

if len(missing_cols) > 0:
    st.markdown("**Columns with missing values:**")
    
    missing_df = pd.DataFrame({
        "Column": missing_cols.index,
        "Missing Count": missing_cols.values,
        "Missing %": (missing_cols.values / len(df) * 100).round(2),
    })
    
    st.dataframe(missing_df, use_container_width=True, hide_index=True)
    
    # Missing value handling options
    st.markdown("**Select handling method:**")
    
    method = st.radio(
        "Method",
        ["Drop rows with missing values", "Fill with mean (numeric only)", "Fill with median (numeric only)", "Fill with mode"],
        horizontal=True,
    )
    
    if st.button("🧹 Apply Missing Value Treatment"):
        if method == "Drop rows with missing values":
            df_cleaned = df.dropna()
        elif method == "Fill with mean (numeric only)":
            df_cleaned = df.copy()
            numeric_cols = df_cleaned.select_dtypes(include=["number"]).columns
            for col in numeric_cols:
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())
        elif method == "Fill with median (numeric only)":
            df_cleaned = df.copy()
            numeric_cols = df_cleaned.select_dtypes(include=["number"]).columns
            for col in numeric_cols:
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
        else:  # Fill with mode
            df_cleaned = df.copy()
            for col in df_cleaned.columns:
                if not df_cleaned[col].mode().empty:
                    df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mode()[0])
        
        rows_removed = len(df) - len(df_cleaned)
        st.session_state["data"] = df_cleaned
        st.success(f"✅ Applied! {rows_removed} rows affected. Dataset now has {len(df_cleaned)} rows.")
        st.rerun()

else:
    st.success("✅ No missing values found in the dataset!")

# Outlier detection section
st.subheader("🔍 Outlier Detection")

numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

if len(numeric_cols) > 0:
    selected_col = st.selectbox(
        "Select column for outlier detection",
        numeric_cols,
    )
    
    if selected_col:
        col_data = df[selected_col].dropna()
        
        # IQR method
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
        
        outlier_col1, outlier_col2, outlier_col3 = st.columns(3)
        outlier_col1.metric("Q1 (25%)", f"{Q1:.2f}")
        outlier_col2.metric("Q3 (75%)", f"{Q3:.2f}")
        outlier_col3.metric("Outliers Detected", len(outliers))
        
        st.markdown(f"**IQR Bounds:** Lower = {lower_bound:.2f}, Upper = {upper_bound:.2f}")
        
        if len(outliers) > 0:
            show_outliers = st.toggle("Show outlier values", value=False)
            if show_outliers:
                st.write("Outlier values:", outliers.tolist())
            
            remove_outliers = st.toggle("Remove outliers from dataset", value=False)
            
            if remove_outliers and st.button("🗑️ Apply Outlier Removal"):
                mask = (df[selected_col] >= lower_bound) & (df[selected_col] <= upper_bound) | df[selected_col].isna()
                df_cleaned = df[mask].copy()
                rows_removed = len(df) - len(df_cleaned)
                st.session_state["data"] = df_cleaned
                st.success(f"✅ Removed {rows_removed} outlier rows. Dataset now has {len(df_cleaned)} rows.")
                st.rerun()
        else:
            st.info("No outliers detected in this column using IQR method.")

else:
    st.info("No numeric columns available for outlier detection.")

# Duplicate handling
st.subheader("🔄 Duplicate Rows")

duplicate_rows = df[df.duplicated(keep=False)]

if len(duplicate_rows) > 0:
    st.warning(f"Found {len(duplicate_rows)} duplicate rows ({df.duplicated().sum()} unique duplicates)")
    
    if st.button("🗑️ Remove Duplicate Rows"):
        df_cleaned = df.drop_duplicates()
        rows_removed = len(df) - len(df_cleaned)
        st.session_state["data"] = df_cleaned
        st.success(f"✅ Removed {rows_removed} duplicate rows. Dataset now has {len(df_cleaned)} rows.")
        st.rerun()
else:
    st.success("✅ No duplicate rows found!")

# Preview cleaned data
st.subheader("👁️ Preview Cleaned Data")

if "data" in st.session_state:
    st.dataframe(st.session_state["data"].head(10), use_container_width=True)
