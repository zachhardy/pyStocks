from functools import cached_property

import pandas as pd

from .fetch import DataFetcher
from .fundamentals import build_fundamentals
from .growth import compute_growth
from .valuation import build_valuation


class Stock:
    """
    High-level API for fetching and computing stock data and metrics.
    """

    def __init__(
            self,
            symbol: str,
            period: str | None = '5y',
            start: str | None = None,
            end: str | None = None,
            interval: str = '1d',
    ) -> None:
        """
        Initialize the Stock interface with a ticker symbol and history parameters.

        Parameters
        ----------
        symbol : str
            The stock symbol to analyze (e.g., 'AAPL').
        period : str or None, default='5y'
            Lookback window (e.g. '1mo', '5y'); ignored if `start` is set.
        start : str or None, optional
            ISO date string to begin history (e.g. '2020-01-01').
        end : str or None, optional
            ISO date string to end history (e.g. '2020-12-31').
        interval : str, default='1d'
            Data granularity (e.g. '1d', '1h', '5m').
        """
        self.symbol: str = symbol.upper()
        self._fetcher: DataFetcher = DataFetcher(self.symbol)
        self._history_params = {
            'period': period,
            'start': start,
            'end': end,
            'interval': interval,
        }

    def __repr__(self) -> str:
        return f"Stock({self.symbol})"

    @cached_property
    def price_history(self) -> pd.DataFrame:
        """
        Cached historical OHLCV price data for the configured period or date range.

        Returns
        -------
        pd.DataFrame
            DataFrame of OHLCV data indexed by date.
        """
        return self._fetcher.fetch_price_history(**self._history_params)

    @cached_property
    def valuation(self) -> pd.DataFrame:
        """
        Valuation ratios over time.

        Returns
        -------
        pd.DataFrame
            DataFrame of valuation ratios indexed by date.
        """
        raw = self._fetcher.get_valuation()
        return build_valuation(raw)

    @cached_property
    def ttm_valuation(self) -> pd.Series:
        """
        Latest snapshot of valuation ratios.

        Returns
        -------
        pd.Series
            Series of the most recent valuation measures, named by symbol.
        """
        return pd.Series(self.valuation.iloc[-1], name=self.symbol)

    @cached_property
    def growth(self) -> pd.DataFrame:
        """
        Year-over-year (YoY) growth and margin-expansion metrics over time.

        Returns
        -------
        pd.DataFrame
            DataFrame of growth metrics indexed by date.
        """
        return compute_growth(self.fundamentals)

    @cached_property
    def ttm_growth(self) -> pd.Series:
        """
        Year-over-year (YoY) growth and margin-expansion for the most
        recent quarter.

        Returns
        -------
        pd.DataFrame
            DataFrame of TTM growth metrics.
        """
        df = compute_growth(self.quarterly_fundamentals, periods=4)
        return pd.Series(df.iloc[-1], name=self.symbol)

    @cached_property
    def fundamentals(self) -> pd.DataFrame:
        """
        Annual fundamentals.

        Returns
        -------
        pd.DataFrame
            Annual fundamentals indexed by date.
        """
        return build_fundamentals(self.income_stmt,
                                  self.cashflow_stmt,
                                  self.balance_sheet).dropna()

    @cached_property
    def quarterly_fundamentals(self) -> pd.DataFrame:
        """
        Quarterly fundamentals.

        Returns
        -------
        pd.DataFrame
            Quarterly fundamentals indexed by date.
        """
        return build_fundamentals(self.quarterly_income_stmt,
                                  self.quarterly_cashflow_stmt,
                                  self.quarterly_balance_sheet).dropna()

    @cached_property
    def ttm_fundamentals(self) -> pd.Series:
        """
        Trailing twelve months (TTM) fundamentals.

        Returns
        -------
        pd.DataFrame
            TTM fundamentals.
        """
        inc = self.ttm_income_stmt.to_frame().T
        cf = self.ttm_cashflow_stmt.to_frame().T
        bs = self.ttm_balance_sheet.to_frame().T
        return build_fundamentals(inc, cf, bs).iloc[-1]

    @cached_property
    def dividend_history(self) -> pd.Series:
        """
        Historical dividends per share.
        """
        div = self._fetcher.get_dividends()
        div.index = pd.to_datetime(div.index)
        return div

    @cached_property
    def dividend_yield_history(self) -> pd.Series:
        """
        Dividend yield at each payment date, based on closing price.
        """
        hist = self.price_history
        # align to the nearest prior close
        yields = (hist['dividends'] / hist['close']) * 100.0
        return yields[yields > 0.0].dropna().round(2)

    @cached_property
    def dividend_growth(self) -> pd.Series:
        """
        Period-over-period growth in dividend payments.
        """
        # wrap into a 1-column DataFrame so compute_growth can work
        df = compute_growth(self.dividend_history.to_frame())
        series = df['Dividend Growth (%)']
        return series[series > 0.0]

    @cached_property
    def income_stmt(self) -> pd.DataFrame:
        """
        Raw annual income statements.

        Returns
        -------
        pd.DataFrame
            Annual income statement indexed by date.
        """
        return self._fetcher.get_income_stmt('a')

    @cached_property
    def quarterly_income_stmt(self) -> pd.DataFrame:
        """
        Raw quarterly income statements.

        Returns
        -------
        pd.DataFrame
            Quarterly income statement indexed by date.
        """
        return self._fetcher.get_income_stmt('q')

    @cached_property
    def ttm_income_stmt(self) -> pd.Series:
        """
        Trailing twelve months (TTM) income statement.

        Returns
        -------
        pd.DataFrame
            TTM income statement.
        """

        return self._fetcher.get_income_stmt('q', True).iloc[-1]

    @cached_property
    def cashflow_stmt(self) -> pd.DataFrame:
        """
        Raw annual cash flow statements.

        Returns
        -------
        pd.DataFrame
            Annual cash flow statement indexed by date.
        """
        return self._fetcher.get_cashflow_stmt('a')

    @cached_property
    def quarterly_cashflow_stmt(self) -> pd.DataFrame:
        """
        Raw quarterly cash flow statements.

        Returns
        -------
        pd.DataFrame
            Quarterly cash flow statement indexed by date.
        """
        return self._fetcher.get_cashflow_stmt('q')

    @cached_property
    def ttm_cashflow_stmt(self) -> pd.Series:
        """
        Trailing twelve months (TTM) cash flow statement.

        Returns
        -------
        pd.DataFrame
            TTM cash flow statement.
        """
        return self._fetcher.get_cashflow_stmt('q', True).iloc[-1]

    @cached_property
    def balance_sheet(self) -> pd.DataFrame:
        """
        Raw annual balance sheet.

        Returns
        -------
        pd.DataFrame
            Annual balance sheet indexed by date.
        """
        return self._fetcher.get_balance_sheet('a')

    @cached_property
    def quarterly_balance_sheet(self) -> pd.DataFrame:
        """
        Raw quarterly balance sheet.

        Returns
        -------
        pd.DataFrame
            Quarterly balance sheet indexed by date.
        """
        return self._fetcher.get_balance_sheet('q')

    @cached_property
    def ttm_balance_sheet(self) -> pd.Series:
        """
        Trailing twelve months (TTM) balance sheet.

        Returns
        -------
        pd.DataFrame
            TTM balance sheet.
        """
        return self._fetcher.get_balance_sheet('q').iloc[-1]

    @cached_property
    def key_stats(self) -> dict:
        return self._fetcher.get_key_stats()

    @cached_property
    def summary_detail(self) -> dict:
        return self._fetcher.get_summary_detail()

    @cached_property
    def price_data(self) -> dict:
        return self._fetcher.get_price()

    @cached_property
    def financial_data(self) -> dict:
        return self._fetcher.get_financial_data()

    @cached_property
    def refresh_history(
            self,
            *,
            period: str | None = None,
            start: str | None = None,
            end: str | None = None,
            interval: str = None,
    ) -> pd.DataFrame:
        """
        Update and cache OHLCV history with new parameters.

        Parameters
        ----------
        period : str or None
            Lookback window; overrides `start`/`end` if provided.
        start : str or None
            ISO date string to begin history; clears `period` when set.
        end : str or None
            ISO date string to end history.
        interval : str, optional
            Data granularity.

        Returns
        -------
        pd.DataFrame
            Updated OHLCV history indexed by date.
        """
        if period is not None:
            self._history_params.update(
                {'period': period, 'start': None, 'end': None})
        if start is not None:
            self._history_params.update(
                {'start': start, 'end': end, 'period': None})
        if interval is not None:
            self._history_params['interval'] = interval
        if 'price_history' in self.__dict__:
            del self.__dict__['price_history']
        return self.price_history
