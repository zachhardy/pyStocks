import pandas as pd
import yahooquery as yq


def _reindex_as_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reindex a DataFrame using its 'asOfDate' column as a datetime index.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing an 'asOfDate' column.

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by the 'Date' index derived from 'asOfDate'.
    """
    df = df.copy()
    df.index = pd.to_datetime(df['asOfDate'])
    df.index = df.index.strftime('%Y-%m-%d')
    df.index.name = 'Date'
    df = df.drop(columns=['asOfDate'])
    return df.sort_index()


class DataFetcher:
    """
    Encapsulates all raw data retrieval from YahooQuery for a given symbol.
    """

    def __init__(self, symbol: str):
        """
        Initialize the DataFetcher with a given ticker symbol.

        Parameters
        ----------
        symbol : str
            The stock symbol to fetch data for.
        """
        self.symbol: str = symbol.upper()
        self._ticker: yq.Ticker = yq.Ticker(self.symbol)

    def fetch_price_history(
            self,
            period: str | None = "5y",
            start: str | None = None,
            end: str | None = None,
            interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV price data by period or start/end dates.

        Parameters
        ----------
        period : str or None, default='5y'
            Lookback window (e.g. '1mo', '5y'). Ignored if `start` is set.
        start : str or None, optional
            ISO date string (e.g. '2020-01-01'). If provided without `end`,
            fetches through the latest available date.
        end : str or None, optional
            ISO date string marking the end of the window. Defaults to None.
        interval : str, default='1d'
            Data granularity (e.g. '1d', '1h', '5m', '1m').

        Returns
        -------
        pd.DataFrame
            OHLCV history indexed by date.

        Raises
        ------
        ValueError
            If neither `period` nor `start` is provided.
        """
        history = None
        if start:
            history = self._ticker.history(
                start=pd.to_datetime(start),
                end=pd.to_datetime(end) if end else None,
                interval=interval,
            )
        elif period:
            history = self._ticker.history(
                period=period,
                interval=interval,
            )
        else:
            raise ValueError(
                'Must specify either `period` or `start` to fetch history'
            )

        history.index = history.index.droplevel(level=0)
        history.index = pd.to_datetime(history.index)
        return history

    def get_income_stmt(
            self,
            frequency: str = 'a',
            trailing: bool = False
    ) -> pd.DataFrame:
        """
        Fetch and reindex the income statement.

        Parameters
        ----------
        frequency : str, default='a'
            Frequency of statement: 'a' for annual, 'q' for quarterly.
        trailing : bool, default=False
            Whether to include trailing twelve months (TTM) data.

        Returns
        -------
        pd.DataFrame
            Income statement indexed by date.
        """
        df = self._ticker.income_statement(frequency, trailing)
        return _reindex_as_date(df)

    def get_cashflow_stmt(
            self,
            frequency: str = 'a',
            trailing: bool = False
    ) -> pd.DataFrame:
        """
        Fetch and reindex the cash flow statement.

        Parameters
        ----------
        frequency : str, default='a'
            Frequency of statement: 'a' for annual, 'q' for quarterly.
        trailing : bool, default=False
            Whether to include trailing twelve months (TTM) data.

        Returns
        -------
        pd.DataFrame
            Cash flow statement indexed by date.
        """
        df = self._ticker.cash_flow(frequency, trailing)
        return _reindex_as_date(df)

    def get_balance_sheet(
            self,
            frequency: str = 'a'
    ) -> pd.DataFrame:
        """
        Fetch and reindex the balance sheet.

        Parameters
        ----------
        frequency : str, default='a'
            Frequency of statement: 'a' for annual, 'q' for quarterly.

        Returns
        -------
        pd.DataFrame
            Balance sheet indexed by date.
        """
        df = self._ticker.balance_sheet(frequency)
        return _reindex_as_date(df)

    def get_valuation(self) -> pd.DataFrame:
        """
        Fetch raw valuation measures.

        Returns
        -------
        pd.DataFrame
            Valuation measures DataFrame from YahooQuery.
        """
        return self._ticker.valuation_measures

    def get_dividends(self) -> pd.Series:
        """
        Fetch historical dividends per share.

        Returns
        -------
        pd.Series
            Dividend amounts indexed by ex-dividend date.
        """
        df = self._ticker.history(period='5y', interval='1d')
        df.index = df.index.droplevel(0)
        series = df[df['dividends'] > 0.0]['dividends']
        series.index = pd.to_datetime(series.index)
        series.name = series.name.replace('dividends', 'Dividend')
        return series

    def get_key_stats(self) -> dict:
        return self._ticker.key_stats[self.symbol]

    def get_summary_detail(self) -> dict:
        return self._ticker.summary_detail[self.symbol]

    def get_price(self) -> dict:
        return self._ticker.price[self.symbol]

    def get_financial_data(self) -> dict:
        return self._ticker.financial_data[self.symbol]
