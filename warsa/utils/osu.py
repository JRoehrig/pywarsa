__author__ = 'roehrig'
"""
Created on 14.10.2013

@author: Roehrig
"""
import time
from os import makedirs, listdir, sep, unlink, rmdir, remove
from os.path import dirname, exists, isfile, isdir, join
from shutil import copy2


def touch(file_name):
    assure_path_exists(file_name)
    open(file_name, 'a').close()


def file_exists(file_name):
    return isfile(file_name)


def assure_path_exists(path):
    d = dirname(path)
    if not exists(d):
        makedirs(d)


def get_file_names(directory, suffix=None, prefix=None, pattern=None):
    if not isdir(directory):
        return []
    if directory[-1] == sep:
        directory = directory[:-1]

    result = listdir(directory)
    if prefix:
        if isinstance(prefix, basestring):
            result = [f for f in result if f.startswith(prefix)]
        else:
            result = [f for f in result for p in prefix if f.startswith(p)]
    if suffix:
        if isinstance(suffix, basestring):
            result = [f for f in result if f.endswith(suffix)]
        else:
            result = [f for f in result for s in suffix if f.endswith(s)]
    if pattern:
        if isinstance(pattern, basestring):
            result = [f for f in result if pattern in f]
        else:
            result = [f for f in result for p in pattern if p in f]
    return result


def copy_file(src, dst):
    copy2(src, dst)


def delete_file(filename):
    if isfile(filename):
        remove(filename)


def delete_files(path, prefix):
    if isdir(path):
        for f in [f for f in listdir(path) if isfile(join(path, f))]:
            if f.startswith(prefix):
                remove(path + '/' + f)


def get_subdirectories(directory):
    if not isdir(directory):
        return []
    if directory[-1] == sep:
        directory = directory[:-1]
    return [name for name in listdir(directory) if isdir(join(directory, name))]


def create_directory(directory):
    if not exists(directory):
        makedirs(directory)
    return directory


def create_tmp_directory(directory):
    """
    Create a temporary host_directory in the given host_directory and return it
    """
    timestamp = str(int(time.time()))
    # Create a new temporary work host_directory. Append a '/' even if there is
    # already one. Append timestamp
    wd = join(directory, 'tmp' + timestamp)
    i = 0
    while isdir(wd):
        wd = directory + str(i)
        i += 1
    makedirs(wd)
    return wd


def remove_directory(directory):
    if not isdir(directory):
        return
    if directory[-1] == sep:
        directory = directory[:-1]
    files = listdir(directory)
    for filename in files:
        if filename == '.' or filename == '..':
            continue
        path = directory + sep + filename
        if isdir(path):
            remove_directory(path)
        else:
            unlink(path)
    rmdir(directory)


