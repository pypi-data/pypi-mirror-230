import pymysql

from open_quant_data.model.StockData import StockData
from open_quant_data.model.StockDataTimed import StockDataTimed
from open_quant_data.model.TimeSegment import TimeSegment


class MysqlUtils:
    def __init__(self, config: dict):
        mysql_config = config["database"]["mysql"]
        self.host = mysql_config["host"]
        self.port = mysql_config["port"]
        self.user = mysql_config["user"]
        self.password = mysql_config["password"]
        self.db = mysql_config["db"]
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, db=self.db)

    def close(self):
        self.conn.close()

    def get_stock_by_id(self) -> StockDataTimed:
        pass

    def get_stock_by_time(self, stock_id: str, time_seg: TimeSegment) -> StockDataTimed:
        cursor = self.conn.cursor()
        # fetch stock id
        sql = "SELECT id FROM stocks WHERE ticker = %s"
        cursor.execute(sql, (stock_id,))
        id = cursor.fetchone()[0]
        # query
        sql = ("SELECT * FROM intraday_data WHERE stock_id = %s AND "
               "timestamp BETWEEN %s AND %s "
               "ORDER BY timestamp")
        cursor.execute(sql, (id, time_seg.start_time, time_seg.end_time,))
        data_list = cursor.fetchall()
        # collect
        start_timestamp = data_list[0][3]
        end_timestamp = data_list[-1][3]
        stock_data_list: list[StockData] = []
        for item in data_list:
            name = item[2]
            timestamp = item[3]
            price = item[4]
            trading_volume = item[5]
            stock_data_list.append(StockData(stock_id, name, price, trading_volume, timestamp))
        return StockDataTimed(stock_id, start_timestamp, end_timestamp, stock_data_list)

    def backup_stock_by_id(self) -> StockDataTimed:
        pass

    def backup_stock_by_time(self, time_seg: TimeSegment) -> StockDataTimed:
        pass
