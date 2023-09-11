from open_quant_data.model.StockDataTimed import StockDataTimed

import csv


class CsvUtils:
    @staticmethod
    def export_stock_data_timed(stock_data_timed: StockDataTimed, path: str):
        data = [["stock_id", "stock_name", "price", "trading_volume", "timestamp"]]
        for stock_data in stock_data_timed.stock_data_list:
            data.append([stock_data.stock_id, stock_data.name, stock_data.price, stock_data.trading_volume,
                         stock_data.timestamp])
        with open(path, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(data)
