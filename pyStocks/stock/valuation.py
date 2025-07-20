import pandas as pd


def build_valuation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw valuation measures into a human-readable table.

    Parameters
    ----------
    df : pd.DataFrame
        Raw valuation_measures DataFrame from YahooQuery, containing columns:
        ['asOfDate', 'periodType', 'ForwardPeRatio', 'PbRatio', 'PeRatio',
         'PegRatio', 'PsRatio', 'EnterprisesValueEBITDARatio',
         'EnterprisesValueRevenueRatio']

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by date (YYYY-MM-DD) with selected valuation ratios:
        - P/E
        - Forward P/E
        - P/S
        - P/B
        - EV/EBITDA
        - EV/Revenue
        Columns are renamed for readability and rounded to 2 decimals.
    """
    # Copy and reindex by date
    df = df.copy()
    df.index = pd.to_datetime(df['asOfDate'])
    df.index = df.index.strftime('%Y-%m-%d')
    df.index.name = 'Date'

    # Drop unneeded columns
    drop_cols = ['asOfDate', 'periodType', 'marketCap', 'enterpriseValue']
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # Rename columns to human-friendly names
    mapping = {
        'PeRatio': 'P/E',
        'ForwardPeRatio': 'Forward P/E',
        'PsRatio': 'P/S',
        'PbRatio': 'P/B',
        'EnterprisesValueEBITDARatio': 'EV/EBITDA',
        'EnterprisesValueRevenueRatio': 'EV/Revenue',
    }
    df = df.rename(columns=mapping)

    # Select and order keys
    keys = ['P/E', 'Forward P/E', 'P/S', 'P/B', 'EV/EBITDA', 'EV/Revenue']
    return df[keys].round(2).dropna()
