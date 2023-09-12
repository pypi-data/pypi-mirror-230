import datetime

from open_quant_data.dataset import DatasetConfig
from open_quant_data.dataset.CsvUtils import CsvUtils
from open_quant_data.model.StockDataTimed import StockDataTimed
from open_quant_data.model.TimeSegment import TimeSegment
from open_quant_data.mysql.MysqlUtils import MysqlUtils

import pandas as pd


class Dataset:
    def __init__(self, config: DatasetConfig, data: StockDataTimed = None):
        self.config: DatasetConfig = config
        self.data: StockDataTimed = data

    def generate(self, start_time: datetime.datetime, end_time: datetime.datetime, stock_id: str):
        mysql_utils = MysqlUtils(self.config.origin_config)
        time_seg = TimeSegment(start_time, end_time)
        self.data = mysql_utils.get_stock_by_time(stock_id, time_seg)

    def export(self, filename: str):
        path = f"{self.config.output_dir}{filename}"
        CsvUtils.export_stock_data_timed(self.data, path)
        print(f"dataset saved to {path}")

    @staticmethod
    def load(path: str) -> pd.DataFrame:
        data = pd.read_csv(path)
        print(f"dataset loaded from {path}")
        return data

