class Model(object):
    ...


def build_app():
    model_map = {}
    for model in Model.__subclasses__():
        model_map[model.__name__] = model
    return True
