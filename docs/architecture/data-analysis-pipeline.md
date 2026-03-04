# Data Analysis Pipeline - Architecture

## System Overview

The Data Analysis & Visualization Suite is a modular analytics toolkit that automates data cleaning, analysis, anomaly detection, forecasting, and reporting.

## High-Level Architecture

```mermaid
flowchart TB
    subgraph Input["Input Layer"]
        CSV["CSV Files"]
        Excel["Excel Files"]
        JSON["JSON Files"]
        DB["Databases"]
    end

    subgraph Pipeline["Processing Pipeline"]
        Ingest["1. Ingest"]
        Clean["2. Clean"]
        Analyze["3. Analyze"]
        Anomaly["4. Anomaly Detection"]
        Forecast["5. Forecast"]
    end

    subgraph Visualization["Visualization"]
        Streamlit["Streamlit UI"]
        Charts["Matplotlib/Plotly"]
        Tables["Data Tables"]
    end

    subgraph Output["Output Layer"]
        PDF["PDF Reports"]
        ExcelOut["Excel Reports"]
        Markdown["Markdown Reports"]
    end

    CSV --> Ingest
    Excel --> Ingest
    JSON --> Ingest
    DB --> Ingest

    Ingest --> Clean
    Clean --> Analyze
    Analyze --> Anomaly
    Analyze --> Forecast

    Analyze --> Streamlit
    Anomaly --> Streamlit
    Forecast --> Streamlit

    Streamlit --> Charts
    Streamlit --> Tables

    Analyze --> PDF
    Anomaly --> PDF
    Forecast --> PDF
    Analyze --> ExcelOut
    Analyze --> Markdown
```

## Pipeline Module Flow

```mermaid
sequenceDiagram
    participant User
    participant Ingest as DataLoader
    participant Clean as DataCleaner
    participant Analyze as StatisticalAnalyzer
    participant Anomaly as AnomalyDetector
    participant Forecast as TimeSeriesForecaster
    participant Report as ReportGenerator

    User->>Ingest: load_csv(filepath)
    Ingest-->>User: DataFrame

    User->>Clean: DataCleaner(df)
    Clean->>Clean: remove_duplicates()
    Clean->>Clean: handle_missing(strategy='mean')
    Clean->>Clean: remove_outliers()
    Clean-->>User: cleaned_df

    User->>Analyze: StatisticalAnalyzer(cleaned_df)
    Analyze->>Analyze: descriptive_stats()
    Analyze->>Analyze: correlation_matrix()
    Analyze-->>User: statistics

    User->>Anomaly: AnomalyDetector(cleaned_df)
    Anomaly->>Anomaly: statistical_outliers()
    Anomaly->>Anomaly: isolation_forest()
    Anomaly-->>User: df_with_flags

    User->>Forecast: TimeSeriesForecaster(cleaned_df)
    Forecast->>Forecast: fit(date_col, value_col)
    Forecast->>Forecast: predict(periods=14)
    Forecast-->>User: forecast_df

    User->>Report: ReportGenerator(title)
    Report->>Report: add_dataframe(stats)
    Report->>Report: add_dataframe(forecast)
    Report->>Report: generate_pdf(filepath)
```

## Data Cleaning Pipeline

```mermaid
flowchart TD
    Raw[Raw DataFrame] --> Dupes{Duplicates?}
    Dupes -->|Yes| RemoveDupes[Remove Duplicates]
    Dupes -->|No| SkipDupes
    RemoveDupes --> Missing
    SkipDupes --> Missing

    Missing{Missing Values?}
    Missing -->|Yes| Impute[Impute Values]
    Missing -->|No| SkipMissing
    Impute --> Outliers
    SkipMissing --> Outliers

    Outliers{Outliers?}
    Outliers -->|Yes| RemoveOut[Remove Outliers]
    Outliers -->|No| SkipOut
    RemoveOut --> Clean
    SkipOut --> Clean

    Clean[Clean DataFrame] --> Return[Return Cleaned]
```

