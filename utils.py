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

    use_full_path = False
    if full_path.startswith('/data/home'): # example: /data/home/10123g/aragaod...
        p=re.compile('^/data/home')
        dirsplit = re.split(p, full_path, 1)
        matched = p.search(full_path)
        last_part=dirsplit[1].split(os.sep)
        full_path = os.path.join(*last_part)
        use_full_path = True
    elif full_path.startswith('/data'): # example: /data/10123g/frames/...
        p=re.compile('^/data')
        dirsplit = re.split(p, full_path, 1)
        matched = p.search(full_path)
        last_part=dirsplit[1].split(os.sep)
        combined = os.path.join(data_dir, *last_part)
        return combined
    p=re.compile('[1-9][0-9]{2,5}[a-z]{0,1}(?!ays)') #regex for EPN - a bunch of numbers plus up to one letter
    matched= p.search(full_path)
    if matched:
        dirsplit = re.split(p, full_path,1)
        found_epn = re.findall(p, full_path)[0]
        last_part=dirsplit[1].split(os.sep)
        if use_full_path:
            combined = os.path.join(data_dir, found_epn, "home", *last_part)
        else:
            combined= os.path.join(data_dir,found_epn, *last_part)
        return combined

def create_auto_dir_from_last_frame(last_frame):
    # general structure of last_frame is /data/$EPN/home/PI. We must add auto after the PI
    import re
    p=re.compile('[1-9][0-9]{2,5}[a-z]{0,1}(?!ays)') #regex for EPN - a bunch of numbers plus up to one letter
    if p.search(last_frame):
        dirsplit = re.split(p, last_frame, 1)
        found_epn = re.findall(p, last_frame)[0]
        import os
        last_part = dirsplit[1].split(os.sep)
        combined = os.path.join(dirsplit[0], found_epn, "home", last_part[1], "auto")
        return combined


