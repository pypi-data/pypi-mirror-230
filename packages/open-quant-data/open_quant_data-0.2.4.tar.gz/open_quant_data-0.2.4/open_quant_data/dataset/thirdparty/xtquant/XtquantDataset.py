from typing import List, Dict

import pandas as pd
from open_quant_app.trade.Trader import Trader

import xtquant.xtdata as xt_data

from datetime import datetime

from loguru import logger


class XtquantDataset:
    def __init__(self, config: dict):
        self.trade = Trader(config)

    def connect(self):
        self.trade.start()
        self.trade.info()

    @staticmethod
    def on_download_progress(data):
        logger.info(f"downloading... total = {data['total']}, finished = {data['finished']}")

    @staticmethod
    def get_market_data(stock_ids: List[str], field_list: List[str], period: str,
                        start_date: datetime, end_date: datetime,
                        dividend_type: str = "front") -> Dict[str, pd.DataFrame]:
        # download
        start_timestamp = start_date.strftime("%Y%m%d")
        end_timestamp = end_date.strftime("%Y%m%d")
        xt_data.download_history_data2(stock_ids, period, start_timestamp, end_timestamp,
                                       callback=XtquantDataset.on_download_progress)
        # get
        if 'time' not in field_list:
            field_list.append('time')
        raw_data = xt_data.get_market_data(field_list, stock_ids, period, start_timestamp, end_timestamp,
                                           dividend_type=dividend_type)
        # format
        data = {}
        for stock_id in stock_ids:
            data_dict = {'date': raw_data['time'].columns}
            for field in field_list:
                if field != 'time':
                    data_dict[field] = raw_data[field].loc[stock_id, :].tolist()
            data_df = pd.DataFrame(data_dict)
            data[stock_id] = data_df
        return data

    @staticmethod
    def get_market_data_single(stock_id: str, field_list: List[str], period: str,
                               start_date: datetime, end_date: datetime,
                               dividend_type: str = "front") -> pd.DataFrame:
        data = XtquantDataset.get_market_data([stock_id], field_list, period, start_date, end_date, dividend_type)
        return data[stock_id]

    @staticmethod
    def save_market_data(stock_ids: List[str], field_list: List[str], period: str,
                         start_date: datetime, end_date: datetime, folder_path: str,
                         dividend_type: str = "front"):
        data = XtquantDataset.get_market_data(stock_ids, field_list, period, start_date, end_date, dividend_type)
        for stock_id in data:
            data[stock_id].to_csv(f'{folder_path}{stock_id}.csv')

    @staticmethod
    def save_market_data_single(stock_id: str, field_list: List[str], period: str,
                                start_date: datetime, end_date: datetime, file_path: str,
                                dividend_type: str = "front"):
        data = XtquantDataset.get_market_data_single(stock_id, field_list, period, start_date, end_date, dividend_type)
        data.to_csv(f'{file_path}')
