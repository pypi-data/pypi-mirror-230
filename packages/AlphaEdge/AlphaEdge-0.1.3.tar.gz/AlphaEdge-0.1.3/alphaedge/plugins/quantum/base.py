import os, pdb
import pandas as pd
import numpy as np
from ultron.factor.data.processing import factor_processing
from ultron.factor.data.winsorize import winsorize_normal
from ultron.factor.data.standardize import standardize


class Base(object):

    def __init__(self,
                 directory,
                 policy_id,
                 is_groups=1,
                 offset=0,
                 k_split=1,
                 is_log=True,
                 is_shift=True):
        self.policy_id = policy_id
        self.base_directory = directory
        self.directory = os.path.join(directory, self.policy_id)
        self.is_groups = is_groups
        self.offset = offset
        self.is_log = is_log
        self.is_shift = is_shift
        self.k_split = k_split
        self.category_directory = os.path.join(
            self.directory, "groups") if is_groups == 1 else os.path.join(
                self.directory, "main")

    def normal(self, total_data, columns):
        diff_columns = [
            col for col in total_data.columns if col not in columns
        ]
        diff_data = total_data[diff_columns]
        new_factors = factor_processing(
            total_data[columns].values,
            pre_process=[winsorize_normal, standardize],
            groups=total_data['trade_date'].values)

        factors_data = pd.DataFrame(new_factors,
                                    columns=columns,
                                    index=total_data.set_index(
                                        ['trade_date', 'code']).index)
        factors_data = factors_data.reset_index()
        factors_data = factors_data.merge(
            diff_data, on=['trade_date',
                           'code']).sort_values(by=['trade_date', 'code'])
        return factors_data

    def create_stats(self,
                     df,
                     horizon,
                     offset,
                     no_code=False,
                     is_log=True,
                     is_shift=True):
        ## 对比JDW中horizon是默认+1  offset+1， 这里要去掉默认+1故shift那里从原来的+1，改成 1 减去 1(horzion) 再减1(offset)为-1
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df.set_index("trade_date", inplace=True)
        df["nxt1_ret"] = np.log(1. +
                                df["chg_pct"]) if is_log else df["chg_pct"]
        if not no_code:
            df = df.groupby("code").rolling(window=horizon)['nxt1_ret'].sum() \
            .groupby(level=0)
        else:
            df = df.rolling(window=horizon)['nxt1_ret'].sum()
        return df.shift(-(horizon + offset - 1)).dropna().reset_index(
        ) if is_shift else df.shift(-(0)).dropna().reset_index()

    def create_train_data(self,
                          horizon,
                          offset,
                          total_data,
                          is_log=True,
                          is_shift=True):
        yields_data = self.create_stats(
            df=total_data[['trade_date', 'code', 'chg_pct']].copy(),
            horizon=int(horizon),
            offset=offset,
            is_log=is_log,
            is_shift=is_shift)
        return total_data.drop(['chg_pct'],
                               axis=1).merge(yields_data,
                                             on=['trade_date', 'code'])

    def create_predict_data(self, horizon, offset, total_data, is_log=True):
        yields_data = self.create_stats(
            df=total_data[['trade_date', 'code', 'chg_pct']].copy(),
            horizon=int(horizon),
            offset=offset,
            is_shift=False,
            is_log=is_log)
        return total_data.drop(['chg_pct'],
                               axis=1).merge(yields_data,
                                             on=['trade_date', 'code'])

    def split_k(self, k_split, columns):
        if len(columns) < k_split:
            return [[col] for col in columns]
        sub_column_cnt = int(len(columns) / k_split)
        group_adjacent = lambda a, k: zip(*([iter(a)] * k))
        cols = list(group_adjacent(columns, sub_column_cnt))
        residue_ind = -(len(columns) %
                        sub_column_cnt) if sub_column_cnt > 0 else 0
        if residue_ind < 0:
            cols.append(columns[residue_ind:])
        return cols