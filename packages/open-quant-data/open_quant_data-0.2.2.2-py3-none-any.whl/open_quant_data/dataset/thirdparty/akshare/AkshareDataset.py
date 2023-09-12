import datetime
from dateutil.relativedelta import relativedelta
from enum import Enum

import akshare as ak
import pandas as pd
from pandas import DataFrame
from loguru import logger


class ReportPeriod(Enum):
    YEARLY = 1
    QUARTERLY = 2
    BY_REPORT = 3


class AkshareDataset:
    def __init__(self):
        pass

    @staticmethod
    def stock_timed(stock_id: str, start_date: str, end_date: str, period: str) -> DataFrame:
        stock = ak.stock_zh_a_hist(symbol=stock_id, period=period, start_date=start_date, end_date=end_date)
        column_translation = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'turnover',
            '振幅': 'amplitude',
            '涨跌幅': 'change_percentage',
            '涨跌额': 'change',
            '换手率': 'turnover_rate'
        }
        for old_col, new_col in column_translation.items():
            if old_col in stock.columns:
                stock.rename(columns={old_col: new_col}, inplace=True)
        return stock

    @staticmethod
    def stock_date(stock_id: str, start_date: str, end_date: str) -> DataFrame:
        stock = ak.stock_zh_a_daily(symbol=stock_id, start_date=start_date, end_date=end_date)
        return stock

    @staticmethod
    def stock_minute(stock_id: str, period: str) -> DataFrame:
        stock = ak.stock_zh_a_minute(symbol=stock_id, period=period)
        return stock

    @staticmethod
    def stock_profit(stock_id: str, period: ReportPeriod = ReportPeriod.QUARTERLY) -> DataFrame:
        profit_table = None
        print(f"===> begin querying profit table of {stock_id} <===")
        if period == ReportPeriod.QUARTERLY:
            profit_table = ak.stock_profit_sheet_by_quarterly_em(symbol=stock_id)
        elif period == ReportPeriod.YEARLY:
            profit_table = ak.stock_profit_sheet_by_yearly_em(symbol=stock_id)
        elif period == ReportPeriod.BY_REPORT:
            profit_table = ak.stock_profit_sheet_by_report_em(symbol=stock_id)
        print(f"===> end querying profit table of {stock_id} <===")
        return profit_table

    @staticmethod
    def stock_balance(stock_id: str, period: ReportPeriod = ReportPeriod.QUARTERLY) -> DataFrame:
        balance_table = None
        print(f"===> begin querying balance table of {stock_id} <===")
        if period == ReportPeriod.QUARTERLY:
            print("Err: we don't support querying balance table by quarter")
        elif period == ReportPeriod.YEARLY:
            balance_table = ak.stock_balance_sheet_by_yearly_em(symbol=stock_id)
        elif period == ReportPeriod.BY_REPORT:
            balance_table = ak.stock_balance_sheet_by_report_em(symbol=stock_id)
        print(f"===> end querying balance table of {stock_id} <===")
        return balance_table

    @staticmethod
    def stock_cash_flow(stock_id: str, period: ReportPeriod = ReportPeriod.QUARTERLY) -> DataFrame:
        cash_flow_table = None
        print(f"===> begin querying cash flow table of {stock_id} <===")
        if period == ReportPeriod.QUARTERLY:
            cash_flow_table = ak.stock_cash_flow_sheet_by_quarterly_em(symbol=stock_id)
        elif period == ReportPeriod.YEARLY:
            cash_flow_table = ak.stock_cash_flow_sheet_by_yearly_em(symbol=stock_id)
        elif period == ReportPeriod.BY_REPORT:
            cash_flow_table = ak.stock_cash_flow_sheet_by_report_em(symbol=stock_id)
        print(f"===> end querying cash flow table of {stock_id} <===")
        return cash_flow_table

    @staticmethod
    def stock_rank(date: str) -> DataFrame:
        return ak.stock_rank_forecast_cninfo(date)

    @staticmethod
    def bond_date(bond_id: str, start_date: str, end_date: str) -> DataFrame:
        dataset = ak.bond_zh_hs_daily(bond_id)
        return dataset

    @staticmethod
    def fund_daily(fund_id: str) -> pd.DataFrame:
        dataset = ak.fund_etf_fund_daily_em()
        return dataset

    @staticmethod
    def fund_timed(fund_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        dataset = ak.fund_etf_fund_info_em(fund=fund_id, start_date=start_date, end_date=end_date)
        column_translation = {
            '净值日期': 'date',
            '单位净值': 'unit_equity',
            '累计净值': 'cumulative_equity',
            '日增长率': 'increase_rate',
            '申购状态': 'subscription_status',
            '赎回状态': 'redemption_status',
        }
        for old_col, new_col in column_translation.items():
            if old_col in dataset.columns:
                dataset.rename(columns={old_col: new_col}, inplace=True)
        return dataset

    @staticmethod
    def between_date(data: DataFrame, start_date: str, end_date: str, date_col_name='date') -> DataFrame:
        filtered_data = data[(data[date_col_name] >= start_date) & (data[date_col_name] <= end_date)]
        return filtered_data

    @staticmethod
    def prev_date(data: DataFrame, start_date: str, date_col_name='date') -> DataFrame:
        filtered_data = data[(data[date_col_name] >= start_date)]
        return filtered_data

    @staticmethod
    def prev_n_month(data: DataFrame, n: int, date_col_name='date') -> DataFrame:
        curr_date = datetime.datetime.now()
        target_date = curr_date - relativedelta(months=n)
        target_date_prev = curr_date - relativedelta(months=n - 1)
        target_date_str = target_date.strftime("%Y-%m-01")
        target_date_prev_str = target_date_prev.strftime("%Y-%m-01")
        return AkshareDataset.between_date(data, target_date_str, target_date_prev_str, date_col_name=date_col_name)

    @staticmethod
    def in_prev_n_month(data: DataFrame, n: int, date_col_name='date') -> DataFrame:
        curr_date = datetime.datetime.now()
        target_date = curr_date - relativedelta(months=n)
        target_date_str = target_date.strftime("%Y-%m-01")
        return AkshareDataset.prev_date(data, target_date_str, date_col_name=date_col_name)
