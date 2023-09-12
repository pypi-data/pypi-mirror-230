import json, os, pdb
from ultron.kdutils.file import dump_pickle
from ultron.strategy.deformer import FusionLoad


class Creator(object):

    @classmethod
    def update_model(cls, model, features):
        m = FusionLoad(model)
        m.update_features(features)
        return m.dump()

    @classmethod
    def model_dump(cls, model_desc, directory, is_groups=True, policy_id=None):
        base_dir = "groups" if is_groups else "main"
        res = {}
        if isinstance(model_desc, list):
            for m in model_desc:
                id = m['id']
                horizon = str(m['horizon'])
                l = [] if horizon not in res else res[horizon]
                l.append(id)
                res[horizon] = l
                filename = os.path.join(directory, base_dir, "desc",
                                        "{0}.h5".format(id))
                dump_pickle(m, filename)
            return res
        else:
            id = model_desc['id']
            filename = os.path.join(directory, base_dir, "desc",
                                    "{0}.h5".format(id))
            dump_pickle(model_desc, filename)
            return id


def establish(groups_model, main_model, directory, policy_id=None):
    directory = os.path.join(directory, policy_id) if isinstance(
        policy_id, str) else directory
    res = Creator.model_dump(groups_model, directory)
    features = [item for sublist in res.values() for item in sublist]
    model_id = Creator.model_dump(Creator.update_model(main_model, features),
                                  directory,
                                  is_groups=False)
    data = {"groups": res, "main": model_id}
    filename = os.path.join(directory, "policy.json")
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)