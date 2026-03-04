"""Demand forecasting for inventory items."""

from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class DemandForecaster:
    """Forecast demand for inventory items."""

    def __init__(self) -> None:
        """Initialize forecaster."""
        self.model = LinearRegression()

    def generate_sample_history(
        self,
        days: int = 90,
        base_demand: float = 10.0,
        trend: float = 0.1,
        noise: float = 2.0,
    ) -> pd.DataFrame:
        """Generate sample demand history.

        Args:
            days: Number of days.
            base_demand: Base daily demand.
            trend: Daily trend.
            noise: Random noise level.

        Returns:
            DataFrame with demand history.
        """
        dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]

        # Generate demand with trend and seasonality
        demand = []
        for i in range(days):
            day_demand = base_demand + (i * trend)
            # Add weekly seasonality (higher on weekends)
            day_of_week = dates[i].weekday()
            if day_of_week >= 5:  # Weekend
                day_demand *= 1.3
            # Add noise
            day_demand += np.random.normal(0, noise)
            demand.append(max(0, day_demand))

        return pd.DataFrame({
            "date": dates,
            "demand": demand,
        })

    def forecast(
        self,
        history: pd.DataFrame,
        periods: int = 14,
    ) -> pd.DataFrame:
        """Generate demand forecast.

        Args:
            history: Historical demand data.
            periods: Number of periods to forecast.

        Returns:
            Forecast DataFrame.
        """
        if len(history) < 7:
            # Not enough data, use simple average
            avg_demand = history["demand"].mean() if len(history) > 0 else 10
            future_dates = [datetime.now() + timedelta(days=i) for i in range(1, periods + 1)]
            return pd.DataFrame({
                "date": future_dates,
                "forecast": [avg_demand] * periods,
                "lower_bound": [avg_demand * 0.8] * periods,
                "upper_bound": [avg_demand * 1.2] * periods,
            })

        # Prepare features
        history = history.copy()
        history["day_num"] = range(len(history))
        history["day_of_week"] = pd.to_datetime(history["date"]).dt.dayofweek

        # Create dummy variables for day of week
        for i in range(7):
            history[f"dow_{i}"] = (history["day_of_week"] == i).astype(int)

        # Features
        feature_cols = ["day_num"] + [f"dow_{i}" for i in range(7)]
        X = history[feature_cols].values
        y = history["demand"].values

        # Fit model
        self.model.fit(X, y)

        # Generate future features
        last_day = history["day_num"].max()
        future_data = []
        future_dates = []

        for i in range(periods):
            future_date = datetime.now() + timedelta(days=i + 1)
            future_dates.append(future_date)

            row = {"day_num": last_day + i + 1}
            dow = future_date.weekday()
            for j in range(7):
                row[f"dow_{j}"] = 1 if j == dow else 0
            future_data.append(row)

        X_future = pd.DataFrame(future_data)[feature_cols].values
        predictions = self.model.predict(X_future)

        # Calculate confidence intervals
        residuals = y - self.model.predict(X)
        mse = np.mean(residuals ** 2)
        std = np.sqrt(mse)

        return pd.DataFrame({
            "date": future_dates,
            "forecast": np.maximum(0, predictions),
            "lower_bound": np.maximum(0, predictions - 1.96 * std),
            "upper_bound": np.maximum(0, predictions + 1.96 * std),
        })

    def calculate_reorder_point(
        self,
        history: pd.DataFrame,
        lead_time_days: int = 7,
        service_level: float = 0.95,
    ) -> dict:
        """Calculate reorder point.

        Args:
            history: Historical demand data.
            lead_time_days: Supplier lead time.
            service_level: Desired service level.

        Returns:
            Reorder point calculation.
        """
        if len(history) == 0:
            return {
                "avg_daily_demand": 0,
                "demand_std": 0,
                "lead_time_demand": 0,
                "safety_stock": 0,
                "reorder_point": 0,
            }

        avg_demand = history["demand"].mean()
        demand_std = history["demand"].std()

        # Lead time demand
        lead_time_demand = avg_demand * lead_time_days

        # Safety stock (using normal distribution z-score)
        from scipy.stats import norm
        z_score = norm.ppf(service_level)
        safety_stock = z_score * demand_std * np.sqrt(lead_time_days)

        # Reorder point
        reorder_point = lead_time_demand + safety_stock

        return {
            "avg_daily_demand": round(avg_demand, 2),
            "demand_std": round(demand_std, 2),
            "lead_time_demand": round(lead_time_demand, 2),
            "safety_stock": round(safety_stock, 2),
            "reorder_point": round(reorder_point, 2),
        }
