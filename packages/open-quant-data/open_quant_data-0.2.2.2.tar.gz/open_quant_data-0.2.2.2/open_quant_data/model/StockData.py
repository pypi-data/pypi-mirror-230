import datetime


class StockData:
    def __init__(self, stock_id: str, name: str, price: float, trading_volume: float, timestamp: datetime.datetime):
        self.stock_id: str = stock_id
        self.name: str = name
        self.price: float = price
        self.trading_volume: int = trading_volume
        self.timestamp: datetime.datetime = timestamp

    def report(self):
        print(f"=====> {self.stock_id} <=====")
        print(f"name = {self.name}")
        print(f"price = {self.price}")
        print(f"trading volume = {self.trading_volume}")
        print(f"timestamp = {self.timestamp}")
        print(f"=====>        <=====")