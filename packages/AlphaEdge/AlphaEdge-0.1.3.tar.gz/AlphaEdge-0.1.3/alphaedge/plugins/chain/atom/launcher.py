# -*- encoding:utf-8 -*-
import pdb
from enum import Enum
from alphaedge.plugins.chain.engine import Engine
from alphaedge.plugins.quantum import establish, Trainer, Predictor


class LANCHER(Enum):
    CREATOR = 1
    CALLCORE = 2
    PREDICT = 3


class Launcher(Engine):

    def __init__(self, policy_id, directory, **kwargs):
        super(Launcher, self).__init__(policy_id, **kwargs)
        self.directory = directory

    def model_creator(self, **kwargs):
        establish(kwargs['groups_model'],
                  kwargs['main_model'],
                  self.directory,
                  policy_id=self.policy_id)

    ### 此处可以考虑针对不同持仓收益率传入不同的total_data
    def create_groups(self, total_data):
        ### 子策略训练
        trainer = Trainer(directory=self.directory,
                          policy_id=self.policy_id,
                          k_split=self.k_split)
        trainer.calculate(train_data=total_data)

        ### 子策略预测
        predictor = Predictor(directory=self.directory,
                              policy_id=self.policy_id,
                              k_split=self.k_split)
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

    def calculate(self, **kwargs):
        if kwargs['op'] == LANCHER.CREATOR.value:
            self.model_creator(**kwargs)
        elif kwargs['op'] == LANCHER.CALLCORE.value:
            returns_data = kwargs['total_data'][[
                'trade_date', 'code', 'nxt1_ret'
            ]]
            factors_data = self.create_groups(kwargs['total_data'])
            factors_data = factors_data.merge(returns_data,
                                              on=['trade_date', 'code'])
            factors_data = self.create_main(factors_data.reset_index())
            return factors_data