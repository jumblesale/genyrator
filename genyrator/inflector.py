import inflection


def pythonize(x: str) -> str:
    return inflection.underscore(x)


def camelize(x: str, skip_first_word=False) -> str:
    return inflection.camelize(x, skip_first_word)


def to_json_case(x: str) -> str:
    return camelize(x, False)


def to_class_name(x: str) -> str:
    return camelize(x, True)


def pluralize(x: str) -> str:
    return inflection.pluralize(x)


def dasherize(x: str) -> str:
    return inflection.dasherize(x)
