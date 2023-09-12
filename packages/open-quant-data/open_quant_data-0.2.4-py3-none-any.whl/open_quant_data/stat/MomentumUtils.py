import pandas as pd
import statsmodels.api as sm
import numpy as np
from loguru import logger


class MomentumUtils:
    @staticmethod
    def return_Nm(data: pd.DataFrame, n: int = 6, col_name='close') -> pd.Series:
        return data[col_name] / data[col_name].shift(n * 22) - 1

    @staticmethod
    def wgt_return_Nm(data: pd.DataFrame, n: int = 6, change_per_col_name='change_percentage',
                      turnover_rate_col_name='turnover_rate') -> pd.Series:
        data['product'] = data[change_per_col_name] * data[turnover_rate_col_name]
        data['wgt_return_nm'] = data['product'].rolling(window=n * 22).mean()
        return data['wgt_return_nm']

    @staticmethod
    def exp_wgt_return_Nm(data: pd.DataFrame, n: int = 6) -> pd.Series:
        pass

    @staticmethod
    def HAlpha(data: pd.DataFrame, n=60, stock_return_col_name='change', bench_return_col_name='bench_change') -> float:
        X = data.tail(n)[stock_return_col_name]
        X = sm.add_constant(X)
        y = data.tail(n)[bench_return_col_name]
        model = sm.OLS(y, X).fit()
        halpha = model.params['const']
        return halpha

    @staticmethod
    def add_ret_Nd(data: pd.DataFrame, n: int = 22, close_col: str = 'close') -> pd.DataFrame:
        data[f'ret_{n}d'] = (data['close'] / data['close'].shift(n) - 1) * 100
        return data

    @staticmethod
    def add_ret_Nds(data: pd.DataFrame, ns: [int] = None, close_col: str = 'close') -> pd.DataFrame:
        for n in ns:
            data = MomentumUtils.add_ret_Nd(data, n, close_col)
        return data

    @staticmethod
    def add_wgt_ret_Nd(data: pd.DataFrame, n: int = 22, daily_ret_col: str = 'ret_1d',
                       wgt_col: str = 'weight') -> pd.DataFrame:
        data[f'wgt_ret_{n}d'] = (
                (data[daily_ret_col] * data[wgt_col]).rolling(window=n).sum() /
                data[wgt_col].rolling(window=n).sum()
        )
        return data

    @staticmethod
    def add_wgt_ret_Nds(data: pd.DataFrame, ns: [int] = None, daily_ret_col: str = 'ret_1d',
                        wgt_col: str = 'weight') -> pd.DataFrame:
        for n in ns:
            data = MomentumUtils.add_wgt_ret_Nd(data, n, daily_ret_col, wgt_col)
        return data

    @staticmethod
    def add_exp_wgt_ret_Nd(data: pd.DataFrame, n: int = 22, daily_ret_col: str = 'ret_1d',
                           wgt_col: str = 'weight') -> pd.DataFrame:
        d = np.ceil(n / 22) * 4
        time_weights = np.array([np.exp(-x / d) for x in range(n)])

        def exp_wgt_rolling_sum(series):
            return sum(series * time_weights)

        data[f'exp_wgt_ret_{n}d'] = np.array([
            np.nan if i < n - 1 else
            (np.sum(data[daily_ret_col].iloc[i - n + 1:i + 1].values
                    * data[wgt_col].iloc[i - n + 1:i + 1].values
                    * time_weights)) /
            (np.sum(data[wgt_col].iloc[i - n + 1:i + 1].values
                    * time_weights))
            for i in range(len(data))
        ])
        return data

    @staticmethod
    def add_exp_wgt_ret_Nds(data: pd.DataFrame, ns: [int] = None, daily_ret_col: str = 'ret_1d',
                            wgt_col: str = 'weight') -> pd.DataFrame:
        for n in ns:
            data = MomentumUtils.add_exp_wgt_ret_Nd(data, n, daily_ret_col, wgt_col)
        return data
