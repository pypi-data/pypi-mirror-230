import pandas as pd
import statsmodels.api as sm


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
    def HAlpha(data: pd.DataFrame, n=60, stock_return_col_name='change', bench_return_col_name='bench_change') -> float:
        X = data.tail(n)[stock_return_col_name]
        X = sm.add_constant(X)
        y = data.tail(n)[bench_return_col_name]
        model = sm.OLS(y, X).fit()
        halpha = model.params['const']
        return halpha



