import os
import sys
import shutil
from pathlib import Path
from typing import List, Union
from string import whitespace

from context_menu import menus
from timebudget import timebudget
from tqdm import tqdm


def clear_menus():
    try:
        menus.removeMenu('SORT', type='DIRECTORY')
        menus.removeMenu('SORT', type='DIRECTORY_BACKGROUND')
        menus.removeMenu('SORT', type='FILES')
    except FileNotFoundError:
        # It's likely because one of the menus specified above is not implemented
        pass


def clean_paths(file_paths: List[str]):
    if type(file_paths) == list:
        for index, file_path in enumerate(file_paths):
            file_path.strip(whitespace + '"')
            file_paths[index] = file_path

        return file_paths
    else:
        raise TypeError(f"Expected a list, obtained a {type(file_paths)}")


def toprint(lock, text):
    lock.acquire()
    print(text)
    lock.release()


def noprint(*args):
    pass


def find_files(mainfolder, skip_files_in_main_folder=False):
    paths = []
    for root, dirs, files in os.walk(mainfolder):
        if skip_files_in_main_folder and root == mainfolder:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            paths.append(file_path)

    return paths


def find_num(name):
    i = name.rfind('(')
    j = name.rfind(')')

    if i != -1 and j == (len(name) - 1):
        try:
            num = int(name[i + 1: -1])

        except ValueError:
            num = 0
            i = len(name)
    else:
        num = 0
        i = len(name)

    return i, num


@timebudget
def find_dest_path_without_conflicts(dict_src_dest: dict):
    # It's needed to check for redundancies in the names
    path_analysed = set()

    for src, dest in tqdm(dict_src_dest.items()):
        basename, filename = os.path.split(dest)

        name, ext = os.path.splitext(filename)
        i, num = find_num(name)

        while dest in path_analysed or os.path.exists(dest):
            num += 1
            dest_name = name[:i] + '(' + str(num) + ')' + ext
            dest = os.path.join(basename, dest_name)

        path_analysed.add(dest)
        dict_src_dest[src] = dest

    return dict_src_dest


def move(lock, src, dest, prt):
    try:
        shutil.move(src, dest)

        prt(lock, f'{src} --- moved to destination as --> {dest}')

    except PermissionError as err:
        lock.acquire()
        print(f'You do not have the permission to move {src}\n'
              f'- Error: {err}\n')
        lock.release()

    except OSError as err:
        lock.acquire()
        print(f'OSError in moving: {src}\n'
              f'- Error: {err}\n')
        lock.release()


def make_parent_folders(filepath: Union[str, Path], lock=None):
    """
    Create the parent folders if they do not exist
    """

    # todo: think about the lock, where to implement it and if to use it everywhere or not

    try:
        if lock:
            lock.acquire()

        if type(filepath) == Path:
            os.makedirs(filepath.parent, exist_ok=True)
        else:
            parent_folder = os.path.dirname(filepath)
            os.makedirs(parent_folder, exist_ok=True)

    except PermissionError as err:
        print(f'You do not have the permission to create all the parent folders of {filepath}\n'
              f'- Error: {err}\n')

    except OSError as err:
        print(f'Error in creating the directory: {filepath}. \n'
              f'- Error: {err}\n')

    except Exception as err:
        print(f'Fatal Exception: {err}\n')

    finally:
        if lock:
            lock.release()
