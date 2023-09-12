import os, json, copy, math
import pandas as pd
import numpy as np
from ultron.tradingday import *
from ultron.strategy.experimental.multiple_factor import MultipleFactor


class Constraint(object):

    def __init__(self, directory, policy_id, volatility_name):
        self.policy_id = policy_id
        self.directory = os.path.join(directory, self.policy_id)
        self.volatility_name = volatility_name

    def load_configure(self):
        policy_file = os.path.join(self.directory, "policy.json")
        with open(policy_file, 'r') as json_file:
            policy_data = json.load(json_file)
        return policy_data['constraint']

    def calculate(self, weighted_data, volatility_data, prev_returns):
        configure = self.load_configure()
        volatility_mc = MultipleFactor(signal_data=None,
                                       volatility_data=volatility_data,
                                       returns_data=prev_returns)

        volatility_data = volatility_mc._winsorize_volatility(
            name=self.volatility_name, volatility_data=volatility_data)

        volatility_data['trade_date'] = pd.to_datetime(
            volatility_data['trade_date'])

        weighted_groups = weighted_data.groupby('trade_date')
        res = []
        for ref_date, this_data in weighted_groups:
            begin_date = advanceDateByCalendar(
                'china.sse', ref_date, '-{0}b'.format(configure['window']))
            end_date = advanceDateByCalendar('china.sse', ref_date, '-0b')

            signal = weighted_data.set_index('trade_date').loc[end_date]
            volatility = volatility_data.set_index('trade_date').loc[end_date]
            returns = prev_returns.set_index(
                'trade_date').loc[begin_date:end_date].reset_index()
            codes = set(signal.code.unique().tolist()) & set(
                returns.code.unique().tolist()) & set(
                    volatility.code.unique().tolist())
            returns = returns.set_index('code').loc[codes].reset_index()
            signal = signal.set_index('code').loc[codes].reset_index()
            w = copy.deepcopy(this_data)

            corr_dt = volatility_mc._returns_corr(returns).fillna(0)

            ###重置w, 波动率顺序
            w = w.set_index('code').reindex(corr_dt.index).reset_index()
            volatility = volatility.set_index('code').reindex(
                corr_dt.index).reset_index()
            data = w.merge(corr_dt, on=['code']).merge(volatility, on=['code'])
            cols = [
                col for col in data.columns if col not in [
                    'code', 'signal', 'trade_date', 'weight',
                    self.volatility_name
                ]
            ]
            s = data['weight'] * data[self.volatility_name]
            v = data[self.volatility_name]
            n = np.dot(s.T, data[cols])
            if n.shape[0] != s.shape[0]:
                print(n.shape[0], n.shape[0])
            else:
                m = np.dot(n, s)
                if m == 0:
                    continue
                op = math.sqrt(m)
                weighted_dt = copy.deepcopy(this_data)
                weighted_dt['weight'] = ((configure['volatility'] / op) *
                                         this_data['weight'])
                res.append(weighted_dt.set_index(['trade_date', 'code']))
        target_pos = pd.concat(res, axis=0)
        return target_pos
