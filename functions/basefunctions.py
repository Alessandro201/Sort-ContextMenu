import os
import sys
import shutil
from pathlib import Path
from typing import List, Union
from string import whitespace

from context_menu import menus


def clear_menus():
    try:
        menus.removeMenu('SORT', type='DIRECTORY')
        menus.removeMenu('SORT', type='DIRECTORY_BACKGROUND')
        menus.removeMenu('SORT', type='FILES')
    except FileNotFoundError:
        # It's likely because one of the menus specified above is not implemented
        pass


# todo: I modified it, I need to adapt the other functions because i now return only lists
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


def find_files(mainfolder, dest=''):
    paths = []
    for root, dirs, files in os.walk(mainfolder):
        if root == dest:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            paths.append(file_path)

    return paths


def findNum(name):
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
    Create the parent folders if they do not exists
    """

    # todo: think about the lock, where to implement it and if to use it everywhere or not

    if lock:
        lock.acquire()

    try:
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
