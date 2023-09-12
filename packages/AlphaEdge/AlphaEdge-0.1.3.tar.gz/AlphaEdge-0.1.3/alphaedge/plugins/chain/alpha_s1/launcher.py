# -*- encoding:utf-8 -*-
import pdb, datetime, os, json
import pandas as pd
from enum import Enum
from alphakit.factor import *
from alphakit.portfolio import TopNWeight
from ultron.tradingday import *
from ultron.strategy.deformer import FusionLoad
from ultron.kdutils.file import load_pickle
from jdwdata.RetrievalAPI import get_data_by_map, get_factors
from alphaedge.plugins.chain.engine import Engine
from alphaedge.plugins.quantum import establish, Trainer, Predictor
from alphaedge.api import FusionDump


class LANCHER(Enum):
    CREATOR = 1
    TRAIN = 2
    PREDICT = 3
    CALLCORE = 4


class Launcher(Engine):

    def __init__(self, policy_id, directory, **kwargs):
        super(Launcher, self).__init__(policy_id, **kwargs)
        self.directory = directory

    def create_model(self):

        def create_ridge(features, universe, batch, freq, horizon,
                         fit_intercept, positive, count):
            return FusionDump('RidgeRegression',
                              features=features,
                              universe=universe,
                              batch=batch,
                              freq=freq,
                              horizon=horizon,
                              alpha=0.001 * count * batch,
                              fit_intercept=fit_intercept,
                              positive=positive)

        # features = ['1098988732', '1089328594']  ## 目前先固定特征
        features = pd.read_csv(os.path.dirname(__file__) +
                               '/select_factors.csv',
                               header=None).astype('str')
        features = features.values[:, 0].tolist()
        universe_sets = ['dummy120_fst']
        data = get_data_by_map(columns=universe_sets,
                               begin_date='2021-01-01',
                               end_date='2023-01-01',
                               method='ddb')
        count_sets = {}
        for u in universe_sets:
            count_sets[u] = int(data['dummy120_fst'].count(axis=1).mean())

        model_list = [
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=20,
                         freq=1,
                         horizon=10,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst']),
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=20,
                         freq=1,
                         horizon=2,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst']),
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=20,
                         freq=1,
                         horizon=3,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst']),
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=20,
                         freq=1,
                         horizon=4,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst']),
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=20,
                         freq=1,
                         horizon=5,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst']),
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=240,
                         freq=1,
                         horizon=1,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst']),
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=20,
                         freq=120,
                         horizon=10,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst']),
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=20,
                         freq=120,
                         horizon=2,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst']),
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=20,
                         freq=120,
                         horizon=3,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst']),
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=20,
                         freq=120,
                         horizon=4,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst']),
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=20,
                         freq=120,
                         horizon=5,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst']),
            create_ridge(features=features,
                         universe='dummy120_fst',
                         batch=240,
                         freq=120,
                         horizon=20,
                         fit_intercept=False,
                         positive=True,
                         count=count_sets['dummy120_fst'])
        ]
        main_model = create_ridge(features=[],
                                  universe='dummy120_fst',
                                  batch=20,
                                  freq=120,
                                  horizon=3,
                                  fit_intercept=False,
                                  positive=True,
                                  count=count_sets['dummy120_fst'])

        establish(groups_model=model_list,
                  main_model=main_model,
                  directory=self.directory,
                  policy_id=self.policy_id)

    def load_params(self):

        def load_desc(m):
            desc_dir = os.path.join(self.directory, str(self.policy_id),
                                    "groups", "desc")
            filename = os.path.join(desc_dir, "{0}.h5".format(m))
            desc = load_pickle(filename)
            return FusionLoad(desc)

        policy_file = os.path.join(self.directory, str(self.policy_id),
                                   "policy.json")
        with open(policy_file, 'r') as json_file:
            policy_data = json.load(json_file)
        features = []
        nested_list = policy_data['groups'].values()
        nested_list = [item for sublist in nested_list for item in sublist]
        max_window = 0
        for m in nested_list:
            desc = load_desc(m)
            features += desc.features
            max_window = max_window if max_window > (
                desc.horizon + desc.batch) else (desc.horizon + desc.batch)
        return {
            'features': list(set(features)),
            'max_window': int(max_window * 1.2)
        }

    def prepare(self, start_date, end_date):
        params = self.load_params()
        begin_date = advanceDateByCalendar(
            'china.sse', start_date, "-{}b".format(params['max_window'] + 100),
            BizDayConventions.Following)
        data = get_data_by_map(columns=['dummy120_fst', 'ret_o2o', 'ret'],
                               begin_date=begin_date.strftime('%Y-%m-%d'),
                               end_date=end_date,
                               method='ddb')
        retstd = data['ret'].rolling(window=90, min_periods=10).std()
        factors = get_factors(begin_date=start_date,
                              end_date=end_date,
                              ids=params['features'],
                              freq='D')
        chg_pct = data['ret_o2o'].unstack()
        chg_pct.name = 'chg_pct'

        retstd = retstd.unstack()
        retstd.name = 'sample_weight'

        dummy = data['dummy120_fst'].unstack()
        dummy.name = 'dummy'
        total_data = factors.merge(chg_pct, on=['trade_date', 'code']).merge(
            retstd, on=['trade_date', 'code']).merge(dummy,
                                                     on=['trade_date', 'code'])
        total_data = total_data[total_data['dummy'] == 1.0]
        return total_data, dummy

    ### 此处可以考虑针对不同持仓收益率传入不同的total_data
    def create_groups(self, total_data):
        ### 子策略训练
        trainer = Trainer(directory=self.directory, policy_id=self.policy_id)
        trainer.calculate(train_data=total_data)

        ### 子策略预测
        predictor = Predictor(directory=self.directory,
                              policy_id=self.policy_id)
        factors_data = predictor.calculate(total_data=total_data)
        return factors_data.reset_index().sort_values(
            by=['trade_date', 'code'])

    def create_main(self, total_data):
        ### 主策略训练
        total_data = total_data.sort_values(by=['trade_date', 'code'])
        trainer = Trainer(directory=self.directory,
                          policy_id=self.policy_id,
                          is_groups=0)
        trainer.calculate(train_data=total_data)

        ### 主策略预测
        returns_data = total_data[['trade_date', 'code', 'chg_pct']]
        predictor = Predictor(directory=self.directory,
                              policy_id=self.policy_id,
                              is_groups=0)
        factors_data = predictor.calculate(total_data=total_data)
        return factors_data

    def calculate(self, total_data):
        suber_data = self.create_groups(total_data)
        returns_data = total_data[['trade_date', 'code', 'chg_pct']]
        suber_data = suber_data.merge(returns_data, on=['trade_date', 'code'])
        predict_data = self.create_main(suber_data)
        return predict_data

    def run(self, **kwargs):
        if kwargs['op'] == LANCHER.CREATOR.value:
            self.create_model()
        elif kwargs['op'] == LANCHER.CALLCORE.value:
            total_data, dummy = self.prepare(kwargs['start_date'],
                                             kwargs['end_date'])
            er = self.calculate(total_data)
            weight = TopNWeight(dummy.unstack().T, er.unstack(), 1, 1000,
                                1).stack()
            return weight
