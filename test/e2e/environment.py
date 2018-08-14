import os
import glob

from genyrator.path import get_root_path_list


def before_feature(context, feature):
    """
    delete the contents of the output dir before every feature gets run
    :param context:
    :param feature:
    :return:
    """
    root_path = get_root_path_list()
    # make very sure this is the directory which the command is being run in
    files = glob.glob(os.path.join(*root_path, 'output', '*'))
    for f in files:
        # shutil.rmtree(f)
        ...
