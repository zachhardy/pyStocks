import pandas as pd

from .utils import split_camel_case


def extract_income_stmt_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract key income statement metrics.

    Parameters
    ----------
    df : pd.DataFrame
        Income statement with columns ['TotalRevenue', 'GrossProfit', 'OperatingIncome', 'NetIncome']

    Returns
    -------
    pd.DataFrame
        DataFrame containing raw metrics:
        - TotalRevenue, GrossProfit, OperatingIncome, NetIncome
    """
    keys = ['TotalRevenue', 'GrossProfit', 'OperatingIncome', 'NetIncome']
    return df[keys].dropna()


def extract_cashflow_stmt_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract key cash flow metrics.

    Parameters
    ----------
    df : pd.DataFrame
        Cash flow statement with columns ['FreeCashFlow', 'CapitalExpenditure', 'StockBasedCompensation']

    Returns
    -------
    pd.DataFrame
        DataFrame containing:
        - FreeCashFlow, CapitalExpenditure, StockBasedCompensation
        - CapitalExpenditure as positive outflow (-)
    """
    keys = ['FreeCashFlow', 'CapitalExpenditure', 'StockBasedCompensation']
    out = df[keys].dropna()
    # normalize sign: capex as positive expense
    out['CapitalExpenditure'] = -out['CapitalExpenditure']
    return out.dropna()


def extract_balance_sheet_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract key balance sheet metrics and compute leverage ratio.

    Parameters
    ----------
    df : pd.DataFrame
        Balance sheet with columns ['CashAndCashEquivalents', 'TotalDebt']

    Returns
    -------
    pd.DataFrame
        DataFrame containing:
        - Cash (from CashAndCashEquivalents), TotalDebt
        - DebtToCash (TotalDebt / Cash)
    """
    keys = ['CashAndCashEquivalents', 'TotalDebt']
    out = df[keys].dropna().rename(columns={'CashAndCashEquivalents': 'Cash'})
    out['DebtToCash'] = out['TotalDebt'] / out['Cash']
    return out.dropna()


def build_fundamentals(
        income_stmt: pd.DataFrame,
        cashflow_stmt: pd.DataFrame,
        balance_sheet: pd.DataFrame
) -> pd.DataFrame:
    """
    Combine raw financial statements into one table and compute key metrics.

    Parameters
    ----------
    income_stmt : pd.DataFrame
        Raw income statement.
    cashflow_stmt : pd.DataFrame
        Raw cash flow statement.
    balance_sheet : pd.DataFrame
        Raw balance sheet.

    Returns
    -------
    pd.DataFrame
        Combined DataFrame with all metrics including:
        - TotalRevenue, GrossProfit, OperatingIncome, NetIncome
        - GrossMargin, OperatingMargin, NetMargin
        - FreeCashFlow, CapitalExpenditure, StockBasedCompensation
        - FreeCashFlowMargin, Cash, TotalDebt, DebtToCash
        Column names humanized and sorted by date.
    """
    # Extract and normalize individual metrics
    inc = extract_income_stmt_metrics(income_stmt)
    cf = extract_cashflow_stmt_metrics(cashflow_stmt)
    bs = extract_balance_sheet_metrics(balance_sheet)

    # Stitch together raw metrics
    df = pd.concat([inc, cf, bs], axis=1)

    # Compute income statement margins
    revenue = df['TotalRevenue']
    df['GrossMargin'] = df['GrossProfit'] / revenue
    df['OperatingMargin'] = df['OperatingIncome'] / revenue
    df['NetMargin'] = df['NetIncome'] / revenue

    # Compute cash flow margin
    df['FreeCashFlowMargin'] = df['FreeCashFlow'] / revenue

    # Humanize column names
    df.columns = [split_camel_case(col) for col in df.columns]

    return df.sort_index()
