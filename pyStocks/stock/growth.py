import pandas as pd


def cagr(start: float, end: float, periods: int) -> float:
    """
    Compute the compound annual growth rate (CAGR).

    Parameters
    ----------
    start : float
        The starting value.
    end : float
        The ending value.
    periods : int
        Number of periods over which growth is computed.

    Returns
    -------
    float
        The CAGR as a decimal (e.g., 0.10 for 10%).
    """
    return (end / start) ** (1.0 / periods) - 1.0


def compute_growth(df: pd.DataFrame, periods: int = 1) -> pd.DataFrame:
    """
    Compute period-over-period growth for each metric in a DataFrame.

    For margin columns (ending with 'Margin'), computes basis-point changes
    over the specified number of periods; for other numeric columns,
    computes percent change over that window.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame of metrics indexed by date. Columns ending in 'Margin' are
        treated as percentage values.
    periods : int, default=1
        Number of periods over which to compute growth.

    Returns
    -------
    pd.DataFrame
        DataFrame of growth metrics with suffixes:
        - ' Change (bps)' for margins
        - ' Growth (%)' for others
        Calculations are rounded to two decimal places. Rows where all
        metrics are NaN are dropped.
    """
    growth = pd.DataFrame(index=df.index)
    for col in df.columns:
        if col.endswith('Margin'):
            # Compute absolute change and convert to basis points
            delta = df[col] - df[col].shift(periods)
            growth[f"{col} Change (bps)"] = delta * 100.0
        else:
            # Compute percent change over the given number of periods
            growth[f"{col} Growth (%)"] = df[col].pct_change(periods) * 100.0
    # Round and drop rows where all values are NaN
    return growth.round(2).dropna(how='all')
