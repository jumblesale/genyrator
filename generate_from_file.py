import sys
import json
from genyrator.genyrator import _entity_from_exemplar, render_templates


def main(entity_name, file_name):
    with open(file_name, 'r') as f:
        dict = json.load(f)
        type_name = type(dict).__name__
        if(type(dict).__name__) == 'list':
            element = dict[0]
        else:
            element = dict
        db_rendered, tuple_rendered, to_type_rendered, type_constructor_rendered = render_templates(_entity_from_exemplar(entity_name, element))
        print(db_rendered)
        print(to_type_rendered)
        print(type_constructor_rendered)
        print(tuple_rendered)


if __name__ == '__main__':
    entity_name = sys.argv[1]
    file_name = sys.argv[2]
    main(entity_name, file_name)
