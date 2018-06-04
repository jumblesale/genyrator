import os
import attr

from genyrator.entities import Template


@attr.s
class File(object):
    file_name: str = attr.ib()
    file_path: str = attr.ib()
    contents:  str = attr.ib()

    def write(self):
        try:
            os.makedirs(self.file_path)
        except FileExistsError:
            ...
        with open('{}/{}'.format(self.file_path, self.file_name), 'w') as f:
            f.write(self.contents)


def create_file_from_template(file_path: str, template: Template):
    if template.out_path is not None:
        file_name = template.out_path[1]
        file_path = '{}/{}'.format(file_path, template.out_path[0])
    else:
        file_name = template.template_file_name
        file_path = file_path
    return File(
        file_name='{}.py'.format(file_name),
        file_path=file_path,
        contents=template.render(),
    )
