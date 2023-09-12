import numpy as np
import pandas as pd


class LabelUtils:
    @staticmethod
    def add_ret1d(data: pd.DataFrame, daily_ret_col: str = 'ret_1d') -> pd.DataFrame:
        data['label'] = data[daily_ret_col].shift(-1)
        return data
