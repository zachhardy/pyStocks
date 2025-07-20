from pyStocks.stock import Stock
from pyStocks.stock.valuation import build_raw_valuation

stock = Stock('ABBV')
build_raw_valuation(stock.income_stmt, stock.cashflow_stmt, stock.balance_sheet)
