"""Metric and inclusive date-window rules for the daily sample dashboard."""
from datetime import timedelta
import pandas as pd


def previous_period(start, end):
    if end < start:
        raise ValueError('End date must be on or after start date')
    days = (end - start).days + 1
    return start - timedelta(days=days), start - timedelta(days=1)


def coverage_complete(dates, start, end):
    available = pd.DatetimeIndex(pd.to_datetime(dates)).normalize().unique()
    return pd.date_range(start, end, freq='D').difference(available).empty


def percentage_change(current, previous):
    return (current - previous) / previous * 100 if previous > 0 else None


def profit_margin(profit, revenue):
    return profit / revenue * 100 if revenue != 0 else float('nan')