## Anomaly Detection Methods

```mermaid
flowchart TB
    Data[Input Data] --> Method{Method}

    Method -->|Statistical| Stats["Statistical Outliers"]
    Method -->|ML| ML["Machine Learning"]

    Stats --> ZScore["Z-Score Method"]
    Stats --> IQR["IQR Method"]

    ML --> IsoForest["Isolation Forest"]
    ML --> LOF["Local Outlier Factor"]

    ZScore --> Output[Flagged DataFrame]
    IQR --> Output
    IsoForest --> Output
    LOF --> Output
```

## Time Series Forecasting

```mermaid
flowchart TB
    History[Historical Data] --> Features["Feature Engineering"]

    Features --> TimeIdx["Time Index"]
    Features --> DayOfWeek["Day of Week (sin/cos)"]
    Features --> Month["Month (sin/cos)"]
    Features --> Quarter["Quarter"]
    Features --> Year["Year"]

    TimeIdx --> Model[Linear Regression Model]
    DayOfWeek --> Model
    Month --> Model
    Quarter --> Model
    Year --> Model

    Model --> Train[Train on History]
    Train --> Predict[Predict Future]

    Predict --> Forecast[Forecast Values]
    Predict --> Lower[Lower Bound]
    Predict --> Upper[Upper Bound]

    Forecast --> Output[Forecast DataFrame]
    Lower --> Output
    Upper --> Output
```

## Report Generation Pipeline

```mermaid
flowchart TB
    subgraph DataSources["Data Sources"]
        Stats["Statistics"]
        Corr["Correlations"]
        Anom["Anomalies"]
        Fcast["Forecast"]
    end

    subgraph Generator["ReportGenerator"]
        AddSection["Add Section"]
        AddTable["Add Table"]
        AddChart["Add Chart"]
    end

    subgraph Formats["Output Formats"]
        PDF["PDF (ReportLab)"]
        Excel["Excel (OpenPyXL)"]
        MD["Markdown"]
    end

    Stats --> AddSection
    Corr --> AddTable
    Anom --> AddTable
    Fcast --> AddChart

    AddSection --> PDF
    AddTable --> PDF
    AddChart --> PDF

    AddSection --> Excel
    AddTable --> Excel

    AddSection --> MD
    AddTable --> MD
```

## Streamlit App Architecture

```mermaid
flowchart TB
    subgraph Pages["Streamlit Pages"]
        Upload["📤 Upload"]
        Cleaning["🧹 Cleaning"]
        Analysis["📈 Analysis"]
        Anomalies["🔍 Anomalies"]
        Forecast["🔮 Forecast"]
        Export["📄 Export Report"]
    end

    subgraph State["Session State"]
        DataFrame["DataFrame"]
        CleanedDF["Cleaned DataFrame"]
        Stats["Statistics"]
        Models["Trained Models"]
    end

    Upload -->|loads| DataFrame
    DataFrame --> Cleaning
    Cleaning -->|produces| CleanedDF
    CleanedDF --> Analysis
    CleanedDF --> Anomalies
    CleanedDF --> Forecast

    Analysis -->|stores| Stats
    Forecast -->|stores| Models

    Stats --> Export
    Models --> Export
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| UI | Streamlit |
| Data Processing | pandas, NumPy |
| Statistics | SciPy |
| Machine Learning | scikit-learn |
| Visualization | Matplotlib, Seaborn, Plotly |
| Reports | ReportLab, OpenPyXL |
| Testing | pytest |

## Key Design Decisions

1. **Modular Pipeline**: Each stage (ingest, clean, analyze) is independent
2. **Method Chaining**: DataCleaner supports fluent interface
3. **Multiple Anomaly Methods**: Statistical and ML approaches
4. **Time Features**: Cyclical encoding for seasonality
5. **Multiple Outputs**: PDF, Excel, Markdown for different audiences
