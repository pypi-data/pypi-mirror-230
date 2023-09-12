import matplotlib.pyplot as plt
import pandas as pd


class KDJUtils:
    @staticmethod
    def kdj(close_price: list[float], high_price: list[float], low_price: list[float], period: int = 9) -> pd.DataFrame:
        data = pd.DataFrame({
            'low': low_price
            , 'high': high_price
            , 'close': close_price
        })
        data['lowest_low'] = data['low'].rolling(window=period).min()
        data['highest_high'] = data['high'].rolling(window=period).max()
        data['rsv'] = (data['close'] - data['lowest_low']) / (data['highest_high'] - data['lowest_low']) * 100
        data['k'] = data['rsv'].ewm(com=2).mean()
        data['d'] = data['k'].ewm(com=2).mean()
        data['j'] = 3 * data['k'] - 2 * data['d']
        return data

    @staticmethod
    def plot_kdj(close_price: list[float], high_price: list[float], low_price: list[float], period: int = 9, title=''):
        data = KDJUtils.kdj(close_price, high_price, low_price, period)
        plt.plot(data['k'], label='k')
        plt.plot(data['d'], label='d')
        plt.plot(data['j'], label='j')
        plt.title(f"{title} KDJ")
        plt.legend()
        plt.show()
