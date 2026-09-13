"""
Data Analytics MCP Server for Parvat Netra
Exposes telemetry aggregation, anomaly detection, and statistical profiling tools.
"""

import os
import math
from typing import Any, Dict, List
from dotenv import load_dotenv

load_dotenv()

try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("data_analytics")
except ImportError:
    mcp = None


def compute_statistics(values: List[float]) -> Dict[str, Any]:
    """Compute mean, median, min, max, variance, and standard deviation."""
    if not values:
        return {"error": "Empty dataset provided"}

    n = len(values)
    mean_val = sum(values) / n
    sorted_vals = sorted(values)
    mid = n // 2
    median_val = sorted_vals[mid] if n % 2 != 0 else (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0
    variance = sum((x - mean_val) ** 2 for x in values) / n
    std_dev = math.sqrt(variance)

    return {
        "count": n,
        "mean": round(mean_val, 4),
        "median": round(median_val, 4),
        "min": min(values),
        "max": max(values),
        "std_dev": round(std_dev, 4)
    }


def find_anomalies(values: List[float], threshold_std_dev: float = 2.0) -> Dict[str, Any]:
    """Detect outlier indices and values exceeding the specified standard deviation threshold."""
    stats = compute_statistics(values)
    if "error" in stats or stats["count"] < 3:
        return {"anomalies": [], "message": "Insufficient data points for outlier analysis"}

    mean = stats["mean"]
    std_dev = stats["std_dev"]
    anomalies = []

    for index, val in enumerate(values):
        if std_dev > 0 and abs(val - mean) > (threshold_std_dev * std_dev):
            anomalies.append({
                "index": index,
                "value": val,
                "deviation_from_mean": round(abs(val - mean), 4)
            })

    return {
        "total_anomalies": len(anomalies),
        "threshold_std_dev": threshold_std_dev,
        "anomalies": anomalies
    }


if mcp:
    @mcp.tool()
    def calculate_statistics(data: List[float]) -> Dict[str, Any]:
        """Calculate statistical summary (mean, median, variance, std_dev) for a series of numbers."""
        return compute_statistics(data)

    @mcp.tool()
    def detect_outliers(data: List[float], threshold_std_dev: float = 2.0) -> Dict[str, Any]:
        """Identify anomalous readings based on standard deviation distance from the mean."""
        return find_anomalies(data, threshold_std_dev)


def main():
    if mcp:
        mcp.run()
    else:
        print("MCP SDK not installed. Please install requirements via `pip install -r requirements-mcp.txt`.")


if __name__ == "__main__":
    main()
