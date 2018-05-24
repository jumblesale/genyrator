import os
import sys
import json
from typing import Tuple

from genyrator.genyrator import (
    render_db_model, create_entity_from_exemplar, render_type_model,
)


def file_to_template(
        entity_name:  str,
        file_name:    str,
        db_import:    str,
        types_module: str,
) -> Tuple[str, str]:
    with open(file_name, 'r') as f:
        dict = json.load(f)
        type_name = type(dict).__name__
        if type_name == 'list':
            element = dict[0]
        else:
            element = dict
        entity = create_entity_from_exemplar(entity_name, element, [])
        return render_db_model(
            entity,
            db_import,
            types_module,
        ), render_type_model(entity)


def generate_from_file(
        input_file:        str,
        db_output_dir:     str,
        model_output_dir:  str,
        entity_class_name: str,
        db_import:         str,
        types_module:      str,
) -> None:
    try:
        os.makedirs(db_output_dir)
        os.makedirs(model_output_dir)
    except FileExistsError:
        pass

    db_model, type_model = file_to_template(
        entity_class_name,
        input_file,
        db_import,
        types_module,
    )

    db_output_file = '{}/{}'.format(db_output_dir, '{}.py'.format(entity_class_name.lower()))
    model_output_file = '{}/{}'.format(model_output_dir, '{}.py'.format(entity_class_name.lower()))
    with open(db_output_file, 'w') as f:
        f.write(db_model)
    with open(model_output_file, 'w') as f:
        f.write(type_model)


if __name__ == '__main__':
    input_file =        sys.argv[1]
    db_output_dir =     sys.argv[2]
    model_output_dir =  sys.argv[3]
    entity_class_name = sys.argv[4]
    db_import =         sys.argv[5]
    types_module =      sys.argv[6]

    generate_from_file(
        input_file,
        db_output_dir,
        model_output_dir,
        entity_class_name,
        db_import,
        types_module,
    )
