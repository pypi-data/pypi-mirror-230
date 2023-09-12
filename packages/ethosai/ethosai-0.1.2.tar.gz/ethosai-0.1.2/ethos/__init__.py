from .ethos_objects import *


def init_model(*, project, name):
    return Model(project=project, name=name)


# Use ethos.config to access the global config object.
config = Config()
