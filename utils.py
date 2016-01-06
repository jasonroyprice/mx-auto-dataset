__author__ = 'aishimaj'


def replace_top_directory_level(full_path, data_dir):
    """

    Replace the part of a path before EPN with what is in data_dir
    :param full_path:
    :param data_dir:
    :return: path with the part before EPN replaced by data_dir

    """
    import re
    import os

    if not data_dir.startswith(os.sep) or data_dir.endswith(os.sep):
        raise ValueError("data_dir must start with %s and not end with %s" % (os.sep, os.sep))
    p=re.compile('[1-9][0-9]{2,5}[a-z]{0,1}(?!ays)') #regex for EPN - a bunch of numbers plus up to one letter
    matched= p.search(full_path)
    if matched:
        dirsplit = re.split(p, full_path,1)
        found_epn = re.findall(p, full_path)[0]
        last_part=dirsplit[1].split(os.sep)
        combined= os.path.join(data_dir,found_epn, *last_part)
        return combined
