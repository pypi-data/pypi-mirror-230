from .ethos_objects import *


def init_model(*, project, name):
    return Model(project=project, name=name)


def config():
    return Config()  # TODO: make this a singleton?
