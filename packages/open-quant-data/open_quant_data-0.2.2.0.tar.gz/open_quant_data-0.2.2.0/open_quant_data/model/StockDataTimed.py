import datetime

from open_quant_data.model.StockData import StockData


class StockDataTimed:
    def __init__(self, stock_id: str, start_time: datetime.datetime, end_time: datetime.datetime,
                 stock_data_list: list[StockData]):
        self.stock_id = stock_id
        self.start_time = start_time
        self.end_time = end_time
        self.stock_data_list = stock_data_list

    def report(self):
        print(f"=====> {self.stock_id} <=====")
        print(f"start time = {self.start_time}")
        print(f"end time = {self.end_time}")
        print(f"stock data list length = {len(self.stock_data_list)}")
        print(f"=====>        <=====")

    def head(self, n: int):
        for i in range(0, min(n, len(self.stock_data_list))):
            self.stock_data_list[i].report()
