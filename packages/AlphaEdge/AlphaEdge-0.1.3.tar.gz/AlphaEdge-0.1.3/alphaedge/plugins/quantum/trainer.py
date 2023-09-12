import os, json, pdb, itertools
from ultron.strategy.deformer import FusionLoad
from ultron.kdutils.file import load_pickle
from ultron.ump.core.process import add_process_env_sig, EnvProcess
from ultron.kdutils.parallel import delayed, Parallel
from ultron.kdutils.progress import Progress
from jdw.mfc.entropy.deformer.fusionx import Futures
from alphaedge.plugins.quantum.base import Base


@add_process_env_sig
def do_groups_train(target_columns, total_data, directory, policy_id,
                    is_groups, offset, is_log, is_shift):
    with Progress(len(target_columns), 0, label='train groups model') as pg:
        i = 0
        for target in target_columns:
            i += 1
            Trainer.workout(total_data=total_data.copy(),
                            model_desc=target[1],
                            horizon=target[0],
                            directory=directory,
                            policy_id=policy_id,
                            is_groups=is_groups,
                            offset=offset,
                            is_log=is_log,
                            is_shift=is_shift)
            pg.show(i)


class Trainer(Base):

    @classmethod
    def workout(cls,
                total_data,
                model_desc,
                horizon,
                directory,
                policy_id,
                is_groups=1,
                offset=1,
                k_split=1,
                is_log=True,
                is_shift=True):
        trainer = cls(directory=directory,
                      policy_id=policy_id,
                      is_groups=is_groups,
                      offset=offset,
                      k_split=k_split,
                      is_log=is_log,
                      is_shift=is_shift)
        train_data = trainer.create_train_data(horizon=horizon,
                                               offset=offset,
                                               total_data=total_data,
                                               is_log=is_log,
                                               is_shift=is_shift)
        trainer.train(model_desc=model_desc, train_data=train_data)

    def __init__(self,
                 directory,
                 policy_id,
                 is_groups=1,
                 offset=1,
                 k_split=1,
                 is_log=True,
                 is_shift=True):
        super(Trainer, self).__init__(directory=directory,
                                      policy_id=policy_id,
                                      is_groups=is_groups,
                                      offset=offset,
                                      k_split=k_split,
                                      is_shift=is_shift,
                                      is_log=is_log)

    def train(self, model_desc, train_data):
        desc_dir = os.path.join(self.category_directory, "desc")
        model_dir = os.path.join(self.category_directory, "model")

        model_desc = model_desc if isinstance(model_desc,
                                              list) else [model_desc]

        model_list = []
        for m in model_desc:
            filename = os.path.join(desc_dir, "{0}.h5".format(m))
            desc = load_pickle(filename)
            model = FusionLoad(desc)
            model_list.append(model)

        columns = [model.formulas.dependency for model in model_list]
        columns = list(set(itertools.chain.from_iterable(columns)))
        train_data = self.normal(total_data=train_data,
                                 columns=columns + ['nxt1_ret'])

        for model in model_list:
            eng = Futures(batch=model.batch,
                          freq=model.freq,
                          horizon=model.horizon,
                          directory=model_dir,
                          is_full=True)
            eng.set_model(model=model)
            eng.train(total_data=train_data)

    def groups_train(self,
                     policy_desc,
                     total_data,
                     is_log=True,
                     is_shift=True):
        parmas = [(k, model_desc) for k, model_desc in policy_desc.items()]
        process_list = self.split_k(self.k_split, parmas)
        parallel = Parallel(len(process_list),
                            verbose=0,
                            pre_dispatch='2*n_jobs')
        _ = parallel(
            delayed(do_groups_train)(target_columns=target_columns,
                                     total_data=total_data,
                                     directory=self.base_directory,
                                     policy_id=self.policy_id,
                                     is_groups=self.is_groups,
                                     offset=self.offset,
                                     is_log=is_log,
                                     is_shift=is_shift,
                                     env=EnvProcess())
            for target_columns in process_list)
        '''
        for k, model_desc in policy_desc.items():
            train_data = self.create_train_data(horizon=int(k),
                                                offset=self.offset,
                                                total_data=total_data,
                                                is_log=is_log,
                                                is_shift=is_shift)
            self.train(model_desc=model_desc, train_data=train_data)
        '''

    def main_train(self, model_desc, total_data, is_log=True, is_shift=True):
        desc_dir = os.path.join(self.category_directory, "desc")
        filename = os.path.join(desc_dir, "{0}.h5".format(model_desc))
        desc = load_pickle(filename)
        horizon = desc['horizon']
        train_data = self.create_train_data(horizon=int(horizon),
                                            offset=self.offset,
                                            total_data=total_data,
                                            is_log=is_log,
                                            is_shift=is_shift)
        self.train(model_desc=model_desc, train_data=train_data)

    def calculate(self, train_data):
        policy_file = os.path.join(self.directory, "policy.json")
        with open(policy_file, 'r') as json_file:
            policy_data = json.load(json_file)
        if self.is_groups:
            self.groups_train(policy_desc=policy_data['groups'],
                              total_data=train_data,
                              is_log=self.is_log,
                              is_shift=self.is_shift)
        else:
            self.main_train(model_desc=policy_data['main'],
                            total_data=train_data,
                            is_log=self.is_log,
                            is_shift=self.is_shift)
        '''    
        model_desc = policy_data['groups'][str(
            horizon)] if self.is_groups else policy_data['main']
        self.train(model_desc=model_desc, train_data=train_data)
        '''
