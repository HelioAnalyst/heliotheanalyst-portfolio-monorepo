#!/usr/bin/env python3
"""Demo script for Data Analysis & Visualization Suite."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from data_analysis.ingest.loader import DataLoader, generate_sample_data
from data_analysis.clean.processor import DataCleaner
from data_analysis.analyze.statistics import StatisticalAnalyzer, DataProfiler
from data_analysis.anomaly.detector import AnomalyDetector
from data_analysis.predict.forecaster import TimeSeriesForecaster
from data_analysis.report.generator import ReportGenerator


def main() -> None:
    """Run data analysis demo."""
    print("=" * 60)
    print("Data Analysis & Visualization Suite - Demo")
    print("=" * 60)
    print()

    # Generate sample data
    print("1. Generating sample data...")
    df = generate_sample_data(n_rows=500)
    print(f"   Generated {len(df)} rows")
    print(f"   Columns: {', '.join(df.columns)}")
    print()

    # Save sample
    Path("outputs").mkdir(exist_ok=True)
    DataLoader.save_csv(df, "outputs/sample_generated.csv")
    print("   Saved to outputs/sample_generated.csv")
    print()

    # Data profiling
    print("2. Data Profiling...")
    profiler = DataProfiler(df)
    profile = profiler.profile()
    print(f"   Shape: {profile['shape']}")
    print(f"   Missing values: {sum(profile['missing_values'].values())}")
    print()

    # Data cleaning
    print("3. Data Cleaning...")
    cleaner = DataCleaner(df)
    cleaner.remove_duplicates()
    cleaner.handle_missing(strategy="mean")
    df_clean = cleaner.get_cleaned_data()
    print(f"   Rows after cleaning: {len(df_clean)}")
    print()

    # Statistical analysis
    print("4. Statistical Analysis...")
    analyzer = StatisticalAnalyzer(df_clean)
    stats = analyzer.descriptive_stats()
    print("   Descriptive statistics:")
    print(stats.to_string())
    print()

    # Correlation
    print("5. Correlation Analysis...")
    corr = analyzer.correlation_matrix()
    print("   Correlation matrix:")
    print(corr.to_string())
    print()

    # Anomaly detection
    print("6. Anomaly Detection...")
    detector = AnomalyDetector(df_clean)
    df_with_outliers = detector.statistical_outliers("sales", method="zscore")
    summary = detector.get_anomaly_summary(df_with_outliers)
    print(f"   Anomalies detected: {summary['anomaly_count']}")
    print(f"   Anomaly percentage: {summary['anomaly_percent']:.2f}%")
    print()

    # Forecasting
    print("7. Time Series Forecasting...")
    forecaster = TimeSeriesForecaster(df_clean)
    forecaster.fit("date", "sales", model_type="linear")
    forecast = forecaster.predict(periods=30, last_date=df_clean["date"].max())
    print(f"   Forecasted {len(forecast)} periods")
    print(f"   Average forecast: ${forecast['forecast'].mean():.2f}")

    # Evaluation
    metrics = forecaster.evaluate("date", "sales")
    print(f"   Model RMSE: {metrics['rmse']:.2f}")
    print()

    # Generate report
    print("8. Generating Report...")
    report = ReportGenerator("Data Analysis Report")
    report.add_section("Overview", f"Dataset contains {len(df_clean)} records")
    report.add_dataframe("Statistics", stats)
    report.add_dataframe("Forecast", forecast)

    report.generate_pdf("outputs/analysis_report.pdf")
    print("   PDF report: outputs/analysis_report.pdf")

    report.generate_excel("outputs/analysis_report.xlsx", {
        "raw_data": df_clean,
        "statistics": stats,
        "forecast": forecast,
    })
    print("   Excel report: outputs/analysis_report.xlsx")

    report.generate_markdown("outputs/analysis_report.md")
    print("   Markdown report: outputs/analysis_report.md")
    print()

    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    print()
    print("To run the Streamlit app:")
    print("  streamlit run src/app.py")


if __name__ == "__main__":
    main()
