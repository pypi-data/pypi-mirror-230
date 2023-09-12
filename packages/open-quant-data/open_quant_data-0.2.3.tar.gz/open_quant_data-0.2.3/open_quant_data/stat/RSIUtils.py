import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class RSIUtils:
    @staticmethod
    def rsi(prices: list[float], period=14) -> pd.Series:
        prices = pd.Series(prices)
        price_change = prices.diff(1)
        positive_change, negative_change = price_change.copy(), price_change.copy()
        positive_change[positive_change < 0] = 0
        negative_change[negative_change > 0] = 0
        avg_gain = positive_change.ewm(period).mean()
        avg_loss = -negative_change.ewm(period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        print(rsi)
        return rsi

    @staticmethod
    def rsi_periods(prices: list[float], short_period=6, mid_period=12, long_period=24) -> pd.DataFrame:
        rsi_short = RSIUtils.rsi(prices, period=short_period)
        rsi_mid = RSIUtils.rsi(prices, period=mid_period)
        rsi_long = RSIUtils.rsi(prices, period=long_period)
        return pd.DataFrame({
            'rsi_short': (rsi_short, short_period),
            'rsi_mid': (rsi_mid, mid_period),
            'rsi_long': (rsi_long, long_period)
        })

    @staticmethod
    def plot_rsi(prices: list[float], short_period=6, mid_period=12, long_period=24, high_ref=70, low_ref=30,
                 title=''):
        data = RSIUtils.rsi_periods(prices, short_period, mid_period, long_period)
        plt.plot(data['rsi_short'][0], label=f"rsi-{data['rsi_short'][1]}", color='b')
        plt.plot(data['rsi_mid'][0], label=f"rsi-{data['rsi_mid'][1]}", color='y')
        plt.plot(data['rsi_long'][0], label=f"rsi-{data['rsi_long'][1]}", color='pink')
        plt.axhline(y=50, color='black', linewidth=1)
        plt.axhline(y=high_ref, color='red', linewidth=1)
        plt.axhline(y=low_ref, color='green', linewidth=1)
        plt.title(f"{title} RSI")
        plt.legend()
        plt.show()
