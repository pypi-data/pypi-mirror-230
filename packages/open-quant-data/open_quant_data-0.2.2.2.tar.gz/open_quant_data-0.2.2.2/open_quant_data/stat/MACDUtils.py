import pandas as pd
import matplotlib.pyplot as plt


class MACDUtils:
    @staticmethod
    def ema(prices: list[float], n: int) -> pd.Series:
        series = pd.Series(prices)
        ema = series.ewm(span=n, adjust=False, min_periods=1).mean()
        return ema

    @staticmethod
    def dif(prices: list[float], short_n: int, long_n: int) -> pd.Series:
        short_ema = MACDUtils.ema(prices, short_n)
        long_ema = MACDUtils.ema(prices, long_n)
        dif = short_ema - long_ema
        return dif

    @staticmethod
    def dea(dif, diff_n: int) -> pd.Series:
        dea = dif.ewm(span=diff_n, adjust=False, min_periods=1).mean()
        return dea

    @staticmethod
    def macd(prices: list[float], short_n: int = 12, long_n: int = 26, diff_n: int = 9) -> pd.Series:
        dif = MACDUtils.dif(prices, short_n, long_n)
        dea = MACDUtils.dea(dif, diff_n)
        return 2 * (dif - dea)

    def macd_details(prices: list[float], short_n: int = 12, long_n: int = 26, diff_n: int = 9) -> pd.DataFrame:
        dif = MACDUtils.dif(prices, short_n, long_n)
        dea = MACDUtils.dea(dif, diff_n)
        macd = 2 * (dif - dea)
        return pd.DataFrame({
            'prices': prices
            , 'dif': dif
            , 'dea': dea
            , 'macd': macd
        })

    @staticmethod
    def plot_macd(prices: list[float], short_n: int = 12, long_n: int = 26, diff_n: int = 9, title=""):
        data = MACDUtils.macd_details(prices, short_n, long_n, diff_n)
        # plt.figure(figure=(10, 6))
        data['macd'].plot(kind='bar', color=['g' if x < 0 else 'r' for x in data['macd']])
        data['dif'].plot(color='blue', label='DIF')
        data['dea'].plot(color='orange', label='DEA')
        plt.axhline(y=0, color='black', linewidth=1)  # 添加0水平线
        plt.title(f"{title} MACD")
        plt.legend()
        plt.show()
